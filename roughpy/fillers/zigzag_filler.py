import copy
import math
from .hachure_filler import HachureFiller
from .scan_line_hachure import polygon_hachure_lines
from ..geometry import line_length
from ..core import OpSet


class ZigZagFiller(HachureFiller):
    def fill_polygons(self, polygon_list, o):
        gap = o.hachure_gap
        if gap < 0:
            gap = o.stroke_width * 4
        gap = max(gap, 0.1)
        o2 = copy.copy(o)
        o2.hachure_gap = gap
        lines = polygon_hachure_lines(polygon_list, o2)
        zigzag_angle = (math.pi / 180) * o.hachure_angle
        zigzag_lines = []
        dgx = gap * 0.5 * math.cos(zigzag_angle)
        dgy = gap * 0.5 * math.sin(zigzag_angle)
        for p1, p2 in lines:
            if line_length((p1, p2)):
                zigzag_lines.append([
                    [p1[0] - dgx, p1[1] + dgy],
                    [p2[0], p2[1]]
                ])
                zigzag_lines.append([
                    [p1[0] + dgx, p1[1] - dgy],
                    [p2[0], p2[1]]
                ])
        ops = self.render_lines(zigzag_lines, o)
        return OpSet(type='fillSketch', ops=ops)
