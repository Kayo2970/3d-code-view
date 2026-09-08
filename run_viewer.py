#!/usr/bin/env python3
"""Root-level launcher to auto-rebuild and serve the 3D Graph Viewer.

Usage:
    python run_viewer.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVE_SCRIPT = os.path.join(HERE, "viewer", "serve.py")

if __name__ == "__main__":
    if not os.path.exists(SERVE_SCRIPT):
        print(f"Error: {SERVE_SCRIPT} not found.")
        sys.exit(1)
    
    import subprocess
    sys.exit(subprocess.call([sys.executable, SERVE_SCRIPT] + sys.argv[1:], cwd=os.path.dirname(SERVE_SCRIPT)))
