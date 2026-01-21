#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/app/share/reshade-installer
python3 /app/share/reshade-installer/gui.py "$@"
