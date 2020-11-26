import requests
import json
import datetime
import configparser
from os import environ
from twilio.rest import Client
import logging
from enum import IntEnum
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from  text_notification import TextNotification

#messages used in notifications
common_text = "Previous Balance = {prev_bal:0,.2f} and New Balance = {cur_bal:0,.2f}, ${dol_val:0,.2f} USD (@{usd_xchng:0,.2f} /NRG)"
no_chg_bal = "No change in balance from last check. " + common_text
increase_bal = "New balance increased. " + common_text
decrease_bal = "Current blance is less than previous balance. Pleae check the block explorer. " + common_text
            
#notify_type enum
class Notification(IntEnum):
    NONE = 0
    EMAIL = 1
    TEXT = 2
    ALEXA = 3
    ALL = 4
    
#read config
def get_config():
    config = configparser.ConfigParser()
    config.read((environ.get('NRG_INI_PATH')+'config.ini'))
    return config

#set up vars
def get_vars(config):
    nrg_vars = {
        #nrg vars
        "base_url": config['API']['BASE_URL'],
        "get_bal": config['API']['GET_BAL'],
        "get_usd": config['API']['GET_USD'],
        "wallet_addr": environ.get('NRG_ADDR'),
        #files
        "bal_file_loc": config['LOGS']['BALANCE'],
        "app_log_loc": config['LOGS']['INFO'],
        #notify type
        "notify_type": config.getint('NOTIFICATION','NOTIFY_TYPE'),
        #twilio vars
        "twilio_sid": environ.get('TWILIO_SID'),
        "twilio_auth": environ.get('TWILIO_AUTH'),
        "twilio_from": environ.get('TWILIO_FROM'),
        "twilio_to": environ.get('TWILIO_TO'),
        #sendgrid vars
        "sendgrid_api_key": environ.get('SENDGRID_API_KEY'),
        "sendgrid_to": environ.get('SENDGRID_TO'),
        "sendgrid_from": environ.get('SENDGRID_FROM'),
        #alexa
        "alexa_api_key": environ.get('ALEXA_API_KEY')
    }
    return nrg_vars

def notify(nrg_vars, msg):
    if (nrg_vars.get('notify_type') == Notification.TEXT):
        text = TextNotification()
        text.notify(nrg_vars.get('twilio_sid'),  nrg_vars.get('twilio_auth'),  nrg_vars.get('twilio_to'),  nrg_vars.get('twilio_from'), msg)
    elif(nrg_vars.get('notify_type') == Notification.EMAIL):
        email_notification(nrg_vars, msg)
    elif(nrg_vars.get('notify_type') == Notification.ALEXA):
        alexa_notification(nrg_vars, msg)
    else:
        #send to all notification types
        text_notification(nrg_vars,msg)
        email_notification(nrg_vars,msg)
        alexa_notification(nrg_vars, msg)

def text_notification(nrg_vars, msg):
    client = Client(nrg_vars.get('twilio_sid'), nrg_vars.get('twilio_auth'))

    client.messages.create(
         body = msg,
         from_ = nrg_vars.get('twilio_from'),
         to = nrg_vars.get('twilio_to')
     )

def email_notification(nrg_vars, msg):
    message = Mail(
        from_email=nrg_vars.get('sendgrid_from'),
        to_emails=nrg_vars.get('sendgrid_to'),
        subject='NRG Balance Update',
        html_content='<strong>'+msg+'</strong>'
    )
    try:
        sg = SendGridAPIClient(nrg_vars.get('sendgrid_api_key'))
        sg.send(message)
    except Exception as e:
        logging.error("Error occurred using SENDGRID: " + str(e))
    
def alexa_notification(nrg_vars, msg):
    body = json.dumps({
        "notification": msg,
        "accessCode": nrg_vars.get('alexa_api_key')
        })
    resp = requests.post(url = "https://api.notifymyecho.com/v1/NotifyMe", data = body)
    logging.info(str(resp.text))


def check_bal(nrg_vars): 
    #file to store balance
    try:
        bal_file = open(nrg_vars.get("bal_file_loc"), "r+")
    except FileNotFoundError:
        bal_file = open(nrg_vars.get("bal_file_loc"), "w+")

    #prev bal
    prev_bal = round(float(bal_file.read() or 0),2)

    #get balance response & status
    response = requests.get(nrg_vars.get("base_url") + nrg_vars.get("get_bal") + nrg_vars.get("wallet_addr"))
    status = float(response.json()["status"])

    #get USD value & status
    usd_response = requests.get(nrg_vars.get("base_url") + nrg_vars.get("get_usd"))
    usd_xchng = float(usd_response.json()["result"]["ethusd"] or 0)

    #curent balance
    #round up 2 decimals
    cur_bal = round(float((response.json()["result"] or 0)) / 10**18,2)

    #bad status, set msg_content with json response
    if (status == 0):
        logging.error("Error occured, bad status returned: " + str(response.json()))
    #save response
    else:
        #check if cur_bal has increased from last check
        if (cur_bal == prev_bal):
            #no change
            msg_body = no_chg_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*usd_xchng), usd_xchng=usd_xchng)
            logging.info(msg_body)
        elif (cur_bal > prev_bal):
            #balance increased
            msg_body = increase_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*usd_xchng), usd_xchng=usd_xchng)
            logging.info(">>> "+msg_body)
            
            #overwrite prev_bal with cur_bal in bal_file
            bal_file.seek(0)
            bal_file.write('{0:.2f}'.format(cur_bal))

            #send notification
            try:
                notify(nrg_vars, "NRG Balance Update\n"+msg_body)
            except Exception as err:
                logging.error(str(err))
        else:
            #cur bal is less than previous balance, may indicate an issue with the NRG node/network
            msg_body = decrease_bal.format(prev_bal=prev_bal, cur_bal=cur_bal, dol_val=(cur_bal*usd_xchng), usd_xchng=usd_xchng)
            logging.info(msg_body)

    #file cleanup
    bal_file.flush()
    bal_file.close()

def main():
    nrg_vars = get_vars(get_config())
    logging.basicConfig(filename=nrg_vars.get("app_log_loc"),format='%(asctime)s [%(levelname)s]: %(message)s',  level=logging.INFO)
    check_bal(nrg_vars)

if __name__ == "__main__":
    main()