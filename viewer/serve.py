#!/usr/bin/env python3
"""Serve the 3D viewer with automatic rebuilding and live connection to graphify-out/.

Features:
- Automatically rebuilds graph-data.js and graphify-3d-viewer.html on launch.
- Live file server rooted at the project folder so viewer/index.html can read graphify-out/ live.
- Live background watcher that automatically rebuilds when graphify-out changes.
- Automatically opens the default browser.

Usage:
    python serve.py
    python serve.py --port 9000
    python serve.py --no-open
"""
import argparse
import http.server
import os
import sys
import threading
import time
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(ROOT, "graphify-out")
GRAPH = os.path.join(OUT_DIR, "graph.json")
BUILD_MODULE = os.path.join(HERE, "build-data.py")

# Import the builder directly
sys.path.insert(0, HERE)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_data", BUILD_MODULE)
    build_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_data)
except Exception as e:
    build_data = None


class LiveViewerHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching so browser always gets the latest graph
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/viewer/")
            self.end_headers()
            return
        if self.path == "/api/rebuild":
            if build_data:
                build_data.rebuild_data(OUT_DIR, verbose=True)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok","rebuilt":true}')
            else:
                self.send_response(500)
                self.end_headers()
            return
        super().do_GET()

    def log_message(self, format, *args):
        # Quiet standard HTTP request logs
        pass


def watch_and_rebuild():
    """Background watcher for changes in graphify-out folder."""
    last_mtime = 0
    while True:
        time.sleep(2)
        if not os.path.exists(GRAPH):
            continue
        try:
            mtime = os.path.getmtime(GRAPH)
            if mtime != last_mtime:
                last_mtime = mtime
                print("\n[Watcher] Detected changes in graphify-out/graph.json -> Rebuilding 3D model...")
                if build_data:
                    build_data.rebuild_data(OUT_DIR, verbose=True)
                print("[Watcher] Rebuild complete.\n")
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description="Serve the 3D Graph Viewer with live data")
    ap.add_argument("--port", type=int, default=8737, help="Port to serve on (default: 8737)")
    ap.add_argument("--no-open", action="store_true", help="Don't open browser automatically")
    ap.add_argument("--no-watch", action="store_true", help="Disable background directory watcher")
    args = ap.parse_args()

    print("=" * 60)
    print(" 🚀 Initializing 3D Graph Viewer Environment")
    print("=" * 60)

    # 1. Initial build on startup
    if os.path.exists(GRAPH):
        if build_data:
            print("Analyzing graphify-out and building fresh 3D model snapshot...")
            build_data.rebuild_data(OUT_DIR, verbose=True)
    else:
        print(f"Warning: {GRAPH} not found yet. The viewer will use graph-data.js.")

    # 2. Start watcher thread
    if not args.no_watch:
        threading.Thread(target=watch_and_rebuild, daemon=True).start()

    os.chdir(ROOT)
    url = f"http://localhost:{args.port}/viewer/"
    
    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), LiveViewerHandler)
    except OSError as e:
        print(f"Port {args.port} in use, trying port {args.port + 1}...")
        args.port += 1
        url = f"http://localhost:{args.port}/viewer/"
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), LiveViewerHandler)

    print(f"\n Serving root: {ROOT}")
    print(f"  ➜ Local URL: {url}")
    print("  ➜ Standalone file: viewer/graphify-3d-viewer.html")
    print("  ➜ Press Ctrl+C to stop\n")

    if not args.no_open:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nViewer server stopped.")


if __name__ == "__main__":
    main()

