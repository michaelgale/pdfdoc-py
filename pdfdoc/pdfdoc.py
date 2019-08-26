#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# PDF document utilities

from PIL import Image
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

pdfmetrics.registerFont(TTFont("DroidSans", "DroidSans.ttf"))
pdfmetrics.registerFont(TTFont("DroidSans-Bold", "DroidSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Medium", "DIN-Medium.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Regular", "DIN-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Bold", "DIN-Bold.ttf"))
pdfmetrics.registerFont(TTFont("IKEA-Sans-Regular", "IKEA-Sans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("IKEA-Sans-Heavy", "IKEA-Sans-Heavy.ttf"))
pdfmetrics.registerFont(TTFont("British-Rail-Light", "britrln_.ttf"))

from fxgeometry import Rect

DEF_FONT_NAME = "DroidSans"
DEF_FONT_SIZE = 15


def register_font(font_name, font_filename):
    pdfmetrics.registerFont(TTFont(font_name, font_filename))


def rl_colour(fromColour):
    return Color(fromColour[0], fromColour[1], fromColour[2], alpha=1.0)


def rl_colour_trans():
    return Color(1, 1, 1, alpha=0.0)


def GetStringMetrics(c, label, fontname, fontsize):
    # print("fontname: %s fontsize: %s" % (fontname, fontsize))
    if fontsize is None or fontname is None:
        return (0, 0)
    if fontsize == 0 or fontname == "":
        return (0, 0)
    face = pdfmetrics.getFont(fontname).face
    ascent, descent = (face.ascent / 1000.0), abs(face.descent / 1000.0)
    height = ascent - descent  # + descent
    height *= fontsize
    width = c.stringWidth(label, fontname, fontsize)
    return (width, height)


def GetImageMetrics(filename):
    img_file = Path(filename)
    if img_file.is_file():
        im = Image.open(filename)
        width, height = im.size
        im.close()
        return width, height
    return (0, 0)


def TrimStringToFit(canvas, s, fontname, fontsize, toWidth):
    sn = s
    sw = canvas.stringWidth(sn, fontname, fontsize)
    while sw > toWidth:
        sn = sn[:-1]
        sw = canvas.stringWidth(sn, fontname, fontsize)
    return sn

def TrimStringWithFunction(canvas, s, fontname, fontsize, toWidth, func):
    sw = canvas.stringWidth(s, fontname, fontsize)
    level = 0
    sn = s
    while sw > toWidth and level < 8:
        sn = func(sn, level)
        sw = canvas.stringWidth(sn, fontname, fontsize)
        # print("level: %d w=%.0f sw=%.0f s=%s sn=%s" % (level, toWidth, sw, s, sn))
        level += 1
    while sw > toWidth:
        sn = sn[:-1]
        sw = canvas.stringWidth(sn, fontname, fontsize)
    return sn
