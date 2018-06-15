#!/usr/bin/env python3

def map_range(x, in_min, in_max, out_min, out_max):
    out_delta = out_max - out_min
    in_delta = in_max - in_min

    return (x - in_min) * out_delta / in_delta + out_min

def show_value(value):
	print(map_range(value, 650, 978, 12, 18))

show_value(650)
show_value(978)
show_value(0)
show_value(1023)
