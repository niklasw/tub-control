#!/usr/bin/env bash

source $PWD/venv/bin/activate
TUB_SERVER='192.168.10.210'
TUB_PORT=5000
python3 tub-control.py > tub-control.log 2>&1 &
