#!/usr/bin/bash

[[ -n "$1" ]] || { echo "log file argument missing"; exit 1; }

TUB_PID=$(awk '$1 == "PID:" {print $2}' $1)

read -p "Kill process $TUB_PID? y/[n]" ans

if [[ "$ans" == "y" ]]
then
	kill $TUB_PID
else
	echo "No action"
fi
