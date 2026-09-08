# Graphify 3D Viewer

Interactive 3D renderer for the `graphify-out/` knowledge graph
(**12,517 nodes · 28,491 edges · 698 communities · 10 hubs** from the codebase).

## Which file to use

| File | Use it for |
|---|---|
| **`graphify-3d-viewer.html`** | **Sharing & Offline.** One self-contained file — graph data is baked in. Send it over chat/email/AirDrop and it opens on a phone, tablet, or any computer. Works with no local server. |
| `index.html` + `graph-data.js` | Local development. Keep the two together in this folder. |

Both open by double-clicking (or tapping on a phone). They download the
3D engine (`three.js` + `3d-force-graph`) from a CDN on first open, then cache it.

## Live Updates & Auto-Rebuilding (Recommended)

From the project root:
```bash
python run_viewer.py
```
or double-click `launch_viewer.bat` on Windows.

When launched:
1. It immediately inspects `graphify-out/`, detects new nodes/edges/communities/god-nodes, and regenerates `graph-data.js` and `graphify-3d-viewer.html`.
2. Serves the viewer with anti-cache headers and opens your browser.
3. Automatically watches `graphify-out/` in the background and re-syncs if `graph.json` changes.

## Manual Rebuilding

If you ran `graphify` and just want to refresh the datasets:
```bash
python rebuild.py
```
or from inside `viewer/`:
```bash
python build-data.py
```

## Controls

- **Drag** orbit · **scroll** zoom · **click node** inspect + highlight neighbours · **click background** reset
- **Show only this node & what it connects to** (checkbox in info panel) — isolates the node and direct links.
- **Layout** — *Force cloud* (physics ball) or *Sphere shell* (clustered by community on a globe)
- **Node spacing** slider — expands repulsion / link length.
- **Colour by** — community / file type / extraction origin
- **Show node types** — toggle code / document / concept / rationale / image
- **Legend** — click an entry to hide/show that community or type
- **Min / Max degree** sliders — filter weakly-connected nodes or major hubs
- **Search** — type a node name or file path, press Enter to fly to the best match

