# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import StyledLine, IN2PTS
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm


def test_line():
    c = canvas.Canvas(
        "./tests/testfiles/test_line.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    style = {
        "line-width": 0.5 * mm,
        "line-colour": "#FF0040",
    }
    line = StyledLine(style=style)
    line.draw_in_canvas(c, *IN2PTS((1, 1, 4, 4)))
    line.draw_in_canvas(c, *IN2PTS((1, 9, 5, 9)))

    pts = IN2PTS((3, 1, 7, 3))
    StyledLine.draw_dim_line(
        c,
        *pts,
        "24 mm",
        line_width=0.65 * mm,
        style={
            "font": "DIN-Medium",
            "font-size": 10,
            "line-colour": "#595959",
        },
    )

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
    pts = IN2PTS((7, 7, 0.5, 7))
    arc.draw_line(c, *pts, style=style)

    style = {
        "line-width": 1.5 * mm,
        "line-colour": "#404040",
        "line-dash": [6, 8, 6, 0],
    }
    pts = IN2PTS((7, 7.5, 1.5, 7.5))
    StyledLine.draw_line(c, *pts, style=style)

    bl = StyledLine()
    bl.line_width = 8 * mm
    bl.line_colour = "#000000"
    bl.arrow.length = 3 * mm
    bl.arrow.style["arrow-style"] = "cap"
    bl.use_default_arrow_style = False
    bl.draw_in_canvas(c, *IN2PTS((5.5, 8, 5.5, 10.5)), False, True)
    bl.style["line-dash"] = [1.5 * mm, 1.5 * mm, 1.5 * mm, 0]
    bl.draw_in_canvas(c, *IN2PTS((5.5, 8.8, 7, 10)), False, True)
    c.showPage()
    c.save()


def test_polyline():
    c = canvas.Canvas(
        "./tests/testfiles/test_polyline.pdf",
        pagesize=(8.5 * inch, 11.0 * inch),
    )
    style = {
        "line-width": 0.2 * mm,
        "line-colour": "#505050",
        "grid-dash": [1, 2, 1, 0],
    }
    pl = StyledLine(style=style)
    coords = IN2PTS([(1, 10), (5, 9), (5, 3), (1.5, 3)])
    pl.draw_from_coords(c, coords)
    coords = IN2PTS([(2, 9), (6, 8), (6, 2), (2.5, 2)])
    pl.line_colour = "#202070"
    pl.line_width = 1 * mm
    pl.draw_from_coords(c, coords, arrow0=True, arrow1=True)

    pl.line_colour = "#FF9090"
    pl.line_width = 0.2 * mm
    pl.draw_from_coords(c, coords)

    coords = IN2PTS([(2.5, 9.5), (6.5, 8.5), (1, 4), (6.5, 7)])
    pl.line_colour = "#CF2020"
    pl.line_width = 0.5 * mm
    pl.arrow.length = 4 * mm
    pl.arrow.width = 5 * mm
    pl.arrow.style["arrow-style"] = "flat"
    pl.arrow.line_colour = "#CF2020"
    pl.use_default_arrow_style = False
    pl.draw_from_coords(c, coords, arrow0=True, arrow1=True)

    coords = IN2PTS([(3.5, 10.5), (7.5, 9.5), (2, 5), (7.5, 8)])
    pl.line_colour = "#20CF20"
    pl.line_width = 0.65 * mm
    pl.arrow.length = 6 * mm
    pl.arrow.width = 4 * mm
    pl.arrow.style["arrow-style"] = "dimension"
    pl.arrow.line_colour = "#20CF20"
    pl.arrow.line_width = pl.line_width
    pl.use_default_arrow_style = False
    pl.draw_from_coords(c, coords, arrow0=True, arrow1=True)

    c.showPage()
    c.save()


def test_grid():
    c = canvas.Canvas(
        "./tests/testfiles/test_grid.pdf",
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
