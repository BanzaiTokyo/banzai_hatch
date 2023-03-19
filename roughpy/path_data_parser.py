import re
import math

COMMAND = 0
NUMBER = 1
EOD = 2

PARAMS = {
    'A': 7,
    'a': 7,
    'C': 6,
    'c': 6,
    'H': 1,
    'h': 1,
    'L': 2,
    'l': 2,
    'M': 2,
    'm': 2,
    'Q': 4,
    'q': 4,
    'S': 4,
    's': 4,
    'T': 2,
    't': 2,
    'V': 1,
    'v': 1,
    'Z': 0,
    'z': 0
}


def tokenize(d):
    tokens = []
    while d != '':
        if re.match(r'^([ \t\r\n,]+)', d):
            d = d[len(re.match(r'^([ \t\r\n,]+)', d).group(1)):]
        elif re.match(r'^([aAcChHlLmMqQsStTvVzZ])', d):
            tokens.append({'type': COMMAND, 'text': re.match(r'^([aAcChHlLmMqQsStTvVzZ])', d).group(1)})
            d = d[len(re.match(r'^([aAcChHlLmMqQsStTvVzZ])', d).group(1)):]
        elif re.match(r'^(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)', d):
            tokens.append({'type': NUMBER, 'text': str(float(re.match(r'^(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)', d).group(1)))})
            d = d[len(re.match(r'^(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)', d).group(1)):]
        else:
            return []
    tokens.append({'type': EOD, 'text': ''})
    return tokens


def is_type(token, type):
    return token['type'] == type


def parse_path(d):
    segments = []
    tokens = tokenize(d)
    mode = 'BOD'
    index = 0
    token = tokens[index]
    while not is_type(token, EOD):
        params_count = 0
        params = []
        if mode == 'BOD':
            if token['text'] == 'M' or token['text'] == 'm':
                index += 1
                params_count = PARAMS[token['text']]
                mode = token['text']
            else:
                return parse_path('M0,0' + d)
        elif is_type(token, NUMBER):
            params_count = PARAMS[mode]
        else:
            index += 1
            params_count = PARAMS[token['text']]
            mode = token['text']
        if (index + params_count) < len(tokens):
            for i in range(index, index + params_count):
                numbe_token = tokens[i]
                if is_type(numbe_token, NUMBER):
                    params.append(float(numbe_token['text']))
                else:
                    raise Exception('Param not a number: ' + mode + ',' + numbe_token['text'])
            if type(PARAMS[mode]) == int:
                segment = {'key': mode, 'data': params}
                segments.append(segment)
                index += params_count
                token = tokens[index]
                if mode == 'M':
                    mode = 'L'
                if mode == 'm':
                    mode = 'l'
            else:
                raise Exception('Bad segment: ' + mode)
        else:
            raise Exception('Path data ended short')
    return segments


def deg_to_rad(degrees):
    return (math.pi * degrees) / 180


def rotate(x, y, angle_rad):
    x1 = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    y1 = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return x1, y1


def arc_to_cubic_curves(x1, y1, x2, y2, r1, r2, angle, large_arc_flag, sweep_flag, recursive=None):
    angle_rad = deg_to_rad(angle)
    params = []

    if recursive:
        f1, f2, cx, cy = recursive
    else:
        x1, y1 = rotate(x1, y1, -angle_rad)
        x2, y2 = rotate(x2, y2, -angle_rad)

        x = (x1 - x2) / 2
        y = (y1 - y2) / 2
        h = (x * x) / (r1 * r1) + (y * y) / (r2 * r2)
        if h > 1:
            h = math.sqrt(h)
            r1 = h * r1
            r2 = h * r2

        sign = -1 if large_arc_flag == sweep_flag else 1

        r1_pow = r1 * r1
        r2_pow = r2 * r2

        left = r1_pow * r2_pow - r1_pow * y * y - r2_pow * x * x
        right = r1_pow * y * y + r2_pow * x * x

        k = sign * math.sqrt(abs(left / right))

        cx = k * r1 * y / r2 + (x1 + x2) / 2
        cy = k * -r2 * x / r1 + (y1 + y2) / 2

        f1 = math.asin(float(round((y1 - cy) / r2, 9)))
        f2 = math.asin(float(round((y2 - cy) / r2, 9)))

        if x1 < cx:
            f1 = math.pi - f1
        if x2 < cx:
            f2 = math.pi - f2

        if f1 < 0:
            f1 = math.pi * 2 + f1
        if f2 < 0:
            f2 = math.pi * 2 + f2

        if sweep_flag and f1 > f2:
            f1 = f1 - math.pi * 2
        if not sweep_flag and f2 > f1:
            f2 = f2 - math.pi * 2

    df = f2 - f1

    if abs(df) > (math.pi * 120 / 180):
        f2old = f2
        x2old = x2
        y2old = y2

        if sweep_flag and f2 > f1:
            f2 = f1 + (math.pi * 120 / 180)
        else:
            f2 = f1 - (math.pi * 120 / 180)
        x2 = cx + r1 * math.cos(f2)
        y2 = cy + r2 * math.sin(f2)
        params = arc_to_cubic_curves(x2, y2, x2old, y2old, r1, r2, angle, 0, sweep_flag, [f2, f2old, cx, cy])
    df = f2 - f1

    c1 = math.cos(f1)
    s1 = math.sin(f1)
    c2 = math.cos(f2)
    s2 = math.sin(f2)
    t = math.tan(df / 4)
    hx = 4 / 3 * r1 * t
    hy = 4 / 3 * r2 * t

    m1 = [x1, y1]
    m2 = [x1 + hx * s1, y1 - hy * c1]
    m3 = [x2 + hx * s2, y2 - hy * c2]
    m4 = [x2, y2]

    m2[0] = 2 * m1[0] - m2[0]
    m2[1] = 2 * m1[1] - m2[1]

    if recursive:
        return [m2, m3, m4] + params

    params = [m2, m3, m4] + params
    curves = []
    for i in range(0, len(params), 3):
        r1 = rotate(params[i][0], params[i][1], angle_rad)
        r2 = rotate(params[i + 1][0], params[i + 1][1], angle_rad)
        r3 = rotate(params[i + 2][0], params[i + 2][1], angle_rad)
        curves.append([r1[0], r1[1], r2[0], r2[1], r3[0], r3[1]])
    return curves


def normalize(segments):
    out = []

    last_type = ''
    cx = 0
    cy = 0
    subx = 0
    suby = 0
    lcx = 0
    lcy = 0

    for segment in segments:
        key = segment['key']
        data = segment['data']

        if key == 'M':
            out.append({'key': 'M', 'data': data[:]})
            cx, cy = data
            subx, suby = data
        elif key == 'C':
            out.append({'key': 'C', 'data': data[:]})
            cx = data[4]
            cy = data[5]
            lcx = data[2]
            lcy = data[3]
        elif key == 'L':
            out.append({'key': 'L', 'data': data[:]})
            cx, cy = data
        elif key == 'H':
            cx = data[0]
            out.append({'key': 'L', 'data': [cx, cy]})
        elif key == 'V':
            cy = data[0]
            out.append({'key': 'L', 'data': [cx, cy]})
        if key == 'S':
            cx1 = 0
            cy1 = 0
            if last_type == 'C' or last_type == 'S':
                cx1 = cx + (cx - lcx)
                cy1 = cy + (cy - lcy)
            else:
                cx1 = cx
                cy1 = cy
            out.append({'key': 'C', 'data': [cx1, cy1, *data]})
            lcx = data[0]
            lcy = data[1]
            cx = data[2]
            cy = data[3]
        elif key == 'T':
            x, y = data
            x1 = 0
            y1 = 0
            if last_type == 'Q' or last_type == 'T':
                x1 = cx + (cx - lcx)
                y1 = cy + (cy - lcy)
            else:
                x1 = cx
                y1 = cy
            cx1 = cx + 2 * (x1 - cx) / 3
            cy1 = cy + 2 * (y1 - cy) / 3
            cx2 = x + 2 * (x1 - x) / 3
            cy2 = y + 2 * (y1 - y) / 3
            out.append({'key': 'C', 'data': [cx1, cy1, cx2, cy2, x, y]})
            lcx = x1
            lcy = y1
            cx = x
            cy = y
        elif key == 'Q':
            x1, y1, x, y = data
            cx1 = cx + 2 * (x1 - cx) / 3
            cy1 = cy + 2 * (y1 - cy) / 3
            cx2 = x + 2 * (x1 - x) / 3
            cy2 = y + 2 * (y1 - y) / 3
            out.append({'key': 'C', 'data': [cx1, cy1, cx2, cy2, x, y]})
            lcx = x1
            lcy = y1
            cx = x
            cy = y
        elif key == 'A':
            r1 = abs(data[0])
            r2 = abs(data[1])
            angle = data[2]
            largeArcFlag = data[3]
            sweepFlag = data[4]
            x = data[5]
            y = data[6]
            if r1 == 0 or r2 == 0:
                out.append({'key': 'C', 'data': [cx, cy, x, y, x, y]})
                cx = x
                cy = y
            else:
                if cx != x or cy != y:
                    curves = arc_to_cubic_curves(cx, cy, x, y, r1, r2, angle, largeArcFlag, sweepFlag)
                    for curve in curves:
                        out.append({'key': 'C', 'data': curve})
                    cx = x
                    cy = y
        elif key == 'Z':
            out.append({'key': 'Z', 'data': []})
            cx = subx
            cy = suby
        last_type = key
    return out


def absolutize(segments):
    cx = 0
    cy = 0
    subx = 0
    suby = 0
    out = []
    for segment in segments:
        key = segment['key']
        data = segment['data']
        if key == 'M':
            out.append({'key': 'M', 'data': data})
            cx, cy = data
            subx, suby = data
        elif key == 'm':
            cx += data[0]
            cy += data[1]
            out.append({'key': 'M', 'data': [cx, cy]})
            subx = cx
            suby = cy
        elif key == 'L':
            out.append({'key': 'L', 'data': data})
            cx, cy = data
        elif key == 'l':
            cx += data[0]
            cy += data[1]
            out.append({'key': 'L', 'data': [cx, cy]})
        elif key == 'C':
            out.append({'key': 'C', 'data': data})
            cx = data[4]
            cy = data[5]
        elif key == 'c':
            newdata = [d + cx if i % 2 == 0 else d + cy for i, d in enumerate(data)]
            out.append({'key': 'C', 'data': newdata})
            cx = newdata[4]
            cy = newdata[5]
        elif key == 'Q':
            out.append({'key': 'Q', 'data': data})
            cx = data[2]
            cy = data[3]
        elif key == 'q':
            newdata = [d + cx if i % 2 == 0 else d + cy for i, d in enumerate(data)]
            out.append({'key': 'Q', 'data': newdata})
            cx = newdata[2]
            cy = newdata[3]
        elif key == 'A':
            out.append({'key': 'A', 'data': data})
            cx = data[5]
            cy = data[6]
        elif key == 'a':
            cx += data[5]
            cy += data[6]
            out.append({'key': 'A', 'data': [data[0], data[1], data[2], data[3], data[4], cx, cy]})
        elif key == 'H':
            out.append({'key': 'H', 'data': data})
            cx = data[0]
        elif key == 'h':
            cx += data[0]
            out.append({'key': 'H', 'data': [cx]})
        elif key == 'V':
            out.append({'key': 'V', 'data': data})
            cy = data[0]
        elif key == 'v':
            cy += data[0]
            out.append({'key': 'V', 'data': [cy]})
        elif key == 'S':
            out.append({'key': 'S', 'data': data})
            cx = data[2]
            cy = data[3]
        elif key == 's':
            newdata = [d + cx if i % 2 == 0 else d + cy for i, d in enumerate(data)]
            out.append({'key': 'S', 'data': newdata})
            cx = newdata[2]
            cy = newdata[3]
        elif key == 'T':
            out.append({'key': 'T', 'data': data})
            cx = data[0]
            cy = data[1]
        elif key == 't':
            cx += data[0]
            cy += data[1]
            out.append({'key': 'T', 'data': [cx, cy]})
        elif key == 'Z' or key == 'z':
            out.append({'key': 'Z', 'data': []})
            cx = subx
            cy = suby
    return out
