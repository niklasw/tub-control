#!/usr/bin/python3

import sys, signal, time
from pathlib import Path
from datetime import datetime, timedelta
import threading
from relay.utils import *
from collections import OrderedDict


class Timer(Configured):

    units = ['d', 'h', 'm', 's']
    interval_choices = [0, 60, 3600, 7200, 14400, 86400]
    duration_choices = [0, 10, 600, 1200, 3600, 14400]

    def __init__(self, interval=0, duration=0):
        self.interval = interval    # seconds
        self.duration = duration    # seconds
        self.intervals = dict(zip(self.interval_choices,
                                  [self.sec_to_string(a) \
                                      for a in self.interval_choices]))
        self.intervals[0] = 'off'
        self.durations = dict(zip(self.duration_choices,
                                  [self.sec_to_string(a) \
                                      for a in self.duration_choices]))
        self.durations[0] = 'off'
        self.active = False
        self.on = False

        self.start_time = datetime.now()
        self.next_start = self.start_time + timedelta(seconds = self.interval)

        self.thread = None
        self.stop_threads = True
        Info('Creating Timer')

    def __str__(self):
        s = f'Timer status: active = {self.active} on = {self.on}\n'
        s+= f'\tinterval = {self.interval}\n'
        s+= f'\tduration = {self.duration}, remaining = {self.remaining()}\n'
        return s

    def update(self):
        self.start_time = self.next_start
        self.next_start += timedelta(seconds = self.interval)

    def get_status(self):
        now = datetime.now()
        if now > self.next_start:
            self.update()
        if self.active:
            stop_time = self.start_time + timedelta(seconds=self.duration)
            if now < stop_time:
                self.on = True
            else:
                self.on = False
        else:
            self.on = False

    def remaining(self):
        if self.on:
            stop_time = self.start_time + timedelta(seconds=self.duration)
            return (stop_time - datetime.now()).total_seconds()
        else:
            return 0

    def set(self, interval, duration):
        self.active = True if duration > 0 else False
        self.start_time = datetime.now()
        self.next_start = self.start_time + timedelta(seconds = self.interval)
        self.interval = interval
        self.duration = duration
        Debug(f'timer set {self.interval}, {self.duration}')

    def stop(self):
        self.active = False
        self.interval = 0
        self.duration = 0
        self.start_time = datetime.now()

    def spawn_thread(self):
        if self.thread is None:
            self.stop_threads = False
            self.thread = threading.Thread(target = self.tick)
            self.thread.name = 'timer'
            self.thread.start()
        else:
            Error('Only allowed to spawn one thread.')
            self.stop_thread()
            sys.exit(1)

    def stop_thread(self):
        self.stop_threads = True
        self.thread.join()

    def tick(self):
        while True:
            time.sleep(0.01)
            self.get_status()
            if self.stop_threads:
                break

    def sec_to_string(self, secs):
        td = timedelta(seconds=secs)
        days = td.days
        td -= timedelta(days=days)
        tl = [int(a) for a in str(td).split(':')]
        r_units = list(reversed(self.units))
        r_list = []
        for i,v in enumerate(tl[::-1]):
            if v != 0:
                r_list.append('{} {}'.format(v, r_units[i]))
        d = '{} d'.format(days) if days > 0 else ''
        r_list.append(d)
        s = ' '.join(reversed(r_list))
        return s.strip()

    def log_data(self):
        return OrderedDict([('timer',int(self.on))])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def without_thread():
    t = Timer(0, 0)
    t.set(interval=10, duration=5)
    t2 = Timer(0, 0)
    t2.set(interval=10, duration=5)

    t2.spawn_thread()

    while True:
        try:
            time.sleep(1)
            t.get_status()
            print(f'{datetime.now().strftime("%S")}\n{t}\n{t2}')
        except KeyboardInterrupt:
            t2.stop_thread()
            break

if __name__ == '__main__':
    without_thread()
