import requests
import json
import smtplib
from email.message import EmailMessage
import datetime
import configparser
from os import environ
from twilio.rest import Client

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
        "log_file_loc": config['LOGS']['INFO'],
        #email vars
        "email_from": config['EMAIL']['EMAIL_FROM'],
        "email_to": config['EMAIL']['EMAIL_TO'],
        "email_pass": environ.get('GMAIL_PWD'),
        "email_host": config['EMAIL']['EMAIL_HOST'],
        "email_port": config['EMAIL']['EMAIL_PORT'],
        #twilio vars
        "twilio_sid": environ.get('TWILIO_SID'),
        "twilio_auth": environ.get('TWILIO_AUTH'),
        "twilio_from": environ.get('TWILIO_FROM'),
        "twilio_to": environ.get('TWILIO_TO')
        
    }
    return nrg_vars


def send_text_msg(nrg_vars, msg):
    client = Client(nrg_vars.get('twilio_sid'), nrg_vars.get('twilio_auth'))

    client.messages \
    .create(
         body = msg,
         from_ = nrg_vars.get('twilio_from'),
         to = nrg_vars.get('twilio_to')
     )

def get_email_message(subject, frm, to):
    #create EmailMessage
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = frm
    msg['To'] = to
    return msg

def get_email_server(email_host, email_port, email_pass, email_from):
    #setup email
    s = smtplib.SMTP(host=email_host, port=email_port)
    s.starttls()
    s.login(email_from, email_pass)
    return s


def check_bal(nrg_vars): 
    #file to store balance
    try:
        bal_file = open(nrg_vars.get("bal_file_loc"), "r+")
    except FileNotFoundError:
        bal_file = open(nrg_vars.get("bal_file_loc"), "w+")

    log_file = open(nrg_vars.get("log_file_loc"), "a+")

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

    #get email message
    #msg = get_email_message("NRG Balance Update", nrg_vars.get("email_from"), nrg_vars.get("email_to"))

    #bad status, set msg_content with json response
    if (status == 0):
        #msg.set_content("Bad status returned. Please see json response: \n" + str(response.json()))
        log_file.write(str(datetime.datetime.now()) + ": Error occured, bad status returned: " + str(response.json)+"\n")
    #save response
    else:
        #check if cur_bal has increased from last check
        if (cur_bal > prev_bal):
            #set email content
            msg_body = "New balance increased: Previous Balance = " + str(prev_bal) + ", New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)\n"
            #msg.set_content("New balance increased:\nPrevious Balance = " + str(prev_bal) + "\nNew Balance = " + str(cur_bal) + "\n${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)")
            log_file.write(str(datetime.datetime.now()) + ": >>> " + msg_body)
            
            #overwrite prev_bal with cur_bal
            bal_file.seek(0)
            bal_file.write(str(cur_bal))

            #send text message
            send_text_msg(nrg_vars, "NRG Balance Update\n"+msg_body)

            #send email
            #try:
            #    get_email_server(nrg_vars.get("email_host"), nrg_vars.get("email_port"), nrg_vars.get("email_pass"), nrg_vars.get("email_from")).send_message(msg)
            #except Exception as err:
            #    log_file.write(str(datetime.datetime.now()) + ": ERROR Sending email: " + str(err) + " >>> New balance increased. Previous Balance = " + str(prev_bal) + ",  New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)"  + "\n")
        else:
        #no change
            msg_body = "No change in balance from last check. Previous Balance = " + str(prev_bal) + " and New Balance = " + str(cur_bal) + ", ${:0,.2f}".format(cur_bal*usd_xchng) + " USD (@{:0,.2f}".format(usd_xchng) + "/NRG)" +  "\n"
            #send_text_msg(nrg_vars, "NRG Balance Update\n"+msg_body)
            log_file.write(str(datetime.datetime.now()) + ": " + msg_body)

    #file cleanup
    bal_file.flush()
    bal_file.close()
    log_file.flush()
    log_file.close()

def main():
    #print("IN MAIN ...")
    nrg_vars = get_vars(get_config())
    check_bal(nrg_vars)

if __name__ == "__main__":
    main()