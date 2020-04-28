#!/bin/bash

export PATH=$PATH:$HOME/energi3/bin

#isRunning=$(energi3 --exec "masternode.masternodeInfo('MyAddress')" attach 2>/dev/null | grep -Fq "isActive: true" && echo $?)

isStaking=$(energi3 --exec "miner.stakingStatus()" attach 2>/dev/null | grep -Fq "staking: true" && echo $?)

if [[ $isRunning == 0 && $isStaking == 0 ]]; then
        echo "running and staking"
elif [[ $isStaking == 0 ]]; then
    echo "staking but masternode not active"
        #send notification
else
        echo "not running"
        #send notification
fi
