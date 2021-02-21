#!/usr/bin/env python3
from pathlib import Path
import sys, time, threading
import pycurl, json
from io import BytesIO
if __name__ == '__main__':
    sys.path.append('../')
from relay.utils import *
from collections import OrderedDict
from datetime import datetime, timedelta

class Curl_sensor(Configured):

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.temp = self.err_temp
        self.running = False
        self.monitor_period=600
        self.stop_threads = False
        self.read()
        self.last_read = datetime.now()

    def __str__(self):
        return f'Remote sensor {self.name} = {self.temp} C\n'

    def check_device(self):
        return  (self.dev_path/self.data_file).exists()

    def check(self):
        if self.check_device():
            self.read()
            if self.temp is not None:
                return True
        return False

    def read(self):
        Info('Updating from web')
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.url)
        recvd=BytesIO()
        curl.setopt(curl.WRITEDATA, recvd)
        curl.perform()
        curl.close()
        data = json.loads(recvd.getvalue())
        try:
            data = json.loads(recvd.getvalue())
            self.temp = float(data['temp'])
            return data
        except:
            return {}

    def start_monitor_thread(self):
        print('\nStarting sensors monitor thread')
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target = self.monitor)
            self.thread.name = 'Curl_sensor_monitor'
            self.thread.start()
        else:
            print('\nWARNING: Curl_sensor monitor is already running.')

    def monitor(self):
        while not self.stop_threads:
            if datetime.now() >= self.last_read+timedelta(seconds=self.monitor_period):
                self.read()
                self.last_read = datetime.now()
            time.sleep(0.1)


    def log_data(self):
        if self.temp is not None:
            ttemp = self.temp
        else:
            ttemp = self.err_temp 
        return OrderedDict([(self.name, ttemp)])

    def quit(self):
        Info('\nStopping Curl_sensor monitor thread.')
        self.stop_threads = True
        self.thread.join()
        self.running = False
        Info('\nStopped Curl_sensor monitor thread')




if __name__ == '__main__':
    from datetime import datetime
    from time import sleep

    sensor = Curl_sensor('test', 'http://minglarn.se/ha_sensor.php')

    sensor.start_monitor_thread()

    while True:
        try:
            Info(sensor)
            sleep(1)
        except KeyboardInterrupt:
            sensor.quit()
            sys.exit(0)
            break

