#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import pprint
import pygame

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""
        
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def listen(self):
        """Listen for events to happen"""
        
        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():
                os.system('clear')

                print("axis count: ", self.controller.get_numaxes())

                if event.type == pygame.JOYAXISMOTION:
                    print("axis = ", event.axis)
                    self.axis_data[event.axis] = round(event.value,2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value
                elif event.type == pygame.JOYBALLMOTION:
                    print("unhandled ball motion event")

                # Insert your code on what you would like to happen for each event here!
                # In the current setup, I have the state simply printing out to the screen.
                
                print("Square:      ", self.button_data[0])
                print("X:           ", self.button_data[1])
                print("Circle:      ", self.button_data[2])
                print("Triangle:    ", self.button_data[3])
                print("L1:          ", self.button_data[4])
                print("R1:          ", self.button_data[5])
                print("L2:          ", self.button_data[6])
                print("R2:          ", self.button_data[7])
                print("Share:       ", self.button_data[8])
                print("Options:     ", self.button_data[9])
                print("L-Joystick:  ", self.button_data[10])
                print("R-Joystick:  ", self.button_data[11])
                print("Playstation: ", self.button_data[12])
                print("Trackpad:    ", self.button_data[13])
                pprint.pprint(self.axis_data)
                pprint.pprint(self.hat_data)


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
