# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import StyledLine
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm


def test_line():
    c = canvas.Canvas(
        "./testfiles/test_line.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    style = {
        "line-width": 0.5 * mm,
        "line-colour": "#FF0040",
    }
    line = StyledLine(style=style)
    line.draw_in_canvas(c, 1 * inch, 1 * inch, 4 * inch, 4 * inch)
    line.draw_in_canvas(c, 1 * inch, 9 * inch, 5 * inch, 9 * inch)

    style = {
        "line-width": 0.8 * mm,
        "line-colour": "#20C040",
    }
    arc = StyledLine(style=style)
    arc.draw_arc(c, 2 * inch, 5 * inch, 1 * inch, 45, 120, style=style)

    style = {
        "line-width": 0.8 * mm,
        "line-colour": "#2040C0",
        "line-dash": [4, 8, 4, 0],
    }
    arc = StyledLine(style=style)
    arc.draw_line(c, 7 * inch, 7 * inch, 0.5 * inch, 7 * inch, style=style)

    style = {
        "line-width": 1.5 * mm,
        "line-colour": "#404040",
        "line-dash": [6, 8, 6, 0],
    }
    StyledLine.draw_line(c, 7 * inch, 7.5 * inch, 1.5 * inch, 7.5 * inch, style=style)
    c.showPage()
    c.save()


def test_grid():
    c = canvas.Canvas(
        "./testfiles/test_grid.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    style = {
        "grid-line-width": 0.25 * mm,
        "grid-line-colour": "#400040",
        "grid-dash": [1, 2, 1, 0],
    }
    line = StyledLine(style=style)
    line.draw_grid(
        c, 0.5 * inch, 0.5 * inch, 0.5 * inch, 0.5 * inch, 10, 10, style=style
    )
    c.showPage()
    c.save()
