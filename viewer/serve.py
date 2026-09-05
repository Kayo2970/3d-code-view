#!/usr/bin/env python3
"""Serve the 3D viewer with a live connection to graphify-out/.

Static file server rooted at the project folder, so viewer/index.html can read
../graphify-out/graph.json directly instead of the baked snapshot. The page polls
that file and reloads itself whenever graphify rewrites it, so this is all you
need after `graphify update .`:

    python serve.py            # serve + open the browser
    python serve.py --watch    # also rebuild the shareable single-file bundle on each change
    python serve.py --port 9000 --no-open

Stop with Ctrl+C.
"""
import argparse
import http.server
import os
import subprocess
import sys
import threading
import time
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
BUILD = os.path.join(HERE, "build-data.py")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # never cache — the viewer needs to see graph.json change
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, *_):
        pass


def watch_and_build():
    last = os.path.getmtime(GRAPH) if os.path.exists(GRAPH) else 0
    while True:
        time.sleep(2)
        try:
            m = os.path.getmtime(GRAPH)
        except OSError:
            continue
        if m != last:
            last = m
            print("* graph.json changed - rebuilding graph-data.js + graphify-3d-viewer.html")
            subprocess.run([sys.executable, BUILD], cwd=HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8737)
    ap.add_argument("--watch", action="store_true", help="rebuild the shareable bundle on every change")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(GRAPH):
        print(f"warning: {GRAPH} not found — the viewer will fall back to graph-data.js")

    if args.watch:
        threading.Thread(target=watch_and_build, daemon=True).start()

    os.chdir(ROOT)
    url = f"http://localhost:{args.port}/viewer/"
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"serving {ROOT}")
    print(f"  {url}")
    print("  the viewer reads graphify-out/graph.json live and reloads itself when it changes")
    print("  Ctrl+C to stop")
    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
