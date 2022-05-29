import inkex
from inkex import Circle, Ellipse, Polygon, Line, Rectangle, Path, PathElement
from random import randint
from PIL import ImageGrab

class ExtendedHatchFill(inkex.EffectExtension):
    """Drawing a simple bezizer"""

    def add_arguments(self, pars):
        pars.add_argument("--even_color", type=inkex.Color, default=inkex.Color("blue"))

    def effect(self):
        s = self.svg
        ds = 30
        pic = ImageGrab.grab()
        #hatching bezier selected rectangular objects
        for elem in self.svg.selection:
            b = elem.bounding_box()
            dxx = b.left # object offsets for bitmap hatching
            dyy = b.top
            for y in range(int(b.top + ds/2), int(b.top + b.height- ds/2), int(ds / 2)):
                for x in range(int(b.left), int(b.left + b.width - ds / 2 ), ds):
                    dy = randint(10,30)
                    dx = randint(30,50)
                    a = [['M', [x, y]],
                        ['Q', [x + dx, y + dy, x + 40, y]],
                        ['T', [x + 40, y]]]

                    # below is code for bitmap hatching objects (in the example by red)
                    # without debugger I can't understand why it gives me an error
                    # The error is shown at line 23 (for ...)

                    # r, g, b = pic.getpixel((int(x), int(y)))
                    # if r == 255 and g == 0 and b == 0:
                    #     hatch = Ellipse(cx=f'{x - dxx}', cy=f'{y - dyy}', rx=f'{10}', ry=f'{10}')
                    #     hatch.set_id(f'hatch' + '{x}' + '{y}')
                    #     hatch.style = { "fill": "green", "stroke": "black" }
                    #     s.add(hatch)

                    bz = PathElement.new(a)
                    bz.style = { "fill": "none", "stroke": "black"}
                    s.add(bz)

if __name__ == '__main__':
    ExtendedHatchFill().run()
