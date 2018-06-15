from sense_hat import SenseHat
import time


class SenseController:
    def __init__(self):
        self.sense = SenseHat()

    def __enter__(self):
        self.clear()

        return self

    def __exit__(self, type, value, traceback):
        self.clear()

    def clear(self):
        self.sense.clear()

    def get_data(self):
        orientation_time = time.time()
        orientation = self.sense.get_orientation_degrees()
        compass_time = time.time()
        compass = self.sense.get_compass_raw()
        acceleration_time = time.time()
        acceleration = self.sense.get_accelerometer_raw()

        return [
            # Environmental sensors
            (time.time(), "humidity", self.sense.get_humidity()),
            (time.time(), "pressure", self.sense.get_pressure()),
            (time.time(), "temperature_from_humidity", self.sense.get_temperature()),
            (time.time(), "temperature_from_pressure", self.sense.get_temperature_from_pressure()),

            # IMU sensors
            (orientation_time, "orientation.pitch", orientation['pitch']),
            (orientation_time, "orientation.roll", orientation['roll']),
            (orientation_time, "orientation.yaw", orientation['yaw']),
            (compass_time, "compass.x", compass['x']),
            (compass_time, "compass.y", compass['y']),
            (compass_time, "compass.z", compass['z']),
            (acceleration_time, "accelerometer.x", acceleration['x']),
            (acceleration_time, "accelerometer.y", acceleration['y']),
            (acceleration_time, "accelerometer.z", acceleration['z'])
        ]

    def show_message(self, message):
        self.sense.show_message(message, text_colour=[0, 64, 0])
