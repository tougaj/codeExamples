#!/usr/bin/env bash

# rm dest/*.*

source venv/bin/activate
python3 cut_represents.py
deactivate
