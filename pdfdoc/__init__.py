"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

__project__ = 'pdfdoc'
__version__ = '0.5.0'

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

DEF_FONT_NAME = "DroidSans"
DEF_FONT_SIZE = 15
AUTO_SIZE = 0

from pdfdoc.pdfdoc import (
    GetImageMetrics,
    GetStringMetrics,
    GetStringAscDes,
    GetImageMetrics,
    TrimStringToFit,
    SplitStringToFit,
    TrimStringWithFunction,
    rl_colour,
    rl_colour_trans,
    fasymbol,
    hazsymbol,
    set_icon,
)
from .docstyle import DocStyle
from .contentrect import ContentRect
from .textrect import TextRect
from .imgrect import ImageRect
from .patternrect import PatternRect
from .tablecell import TableCell, TableVector
from .tablerow import TableRow
from .tablecolumn import TableColumn
from .labeldoc import LabelDoc
from .labelstyles import *
from .genericlabel import GenericLabel
from .safetylabel import SafetyLabel

