#!/usr/bin/env bash

source $PWD/venv/bin/activate
python3 tub-control.py > tub-control.log 2>&1 &
