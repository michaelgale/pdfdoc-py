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
# Page styles

from reportlab.lib.units import inch, mm

DEFAULT_MARGINS = {
    "left-margin": 0.5 * inch,
    "right-margin": 0.5 * inch,
    "top-margin": 0.5 * inch,
    "bottom-margin": 0.5 * inch,
}

PAGE_LETTER = {"width": 8.5 * inch, "height": 11 * inch, "orientation": "portrait"}
CANVAS_LETTER = (8.5 * inch, 11 * inch)
CANVAS_LETTER_LANDSCAPE = (11 * inch, 8.5 * inch)

PAGE_TABLOID = {"width": 17 * inch, "height": 11 * inch, "orientation": "landscape"}
CANVAS_TABLOID = (11 * inch, 17 * inch)

PAGE_LEDGER = {"width": 11 * inch, "height": 17 * inch, "orientation": "portrait"}
CANVAS_LEDGER = (17 * inch, 11 * inch)

PAGE_A5 = {"width": 148 * mm, "height": 210 * mm, "orientation": "portrait"}
CANVAS_A5 = (148 * mm, 210 * mm)
CANVAS_A5_LANDSCAPE = (210 * mm, 148 * mm)

PAGE_A4 = {"width": 210 * mm, "height": 297 * mm, "orientation": "portrait"}
CANVAS_A4 = (210 * mm, 297 * mm)
CANVAS_A4_LANDSCAPE = (297 * mm, 210 * mm)

PAGE_A3 = {"width": 297 * mm, "height": 420 * mm, "orientation": "portrait"}
CANVAS_A3 = (297 * mm, 420 * mm)
CANVAS_A3_LANDSCAPE = (420 * mm, 297 * mm)
