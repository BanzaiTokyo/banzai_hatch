#!/usr/bin/env python
# coding=utf-8

#
"""
This extension changes the fill of all selected elements to blue.
"""

import inkex


class ExtendedHatchFill(inkex.EffectExtension):
    """EffectExtension to fill selected objects red"""

        #pass # We don't need arguments for this extension
    # def add_arguments(self, pars):
    #     #self.msg(pars)
    #     pass

    # def add_arguments(self, pars):
    #     pars.add_argument("--my_option", type=inkex.Boolean,\
    #         help="An example option, put your options here")

    def add_arguments(self, pars):
        pars.add_argument("--even_color", type=inkex.Color, default=inkex.Color("blue"))



    # def effect(self):
    #     for elem in self.svg.selection:
    #         elem.style['fill'] = 'blue'
    #         elem.style['fill-opacity'] = 1
    #         elem.style['opacity'] = 1

    def effect(self):
        for elem in self.svg.selection:
            elem.style['fill'] = self.options.even_color
            elem.style['fill-opacity'] = 1
            elem.style['opacity'] = 1
            #width(3)
            # color("black", self.options.even_color)
            #begin_fill()
            #circle(150, 180)
            #circle(100, 180)

        # x,y,x2,y2 = 0,0,100,100
        # color = 'red'
        # return f'<circle cx="25" cy="75" r="20" stroke="red" fill="transparent" stroke-width="5"/>'
        # return f'<line x1="{x}" y1 = "{y}" x2 = "{x2}" y2 = "{y2}" stroke ="{color}" />'


if __name__ == '__main__':
    ExtendedHatchFill().run()
