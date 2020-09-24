#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# Document container class

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

from fxgeometry import Rect, Point
from pdfdoc import *
from .doccallbacks import DocumentCallback

class Document:
    def __init__(self, filename=None, style=None):
        self.style = DocStyle(style=DEFAULT_MARGINS)
        self.filename = filename if filename is not None else ""
        self.title = None
        self.author = None
        self.subject = None
        self.page_number = 1
        self.section = None
        self.cursor = (0, 0)
        self.page_end_callbacks = None
        self.page_start_callbacks = None
        self.doc_start_callbacks = None
        self.doc_end_callbacks = None
        self.section_start_callbacks = None
        self.section_end_callbacks = None
        self.bleed_rect = Rect(0, 0)
        self.page_rect = Rect(0, 0)
        self.inset_rect = Rect(0, 0)
        self.header_rect = Rect(0, 0)
        self.footer_rect = Rect(0, 0)
        self.c = None
        if style is not None:
            self.style.set_with_dict(style)
        else:
            self.set_page_size(PAGE_LETTER)
        self.section_list = []

    def get_context(self):
        """ Returns a dictionary representing essential document context state."""
        return {
            "canvas": self.c,
            "page_number": self.page_number,
            "cursor": self.cursor,
            "section": self.section,
            "page_rect": self.page_rect,
            "inset_rect": self.inset_rect,
            "header_rect": self.header_rect,
            "footer_rect": self.footer_rect,
            "bleed_rect": self.bleed_rect,
        }

    def set_page_size(self, page_style, orientation=None, with_bleed=None):
        """ Configures size based on supplied page style including
        reversal for landscape vs. portrait orientation."""
        self.style.set_with_dict(page_style)
        if orientation is not None:
            o = orientation
        else:
            o = self.style.get_attr("orientation")
        if o == "landscape":
            self.page_rect.set_size(
                self.style.get_attr("height"), self.style.get_attr("width")
            )
        else:
            self.page_rect.set_size(
                self.style.get_attr("width"), self.style.get_attr("height")
            )
        self.page_rect.move_bottom_left_to((0, 0))
        self.bleed_rect = self.page_rect.copy()
        if with_bleed is not None:
            self.bleed_rect = self.bleed_rect.expanded_by(with_bleed)
            self.bleed_rect.move_bottom_left_to((0, 0))
            self.page_rect.move_bottom_left_to((with_bleed, with_bleed))
        self.inset_rect = self.style.get_inset_rect(self.page_rect)
        r = self.page_rect
        ri = self.inset_rect
        self.header_rect = Rect()
        self.header_rect.set_points((ri.left, r.top), (ri.right, ri.top))
        self.footer_rect = Rect()
        self.footer_rect.set_points((ri.left, ri.bottom), (ri.right, r.bottom))

    def set_author(self, author):
        self.author = author

    def set_title(self, title):
        self.title = title

    def set_subject(self, subject):
        self.subject = subject

    # Convenience accessors for page geometry

    def get_remaining_height(self):
        return self.cursor[1] - self.inset_rect.bottom

    def get_top_left(self, with_margins=True):
        """ Returns the coordinate of the top left corner of the page or content region."""
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.left, r.top

    def get_bottom_left(self, with_margins=True):
        """ Returns the coordinate of the bottom left corner of the page or content region."""
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.left, r.bottom

    def get_top_right(self, with_margins=True):
        """ Returns the coordinate of the top right corner of the page or content region."""
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.right, r.top

    def get_bottom_right(self, with_margins=True):
        """ Returns the coordinate of the bottom right corner of the page or content region."""
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.right, r.bottom

    def _cursor_top_left(self, with_margins=True):
        """ Moves document coordinate pointer to top left of content region."""
        self.cursor = self.get_top_left(with_margins=with_margins)

    def _cursor_top_right(self, with_margins=True):
        """ Moves document coordinate pointer to top right of content region."""
        self.cursor = self.get_top_right(with_margins=with_margins)

    def _cursor_bottom_left(self, with_margins=True):
        """ Moves document coordinate pointer to bottom left of content region."""
        self.cursor = self.get_bottom_left(with_margins=with_margins)

    def _cursor_bottom_right(self, with_margins=True):
        """ Moves document coordinate pointer to bottom right of content region."""
        self.cursor = self.get_bottom_right(with_margins=with_margins)

    def _cursor_shift_down(self, yoffset):
        """ Shifts the global coordinate pointer down. """
        self.cursor = (self.cursor[0], self.cursor[1] - yoffset)

    def _get_next_section(self):
        if self.section_list is None:
            return None
        n_sections = len(self.section_list)
        if n_sections > 0:
            for i, e in enumerate(self.section_list):
                if e == self.section:
                    if i < n_sections - 1:
                        return self.section_list[i + 1]
                    else:
                        return self.section_list[0]
        return None

    # Document control actions

    def page_break(self, new_page_number=None):
        self._page_end(new_page_number=new_page_number)
        self._page_start()

    def section_break(self, new_section=None, page_break=True, new_page_number=None):
        self._process_callbacks(self.section_end_callbacks)
        if page_break:
            self._page_end(new_page_number=new_page_number)
        if new_section is not None:
            self.section = new_section
        else:
            self.section = self._get_next_section()
        self._section_start()
        if page_break:
            self._page_start(new_page_number=new_page_number)
        else:
            if new_page_number is not None:
                self.page_number = new_page_number

    def change_section(self, new_section=None):
        self.section_break(new_section=new_section, page_break=False)

    def end_document(self):
        self._doc_end()

    # Automated document control actions/callbacks

    def _process_callbacks(self, callbacks):
        def z_order_key(e):
            return e.z_order

        all_callbacks = []
        if isinstance(callbacks, list):
            for callback in callbacks:
                if callback is not None:
                    if isinstance(callback, list):
                        all_callbacks.extend(callback)
                    else:
                        all_callbacks.append(callback)
        else:
            if callbacks is not None:
                all_callbacks = [callbacks]
        ordered = sorted(all_callbacks, key=z_order_key)
        for callback in ordered:
            if isinstance(callback, DocumentCallback):
                if callback.is_enabled(self.get_context()):
                    callback.render(self.get_context())
            elif callable(callback):
                callback()

    def _doc_start(self):
        """ Initialize state for document creation start. """
        self.c = canvas.Canvas(
            self.filename, pagesize=(self.bleed_rect.width, self.bleed_rect.height)
        )
        if self.author is not None:
            self.c.setAuthor(self.author)
        if self.title is not None:
            self.c.setTitle(self.title)
        if self.subject is not None:
            self.c.setSubject(self.subject)
        self.c.saveState()
        self.page_number = 1
        if self.section_list is not None:
            if len(self.section_list) > 0:
                self.section = self.section_list[0]
        self._process_callbacks([self.doc_start_callbacks, self.page_start_callbacks])
        self._cursor_top_left()

    def _doc_end(self):
        """ Close document session and save file. """
        self._process_callbacks([self.page_end_callbacks, self.doc_end_callbacks])
        self.c.showPage()
        self.c.save()
        self.c = None

    def _section_start(self):
        self._process_callbacks(self.section_start_callbacks)

    def _page_start(self, new_page_number=None):
        """ Configure state for the start of a new page. """
        if new_page_number is not None:
            self.page_number = new_page_number
        self._process_callbacks(self.page_start_callbacks)
        self._cursor_top_left()

    def _page_end(self, new_page_number=None):
        """ Peform actions to end this page and start a new page."""
        self._process_callbacks(self.page_end_callbacks)
        self.c.showPage()
        if new_page_number is not None:
            self.page_number = new_page_number
        else:
            self.page_number += 1

    def iter_doc(self, blocks):
        """ Generator which yields sequential content generation based on the
        caller's iteration intervals as arbitrary blocks."""
        self._doc_start()
        for block in blocks:
            # check for pre-mature end of document
            if self.c is None:
                break
            yield block, self.get_context()
        # guard against already terminated document
        if self.c is not None:
            self._doc_end()
