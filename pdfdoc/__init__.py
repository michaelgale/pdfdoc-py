"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

__project__ = 'pdfdoc'
__version__ = '0.1.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .ldrawpy import *
from .ldrcolour import LDRColour
from .ldrprimitives import LDRAttrib, LDRHeader, LDRLine, LDRTriangle, LDRQuad, LDRPart
