import copy
from .hachure_filler import HachureFiller


class HatchFiller(HachureFiller):
    def fill_polygons(self, polygon_list, o):
        set = self._fill_polygons(polygon_list, o)
        o2 = copy.copy(o)
        o2.hachure_angle += 90
        set2 = self._fill_polygons(polygon_list, o2)
        set.ops = set.ops + set2.ops
        return set
