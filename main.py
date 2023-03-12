import logging
import inkex

from lxml import etree
from roughpy.core import Options
from roughpy.generator import NOS
from roughpy.svg import RoughSVG


class RoughPy(inkex.EffectExtension):
    def __init__(self):
        super().__init__()
        self.rough = None

    def add_arguments(self, pars):
        pars.add_argument('--contour', type=bool, default=False, help='Rough the shape itself')
        pars.add_argument('--fill_style', type=str, default='hachure', help='Fill Style')
        pars.add_argument('--roughness', type=float, default=1.0, help='Roughness')
        pars.add_argument('--hachure_angle', type=int, default=-45, help='Hachure Angle')
        pars.add_argument('--hachure_gap', type=float, default=-1, help='Hachure Gap')
        pars.add_argument('--disable_multi_stroke', type=bool, default=False, help='Disable multi-stroke')
        pars.add_argument('--disable_multi_stroke_fill', type=bool, default=False, help='Disable multi-stroke fill')

    def effect(self):
        if not self.rough:
            self.rough = RoughSVG(self.document.getroot())
        if self.options.ids:
            # Traverse the selected objects
            for id_ in self.options.ids:
                self.recursively_traverse_svg([self.svg.selected[id_]])
        else:
            # Traverse the entire document
            self.recursively_traverse_svg(self.document.getroot())

    def recursively_traverse_svg(self, a_node_list):
        for node in a_node_list:
            if node.tag in [inkex.addNS('g', 'svg'), 'g']:
                self.recursively_traverse_svg(node)

            elif node.tag in [
                inkex.addNS('path', 'svg'), 'path',
                inkex.addNS('rect', 'svg'), 'rect', 
                inkex.addNS('line', 'svg'), 'line', 
                inkex.addNS('polyline', 'svg'), 'polyline', 
                inkex.addNS('polygon', 'svg'), 'polygon', 
                inkex.addNS('ellipse', 'svg'), 'ellipse',
                inkex.addNS('circle', 'svg'), 'circle']:
                self.make_hatch(node)
            elif node.tag in [inkex.addNS('use', 'svg'), 'use']:
                #inkex.errormsg('Warning: unable to hatch object <{0}>, please unlink any clones first.'.format(node.get_id()))
                pass
            elif node.tag in [inkex.addNS('text', 'svg'), 'text']:
                #inkex.errormsg('Warning: unable to draw text, please convert it to a path first.')
                pass
            else:
                #inkex.errormsg('Warning: unable to hatch object <{0}>, please convert it to a path first.'.format(node.get_id()))
                pass

    def make_hatch(self, node):
        color, width = self.get_color_and_width(node)
        hatch = self.rough.path(str(node.path), Options(
            roughness=self.options.roughness,
            stroke=NOS if not self.options.contour else color,
            stroke_width=width,
            fill=color,
            fill_style=self.options.fill_style,
            fill_weight=width / 2,
            hachure_angle=self.options.hachure_angle,
            hachure_gap=self.options.hachure_gap,
            disable_multi_stroke=self.options.disable_multi_stroke,
            disable_multi_stroke_fill=self.options.disable_multi_stroke_fill,
        ))
        if len(hatch) == 0 and not hatch.attrib['d']:
            inkex.errormsg(f'unable to fill the path for {node}')
            return
        parent = node.getparent()
        if parent is None:
            parent = self.document.getroot()
        g = etree.SubElement(parent, inkex.addNS('g', 'svg'))
        if self.options.contour:
            parent.remove(node)
        else:
            g.append(node)
        g.append(hatch)

    def get_color_and_width(self, node):
        stroke_color = '#000000'
        stroke_width = 1.0
        try:
            style = node.get('style')
            if style is not None:
                declarations = style.split(';')
                for i, declaration in enumerate(declarations):
                    parts = declaration.split(':', 2)
                    if len(parts) == 2:
                        (prop, val) = parts
                        prop = prop.strip().lower()
                        if prop == 'stroke-width':
                            stroke_width = float(val.strip())
                        elif prop == 'stroke':
                            val = val.strip()
                            stroke_color = val
        finally:
            return stroke_color, stroke_width


if __name__ == '__main__':
    input_file = 'rect1.svg'
    output_file = 'rect2.svg'
    RoughPy().run()#[input_file, '--output=' + output_file])
