"""Replay road accessibility on saved HMC–REFlEx maximum-depth products in Linux."""
import argparse
from collections import Counter
import math
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET

import rasterio
from pyproj import Geod
from shapely.geometry import shape

from hazardia.flood_access import compare_access
from hazardia.flood_road_depth import METHOD, RoadDepth
from hazardia.io import load, sha256, utcnow, write_new
from hazardia.web.traffic import graph_from_osm

GEO = Geod(ellps="WGS84")
SNAP_LIMIT_M = 150


def road_graph(source, bounds):
    """Adapt cached OSM JSON to the same parser used by the visual traffic layer."""
    root = ET.Element("osm")
    tags_by_way = {}
    for item in source["elements"]:
        kind = item["type"]
        tags = item.get("tags", {})
        if kind == "way" and "highway" not in tags:
            continue
        if kind == "relation" and tags.get("type") != "restriction":
            continue
        node = ET.SubElement(root, kind, id=str(item["id"]))
        if kind == "node":
            node.set("lat", str(item["lat"]))
            node.set("lon", str(item["lon"]))
        if kind == "way":
            tags_by_way[str(item["id"])] = tags
            for ref in item["nodes"]:
                ET.SubElement(node, "nd", ref=str(ref))
        if kind == "relation":
            for member in item["members"]:
                ET.SubElement(node, "member", type=member["type"], ref=str(member["ref"]))
        for key, value in tags.items():
            ET.SubElement(node, "tag", k=key, v=value)
    graph = graph_from_osm(root, bounds, edge_limit=40_000)
    for edge in graph["edges"]:
        tags = tags_by_way[edge["way"]]
        edge["name"] = tags.get("name") or tags.get("ref")
        edge["structure"] = {
            key: tags[key] for key in ("bridge", "viaduct", "tunnel", "covered", "layer")
            if tags.get(key) not in (None, "no", "0", "false")
        }
    return graph


def endpoints(features, categories, graph, depth):
    nodes = {edge["u"]: edge["a"] for edge in graph}
    nodes.update({edge["v"]: edge["b"] for edge in graph})
    result = []
    for feature in features:
        prop = feature["properties"]
        if prop.get("category") not in categories or not prop.get("name"):
            continue
        position = shape(feature["geometry"]).representative_point()
        point = [position.x, position.y]
        lon, lat = point
        distance, node = min(
            (GEO.inv(lon, lat, *coordinate)[2], node) for node, coordinate in nodes.items()
        )
        accepted = distance <= SNAP_LIMIT_M
        result.append(dict(id=feature["id"], name=prop["name"], category=prop["category"],
                           point=point, source=prop.get("source"), depth=depth.point(point),
                           node=node if accepted else None, snapped_point=nodes[node] if accepted else None,
                           snap_distance_m=distance))
    return sorted(result, key=lambda entry: (entry["name"], entry["id"]))


def default_pair(pairs, origins):
    """Show an affected dry locality first if one exists. All pairs remain available."""
    rank = {"interrupted": 0, "detour": 1, "indeterminate": 2,
            "available": 3, "no_reference": 4, "unsnapped": 5}
    dry = {origin["id"] for origin in origins if origin["depth"]["depth_m"] == 0}
    return min(range(len(pairs)), key=lambda i: (rank[pairs[i]["status"]],
                                                 pairs[i]["origin"] not in dry, i))


def replay(root, output, job_id, graph, territory, thresholds, source):
    if not re.fullmatch(r"job-[a-f0-9]{32}", job_id):
        raise ValueError("Invalid job identifier")
    job = root / "jobs" / job_id
    product_file = job / "product.json"
    product = load(product_file)
    if product["hazard"] != "FLOOD" or product["job_id"] != job_id:
        raise ValueError("Expected saved flood product")
    layer = next(layer for layer in product["layers"] if layer["name"] == "MAXIMUM_DEPTH")
    if layer["unit"] != "m" or layer["path"] != "products/maximum-depth.tif":
        raise ValueError("Unsupported flood product layer")
    raster = job / layer["path"]
    if sha256(raster) != layer["sha256"]:
        raise ValueError("Flood depth checksum mismatch")
    catalog = load(root / "web-assets/catalog.json")
    scenario = next(item for item in catalog["scenarios"] if item["id"] == job_id)
    with rasterio.open(raster) as dataset:
        depth = RoadDepth(dataset)
        grid = dict(crs=dataset.crs.to_string(), shape=list(dataset.shape), transform=list(dataset.transform)[:6])
        declared = product["grid"]
        if (grid["crs"] != declared["crs"] or grid["shape"] != declared["shape"]
                or not all(math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12)
                           for actual, expected in zip(grid["transform"], declared["transform"]))):
            raise ValueError("Flood depth grid does not match published product")
        hydraulic = dict(job_id=job_id, layer=layer, product_sha256=sha256(product_file),
                         catalog_sha256=scenario["reference"]["sha256"], grid=grid, nodata=dataset.nodata,
                         mask_flags=[flag.name for flag in dataset.mask_flag_enums[0]],
                         valid_from=product["valid_from"], valid_until=product["valid_until"],
                         support="window_maximum", engine=product["engine"],
                         qualification=product["qualification"], overlay=scenario["overlay"],
                         bounds=scenario["bounds"], assumptions=product["assumptions"])
        support = {}
        roads = []
        for edge in graph["edges"]:
            segment = edge["id"].rsplit(":", 1)[0]
            if segment not in support:
                support[segment] = depth.segment(edge["a"], edge["b"])
            roads.append(dict(edge, **support[segment]))
        origins = endpoints(territory["features"], {"settlement"}, roads, depth)
        destinations = endpoints(territory["features"], {"hospital", "clinic", "doctors"}, roads, depth)
    if not origins or not destinations:
        raise ValueError("No mapped settlement–healthcare pairs in the input inventory")
    replays = [compare_access(roads, origins, destinations, threshold) for threshold in thresholds]
    summary = []
    view_replays = []
    visible_ids = set()
    for result in replays:
        pairs = result["pairs"]
        for pair in pairs:
            for key in ("reference", "scenario", "possible"):
                if pair[key] is not None:
                    visible_ids.update(pair[key]["arcs"])
        summary.append(dict(threshold_m=result["threshold_m"], pairs=dict(Counter(p["status"] for p in pairs)),
                            edges=dict(Counter(e["state"] for e in result["edges"].values()))))
    # Retain all edge assessments in the audit product. The map only needs
    # edges on candidate paths, including the uncertain optimistic witnesses.
    for result in replays:
        view_replays.append(dict(result, edges={k: v for k, v in result["edges"].items() if k in visible_ids},
                                 default_pair=default_pair(result["pairs"], origins)))
    network = dict(source, bounds=graph["bounds"], directed_arcs=len(roads), counts=graph["counts"],
                   assumptions=graph["missing"], restriction_policy=graph["restriction_policy"],
                   snap_limit_m=SNAP_LIMIT_M)
    output.mkdir()
    write_new(output / "hydraulic.json", hydraulic)
    write_new(output / "road-depth.json", dict(schema="hazardia.flood-road-depth/1", method=METHOD, network=network,
                                               hydraulic_sha256=sha256(output / "hydraulic.json"), edges=roads))
    write_new(output / "routing.json", dict(schema="hazardia.flood-access-routing/1",
                                            road_depth_sha256=sha256(output / "road-depth.json"), origins=origins,
                                            destinations=destinations, replays=replays, summary=summary))
    write_new(output / "view.json", dict(schema="hazardia.flood-access-view/1", hydraulic=hydraulic, network=network,
                                         origins=origins, destinations=destinations, replays=view_replays, summary=summary,
                                         edges={edge["id"]: edge for edge in roads if edge["id"] in visible_ids},
                                         method=METHOD))
    print(job_id, summary, flush=True)


def main():
    if sys.platform != "linux":
        raise RuntimeError("Use the existing Linux VM for scientific replay")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New immutable replay directory")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--territory", type=Path, required=True)
    parser.add_argument("--job", action="append", required=True)
    parser.add_argument("--threshold", action="append", type=float, required=True)
    args = parser.parse_args()
    if len(args.job) > 10 or len(args.threshold) > 10 or any(
        not math.isfinite(value) or value <= 0 for value in args.threshold
    ):
        parser.error("Use at most 10 products and 10 positive finite thresholds")
    if shutil.disk_usage(args.root).free < 2 * 1024**3 + 128 * 1024**2:
        parser.error("Insufficient disk headroom above the VM reserve")
    source = load(args.osm)
    territory = load(args.territory)
    bounds = [source["bounds"][key] for key in ("minlon", "minlat", "maxlon", "maxlat")]
    if territory["source_sha256"] != sha256(args.osm) or bounds != territory["coverage_bbox_wgs84"]:
        raise ValueError("Road and endpoint snapshots do not share the same OSM extract")
    metadata = dict(osm_sha256=sha256(args.osm), territory_sha256=sha256(args.territory),
                    source_url=territory["source_url"], source_data_at=territory.get("source_data_at"),
                    source_available_at=territory.get("source_available_at"),
                    attribution="© OpenStreetMap contributors", license="ODbL-1.0")
    args.output.mkdir(exist_ok=False)
    write_new(args.output / "protocol.json", dict(run_id=args.output.name, created_at=utcnow(),
              inputs=metadata, jobs=args.job, thresholds_m=args.threshold, script_sha256=sha256(Path(__file__)),
              association=METHOD, hypothesis="A dry mapped locality may have a route affected by flood depth",
              qualification="RESEARCH_SCENARIO", geometry="CACHED_OSM", snap_limit_m=SNAP_LIMIT_M))
    graph = road_graph(source, bounds)
    for job in args.job:
        replay(args.root, args.output / job, job, graph, territory, args.threshold, metadata)


if __name__ == "__main__":
    main()
