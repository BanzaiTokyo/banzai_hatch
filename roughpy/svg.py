from lxml import etree
from .core import Drawable
from .generator import RoughGenerator


class RoughSVG:
    gen: RoughGenerator
    svg: etree.Element

    def __init__(self, svg, config=None):
        self.svg = svg
        self.gen = RoughGenerator(config)

    def draw(self, drawable: Drawable):
        sets = drawable.sets or []
        o = drawable.options or self.get_default_options()
        g = etree.Element('g')
        precision = drawable.options.fixed_decimal_place_digits
        for drawing in sets:
            path = None
            if drawing.type == 'path':
                path = etree.Element(
                    'path',
                    d=self.ops_to_path(drawing, precision),
                    stroke=o.stroke,
                    stroke_width=str(o.stroke_width),
                    fill='none'
                )
                if o.stroke_line_dash:
                    path.set('stroke-dasharray', ' '.join(map(str, o.stroke_line_dash)).strip())
                if o.stroke_line_dash_offset:
                    path.set('stroke-dashoffset', o.stroke_line_dash_offset)
            elif drawing.type == 'fillPath':
                path = etree.Element(
                    'path',
                    d=self.ops_to_path(drawing, precision),
                    stroke='none',
                    stroke_width='0',
                    fill=o.fill or ''
                )
                if drawable.shape == 'curve' or drawable.shape == 'polygon':
                    path.set('fill-rule', 'evenodd')
            elif drawing.type == 'fillSketch':
                path = self.fill_sketch(drawing, o)
            if path is not None:
                g.append(path)
        return g if len(g) > 1 else g[0]

    def fill_sketch(self, drawing, o):
        fweight = o.fill_weight
        if fweight < 0:
            fweight = o.stroke_width / 2
        path = etree.Element(
            'path',
            d=self.ops_to_path(drawing, o.fixed_decimal_place_digits),
            stroke=o.fill or '',
            stroke_width=str(fweight),
            fill='none'
        )
        if o.fill_line_dash:
            path.set('stroke-dasharray', o.fill_line_dash.join(' ').trim())
        if o.fill_line_dash_offset:
            path.set('stroke-dashoffset', o.fill_line_dash_offset)
        return path

    def get_generator(self):
        return self.gen

    def get_default_options(self):
        return self.gen.default_options

    def ops_to_path(self, drawing, fixed_decimal_place_digits=None):
        return self.gen.ops_to_path(drawing, fixed_decimal_place_digits)

    def line(self, x1, y1, x2, y2, options=None):
        d = self.gen.line(x1, y1, x2, y2, options)
        return self.draw(d)

    def rectangle(self, x, y, width, height, options=None):
        d = self.gen.rectangle(x, y, width, height, options)
        return self.draw(d)

    def ellipse(self, x, y, width, height, options=None):
        d = self.gen.ellipse(x, y, width, height, options)
        return self.draw(d)

    def circle(self, x, y, diameter, options=None):
        d = self.gen.circle(x, y, diameter, options)
        return self.draw(d)

    def linear_path(self, points, options=None):
        d = self.gen.linear_path(points, options)
        return self.draw(d)

    def polygon(self, points, options=None):
        d = self.gen.polygon(points, options)
        return self.draw(d)

    def arc(self, x, y, width, height, start, stop, closed=False, options=None):
        d = self.gen.arc(x, y, width, height, start, stop, closed, options)
        return self.draw(d)

    def curve(self, points, options=None):
        d = self.gen.curve(points, options)
        return self.draw(d)

    def path(self, d, options=None):
        drawing = self.gen.path(d, options)
        return self.draw(drawing)
