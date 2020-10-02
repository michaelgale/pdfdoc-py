# pdfdoc-py

![python version](https://img.shields.io/static/v1?label=python&message=3.6%2B&color=blue&style=flat&logo=python)
![https://github.com/michaelgale/pdfdoc-py/blob/master/LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>  

Python utility library for compositing PDF documents with reportlab.

## Installation

The **pdfdoc-py** package can be installed directly from the source code:

```shell
    $ git clone https://github.com/michaelgale/pdfdoc-py.git
    $ cd pdfdoc-py
    $ python setup.py install
```

## Usage

After installation, the package can imported:

```shell
    $ python
    >>> import pdfdoc
    >>> pdfdoc.__version__
```

Example of making a label sheet with 25 labels on Avery 5262 self-adhesive label sheets:

```python
from pdfdoc import *

ld = LabelDoc("my_labels.pdf", style=AVERY_5262_LABEL_DOC_STYLE)
labels = [i for i in range(25)]
for label, row, col in ld.iter_label(labels):
    tr = TextRect(withText="Label %d" % (label))
    # tr can be any derived ContentRect or TableVector class
    ld.set_table_cell(tr, row, col)
```



## Requirements

* Python 3.6+
* reportlab
* toolbox-py

## Authors

`pdfdoc-py` was written by [Michael Gale](https://github.com/michaelgale)
