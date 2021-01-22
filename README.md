# tub-control
Flask app to control pump and heater using raspberry pi equipped with a relay
board and temp sensors. Web interface for on/off control via buttons, timer
or sensors.

## Requires
> Python3

> Raspberry pi with a seeed relay board: https://wiki.seeedstudio.com/Raspberry_Pi_Relay_Board_v1.0/
> and "one wire" temperature sensors type ds18b20

> Seems like raspbian needs some system packages for numpy to run:
> - libatlas-base-dev
> - libopenjp2-7-dev
> - libtiff5

## In this folder, do the following:
### Create a python container/environment
`python3 -m venv venv`
### Enter the sandbox
`source venv/bin/activate`
### Install all python stuff needed
`pip install -r requirements.txt`
### Start the server
`python3 ./tub-control.py'
