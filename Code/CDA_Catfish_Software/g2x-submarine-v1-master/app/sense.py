#!/usr/bin/env python3.4

from Sensor import SenseController
from KeyDispatcher import KeyDispatcher
from Display import Display
from DataLogger import SQLiteLogger
import time


DEVICE = "PiSense"
DELAY = 1  # in seconds


class Handler:
    def __init__(self, display, logger, sensor):
        self.display = display
        self.logger = logger
        self.sensor = sensor
        self.recording = False
        self.logger.log(DEVICE, "running", 1)

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


with SenseController() as sensor, KeyDispatcher() as dispatcher, SQLiteLogger(filename="g2x-sense.db") as logger:
    # setup display
    display = Display(DEVICE, "[r]ecord [q]uit")

    # setup key handlers
    handler = Handler(display, logger, sensor)

    dispatcher.add("r", handler, "record")
    dispatcher.add("q", handler, "quit")

    # start processing key presses
    while True:
        if dispatcher.can_process_key():
            if not dispatcher.process_key():
                break
        else:
            handler.read()
            time.sleep(DELAY)

    display.clear()
