import requests
import json
import smtplib
from email.message import EmailMessage
import datetime
import configparser
from os import environ

#read config
config = configparser.ConfigParser()   
config.read((environ.get('NRG_INI_PATH')+'config.ini'))
print ("addr:*"+environ.get('NRG_ADDR')+"*")

#set up vars
base_url = config['API']['BASE_URL']
get_bal = config['API']['GET_BAL']
wallet_addr = environ.get('NRG_ADDR')
bal_file_loc = config['LOGS']['BALANCE']
log_file_loc = config['LOGS']['INFO']

#email vars
email_from = config['EMAIL']['EMAIL_FROM']
email_to = config['EMAIL']['EMAIL_TO']
email_pass = environ.get('GMAIL_PWD')
email_host = config['EMAIL']['EMAIL_HOST']
email_port = config['EMAIL']['EMAIL_PORT']

#create EmailMessage
msg = EmailMessage()
msg['Subject'] = "NRG Balance Update"
msg['From'] = email_from
msg['To'] = email_to

#setup email
s = smtplib.SMTP(host=email_host, port=email_port)
s.starttls()
s.login(email_from, email_pass)


#file to store balance
bal_file = open(bal_file_loc, "r+")
log_file = open(log_file_loc, "a+")

#prev bal
prev_bal = float(bal_file.read() or 0)

#get balance response
response = requests.get(base_url+get_bal+wallet_addr)

#response status
status = float(response.json()["status"])

#curent balance
cur_bal = float((response.json()["result"] or 0)) / 10**18

#bad status, set msg_content with json response
if (status == 0):
    msg.set_content("Bad status returned. Please see json response: \n" + str(response.json()))
    log_file.write(str(datetime.datetime.now()) + ": Error occured, bad status returned: " + str(response.json)+"\n")
#save response
else:
    #check if cur_bal has increased from last check
    if (cur_bal > prev_bal):
        #set email content
        msg.set_content("New balance increased ... " + str(cur_bal) + " > " + str(prev_bal))
        log_file.write(str(datetime.datetime.now()) + ": New balance increased ... " + str(cur_bal) + " > " + str(prev_bal) + "\n")
        
        #overwrite prev_bal with cur_bal
        bal_file.seek(0)
        bal_file.write(str(cur_bal))

        #send email
        s.send_message(msg)
    else:
       #no change
        log_file.write(str(datetime.datetime.now()) + ": No change in balance from last check. cur_bal = " + str(cur_bal) + " and prev_bal = " + str(prev_bal) +"\n")

#file cleanup
bal_file.flush()
bal_file.close()
log_file.flush()
log_file.close()