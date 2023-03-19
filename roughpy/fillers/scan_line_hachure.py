from ..geometry import Point, Line, rotate_points, rotate_lines


class EdgeEntry:
    def __init__(self, ymin, ymax, x, islope):
        self.ymin = ymin
        self.ymax = ymax
        self.x = x
        self.islope = islope


class ActiveEdgeEntry:
    def __init__(self, s, edge):
        self.s = s
        self.edge = edge


def polygon_hachure_lines(polygon_list, o):
    angle = o.hachure_angle + 90
    gap = o.hachure_gap
    if gap < 0:
        gap = o.stroke_width * 4
    gap = max(gap, 0.1)

    rotation_center: Point = (.0, .0)
    if angle:
        for polygon in polygon_list:
            rotate_points(polygon, rotation_center, angle)
    lines = straight_hachure_lines(polygon_list, gap)
    if angle:
        for polygon in polygon_list:
            rotate_points(polygon, rotation_center, -angle)
        rotate_lines(lines, rotation_center, -angle)
    return lines


def straight_hachure_lines(polygon_list, gap):
    vertex_array = []
    for polygon in polygon_list:
        vertices = list(polygon)
        if vertices[0] != vertices[-1]:
            vertices.append([vertices[0][0], vertices[0][1]])
        if len(vertices) > 2:
            vertex_array.append(vertices)

    lines = []
    gap = max(gap, 0.1)

    # Create sorted edges table
    edges = []

    for vertices in vertex_array:
        for i in range(len(vertices) - 1):
            p1 = vertices[i]
            p2 = vertices[i + 1]
            if p1[1] != p2[1]:
                ymin = min(p1[1], p2[1])
                edges.append(EdgeEntry(
                    ymin=ymin,
                    ymax=max(p1[1], p2[1]),
                    x=p1[0] if ymin == p1[1] else p2[0],
                    islope=(p2[0] - p1[0]) / (p2[1] - p1[1]),
                ))
    edges.sort(key=lambda e: (e.ymin, e.x, -e.ymax))
    if not edges:
        return lines

    # Start scanning
    active_edges = []
    y = edges[0].ymin
    while active_edges or edges:
        if edges:
            ix = -1
            for i in range(len(edges)):
                if edges[i].ymin > y:
                    break
                ix = i
            removed = edges[:ix + 1]
            del edges[:ix + 1]
            for edge in removed:
                active_edges.append(ActiveEdgeEntry(s=y, edge=edge))
        active_edges = [ae for ae in active_edges if ae.edge.ymax > y]
        active_edges.sort(key=lambda ae: ae.edge.x)

        # fill between the edges
        if len(active_edges) > 1:
            for i in range(0, len(active_edges), 2):
                nexti = i + 1
                if nexti >= len(active_edges):
                    break
                ce = active_edges[i].edge
                ne = active_edges[nexti].edge
                lines.append((
                    (round(ce.x), y),
                    (round(ne.x), y),
                ))
        y += gap
        for ae in active_edges:
            ae.edge.x = ae.edge.x + (gap * ae.edge.islope)
    return lines
