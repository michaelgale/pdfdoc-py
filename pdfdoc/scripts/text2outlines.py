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

from pdfrw import PdfReader

from toolbox import toolboxprint, FileOps, colour_path_str, full_path
from pdfdoc import *


def main():
    parser = argparse.ArgumentParser(
        description="Convert all text to outlines in a PDF, removing font dependencies."
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
        "-c",
        "--compress",
        action="store_true",
        default=False,
        help="Compress images in PDF files",
    )
    parser.add_argument(
        "-k",
        "--cmyk",
        action="store_true",
        default=False,
        help="Convert PDF colour space to CMYK",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show verbose output from ghostscript",
    )
    args = parser.parse_args()
    argsd = vars(args)
    fn = argsd["input"]
    fs = FileOps(simulate=True, verbose=True, overwrite=False)
    if not fs.verify_file(fn):
        toolboxprint("Input file %s cannot be found" % (colour_path_str(fn)))
        exit()
    size = os.stat(fn)
    size = size.st_size
    fn = full_path(fn)
    pages = PdfReader(fn).pages
    num_pages = len(pages)
    toolboxprint("Input file  : %s" % (colour_path_str(fn)))
    toolboxprint(
        "              %d pages, size %s" % (num_pages, eng_units(size, units="B"))
    )
    if argsd["output"] is None:
        ofn = fn.replace(".pdf", "_outlines.pdf")
    else:
        ofn = argsd["output"]
    opts = ""
    if argsd["cmyk"]:
        opts += " converting to CMYK"
    if argsd["compress"]:
        opts += " with compression"
    print("Converting text to outlines%s..." % (opts))
    modify_pdf_file(
        fn,
        ofn,
        outlines=True,
        cmyk=argsd["cmyk"],
        compress=argsd["compress"],
        verbose=argsd["verbose"],
    )

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
