from typing import List, Tuple
import math

Point = Tuple[float, float]
Line = Tuple[Point, Point]


class Rectangle:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def rotate_points(points: List[Point], center: Point, degrees: float) -> None:
    if points:
        cx, cy = center
        angle = (math.pi / 180) * degrees
        cos = math.cos(angle)
        sin = math.sin(angle)
        for i, p in enumerate(points):
            x, y = p
            points[i] = (
                (x - cx) * cos - (y - cy) * sin + cx,
                (x - cx) * sin + (y - cy) * cos + cy
            )


def rotate_lines(lines: List[Line], center: Point, degrees: float) -> None:
    points = [point for line in lines for point in line]
    rotate_points(points, center, degrees)
    for i in range(len(lines)):
        lines[i] = (points[i*2], points[i*2+1])


def line_length(line: Line) -> float:
    p1, p2 = line
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
