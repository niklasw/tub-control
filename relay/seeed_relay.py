#!/usr/bin/env python3
# based on code from Seeed Studio Wiki
# http://wiki.seeed.cc/Raspberry_Pi_Relay_Board_v1.0/

import sys, signal, smbus
from pathlib import Path
from datetime import datetime
try:
    from relay.utils import Debug, Error, Info
except:
    from utils import Debug, Error, Info
from collections import OrderedDict


bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

class Relay():
    global bus

    def __init__(self, state_file='/tmp/relay_state'):
        self.state_file = Path(state_file)

        self.N_PORTS = 4
        self.DEVICE_ADDRESS = 0x20
        self.DEVICE_REG_MODE1 = 0x06
        try:
            self.DEVICE_REG_DATA = \
                bus.read_byte_data(self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1)
        except:
            self.DEVICE_REG_DATA = 0xff
            try:
                self.all_off()
            except:
                Error('Relay communication error')
                sys.exit(1)

        if not self.state_file.exists():
            with self.state_file.open('w') as fp:
                now = datetime.now().strftime('%d/%m:%H.%M.%S')
                fp.write('{} {}\n'.format(now,str(bin(self.DEVICE_REG_DATA))))
        with self.state_file.open('r') as fp:
            try:
                self.__read_state__()
            except:
                Warning('failed read {0:s}'.format(self.state_file.as_posix()))

        # Storage of each ports latest trigger (file, button, timer, sensor,...)
        self.last_control = self.N_PORTS*['file']

    def __bus_write__(self):
        bus.write_byte_data(self.DEVICE_ADDRESS,
                            self.DEVICE_REG_MODE1,
                            self.DEVICE_REG_DATA)
        with self.state_file.open('a') as fp:
            now = datetime.now().strftime('%d/%m:%H.%M.%S')
            fp.write('{} {}\n'.format(now,str(bin(self.DEVICE_REG_DATA))))

    def __str__(self):
        s = '[{0:d} {0:b}] '.format(self.DEVICE_REG_DATA)
        s = s+' '.join((str(self.get_port_status(i)) for i in range(0,4)))
        return s+'\n'

    def __read_state__(self):
        with self.state_file.open('r') as fp:
            lines = fp.readlines()
            if lines:
                int_state = int(lines[-1].strip(),2)
                ds = self.DEVICE_REG_DATA
                rs = int_state
                if self.DEVICE_REG_DATA == int_state:
                    Info('Board state equals stored state {0:b} vs {1:b}'.format(ds,rs))
                else:
                    Info('Board state differs from stored state {0:b} vs {1:b}'.format(ds,rs))
                self.DEVICE_REG_DATA = int_state

    def on(self, rid):
        if rid in range(0,4):
            self.DEVICE_REG_DATA &= ~(0x1 << rid)
            self.__bus_write__()
        else:
            Info('Wrong input to Relay.on(): {}'.format(rid))
        Debug(self)

    def off(self,rid):
        if rid in range(0,4):
            self.DEVICE_REG_DATA |= (0x1 << rid)
            self.__bus_write__()
        else:
            Info('Wrong input to Relay.off(): {}'.format(rid))
        Debug(self)

    def toggle(self, rid):
        if not self.get_port_status(rid):
            self.on(rid)
        else:
            self.off(rid)
        return self.get_port_status(rid)

    def all_on(self):
        Debug('ALL ON...')
        self.DEVICE_REG_DATA &= ~(0xf << 0)
        self.__bus_write__()
        Debug(self)

    def all_off(self):
        Debug('ALL OFF...')
        self.DEVICE_REG_DATA |= (0xf << 0)
        self.__bus_write__()
        Debug(self)

    def manual_toggle(self):
        instruction = input('which relay [-]<1..4>? ')
        if instruction == '?':
            Debug(self)
            return
        elif instruction == 'q':
            sys.exit(0)

        try:
            number = int(instruction)
            relay_no = number - 1
            assert relay_no in range(0,4)
        except:
            Info('Wrong input')
            return
        self.toggle(relay_no)

    def manual_switch(self):
        instruction = input('which relay [-]<1..4>? ')
        if instruction == '?':
            Debug(self)
            return
        elif instruction == 'q':
            sys.exit(0)

        try:
            number = int(instruction)
            relay_no = number - 1 if number > 0 else number + 1
            assert relay_no in range(-4,4)
        except:
            Info('Wrong input')
            return
        if number > 0:
            self.on(relay_no)
        elif number < 0:
            self.off(-relay_no)
        elif number == 0:
            self.all_off()

    def get_port_data(self, relay_num):
        # gets the current byte value stored in the relay board
        #Debug('Reading relay status value for relay {}'.format(relay_num))
        # do we have a valid port?
        if relay_num in range(0,self.N_PORTS):
            # read the memory location
            self.DEVICE_REG_DATA = \
                bus.read_byte_data(self.DEVICE_ADDRESS, self.DEVICE_REG_MODE1)
            # return the specified bit status
            return self.DEVICE_REG_DATA
        else:
            # otherwise (invalid port), always return 0
            Error("Specified relay port is invalid")
            return 0

    def get_port_status(self, relay_num):
        # determines whether the specified port is ON/OFF
        #Debug('Checking status of relay {0}'.format(relay_num))
        res = self.get_port_data(relay_num)
        if res > 0:
            mask = 1 << relay_num
            # return the specified bit status
            return (self.DEVICE_REG_DATA & mask) == 0
        else:
            Error("Specified relay port is invalid")
            return False

    def log_data(self):
        odict = OrderedDict()
        for i in range(self.N_PORTS):
            value = self.get_port_status(i)
            odict[f'relay_port_{str(i)}'] = int(value)
        return odict


class DummyRelay():

    def __init__(self, state_file='/tmp/relay_state'):
        self.N_PORTS = 4
        Info('DUMMY RELAY')

    def __bus_write__(self):
        pass

    def __str__(self):
        return 'DUMMY_RELAY\n'


    def on(self, rid):
        Debug('Dummy Relay: ON...')
        Debug(self)

    def off(self,rid):
        Debug('Dummy Relay: OFF...')
        Debug(self)

    def toggle(self, rid):
        if not self.get_port_status(rid):
            self.on(rid)
        else:
            self.off(rid)
        return self.get_port_status(rid)

    def all_on(self):
        Debug('Dummy Relay: ALL ON...')

    def all_off(self):
        Debug('Dummy Relay: ALL OFF...')
        Debug(self)

    def manual_toggle(self):
        instruction = input('which relay [-]<1..4>? ')
        if instruction == '?':
            Debug(self)
            return
        elif instruction == 'q':
            sys.exit(0)

        try:
            number = int(instruction)
            relay_no = number - 1
            assert relay_no in range(0,4)
        except:
            Info('Wrong input')
            return
        self.toggle(relay_no)

    def manual_switch(self):
        instruction = input('which relay [-]<1..4>? ')
        if instruction == '?':
            Debug(self)
            return
        elif instruction == 'q':
            sys.exit(0)

        try:
            number = int(instruction)
            relay_no = number - 1 if number > 0 else number + 1
            assert relay_no in range(-4,4)
        except:
            Info('Wrong input')
            return
        if number > 0:
            self.on(relay_no)
        elif number < 0:
            self.off(-relay_no)
        elif number == 0:
            self.all_off()

    def get_port_status(self, relay_num):
        # determines whether the specified port is ON/OFF
        #Debug('Checking status of relay {0}'.format(relay_num))
        return False

    def log_data(self):
        odict = OrderedDict()
        for i in range(self.N_PORTS):
            value = self.get_port_status(i)
            odict[f'relay_port_{str(i)}'] = int(value)
        return odict


if __name__ == "__main__":
    relay = Relay()

    # Called on process interruption. Set all pins to "Input" default mode.
    def end_process(signalnum=None, handler=None):
        print('')
        #relay.all_off()
        sys.exit()


    signal.signal(signal.SIGINT, end_process)

    while True:
        try:
            while True:
                relay.manual_toggle()
                print(relay)
        except KeyboardInterrupt:
            end_process()


