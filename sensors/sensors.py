#!/usr/bin/env python3
from pathlib import Path
import sys, time, threading
from relay.utils import *
from collections import OrderedDict

class ds18b20:
    devices_path  = Path('/sys/bus/w1/devices')
    device_prefix = '28-'
    slave_file = 'w1_slave'
    precision = 0.001
    err_temp = -100

    def __init__(self, device_path):
        self.dev_path = device_path
        self.data_file = self.dev_path/self.slave_file
        self.temp = None
        # id is the device directory name
        self.id = self.dev_path.name
        self.name = TSensors.names[self.id]
        self.read()
        

    def check_device(self):
        return  (self.dev_path/self.data_file).exists()

    def check(self):
        if self.check_device():
            self.read()
            if self.temp is not None:
                return True
        return False

    def read(self):
        if not self.check_device():
            self.temp = self.err_temp
            return self.err_temp

        import re
        lines = []
        # Give it a few tries
        for i in range(10):
            try:
                with self.data_file.open('r') as fp:
                    lines = fp.readlines()
                    read_ok = lines and lines[0].strip()[-3:] == 'YES'
                    if read_ok:
                        break
                    time.sleep(0.1)
            except:
                Info('device read problem, retrying')
        pat1 = re.compile('.*\st=(-?[0-9]+)')

        temp = self.err_temp

        for line in lines:
            match = pat1.search(line)
            if match:
                t = match.group(1)
                try:
                    temp = int(t)*self.precision
                except:
                    print('Could not read temperature')
        self.temp = temp
        return self.temp

    def log_data(self):
        if self.temp is not None:
            ttemp = self.temp
        else:
            ttemp = self.err_temp 
        return OrderedDict([(self.name, ttemp)])


class TSensors(list, Configured):

    # Try this to prevent multiple instances to monitor
    running = False
    # move to some config
    names = {'28-3c01b607ee7e':'pool',
             '28-3c01b607b5a1':'pump',
             '28-0120358fb53e':'pool',
             '28-012035906bf0':'pump'}

    def __init__(self, sensor_type):
        self.type = sensor_type
        self.values = {}
        self.monitor_period = 1
        self.stop_threads = False
        self.active = False
        self.ok = False

        super().__init__( (sensor_type(a) for a in self.ls_devices()) )
        Info('Creating TSensors')
        self.values = {'pool':100,'pump':100}

    def __str__(self):
        s = f'Sensors status: active = {self.active} ok = {self.ok}\n'
        for s_id, name in self.names.items():
            if name in self.values:
                s += f'\t{name} ({s_id}) temperature = {self.values[name]}\n'
        return s

    def ls_devices(self):
        devs = Path(self.type.devices_path).glob(self.type.device_prefix+'*')
        for device in devs:
            slave_file = Path(device, self.type.slave_file)
            if slave_file.exists():
                yield device

    def read(self):
        for sensor in self:
            self.values[sensor.name] = sensor.read()

    def get_status(self):
        self.read()
        self.ok = not None in self.values.values()
        self.active = self.active and self.ok

    def start_monitor_thread(self):
        print('\nStarting sensors monitor thread')
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target = self.monitor)
            self.thread.name = 'sensors_monitor'
            self.thread.start()
        else:
            print('\nWARNING: TSensors monitor is already running.')

    def monitor(self):
        while not self.stop_threads:
            self.read()
            time.sleep(self.monitor_period)

    def quit(self):
       print('\nStopping monitor thread. This can take some time.')
       self.stop_threads = True
       self.thread.join()
       self.running = False
       print('\nStopped monitor thread')

    def log_data(self):
        odict = OrderedDict()
        for s in self:
            odict.update(s.log_data())
        return odict


if __name__ == '__main__':
    from datetime import datetime

    sensors = TSensors(ds18b20)
    sensors.read()
    sensors.start_monitor_thread()

    while True:
        try:
            #input('Check timer (press enter):')
            time.sleep(1)
            print('{} {}\n{}'.format(datetime.now().strftime('%S'), sensors.running, sensors))
        except KeyboardInterrupt:
            sensors.quit()
            sys.exit(0)
            break





