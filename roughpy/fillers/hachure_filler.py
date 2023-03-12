from .filler_interface import PatternFiller
from ..core import Options, OpSet, Op
from ..geometry import Point, Line
from .scan_line_hachure import polygon_hachure_lines


class HachureFiller(PatternFiller):
    def __init__(self, helper):
        self.helper = helper

    def fill_polygons(self, polygon_list, o):
        return self._fill_polygons(polygon_list, o)

    def _fill_polygons(self, polygon_list, o):
        lines = polygon_hachure_lines(polygon_list, o)
        ops = self.render_lines(lines, o)
        return OpSet('fillSketch', ops)

    def render_lines(self, lines, o):
        ops = []
        for line in lines:
            ops.extend(self.helper.double_line_ops(line[0][0], line[0][1], line[1][0], line[1][1], o))
        return ops
