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
# Pre-defined Label Document Styles

from reportlab.lib.units import inch, mm, cm

# Avery 5260
# - 30 labels per sheet
# - 1" x 2-5/8" label size

AVERY_5260_LABEL_DOC_STYLE = {
    "height": 11 * inch,
    "width": 8.5 * inch,
    "ncolumns": 3,
    "nrows": 10,
    "top-margin": 0.5 * inch,
    "bottom-margin": 0.5 * inch,
    "left-margin": 3 / 16 * inch,
    "right-margin": 3 / 16 * inch,
    "gutter-width": 1 / 8 * inch,
    "gutter-height": 0,
}

# Avery 5262
# - 14 labels per sheet
# - 1-1/3" x 4" label size

AVERY_5262_LABEL_DOC_STYLE = {
    "height": 11 * inch,
    "width": 8.5 * inch,
    "ncolumns": 2,
    "nrows": 7,
    "top-margin": 55 / 64 * inch,
    "bottom-margin": 13 / 16 * inch,
    "left-margin": 21 / 128 * inch,
    "right-margin": 19 / 128 * inch,
    "gutter-width": 3 / 16 * inch,
    "gutter-height": 0,
}

# Avery 5263
# - 10 labels per sheet
# - 2" x 4" label size

AVERY_5263_LABEL_DOC_STYLE = {
    "height": 11 * inch,
    "width": 8.5 * inch,
    "ncolumns": 2,
    "nrows": 5,
    "top-margin": 0.5 * inch,
    "bottom-margin": 0.5 * inch,
    "left-margin": 21 / 128 * inch,
    "right-margin": 19 / 128 * inch,
    "gutter-width": 3 / 16 * inch,
    "gutter-height": 0,
}

# Avery 5267
# - 80 labels per sheet
# - 0.5" x 1.75" label size

AVERY_5267_LABEL_DOC_STYLE = {
    "height": 11 * inch,
    "width": 8.5 * inch,
    "ncolumns": 4,
    "nrows": 20,
    "top-margin": 0.5 * inch,
    "bottom-margin": 0.5 * inch,
    "left-margin": 19 / 64 * inch,
    "right-margin": 5 / 16 * inch,
    "gutter-width": 19 / 64 * inch,
    "gutter-height": 0,
}

# Avery 5164
# - 6 labels per sheet
# - 4" x 3-1/3" label size

AVERY_5164_LABEL_DOC_STYLE = {
    "height": 11 * inch,
    "width": 8.5 * inch,
    "ncolumns": 2,
    "nrows": 3,
    "top-margin": 17 / 32 * inch,
    "bottom-margin": 15 / 32 * inch,
    "left-margin": 21 / 128 * inch,
    "right-margin": 19 / 128 * inch,
    "gutter-width": 3 / 16 * inch,
    "gutter-height": 0,
}

GENERIC_LABEL_TITLE = {
    "font": "IKEA-Sans-Heavy",
    "font-size": 21,
    "horz-align": "centre",
    "vert-align": "centre",
    "left-padding": 0.03 * inch,
    "right-padding": 0.03 * inch,
}

GENERIC_LABEL_DESC = {
    "font": "IKEA-Sans-Heavy",
    "font-size": 17,
    "horz-align": "centre",
    "vert-align": "centre",
    "left-padding": 0.03 * inch,
    "right-padding": 0.03 * inch,
}

GENERIC_SYMBOL_LABEL = {
    "font": "FontAwesome",
    "font-size": 20,
    "horz-align": "centre",
    "vert-align": "centre",
    "left-padding": 0.03 * inch,
    "right-padding": 0.03 * inch,
}

SAFETY_LABEL_ICON = {
    "font": "Hazard",
    "font-size": 64,
    "horz-align": "left",
    "vert-align": "top",
    "left-padding": 0 * inch,
}


SAFETY_LABEL_TITLE = {
    "font": "IKEA-Sans-Heavy",
    "font-size": 24,
    "horz-align": "centre",
    "vert-align": "centre",
    "left-padding": 0.0 * inch,
    "right-padding": 0.0 * inch,
    "border-outline": True,
    "border-width": 0.05 * inch,
    "border-colour": (0, 0, 0),
    "background-fill": True,
    "background-colour": (0.9, 0.9, 0.1),
}

SAFETY_LABEL_DESC = {
    "font": "IKEA-Sans-Heavy",
    "font-size": 20,
    "horz-align": "left",
    "vert-align": "centre",
    "left-padding": 0.03 * inch,
    "right-padding": 0.03 * inch,
}
