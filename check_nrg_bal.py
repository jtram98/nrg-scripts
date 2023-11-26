import requests
import json
from os import environ
from twilio.rest import Client
import logging
from enum import IntEnum
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from text_notification import TextNotification
from dotenv import load_dotenv

load_dotenv()

# Messages used in notifications
common_text = "Previous Balance = {prev_bal:0,.2f} and New Balance = {cur_bal:0,.2f}, ${dol_val:0,.2f} USD (@{usd_xchng:0,.2f}/NRG)"
no_chg_bal = "No change in balance from last check. " + common_text
increase_bal = "New balance increased. " + common_text
decrease_bal = "Current balance is less than previous balance. Please check the block explorer. " + common_text

# NOTIFY_TYPE enum
class Notification(IntEnum):
    NONE  = 0
    EMAIL = 1
    TEXT  = 2
    ALEXA = 3
    ALL   = 4

def notify(notification_type, msg):
    try:
        logging.info(f"Sending notification via: {Notification(int(notification_type)).name}")
        match notification_type:
            case Notification.TEXT:
                text_notification(msg)
            case Notification.EMAIL:
                email_notification(msg)
            case Notification.ALEXA:
                alexa_notification(msg)
            case Notification.ALL:
                text_notification(msg)
                email_notification(msg)
                alexa_notification(msg)
            case _:
                email_notification(msg)
    except Exception as e:
        logging.error("Error in notify function: " + str(e))

def text_notification(msg):
    try:
        client = Client(environ.get('TWILIO_SID'), environ.get('TWILIO_AUTH'))
        client.messages.create(
            body=msg,
            from_=environ.get('TWILIO_FROM'),
            to=environ.get('TWILIO_TO')
        )
    except Exception as e:
        logging.error("Error occurred with Twilio: " + str(e))


def text_notification(msg):
    try:
        client = Client(environ.get('TWILIO_SID'), environ.get('TWILIO_AUTH'))
        client.messages.create(
            body=msg,
            from_=environ.get('TWILIO_FROM'),
            to=environ.get('TWILIO_TO')
        )
    except Exception as e:
        logging.error("Error occurred with Twilio: " + str(e))

def email_notification(msg):
    try:
        message = Mail(
            from_email=environ.get('SENDGRID_FROM'),
            to_emails=environ.get('SENDGRID_TO'),
            subject='NRG Balance Update',
            html_content=f'<strong>{msg}</strong>'
        )
        sg = SendGridAPIClient(environ.get('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as e:
        logging.error("Error occurred using SendGrid: " + str(e))

def alexa_notification(msg):
    try:
        body = json.dumps({
            "notification": msg,
            "accessCode": environ.get('ALEXA_API_KEY')
        })
        response = requests.post(url="https://api.notifymyecho.com/v1/NotifyMe", data=body)
        logging.info(response.text)
    except Exception as e:
        logging.error("Error occurred with Alexa notification: " + str(e))

def check_bal(): 
    try:
        with open(environ.get("BALANCE_FILE"), "r+") as bal_file:
            prev_bal = round(float(bal_file.read() or 0), 2)
            response, usd_response = fetch_balance_data()

            if response is not None and usd_response is not None:
                coin_usd = float(usd_response.json().get("result", {}).get("coin_usd", 0))
                cur_bal = round(float((response.json().get("result") or 0)) / 10**18, 2)

                handle_balance_change(prev_bal, cur_bal, coin_usd, bal_file)
                
    except IOError as e:
        logging.error("File operation failed: " + str(e))
    except Exception as e:
        logging.error("Unexpected error in check_bal: " + str(e))

def fetch_balance_data():
    try:
        response = requests.get(environ.get("BASE_URL") + environ.get("GET_BAL") + environ.get("WALLET_ADDR"))
        usd_response = requests.get(environ.get("BASE_URL") + environ.get("GET_USD"))
        return response, usd_response
    except requests.RequestException as e:
        logging.error("Network request failed: " + str(e))
        return None, None

def handle_balance_change(prev_bal, cur_bal, coin_usd, bal_file):
    #check if cur_bal has increased from last check
    if (cur_bal == prev_bal):
        #no change
        msg_body = no_chg_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logging.info(msg_body)
    elif (cur_bal > prev_bal):
        #balance increased
        msg_body = increase_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logging.info(">>> "+msg_body)
        
        #overwrite prev_bal with cur_bal in bal_file
        bal_file.seek(0)
        bal_file.write('{0:.2f}'.format(cur_bal))

        #send notification
        try:
            notify(environ.get('NOTIFY_TYPE'), "NRG Balance Update\n"+msg_body)
        except Exception as err:
            logging.error(str(err))
    else:
        #cur bal is less than previous balance, may indicate an issue with the NRG node/network
        msg_body = decrease_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logging.info(msg_body)
    
    print(msg_body)


def main():
    logging.basicConfig(filename=environ.get("LOG_FILE"), format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
    check_bal()

if __name__ == "__main__":
    main()