#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/app/share/leshade
python3 /app/share/leshade/main.py "$@"
