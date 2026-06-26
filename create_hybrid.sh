#!/bin/bash
# MAIN EXECUTION SCRIPT
# Run this to create the hybrid KAR file

cd "$(dirname "$0")" || exit

python3 hybrid_kar_creator.py
exit $?
