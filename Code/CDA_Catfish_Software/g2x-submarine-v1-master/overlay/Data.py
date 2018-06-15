import time


class Data:
    def __init__(self, secs_since_epoch, depth_chart, temperature_chart, frame_path):
        # general settings
        self.width = 1296
        self.height = 972
        self.padding = 5
        self.frame_path = frame_path

        # date/time settings
        local_time = time.localtime(secs_since_epoch)
        self.frame_date = time.strftime("%B %d, %Y", local_time)
        self.frame_time = time.strftime("%I:%M:%S %p", local_time)
        self.font_size = 22
        self.text_color = "rgb(255,255,255)"
        self.datetime_x = self.width - self.padding

        # charts
        self.depth_chart = depth_chart.to_svg()
        self.temperature_chart = temperature_chart.to_svg()
