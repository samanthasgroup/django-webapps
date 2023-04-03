#!/bin/bash
# Note that you need to install dev dependencies for this script to work
python ../../manage.py graph_models --output erd.dot --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api
dot -Tpng erd.dot -o erd.png
rm erd.dot

# now the small graph (with verbose names) for the "core" models: personal info and roles
python ../../manage.py graph_models --output erd_core.dot --verbose-names -I PersonalInfo,Coordinator,Student,Teacher --theme django2018 --layout fdp --rankdir TB --arrow crow --verbosity 2 api
dot -Tpng erd_core.dot -o erd_core.png
rm erd_core.dot
