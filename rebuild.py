#!/usr/bin/env python3
"""Root-level shortcut to analyze graphify-out/ and rebuild the 3D Graph Viewer.

Usage:
    python rebuild.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_SCRIPT = os.path.join(HERE, "viewer", "build-data.py")

if __name__ == "__main__":
    if not os.path.exists(BUILD_SCRIPT):
        print(f"Error: {BUILD_SCRIPT} not found.")
        sys.exit(1)
    
    import subprocess
    sys.exit(subprocess.call([sys.executable, BUILD_SCRIPT] + sys.argv[1:], cwd=os.path.dirname(BUILD_SCRIPT)))
