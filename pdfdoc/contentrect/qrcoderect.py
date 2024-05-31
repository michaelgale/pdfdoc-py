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
# QRCodeRect image cell container class derived from ContentRect

import hashlib
import tempfile
import qrcode
import qrcode.image.pil
import qrcode.image.svg
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from toolbox import *
from pdfdoc import *


class QRCodeRect(ContentRect):
    def __init__(
        self,
        w=None,
        h=None,
        qrtext=None,
        style=None,
        dpi=None,
        auto_size=None,
        **kwargs
    ):
        if isinstance(w, (int, float)) and isinstance(h, (int, float)):
            super().__init__(w, h, style)
        else:
            super().__init__(1, 1, style)
        if isinstance(w, str) and qrtext is None:
            self.qrtext = w
        elif qrtext is not None:
            self.qrtext = qrtext
        else:
            self.qrtext = ""
        self.auto_size = auto_size if auto_size is not None else True
        self.dpi = dpi if dpi is not None else 300
        self.border = 4
        self.qr_err_thr = 15
        self.style["background-colour"] = "#FFFFFF"
        self.style["fill-colour"] = "#000000"
        self.format = "svg"
        self.parse_kwargs(**kwargs)
        self._qrimg = None

    def __repr__(self):
        return "%s(%.2f, %.2f, %r)" % (
            self.__class__.__name__,
            self.rect.width,
            self.rect.height,
            self.qrtext,
        )

    def __str__(self):
        s = []
        s.append("QRCodeRect: %s" % (self.rect))
        s.append("  QR text: %s" % (self.qrtext))
        return "\n".join(s)

    @property
    def image_shape(self):
        if self.is_svg:
            return self.qr_image.pixel_size, self.qr_image.pixel_size
        return self.qr_image._img.size

    @property
    def qr_box_size(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=self.qr_err_constant,
            box_size=1,
            border=self.border,
            image_factory=self.qr_factory,
        )
        qr.add_data(self.qrtext)
        qr.make(fit=True)
        sz = qr.modules_count + 2 * self.border
        w, h = self.style.get_inset_rect(self.rect).size
        pix = PTS2PIX(min(w, h), dpi=self.dpi)
        return max(1, int(pix / sz))

    @property
    def qr_err_constant(self):
        if self.qr_err_thr <= 7:
            return qrcode.constants.ERROR_CORRECT_L
        elif self.qr_err_thr <= 15:
            return qrcode.constants.ERROR_CORRECT_M
        elif self.qr_err_thr <= 25:
            return qrcode.constants.ERROR_CORRECT_Q
        return qrcode.constants.ERROR_CORRECT_H

    @property
    def is_svg(self):
        return "svg" in self.format.lower()

    @property
    def qr_factory(self):
        if self.is_svg:
            return qrcode.image.svg.SvgPathImage
        return qrcode.image.pil.PilImage

    @property
    def qr_temp_file(self):
        shash = hashlib.sha1()
        shash.update(bytes(str(self.qrtext), encoding="utf8"))
        return tempfile.gettempdir() + os.sep + shash.hexdigest()[:24]

    @property
    def qr_image(self):
        if self._qrimg is not None:
            return self._qrimg
        qr = qrcode.QRCode(
            version=None,
            error_correction=self.qr_err_constant,
            box_size=self.qr_box_size,
            border=self.border,
            image_factory=self.qr_factory,
        )
        qr.add_data(self.qrtext)
        qr.make(fit=True)
        if self.is_svg:
            colour = (
                rgb_to_hex(self.fill_colour)
                if not isinstance(self.fill_colour, str)
                else self.fill_colour
            )
            qr.image_factory.QR_PATH_STYLE["fill"] = colour
            self._qrimg = qr.make_image()
        else:
            self._qrimg = qr.make_image(
                fill_color=self.style.fill_colour_tuple,
                back_color=self.style.background_colour_tuple,
            )
        self._qrimg.save(self.qr_temp_file)
        return self._qrimg

    def draw_in_canvas(self, c):
        self.snapshot_rect()
        self.draw_rect(c)
        self.draw_image_rect(c)
        self.draw_overlay_content(c)
        if self.show_debug_rects:
            self.draw_debug_rect(c, self.rect)
            self.draw_debug_rect(c, self.inset_rect, (0, 0, 1))
        self.restore_rect()

    def get_content_size(self, with_padding=True):
        if self.qrtext is None:
            return 0, 0
        if self.qrtext == "":
            return 0, 0
        tw, th = PIX2PTS(self.image_shape, self.dpi)
        return super().get_content_size(tw, th, with_padding=with_padding)

    def draw_image_rect(self, c):
        if self.qrtext is None:
            return
        if self.qrtext == "":
            return
        if self.is_svg:
            _ = self.qr_image
            dwg = svg2rlg(self.qr_temp_file)
            (iw, ih) = dwg.minWidth(), dwg.height
            if self.auto_size:
                tw, th = Rect.get_best_rect_metrics(
                    iw, ih, self.inset_width, self.inset_height
                )
            else:
                tw, th = iw, ih
            dwg.scale(tw / iw, th / ih)
            tx, ty = self.aligned_corner(tw, th)
            tx, ty = self.rotated_origin(c, tx, ty)
            renderPDF.draw(dwg, c, tx, ty)
        else:
            (iw, ih) = self.qr_image.size
            if not iw > 0 or not ih > 0:
                return
            if self.auto_size:
                tw, th = Rect.get_best_rect_metrics(
                    iw, ih, self.inset_width, self.inset_height
                )
            else:
                tw, th = PIX2PTS((iw, ih), self.dpi)
            tx, ty = self.aligned_corner(tw, th)
            tx, ty = self.rotated_origin(c, tx, ty)
            c.drawImage(self.qr_temp_file, tx, ty, tw, th, mask="auto")
        if self.style["rotation"]:
            c.restoreState()

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
