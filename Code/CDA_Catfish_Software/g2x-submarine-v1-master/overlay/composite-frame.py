#!/usr/bin/env python3

import os
import io
import argparse
import sys
import multiprocessing
import concurrent.futures

from PIL import Image
import cairosvg

from Frame import Frame
from SVGGenerator import SVGGenerator
from DataManager import DataManager
from Data import Data
from Chart import Chart


def process_args():
    start = 0
    end = sys.maxsize
    show_svg = False
    threads = multiprocessing.cpu_count()

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="The directory that contains the input frames")
    parser.add_argument("-o", "--output", help="The directory to write the composited frames")
    parser.add_argument("-s", "--start", type=int, help="The frame number to start processing")
    parser.add_argument("-e", "--end", type=int, help="The frame number to end processing")
    parser.add_argument("-t", "--threads", type=int, help="The number of threads to use for processing")
    args = parser.parse_args()

    # check for required arguments

    if args.input is None:
        raise ValueError('input directory must be defined')

    if args.output is None:
        raise ValueError('output directory must be defined')

    # handle optional arguments

    if args.start is not None:
        start = args.start

    if args.end is not None:
        end = args.end

    if args.threads is not None:
        threads = args.threads

    # return dictionary of values
    # NOTE: what do we need here to be able to use dot notation for these properties?
    return {
        "input": args.input,
        "output": args.output,
        "start": start,
        "end": end,
        "show_svg": show_svg,
        "threads": threads
    }


def map_range(x, in_min, in_max, out_min, out_max):
    out_delta = out_max - out_min
    in_delta = in_max - in_min

    return (x - in_min) * out_delta / in_delta + out_min


def get_frame_data(info):
    # load data
    def map_depth(item):
        result = ",".join([
            str(round(map_range(item[0], info.frame_time - 60, info.frame_time, 0, 100), 3)),
            str(round(map_range(item[1], map_depth.start, map_depth.end, 0, 100), 3))
        ])

        # print("{0} became {1}".format(item, result))
        return result

    depth_data = data_manager.select_depths(info.frame_time - 60, info.frame_time)

    if len(depth_data) > 0:
        map_depth.start = depth_data[-1][1] - 50
        map_depth.end = depth_data[-1][1] + 50
        depth_text = "{0:0.2f} ft".format(depth_data[-1][1])
        depth_path_data = "M" + " ".join(map(map_depth, depth_data))
    else:
        depth_text = "-- ft"
        depth_path_data = ""

    def map_temperature(item):
        result = ",".join([
            str(round(map_range(item[0], info.frame_time - 60, info.frame_time, 0, 100), 3)),
            str(round(map_range(item[1], 40, 55, 100, 0), 3))
        ])

        # print("{0} became {1}".format(item, result))
        return result

    temperature_data = data_manager.select_temperatures(info.frame_time - 60, info.frame_time)

    if len(temperature_data) > 0:
        temperature_text = "{0:0.2f} °F".format(temperature_data[-1][1])
        temperature_path_data = "M" + " ".join(map(map_temperature, temperature_data))
    else:
        temperature_text = "-- °F"
        temperature_path_data = ""

    # for testing
    depth_chart = Chart("Depth", depth_text, depth_path_data)
    depth_chart.x = 5
    depth_chart.y = 972 - 5 - 110

    temperature_chart = Chart("Temperature", temperature_text, temperature_path_data)
    temperature_chart.x = 5 + 5 + 100 + 5 + 5
    temperature_chart.y = 972 - 5 - 110

    # print(depth_path_data)
    return Data(info.frame_time, depth_chart, temperature_chart, info.input_path)


def process_frame(info):
    # let the user know which frame we're currently processing
    print("frame={0}, time={1}".format(str(int(info.frame_number)), str(round(info.frame_time, 3))))

    # load frame
    frame = Image.open(info.input_path, 'r')

    # get data for this frame
    frame_data = get_frame_data(info)

    # render SVG text
    svg = generator.to_svg(frame_data)

    if options["show_svg"]:
        print(svg)

    # create overlay image from SVG
    overlay_bytes = cairosvg.svg2png(bytestring=svg)
    overlay = Image.open(io.BytesIO(overlay_bytes))

    # create composite image holder
    composite = Image.new('RGB', frame.size, (255, 255, 255))

    # composite images
    composite.paste(frame)
    composite.paste(overlay, (0, 0), overlay)

    # output result
    composite.save(info.output_path, optimize=False)


def process_frames(infos, threads=2):
    print("Processing with {0} thread(s)".format(threads))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for info in infos:
            executor.submit(process_frame, info)


if __name__ == "__main__":
    # process command line arguments
    options = process_args()

    # load data
    data_manager = DataManager()
    data_manager.load("../db/g2x-1479064727.db")

    # make svg generator
    generator = SVGGenerator('./overlay.svg.mustache')

    # build list of frames of interest, and their associated metadata
    frames = filter(
        lambda f: f.in_range(options["start"], options["end"]),
        map(
            lambda f: Frame(options["input"], options["output"], f),
            os.listdir(options["input"])
        )
    )

    # process all frames
    process_frames(frames, options["threads"])
