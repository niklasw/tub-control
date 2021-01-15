#!/usr/bin/env python3

from sensors.sensors import TSensors, ds18b20


if __name__ == '__main__':

    sensors = TSensors(ds18b20)
    sensors.read()

    print(sensors)


