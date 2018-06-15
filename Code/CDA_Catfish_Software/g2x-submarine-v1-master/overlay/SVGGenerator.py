import pystache


class SVGGenerator:
    def __init__(self, template_file):
        self.template_file = template_file
        self.template = None
        self.renderer = pystache.Renderer()

    def to_svg(self, data=None):
        if self.template is None:
            template_file = open(self.template_file)
            self.template = template_file.read()
            template_file.close()

        return self.renderer.render(self.template, data)
