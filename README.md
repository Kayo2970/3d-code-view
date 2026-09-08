# 3d-code-view

Interactive 3D exploration of the **LEADS ERP** codebase as a knowledge graph.

[graphify](https://github.com/) analysed the ERP codebase into `graphify-out/` — **12,517 nodes / 28,491 edges / 698 communities / 10 major hubs** — and `viewer/` renders it as a rich, navigable 3D force graph in any browser.

## Contents

| Path | What it is |
|---|---|
| `viewer/` | The 3D viewer (see [`viewer/README.md`](viewer/README.md) for full docs) |
| `graphify-out/` | graphify output: `graph.json`, `.graphify_analysis.json`, `.graphify_labels.json`, `GRAPH_REPORT.md` |
| `rebuild.py` | One-click script to analyze `graphify-out/` and rebuild the 3D model & bundle |
| `run_viewer.py` / `launch_viewer.bat` | Auto-rebuilds and serves the viewer with live-reload |

## Quick Start

### 1. One-Click Dynamic Launcher (Windows)
Double-click **`launch_viewer.bat`** or run:
```bash
python run_viewer.py
```
This automatically analyzes `graphify-out/`, rebuilds the 3D dataset in 0.2s, starts the local server, and opens your browser to `http://localhost:8737/viewer/`.

### 2. Standalone Shareable Build (No Server Needed)
Just open:
```
viewer/graphify-3d-viewer.html
```
Works directly in any browser (desktop, tablet, or phone) with baked-in graph data.

### 3. Rebuilding the Model Manually
Whenever you update code or re-run `graphify`:
```bash
python rebuild.py
```
This inspects `graphify-out/graph.json`, labels, analysis, and god nodes, immediately updating `viewer/graph-data.js` and `viewer/graphify-3d-viewer.html`.

## Controls

Drag to orbit · scroll to zoom · click a node to inspect it and highlight its neighbours · click the background to reset. Layout, colour-by, node-type toggles, degree filters, and search live in the side panels. Full reference in [`viewer/README.md`](viewer/README.md).

