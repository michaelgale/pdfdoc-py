#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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

import os, os.path
import string

from PIL import Image
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

from toolbox import *
from pdfdoc import *


def rl_colour(fromColour):
    if isinstance(fromColour, Color):
        return fromColour
    if isinstance(fromColour, (list, tuple)):
        return Color(fromColour[0], fromColour[1], fromColour[2], alpha=1.0)
    return None


def rl_colour_trans():
    return Color(1, 1, 1, alpha=0.0)


def rl_colour_hex(hexstr, alpha=1.0):
    if len(hexstr) < 6:
        return 0, 0, 0
    hs = hexstr.lstrip("#")
    if not all(c in string.hexdigits for c in hs):
        return 0, 0, 0
    [rd, gd, bd] = tuple(int(hs[i : i + 2], 16) for i in (0, 2, 4))
    r = float(rd) / 255.0
    g = float(gd) / 255.0
    b = float(bd) / 255.0
    return Color(r, g, b, alpha=alpha)


def GetStringMetrics(c, label, fontname, fontsize, with_descent=True):
    # print("fontname: %s fontsize: %s" % (fontname, fontsize))
    if fontsize is None or fontname is None:
        return (0, 0)
    if fontsize == 0 or fontname == "":
        return (0, 0)
    try:
        face = pdfmetrics.getFont(fontname).face
        fontname_ = fontname
    except:
        face = pdfmetrics.getFont(DEF_FONT_NAME).face
        fontname_ = DEF_FONT_NAME
    # print(face.ascent, face.descent)
    ascent, descent = (face.ascent / 1000.0), abs(face.descent / 1000.0)
    height = ascent - descent if with_descent else ascent

    height *= fontsize
    width = c.stringWidth(label, fontname_, fontsize)
    return (width, height)


def GetStringAscDes(c, label, fontname, fontsize):
    # print("fontname: %s fontsize: %s" % (fontname, fontsize))
    if fontsize is None or fontname is None:
        return (0, 0)
    if fontsize == 0 or fontname == "":
        return (0, 0)
    try:
        face = pdfmetrics.getFont(fontname).face
        fontname_ = fontname
    except:
        face = pdfmetrics.getFont(DEF_FONT_NAME).face
        fontname_ = DEF_FONT_NAME
    # print(face.ascent, face.descent)
    ascent, descent = (face.ascent / 1000.0), abs(face.descent / 1000.0)
    return (ascent * fontsize, descent * fontsize)


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


def SplitStringToFit(canvas, s, fontname, fontsize, toWidth):
    words = s.split()
    lines = []
    line = []
    line_sum = 0
    for word in words:
        sw = canvas.stringWidth(word, fontname, fontsize)
        if "`" in word:
            w = word.replace("`", "")
            line.append(w)
            lines.append(" ".join(line))
            line_sum = 0
            line = []
        elif line_sum + sw < toWidth:
            line_sum += sw
            line.append(word)
        else:
            lines.append(" ".join(line))
            line_sum = sw
            line = [word]
    lines.append(" ".join(line))
    return lines


def TrimStringWithFunction(canvas, s, fontname, fontsize, toWidth, func):
    try:
        sw = canvas.stringWidth(s, fontname, fontsize)
        fontname_ = fontname
    except:
        sw = canvas.stringWidth(s, DEF_FONT_NAME, fontsize)
        fontname_ = DEF_FONT_NAME

    level = 0
    sn = s
    while sw > toWidth and level < 8:
        sn = func(sn, level)
        sw = canvas.stringWidth(sn, fontname_, fontsize)
        # print("level: %d w=%.0f sw=%.0f s=%s sn=%s" % (level, toWidth, sw, s, sn))
        level += 1
    while sw > toWidth:
        sn = sn[:-1]
        sw = canvas.stringWidth(sn, fontname_, fontsize)
    return sn


def PTS2MM(pts):
    return pts / 72 * 25.4


def PTS2IN(pts):
    return pts / 72


def IN2PTS(inch):
    return inch * 72


def MM2PTS(mm):
    return mm / 25.4 * 72
