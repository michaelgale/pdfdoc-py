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
import math
import string
from PIL import Image
from pathlib import Path
import fitz

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


def get_string_metrics(c, label, fontname, fontsize, with_descent=True):
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


def get_string_asc_des(c, label, fontname, fontsize):
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


def get_image_metrics(filename):
    img_file = Path(filename)
    if img_file.is_file():
        im = Image.open(filename)
        width, height = im.size
        im.close()
        return width, height
    return (0, 0)


def trim_string_to_fit(canvas, s, fontname, fontsize, toWidth):
    sn = s
    sw = canvas.stringWidth(sn, fontname, fontsize)
    while sw > toWidth:
        sn = sn[:-1]
        sw = canvas.stringWidth(sn, fontname, fontsize)
    return sn


def split_string_to_fit(canvas, s, fontname, fontsize, toWidth):
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


def trim_string_function(canvas, s, fontname, fontsize, toWidth, func):
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


def get_edge_colours(fn, pageno, scale=1.0):
    """returns a dictionary containing a list of colour boundary
    regions for each edge of the page.
    """
    PIX_SCALE = 2

    def _rgb_at_xy(pixmap, x, y):
        idx = int(y * pixmap.width + x) * 3
        pix = pixmap.samples
        r, g, b = pix[idx], pix[idx + 1], pix[idx + 2]
        return r / 255, g / 255, b / 255

    def _diff_rgb(p0, p1):
        diff = (p0[0] - p1[0]) * (p0[0] - p1[0])
        diff += (p0[1] - p1[1]) * (p0[1] - p1[1])
        diff += (p0[2] - p1[2]) * (p0[2] - p1[2])
        return math.sqrt(diff)

    def _sum_rgb(p0, p1):
        return (p0[0] + p1[0], p0[1] + p1[1], p0[2] + p1[2])

    def _diff_strip(pix, plen):
        edges = []
        acc_diff = 0
        acc_avg = 0, 0, 0
        acc_cnt = 0
        for p in range(1, plen):
            p0 = pix[p - 1]
            p1 = pix[p]
            acc_cnt += 1
            acc_avg = _sum_rgb(acc_avg, p0)
            acc_diff += _diff_rgb(p0, p1)
            if acc_diff > 0.01:
                acc_avg = tuple([x / acc_cnt for x in acc_avg])
                edges.append((p * scale * 1 / PIX_SCALE, acc_avg))
                acc_diff = 0
                acc_avg = 0, 0, 0
                acc_cnt = 0
        edges.append((plen * scale * 1 / PIX_SCALE, p1))
        return edges

    mudoc = fitz.open(fn)
    pmh = mudoc[pageno].get_pixmap(matrix=fitz.Matrix(PIX_SCALE, 0.5), alpha=False)
    pmv = mudoc[pageno].get_pixmap(matrix=fitz.Matrix(0.5, PIX_SCALE), alpha=False)
    hstrip = [_rgb_at_xy(pmh, x, 0) for x in range(0, pmh.width)]
    vstrip = [_rgb_at_xy(pmv, 0, y) for y in range(0, pmv.height)]
    hstrip2 = [_rgb_at_xy(pmh, x, pmh.height - 1) for x in range(0, pmh.width)]
    vstrip2 = [_rgb_at_xy(pmv, pmv.width - 1, y) for y in range(0, pmv.height)]
    edge_dict = {}
    edge_dict["top"] = _diff_strip(hstrip, pmh.width)
    edge_dict["left"] = _diff_strip(vstrip, pmv.height)
    edge_dict["bottom"] = _diff_strip(hstrip2, pmh.width)
    edge_dict["right"] = _diff_strip(vstrip2, pmv.height)
    return edge_dict
