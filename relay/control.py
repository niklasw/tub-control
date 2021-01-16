#!/usr/bin/env python3

import time, threading
from relay.timer2 import Timer
from sensors import TSensors, ds18b20
from relay.utils import *

from relay.logger import logger


# Fixme: make relay control independent of buttons. Control relay directly
# instead.
class Relay_control:

    rid_pump = 0
    rid_heat = 1
    rid_aux = 2

    def __init__(self, relay):
        self.stop_threads = False
        self.relay = relay
        self.buttons = Relay_buttons(relay, self.rid_pump, self.rid_heat, self.rid_aux)
        self.timer = Timer()
        self.sensors = TSensors(ds18b20)
        self.sensors.read()

        self.buttons.get_status()

        self.set_temperatures = {'pool':18, 'pump': 18}
        Info('Creating Relay_control')
        
    def pump_running(self):
        return self.relay.get_port_status(self.rid_pump)
    def heat_running(self):
        return self.relay.get_port_status(self.rid_heat)
    def aux_running(self):
        return self.relay.get_port_status(self.rid_aux)

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
        self.thread.start()

    def monitor_inputs(self):
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
                    if self.buttons.pump_on and not self.timer.on and not self.timer.interval:
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
        Info('Thread monitor_inputs stopped')

                

    def quit(self):
       Info('\nStopping control thread')
       #self.timer.quit()
       #self.sensors.quit()
       self.stop_threads = True
       self.thread.join()
       Info('\nStopped control thread')

                   
class Relay_buttons:
    def __init__(self, relay, pump_id, heat_id, aux_id):
        self.relay = relay
        self.pump_id = pump_id
        self.heat_id = heat_id
        self.aux_id = aux_id
        self.pump_on = None
        self.heat_on = None
        self.aux_on = None
        Info('Creating Relay_buttons')

    def get_status(self):
        self.pump_on = self.relay.get_port_status(self.pump_id)
        self.heat_on = self.relay.get_port_status(self.heat_id)
        self.aux_on = self.relay.get_port_status(self.aux_id)

    def heat(self):
        self.get_status()
        if self.heat_on:
            self.relay.off(self.heat_id)
        else:
            if not self.pump_on:
                self.relay.on(self.pump_id)
            self.relay.on(self.heat_id)
    
    def pump(self):
        self.get_status()
        if self.pump_on:
            if not self.heat_on:
                self.relay.off(self.pump_id)
        else:
            self.relay.on(self.pump_id)

    def aux(self):
        self.get_status()
        if self.aux_on:
            self.relay.off(self.aux_id)
        else:
            self.relay.on(self.aux_id)


