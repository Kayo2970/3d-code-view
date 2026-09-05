# Graphify 3D Viewer

Interactive 3D renderer for the `graphify-out/graph.json` knowledge graph
(1,857 nodes · 5,220 edges from the LEADS ERP codebase + docs).

## Which file to use

| File | Use it for |
|---|---|
| **`graphify-3d-viewer.html`** | **Sharing.** One self-contained file — graph data is baked in. Send it over chat/email/AirDrop and it opens on a phone, tablet, or any computer. Works with no local server. |
| `index.html` + `graph-data.js` | Local development. Keep the two together in this folder. |

Both open by just double-clicking (or tapping on a phone). They download the
3D engine (`three.js` + `3d-force-graph`) from a CDN the **first time** they run,
so the device needs internet on first open; after that the browser caches it.
On a phone the side panels collapse into **☰ Controls** / **▤ Legend** buttons,
and quality defaults to *Performance*. One finger orbits, two fingers zoom/pan,
tap a node to inspect it.

## Live updates (recommended for local use)

```
python serve.py            # serves + opens the browser
python serve.py --watch    # also rebuilds graphify-3d-viewer.html on every change
```

When opened this way the viewer reads `graphify-out/graph.json` **directly** and
polls it every few seconds — so after you run `graphify update .` the graph
refreshes on its own (a full auto-reload). Opened as a plain file instead, it
uses the snapshot in `graph-data.js` and doesn't auto-update.

## Controls

- **Drag** orbit · **scroll** zoom · **click node** inspect + highlight neighbours · **click background** reset
- **Show only this node & what it connects to** (checkbox in the info panel) — collapses the view to just the selected node and its direct links, and **ignores the min/max-degree and legend filters** while active. Click another visible node to walk the graph; untick or click the background to exit.
- **Layout** — *Force cloud* (physics ball) or *Sphere shell* (nodes fixed on a globe, clustered by community)
- **Node spacing** slider — 0.5×–6×; cranks up repulsion + link length (or the sphere radius) to pull a tight cluster apart. The layout re-settles each time you move it.
- **Colour by** — community / file type / extraction origin
- **Show node types** — toggle code / document / concept / rationale / image
- **Legend** — click an entry to hide/show that community or type
- **Min / Max degree** sliders — hide weakly-connected nodes, or hide the giant hub nodes (`apiError`, `requireSession`…) to see the rest of the structure
- **Search** — type a node name or file path, press Enter to fly to the best match
- **Performance** — *Performance / Balanced / High* trades sphere detail + antialiasing + pixel-ratio for frame rate. "Freeze layout once settled" (on by default) stops the physics after ~6 s so orbiting is buttery; **Re-run layout** restarts it. The line under the buttons shows which renderer the browser gave you — if it says "software render", turn on hardware acceleration in your browser settings / check `chrome://gpu`.

## Files

| File | Role |
|---|---|
| `index.html` | the viewer (dev version) |
| `graph-data.js` | baked snapshot of the graph — the offline fallback |
| `graphify-3d-viewer.html` | the shareable single-file build |
| `build-data.py` | regenerates `graph-data.js` **and** `graphify-3d-viewer.html` from `graphify-out/` + `index.html` |
| `serve.py` | local server with live reload against `graphify-out/` |

After `graphify update .`: the live server picks it up automatically. For the
snapshot / shareable file, run `python build-data.py` (or `serve.py --watch`).
