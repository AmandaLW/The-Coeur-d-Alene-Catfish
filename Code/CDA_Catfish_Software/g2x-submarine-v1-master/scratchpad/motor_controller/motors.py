#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT
import atexit
import pygame

from Vector import Vector
from Interpolator import Interpolator

PRECISION = 3

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# setup left joystick
j1 = Vector()
left_thruster = Interpolator()
left_thruster.addIndexValue(0.0, -1.0)
left_thruster.addIndexValue(90.0, 1.0)
left_thruster.addIndexValue(180.0, 1.0)
left_thruster.addIndexValue(270.0, -1.0)
left_thruster.addIndexValue(360.0, -1.0)
right_thruster = Interpolator()
right_thruster.addIndexValue(0.0, 1.0)
right_thruster.addIndexValue(90.0, 1.0)
right_thruster.addIndexValue(180.0, -1.0)
right_thruster.addIndexValue(270.0, -1.0)
right_thruster.addIndexValue(360.0, 1.0)

# setup right joystick
j2 = Vector()
v_front_thruster = Interpolator()
v_front_thruster.addIndexValue(0.0, 0.0)
v_front_thruster.addIndexValue(90.0, -1.0)
v_front_thruster.addIndexValue(180.0, 0.0)
v_front_thruster.addIndexValue(270.0, 1.0)
v_front_thruster.addIndexValue(360.0, 0.0)
v_back_left_thruster = Interpolator()
v_back_left_thruster.addIndexValue(0.0, 1.0)
v_back_left_thruster.addIndexValue(90.0, 1.0)
v_back_left_thruster.addIndexValue(180.0, -1.0)
v_back_left_thruster.addIndexValue(270.0, -1.0)
v_back_left_thruster.addIndexValue(360.0, 1.0)
v_back_right_thruster = Interpolator()
v_back_right_thruster.addIndexValue(0.0, -1.0)
v_back_right_thruster.addIndexValue(90.0, 1.0)
v_back_right_thruster.addIndexValue(180.0, 1.0)
v_back_right_thruster.addIndexValue(270.0, -1.0)
v_back_right_thruster.addIndexValue(360.0, -1.0)

# setup ascent/descent controllers
ascent = -1.0
descent = -1.0


# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def setMotor(motor_number, value):
    motor = mh.getMotor(motor_number)
    value *= 255.0

    if value < 0:
        motor.run(Adafruit_MotorHAT.BACKWARD)
        motor.setSpeed(-int(value))
    else:
        motor.run(Adafruit_MotorHAT.FORWARD)
        motor.setSpeed(int(value))


atexit.register(turnOffMotors)

pygame.init()
# screen = pygame.display.set_mode([500, 700])
# pygame.display.set_caption("G2X")
clock = pygame.time.Clock()
pygame.joystick.init()
stick = pygame.joystick.Joystick(0)
stick.init()

done = False

while done is False:
    for event in pygame.event.get():
        update_horizontal_thrusters = False
        update_vertical_thrusters = False

        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                value = round(event.value, PRECISION)
                if j1.x != value:
                    j1.x = value
                    update_horizontal_thrusters = True
            elif event.axis == 1:
                value = round(event.value, PRECISION)
                if j1.y != value:
                    j1.y = value
                    update_horizontal_thrusters = True
            elif event.axis == 2:
                value = round(event.value, PRECISION)
                if j2.x != value:
                    j2.x = value
                    update_vertical_thrusters = True
            elif event.axis == 5:
                value = round(event.value, PRECISION)
                if j2.y != value:
                    j2.y = value
                    update_vertical_thrusters = True
            elif event.axis == 3:
                value = round(event.value, PRECISION)
                if descent != value:
                    descent = value
                    update_vertical_thrusters = True
            elif event.axis == 4:
                value = round(event.value, PRECISION)
                if ascent != value:
                    ascent = value
                    update_vertical_thrusters = True
            else:
                print("unknown axis ", event.axis)
        elif event.type == pygame.JOYBUTTONDOWN:
            pass
            # print("unhandled button down event")
        elif event.type == pygame.JOYBUTTONUP:
            pass
            # print("unhandled button up event")
        elif event.type == pygame.JOYHATMOTION:
            pass
            # print("unhandled hat event")
        elif event.type == pygame.JOYBALLMOTION:
            pass
            # print("unhandled ball motion event")

        if update_horizontal_thrusters:
            left_value = left_thruster.valueAtIndex(j1.angle)
            right_value = right_thruster.valueAtIndex(j1.angle)
            power = min(1.0, j1.length)
            setMotor(1, left_value * power)
            setMotor(3, right_value * power)

        if update_vertical_thrusters:
            power = min(1.0, j2.length)
            front_value = v_front_thruster.valueAtIndex(j2.angle) * power
            back_left_value = v_back_left_thruster.valueAtIndex(j2.angle) * power
            back_right_value = v_back_right_thruster.valueAtIndex(j2.angle) * power
            if ascent != -1.0:
                percent = (1.0 + ascent) / 2.0
                max_thrust = max(front_value, back_left_value, back_right_value)
                max_adjust = (1.0 - max_thrust) * percent
                front_value += max_adjust
                back_left_value += max_adjust
                back_right_value += max_adjust
            elif descent != -1.0:
                percent = (1.0 + descent) / 2.0
                min_thrust = min(front_value, back_left_value, back_right_value)
                max_adjust = (min_thrust - -1.0) * percent
                front_value -= max_adjust
                back_left_value -= max_adjust
                back_right_value -= max_adjust
            setMotor(2, front_value)
            setMotor(1, back_left_value)
            setMotor(3, back_right_value)
