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
# Document container class

from reportlab.pdfgen import canvas

from toolbox import *
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
        self.num_columns = 1
        self.column = 1
        self.page_end_callbacks = None
        self.page_start_callbacks = None
        self.doc_start_callbacks = None
        self.doc_end_callbacks = None
        self.section_start_callbacks = None
        self.section_end_callbacks = None
        self.column_start_callbacks = None
        self.column_end_callbacks = None
        self.bleed_rect = Rect(0, 0)
        self.page_rect = Rect(0, 0)
        self.inset_rect = Rect(0, 0)
        self.header_rect = Rect(0, 0)
        self.footer_rect = Rect(0, 0)
        self.column_rects = [Rect(0, 0)]
        self.gutter_rects = []
        self.c = None
        if style is not None:
            self.style.set_with_dict(style)
        else:
            self.set_page_size(PAGE_LETTER)
        self.section_list = []
        self.chapter = 1

    def _callbacks_str(self, title, callbacks):
        s = []
        s.append(title)
        if callbacks is not None:
            for callback in callbacks:
                s.append("    %r  z-order : %d" % (callback, callback.z_order))
                if callback.sections_active is not None:
                    s.append("      Sections Active : %s" % (callback.sections_active))
                if callback.pages_active is not None:
                    s.append("      Pages Active    : %s" % (callback.pages_active))
                if len(callback.section_exclusions) > 0:
                    s.append(
                        "      Section Exc     : %s" % (callback.section_exclusions)
                    )
                if len(callback.page_exclusions) > 0:
                    s.append("      Page Exc        : %s" % (callback.page_exclusions))
        return "\n".join(s)

    def __str__(self):
        s = []
        s.append("Document Class : %r" % (self))
        s.append("  Filename : %-32s Title   : %s" % (self.filename, self.title))
        s.append("  Author   : %-32s Subject : %s" % (self.author, self.subject))
        s.append("  Columns  : %d" % (self.num_columns))
        s.append("  Page Metrics :")
        s.append("    Bleed  : %s" % (self.bleed_rect))
        s.append("    Page   : %s" % (self.page_rect))
        s.append("    Inset  : %s" % (self.inset_rect))
        s.append("    Header : %s" % (self.header_rect))
        s.append("    Footer : %s" % (self.footer_rect))
        for i, col in enumerate(self.column_rects, 1):
            s.append("    Column %d : %s" % (i, col))
        s.append("  Section List :")
        for section in self.section_list:
            s.append("    %s" % (section))
        s.append(
            self._callbacks_str(
                "  Document Start Callbacks :", self.doc_start_callbacks
            )
        )
        s.append(
            self._callbacks_str("  Document End Callbacks :", self.doc_end_callbacks)
        )
        s.append(
            self._callbacks_str(
                "  Section Start Callbacks :", self.section_start_callbacks
            )
        )
        s.append(
            self._callbacks_str("  Section End Callbacks :", self.section_end_callbacks)
        )
        s.append(
            self._callbacks_str("  Page Start Callbacks :", self.page_start_callbacks)
        )
        s.append(self._callbacks_str("  Page End Callbacks :", self.page_end_callbacks))
        s.append(
            self._callbacks_str(
                "  Column Start Callbacks :", self.column_start_callbacks
            )
        )
        s.append(
            self._callbacks_str("  Column End Callbacks :", self.column_end_callbacks)
        )
        s.append(
            "  Section : %s  Chapter : %d  Page : %d  Column : %d  Cursor : %s"
            % (self.section, self.chapter, self.page_number, self.column, self.cursor)
        )
        return "\n".join(s)

    def get_context(self):
        """ Returns a dictionary representing essential document context state."""
        return {
            "canvas": self.c,
            "page_number": self.page_number,
            "cursor": self.cursor,
            "section": self.section,
            "column": self.column,
            "chapter": self.chapter,
            "num_columns": self.num_columns,
            "page_rect": self.page_rect,
            "inset_rect": self.inset_rect,
            "header_rect": self.header_rect,
            "footer_rect": self.footer_rect,
            "bleed_rect": self.bleed_rect,
            "column_rects": self.column_rects,
            "gutter_rect": None
            if self.column >= self.num_columns
            else self.gutter_rects[self.column - 1],
            "column_rect": self.column_rects[
                min(self.column - 1, self.num_columns - 1)
            ],
        }

    def set_page_size(self, page_style, orientation=None, with_bleed=None):
        """Configures size based on supplied page style including
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
        self.set_columns(self.num_columns)

    def set_columns(self, num_columns):
        self.num_columns = num_columns
        num_gutters = num_columns - 1
        self.gutter_rects = []
        self.column_rects = []
        gw = self.style.get_attr("gutter-width")
        cw = (self.inset_rect.width - (num_columns - 1) * gw) / num_columns
        for column in range(num_columns):
            cx = self.inset_rect.left + column * (cw + gw)
            crect = Rect(cw, self.inset_rect.height)
            crect.move_top_left_to((cx, self.inset_rect.top))
            self.column_rects.append(crect)
            if column > 0:
                grect = Rect(gw, self.inset_rect.height)
                grect.move_top_left_to((cx - gw, self.inset_rect.top))
                self.gutter_rects.append(grect)

    def is_portrait(self):
        return True if self.page_rect.height > self.page_rect.width else False

    def is_landscape(self):
        return True if self.page_rect.height < self.page_rect.width else False

    def set_author(self, author):
        self.author = author

    def set_title(self, title):
        self.title = title

    def set_subject(self, subject):
        self.subject = subject

    # Convenience accessors for page geometry

    def get_column_width(self):
        return self.column_rects[self.column - 1].width

    def get_remaining_height(self):
        return self.cursor[1] - self.inset_rect.bottom

    def get_remaining_width(self):
        return self.inset_rect.right - self.cursor[0]

    def is_enough_height(self, for_height):
        return for_height < self.get_remaining_height()

    def is_enough_width(self, for_width):
        return for_width < self.get_remaining_width()

    def is_enough_space(self, for_space):
        if self.is_portrait():
            return self.is_enough_height(for_space)
        else:
            return self.is_enough_width(for_space)

    def get_current_column_rect(self):
        return self.column_rects[self.column - 1]

    def is_cursor_at_column_start(self):
        x, y = self.get_top_left(in_column=True)
        if self.cursor[0] == x and self.cursor[1] == y:
            return True
        return False

    def get_top_left(self, with_margins=True, in_column=False):
        """ Returns the coordinate of the top left corner of the page or content region."""
        if in_column:
            return self.get_current_column_rect().get_top_left()
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.left, r.top

    def get_bottom_left(self, with_margins=True, in_column=False):
        """ Returns the coordinate of the bottom left corner of the page or content region."""
        if in_column:
            return self.get_current_column_rect().get_bottom_left()
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.left, r.bottom

    def get_top_right(self, with_margins=True, in_column=False):
        """ Returns the coordinate of the top right corner of the page or content region."""
        if in_column:
            return self.get_current_column_rect().get_top_right()
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.right, r.top

    def get_bottom_right(self, with_margins=True, in_column=False):
        """ Returns the coordinate of the bottom right corner of the page or content region."""
        if in_column:
            return self.get_current_column_rect().get_bottom_right()
        r = (
            self.style.get_inset_rect(self.page_rect)
            if with_margins
            else self.page_rect
        )
        return r.right, r.bottom

    def cursor_top_left(self, with_margins=True, column=None):
        """ Moves document coordinate pointer to top left of content region."""
        if column is not None:
            if column - 1 < self.num_columns:
                self.cursor = self.column_rects[column - 1].get_top_left()
        else:
            self.cursor = self.get_top_left(with_margins=with_margins)

    def cursor_top_right(self, with_margins=True, column=None):
        """ Moves document coordinate pointer to top right of content region."""
        if column is not None:
            if column - 1 < self.num_columns:
                self.cursor = self.column_rects[column - 1].get_top_right()
        else:
            self.cursor = self.get_top_right(with_margins=with_margins)

    def cursor_bottom_left(self, with_margins=True, column=None):
        """ Moves document coordinate pointer to bottom left of content region."""
        if column is not None:
            if column - 1 < self.num_columns:
                self.cursor = self.column_rects[column - 1].get_bottom_left()
        else:
            self.cursor = self.get_bottom_left(with_margins=with_margins)

    def cursor_bottom_right(self, with_margins=True, column=None):
        """ Moves document coordinate pointer to bottom right of content region."""
        if column is not None:
            if column - 1 < self.num_columns:
                self.cursor = self.column_rects[column - 1].get_bottom_right()
        else:
            self.cursor = self.get_bottom_right(with_margins=with_margins)

    def cursor_shift_down(self, yoffset):
        """ Shifts the global coordinate pointer down. """
        self.cursor = (self.cursor[0], self.cursor[1] - yoffset)

    def cursor_shift_across(self, xoffset):
        self.cursor = (self.cursor[0] + xoffset, self.cursor[1])

    def cursor_auto_shift(self, offset):
        if self.is_enough_height(offset):
            self.cursor_shift_down(offset)
        else:
            self.column_break()

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
                        return self.section_list[i]
        return None

    def is_last_section(self):
        if self.section_list is None:
            return False
        return self.section == self.section_list[-1]

    # Document control actions

    def column_break(self):
        if self.column < self.num_columns:
            self._process_callbacks(self.column_end_callbacks)
            self.column += 1
            self.cursor_top_left(column=self.column)
            self._process_callbacks(self.column_start_callbacks)
        else:
            self.page_break()

    def page_break(self, new_page_number=None):
        self._page_end(new_page_number=new_page_number)
        self._page_start()

    def section_break(
        self,
        new_section=None,
        page_break=True,
        new_page_number=None,
        column_break=False,
    ):
        self._process_callbacks(self.section_end_callbacks)
        if page_break:
            self._page_end(new_page_number=new_page_number)
        elif column_break:
            self.column_break()
        if new_section is not None:
            ns = new_section
        else:
            ns = self._get_next_section()
        if self.section == ns:
            return
        else:
            self.section = ns
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

    def start_document(self):
        self._doc_start()

    # Automated document control actions/callbacks

    def _process_callbacks(self, callbacks):
        def z_order_key(e):
            if "z_order" in e.__dict__:
                return e.z_order
            return 0

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
        self._process_callbacks([self.doc_start_callbacks, self.section_start_callbacks, self.page_start_callbacks])
        self.cursor_top_left()

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
        self.column = 1
        self._process_callbacks(self.column_start_callbacks)
        self.cursor_top_left()

    def _page_end(self, new_page_number=None):
        """ Peform actions to end this page and start a new page."""
        self._process_callbacks(self.page_end_callbacks)
        self.c.showPage()
        if new_page_number is not None:
            self.page_number = new_page_number
        else:
            self.page_number += 1

    def iter_doc(self, blocks):
        """Generator which yields sequential content generation based on the
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
