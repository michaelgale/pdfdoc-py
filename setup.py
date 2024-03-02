#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Learn more: https://github.com/michaelgale/pdfdoc-py

import os
import os.path
from pathlib import Path
import sys
import setuptools

PACKAGE_NAME = "pdfdoc"
MINIMUM_PYTHON_VERSION = "3.7"

dependency_links = []

def read_package_variable(key, filename="__init__.py"):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(" ", 2)
            if parts[:-1] == [key, "="]:
                return parts[-1].strip("'")
    sys.exit("'{0}' not found in '{1}'".format(key, module_path))

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setuptools.setup(
    name=read_package_variable("__project__"),
    version=read_package_variable("__version__"),
    description="Python utility library for compositing PDF documents with reportlab.",
    url="https://github.com/michaelgale/pdfdoc-py",
    author="Michael Gale",
    author_email="michael@fxbricks.com",
    packages=setuptools.find_packages(),
    package_data = { "": ["*.svg", "*.png"], },
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["reportlab", "pdfrw"],
    entry_points={
        "console_scripts": [
            "fourup=pdfdoc.scripts.fourup:main",
            "fullbleed=pdfdoc.scripts.fullbleed:main",
            "text2outlines=pdfdoc.scripts.text2outlines:main",
        ]
    }
)
