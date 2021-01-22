#!/usr/bin/env python3
from relay.plotter import Plotter

def init_controls():
    from relay.seeed_relay import Relay
    from relay.control import Relay_control
    relay = Relay()

    control = Relay_control(relay)
    control.start_monitor_thread()

    return control

