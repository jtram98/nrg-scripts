#!/bin/sh

#values for scripts
export GMAIL_PWD=<GMAIL PWD>
export NRG_ADDR=<NRG WALLET ADDR>
export NRG_INI_PATH=<INI PATH>
export TWILIO_SID=<TWILIO SID>
export TWILIO_AUTH=<TWILIO AUTH>
export TWILIO_FROM=<FROM PHONE>
export TWILIO_TO=<TO PHONE>
export WSLENV=$GMAIL_PWD/w:$NRG_ADDR/w:$NRG_INI_PATH/wp:$TWILIO_SID/w:$TWILIO_SID/w:$TWILIO_FROM/w:$TWILIO_TO/w:
echo $WSLENV
/usr/bin/python3.6 /path/to/script/check_bal_v2.py
