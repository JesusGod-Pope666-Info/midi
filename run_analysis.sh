#!/bin/bash
# Run the analysis
python3 analyze_and_merge.py > analysis_output.txt 2>&1
echo "Analysis complete. Output saved to analysis_output.txt"
cat analysis_output.txt
