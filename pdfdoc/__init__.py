"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

# fmt: off
__project__ = 'pdfdoc'
__version__ = '0.9.7'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

DEF_FONT_NAME = "DroidSans"
DEF_FONT_SIZE = 15
AUTO_SIZE = 0
CONTENT_SIZE = -1

FONT_PATHS = ["/System/Library/Fonts/", "~/Library/Fonts/"]
REGISTERED_FONTS = {}

from .helpers import (
    get_string_metrics,
    get_string_asc_des,
    get_image_metrics,
    does_string_fit,
    scale_string_to_fit,
    trim_string_to_fit,
    split_string_to_fit,
    trim_string_function,
    rl_colour,
    rl_colour_trans,
    rl_colour_hex,
    rl_set_border_stroke,
    rl_draw_rect,
    clamp_cmyk,
    canvas_save_state,
    canvas_restore_state,
    MM2PTS,
    IN2PTS,
    PTS2IN,
    PTS2MM,
    PIX2PTS,
    PTS2PIX,
    get_edge_colours,
    is_rect_in_transparent_region,
    modify_pdf_file,
)
from .fonthelpers import (
    register_font_family,
    register_font,
    get_registered_fonts,
    fa_symbol,
    haz_symbol,
    set_icon,
    get_system_font_list,
    print_system_fonts,
    find_font,
    create_specimen_pdf,
    create_font_family_pdf,
    print_symbol_list,
)
from .style.docstyle import DocStyle, DocStyleSheet, DocStyleMixin, roman_number
from .style.pagestyles import *
from .style.labelstyles import *
from .contentrect.contentrect import ContentRect, FixedRect
from .contentrect.textrect import TextRect
from .contentrect.imgrect import ImageRect
from .contentrect.patternrect import PatternRect
from .contentrect.svgrect import SvgRect
from .contentrect.alignmentrect import AlignmentRect
from .tablecell.tablecell import TableCell
from .tablecell.tablevector import TableVector
from .tablecell.tablegrid import TableGrid
from .tablecell.layoutcell import LayoutCell
from .tablecell.tablerow import TableRow
from .tablecell.tablecolumn import TableColumn
from .document.document import Document
from .document.doccallbacks import *
from .labeldoc.labeldoc import LabelDoc
from .labeldoc.genericlabel import GenericLabel
from .labeldoc.safetylabel import SafetyLabel
from .labeldoc.mechlabel import MechanicalLabel
from .labeldoc.eleclabel import ElectronicLabel
from .labeldoc.simplelabel import SimpleLabel, PlainTextLabel
from .graphics.arrowhead import ArrowHead
from .graphics.cmykgrid import CMYKGrid
from .graphics.line import StyledLine

_font_dict = {
    "DroidSans": "DroidSans.ttf",
    "DroidSans-Bold": "DroidSans-Bold.ttf",
    "DIN-Light": "DIN-Light.ttf",
    "DIN-Medium": "DIN-Medium.ttf",
    "DIN-Regular": "DIN-Regular.ttf",
    "DIN-Bold": "DIN-Bold.ttf",
    "IKEA-Sans-Regular": "IKEA-Sans-Regular.ttf",
    "IKEA-Sans-Heavy": "IKEA-Sans-Heavy.ttf",
    "IKEA-Sans-Regular": "IKEA-Sans-Regular.ttf",
    "IKEA-Sans-Heavy": "IKEA-Sans-Heavy.ttf",
    "IKEA-Sans-Bold-Italic": "IKEA-Sans-Bold-Italic.ttf",
    "British-Rail-Light": "britrln_.ttf",
    "British-Rail-Dark": "britrdn_.ttf",
    "FontAwesome": "fontawesome-webfont.ttf",
    "Hazard": "haw_____.ttf",
    "Zapf Dingbats": "ZapfDingbats.ttf",
    "Transport-Medium": "Transport Medium.ttf",
    "Transport-Heavy": "Transport Heavy.ttf",
}

for k, v in _font_dict.items():
    reg_font, font_file = register_font(k, v)
    if reg_font is not None:
        REGISTERED_FONTS[reg_font] = font_file

_font_families = ["Avenir Next Condensed"]

for f in _font_families:
    _valid_fonts = register_font_family(f)
    if len(_valid_fonts) == 0:
        print("Cannot register font family %s" % (f))
