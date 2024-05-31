# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def test_qrcoderect_render():
    c = canvas.Canvas(
        "./tests/testfiles/test_qrcoderect.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    style_dict = {
        "top-margin": 0.05 * inch,
        "bottom-margin": 0.1 * inch,
        "left-margin": 0.1 * inch,
        "right-margin": 0.05 * inch,
        "horz-align": "centre",
        "vert-align": "centre",
    }

    qr = QRCodeRect(2 * inch, 2 * inch, qrtext="https://www.apple.com")
    qr.show_debug_rects = True
    qr.style.set_with_dict(style_dict)
    qr.fill_colour = "#2040FF"
    qr.top_left = 1 * inch, 10 * inch
    assert qr.image_shape == (528, 528)
    qr.rotation = 30
    qr.draw_in_canvas(c)

    qr = QRCodeRect(
        "This is a large selection of text 0123456789 This is more text ABCDEFGHIJKLMOPQRSTUVWXYZ 0123456789"
    )
    qr.format = "png"
    qr.fill_colour = "#FF4040"
    qr.rect.set_size(2 * inch, 3 * inch)
    qr.show_debug_rects = True
    qr.style.set_with_dict(style_dict)
    qr.top_left = 3 * inch, 7 * inch
    assert qr.image_shape == (539, 539)
    qr.rotation = -15
    qr.draw_in_canvas(c)

    qr = QRCodeRect(
        "This is a large selection of text 0123456789 This is more text ABCDEFGHIJKLMOPQRSTUVWXYZ 0123456789"
    )
    qr.rect.set_size(3 * inch, 2 * inch)
    qr.show_debug_rects = True
    qr.style.set_with_dict(style_dict)
    qr.top_left = 1 * inch, 3 * inch
    qr.draw_in_canvas(c)

    qr = QRCodeRect()
    qr.rect.set_size(1 * inch, 1 * inch)
    qr.show_debug_rects = True
    qr.style.set_with_dict(style_dict)
    qr.top_left = 4 * inch, 3 * inch
    qr.draw_in_canvas(c)

    c.showPage()
    c.save()
