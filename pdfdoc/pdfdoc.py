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


def register_font(font_name, font_filename):
    pdfmetrics.registerFont(TTFont(font_name, font_filename))


def rl_colour(fromColour):
    return Color(fromColour[0], fromColour[1], fromColour[2], alpha=1.0)


def rl_colour_trans():
    return Color(1, 1, 1, alpha=0.0)


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


fa_lookup_dict = {
    "fa-caution": "\uF071",
    "mandatory": "\uF06A",
    "power-button": "\uF011",
    "paper": "\uF016",
    "paper-solid": "\uF15B",
    "home": "\uF015",
    "gear": "\uF013",
    "gears": "\uF085",
    "speaker-off": "\uF025",
    "speaker-min": "\uF026",
    "speaker-max": "\uF027",
    "label": "\uF02B",
    "labels": "\uF02C",
    "beaker": "\uF0C3",
    "wrench": "\uF0AD",
    "lightning": "\uF0E7",
    "apple": "\uF179",
    "windows": "\uF17A",
    "man": "\uF183",
    "woman": "\uF182",
    "box": "\uF1B2",
    "recycle": "\uF1B8",
    "plug": "\uF1E6",
    "wifi": "\uF1EB",
    "syringe": "\uF1FB",
    "puzzle": "\uF12E",
    "info": "\uF05A",
    "desktop-pc": "\uF108",
    "laptop-pc": "\uF109",
    "tablet": "\uF10A",
    "phone": "\uF10B",
    "cup": "\uF0F4",
    "lightbulb": "\uF0EB",
    "truck": "\uF0D1",
    "list": "\uF0CA",
    "paperclip": "\uF0C6",
    "people": "\uF0C0",
    "link": "\uF0C1",
    "toolbox": "\uF0B1",
    "globe": "\uF0AC",
    "bell": "\uF0A2",
    "horn": "\uF0A1",
    "unlock": "\uF09C",
    "cart": "\uF07A",
    "magnet": "\uF076",
    "calendar": "\uF073",
    "airplane": "\uF072",
    "gift": "\uF06B",
    "fa-prohibited": "\uF05E",
    "question": "\uF059",
    "crosshair": "\uF05B",
    "check-yes": "\uF058",
    "cross-no": "\uF057",
    "nav-first": "\uF048",
    "nav-prev": "\uF049",
    "nav-rew": "\uF04A",
    "nav-play": "\uF04B",
    "nav-pause": "\uF04C",
    "nav-stop": "\uF04D",
    "nav-fwd": "\uF04E",
    "nav-next": "\uF050",
    "nav-last": "\uF051",
    "nav-eject": "\uF052",
    "pencil": "\uF040",
    "camera": "\uF030",
    "lock": "\uF023",
    "trash": "\uF014",
    "person": "\uF007",
    "star": "\uF005",
    "envelope": "\uF003",
    "find": "\uF002",
    "music": "\uF001",
    "x": "\uF00D",
    "check": "\uF00C",
    "flag": "\uF024",
    "water": "\uF043",
    "leaf": "\uF06C",
    "up-down": "\uF07D",
    "left-right": "\uF07E",
    "boxes": "\uF1B3",
    "shower": "\uF2CC",
    "chip": "\uF2DB",
    "snowflake": "\uF2DC",
    "thermometer": "\uF2C9",
    "bluetooth": "\uF294",
    "bluetooth-solid": "\uF293",
    "batt-full": "\uF240",
    "batt-3quarter": "\uF241",
    "batt-half": "\uF242",
    "batt-quarter": "\uF243",
    "batt-empty": "\uF244",
    "train-headlight": "\uF238",
    "train-twolight": "\uF239",
    "brush": "\uF1FC",
    "truck": "\uF0D1",
    "receipt": "\uF298",
    "orders": "\uF218",
    "inbox": "\uF01C",
    "round-left": "\uF0A8",
    "round-right": "\uF0A9",
    "round-up": "\uF0AA",
    "round-down": "\uF0AB",
    "yes-box": "\uF14A",
}


def fasymbol(x):
    """ Returns a FontAwesome symbol using a descriptive name """
    if x.lower() in fa_lookup_dict:
        return fa_lookup_dict[x.lower()]
    return ""


haz_lookup_dict = {
    "caution": "!",
    "laser": "C",
    "radiation": "E",
    "electrical": "F",
    "fire": "H",
    "poison": "I",
    "oxidization": "L",
    "eye-protection": "l",
    "boots": "m",
    "gloves": "n",
    "hat": "o",
    "ear-protection": "p",
    "wash-hands": "w",
    "face-shield": "x",
    "face-mask": "y",
    "no-people": "b",
    "no-smoking": "d",
    "no-cups": "f",
    "no-utensils": "g",
    "no-food": "=",
    "exit": "\u005E",
    "first-aid": "Q",
    "left-arrow": "R",
    "right-arrow": "S",
    "up-arrow": "T",
    "down-arrow": "U",
    "prohibited": "1",
    "power-off": "u",
}


def hazsymbol(x):
    """ Returns a Hazard symbol using a descriptive name """
    if x.lower() in haz_lookup_dict:
        return haz_lookup_dict[x.lower()]
    return ""


def set_icon(x, textrect):
    """ Automatically fills a TextRect with an icon from Hazard or FontAwesome fonts """
    xl = x.lower()
    if xl in haz_lookup_dict:
        textrect.style.set_attr("font-name", "Hazard")
        textrect.text = haz_lookup_dict[xl]
    if xl in fa_lookup_dict:
        textrect.style.set_attr("font-name", "FontAwesome")
        textrect.text = fa_lookup_dict[xl]
