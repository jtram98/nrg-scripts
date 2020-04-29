#!/bin/bash

threshold=80
result=`df -BG --output=source,used,avail,pcent /dev/vda1 | grep -v "Filesystem" | awk '{ print $4}' | sed 's/%//g'`

if [ "$result" -gt  "$threshold" ]; then
	echo "disk usage ${result}% > ${threshold}%"
else
	echo "disk usage ${result}% <  ${threshold}%"
fi
