from .points_on_curve import points_on_bezier_curves, simplify
from .path_data_parser import parse_path, normalize, absolutize


def points_on_path(path, tolerance=None, distance=None):
    segments = parse_path(path)
    normalized = normalize(absolutize(segments))

    sets = []
    current_points = []
    start = [0, 0]
    pending_curve = []

    def append_pending_curve():
        nonlocal pending_curve
        if len(pending_curve) >= 4:
            current_points.extend(points_on_bezier_curves(pending_curve, tolerance))
        pending_curve = []

    def append_pending_points():
        nonlocal current_points
        append_pending_curve()
        if current_points:
            sets.append(current_points)
            current_points = []

    for command in normalized:
        key = command['key']
        data = command['data']
        if key == 'M':
            append_pending_points()
            start = [data[0], data[1]]
            current_points.append(start)
        elif key == 'L':
            append_pending_curve()
            current_points.append([data[0], data[1]])
        elif key == 'C':
            if not pending_curve:
                last_point = current_points[-1] if current_points else start
                pending_curve.append([last_point[0], last_point[1]])
            pending_curve.extend([[data[0], data[1]], [data[2], data[3]], [data[4], data[5]]])
        elif key == 'Z':
            append_pending_curve()
            current_points.append([start[0], start[1]])
    append_pending_points()

    if not distance:
        return sets

    out = []
    for set in sets:
        simplified_set = simplify(set, distance)
        if simplified_set:
            out.append(simplified_set)
    return out
