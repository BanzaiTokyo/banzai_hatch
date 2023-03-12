from .hachure_filler import HachureFiller
from .zigzag_filler import ZigZagFiller
from .hatch_filler import HatchFiller
from .dot_filler import DotFiller
from .dashed_filler import DashedFiller
from .zigzag_line_filler import ZigZagLineFiller

fillers = {}


def get_filler(o, helper):
    filler_name = o.fill_style
    if filler_name not in fillers:
        if filler_name == 'zigzag':
            fillers[filler_name] = ZigZagFiller(helper)
        elif filler_name == 'cross-hatch':
            fillers[filler_name] = HatchFiller(helper)
        elif filler_name == 'dots':
            fillers[filler_name] = DotFiller(helper)
        elif filler_name == 'dashed':
            fillers[filler_name] = DashedFiller(helper)
        elif filler_name == 'zigzag-line':
            fillers[filler_name] = ZigZagLineFiller(helper)
        else:
            filler_name = 'hachure'
            fillers[filler_name] = HachureFiller(helper)
    return fillers[filler_name]
