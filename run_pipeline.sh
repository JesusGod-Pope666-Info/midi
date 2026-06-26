#!/bin/bash
# Run the complete analysis and hybrid KAR creation pipeline

echo "=========================================="
echo "KAR File Analysis & Hybrid Creation"
echo "=========================================="
echo ""

echo "Step 1: Analyzing SK and ME files..."
python3 analyze_and_merge.py
echo ""

echo "=========================================="
echo ""
echo "Step 2: Creating hybrid KAR file..."
python3 create_hybrid_kar.py
echo ""

echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="
echo ""
echo "Files created:"
ls -lh *.kar *.txt 2>/dev/null | grep -E "(HYBRID|analysis)"
