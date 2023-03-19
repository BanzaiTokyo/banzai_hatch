import math
import copy
from .fillers.filler import get_filler
from .fillers.filler_interface import RenderHelper
from .roughmath import Random
from .path_data_parser import parse_path, normalize, absolutize
from .core import Op, OpSet, Point


class EllipseParams:
    def __init__(self, rx, ry, increment):
        self.rx = rx
        self.ry = ry
        self.increment = increment


class EllipseResult:
    def __init__(self, opset, estimated_points):
        self.opset = opset
        self.estimated_points = estimated_points


helper = RenderHelper()


def _offset(min, max, ops, roughness_gain=1):
    return ops.roughness * roughness_gain * ((random(ops) * (max - min)) + min)


def _offset_opt(x, ops, roughness_gain=1):
    return _offset(-x, x, ops, roughness_gain)


def _line(x1, y1, x2, y2, o, move, overlay):
    length_sq = math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2)
    length = math.sqrt(length_sq)
    roughness_gain = 1
    if length < 200:
        roughness_gain = 1
    elif length > 500:
        roughness_gain = 0.4
    else:
        roughness_gain = (-0.0016668) * length + 1.233334

    offset = o.max_randomness_offset or 0
    if (offset * offset * 100) > length_sq:
        offset = length / 10
    half_offset = offset / 2
    diverge_point = 0.2 + random(o) * 0.2
    mid_disp_x = o.bowing * o.max_randomness_offset * (y2 - y1) / 200
    mid_disp_y = o.bowing * o.max_randomness_offset * (x1 - x2) / 200
    mid_disp_x = _offset_opt(mid_disp_x, o, roughness_gain)
    mid_disp_y = _offset_opt(mid_disp_y, o, roughness_gain)
    ops = []
    random_half = lambda: _offset_opt(half_offset, o, roughness_gain)
    random_full = lambda: _offset_opt(offset, o, roughness_gain)
    preserve_vertices = o.preserve_vertices
    if move:
        if overlay:
            ops.append(Op(
                op='move',
                data=[
                    x1 + (0 if preserve_vertices else random_half()),
                    y1 + (0 if preserve_vertices else random_half()),
                ],
            ))
        else:
            ops.append(Op(
                op='move',
                data=[
                    x1 + (0 if preserve_vertices else _offset_opt(offset, o, roughness_gain)),
                    y1 + (0 if preserve_vertices else _offset_opt(offset, o, roughness_gain)),
                ],
            ))
    if overlay:
        ops.append(Op(
            op='bcurveTo',
            data=[
                mid_disp_x + x1 + (x2 - x1) * diverge_point + random_half(),
                mid_disp_y + y1 + (y2 - y1) * diverge_point + random_half(),
                mid_disp_x + x1 + 2 * (x2 - x1) * diverge_point + random_half(),
                mid_disp_y + y1 + 2 * (y2 - y1) * diverge_point + random_half(),
                x2 + (0 if preserve_vertices else random_half()),
                y2 + (0 if preserve_vertices else random_half()),
            ],
        ))
    else:
        ops.append(Op(
            op='bcurveTo',
            data=[
                mid_disp_x + x1 + (x2 - x1) * diverge_point + random_full(),
                mid_disp_y + y1 + (y2 - y1) * diverge_point + random_full(),
                mid_disp_x + x1 + 2 * (x2 - x1) * diverge_point + random_full(),
                mid_disp_y + y1 + 2 * (y2 - y1) * diverge_point + random_full(),
                x2 + (0 if preserve_vertices else random_full()),
                y2 + (0 if preserve_vertices else random_full()),
            ],
        ))
    return ops


def _double_line(x1, y1, x2, y2, o, filling=False):
    single_stroke = o.disable_multi_stroke_fill if filling else o.disable_multi_stroke
    o1 = _line(x1, y1, x2, y2, o, True, False)
    if single_stroke:
        return o1
    o2 = _line(x1, y1, x2, y2, o, True, True)
    return o1 + o2


def _curve(points, close_point, o):
    len_ = len(points)
    ops = []
    if len_ > 3:
        s = 1 - o.curve_tightness
        ops.append(Op(op='move', data=[points[1][0], points[1][1]]))
        for i in range(1, len_ - 2):
            cached_vert_array = points[i]
            b = [
                (cached_vert_array[0], cached_vert_array[1]),
                (cached_vert_array[0] + (s * points[i + 1][0] - s * points[i - 1][0]) / 6,
                 cached_vert_array[1] + (s * points[i + 1][1] - s * points[i - 1][1]) / 6),
                (points[i + 1][0] + (s * points[i][0] - s * points[i + 2][0]) / 6,
                 points[i + 1][1] + (s * points[i][1] - s * points[i + 2][1]) / 6),
                (points[i + 1][0], points[i + 1][1])
            ]
            ops.append(Op(op='bcurveTo', data=[b[1][0], b[1][1], b[2][0], b[2][1], b[3][0], b[3][1]]))
        if close_point and len(close_point) == 2:
            ro = o.max_randomness_offset
            ops.append(Op(op='lineTo', data=[close_point[0] + _offset_opt(ro, o), close_point[1] + _offset_opt(ro, o)]))
    elif len_ == 3:
        ops.append(Op(op='move', data=[points[1][0], points[1][1]]))
        ops.append(Op(op='bcurveTo',
                      data=[points[1][0], points[1][1], points[2][0], points[2][1], points[2][0], points[2][1]]))
    elif len_ == 2:
        ops.append(_double_line(points[0][0], points[0][1], points[1][0], points[1][1], o))
    return ops


def _curve_with_offset(points, offset, o):
    ps = []
    ps.append((
        points[0][0] + _offset_opt(offset, o),
        points[0][1] + _offset_opt(offset, o),
    ))
    ps.append((
        points[0][0] + _offset_opt(offset, o),
        points[0][1] + _offset_opt(offset, o),
    ))
    for i in range(1, len(points)):
        ps.append((
            points[i][0] + _offset_opt(offset, o),
            points[i][1] + _offset_opt(offset, o),
        ))
        if i == (len(points) - 1):
            ps.append((
                points[i][0] + _offset_opt(offset, o),
                points[i][1] + _offset_opt(offset, o),
            ))
    return _curve(ps, None, o)


def _compute_ellipse_points(increment, cx, cy, rx, ry, offset, overlap, o):
    core_only = o.roughness == 0
    core_points = []
    all_points = []

    if core_only:
        increment = increment / 4
        all_points.append((
            cx + rx * math.cos(-increment),
            cy + ry * math.sin(-increment),
        ))
        angle = 0
        while angle <= math.pi * 2:
            p: Point = (cx + rx * math.cos(angle), cy + ry * math.sin(angle))
            core_points.append(p)
            all_points.append(p)
            angle += increment
        all_points.append((
            cx + rx * math.cos(0),
            cy + ry * math.sin(0),
        ))
        all_points.append((
            cx + rx * math.cos(increment),
            cy + ry * math.sin(increment),
        ))
    else:
        rad_offset = _offset_opt(0.5, o) - (math.pi / 2)
        all_points.append((
            _offset_opt(offset, o) + cx + 0.9 * rx * math.cos(rad_offset - increment),
            _offset_opt(offset, o) + cy + 0.9 * ry * math.sin(rad_offset - increment),
        ))
        end_angle = math.pi * 2 + rad_offset - 0.01
        angle = rad_offset
        while angle < end_angle:
            p: Point = (
                _offset_opt(offset, o) + cx + rx * math.cos(angle),
                _offset_opt(offset, o) + cy + ry * math.sin(angle),
            )
            core_points.append(p)
            all_points.append(p)
            angle += increment
        all_points.append((
            _offset_opt(offset, o) + cx + rx * math.cos(rad_offset + math.pi * 2 + overlap * 0.5),
            _offset_opt(offset, o) + cy + ry * math.sin(rad_offset + math.pi * 2 + overlap * 0.5),
        ))
        all_points.append((
            _offset_opt(offset, o) + cx + 0.98 * rx * math.cos(rad_offset + overlap),
            _offset_opt(offset, o) + cy + 0.98 * ry * math.sin(rad_offset + overlap),
        ))
        all_points.append((
            _offset_opt(offset, o) + cx + 0.9 * rx * math.cos(rad_offset + overlap * 0.5),
            _offset_opt(offset, o) + cy + 0.9 * ry * math.sin(rad_offset + overlap * 0.5),
        ))

    return [all_points, core_points]


def _arc(increment, cx, cy, rx, ry, strt, stp, offset, o):
    rad_offset = strt + _offset_opt(0.1, o)
    points = []
    points.append((
        _offset_opt(offset, o) + cx + 0.9 * rx * math.cos(rad_offset - increment),
        _offset_opt(offset, o) + cy + 0.9 * ry * math.sin(rad_offset - increment),
    ))
    angle = rad_offset
    while angle <= stp:
        points.append((
            _offset_opt(offset, o) + cx + rx * math.cos(angle),
            _offset_opt(offset, o) + cy + ry * math.sin(angle),
        ))
        angle += increment
    points.append((
        cx + rx * math.cos(stp),
        cy + ry * math.sin(stp),
    ))
    points.append((
        cx + rx * math.cos(stp),
        cy + ry * math.sin(stp),
    ))
    return _curve(points, None, o)


def _bezier_to(x1, y1, x2, y2, x, y, current, o):
    ops = []
    ros = [o.max_randomness_offset or 1, (o.max_randomness_offset or 1) + 0.3]
    iterations = 1 if o.disable_multi_stroke else 2
    preserve_vertices = o.preserve_vertices
    for i in range(iterations):
        if i == 0:
            ops.append(Op(op='move', data=[current[0], current[1]]))
        else:
            ops.append(Op(op='move', data=[current[0] + (0 if preserve_vertices else _offset_opt(ros[0], o)),
                                           current[1] + (0 if preserve_vertices else _offset_opt(ros[0], o))]))
        f = [x, y] if preserve_vertices else [x + _offset_opt(ros[i], o), y + _offset_opt(ros[i], o)]
        ops.append(Op(
            op='bcurveTo',
            data=[
                x1 + _offset_opt(ros[i], o), y1 + _offset_opt(ros[i], o),
                x2 + _offset_opt(ros[i], o), y2 + _offset_opt(ros[i], o),
                f[0], f[1],
            ],
        ))
    return ops


def clone_options_alter_seed(ops):
    result = copy.copy(ops)
    result.randomizer = None
    if ops.seed:
        result.seed = ops.seed + 1
    return result


def random(ops):
    if not ops.randomizer:
        ops.randomizer = Random(ops.seed or 0)
    return ops.randomizer.next()


def line(x1, y1, x2, y2, o):
    return OpSet(type='path', ops=_double_line(x1, y1, x2, y2, o))


def linear_path(points, close, o):
    len_ = len(points) if points else 0
    if len_ > 2:
        ops = []
        for i in range(len_ - 1):
            ops += _double_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], o)
        if close:
            ops += _double_line(points[len_ - 1][0], points[len_ - 1][1], points[0][0], points[0][1], o)
        return OpSet(type='path', ops=ops)
    elif len_ == 2:
        return line(points[0][0], points[0][1], points[1][0], points[1][1], o)
    return OpSet(type='path', ops=[])


def polygon(points, o):
    return linear_path(points, True, o)


def rectangle(x, y, width, height, o):
    points = [
        [x, y],
        [x + width, y],
        [x + width, y + height],
        [x, y + height],
    ]
    return polygon(points, o)


def curve(points, o):
    o1 = _curve_with_offset(points, 1 * (1 + o.roughness * 0.2), o)
    if not o.disable_multi_stroke:
        o2 = _curve_with_offset(points, 1.5 * (1 + o.roughness * 0.22), clone_options_alter_seed(o))
        o1 += o2
    return OpSet(type='path', ops=o1)


def ellipse(x, y, width, height, o):
    params = generate_ellipse_params(width, height, o)
    return ellipse_with_params(x, y, o, params)


def generate_ellipse_params(width, height, o):
    psq = math.sqrt(math.pi * 2 * math.sqrt((width / 2) ** 2 + (height / 2) ** 2) / 2)
    step_count = math.ceil(max(o.curve_step_count, (o.curve_step_count / math.sqrt(200)) * psq))
    increment = (math.pi * 2) / step_count
    rx = abs(width / 2)
    ry = abs(height / 2)
    curve_fit_randomness = 1 - o.curve_fitting
    rx += _offset_opt(rx * curve_fit_randomness, o)
    ry += _offset_opt(ry * curve_fit_randomness, o)
    return EllipseParams(rx=rx, ry=ry, increment=increment)


def ellipse_with_params(x, y, o, ellipse_params):
    ap1, cp1 = _compute_ellipse_points(ellipse_params.increment, x, y, ellipse_params.rx, ellipse_params.ry, 1,
                                       ellipse_params.increment * _offset(0.1, _offset(0.4, 1, o), o), o)
    o1 = _curve(ap1, None, o)
    if not o.disable_multi_stroke and o.roughness != 0:
        ap2, _ = _compute_ellipse_points(ellipse_params.increment, x, y, ellipse_params.rx, ellipse_params.ry,
                                         1.5, 0, o)
        o2 = _curve(ap2, None, o)
        o1 += o2
    return EllipseResult(opset=OpSet(type='path', ops=o1), estimated_points=cp1)


def arc(cx, cy, width, height, start, stop, closed, rough_closure, o):
    rx = abs(width / 2)
    ry = abs(height / 2)
    rx += _offset_opt(rx * 0.01, o)
    ry += _offset_opt(ry * 0.01, o)
    strt = start
    stp = stop
    while strt < 0:
        strt += math.pi * 2
        stp += math.pi * 2
    if (stp - strt) > (math.pi * 2):
        strt = 0
        stp = math.pi * 2
    ellipse_inc = (math.pi * 2) / o.curve_step_count
    arc_inc = min(ellipse_inc / 2, (stp - strt) / 2)
    ops = _arc(arc_inc, cx, cy, rx, ry, strt, stp, 1, o)
    if not o.disable_multi_stroke:
        o2 = _arc(arc_inc, cx, cy, rx, ry, strt, stp, 1.5, o)
        ops.extend(o2)
    if closed:
        if rough_closure:
            ops.extend(
                _double_line(cx, cy, cx + rx * math.cos(strt), cy + ry * math.sin(strt), o)
            )
            ops.extend(
                _double_line(cx, cy, cx + rx * math.cos(stp), cy + ry * math.sin(stp), o)
            )
        else:
            ops.extend([
                Op(op='lineTo', data=[cx, cy]),
                Op(op='lineTo', data=[cx + rx * math.cos(strt), cy + ry * math.sin(strt)])
            ])
    return OpSet(type='path', ops=ops)


def svg_path(path, o):
    segments = normalize(absolutize(parse_path(path)))
    ops = []
    first = [0, 0]
    current = [0, 0]
    for segment in segments:
        key = segment['key']
        data = segment['data']
        if key == 'M':
            ro = 1 * (o.max_randomness_offset or 0)
            pv = o.preserve_vertices
            ops.append(Op(op='move', data=[d + (0 if pv else _offset_opt(ro, o)) for d in data]))
            current = [data[0], data[1]]
            first = [data[0], data[1]]
        elif key == 'L':
            ops.extend(_double_line(current[0], current[1], data[0], data[1], o))
            current = [data[0], data[1]]
        elif key == 'C':
            x1, y1, x2, y2, x, y = data
            ops.extend(_bezier_to(x1, y1, x2, y2, x, y, current, o))
            current = [x, y]
        elif key == 'Z':
            ops.extend(_double_line(current[0], current[1], first[0], first[1], o))
            current = [first[0], first[1]]
    return OpSet(type='path', ops=ops)


def solid_fill_polygon(polygon_list, o):
    ops = []
    for points in polygon_list:
        len_ = len(points)
        if len_ > 2:
            offset = o.max_randomness_offset or 0
            ops.append(
                Op(op='move', data=[points[0][0] + _offset_opt(offset, o), points[0][1] + _offset_opt(offset, o)]))
            for i in range(1, len_):
                ops.append(Op(op='lineTo',
                              data=[points[i][0] + _offset_opt(offset, o), points[i][1] + _offset_opt(offset, o)]))
    return OpSet(type='fillPath', ops=ops)


def pattern_fill_polygons(polygon_list, o):
    return get_filler(o, helper).fill_polygons(polygon_list, o)


def pattern_fill_arc(cx, cy, width, height, start, stop, o):
    rx = abs(width / 2)
    ry = abs(height / 2)
    rx += _offset_opt(rx * 0.01, o)
    ry += _offset_opt(ry * 0.01, o)
    strt = start
    stp = stop
    while strt < 0:
        strt += math.pi * 2
        stp += math.pi * 2
    if (stp - strt) > (math.pi * 2):
        strt = 0
        stp = math.pi * 2
    increment = (stp - strt) / o.curve_step_count
    points = []
    for angle in range(strt, stp, increment):
        points.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    points.append((cx + rx * math.cos(stp), cy + ry * math.sin(stp)))
    points.append((cx, cy))
    return pattern_fill_polygons([points], o)


def rand_offset(x, o):
    return _offset_opt(x, o)


def rand_offset_with_range(min, max, o):
    return _offset(min, max, o)


def double_line_fill_ops(x1, y1, x2, y2, o):
    return _double_line(x1, y1, x2, y2, o, True)


helper.rand_offset = rand_offset
helper.rand_offset_with_range = rand_offset_with_range
helper.ellipse = ellipse
helper.double_line_ops = double_line_fill_ops
