#!/usr/bin/env python3.4

from Camera import CameraController
from KeyDispatcher import KeyDispatcher
from Display import Display
from DataLogger import SQLiteLogger

DEVICE = "PiCamera"


class Handler:
    def __init__(self, logger, camera):
        self.logger = logger
        self.camera = camera
        self.logger.log(DEVICE, "running", 1)

    def increase_brightness(self):
        self.camera.brightness += 1
        self.logger.log(DEVICE, "brightness", self.camera.brightness)
        return True

    def decrease_brightness(self):
        self.camera.brightness -= 1
        self.logger.log(DEVICE, "brightness", self.camera.brightness)
        return True

    def increase_contrast(self):
        self.camera.contrast += 1
        self.logger.log(DEVICE, "contrast", self.camera.contrast)
        return True

    def decrease_contrast(self):
        self.camera.contrast -= 1
        self.logger.log(DEVICE, "contrast", self.camera.contrast)
        return True

    def toggle_preview(self):
        self.camera.toggle_preview()
        self.logger.log(DEVICE, "preview", self.camera.preview)
        return True

    def toggle_record(self):
        self.camera.toggle_record()
        self.logger.log(DEVICE, "record", self.camera.record)
        return True

    def quit(self):
        self.logger.log(DEVICE, "running", 0)
        return False


def update(display, camera):
    properties = []
    values = {}

    for item in camera.get_data():
        properties.append(item[1])
        values[item[1]] = item[2]

    display.show_properties(values, properties)


with CameraController() as camera, KeyDispatcher() as dispatcher, SQLiteLogger(filename="g2x-camera.db") as logger:
    # setup key handlers
    handler = Handler(logger, camera)

    dispatcher.add("-", handler, "decrease_brightness")
    dispatcher.add("=", handler, "increase_brightness")
    dispatcher.add("_", handler, "decrease_contrast")
    dispatcher.add("+", handler, "increase_contrast")
    dispatcher.add("p", handler, "toggle_preview")
    dispatcher.add("r", handler, "toggle_record")
    dispatcher.add("q", handler, "quit")

    # setup display and start processing key presses
    display = Display(DEVICE, "[-/=] brightness [_/+] contrast [p]review [r]ecord [q]uit")

    update(display, camera)

    while dispatcher.process_key():
        update(display, camera)

    display.clear()
