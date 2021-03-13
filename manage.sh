#!/usr/bin/env bash

source $PWD/venv/bin/activate
TUB_SERVER='192.168.10.210'
TUB_PORT=5000
LOG_NAME=tub-control
LOG_FILE=$LOG_NAME.log

function start_app()
{
	if [ -f $LOG_FILE ]
	then
	    mv $LOG_FILE ${LOG_NAME}.$(date +%s).log
	fi
	
	python3 tub-control.py > $LOG_FILE 2>&1 &
}

function stop_app()
{
	if [ -f $LOG_FILE ]
	then
		TUB_PID=$(awk '$1 == "PID:" {print $2}' $LOG_FILE)

		read -p "Kill process $TUB_PID? y/[n]" ans

		if [[ "$ans" == "y" ]]
		then
			kill $TUB_PID
		else
			echo "No action"
		fi
	else
		echo "No log file found ($LOG_FILE). Can not stop."
	fi
}

TASK=$1

case $TASK in
	start|run)
		start_app
		;;
	stop)
		stop_app
		;;
	*)
		echo "manage.sh [start|run|stop]"
		;;
esac
