import copy
import random
import math
from .filler_interface import PatternFiller, RenderHelper
from .scan_line_hachure import polygon_hachure_lines
from ..core import Options, OpSet
from ..geometry import line_length


class DotFiller(PatternFiller):
    def __init__(self, helper: RenderHelper):
        self.helper = helper

    def fill_polygons(self, polygon_list, o: Options):
        o = copy.copy(o)
        o.hachure_angle = 0
        lines = polygon_hachure_lines(polygon_list, o)
        return self.dots_on_lines(lines, o)

    def dots_on_lines(self, lines, o: Options):
        ops = []
        gap = o.hachure_gap
        if gap < 0:
            gap = o.stroke_width * 4
        gap = max(gap, 0.1)
        fweight = o.fill_weight
        if fweight < 0:
            fweight = o.stroke_width / 2
        ro = gap / 4
        for line in lines:
            length = line_length(line)
            dl = length / gap
            count = math.ceil(dl) - 1
            offset = length - (count * gap)
            x = ((line[0][0] + line[1][0]) / 2) - (gap / 4)
            minY = min(line[0][1], line[1][1])

            for i in range(count):
                y = minY + offset + (i * gap)
                cx = (x - ro) + random.random() * 2 * ro
                cy = (y - ro) + random.random() * 2 * ro
                el = self.helper.ellipse(cx, cy, fweight, fweight, o)
                ops.extend(el.opset.ops)
        return OpSet(type='fillSketch', ops=ops)
