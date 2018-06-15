#!/usr/bin/env python3.4

from KeyDispatcher import KeyDispatcher
from Display import Display
from DataLogger import SQLiteLogger
from Voltage import Voltage
import time

DEVICE = "Arduino Nano"
DELAY = 1  # in seconds


class Handler:
    def __init__(self, display, logger):
        self.display = display
        self.logger = logger
        self.recording = False
        self.sensor = Voltage()

    def record(self):
        self.recording = not self.recording

        if self.recording:
            self.logger.log(DEVICE, "recording", 1)
        else:
            self.logger.log(DEVICE, "recording", 0)

        return True

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

    def quit(self):
        self.logger.log(DEVICE, "running", 0)

        return False


with KeyDispatcher() as dispatcher, SQLiteLogger(filename="g2x-voltage.db") as logger:
    # setup display
    display = Display(DEVICE, "[r]ecord [q]uit")

    # create key handler
    handler = Handler(display, logger)

    # register keys
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
