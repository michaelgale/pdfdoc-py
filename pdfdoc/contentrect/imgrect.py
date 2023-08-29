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
# ImageRect image cell container class derived from ContentRect

from toolbox import *
from pdfdoc import *


class ImageRect(ContentRect):
    def __init__(
        self,
        w=None,
        h=None,
        filename=None,
        style=None,
        dpi=None,
        auto_size=None,
        **kwargs
    ):
        if isinstance(w, (int, float)) and isinstance(h, (int, float)):
            super().__init__(w, h, style)
        else:
            super().__init__(1, 1, style)
        if isinstance(w, str) and filename is None:
            self.filename = w
        else:
            self.filename = filename
        self.auto_size = auto_size if auto_size is not None else True
        self.dpi = dpi if dpi is not None else 300
        self.parse_kwargs(**kwargs)

    def __repr__(self):
        return "%s(%.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
            self.filename,
        )

    def __str__(self):
        s = []
        s.append("ImageRect: %s" % (self.rect))
        s.append("  filename: %s" % (self.filename))
        return "\n".join(s)

    @property
    def image_shape(self):
        return get_image_metrics(self.filename)

    def draw_in_canvas(self, c):
        self.draw_rect(c)
        self.draw_image_rect(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(c, inset_rect, (0, 0, 1))

    def get_content_size(self, with_padding=True):
        if self.filename is None:
            return 0, 0
        if self.filename == "":
            return 0, 0
        tw, th = PIX2PTS(get_image_metrics(self.filename), self.dpi)
        return super().get_content_size(tw, th, with_padding=with_padding)

    def draw_image_rect(self, c):
        if self.filename is None:
            return
        if self.filename == "":
            return
        (iw, ih) = get_image_metrics(self.filename)
        if not iw > 0 or not ih > 0:
            return
        inset_rect = self.style.get_inset_rect(self.rect)
        if self.auto_size:
            tw, th = Rect.get_best_rect_metrics(
                iw, ih, inset_rect.width, inset_rect.height
            )
        else:
            tw, th = PIX2PTS((iw, ih), self.dpi)
        tx, ty = self.aligned_corner(tw, th)
        c.setFillColor(rl_colour((0, 0, 0)))
        c.drawImage(self.filename, tx, ty, tw, th, mask="auto")

    def convert_rect_to_pix(self, rect):
        """Converts a passed rect into the pixel coordinates of this image."""
        pl = clamp_value(rect.left, self.rect.left, self.rect.right)
        pr = clamp_value(rect.right, self.rect.left, self.rect.right)
        pt = clamp_value(rect.top, self.rect.bottom, self.rect.top)
        pb = clamp_value(rect.bottom, self.rect.bottom, self.rect.top)
        iw, ih = self.image_shape
        pl = int((pl - self.rect.left) / self.rect.width * iw)
        pr = int((pr - self.rect.left) / self.rect.width * iw)
        pt = ih - int((pt - self.rect.bottom) / self.rect.height * ih)
        pb = ih - int((pb - self.rect.bottom) / self.rect.height * ih)
        return Rect.rect_from_points((pl, pt), (pr, pb))

    @staticmethod
    def from_preset(name, **kwargs):
        """Returns an instance of ImageRect from a named preset graphic included
        in this package."""
        if not name.endswith(".png"):
            name = name + ".png"
        presets = ImageRect.list_presets()
        for preset in presets:
            _, pf = split_path(preset)
            if pf == name:
                return ImageRect(filename=preset, **kwargs)
            
    @staticmethod
    def list_presets():
        fp, _ = split_path(__file__)
        fp = fp + os.sep + ".." + os.sep + "graphics"
        fs = FileOps()
        return fs.get_file_list(fp, "*.png", recursive=True)
