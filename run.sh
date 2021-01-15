#!/usr/bin/env bash

source $PWD/venv/bin/activate
python3 pool-control.py > pool-control.log 2>&1 &
sleep 1
cat pool-control.log
