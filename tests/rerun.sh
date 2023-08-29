#!/usr/bin/env bash
# rm ~/Dropbox/Lego/PartCache/Thumbnails/*
cd ..
pip install .
cd tests
pytest -s -v
