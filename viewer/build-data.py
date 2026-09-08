#!/usr/bin/env python3
"""Rebuild viewer/graph-data.js and viewer/graphify-3d-viewer.html from graphify-out/.

Analyzes:
- graphify-out/graph.json (nodes & links)
- graphify-out/.graphify_labels.json (community labels)
- graphify-out/.graphify_analysis.json (god nodes, cohesion, architecture insights)
- graphify-out/manifest.json (indexed source files)

Trims each node/link to essential viewer fields, precomputes degrees and hub status,
inlines community labels and metadata, and creates the single-file offline bundle.
"""
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(ROOT, "graphify-out")
GRAPH_PATH = os.path.join(OUT_DIR, "graph.json")
LABELS_PATH = os.path.join(OUT_DIR, ".graphify_labels.json")
ANALYSIS_PATH = os.path.join(OUT_DIR, ".graphify_analysis.json")
MANIFEST_PATH = os.path.join(OUT_DIR, "manifest.json")
DEST_JS = os.path.join(HERE, "graph-data.js")
INDEX_HTML = os.path.join(HERE, "index.html")
BUNDLE_HTML = os.path.join(HERE, "graphify-3d-viewer.html")


def rebuild_data(graph_dir: str = OUT_DIR, verbose: bool = True) -> bool:
    graph_file = os.path.join(graph_dir, "graph.json")
    labels_file = os.path.join(graph_dir, ".graphify_labels.json")
    analysis_file = os.path.join(graph_dir, ".graphify_analysis.json")
    manifest_file = os.path.join(graph_dir, "manifest.json")

    if not os.path.exists(graph_file):
        if verbose:
            print(f"Error: {graph_file} does not exist.")
        return False

    t0 = time.time()
    if verbose:
        print(f"Analyzing graphify output in: {graph_dir} ...")

    with open(graph_file, encoding="utf-8") as fh:
        graph = json.load(fh)

    # 1. Labels
    labels = {}
    if os.path.exists(labels_file):
        try:
            with open(labels_file, encoding="utf-8") as fh:
                labels = json.load(fh)
        except Exception as e:
            if verbose:
                print(f"  Warning: failed reading labels: {e}")

    # 2. Analysis (god nodes, cohesion, surprises)
    god_nodes = set()
    cohesion_map = {}
    if os.path.exists(analysis_file):
        try:
            with open(analysis_file, encoding="utf-8") as fh:
                analysis = json.load(fh)
                if isinstance(analysis, dict):
                    gods_raw = analysis.get("gods", [])
                    if isinstance(gods_raw, list):
                        for g in gods_raw:
                            if isinstance(g, str):
                                god_nodes.add(g)
                            elif isinstance(g, dict) and "id" in g:
                                god_nodes.add(g["id"])
                    cohesion_map = analysis.get("cohesion", {})
        except Exception as e:
            if verbose:
                print(f"  Warning: failed reading analysis: {e}")

    # 3. Compute node degree & link index
    degree = collections.Counter()
    valid_links = []
    for link in graph.get("links", []):
        src = link.get("source")
        tgt = link.get("target")
        if src and tgt:
            degree[src] += 1
            degree[tgt] += 1
            valid_links.append(link)

    # Top degree nodes automatically count as hubs if god nodes wasn't specified
    if not god_nodes and degree:
        top_hubs = [nid for nid, _ in degree.most_common(25)]
        god_nodes = set(top_hubs)

    # 4. Filter and normalize nodes
    raw_nodes = graph.get("nodes", [])
    nodes = []
    for n in raw_nodes:
        nid = n.get("id")
        if not nid:
            continue
        meta = n.get("metadata") or {}
        deg = degree.get(nid, 0)
        is_god = nid in god_nodes
        nodes.append({
            "id": nid,
            "label": n.get("label", nid),
            "ft": n.get("file_type", "code"),
            "com": n.get("community", -1) if n.get("community") is not None else -1,
            "sf": n.get("source_file", ""),
            "loc": n.get("source_location") or "",
            "og": n.get("_origin", "ast"),
            "k": meta.get("kind", ""),
            "deg": deg,
            "god": 1 if is_god else 0,
        })

    links = [
        {
            "s": l["source"],
            "t": l["target"],
            "r": l.get("relation", ""),
            "c": l.get("confidence", "")
        }
        for l in valid_links
    ]

    sizes = collections.Counter(n["com"] for n in nodes)
    
    # Summary meta
    meta = {
        "built_at_commit": graph.get("built_at_commit", ""),
        "built_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_nodes": len(nodes),
        "n_links": len(links),
        "n_communities": len(sizes),
        "n_gods": len([n for n in nodes if n.get("god")]),
    }

    payload = {
        "meta": meta,
        "communityLabels": labels,
        "communitySizes": sizes,
        "cohesion": cohesion_map,
        "godNodes": list(god_nodes),
        "nodes": nodes,
        "links": links,
    }

    data_js = "window.GRAPH_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"

    with open(DEST_JS, "w", encoding="utf-8") as fh:
        fh.write(data_js)
    
    elapsed = time.time() - t0
    if verbose:
        print(f"Generated {DEST_JS}")
        print(f"  Nodes: {len(nodes):,} | Links: {len(links):,} | Communities: {len(sizes)} | Hubs: {len(god_nodes)}")
        print(f"  Size: {os.path.getsize(DEST_JS):,} bytes in {elapsed:.2f}s")

    # Rebuild single-file HTML bundle
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, encoding="utf-8") as fh:
            html = fh.read()
        marker = '<script src="./graph-data.js"></script>'
        if marker in html:
            inline = "<script>" + data_js.replace("</", "<\\/") + "</script>"
            bundle_html = html.replace(marker, inline, 1)
            with open(BUNDLE_HTML, "w", encoding="utf-8") as fh:
                fh.write(bundle_html)
            if verbose:
                print(f"Generated standalone 3D viewer: {BUNDLE_HTML} ({os.path.getsize(BUNDLE_HTML):,} bytes)")
        elif verbose:
            print("  Warning: could not find graph-data.js script marker in index.html")

    return True


def main() -> None:
    target_dir = sys.argv[1] if len(sys.argv) > 1 else OUT_DIR
    rebuild_data(target_dir)


if __name__ == "__main__":
    main()

