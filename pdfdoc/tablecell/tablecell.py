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
# TableCell and TableVector container classes

from toolbox import *
from pdfdoc import *


class TableCell:
    def __init__(
        self,
        label,
        content=None,
        order=0,
        width=AUTO_SIZE,
        height=AUTO_SIZE,
        constraints=None,
    ):
        self.label = label
        # If no content is provided, create a placeholder ContentRect
        if content is not None:
            self.content = content
        else:
            self.content = ContentRect(width, height)
        self.order = order
        # width and height are specified as ratios between 0 and 1 and
        # not in absolute units. These values are used by parent TableVector
        # classes to compute absolute dimensions relative to peers in the
        # same row or column
        self.width = width
        self.height = height
        self.visible = True
        self.constraints = []
        if constraints is not None:
            self.constraints = constraints

    def __repr__(self):
        return "%s(%r, %r, %.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.label,
            self.order,
            self.width,
            self.height,
            self.constraints,
        )
