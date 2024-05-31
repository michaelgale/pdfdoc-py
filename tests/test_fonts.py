# Sample Test passing with nose and pytest

import crayons as cr

from toolbox import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pdfdoc import *
from pdfdoc.fonthelpers import stroke_width


def test_listfiles():
    # print_system_fonts()

    find_font("freesans")
    find_font("FuturaStd-Medium.otf")
    find_font("UKNumberPlate")
    find_font("uknumberplate")
    find_font("Transport Heavy")
    find_font("IKEA Sans Regular")
    find_font("IKEA-Sans-Regular")

    # all_fonts = get_registered_fonts()
    # for k, v in all_fonts.items():
    #     print(cr.white(k), cr.cyan(v))


def test_font_specimen():
    FONT_LIST = [
        "DIN-Regular",
        "DroidSans",
        "IKEA-Sans-Regular",
        "Hazard",
        "Transport-Medium",
        "Transport-Heavy",
        "British-Rail-Dark",
    ]
    for f in FONT_LIST:
        fn = f.replace(" ", "").replace("-", "").replace("_", "")
        create_specimen_pdf(f, "./tests/testfiles/test_specimen_%s.pdf" % (fn))


_font_dict = {
    "font-name": "Avenir-0",
    "font-size": 18,
    "horz-align": "left",
}


def test_register_font():
    valid_fonts = register_font_family("Avenir Next Condensed.ttc")
    c = canvas.Canvas(
        "./tests/testfiles/test_fontnames.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    c.saveState()
    for i, font in enumerate(valid_fonts):
        _font_dict["font-name"] = font
        t1 = TextRect(
            7 * inch, 0.5 * inch, "%s Font Specimen" % (font), style=_font_dict
        )
        t1.rect.move_top_left_to(Point(1 * inch, 10 * inch - i * 0.5 * inch))
        t1.draw_in_canvas(c)
    c.showPage()
    c.save()
