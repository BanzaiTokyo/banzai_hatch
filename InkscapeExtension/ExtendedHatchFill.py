import inkex
from inkex import Circle, Ellipse, Polygon, Line, Rectangle, bezier


class ExtendedHatchFill(inkex.EffectExtension):
    """EffectExtension to fill selected objects red"""

    def add_arguments(self, pars):
        pars.add_argument("--even_color", type=inkex.Color, default=inkex.Color("blue"))

    def effect(self):
        s = self.svg
        for elem in self.svg.selection:
            b = elem.bounding_box()
            rx, ry = 5, 5
            if elem is Rectangle:
                pass
            if elem is Circle:
                pass
            if elem is bezier:
                pass
            for y in range(int(b.top) + ry, int(b.top + b.height), ry):
                for x in range(int(b.left) + rx, int(b.left + b.width), rx):
                    hatch = Ellipse(cx=f"{x}", cy=f"{y}", rx=f"{rx}", ry=f"{ry}")
                    hatch.set_id("hatch" + "{x}" + "{y}")
                    hatch.style = {"fill": "none", "stroke": "black"}
                    s.add(hatch)


if __name__ == "__main__":
    ExtendedHatchFill().run()
