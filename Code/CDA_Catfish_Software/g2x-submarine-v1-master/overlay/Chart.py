from SVGGenerator import SVGGenerator
from Label import Label


class Chart(SVGGenerator):
    def __init__(self, name, title, data):
        SVGGenerator.__init__(self, './chart.svg.mustache')
        self.name = name
        self.title = title
        self.x = 10
        self.y = 10
        self.width = 110
        self.height = 110
        self.padding = 5
        self.background_color = "white"
        self.background_opacity = 0.6
        self.path_data = data
        # self.path_color = "rgb(0,192,0)"
        self.path_color = "rgb(255,0,0)"

    def to_svg(self, data=None):
        label = Label(self.width * 0.5, self.height - self.padding, self.title)
        label.alignment = "middle"
        self.label_svg = label.to_svg(label)

        return SVGGenerator.to_svg(self, self)
