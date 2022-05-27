import inkex
from inkex import Rectangle, Transform
from inkex import Vector2d
from inkex import Circle, Ellipse, Polygon, Line, Rectangle, Path


class ExtendedHatchFill(inkex.EffectExtension):
    """EffectExtension to fill selected objects red"""

    def add_arguments(self, pars):
        pars.add_argument("--even_color", type=inkex.Color, default=inkex.Color("blue"))

    def effect(self):
        s = self.svg
        a = [['M ', [100, 100]],
             [' L ', [200, 300]],
             [' L ', [600, 300]],
             [' L ', [800, 550]],
             [' L ', [1000, 300]],
             [' Z', []], ]

        bz = Path(d=a)  # or  bz = Path(d = f'{a}')  or bz = Path(f'{a}')
        bz.style = {"fill": "none", "stroke": "#888888", "stroke-width": "2"}
        s.add(bz)

if __name__ == '__main__':
    ExtendedHatchFill().run()
