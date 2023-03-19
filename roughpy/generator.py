import re
import math
import copy
from .core import Config, Options, Drawable, OpSet, Options, PathInfo
from .renderer import line, solid_fill_polygon, pattern_fill_polygons, rectangle, ellipse_with_params, \
    generate_ellipse_params, linear_path, arc, pattern_fill_arc, curve, svg_path
from .roughmath import random_seed
from .points_on_curve import points_on_bezier_curves, curve_to_bezier
from .points_on_path import points_on_path

NOS = 'none'


class RoughGenerator:
    default_options = Options(
        max_randomness_offset=2,
        roughness=1,
        bowing=1,
        stroke='#000',
        stroke_width=1,
        curve_tightness=0,
        curve_fitting=0.95,
        curve_step_count=9,
        fill_style='hachure',
        fill_weight=-1,
        hachure_angle=-45,
        hachure_gap=-1,
        dash_offset=-1,
        dash_gap=-1,
        zigzag_offset=-1,
        seed=0,
        disable_multi_stroke=False,
        disable_multi_stroke_fill=False,
        preserve_vertices=False,
    )

    def __init__(self, config=None):
        self.config = config or Config()
        if self.config.options:
            self.default_options = self._o(self.config.options)

    @staticmethod
    def new_seed():
        return random_seed()

    def _o(self, options=None):
        if not options:
            options = Options()
        result = Options()
        for field, value in options.__dict__.items():
            setattr(result, field, getattr(self.default_options, field) if value is None else value)
        return result

    def _d(self, shape, sets, options) -> Drawable:
        return Drawable(shape=shape, sets=sets or [], options=options or self.default_options)

    def line(self, x1, y1, x2, y2, options=None):
        o = self._o(options)
        return self._d('line', [line(x1, y1, x2, y2, o)], o)

    def rectangle(self, x, y, width, height, options=None):
        o = self._o(options)
        paths = []
        outline = rectangle(x, y, width, height, o)
        if o.fill:
            points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
            if o.fill_style == 'solid':
                paths.append(solid_fill_polygon([points], o))
            else:
                paths.append(pattern_fill_polygons([points], o))
        if o.stroke != NOS:
            paths.append(outline)
        return self._d('rectangle', paths, o)

    def ellipse(self, x, y, width, height, options=None):
        o = self._o(options)
        paths = []
        ellipse_params = generate_ellipse_params(width, height, o)
        ellipse_response = ellipse_with_params(x, y, o, ellipse_params)
        if o.fill:
            if o.fill_style == 'solid':
                shape = ellipse_with_params(x, y, o, ellipse_params).opset
                shape.type = 'fillPath'
                paths.append(shape)
            else:
                paths.append(pattern_fill_polygons([ellipse_response.estimated_points], o))
        if o.stroke != NOS:
            paths.append(ellipse_response.opset)
        return self._d('ellipse', paths, o)

    def circle(self, x, y, diameter, options=None):
        ret = self.ellipse(x, y, diameter, diameter, options)
        ret.shape = 'circle'
        return ret

    def linear_path(self, points, options=None):
        o = self._o(options)
        return self._d('linearPath', [linear_path(points, False, o)], o)

    def arc(self, x, y, width, height, start, stop, closed=False, options=None):
        o = self._o(options)
        paths = []
        outline = arc(x, y, width, height, start, stop, closed, True, o)
        if closed and o.fill:
            if o.fill_style == 'solid':
                fill_options = copy.copy(o)
                fill_options.disable_multi_stroke = True
                shape = arc(x, y, width, height, start, stop, True, False, fill_options)
                shape.type = 'fillPath'
                paths.append(shape)
            else:
                paths.append(pattern_fill_arc(x, y, width, height, start, stop, o))
        if o.stroke != NOS:
            paths.append(outline)
        return self._d('arc', paths, o)

    def curve(self, points, options=None):
        o = self._o(options)
        paths = []
        outline = curve(points, o)
        if o.fill and o.fill != NOS and len(points) >= 3:
            bcurve = curve_to_bezier(points)
            poly_points = points_on_bezier_curves(bcurve, 10, (1 + o.roughness) / 2)
            if o.fill_style == 'solid':
                paths.append(solid_fill_polygon([poly_points], o))
            else:
                paths.append(pattern_fill_polygons([poly_points], o))
        if o.stroke != NOS:
            paths.append(outline)
        return self._d('curve', paths, o)

    def polygon(self, points, options=None):
        o = self._o(options)
        paths = []
        outline = linear_path(points, True, o)
        if o.fill:
            if o.fill_style == 'solid':
                paths.append(solid_fill_polygon([points], o))
            else:
                paths.append(pattern_fill_polygons([points], o))
        if o.stroke != NOS:
            paths.append(outline)
        return self._d('polygon', paths, o)

    def path(self, d, options=None):
        o = self._o(options)
        paths = []
        if not d:
            return self._d('path', paths, o)
        d = re.sub(r'\n|(\s\s)', ' ', d)
        d = re.sub(r'-\s', '-', d)

        has_fill = o.fill and o.fill != 'transparent' and o.fill != NOS
        has_stroke = o.stroke != NOS
        simplified = bool(o.simplification and (o.simplification < 1))
        distance = (4 - 4 * int(o.simplification)) if simplified else ((1 + o.roughness) / 2)
        sets = points_on_path(d, 1, distance)

        if has_fill:
            if o.fill_style == 'solid':
                paths.append(solid_fill_polygon(sets, o))
            else:
                paths.append(pattern_fill_polygons(sets, o))
        if has_stroke:
            if simplified:
                for s in sets:
                    paths.append(linear_path(s, False, o))
            else:
                paths.append(svg_path(d, o))

        return self._d('path', paths, o)

    def ops_to_path(self, drawing, fixed_decimals=None):
        path = ''
        for item in drawing.ops:
            data = item.data if fixed_decimals is None else [round(d, fixed_decimals) for d in item.data]
            if item.op == 'move':
                path += 'M{} {} '.format(data[0], data[1])
            elif item.op == 'bcurveTo':
                path += 'C{} {} {} {} {} {} '.format(data[0], data[1], data[2], data[3], data[4], data[5])
            elif item.op == 'lineTo':
                path += 'L{} {} '.format(data[0], data[1])
        return path.strip()

    def fill_sketch(self, drawing, o):
        fweight = o.fill_weight
        if fweight < 0:
            fweight = o.stroke_width / 2
        return {
            'd': self.ops_to_path(drawing),
            'stroke': o.fill or NOS,
            'strokeWidth': fweight,
            'fill': NOS,
        }


def rotate_points(points, center, degrees):
    if points and len(points):
        cx, cy = center
        angle = (math.pi / 180) * degrees
        cos = math.cos(angle)
        sin = math.sin(angle)
        for p in points:
            x, y = p
            p[0] = ((x - cx) * cos) - ((y - cy) * sin) + cx
            p[1] = ((x - cx) * sin) + ((y - cy) * cos) + cy


def rotate_lines(lines, center, degrees):
    points = []
    for line in lines:
        points.extend(line)
    rotate_points(points, center, degrees)


def line_length(line):
    p1 = line[0]
    p2 = line[1]
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
