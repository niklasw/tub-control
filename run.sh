#!/usr/bin/env bash

source $PWD/venv/bin/activate
python3 tub-control.py > log 2>&1 &
sleep 1
cat log
