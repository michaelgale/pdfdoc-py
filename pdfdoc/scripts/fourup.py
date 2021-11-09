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
# 4-up PDF layout

import argparse
import math
import sys
import os

import fitz
import crayons
from pdfdoc.style.pagestyles import PAGE_TABLOID
from reportlab.pdfgen.canvas import Canvas

from pdfrw import PdfReader, PageMerge, PdfDict
from pdfrw.pagemerge import RectXObj
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from toolbox import *
from pdfdoc import *


def four_up_index(idx, num_pages):
    """converts a linear page index into a remapped 4-up page index"""
    ridx = int(math.floor(idx / 2))
    if (idx & 0x03) == 0x01 or (idx & 0x03) == 0x02:
        return ridx
    return num_pages - 1 - ridx


def get_edge_colours(fn, pageno, scale=1.0):
    """returns a dictionary containing a list of colour boundary
    regions for each each of the page.
    """

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
            if acc_diff > 0.03:
                acc_avg = tuple([x / acc_cnt for x in acc_avg])
                edges.append((p * scale, acc_avg))
                acc_diff = 0
                acc_avg = 0, 0, 0
                acc_cnt = 0
        edges.append((plen * scale, p1))
        return edges

    def _diff_rgb_strip(pixmap, ps, axis="horz"):
        if axis == "horz":
            strip = [_rgb_at_xy(pixmap, x, ps) for x in range(0, pixmap.width)]
            edges = _diff_strip(strip, pixmap.width)
        else:
            strip = [_rgb_at_xy(pixmap, ps, y) for y in range(0, pixmap.height)]
            edges = _diff_strip(strip, pixmap.height)
        return edges

    mudoc = fitz.open(fn)
    pm = mudoc[pageno].get_pixmap(alpha=False)
    edge_dict = {}
    edge_dict["top"] = _diff_rgb_strip(pm, 0, axis="horz")
    edge_dict["left"] = _diff_rgb_strip(pm, 0, axis="vert")
    edge_dict["bottom"] = _diff_rgb_strip(pm, pm.height - 1, axis="horz")
    edge_dict["right"] = _diff_rgb_strip(pm, pm.width - 1, axis="vert")
    return edge_dict


def get_page_size(pages):
    allpages = [pagexobj(x) for x in pages]
    width = max(page.BBox[2] for page in allpages)
    height = max(page.BBox[3] for page in allpages)
    return width, height


def draw_bleed_rect(doc, side, location, edge_colours, margin):
    """Draws colour rectangles in the specified bleed page location
    The bleed colour regions must be computed by get_edge_colours
    first and passed into the edge_colours argument."""
    r = Rect()
    br = doc.bleed_rect.copy()
    m = 0
    if margin is not None:
        m = float(margin)
        if m > 0:
            br.top -= m
            br.bottom += m
            br.left += m
            br.right -= m
            br.width = br.right - br.left
            br.height = abs(br.top - br.bottom)
    pr = doc.page_rect
    j = 0
    for i, edge in enumerate(edge_colours[location]):
        if side == "left":
            x0 = br.left if i == 0 else pr.left
            if location == "top":
                r.set_points((x0 + j, br.top), (pr.left + edge[0], pr.top))
            elif location == "bottom":
                r.set_points((x0 + j, pr.bottom), (pr.left + edge[0], br.bottom))
            elif location == "left":
                r.set_points((br.left, pr.top - j), (pr.left, pr.top - edge[0]))
        elif side == "right":
            if location == "top":
                r.set_points((br.width / 2 + j + m, br.top), (br.right, pr.top))
            elif location == "bottom":
                r.set_points((br.width / 2 + j + m, pr.bottom), (br.right, br.bottom))
            elif location == "right":
                r.set_points((pr.right, pr.top - j), (br.right, pr.top - edge[0]))
        j = edge[0]
        colour = edge[1]
        cr = ContentRect()
        cr.style["background-fill"] = True
        cr.style["background-colour"] = colour
        cr.style["border-outline"] = True
        cr.style["border-colour"] = colour
        cr.style["border-width"] = 0.02
        cr.rect = r
        cr.draw_in_canvas(doc.c)


def blank_page(width, height):
    blank = PageMerge()
    blank.mbox = [0, 0, width, height]
    blank = blank.render()
    return blank


def pad_pages(pages, padding=4):
    w, h = get_page_size(pages)
    for _ in range(len(pages) % padding):
        pages.append(blank_page(w, h))
    return pages


def make_four_up(fn, ofn, bleed=None, scale=1.0, crop_marks=None, margin=None):
    scale = float(scale)
    pages = PdfReader(fn).pages
    pages = pad_pages(pages)
    num_pages = len(pages)
    pw, ph = get_page_size(pages)
    pages = [pagexobj(x) for x in pages]
    toolboxprint(
        "Document page size : %4.0f x %4.0f pts ( %4.0f x %4.0f mm) ( %5.2f x %5.2f in)"
        % (pw, ph, PTS2MM(pw), PTS2MM(ph), PTS2IN(pw), PTS2IN(ph))
    )
    w, h = 2.0 * pw * scale, ph * scale
    if abs(scale - 1.0) > 0:
        print(crayons.yellow("Rescaling document pages by %.2fx" % (scale)))
    toolboxprint(
        "4-up page size     : %4.0f x %4.0f pts ( %4.0f x %4.0f mm) ( %5.2f x %5.2f in)"
        % (w, h, PTS2MM(w), PTS2MM(h), PTS2IN(w), PTS2IN(h))
    )

    doc_style = {"width": w, "height": h}
    doc = Document(ofn)
    total_bleed = 0
    if bleed is not None:
        toolboxprint("Bleed size  : %4.0f" % (float(bleed)))
        total_bleed += float(bleed)
    if margin is not None:
        toolboxprint("Margin size : %4.0f" % (float(margin)))
        total_bleed += float(margin)
    doc.set_page_size(doc_style, with_bleed=total_bleed)
    if total_bleed > 0:
        wb, hb = doc.bleed_rect.width, doc.bleed_rect.height
        toolboxprint(
            "4-up with bleed    : %4.0f x %4.0f pts ( %4.0f x %4.0f mm) ( %5.2f x %5.2f in)"
            % (wb, hb, PTS2MM(wb), PTS2MM(hb), PTS2IN(wb), PTS2IN(hb))
        )
    doc.page_end_callbacks = []
    if crop_marks is not None:
        crop_callback = CropMarksCallback(length=float(crop_marks))
        crop_callback.style["line-colour"] = (0.5, 0.5, 0.5)
        doc.page_end_callbacks.append(crop_callback)
    doc._doc_start()
    for idx, page in enumerate(pages):
        ridx = four_up_index(idx, num_pages)
        if idx % 4 == 0:
            print(crayons.green("Sheet : %d" % (int((idx + 4) / 4))))
        toolboxprint(
            "  Adding page : %3d / %-3d -> %3d" % (ridx + 1, num_pages, idx + 1)
        )
        if (idx + 1) % 2 == 0:
            toolboxprint("  Page break  : %d" % (int((idx + 1) / 2)))
        x = w * (idx & 1) / 2.0
        y = 0
        if total_bleed > 0:
            x += float(total_bleed)
            y += float(total_bleed)
            edges = get_edge_colours(fn, ridx, scale)
            if idx & 0x01 == 0:
                # left page bleeds
                draw_bleed_rect(doc, "left", "top", edges, margin)
                draw_bleed_rect(doc, "left", "left", edges, margin)
                draw_bleed_rect(doc, "left", "bottom", edges, margin)
            else:
                # right page bleeds
                draw_bleed_rect(doc, "right", "top", edges, margin)
                draw_bleed_rect(doc, "right", "right", edges, margin)
                draw_bleed_rect(doc, "right", "bottom", edges, margin)
        doc.c.saveState()
        doc.c.translate(x, y)
        doc.c.scale(scale, scale)
        doc.c.doForm(makerl(doc.c, pages[ridx]))
        doc.c.restoreState()
        if (idx + 1) % 2 == 0 and (idx + 1) < num_pages:
            doc.page_break()
    doc._doc_end()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reassemble document into a 4-up print layout"
    )
    parser.add_argument("input", metavar="input", type=str, help="Input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        action="store",
        help="Optional output PDF filename",
    )
    parser.add_argument(
        "-b",
        "--bleed",
        action="store",
        default=None,
        help="Add bleed region with size specified in points",
    )
    parser.add_argument(
        "-m",
        "--margin",
        action="store",
        default=None,
        help="Margin around the bleed region in points",
    )
    parser.add_argument(
        "-c",
        "--crop",
        action="store",
        default=None,
        help="Add crop marks with length in points",
    )
    parser.add_argument(
        "-s",
        "--scale",
        action="store",
        default=1.0,
        help="Re-scale document by factor (0.1 ~ 5.0) default=1.0",
    )
    args = parser.parse_args()
    argsd = vars(args)
    fn = argsd["input"]
    fs = FileOps(simulate=True, verbose=True, overwrite=False)
    if not fs.verify_file(fn):
        print("Input file %s cannot be found" % (colour_path_str(fn)))
        exit()
    fn = full_path(fn)
    pages = PdfReader(fn).pages
    num_pages = len(pages)
    print("Input file  : %s has %d pages" % (colour_path_str(fn), num_pages))
    if num_pages % 4 > 0:
        print(
            crayons.yellow(
                "Warning file must have a multiple of 4 pages. Padding with blank pages."
            )
        )
    if argsd["output"] is None:
        ofn = fn.replace(".pdf", "_4up.pdf")
    else:
        ofn = argsd["output"]
    print("Output file : %s" % (colour_path_str(ofn)))
    make_four_up(
        fn, ofn, argsd["bleed"], argsd["scale"], argsd["crop"], argsd["margin"]
    )
