import requests
import json
import datetime
import configparser
from os import environ
from twilio.rest import Client
import logging
from enum import IntEnum

#notify_type enum
class Notification(IntEnum):
    NONE = 0
    EMAIL = 1
    TEXT = 2
    BOTH = 3


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
        "notify_type": config['NOTIFICATION']['NOTIFY_TYPE'],
        #twilio vars
        "twilio_sid": environ.get('TWILIO_SID'),
        "twilio_auth": environ.get('TWILIO_AUTH'),
        "twilio_from": environ.get('TWILIO_FROM'),
        "twilio_to": environ.get('TWILIO_TO')
    }
    return nrg_vars

def notify(nrg_vars, msg):
    if (int(nrg_vars.get('notify_type')) == int(Notification.TEXT)):
        text_notification(nrg_vars,msg)
    elif(int(nrg_vars.get('notify_type')) == int(Notification.EMAIL)):
        #email
        print("send email")
    else:
        #send both email and text
        print("send both")


def text_notification(nrg_vars, msg):
    client = Client(nrg_vars.get('twilio_sid'), nrg_vars.get('twilio_auth'))

    client.messages.create(
         body = msg,
         from_ = nrg_vars.get('twilio_from'),
         to = nrg_vars.get('twilio_to')
     )

def check_bal(nrg_vars): 
    #file to store balance
    try:
        bal_file = open(nrg_vars.get("bal_file_loc"), "r+")
    except FileNotFoundError:
        bal_file = open(nrg_vars.get("bal_file_loc"), "w+")

    #prev bal
    prev_bal = float(bal_file.read() or 0)

    #get balance response & status
    response = requests.get(nrg_vars.get("base_url") + nrg_vars.get("get_bal") + nrg_vars.get("wallet_addr"))
    status = float(response.json()["status"])

    #get USD value & status
    usd_response = requests.get(nrg_vars.get("base_url") + nrg_vars.get("get_usd"))
    usd_xchng = float(usd_response.json()["result"]["ethusd"] or 0)

    #curent balance
    cur_bal = float((response.json()["result"] or 0)) / 10**18

    #bad status, set msg_content with json response
    if (status == 0):
        logging.error("Error occured, bad status returned: " + str(response.json()))
    #save response
    else:
        #check if cur_bal has increased from last check
        if (cur_bal == prev_bal):
            #no change
            msg_body = "No change in balance from last check. Previous Balance = " + str(prev_bal) + " and New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)"
            logging.info(msg_body)
        elif (cur_bal > prev_bal):
            #set message content
            msg_body = "New balance increased: Previous Balance = " + str(prev_bal) + ", New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)"
            logging.info(">>> "+msg_body)
            
            #overwrite prev_bal with cur_bal
            bal_file.seek(0)
            bal_file.write(str(cur_bal))

            #send notification
            try:
                notify(nrg_vars, "NRG Balance Update\n"+msg_body)
            except Exception as err:
                logging.error(str(err))
        else:
        #cur bal is less than previous balance, may indicate an issue with the NRG node/network
            msg_body = "Current blance is less than previous balance. Pleae check the block explorer. Previous Balance = " + str(prev_bal) + " and New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)"
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