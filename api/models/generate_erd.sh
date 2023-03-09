#!/bin/bash
# Note that you need to install dev dependencies for this script to work
python ../../manage.py graph_models --output erd.dot --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api
dot -Tpng erd.dot -o erd.png
rm erd.dot
