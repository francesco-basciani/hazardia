"""Build the reviewed flood road segment inventory from a frozen OSM extract."""
import argparse
import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

from hazardia.io import load, write_new
from hazardia.web.traffic import graph_from_osm


def prepare(osm, request, output):
    raw = osm.read_bytes()
    bounds = load(request)["territory"]["bbox_wgs84"]
    root = ET.fromstring(raw)
    graph = graph_from_osm(root, bounds, edge_limit=40_000)
    tags = {way.get("id"): {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
            for way in root.findall("way")}
    for edge in graph["edges"]:
        attrs = tags[edge["way"]]
        edge["structure"] = {key: attrs[key] for key in ("bridge", "viaduct", "tunnel", "covered", "layer")
                             if attrs.get(key) not in (None, "no", "0", "false")}
    if not graph["edges"]:
        raise ValueError("No eligible roads found in the simulation bounds")
    write_new(output, dict(graph, schema="hazardia.flood-road-depth/1", raw_sha256=hashlib.sha256(raw).hexdigest()))
    print(len(graph["edges"]), "directed road segments")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("osm", "request", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    prepare(args.osm, args.request, args.output)
