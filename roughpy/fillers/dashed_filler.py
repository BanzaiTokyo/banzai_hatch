import math
from .filler_interface import PatternFiller
from .scan_line_hachure import polygon_hachure_lines
from ..core import OpSet
from ..geometry import line_length


class DashedFiller(PatternFiller):
    def __init__(self, helper):
        self.helper = helper

    def fill_polygons(self, polygon_list, o):
        lines = polygon_hachure_lines(polygon_list, o)
        return OpSet(type='fillSketch', ops=self.dashed_line(lines, o))

    def dashed_line(self, lines, o):
        offset = o.dash_offset if o.dash_offset >= 0 else (o.hachure_gap if o.hachure_gap >= 0 else (o.stroke_width * 4))
        gap = o.dash_gap if o.dash_gap >= 0 else (o.hachure_gap if o.hachure_gap >= 0 else (o.stroke_width * 4))
        ops = []
        for line in lines:
            length = line_length(line)
            count = math.floor(length / (offset + gap))
            start_offset = (length + gap - (count * (offset + gap))) / 2
            p1, p2 = line
            if p1[0] > p2[0]:
                p2, p1 = line
            dx = p2[0] - p1[0]
            alpha = math.atan((p2[1] - p1[1]) / dx) if dx != 0 else math.pi / 2
            for i in range(count):
                lstart = i * (offset + gap)
                lend = lstart + offset
                start = [p1[0] + (lstart * math.cos(alpha)) + (start_offset * math.cos(alpha)), p1[1] + lstart * math.sin(alpha) + (start_offset * math.sin(alpha))]
                end = [p1[0] + (lend * math.cos(alpha)) + (start_offset * math.cos(alpha)), p1[1] + (lend * math.sin(alpha)) + (start_offset * math.sin(alpha))]
                ops.extend(self.helper.double_line_ops(start[0], start[1], end[0], end[1], o))
        return ops
