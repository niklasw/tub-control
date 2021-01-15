#!/usr/bin/python3

import sys, signal, time
from pathlib import Path
from datetime import datetime, timedelta
import threading


class Timer:

    units = ['d', 'h', 'm', 's']

    def __init__(self, interval=0, duration=0):
        self.stop_threads = False
        self.interval = interval # seconds
        self.duration = duration     # seconds
        self.start_time = datetime.now()
        self.on = False
        self.thread = None
        self.running = False
        self.interval_choices = [0, 60, 3600, 7200, 14400, 86400]
        self.duration_choices = [0, 10, 600, 1200, 3600, 14400]
        self.intervals = dict(zip(self.interval_choices,
                                  [self.sec_to_string(a) \
                                      for a in self.interval_choices]))
        self.intervals[0] = 'off'
        self.durations = dict(zip(self.duration_choices,
                                  [self.sec_to_string(a) \
                                      for a in self.duration_choices]))
        self.durations[0] = 'off'
        self.remaining = 0
        self.active = False
        self.manual = False
        print('Creating timer')

    def __str__(self):
        s = f'Timer status: active = {self.active} on = {self.on}\n'
        s+= f'\tinterval = {self.interval}\n'
        s+= f'\tduration = {self.duration}, remaining = {self.remaining}\n'
        return s


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

    def get_status(self):
        if self.active:
            up_time = datetime.now() - self.start_time
            self.remaining = max(self.duration - up_time.seconds, 0)
            self.on = True if self.remaining > 0 else False
            if self.interval and up_time.seconds > self.interval:
                self.start_time = datetime.now()
            # deactivate if no time left and not repeating
            if not self.on and not self.interval:
                self.duration = 0
                #self.active = False
        else:
            self.on = False

    def tick(self):
        if self.active:
            time.sleep(1e-1)
            up_time = datetime.now() - self.start_time
            self.remaining = self.duration - up_time.seconds
            self.on = True if self.remaining >= 0 else False
            if self.interval and up_time.seconds >= self.interval:
                self.start_time = datetime.now()
            # deactivate if no time left and not repeating
            if not self.on and not self.interval:
                self.duration = 0
                self.active = False
        else:
            self.on = False

    def __run__(self):
        self.running = True
        while not self.stop_threads:
            self.tick()
        self.running = False

    def go(self):
        self.thread = threading.Thread(target = self.__run__)
        self.thread.name = 'timer_thread'
        self.thread.start()

    def set(self, interval, duration):
        self.active = True if duration > 0 else False
        self.interval = interval
        self.duration = duration
        self.start_time = datetime.now()
        print('timer set', self.interval, self.duration)

    def reset(self):
        self.active = False
        self.interval = 0
        self.duration = 0
        self.start_time = 0

    def quit(self):
        self.reset()
        print('\nStopping timer thread')
        self.stop_threads = True
        self.thread.join()
        print('\nStopped timer thread')

if __name__ == '__main__':
    t = Timer(20, 5)

    print(t.intervals)
    print(t.durations)

    t.go()
    t.set(10,2)

    while True:
        try:
            #input('Check timer (press enter):')
            time.sleep(0.5)
            print(datetime.now().strftime('%S'),t.on)
        except KeyboardInterrupt:
            t.quit()
            sys.exit(0)
            break

