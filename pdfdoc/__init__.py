"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

__project__ = 'pdfdoc'
__version__ = '0.5.0'

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

DEF_FONT_NAME = "DroidSans"
DEF_FONT_SIZE = 15
AUTO_SIZE = 0
CONTENT_SIZE = -1

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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
from .tablegrid import TableGrid
from .layoutcell import LayoutCell
from .tablerow import TableRow
from .tablecolumn import TableColumn
from .labeldoc import LabelDoc
from .labelstyles import *
from .genericlabel import GenericLabel
from .safetylabel import SafetyLabel
from .mechlabel import MechanicalLabel
from .eleclabel import ElectronicLabel

try:
    pdfmetrics.registerFont(TTFont("DroidSans", "DroidSans.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("DroidSans-Bold", "DroidSans-Bold.ttf"))
except:
    pass
pdfmetrics.registerFont(TTFont("DIN-Medium", "DIN-Medium.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Regular", "DIN-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Bold", "DIN-Bold.ttf"))
# pdfmetrics.registerFont(TTFont("FontAwesome", "fontawesome-webfont.ttf"))

try:
    pdfmetrics.registerFont(TTFont("IKEA-Sans-Regular", "IKEA-Sans-Regular.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("IKEA-Sans-Heavy", "IKEA-Sans-Heavy.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("British-Rail-Light", "britrln_.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("British-Rail-Dark", "britrdn_.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("FontAwesome", "fontawesome-webfont.ttf"))
except:
    pass
try:
    pdfmetrics.registerFont(TTFont("Hazard", "haw_____.ttf"))
except:
    print("Cannot load hazard font")
try:
    pdfmetrics.registerFont(TTFont("Zapf Dingbats", "ZapfDingbats.ttf"))
except:
    print("Cannot load dingbats font")
