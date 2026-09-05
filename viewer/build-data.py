#!/usr/bin/env python3
"""Rebuild viewer/graph-data.js from ../graphify-out/graph.json.

Trims each node/link to the fields the viewer needs, precomputes node degree,
and inlines the community labels so the page needs no fetch()/server.
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "graphify-out"))
GRAPH = os.path.join(OUT_DIR, "graph.json")
LABELS = os.path.join(OUT_DIR, ".graphify_labels.json")
DEST = os.path.join(HERE, "graph-data.js")


def main() -> None:
    with open(GRAPH, encoding="utf-8") as fh:
        graph = json.load(fh)

    labels = {}
    if os.path.exists(LABELS):
        with open(LABELS, encoding="utf-8") as fh:
            labels = json.load(fh)

    degree = collections.Counter()
    for link in graph["links"]:
        degree[link["source"]] += 1
        degree[link["target"]] += 1

    nodes = [
        {
            "id": n["id"],
            "label": n.get("label", ""),
            "ft": n.get("file_type", ""),
            "com": n.get("community", -1),
            "sf": n.get("source_file", ""),
            "loc": n.get("source_location") or "",
            "og": n.get("_origin", ""),
            "k": (n.get("metadata") or {}).get("kind", ""),
            "deg": degree.get(n["id"], 0),
        }
        for n in graph["nodes"]
    ]

    links = [
        {"s": l["source"], "t": l["target"], "r": l.get("relation", ""), "c": l.get("confidence", "")}
        for l in graph["links"]
    ]

    sizes = collections.Counter(n["com"] for n in nodes)
    payload = {
        "meta": {
            "built_at_commit": graph.get("built_at_commit"),
            "n_nodes": len(nodes),
            "n_links": len(links),
        },
        "communityLabels": labels,
        "communitySizes": sizes,
        "nodes": nodes,
        "links": links,
    }

    data_js = "window.GRAPH_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"

    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write(data_js)
    print(f"wrote {DEST}  ({len(nodes)} nodes, {len(links)} links, {os.path.getsize(DEST):,} bytes)")

    # Single-file build: inline the data into the HTML so one file can be shared
    # (e.g. sent to a phone). The 3D library is still pulled from a CDN on first open.
    index_path = os.path.join(HERE, "index.html")
    bundle_path = os.path.join(HERE, "graphify-3d-viewer.html")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as fh:
            html = fh.read()
        marker = '<script src="./graph-data.js"></script>'
        if marker not in html:
            print("  ! could not find graph-data.js <script> tag in index.html; skipped bundle")
            return
        inline = "<script>" + data_js.replace("</", "<\\/") + "</script>"
        html = html.replace(marker, inline, 1)
        with open(bundle_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"wrote {bundle_path}  ({os.path.getsize(bundle_path):,} bytes)  <- share this one")


if __name__ == "__main__":
    main()
