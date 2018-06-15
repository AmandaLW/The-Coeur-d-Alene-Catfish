import re
import os

# create regex for extracting time data from file names
TIME_AND_FRAME_PATTERN = re.compile(r"^g2x-(\d+)-(\d+)$")


class Frame:
    def __init__(self, input_dir, output_dir, frame_file):
        base_name = os.path.splitext(frame_file)[0]

        self.input_path = input_dir + "/" + frame_file
        self.output_path = output_dir + "/" + base_name + ".png"

        file_match = TIME_AND_FRAME_PATTERN.search(base_name)

        if file_match is not None:
            base_time = float(file_match.group(1))

            self.frame_number = float(file_match.group(2))
            self.frame_time = base_time + self.frame_number / 24
        else:
            self.frame_number = -1
            self.frame_time = -1

    def in_range(self, low, high):
        return low <= self.frame_number <= high
