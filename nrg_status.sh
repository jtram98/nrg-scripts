#!/bin/bash -l
export PATH=$PATH:$HOME/energi3/bin
#original Author: @ProjectJourneyman

#updated to use sendgrid
#the following env variables defined:
#   SENDGRID_API_KEY
#   TO_EMAIL_ADDR
#   FROM_EMAIL_ADDR 

#isRunning=$(energi3 --exec "masternode.masternodeInfo('MyAddress')" attach 2>/dev/null | grep -Fq "isActive: true" && echo $?)

isStaking=$(energi3 --exec "miner.stakingStatus()" attach 2>/dev/null | grep -Fq "staking: true" && echo $?)

msg="not running"

if [[ $isRunning == 0 && $isStaking == 0 ]]; then
        msg="running and staking"
elif [[ $isStaking == 0 ]]; then
    msg="staking but masternode not active"
fi

echo $msg
#send notification
email_data='{"personalizations": [{"to": [{"email": "'${TO_EMAIL_ADDR}'"}]}],"from": {"email": "'${FROM_EMAIL_ADDR}'"},"subject": "NRG Staking Status","content": [{"type": "text/plain", "value":"'${msg}'"}]}'

curl --request POST \
    --url https://api.sendgrid.com/v3/mail/send \
    --header "Authorization: Bearer $SENDGRID_API_KEY" \
    --header 'Content-Type: application/json' \
    --data "$email_data"
