from .core import Config
from .svg import RoughSVG
from .generator import RoughGenerator


def svg(svg, config: Config=None) -> RoughSVG:
    return RoughSVG(svg, config)


def generator(config: Config=None) -> RoughGenerator:
    return RoughGenerator(config)


def new_seed() -> float:
    return RoughGenerator.new_seed()
