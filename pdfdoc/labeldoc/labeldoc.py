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
# Label Document Class

import math

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *


class LabelDoc:
    """A convenient document class for making labels on typical self-adhesive
    label sheets.  The contents of each label can be filled sequentially
    using iter_label generator method.  Each label's content can be any object
    which supports a draw_in_canvas method, i.e. any ContentRect dervied class
    or TableVector derived class."""

    def __init__(self, filename, style=None):
        self.filename = filename
        self.style = DocStyle()
        self.style.set_with_dict(style)
        self.tablegrid = TableColumn(0, 0)
        self.compute_page_metrics()
        self.c = None
        self.page_number = 1

    def __str__(self):
        rs = []
        rs.append(
            "LabelDoc (%d rows x %d columns) %d labels per page"
            % (self.nrows, self.ncolumns, self.labels_per_page)
        )
        rs.append(
            '  Label size: (%.2f" x %.2f") '
            % (self.col_width / inch, self.row_height / inch)
        )
        rs.append(
            '  Page size: (%.2f" x %.2f") '
            % (self.pagerect.width / inch, self.pagerect.height / inch)
        )
        rs.append(
            "  Margins: (Top: %.3f Bottom: %.3f Left: %.3f Right: %.3f)"
            % (
                self.style.get_attr("top-margin") / inch,
                self.style.get_attr("bottom-margin") / inch,
                self.style.get_attr("left-margin") / inch,
                self.style.get_attr("right-margin") / inch,
            )
        )
        if self.row_gutters:
            rs.append(
                "  Row gutters: %.3f (%d total rows)"
                % (self.style.get_attr("gutter-height") / inch, self.total_rows)
            )
        if self.col_gutters:
            rs.append(
                "  Col gutters: %.3f (%d total cols)"
                % (self.style.get_attr("gutter-width") / inch, self.total_columns)
            )
        for i, r in enumerate(self.tablegrid.cells):
            if isinstance(r.content, (TableRow, TableColumn, TableVector)):
                s = []
                s.append("  Row %d (%.3f): " % (i + 1, r.content.rect.height / inch))
                for j, c in enumerate(r.content.cells):
                    s.append("%d: (%.3f) | " % (j + 1, c.content.rect.width / inch))
                rs.append("".join(s))
            else:
                rs.append(
                    "  Row %d: %s (%.2f, %.2f)"
                    % (
                        i + 1,
                        repr(r),
                        r.content.rect.width / inch,
                        r.content.rect.height / inch,
                    )
                )
        return "\n".join(rs)

    def get_row_col(self, idx):
        """ Helper method to return row, col index computed from a linear index """
        r = math.floor(idx / self.ncolumns) % self.nrows
        c = idx % self.ncolumns
        return r, c

    def get_table_cell(self, row, col=None):
        """Returns the content container at a specified cell in the tablegrid
        Note that this lookup is designed to return content cells rather than
        placeholder cells used for gutters.  It performs this lookup using the
        labels which are assigned by compute_page_metrics.  If the labels are not
        assigned or have been modified, then this lookup will not work as expected.
        """
        if col is None:
            row, col = self.get_row_col(row)
        for r in self.tablegrid.cells:
            if isinstance(r.content, (TableRow, TableColumn, TableVector)):
                title = "%02d%02d" % (row, col)
                cell = r.content.get_cell_content(title)
                if cell is not None:
                    return cell
        return None

    def set_table_cell(self, content, row, col=None):
        """This function will typically be called within the context of a
        iter_label generator loop to specify the desired content of
        each individual label cell.
        """
        if col is None:
            row, col = self.get_row_col(row)
        for r in self.tablegrid.cells:
            if isinstance(r.content, (TableRow, TableColumn, TableVector)):
                title = "%02d%02d" % (row, col)
                cell = r.content.get_cell_content(title)
                if cell is not None:
                    r.content.set_cell_content(title, content)

    def compute_page_metrics(self):
        """Computes all of the derived page metrics of the label grid sheet.
        It also prepares the tablegrid content container (a TableVector class)
        with placeholder content for both the actual label content cells and
        dummy cells representing gutter regions between labels.  Although this
        is called automatically during __init__, it should be called if any major
        alterations are made to the label sheet layout.
        """
        self.pagerect = Rect(
            self.style.get_attr("width"), self.style.get_attr("height")
        )
        self.pagerect.move_bottom_left_to((0, 0))
        self.contentrect = self.style.get_margin_rect(self.pagerect)
        self.nrows = self.style.get_attr("nrows")
        self.ncolumns = self.style.get_attr("ncolumns")
        self.labels_per_page = self.nrows * self.ncolumns
        self.row_height = (
            self.style.get_attr("height")
            - self.style.get_attr("top-margin")
            - self.style.get_attr("bottom-margin")
            - (self.nrows - 1) * self.style.get_attr("gutter-height")
        ) / self.nrows
        self.col_width = (
            self.style.get_attr("width")
            - self.style.get_attr("right-margin")
            - self.style.get_attr("left-margin")
            - (self.ncolumns - 1) * self.style.get_attr("gutter-width")
        ) / self.ncolumns
        if self.style.get_attr("gutter-width") > 0:
            self.total_columns = 2 * self.ncolumns - 1
            self.col_gutters = True
        else:
            self.total_columns = self.ncolumns
            self.col_gutters = False
        if self.style.get_attr("gutter-height") > 0:
            self.total_rows = 2 * self.nrows - 1
            self.row_gutters = True
        else:
            self.total_rows = self.nrows
            self.row_gutters = False
        self.tablegrid.rect.set_size(self.contentrect.width, self.contentrect.height)
        self.tablegrid.rect.move_top_left_to(
            Point(self.contentrect.left, self.contentrect.top)
        )
        self.tablegrid.clear()
        ly = self.contentrect.top
        for r in range(self.total_rows):
            if (self.row_gutters and r % 2 == 0) or not self.row_gutters:
                row = TableRow(self.contentrect.width, self.row_height)
                for c in range(self.total_columns):
                    if (self.col_gutters and c % 2 == 0) or not self.col_gutters:
                        cx = (c + 1) / 2
                        title = "%02d%02d" % (r, cx)
                    else:
                        title = "gutter%02d" % (c)
                    w = (
                        self.col_width
                        if c % 2 == 0
                        else self.style.get_attr("gutter-width")
                    )
                    wr = w / self.contentrect.width
                    row.add_column(title, content=None, order=c, width=wr)
                h = self.row_height
                row.rect.move_top_left_to(Point(self.contentrect.left, ly))
                row.compute_cell_sizes("width")
            else:
                row = None
                h = self.style.get_attr("gutter-height")
            hr = h / self.contentrect.height
            self.tablegrid.add_row("%02d" % (r), row, order=r, height=hr)
            ly -= self.row_height
        self.tablegrid.compute_cell_sizes("height")

    def _doc_start(self):
        """ Called by iter_label automatically at document start """
        self.compute_page_metrics()
        self.c = canvas.Canvas(
            self.filename,
            pagesize=(self.style.get_attr("width"), self.style.get_attr("height")),
        )
        self.c.saveState()
        self.page_number = 1

    def _page_end(self):
        """Called by iter_label automatically at page boundaries
        A call to compute_page_metrics is performed to clear the tablegrid
        content containers for a new page
        """
        self.c.showPage()
        self.page_number += 1
        self.compute_page_metrics()

    def _doc_end(self):
        """ Called by iter_label automatically at the end of label document """
        self.c.showPage()
        self.c.save()

    def iter_label(self, labels):
        """Generator which makes the labels based on provided content list.
        It returns the next label data content from the list as well as the row
        and column index of the label.  The caller can then use the row, col index
        to specify the label grid content.  This content can be any derived member
        of ContentRect or TableVector.
        """
        idx = 0
        for i, label in enumerate(labels):
            row, col = self.get_row_col(idx)
            if idx == 0:
                self._doc_start()
            if idx > 0:
                if (idx % self.labels_per_page) == 0:
                    self.tablegrid.draw_in_canvas(self.c)
                    self._page_end()
            yield label, row, col
            idx += 1
            if idx == len(labels):
                self.tablegrid.draw_in_canvas(self.c)
                self._doc_end()
