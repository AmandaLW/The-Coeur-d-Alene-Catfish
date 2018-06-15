from SVGGenerator import SVGGenerator


class Label(SVGGenerator):
    def __init__(self, x, y, text):
        SVGGenerator.__init__(self, './label.svg.mustache')
        self.x = x
        self.y = y
        self.text = text
        self.alignment = "start"
        self.font_size = 14
        self.color = "rgb(0,0,0)"
