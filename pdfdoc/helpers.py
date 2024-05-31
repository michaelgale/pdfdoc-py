#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale

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

import math
import string
import subprocess, shlex
import shutil
import tempfile

from PIL import Image
from pathlib import Path
import fitz

from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import Color, CMYKColor


from toolbox import *


def rl_colour(from_colour, alpha=None):
    if isinstance(from_colour, str):
        return rl_colour_hex(from_colour)
    if isinstance(from_colour, (Color, CMYKColor)):
        return from_colour
    if isinstance(from_colour, (list, tuple)):
        alpha = alpha if alpha is not None else 1.0
        if len(from_colour) == 3:
            return Color(from_colour[0], from_colour[1], from_colour[2], alpha=alpha)
        else:
            return CMYKColor(
                from_colour[0], from_colour[1], from_colour[2], from_colour[3]
            )
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


def canvas_save_state(c, x, y, a):
    c.saveState()
    c.translate(x, y)
    c.rotate(a)


def canvas_restore_state(c, a):
    c.rotate(-a)
    c.restoreState()


def clamp_cmyk(v):
    v = (min(v[0], 1.0), min(v[1], 1.0), min(v[2], 1.0), min(v[3], 1.0))
    v = (max(v[0], 0.0), max(v[1], 0.0), max(v[2], 0.0), max(v[3], 0.0))
    return v


def rl_set_border_stroke(c, style):
    if style["border-outline"]:
        c.setStrokeColor(rl_colour(style["border-colour"], style["border-alpha"]))
        c.setLineWidth(style["border-width"])


def rl_draw_rect(c, rect, style):
    rotation = style["rotation"]
    has_background = style["background-fill"]
    background_colour = style["background-colour"]
    border_margin = style["border-margin"]
    mrect = style.get_margin_rect(rect)
    if rotation:
        c.saveState()
        c.translate(*rect.centre)
        c.rotate(rotation)
        rx, ry = rect.centre
        mx, my = mrect.centre
        xo, yo = mx - rx, my - ry
        mrect.move_to(xo, yo)
    if has_background:
        fc = rl_colour(background_colour, style["background-alpha"])
        c.setFillColor(fc)
    else:
        fc = rl_colour_trans()
    rl_set_border_stroke(c, style)
    border_radius = style["border-radius"]
    stroke = style["border-outline"] and not abs(border_margin) > 0
    if border_radius > 0:
        c.roundRect(
            mrect.left,
            mrect.bottom,
            mrect.width,
            mrect.height,
            radius=border_radius,
            stroke=stroke,
            fill=has_background,
        )
    else:
        c.rect(
            mrect.left,
            mrect.bottom,
            mrect.width,
            mrect.height,
            stroke=stroke,
            fill=has_background,
        )
    if style["border-outline"] and abs(border_margin) > 0:
        mrect = mrect.expanded_by(-style["border-margin"])
        if border_radius > 0:
            c.roundRect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                radius=border_radius,
                stroke=True,
                fill=False,
            )
        else:
            c.rect(
                mrect.left,
                mrect.bottom,
                mrect.width,
                mrect.height,
                stroke=True,
                fill=False,
            )
    c.setStrokeColor(rl_colour(style["border-colour"], style["border-alpha"]))
    c.setLineWidth(style["border-width"])
    if style["border-line-left"]:
        c.line(mrect.left, mrect.top, mrect.left, mrect.bottom)
    if style["border-line-right"]:
        c.line(mrect.right, mrect.top, mrect.right, mrect.bottom)
    if style["border-line-top"]:
        c.line(mrect.left, mrect.top, mrect.right, mrect.top)
    if style["border-line-bottom"]:
        c.line(mrect.left, mrect.bottom, mrect.right, mrect.bottom)
    if rotation:
        c.restoreState()


def get_string_metrics(c, label, fontname, fontsize, with_descent=True):
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
    ascent, descent = (face.ascent / 1000.0), abs(face.descent / 1000.0)
    height = ascent - descent if with_descent else ascent
    height *= fontsize
    width = c.stringWidth(label, fontname_, fontsize)
    return (width, height)


def get_string_asc_des(c, label, fontname, fontsize):
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


def does_string_fit(canvas, s, fontname, fontsize, width):
    return canvas.stringWidth(s, fontname, fontsize) <= width


def trim_string_to_fit(canvas, s, fontname, fontsize, toWidth):
    sn = s
    while not does_string_fit(canvas, sn, fontname, fontsize, toWidth):
        sn = sn[:-1]
    return sn


def scale_string_to_fit(canvas, s, fontname, fontsize, toWidth):
    fs = fontsize
    while not does_string_fit(canvas, s, fontname, fs, toWidth):
        fs *= 0.95
    return fs


def expand_string_to_fit(canvas, s, fontname, fontsize, toWidth):
    fs = fontsize
    new_size = False
    while does_string_fit(canvas, s, fontname, fs, toWidth):
        fs *= 1.05
        new_size = True
    if new_size:
        fs *= 0.9
    return fs


def split_string_to_fit(canvas, s, fontname, fontsize, toWidth):
    words = s.split()
    lines = []
    line = []
    line_sum = 0
    for word in words:
        sw = canvas.stringWidth(word + " ", fontname, fontsize)
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


def scale_iterable(v, scale):
    if isinstance(v, list):
        return [scale_iterable(e, scale) for e in v]
    elif isinstance(v, tuple):
        return tuple(scale_iterable(e, scale) for e in v)
    else:
        return v * scale


def PTS2MM(pts):
    return scale_iterable(pts, 25.4 / 72)


def PTS2IN(pts):
    return scale_iterable(pts, 1 / 72)


def IN2PTS(inch):
    return scale_iterable(inch, 72)


def MM2PTS(mm):
    return scale_iterable(mm, 72 / 25.4)


def PIX2PTS(pix, dpi):
    if isinstance(pix, tuple):
        return pix[0] / dpi * 72, pix[1] / dpi * 72
    return pix / dpi * 72


def PTS2PIX(pts, dpi):
    if isinstance(pts, tuple):
        return int(pts[0] * dpi / 72), int(pts[1] * dpi / 72)
    return int(pts * dpi / 72)


def get_edge_colours(fn, pageno, scale=1.0, pix_scale=2.0):
    """returns a dictionary containing a list of colour boundary
    regions for each edge of the page.
    """
    PIX_SCALE = pix_scale

    def _rgb_at_xy(pixmap, x, y):
        idx = int(y * pixmap.width + x) * 3
        pix = pixmap.samples
        r, g, b = pix[idx], pix[idx + 1], pix[idx + 2]
        return r / 255, g / 255, b / 255

    def _cmyk_at_xy(pixmap, x, y):
        idx = int(y * pixmap.width + x) * 4
        pix = pixmap.samples
        c, m, y, k = pix[idx], pix[idx + 1], pix[idx + 2], pix[idx + 3]
        return c / 255, m / 255, y / 255, k / 255

    def _mag_rgb(p):
        return math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])

    def _diff_rgb(p0, p1):
        diff = (p0[0] - p1[0]) * (p0[0] - p1[0])
        diff += (p0[1] - p1[1]) * (p0[1] - p1[1])
        diff += (p0[2] - p1[2]) * (p0[2] - p1[2])
        return math.sqrt(diff)

    def _diff_cmyk(p0, p1):
        diff = (p0[0] - p1[0]) * (p0[0] - p1[0])
        diff += (p0[1] - p1[1]) * (p0[1] - p1[1])
        diff += (p0[2] - p1[2]) * (p0[2] - p1[2])
        diff += (p0[3] - p1[3]) * (p0[3] - p1[3])
        return math.sqrt(diff)

    def _sum_rgb(p0, p1):
        return (p0[0] + p1[0], p0[1] + p1[1], p0[2] + p1[2])

    def _sum_cmyk(p0, p1):
        return (p0[0] + p1[0], p0[1] + p1[1], p0[2] + p1[2], p0[3] + p1[3])

    def find_bottom_edge(pix):
        ph = pix.height
        if ph >= 2:
            py = ph - 1
            for py in range(py, 1, -1):
                h1 = [_rgb_at_xy(pix, x, py) for x in range(0, pix.width)]
                h0 = [_rgb_at_xy(pix, x, py - 1) for x in range(0, pix.width)]
                diff = sum([_diff_rgb(h1[i], h0[i]) for i in range(pix.width)])
                if diff / pix.width < 0.006:
                    return h1
        return [_rgb_at_xy(pix, x, ph - 1) for x in range(0, pix.width)]

    def find_right_edge(pix):
        pw = pix.width
        if pw >= 2:
            px = pw - 1
            for px in range(px, 1, -1):
                h1 = [_rgb_at_xy(pix, px, y) for y in range(0, pix.height)]
                h0 = [_rgb_at_xy(pix, px - 1, y) for y in range(0, pix.height)]
                diff = sum([_diff_rgb(h1[i], h0[i]) for i in range(pix.height)])
                if diff / pix.height < 0.006:
                    return h1
        return [_rgb_at_xy(pix, pw - 1, y) for y in range(0, pix.height)]

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
            diff = _diff_rgb(p0, p1)
            acc_diff += diff
            if _mag_rgb(p1) < 0.015:
                continue
            if acc_diff > 0.03:
                acc_avg = tuple([x / acc_cnt for x in acc_avg])
                edges.append((p * scale / PIX_SCALE, acc_avg))
                acc_diff = 0
                acc_avg = 0, 0, 0
                acc_cnt = 0
        edges.append((plen * scale / PIX_SCALE, p0))
        return edges

    mudoc = fitz.open(fn)
    page = mudoc[pageno]
    rect = page.rect
    clip_top = fitz.Rect((0, 0), (rect.width, 2))
    clip_bottom = fitz.Rect((0, rect.height - 2), rect.br)
    clip_left = fitz.Rect((0, 0), (2, rect.height))
    clip_right = fitz.Rect((rect.width - 2, 0), rect.br)
    pix_top = page.get_pixmap(
        matrix=fitz.Matrix(PIX_SCALE, PIX_SCALE),
        alpha=False,
        clip=clip_top,
        colorspace="RGB",
    )
    pix_bottom = page.get_pixmap(
        matrix=fitz.Matrix(PIX_SCALE, PIX_SCALE),
        alpha=False,
        clip=clip_bottom,
        colorspace="RGB",
    )
    pix_left = page.get_pixmap(
        matrix=fitz.Matrix(PIX_SCALE, PIX_SCALE),
        alpha=False,
        clip=clip_left,
        colorspace="RGB",
    )
    pix_right = page.get_pixmap(
        matrix=fitz.Matrix(PIX_SCALE, PIX_SCALE),
        alpha=False,
        clip=clip_right,
        colorspace="RGB",
    )
    top_strip = [_rgb_at_xy(pix_top, x, 0) for x in range(0, pix_top.width)]
    left_strip = [_rgb_at_xy(pix_left, 0, y) for y in range(0, pix_left.height)]
    bottom_strip = find_bottom_edge(pix_bottom)
    right_strip = find_right_edge(pix_right)
    edge_dict = {}
    edge_dict["top"] = _diff_strip(top_strip, pix_top.width)
    edge_dict["left"] = _diff_strip(left_strip, pix_left.height)
    edge_dict["bottom"] = _diff_strip(bottom_strip, pix_bottom.width)
    edge_dict["right"] = _diff_strip(right_strip, pix_right.height)
    return edge_dict


def is_rect_in_transparent_region(fn, rect):
    """Determines if a rect area overlaps only transparent pixels in an image"""
    im = Image.open(fn)
    im = im.convert("RGBA")
    pix = im.load()
    width, height = im.size
    # intersect the rectangle within the bounds of the image
    rb, rt = int(rect.bottom), int(rect.top)
    y0, y1 = min(rb, rt), max(rb, rt)
    x0, x1 = int(rect.left), int(rect.right)
    x0, x1 = clamp_value(x0, 0, width), clamp_value(x1, 0, width)
    y0, y1 = clamp_value(y0, 0, height), clamp_value(y1, 0, height)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not pix[x, y][3] == 0:
                return False
    return True


def modify_pdf_file(
    fn, fnout, outlines=True, cmyk=False, compress=False, verbose=False
):
    temp_path = tempfile.gettempdir() + os.sep + "temp_outlines.pdf"
    s = []
    s.append("gs")
    s.append("-sOutputFile=%s" % (temp_path))
    if outlines:
        s.append("-dNoOutputFonts")
    s.append("-sDEVICE=pdfwrite")
    if cmyk:
        s.append("-sColorConversionStrategy=CMYK")
    s.append("-dbatch")
    s.append("-dNOPAUSE")
    if not verbose:
        s.append("-q")
        s.append("-dQUIET")
    if compress:
        s.append("-dAutoFilterColorImages=true")
    else:
        s.append("-dAutoFilterColorImages=false")
        s.append("-dColorImageFilter=/FlateEncode")
    s.append("-dInterpolateControl=0")
    s.append("%s" % (fn))
    s.append("-c quit")
    s = " ".join(s)
    args = shlex.split(s)
    subprocess.Popen(args).wait()
    shutil.copyfile(temp_path, fnout)


def convert_pdf_to_thumbnail(fn, ofn=None, res=144, **kwargs):
    if ofn is not None:
        outfile = ofn
    else:
        fp, f = split_path(fn)
        fa, fe = split_filename(f)
        outfile = fp + os.sep + fa
    outfile = outfile.replace(".png", "")
    s = []
    s.append("pdftopng")
    s.append(fn)
    s.append(outfile)
    s.append("-f 1 -l 1")
    s.append("-singlefile")
    s.append("-r %d" % (res))
    for k, v in kwargs.items():
        s.append("-%s %s" % (k, v))
    s = " ".join(s)
    args = shlex.split(s)
    subprocess.Popen(args).wait()


def convert_pdf_to_png(
    fn,
    ofn=None,
    res=150,
    first=1,
    last=1,
    auto_crop_height=False,
    auto_crop_width=False,
    pad=None,
    **kwargs
):
    if ofn is not None:
        outfile = ofn
    else:
        fp, f = split_path(fn)
        fa, fe = split_filename(f)
        outfile = fp + os.sep + fa
    outfile = outfile.replace(".png", "")
    s = []
    s.append("pdftopng")
    s.append("-f %d -l %d" % (first, last))
    s.append("-r %d" % (res))
    for k, v in kwargs.items():
        s.append("-%s %s" % (k, v))
    s.append(fn)
    s.append(outfile)
    s = " ".join(s)
    args = shlex.split(s)
    subprocess.Popen(args).wait()
    for page_no in range(first, last + 1):
        pfn = outfile + "-%06d.png" % (page_no)
        img = ImageMixin.auto_open(pfn)
        bg = tuple(int(x) for x in img[0, 0])
        if auto_crop_height or auto_crop_width:
            img = ImageMixin.crop_to_content(
                img, widthwise=auto_crop_width, heightwise=auto_crop_height
            )
        if pad is not None:
            top = True if auto_crop_height else False
            bottom = True if auto_crop_height else False
            left = True if auto_crop_width else False
            right = True if auto_crop_width else False
            img = ImageMixin.pad_image(
                img, pad, val=bg, top=top, left=left, bottom=bottom, right=right
            )
        ImageMixin.save_image(pfn, img)


def line_angle(p0, p1, degrees=True):
    """Angle of line from point p1 to p0"""
    xl, yl = p1[0] - p0[0], p1[1] - p0[1]
    if degrees:
        return math.degrees(math.atan2(yl, xl))
    return math.atan2(yl, xl)


def line_mid_point(p0, p1):
    return p0[0] + (p1[0] - p0[0]) / 2, p0[1] + (p1[1] - p0[1]) / 2


def linear_offset(length, width, thickness):
    th = math.atan2(width, length)
    rx = thickness / math.sin(th)
    return math.sqrt(rx * rx - thickness * thickness)
