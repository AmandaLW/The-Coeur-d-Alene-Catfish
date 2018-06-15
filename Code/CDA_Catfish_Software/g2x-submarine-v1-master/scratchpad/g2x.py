#!/usr/bin/env python3

import signal
import shutil
import time
import curses
import logging
from sqlite_logger import SQLiteLogger
from sense_hat import SenseHat
from picamera import PiCamera

sense = SenseHat()
sense.clear()

# setup sensor logging
data_logger = SQLiteLogger()

# setup logging
# timestamp = int(time.time())
# filename = "g2x-{}.log".format(timestamp)
logging.basicConfig(filename="g2x.log", level=logging.DEBUG)

# config
use_image_overlay = False
use_text_overlay = True
preview_window = (0, 0, 640, 480)
camera_resolution = (1296, 972)  # "1080p"
camera_framerate = 24
preview = False
recording = False

# create access to camera
camera = PiCamera(resolution=camera_resolution, framerate=camera_framerate)

# create overlays
if use_image_overlay:
    img0 = Image.open('recording.png')
    pad0 = Image.new('RGB', (
        ((img0.size[0] + 31) // 32) * 32,
        ((img0.size[1] + 15) // 16) * 16))
    pad0.paste(img0, (0, 0), img0)
    o0 = camera.add_overlay(pad0.tostring(), size=img0.size)
    o0.layer = 3
    o0.alpha = 0

    img1 = Image.open('not-recording.png')
    pad1 = Image.new('RGB', (
        ((img1.size[0] + 31) // 32) * 32,
        ((img1.size[1] + 15) // 16) * 16))
    pad1.paste(img1, (0, 0), img1)
    o1 = camera.add_overlay(pad1.tostring(), size=img1.size)
    o1.layer = 4
    o1.alpha = 0

# create list of properties to display
properties = [
    "analog_gain",
    "annotate_text",
    "annotate_text_size",
    # "awb_gains",
    "awb_mode",
    "brightness",
    "color_effects",
    "contrast",
    "crop",
    "digital_gain",
    "drc_strength",
    "exposure_compensation",
    "exposure_mode",
    "exposure_speed",
    "flash_mode",
    "framerate",
    "framerate_delta",
    "hflip",
    "image_denoise",
    "image_effect",
    "iso",
    # the follwing is a read-only boolean property and it is not available on
    # the Pi 3
    # "led",
    "meter_mode",
    "resolution",
    "rotation",
    "saturation",
    "sensor_mode",
    "sharpness",
    "shutter_speed",
    "vflip",
    "video_denoise",
    "video_stabilization",
    "zoom"
]

# get maximum property name length for padding during display
max_len = 0

for property in properties:
    property_len = len(property)
    if max_len < property_len:
        max_len = property_len


def update_screen(stdscr):
    global max_len, properties
    row = 0
    col = 0
    max_col = 0

    # clear screen
    stdscr.clear()

    # display properties
    for key in properties:
        # just in case we have an invalid property, wrap this iteration in
        # a try/except statement
        try:
            # NOTE: we may need to handle the case where the current string
            # cannot fit in the current row

            # display key/value on screen
            value = getattr(camera, key)
            keystring = key.rjust(max_len) + ": "
            stdscr.addstr(row, col, keystring)
            valuestring = str(value)
            stdscr.addstr(row, col + len(keystring), valuestring, curses.A_BOLD)

            # update max_col
            current_end_col = col + len(keystring) + len(valuestring)

            if current_end_col > max_col:
                max_col = current_end_col

            # update current row
            row = row + 1

            if row >= curses.LINES:
                row = 0
                col = max_col + 2

                # we're off of the display
                if col >= curses.COLS:
                    break
        except:
            # TODO: figure out how to include the exception in the output
            logging.error("An exception occurred")

    # move the cursor to a sensible location and update the screen
    stdscr.addstr(curses.LINES - 1, 0, "[p]review [q]uit [r]ecord [-/=]brightness [_/+]contrast", curses.A_BOLD)
    stdscr.move(curses.LINES - 1, 0)
    stdscr.refresh()


def sigwinch_handler(n, frame):
    # based on example 5 at
    # http://www.programcreek.com/python/example/9546/curses.KEY_RESIZE
    size = shutil.get_terminal_size()
    curses.resizeterm(size.lines, size.columns)
    curses.ungetch(curses.KEY_RESIZE)


def process_character(ch):
    global preview, recording

    if ch == ord("-"):
        if camera.brightness > 0:
            camera.brightness -= 1
    elif ch == ord("="):
        if camera.brightness < 100:
            camera.brightness += 1
    elif ch == ord("_"):
        if camera.contrast > -100:
            camera.contrast -= 1
    elif ch == ord("+"):
        if camera.contrast < 100:
            camera.contrast += 1
    elif ch == ord("p"):
        preview = not preview
        if preview:
            camera.start_preview(fullscreen=False, window=preview_window)
        else:
            camera.stop_preview()
    elif ch == ord("r"):
        recording = not recording
        if recording:
            # calculate file name and start recording
            timestamp = int(time.time())
            filename = "g2x-{}.h264".format(timestamp)
            camera.start_recording(filename)

            if use_image_overlay:
                o0.alpha = 255
                o1.alpha = 0
            elif use_text_overlay:
                camera.annotate_text = "Recording"
        else:
            camera.stop_recording()

            if use_image_overlay:
                o0.alpha = 0
                o1.alpha = 255
            elif use_text_overlay:
                camera.annotate_text = ""
    else:
        logging.debug("Unhandled key: " + str(ch))


def log_sensors():
    orientation = sense.get_orientation_radians()
    compass = sense.get_compass_raw()
    acceleration = sense.get_accelerometer_raw()

    # Environmental sensors
    data_logger.log("SenseHat", "humidity", sense.get_humidity())
    data_logger.log("SenseHat", "temperature_from_humidity", sense.get_temperature())
    data_logger.log("SenseHat", "temperature_from_pressure", sense.get_temperature_from_pressure())
    data_logger.log("SenseHat", "pressure", sense.get_pressure())

    # IMU sensors
    data_logger.log("SenseHat", "orientation.pitch", orientation['pitch'])
    data_logger.log("SenseHat", "orientation.roll", orientation['roll'])
    data_logger.log("SenseHat", "orientation.yaw", orientation['yaw'])
    data_logger.log("SenseHat", "compass.x", compass['x'])
    data_logger.log("SenseHat", "compass.y", compass['y'])
    data_logger.log("SenseHat", "compass.z", compass['z'])
    data_logger.log("SenseHat", "accelerometer.x", acceleration['x'])
    data_logger.log("SenseHat", "accelerometer.y", acceleration['y'])
    data_logger.log("SenseHat", "accelerometer.z", acceleration['z'])


# display all current property values
def main(stdscr):
    while True:
        update_screen(stdscr)

        ch = stdscr.getch()

        if ch == ord("q"):
            break
        elif ch == -1:
            log_sensors()
        else:
            process_character(ch)


try:
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    curses.wrapper(main)
finally:
    camera.close()
    data_logger.close()
