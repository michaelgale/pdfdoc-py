"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

__project__ = 'pdfdoc'
__version__ = '0.1.0'

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .docstyle import DocStyle
from .tablerow import TableRow
from .tablecolumn import TableColumn
from .textrect import TextRect
from .imgrect import ImageRect
from .tablecell import TableCell, TableVector
from .contentrect import ContentRect
from .pdfdoc import *
