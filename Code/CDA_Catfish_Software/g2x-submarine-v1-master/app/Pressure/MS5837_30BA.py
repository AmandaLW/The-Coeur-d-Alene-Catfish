# derived from the following libraries:
#   https://github.com/bluerobotics/BlueRobotics_MS5837_Library/blob/master/MS5837.cpp
#   https://github.com/ControlEverythingCommunity/MS5837-30BA01/blob/master/Python/MS5837_30BA01.py

import smbus
import math
import time
from collections import deque

ADDRESS = 0x76
RESET = 0x1E
FEET_PER_METER = 3.28084


class MS5837_30BA:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.depth_samples = deque([(0, 0), (0, 0), (0, 0)])

        # reset
        self.bus.write_byte(ADDRESS, RESET)
        time.sleep(0.5)

        # Read 14 bytes of calibration data

        # Read crc
        data = self.bus.read_i2c_block_data(ADDRESS, 0xA0, 2)
        self.C0 = data[0] * 256 + data[1]

        # Read pressure sensitivity
        data = self.bus.read_i2c_block_data(ADDRESS, 0xA2, 2)
        self.C1 = data[0] * 256 + data[1]

        # Read pressure offset
        data = self.bus.read_i2c_block_data(ADDRESS, 0xA4, 2)
        self.C2 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure sensitivity
        data = self.bus.read_i2c_block_data(ADDRESS, 0xA6, 2)
        self.C3 = data[0] * 256 + data[1]

        # Read temperature coefficient of pressure offset
        data = self.bus.read_i2c_block_data(ADDRESS, 0xA8, 2)
        self.C4 = data[0] * 256 + data[1]

        # Read reference temperature
        data = self.bus.read_i2c_block_data(ADDRESS, 0xAA, 2)
        self.C5 = data[0] * 256 + data[1]

        # Read temperature coefficient of the temperature
        data = self.bus.read_i2c_block_data(ADDRESS, 0xAC, 2)
        self.C6 = data[0] * 256 + data[1]

    @property
    def pressure_raw(self):
        # Pressure conversion(OSR = 256) command
        self.bus.write_byte(0x76, 0x40)
        time.sleep(0.02)  # Max conversion time per datasheet

        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.bus.read_i2c_block_data(0x76, 0x00, 3)

        return value[0] * 65536 + value[1] * 256 + value[2]

    @property
    def temperature_raw(self):
        # Temperature conversion(OSR = 256) command
        self.bus.write_byte(0x76, 0x50)
        time.sleep(0.02)  # Max conversion time per datasheet

        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = self.bus.read_i2c_block_data(0x76, 0x00, 3)

        return value[0] * 65536 + value[1] * 256 + value[2]

    @property
    def depth_rate(self):
        rate1 = self.depth_rate_at_index(0)
        rate2 = self.depth_rate_at_index(1)

        return (rate1 + rate2) * 0.5

    def depth_rate_at_index(self, index):
        sample1 = self.depth_samples[index]
        sample2 = self.depth_samples[index + 1]
        dt = sample2[0] - sample1[0]
        dm = sample2[1] - sample1[1]

        if dt == 0:
            rate = 0
        else:
            rate = dm / dt

        return rate

    def add_depth(self, data):
        self.depth_samples.append(data)
        self.depth_samples.popleft()

    # pressure_raw is D1 in data sheet
    # temperature_raw is D2 in the data sheet
    def calculate_values(self, pressure_raw, temperature_raw):
        dT = temperature_raw - self.C5 * 256
        SENS = self.C1 * 32768 + (self.C3 * dT) / 256
        OFF = self.C2 * 65536 + (self.C4 * dT) / 128

        TEMP = 2000 + dT * self.C6 / 8388608

        T2 = 0
        OFF2 = 0
        SENS2 = 0

        if TEMP >= 2000:
            T2 = 2 * (dT * dT) / 137438953472
            OFF2 = ((TEMP - 2000) * (TEMP - 2000)) / 16
            SENS2 = 0
        elif TEMP < 2000:
            T2 = 3 * (dT * dT) / 8589934592
            OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 2
            SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 8
            if TEMP < -1500:
                OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 4 * ((TEMP + 1500) * (TEMP + 1500))

        OFF2 = OFF - OFF2
        SENS2 = SENS - SENS2

        pressure = ((((pressure_raw * SENS2) / 2097152) - OFF2) / 8192) / 10.0

        TEMP = TEMP - T2
        celsius = TEMP / 100.0
        fahrenheit = celsius * 1.8 + 32

        fluid_density = 1029
        depth = ((pressure * 100) - 101300) / (fluid_density * 9.80665)
        altitude = (1 - math.pow(pressure / 1013.25, 0.190284)) * 145366.45 * 0.3048

        return (pressure, celsius, fahrenheit, depth, altitude)

    def get_data(self):
        pressure_time = time.time()
        pressure_raw = self.pressure_raw
        temperature_time = time.time()
        temperature_raw = self.temperature_raw
        values_time = time.time()
        pressure, celsius, fahrenheit, depth, altitude = self.calculate_values(pressure_raw, temperature_raw)

        self.add_depth((values_time, depth))

        return [
            (pressure_time, "pressure_raw", pressure_raw),
            (temperature_time, "temperature_raw", temperature_raw),
            (values_time, "mbars", pressure),
            (values_time, "celsius", celsius),
            (values_time, "fahrenheit", fahrenheit),
            (values_time, "depth_meters", depth),
            (values_time, "depth_feet", depth * FEET_PER_METER),
            (values_time, "descent_mps", self.depth_rate),
            (values_time, "descent_mpm", self.depth_rate / 60),
            (values_time, "descent_mph", self.depth_rate / (60 * 60)),
            (values_time, "descent_fps", self.depth_rate * FEET_PER_METER),
            (values_time, "descent_fpm", self.depth_rate * FEET_PER_METER / 60),
            (values_time, "descent_fph", self.depth_rate * FEET_PER_METER / (60 * 60)),
            (values_time, "altitude", altitude),
        ]
