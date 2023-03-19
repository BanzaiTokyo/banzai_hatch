import copy
import math
from .filler_interface import PatternFiller
from .scan_line_hachure import polygon_hachure_lines
from ..core import Options, OpSet
from ..geometry import line_length


class ZigZagLineFiller(PatternFiller):
    def __init__(self, helper):
        self.helper = helper

    def fill_polygons(self, polygon_list, o: Options):
        gap = o.hachure_gap if o.hachure_gap >= 0 else (o.stroke_width * 4)
        zo = o.zigzag_offset if o.zigzag_offset >= 0 else gap
        o = copy.copy(o)
        o.hachure_gap = gap + zo
        lines = polygon_hachure_lines(polygon_list, o)
        return OpSet(type='fillSketch', ops=self.zigzag_lines(lines, zo, o))

    def zigzag_lines(self, lines, zo, o):
        ops = []
        for line in lines:
            length = line_length(line)
            count = round(length / (2 * zo))
            p1, p2 = line
            if p1[0] > p2[0]:
                p2, p1 = line
            dx = p2[0] - p1[0]
            alpha = math.atan((p2[1] - p1[1]) / dx) if dx != 0 else math.pi / 2
            for i in range(count):
                lstart = i * 2 * zo
                lend = (i + 1) * 2 * zo
                dz = math.sqrt(2 * pow(zo, 2))
                start = (p1[0] + (lstart * math.cos(alpha)), p1[1] + lstart * math.sin(alpha))
                end = (p1[0] + (lend * math.cos(alpha)), p1[1] + (lend * math.sin(alpha)))
                middle = [start[0] + dz * math.cos(alpha + math.pi / 4), start[1] + dz * math.sin(alpha + math.pi / 4)]
                ops.extend(self.helper.double_line_ops(start[0], start[1], middle[0], middle[1], o))
                ops.extend(self.helper.double_line_ops(middle[0], middle[1], end[0], end[1], o))
        return ops
