from turtle import radians
import inkex
from inkex import Circle, Ellipse, Polygon, Line, Rectangle, Path, PathElement
from random import randint
from PIL import ImageGrab

class ExtendedHatchFill(inkex.EffectExtension):
    """Drawing a simple bezizer"""

# Getting values from the interface

    def add_arguments(self, pars):
        pars.add_argument("--radio_type_hatch", dest="fill_type", default="hatch_wavy")
        pars.add_argument("--size_hatch", type=int, default=10)


    def effect(self):
        s = self.svg
        ds = 30
        pic = ImageGrab.grab()
        #hatching bezier selected rectangular objects
        for elem in self.svg.selection:
            if self.options.fill_type == "Cross": # How do I get the fill_type value from the add_arguments method here ?
                elem.style = { "fill": "green", "stroke": "black" }
                # elem.style['fill'] = "green"
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
