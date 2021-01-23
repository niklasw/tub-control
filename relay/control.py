#!/usr/bin/env python3

import time, threading
from relay.timer2 import Timer
from sensors import TSensors, ds18b20
from relay.utils import *

from relay.logger import DbLogger
from pathlib import Path
from collections import OrderedDict


# Fixme: make relay control independent of buttons. Control relay directly
# instead.
class Relay_control(Configured):

    def __init__(self, relay):
        self.stop_threads = False
        self.relay = relay
        self.buttons = Relay_buttons(relay)
        self.timer = Timer()
        self.sensors = TSensors(ds18b20)
        self.sensors.read()

        self.buttons.get_status()

        self.set_temperatures = {'pool':18, 'pump': 3}
        Info('Creating Relay_control')
        
    def start_timer(self):
        if not self.timer.running:
            self.timer.go()

    def start_sensors(self):
        if not self.sensors.running:
            self.sensors.start_monitor_thread()

    def start_monitor_thread(self):
        #self.start_timer()
        #self.start_sensors()
        self.thread = threading.Thread(target = self.monitor_inputs)
        self.thread.name = 'control_monitor'
        self.thread.daemon = True
        self.thread.start()

    def monitor_inputs(self):
        logger = DbLogger(Path(self.database), \
                          [self.buttons, self.timer, self.sensors, self.relay, self])

        while not self.stop_threads:
            time.sleep(0.1)
            self.buttons.get_status()
            self.timer.get_status()
            Debug(self.timer)
            #if self.timer.active() and not self.heat_on:
            if self.timer.active:
                if self.timer.on:
                    if not self.buttons.pump_on:
                        self.buttons.pump()
                        Debug(f'timer turns ON pump {self.timer.duration}')
                elif self.buttons.pump_on:
                    self.buttons.pump()
                    Debug(f'timer turns OFF pump {self.timer.duration}')
                    if not self.timer.interval:
                        self.timer.stop()

            self.sensors.get_status()
            Debug(self.sensors)
            self.buttons.get_status()
            if self.sensors.active:
                temps = self.sensors.values
                if temps['pump'] < self.set_temperatures['pump']:
                    if not self.buttons.pump_on:
                        self.timer.set(0,10)
                else:
                    if self.buttons.pump_on and not (self.timer.on or self.timer.interval):
                        self.buttons.pump()
                        self.timer.active = False
                        Debug('sensor turns OFF pump')

                if temps['pool'] < self.set_temperatures['pool']:
                    if not self.buttons.heat_on:
                        self.buttons.heat()
                        Debug('sensor turns ON heat')
                elif temps['pool'] >= self.set_temperatures['pool']+1:
                    if self.buttons.heat_on:
                        self.buttons.heat()
                        Debug('sensor turns OFF heat')

            logger.update()
            
        Info('Thread monitor_inputs stopped')

                

    def quit(self):
       Info('\nStopping control thread')
       #self.timer.quit()
       #self.sensors.quit()
       self.stop_threads = True
       self.thread.join()
       Info('\nStopped control thread')

    def log_data(self):
        names = ['set_temp_pump', 'set_temp_pool']
        values= [self.set_temperatures['pump'], self.set_temperatures['pool']]
        return OrderedDict(zip(names,values))

                   
class Relay_buttons(Configured):

    def __init__(self, relay):
        self.relay = relay
        self.pump_on = None
        self.heat_on = None
        self.aux_on = None
        Info('Creating Relay_buttons')

    def get_status(self):
        self.pump_on = self.relay.get_port_status(self.rid_pump)
        self.heat_on = self.relay.get_port_status(self.rid_heat)
        self.aux_on = self.relay.get_port_status(self.rid_aux)

    def heat(self):
        self.get_status()
        if self.heat_on:
            self.relay.off(self.rid_heat)
        else:
            if not self.pump_on:
                self.relay.on(self.rid_pump)
            self.relay.on(self.rid_heat)
    
    def pump(self):
        self.get_status()
        if self.pump_on:
            if not self.heat_on:
                self.relay.off(self.rid_pump)
        else:
            self.relay.on(self.rid_pump)

    def aux(self):
        self.get_status()
        if self.aux_on:
            self.relay.off(self.rid_aux)
        else:
            self.relay.on(self.rid_aux)

    def log_data(self):
        names = ['aux_on', 'pump_on', 'heat_on']
        values= [int(a) for a in [self.aux_on, self.pump_on, self.heat_on]]
        return OrderedDict(zip(names,values))

