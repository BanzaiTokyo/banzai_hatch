from random import randint, uniform
import sys
import math
from lxml import etree
import inkex
from inkex.transforms import DirectedLineSegment
from inkex.styles import Style
from inkex.paths import CubicSuperPath


class oval_fill(inkex.EffectExtension):
    F_MINGAP_SMALL_VALUE = 1E-10
    MIN_HATCH_FRACTION = 0.25

    def __init__(self):
        super().__init__()
        self.xmin, self.ymin = (0.0, 0.0)
        self.xmax, self.ymax = (0.0, 0.0)
        self.paths = {}
        self.grid = []
        self.hatches = {}
        self.transforms = {}

    def add_arguments(self, pars):
        pars.add_argument("--hatchSpacing", type=int, default=10)
        pars.add_argument("--hatchAngle", type=int, default=90)
        pars.add_argument("--crossHatch", type=inkex.Boolean, default=False)
        pars.add_argument("--outer_dist", type=int, default=0)
        pars.add_argument("--curv_coef", type=int, default=1)
        pars.add_argument("--len_hatch", type=int, default=10)

    def effect(self):
        self.hatch_spacing_px = self.options.hatchSpacing
        self.options.inset_dist = 1
        self.options.tolerance = 2.0
        self.inset_dist_px = self.options.inset_dist
        self.options.crossHatch = False

        self.recursivelyTraverseSvg(self.svg.selection)
        for node in self.hatches:
            path = ''
            for (line_start, line_end) in self.hatches[node]:
                path += self.buildHatchLinePath(line_start, line_end)
            self.joinFillsWithNode(node, path[:])

    def recursivelyTraverseSvg(self, a_node_list):
        for node in a_node_list:
            self.xmin, self.ymin = (0.0, 0.0)
            self.xmax, self.ymax = (0.0, 0.0)
            self.paths = {}
            self.grid = []
            path_data = None
            if node.tag in [inkex.addNS('g', 'svg'), 'g']:
                self.recursivelyTraverseSvg(node)
            if node.tag in [inkex.addNS('rect', 'svg'), 'rect']:
                x = float(node.get('x'))
                y = float(node.get('y'))
                w = float(node.get('width', '0'))
                h = float(node.get('height', '0'))
                path_data = f'M {x},{y} l {w},0 l 0,{h} l {-w},0 Z'
            elif node.tag in [inkex.addNS('ellipse', 'svg'), 'ellipse',
                              inkex.addNS('circle', 'svg'), 'circle']:
                if node.tag in [inkex.addNS('ellipse', 'svg'), 'ellipse']:
                    rx = float(node.get('rx', '0'))
                    ry = float(node.get('ry', '0'))
                else:
                    rx = float(node.get('r', '0'))
                    ry = rx
                cx = float(node.get('cx', '0'))
                cy = float(node.get('cy', '0'))
                x1 = cx - rx
                x2 = cx + rx
                path_data = 'M {x1:f},{cy:f} A {rx:f},{ry:f} 0 1 0 {x2:f},{cy:f} A {rx:f},{ry:f} 0 1 0 {x1:f},{cy:f}'.format(
                    x1=x1, x2=x2, rx=rx, ry=ry, cy=cy)
            elif node.tag in [inkex.addNS('polygon', 'svg'), 'polygon']:
                pa = node.get('points', '').strip().split()
                path_data = "".join(["M " + pa[i] if i == 0 else " L " + pa[i] for i in range(0, len(pa))])
                path_data += " Z"
            elif node.tag in [inkex.addNS('polyline', 'svg'), 'polyline']:
                pa = node.get('points', '').strip().split()
                pathLength = len(pa)
                if pathLength < 4:
                    continue
                path_data = "M " + pa[0] + " " + pa[1]
                i = 2
                while i < (pathLength - 1):
                    path_data += " L " + pa[i] + " " + pa[i + 1]
                    i += 2
            elif node.tag in [inkex.addNS('line', 'svg'), 'line']:
                path_data = f"M {node.get('x1')},{node.get('y1')} L {node.get('x2')},{node.get('y2')}"
            elif node.tag in [inkex.addNS('path', 'svg'), 'path']:
                path_data = node.get('d')
            if not path_data:
                continue
            self.addPathVertices(path_data, node)
            b_have_grid = self.makeHatchGrid(float(self.options.hatchAngle), float(self.hatch_spacing_px), True)
            if b_have_grid:
                if self.options.crossHatch:
                    self.makeHatchGrid(float(self.options.hatchAngle + 90.0), float(self.hatch_spacing_px), False)
                for h in self.grid:
                    self.interstices((h[0], h[1]), (h[2], h[3]))

    def buildHatchLinePath(self, pt1, pt2):

        od = self.options.outer_dist  # Outer contour indent
        cc = self.options.curv_coef  # Pseudo-human coefficient
        rds = self.options.len_hatch
        x1, y1 = pt1[0], pt1[1] + rds / 2 + od
        x2, y2 = pt2[0], pt2[1] + rds / 2 + od

        # absolute length of the segment between the points
        w = x2 - x1
        h = y2 - y1

        totLen = (w ** 2 + h ** 2) ** 0.5

        wx = w / totLen
        hx = h / totLen

        number_segm = int(totLen // rds)
        if number_segm == 0:
            number_segm = 1
        dxR = rds * wx + (w % rds) / number_segm
        dyR = rds * hx + (h % rds) / number_segm

        path = ''
        x1 += hx * rds / 2
        y1 += wx * rds / 2
        for _ in range(number_segm + 1):
            rnd = [uniform(-cc, cc) for _ in range(10)]

            path += f'M {x1}, {y1 - abs(rnd[0])} c {0}, {rds * 2 / 3 + rnd[2]}  {-rds}, {rds * 2 / 3} {-rds} {rnd[4] / 3} \
                      M {x1}, {y1 + abs(rnd[1])} c {0}, {-rds * 2 / 3 + rnd[3]}  {-rds}, {-rds * 2 / 3} {-rds} {rnd[5] / 3} '

            x1 += dxR
            y1 += dyR

        return path

    def joinFillsWithNode(self, node, path):
        if not path:
            return
        parent = node.getparent()
        if parent is None:
            parent = self.document.getroot()
        g = etree.SubElement(parent, inkex.addNS('g', 'svg'))
        g.append(node)
        style = Style(node.get('style'))
        style = f"stroke:{style.get('stroke', '#000000')};stroke-width:{style.get('stroke-width', '1.0')}"
        line_attribs = {'style': style, 'd': path, 'fill': 'none'}
        tran = node.get('transform')
        if tran:
            line_attribs['transform'] = tran
        etree.SubElement(g, inkex.addNS('path', 'svg'), line_attribs)

    @staticmethod
    def distanceSquared(p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx * dx + dy * dy

    @staticmethod
    def subdivideCubicPath(sp, flat, i=1):
        while True:
            while True:
                if i >= len(sp):
                    return
                p0 = sp[i - 1][1]
                p1 = sp[i - 1][2]
                p2 = sp[i][0]
                p3 = sp[i][1]
                b = (p0, p1, p2, p3)
                if oval_fill.maxdist(*b) > flat:
                    break
                i += 1
            one, two = oval_fill.beziersplitatt(*b, 0.5)
            sp[i - 1][2] = one[1]
            sp[i][0] = two[2]
            p = [one[2], one[3], two[1]]
            sp[i:1] = [p]

    @staticmethod
    def beziersplitatt(p0, p1, p2, p3, t):
        def tpoint(param1, param2):
            (x1, y1) = param1
            (x2, y2) = param2
            return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

        m1 = tpoint(p0, p1)
        m2 = tpoint(p1, p2)
        m3 = tpoint(p2, p3)
        m4 = tpoint(m1, m2)
        m5 = tpoint(m2, m3)
        m = tpoint(m4, m5)
        return (p0, m1, m4, m), (m, m5, m3, p3)

    @staticmethod
    def maxdist(p0, p1, p2, p3):
        s1 = DirectedLineSegment(p0, p3)
        return max(s1.distance_to_point(*p1), s1.distance_to_point(*p2))

    def addPathVertices(self, path, node):
        p = CubicSuperPath(path)
        if len(p) == 0:
            return

        subpaths = []
        subpath_vertices = []
        for sp in p:
            if len(subpath_vertices):
                if self.distanceSquared(subpath_vertices[0], subpath_vertices[-1]) < 1:
                    subpaths.append(subpath_vertices)
            subpath_vertices = []
            self.subdivideCubicPath(sp, float(self.options.tolerance / 100))
            for csp in sp:
                subpath_vertices.append(csp[1])
        if len(subpath_vertices):
            if self.distanceSquared(subpath_vertices[0], subpath_vertices[-1]) < 1:
                subpaths.append(subpath_vertices)
        if len(subpaths) == 0:
            return
        self.paths[node] = subpaths

    def makeHatchGrid(self, angle, spacing, init=True):
        if init:
            self.getBoundingBox()
            self.grid = []

        w = self.xmax - self.xmin
        h = self.ymax - self.ymin
        b_bounding_box_exists = w > 0 and h > 0
        if not b_bounding_box_exists:
            return False

        r = math.sqrt(w * w + h * h) / 2.0
        ca = math.cos(math.radians(90 - angle))
        sa = math.sin(math.radians(90 - angle))
        cx = self.xmin + (w / 2)
        cy = self.ymin + (h / 2)
        spacing = float(abs(spacing))
        i = -r
        while i <= r:
            # Line starts at (i, -r) and goes to (i, +r)
            x1 = cx + (i * ca) + (r * sa)  # i * ca - (-r) * sa
            y1 = cy + (i * sa) - (r * ca)  # i * sa + (-r) * ca
            x2 = cx + (i * ca) - (r * sa)  # i * ca - (+r) * sa
            y2 = cy + (i * sa) + (r * ca)  # i * sa + (+r) * ca
            i += spacing
            if (x1 < self.xmin and x2 < self.xmin) or (x1 > self.xmax and x2 > self.xmax):
                continue
            if (y1 < self.ymin and y2 < self.ymin) or (y1 > self.ymax and y2 > self.ymax):
                continue
            self.grid.append((x1, y1, x2, y2))
        return True

    def getBoundingBox(self):
        EXTREME = 1.0E70  # Just a big unreachable coordinate
        self.xmin, self.xmax = EXTREME, -EXTREME
        self.ymin, self.ymax = EXTREME, -EXTREME
        for path in self.paths:
            for subpath in self.paths[path]:
                for vertex in subpath:
                    if vertex[0] < self.xmin:
                        self.xmin = vertex[0]
                    if vertex[0] > self.xmax:
                        self.xmax = vertex[0]
                    if vertex[1] < self.ymin:
                        self.ymin = vertex[1]
                    if vertex[1] > self.ymax:
                        self.ymax = vertex[1]

    @staticmethod
    def intersect(p1, p2, p3, p4):
        """ if lines (p1, p2) and (p3, p4) intersect,
            return %% of line 1 length from start to the intersection point
        """
        d21x = p2[0] - p1[0]
        d21y = p2[1] - p1[1]
        d43x = p4[0] - p3[0]
        d43y = p4[1] - p3[1]
        d = d21x * d43y - d21y * d43x
        if d == 0:
            return -1.0

        nb = (p1[1] - p3[1]) * d21x - (p1[0] - p3[0]) * d21y
        sb = float(nb) / float(d)
        if sb < 0 or sb > 1:
            return -1.0

        na = (p1[1] - p3[1]) * d43x - (p1[0] - p3[0]) * d43y
        sa = float(na) / float(d)
        if sa < 0 or sa > 1:
            return -1.0
        return sa

    def interstices(self, p1, p2):
        f_hold_back_steps = self.inset_dist_px
        b_hold_back_hatches = f_hold_back_steps != 0.0
        hatches = self.hatches
        d_and_a = []
        # p1 & p2 is the hatch line
        # p3 & p4 is the polygon edge to check
        for path in self.paths:
            for subpath in self.paths[path]:
                p3 = subpath[0]
                for p4 in subpath[1:]:
                    s = self.intersect(p1, p2, p3, p4)
                    if 0.0 <= s <= 1.0:
                        if b_hold_back_hatches:
                            angle_hatch_radians = math.atan2(-(p2[1] - p1[1]), (p2[0] - p1[0]))
                            angle_segment_radians = math.atan2(-(p4[1] - p3[1]), (p4[0] - p3[0]))
                            angle_difference_radians = angle_hatch_radians - angle_segment_radians
                            # coerce to range -pi to +pi
                            if angle_difference_radians > math.pi:
                                angle_difference_radians -= 2 * math.pi
                            elif angle_difference_radians < -math.pi:
                                angle_difference_radians += 2 * math.pi
                            f_sin_of_join_angle = math.sin(angle_difference_radians)
                            f_abs_sin_of_join_angle = abs(f_sin_of_join_angle)
                            if f_abs_sin_of_join_angle != 0.0:
                                intersection = [0, 0]
                                intersection[0] = p1[0] + s * (p2[0] - p1[0])
                                intersection[1] = p1[1] + s * (p2[1] - p1[1])
                                if abs(angle_difference_radians) < math.pi / 2:
                                    dist_intersection_to_relevant_end = math.hypot(p3[0] - intersection[0],
                                                                                   p3[1] - intersection[1])
                                    dist_intersection_to_irrelevant_end = math.hypot(p4[0] - intersection[0],
                                                                                     p4[1] - intersection[1])
                                else:
                                    dist_intersection_to_relevant_end = math.hypot(p4[0] - intersection[0],
                                                                                   p4[1] - intersection[1])
                                    dist_intersection_to_irrelevant_end = math.hypot(p3[0] - intersection[0],
                                                                                     p3[1] - intersection[1])
                                prelim_length_to_be_removed = f_hold_back_steps / f_abs_sin_of_join_angle
                                length_remove_starting_hatch = prelim_length_to_be_removed
                                length_remove_ending_hatch = prelim_length_to_be_removed

                                if prelim_length_to_be_removed > (
                                        dist_intersection_to_relevant_end + f_hold_back_steps):
                                    length_remove_starting_hatch = dist_intersection_to_relevant_end + f_hold_back_steps
                                if prelim_length_to_be_removed > (
                                        dist_intersection_to_irrelevant_end + f_hold_back_steps):
                                    length_remove_ending_hatch = dist_intersection_to_irrelevant_end + f_hold_back_steps

                                d_and_a.append((s, path, length_remove_starting_hatch, length_remove_ending_hatch))
                            else:
                                # Mark for complete hatch excision, hatch is parallel to segment
                                # Just a random number guaranteed large enough to be longer than any hatch length
                                d_and_a.append((s, path, 123456.0, 123456.0))
                        else:
                            d_and_a.append((s, path, 0, 0))  # zero length to be removed from hatch
                    p3 = p4
        if len(d_and_a) == 0:
            return
        # Remove duplicate intersections.
        d_and_a.sort()
        n = len(d_and_a)
        i_last = 1
        i = 1
        last = d_and_a[0]
        while i < n:
            if (abs(d_and_a[i][0] - last[0])) > self.F_MINGAP_SMALL_VALUE:
                d_and_a[i_last] = last = d_and_a[i]
                i_last += 1
            i += 1
        d_and_a = d_and_a[:i_last]
        i = 0
        while i < (len(d_and_a) - 1):
            if d_and_a[i][1] not in hatches:
                hatches[d_and_a[i][1]] = []

            x1 = p1[0] + d_and_a[i][0] * (p2[0] - p1[0])
            y1 = p1[1] + d_and_a[i][0] * (p2[1] - p1[1])
            x2 = p1[0] + d_and_a[i + 1][0] * (p2[0] - p1[0])
            y2 = p1[1] + d_and_a[i + 1][0] * (p2[1] - p1[1])

            if not b_hold_back_hatches:
                hatches[d_and_a[i][1]].append([[x1, y1], [x2, y2]])
            else:
                f_min_allowed_hatch_length = self.hatch_spacing_px * self.MIN_HATCH_FRACTION
                f_initial_hatch_length = math.hypot(x2 - x1, y2 - y1)
                f_length_to_be_removed_from_pt1 = d_and_a[i][3]
                f_length_to_be_removed_from_pt2 = d_and_a[i + 1][2]
                if (f_initial_hatch_length - (
                        f_length_to_be_removed_from_pt1 + f_length_to_be_removed_from_pt2)) > f_min_allowed_hatch_length:
                    pt1 = self.relativeControlPointPosition(f_length_to_be_removed_from_pt1, x2 - x1, y2 - y1, x1, y1)
                    pt2 = self.relativeControlPointPosition(f_length_to_be_removed_from_pt2, x1 - x2, y1 - y2, x2, y2)
                    hatches[d_and_a[i][1]].append([[pt1[0], pt1[1]], [pt2[0], pt2[1]]])
            i += 2

    @staticmethod
    def relativeControlPointPosition(distance, f_delta_x, f_delta_y, delta_x, delta_y):
        pt_return = [0, 0]
        if f_delta_x == 0:
            pt_return[0] = delta_x
            pt_return[1] = math.copysign(distance, f_delta_y) + delta_y
        elif f_delta_y == 0:
            pt_return[0] = math.copysign(distance, f_delta_x) + delta_x
            pt_return[1] = delta_y
        else:
            f_slope = math.atan2(f_delta_y, f_delta_x)
            pt_return[0] = distance * math.cos(f_slope) + delta_x
            pt_return[1] = distance * math.sin(f_slope) + delta_y
        return pt_return


if __name__ == '__main__':
    oval_fill().run()
