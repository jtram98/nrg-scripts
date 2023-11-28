import requests
from os import environ
from notification import AlexaNotification, EmailNotification, TextNotification
from config import no_chg_bal, increase_bal, decrease_bal, NotificationTypes
import logging

logger = logging.getLogger(__name__)

# Function to fetch balance data and handle balance change
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
        logger.error("File operation failed: " + str(e))
    except Exception as e:
        logger.error("Unexpected error in check_bal: " + str(e))


def fetch_balance_data():
    try:
        response = requests.get(environ.get("BASE_URL") + environ.get("GET_BAL") + environ.get("WALLET_ADDR"))
        usd_response = requests.get(environ.get("BASE_URL") + environ.get("GET_USD"))
        return response, usd_response
    except requests.RequestException as e:
        logger.error("Network request failed: " + str(e))
        return None, None

def handle_balance_change(prev_bal, cur_bal, coin_usd, bal_file):
    #check if cur_bal has increased from last check
    if (cur_bal == prev_bal):
        #no change
        msg_body = no_chg_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logger.info(msg_body)
    elif (cur_bal > prev_bal):
        #balance increased
        msg_body = increase_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logger.info(">>> "+msg_body)
        
        #overwrite prev_bal with cur_bal in bal_file
        bal_file.seek(0)
        bal_file.write('{0:.2f}'.format(cur_bal))

        #send notification
        try:
            notify(environ.get('NOTIFY_TYPE'), "NRG Balance Updatee<br/><br/>"+msg_body)
        except Exception as err:
            logger.error(str(err))

    else:
        #cur bal is less than previous balance, may indicate an issue with the NRG node/network
        msg_body = decrease_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*coin_usd), usd_xchng=coin_usd)
        logger.info(msg_body)

        #send notification indicating a possible error
        try:
            notify(environ.get('NOTIFY_TYPE'), "NRG Balance Update<br/><br/>"+msg_body)
        except Exception as err:
            logger.error(str(err))
    
    print(msg_body)

    


def notify(notification_type, msg):
    try:
        logger.info(f"Sending notification via: {NotificationTypes(int(notification_type)).name}")
        match notification_type:
            case NotificationTypes.TEXT:
               TextNotification().notify(msg)
            case NotificationTypes.EMAIL:
               EmailNotification().notify(msg)
            case NotificationTypes.ALEXA:
                AlexaNotification(msg)
            case NotificationTypes.ALL:
                TextNotification().notify(msg)
                EmailNotification().notify(msg)
                AlexaNotification(msg)
            case _:
                EmailNotification().notify(msg)
    except Exception as e:
        logger.error("Error in notify function: " + str(e))

