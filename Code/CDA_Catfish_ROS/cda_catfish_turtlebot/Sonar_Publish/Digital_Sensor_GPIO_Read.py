#!/usr/bin/env python

# Code Modified From: https://raspberrypi.stackexchange.com/questions/44276/reading-weird-serial-communication-gpio?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

# serial_invert.py
# 2016-03-18
# Public Domain

# NOTE: Must run "sudo pigpoid" before attempting to read serial data from sonars!

import time
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import struct

def bubbleSort(arr):
    n = len(arr)
 
    # Traverse through all array elements
    for i in range(n):
 
        # Last i elements are already in place
        for j in range(0, n-i-1):
 
            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j+1] :
                arr[j], arr[j+1] = arr[j+1], arr[j]

def read_Sensor_GPIO(RXD, pi):

	# Array of five elements
	bubbleSortArray = [None] * 3

	i = 0

	while True:
		if i == 3:
			bubbleSort(bubbleSortArray)
			#byteArrayString = str(bubbleSortArray[2])[1:4]			# One readding is array size 5 (want to skip "R" in R# data reading, so we just have length as #, thus skip 1st element)
			#byteArrayString2 = str(bubbleSortArray[2])
			return bubbleSortArray[1]
			i = 0
		(count, data) = pi.bb_serial_read(RXD)
		if count:
			bubbleSortArray[i] = str(data[1:4])
			i = i + 1
			time.sleep(.01)

		# .1 second is time it takes to gather one "reading" from sensor (R#), thus .2 gather 2, .3 is 3 and so on
		time.sleep(.1)

#pi = pigpio.pi()
#read_Sensor_GPIO_13(13, pi)		# set whatever # you desire for reading GPIO, meaning # must correspond to GPIO pin you wish to read
