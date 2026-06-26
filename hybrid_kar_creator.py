#!/usr/bin/env python3
"""
MAIN EXECUTION SCRIPT - Hybrid KAR File Creator
Creates a hybrid KAR file combining SK (Soft Karaoke) and ME (MIDI Events) formats
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*100}")
    print(f"{description}")
    print(f"{'='*100}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed")
        return False

def main():
    print("\n")
    print("╔" + "="*98 + "╗")
    print("║" + " "*20 + "HYBRID KAR FILE CREATOR - SK + ME MERGER" + " "*36 + "║")
    print("╚" + "="*98 + "╝")
    print()
    
    # Check if input files exist
    sk_file = Path('Our_Gods_are_an_awesome_God_En x2SKforAI.kar')
    me_file = Path('Our_Gods_are_an_awesome_God_En x2MEforAI.kar')
    
    if not sk_file.exists():
        print(f"❌ SK file not found: {sk_file.name}")
        print("   Please ensure the SK KAR file is in this directory")
        return False
    
    if not me_file.exists():
        print(f"❌ ME file not found: {me_file.name}")
        print("   Please ensure the ME KAR file is in this directory")
        return False
    
    print(f"✓ SK file found: {sk_file.name} ({sk_file.stat().st_size:,} bytes)")
    print(f"✓ ME file found: {me_file.name} ({me_file.stat().st_size:,} bytes)")
    print()
    
    # Run analysis
    if not run_command('python3 analyze_and_merge.py', 'STEP 1: ANALYZING SK AND ME FILES'):
        return False
    
    # Run hybrid creation
    if not run_command('python3 create_hybrid_kar.py', 'STEP 2: CREATING HYBRID KAR FILE'):
        return False
    
    # Show results
    print(f"\n{'='*100}")
    print("PIPELINE COMPLETE ✓")
    print(f"{'='*100}\n")
    
    hybrid_file = Path('Our_Gods_are_an_awesome_God_En_HYBRID.kar')
    if hybrid_file.exists():
        size = hybrid_file.stat().st_size
        print(f"✓ Hybrid KAR file created successfully!")
        print(f"  File: {hybrid_file.name}")
        print(f"  Size: {size:,} bytes")
        print()
        print("The hybrid file contains:")
        print("  • All SK metadata and lyrics")
        print("  • All ME MIDI events and notes")
        print("  • Combined timing information")
        print("  • Compatible with both SK and ME players")
        print()
        return True
    else:
        print("❌ Hybrid file was not created")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
