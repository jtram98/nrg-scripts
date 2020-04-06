#!/bin/sh


export WSLENV=$GMAIL_PWD/w:$NRG_ADDR/w:$NRG_INI_PATH/wp:
echo $WSLENV
/usr/bin/python3.6 /home/johnt/nrg-scripts/check_bal.py
