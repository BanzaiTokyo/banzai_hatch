import math


def curve_to_bezier(pointsIn, curveTightness=0):
    len_ = len(pointsIn)
    if len_ < 3:
        raise Exception('A curve must have at least three points.')
    out = []
    if len_ == 3:
        out.append(pointsIn[0])
        out.append(pointsIn[1])
        out.append(pointsIn[2])
        out.append(pointsIn[2])
    else:
        points = []
        points.append(pointsIn[0])
        points.append(pointsIn[0])
        for i in range(1, len_):
            points.append(pointsIn[i])
            if i == len_ - 1:
                points.append(pointsIn[i])
        b = []
        s = 1 - curveTightness
        out.append(points[0])
        for i in range(1, len_ + 2):
            cachedVertArray = points[i]
            b[0] = [cachedVertArray[0], cachedVertArray[1]]
            b[1] = [cachedVertArray[0] + (s * points[i + 1][0] - s * points[i - 1][0]) / 6, cachedVertArray[1] + (s * points[i + 1][1] - s * points[i - 1][1]) / 6]
            b[2] = [points[i + 1][0] + (s * points[i][0] - s * points[i + 2][0]) / 6, points[i + 1][1] + (s * points[i][1] - s * points[i + 2][1]) / 6]
            b[3] = [points[i + 1][0], points[i + 1][1]]
            out.append(b[1])
            out.append(b[2])
            out.append(b[3])
    return out

def distance(p1, p2):
    return math.sqrt(distance_sq(p1, p2))

def distance_sq(p1, p2):
    return math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2)

def distance_to_segment_sq(p, v, w):
    l2 = distance_sq(v, w)
    if l2 == 0:
        return distance_sq(p, v)
    t = ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2
    t = max(0, min(1, t))
    return distance_sq(p, lerp(v, w, t))

def lerp(a, b, t):
    return [
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
    ]

def flatness(points, offset):
    p1 = points[offset + 0]
    p2 = points[offset + 1]
    p3 = points[offset + 2]
    p4 = points[offset + 3]

    ux = 3 * p2[0] - 2 * p1[0] - p4[0]
    ux *= ux
    uy = 3 * p2[1] - 2 * p1[1] - p4[1]
    uy *= uy
    vx = 3 * p3[0] - 2 * p4[0] - p1[0]
    vx *= vx
    vy = 3 * p3[1] - 2 * p4[1] - p1[1]
    vy *= vy

    if ux < vx:
        ux = vx
    if uy < vy:
        uy = vy

    return ux + uy


def get_points_on_bezier_curve_with_splitting(points, offset, tolerance, new_points=None):
    out_points = [] if new_points is None else new_points
    if flatness(points, offset) < tolerance:
        p0 = points[offset + 0]
        if len(out_points):
            d = distance(out_points[len(out_points) - 1], p0)
            if d > 1:
                out_points.append(p0)
        else:
            out_points.append(p0)
        out_points.append(points[offset + 3])
    else:
        # subdivide
        t = .5
        p1 = points[offset + 0]
        p2 = points[offset + 1]
        p3 = points[offset + 2]
        p4 = points[offset + 3]

        q1 = lerp(p1, p2, t)
        q2 = lerp(p2, p3, t)
        q3 = lerp(p3, p4, t)

        r1 = lerp(q1, q2, t)
        r2 = lerp(q2, q3, t)

        red = lerp(r1, r2, t)

        out_points = get_points_on_bezier_curve_with_splitting([p1, q1, r1, red], 0, tolerance, out_points)
        out_points = get_points_on_bezier_curve_with_splitting([red, r2, q3, p4], 0, tolerance, out_points)
    return out_points


# Ramer–Douglas–Peucker algorithm
# https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2
def simplify_points(points, start, end, epsilon, new_points=None):
    out_points = [] if new_points is None else new_points

    # find the most distance point from the endpoints
    s = points[start]
    e = points[end - 1]
    max_dist_sq = 0
    max_ndx = 1
    for i in range(start + 1, end - 1):
        dist_sq = distance_to_segment_sq(points[i], s, e)
        if dist_sq > max_dist_sq:
            max_dist_sq = dist_sq
            max_ndx = i

    # if that point is too far, split
    if math.sqrt(max_dist_sq) > epsilon:
        out_points = simplify_points(points, start, max_ndx + 1, epsilon, out_points)
        out_points = simplify_points(points, max_ndx, end, epsilon, out_points)
    else:
        if not out_points:
            out_points.append(s)
        out_points.append(e)

    return out_points


def simplify(points, distance):
    return simplify_points(points, 0, len(points), distance)


def points_on_bezier_curves(points, tolerance=0.15, distance=None):
    new_points = []
    num_segments = (len(points) - 1) // 3
    for i in range(num_segments):
        offset = i * 3
        new_points = get_points_on_bezier_curve_with_splitting(points, offset, tolerance, new_points)
    if distance and distance > 0:
        return simplify_points(new_points, 0, len(new_points), distance)
    return new_points
