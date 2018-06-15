#!/usr/bin/env python3.4

from Pressure import MS5837_30BA
from KeyDispatcher import KeyDispatcher
from Display import Display
from DataLogger import SQLiteLogger
import time

DEVICE = "Pressure/Temperature"
DELAY = 1.0  # in seconds


class Handler:
    def __init__(self, display, logger, sensor):
        self.display = display
        self.logger = logger
        self.sensor = sensor
        self.recording = False
        self.logger.log(DEVICE, "running", 1)
        self.logger.log(DEVICE, "C0", self.sensor.C0)
        self.logger.log(DEVICE, "C1", self.sensor.C1)
        self.logger.log(DEVICE, "C2", self.sensor.C2)
        self.logger.log(DEVICE, "C3", self.sensor.C3)
        self.logger.log(DEVICE, "C4", self.sensor.C4)
        self.logger.log(DEVICE, "C5", self.sensor.C5)
        self.logger.log(DEVICE, "C6", self.sensor.C6)

    def read(self):
        properties = []
        values = {}

        if self.recording:
            for reading in self.sensor.get_data():
                properties.append(reading[1])
                values[reading[1]] = reading[2]
                self.logger.log(DEVICE, reading[1], reading[2], reading[0])
            self.display.show_properties(values, properties)
        else:
            values["recording"] = False
            self.display.show_properties(values)

        return True

    def record(self):
        self.recording = not self.recording

        if self.recording:
            self.logger.log(DEVICE, "recording", 1)
        else:
            self.logger.log(DEVICE, "recording", 0)

        return True

    def quit(self):
        self.logger.log(DEVICE, "running", 0)

        return False


with KeyDispatcher() as dispatcher, SQLiteLogger(filename="g2x-pressure.db") as logger:
    # setup display
    display = Display(DEVICE, "[r]ecord [q]uit")

    # setup pressure sensor
    sensor = MS5837_30BA()

    # setup key handlers
    handler = Handler(display, logger, sensor)

    dispatcher.add("r", handler, "record")
    dispatcher.add("q", handler, "quit")

    while True:
        if dispatcher.can_process_key():
            if not dispatcher.process_key():
                break
        else:
            handler.read()
            time.sleep(DELAY)

    display.clear()
