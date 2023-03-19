from typing import List, Union

from .geometry import Point


class Config:
    def __init__(self, options: dict = None):
        self.options = options or {}


class Options:
    def __init__(self, max_randomness_offset: float = None, roughness: float = None, bowing: float = None,
                 stroke: str = None, stroke_width: float = None, curve_fitting: float = None,
                 curve_tightness: float = None, curve_step_count: int = None, fill: str = None,
                 fill_style: str = None, fill_weight: float = None, hachure_angle: float = None,
                 hachure_gap: float = None, simplification: float = None, dash_offset: float = None,
                 dash_gap: float = None, zigzag_offset: float = None, seed: int = None,
                 stroke_line_dash: List[float] = None, stroke_line_dash_offset: float = None,
                 fill_line_dash: List[float] = None, fill_line_dash_offset: float = None,
                 disable_multi_stroke: bool = None, disable_multi_stroke_fill: bool = None,
                 preserve_vertices: bool = None, fixed_decimal_place_digits: int = None):
        self.max_randomness_offset = max_randomness_offset
        self.roughness = roughness
        self.bowing = bowing
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.curve_fitting = curve_fitting
        self.curve_tightness = curve_tightness
        self.curve_step_count = curve_step_count
        self.fill = fill
        self.fill_style = fill_style
        self.fill_weight = fill_weight
        self.hachure_angle = hachure_angle
        self.hachure_gap = hachure_gap
        self.simplification = simplification
        self.dash_offset = dash_offset
        self.dash_gap = dash_gap
        self.zigzag_offset = zigzag_offset
        self.seed = seed
        self.stroke_line_dash = stroke_line_dash
        self.stroke_line_dash_offset = stroke_line_dash_offset
        self.fill_line_dash = fill_line_dash
        self.fill_line_dash_offset = fill_line_dash_offset
        self.disable_multi_stroke = disable_multi_stroke
        self.disable_multi_stroke_fill = disable_multi_stroke_fill
        self.preserve_vertices = preserve_vertices
        self.fixed_decimal_place_digits = fixed_decimal_place_digits
        self.randomizer = None


OpType = Union['move', 'bcurveTo', 'lineTo']
OpSetType = Union['path', 'fillPath', 'fillSketch']


class Op:
    def __init__(self, op: OpType, data: List[float]):
        self.op = op
        self.data = data


class OpSet:
    def __init__(self, type: OpSetType = None, ops: List[Op] = None, size: Point = None, path: str = None):
        self.type = type
        self.ops = ops or []
        self.size = size
        self.path = path


class Drawable:
    def __init__(self, shape: str, options: Options, sets: List[OpSet]):
        self.shape = shape
        self.options = options
        self.sets = sets


class PathInfo:
    def __init__(self, d: str, stroke: str, stroke_width: float, fill: str = None):
        self.d = d
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill = fill
