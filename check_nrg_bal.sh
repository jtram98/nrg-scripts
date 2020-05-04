#!/bin/sh

#values for scripts
#create a file called private_env.sh with actual values. this is provided as a guide. DO NOT check in sensitive info to git
export GMAIL_PWD=<GMAIL PWD>
export NRG_ADDR=<NRG WALLET ADDR>
export NRG_INI_PATH=<INI PATH>
export TWILIO_SID=<TWILIO SID>
export TWILIO_AUTH=<TWILIO AUTH>
export TWILIO_FROM=<FROM PHONE>
export TWILIO_TO=<TO PHONE>
export SENDGRID_API_KEY=<SENDGRID_API_KEY>
export SENDGRID_FROM=<SENDGRID_FROM>
export SENDGRID_TO=<SENDGRID_TO>

#for use on Windows Bash
#export WSLENV=$GMAIL_PWD/w:$NRG_ADDR/w:$NRG_INI_PATH/wp:$TWILIO_SID/w:$TWILIO_SID/w:$TWILIO_FROM/w:$TWILIO_TO/w:
#echo $WSLENV
/path/to/python3.x /path/to/script/check_nrg_bal.py
