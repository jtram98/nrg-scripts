#!/bin/bash
#original Author: @ProjectJourneyman
#updated to use send grid
#export PATH=$PATH:$HOME/energi3/bin

#isRunning=$(energi3 --exec "masternode.masternodeInfo('MyAddress')" attach 2>/dev/null | grep -Fq "isActive: true" && echo $?)

isStaking=$(/home/nrgstaker/energi3/bin/energi3 --exec "miner.stakingStatus()" attach 2>/dev/null | grep -Fq "staking: true" && echo $?)

msg="not running"

if [[ $isRunning == 0 && $isStaking == 0 ]]; then
        msg="running and staking"
elif [[ $isStaking == 0 ]]; then
    msg="staking but masternode not active"
fi

#send notification
echo $msg
email_data='{"personalizations": [{"to": [{"email": "email_addr"}]}],"from": {"email": "email_addr"},"subject": "NRG Staking Status","content": [{"type": "text/plain", "value":"'${msg}'"}]}'
curl --request POST a
    --url https://api.sendgrid.com/v3/mail/send \
    --header "Authorization: Bearer $SENDGRID_API_KEY" \
    --header 'Content-Type: application/json' \
    --data "$email_data"
