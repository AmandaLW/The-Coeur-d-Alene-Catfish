import smbus
import time

ADDRESS = 4
CMD_READ_ANALOG = 1

# Submarine v1
#VOLT12 = 650
#VOLT18 = 978

# Submarine v2
VOLT12 = 638
VOLT18 = 959

def map_range(x, in_min, in_max, out_min, out_max):
    out_delta = out_max - out_min
    in_delta = in_max - in_min

    return (x - in_min) * out_delta / in_delta + out_min


class Voltage:
    def __init__(self):
        self.bus = smbus.SMBus(1)

    def get_data(self):
        voltage_time = time.time()
        voltage_raw = self.bus.read_word_data(ADDRESS, CMD_READ_ANALOG)
        voltage = map_range(voltage_raw, VOLT12, VOLT18, 12, 18)

        return [
            (voltage_time, "voltage_raw", voltage_raw),
            (voltage_time, "voltage", voltage)
        ]
