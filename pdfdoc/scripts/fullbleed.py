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
# Add full bleed features to PDF

import argparse

import crayons

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from toolbox import toolboxprint, FileOps, colour_path_str, full_path, Rect
from pdfdoc import *


def draw_bleed_rect(doc, location, edge_colours, margin):
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
    num_edges = len(edge_colours[location]) - 1
    for i, edge in enumerate(edge_colours[location]):
        x0 = br.left if i == 0 else br.left + j + m
        x1 = pr.left + edge[0] if i < num_edges else br.right
        if location == "top":
            r.set_points((x0, br.top), (x1, pr.top))
        elif location == "bottom":
            r.set_points((x0, pr.bottom), (x1, br.bottom))
        elif location == "left":
            r.set_points((br.left, pr.top - j), (pr.left, pr.top - edge[0]))
        elif location == "right":
            r.set_points((pr.right, pr.top - j), (br.right, pr.top - edge[0]))
        j = edge[0]
        colour = edge[1]
        cr = ContentRect()
        cr.style["background-fill"] = True
        cr.style["background-colour"] = colour
        cr.style["border-outline"] = True
        cr.style["border-colour"] = colour
        cr.style["border-width"] = 0.1
        cr.rect = r
        cr.draw_in_canvas(doc.c)


def get_page_size(pages):
    allpages = [pagexobj(x) for x in pages]
    width = max(page.BBox[2] for page in allpages)
    height = max(page.BBox[3] for page in allpages)
    return width, height


def add_bleed(
    fn, ofn, bleed=None, scale=1.0, crop_marks=None, margin=None, pix_scale=2.0
):
    scale = float(scale)
    pages = PdfReader(fn).pages
    num_pages = len(pages)
    pw, ph = get_page_size(pages)
    page_list = [pagexobj(x) for x in pages]
    toolboxprint(
        "Document page size : %4.0f x %4.0f pts ( %4.1f x %4.1f mm) ( %5.2f x %5.2f in)"
        % (pw, ph, PTS2MM(pw), PTS2MM(ph), PTS2IN(pw), PTS2IN(ph))
    )
    w, h = pw * scale, ph * scale
    if abs(scale - 1.0) > 0:
        print(crayons.yellow("Rescaling document pages by %.2fx" % (scale)))
        toolboxprint(
            "Scaled page size   : %4.0f x %4.0f pts ( %4.1f x %4.1f mm) ( %5.2f x %5.2f in)"
            % (w, h, PTS2MM(w), PTS2MM(h), PTS2IN(w), PTS2IN(h))
        )

    doc_style = {"width": w, "height": h}
    doc = Document(ofn)
    toolboxprint("Pixel scale : %.3f ( %.1f dpi)" % (pix_scale, pix_scale * 72))
    total_bleed = 0
    if bleed is not None:
        bleed = float(bleed)
        toolboxprint(
            "Bleed size  : %4.0f pts (%4.1f mm) ( %5.3f in)"
            % (float(bleed), PTS2MM(bleed), PTS2IN(bleed))
        )
        total_bleed += float(bleed)
    if margin is not None:
        margin = float(margin)
        toolboxprint(
            "Margin size : %4.0f pts (%4.1f mm) ( %5.3f in)"
            % (float(margin), PTS2MM(margin), PTS2IN(margin))
        )
        total_bleed += float(margin)
    doc.page_end_callbacks = []
    if crop_marks is not None:
        crop_marks = float(crop_marks)
        crop_marks = min(crop_marks, total_bleed)
        crop_callback = CropMarksCallback(length=crop_marks)
        crop_callback.style["line-colour"] = (1.0, 0.1, 0.4)
        doc.page_end_callbacks.append(crop_callback)
        toolboxprint(
            "Adding crop marks : %4.0f pts (%4.1f mm) ( %5.3f in)"
            % (crop_marks, PTS2MM(crop_marks), PTS2IN(crop_marks))
        )
    doc.set_page_size(doc_style, with_bleed=total_bleed)
    if total_bleed > 0:
        wb, hb = doc.bleed_rect.width, doc.bleed_rect.height
        toolboxprint(
            "Size with bleed    : %4.0f x %4.0f pts ( %4.1f x %4.1f mm) ( %5.2f x %5.2f in)"
            % (wb, hb, PTS2MM(wb), PTS2MM(hb), PTS2IN(wb), PTS2IN(hb))
        )
    doc._doc_start()
    for idx, page in enumerate(pages):
        toolboxprint("  Adding page : %3d / %-3d" % (idx + 1, num_pages))
        x = 0
        y = 0
        if total_bleed > 0:
            x += float(total_bleed)
            y += float(total_bleed)
            edges = get_edge_colours(fn, idx, scale, pix_scale=pix_scale)
            draw_bleed_rect(doc, "top", edges, margin)
            draw_bleed_rect(doc, "left", edges, margin)
            draw_bleed_rect(doc, "bottom", edges, margin)
            draw_bleed_rect(doc, "right", edges, margin)
        doc.c.saveState()
        doc.c.translate(x, y)
        doc.c.scale(scale, scale)
        doc.c.doForm(makerl(doc.c, page_list[idx]))
        doc.c.restoreState()
        if (idx + 1) < num_pages:
            doc.page_break()
    doc._doc_end()


def main():
    parser = argparse.ArgumentParser(
        description="Add full bleed printing features to PDF."
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
        default=18,
        help="Add bleed region with size specified in points",
    )
    parser.add_argument(
        "-m",
        "--margin",
        action="store",
        default=18,
        help="Margin around the bleed region in points",
    )
    parser.add_argument(
        "-c",
        "--crop",
        action="store",
        default=32,
        help="Add crop marks with length in points",
    )
    parser.add_argument(
        "-s",
        "--scale",
        action="store",
        default=1.0,
        help="Re-scale document by factor (0.1 ~ 5.0) default=1.0",
    )
    parser.add_argument(
        "-f",
        "--fontoutlines",
        action="store_true",
        default=False,
        help="Convert all fonts to outline shapes",
    )
    parser.add_argument(
        "-p",
        "--pixscale",
        action="store",
        default=4.1666667,
        help="Pixel scale resolution factor used for bleed (default=4.167, 300 dpi)",
    )

    args = parser.parse_args()
    argsd = vars(args)
    fn = argsd["input"]
    fs = FileOps(simulate=True, verbose=True, overwrite=False)
    if not fs.verify_file(fn):
        toolboxprint("Input file %s cannot be found" % (colour_path_str(fn)))
        exit()
    fn = full_path(fn)
    size = os.stat(fn)
    size = size.st_size
    pages = PdfReader(fn).pages
    num_pages = len(pages)
    toolboxprint("Input file  : %s has %d pages" % (colour_path_str(fn), num_pages))
    toolboxprint(
        "              %d pages, size %s" % (num_pages, eng_units(size, units="B"))
    )
    if argsd["output"] is None:
        ofn = fn.replace(".pdf", "_bleed.pdf")
    else:
        ofn = argsd["output"]
    if argsd["bleed"] is None and argsd["margin"] is None:
        print("Converting text to outlines...")
        modify_pdf_file(fn, ofn, outlines=True)
    else:
        add_bleed(
            fn,
            ofn,
            argsd["bleed"],
            argsd["scale"],
            argsd["crop"],
            argsd["margin"],
            float(argsd["pixscale"]),
        )
        if argsd["fontoutlines"]:
            print("Converting text to outlines...")
            modify_pdf_file(ofn, ofn, outlines=True)

    toolboxprint("Output file : %s" % (colour_path_str(ofn)))
    pages = PdfReader(ofn).pages
    num_pages = len(pages)
    size = os.stat(ofn)
    size = size.st_size
    toolboxprint(
        "              %d pages, size %s" % (num_pages, eng_units(size, units="B"))
    )


if __name__ == "__main__":
    main()
