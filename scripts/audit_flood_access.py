"""Check replay paths against SciPy and independently overlay witness cells in Linux."""
from collections import Counter
import argparse
import math
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import LineString, box

from hazardia.io import load, sha256, write_new


def audit(job, folder):
    h = load(folder / "hydraulic.json")
    road_file = folder / "road-depth.json"
    roads = load(road_file)
    routing = load(folder / "routing.json")
    assert sha256(job / "product.json") == h["product_sha256"]
    assert sha256(job / h["layer"]["path"]) == h["layer"]["sha256"]
    assert roads["hydraulic_sha256"] == sha256(folder / "hydraulic.json")
    assert routing["road_depth_sha256"] == sha256(road_file)
    edges = {edge["id"]: edge for edge in roads["edges"]}
    ids = {node: i for i, node in enumerate(sorted({e[k] for e in edges.values() for k in ("u", "v")}))}
    origins = {p["id"]: p for p in routing["origins"]}
    destinations = {p["id"]: p for p in routing["destinations"]}
    for edge in edges.values():
        assert math.isclose(sum(edge["coverage"].values()), 1, abs_tol=1e-12)

    checks = []
    witnesses = set()
    for replay in routing["replays"]:
        states = {key: value["state"] for key, value in replay["edges"].items()}
        matrices = []
        for allowed in ({"open", "unknown", "closed"}, {"open"}, {"open", "unknown"}):
            weights = {}
            for edge_id, edge in edges.items():
                if states[edge_id] in allowed:
                    pair = ids[edge["u"]], ids[edge["v"]]
                    weights[pair] = min(weights.get(pair, math.inf), edge["length"])
            ij = list(zip(*weights))
            graph = csr_matrix((list(weights.values()), tuple(ij)), shape=(len(ids), len(ids)))
            matrices.append(dijkstra(graph, directed=True, indices=[ids[o["node"]] for o in origins.values()]))
        counts = Counter()
        for pair in replay["pairs"]:
            origin = origins[pair["origin"]]
            destination = destinations[pair["destination"]]
            row = list(origins).index(origin["id"])
            col = ids[destination["node"]]
            ref, verified, optimistic = [matrix[row, col] for matrix in matrices]
            if not np.isfinite(ref):
                expected = "no_reference"
            elif np.isfinite(verified):
                expected = "available" if all(states[k] == "open" for k in pair["reference"]["arcs"]) else "detour"
            elif np.isfinite(optimistic):
                expected = "indeterminate"
            else:
                expected = "interrupted"
            assert pair["status"] == expected
            counts[expected] += 1
            for key, length in (("reference", ref), ("scenario", verified), ("possible", optimistic)):
                path = pair[key]
                if path is None:
                    assert key == "possible" or not np.isfinite(length)
                    continue
                assert math.isclose(path["distance_m"], length, abs_tol=1e-8)
                node = origin["node"]
                measured = 0
                for edge_id in path["arcs"]:
                    edge = edges[edge_id]
                    assert edge["u"] == node
                    node = edge["v"]
                    measured += edge["length"]
                    assert key == "reference" or states[edge_id] != "closed"
                    assert key != "scenario" or states[edge_id] == "open"
                assert node == destination["node"] and math.isclose(measured, length, abs_tol=1e-8)
            witnesses.update(pair["explanatory_arcs"])
        checks.append(dict(threshold_m=replay["threshold_m"], pairs=dict(counts),
                           arcs=dict(Counter(states.values()))))

    # Native grid is EPSG:4326, so the line in pixel coordinates can be
    # independently intersected with the raster domain and individual cells.
    with rasterio.open(job / h["layer"]["path"]) as raster:
        assert raster.crs.to_string() == "EPSG:4326"
        array = raster.read(1, masked=True)
        assert int(array.count()) == h["layer"]["statistics"]["valid_cells"]
        tested = witnesses | {key for key, status in routing["replays"][0]["edges"].items() if status["state"] == "closed"}
        for key in sorted(tested):
            edge = edges[key]
            line = LineString([(~raster.transform) * edge[p] for p in ("a", "b")])
            assert line.length > 0
            x, y, X, Y = line.bounds
            coverage = dict(valid=0.0, nodata=0.0, outside=1 -
                            line.intersection(box(0, 0, raster.width, raster.height)).length / line.length)
            maximum = None
            for row in range(max(0, math.floor(y)), min(raster.height, math.floor(Y) + 1)):
                for col in range(max(0, math.floor(x)), min(raster.width, math.floor(X) + 1)):
                    fraction = line.intersection(box(col, row, col + 1, row + 1)).length / line.length
                    if fraction <= 1e-10:
                        continue
                    if np.ma.is_masked(array[row, col]):
                        coverage["nodata"] += fraction
                    else:
                        coverage["valid"] += fraction
                        value = float(array[row, col])
                        maximum = value if maximum is None else max(maximum, value)
            assert maximum == edge["max_depth_m"]
            assert all(math.isclose(coverage[k], edge["coverage"][k], abs_tol=1e-8) for k in coverage)
    return dict(job_id=job.name, thresholds=checks, geometry_checks=len(tested), witness_arcs=len(witnesses),
                hydraulic_sha256=h["layer"]["sha256"], routing_sha256=sha256(folder / "routing.json"))


def main():
    if sys.platform != "linux":
        raise RuntimeError("Use the Linux VM for scientific audit")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("replay", type=Path)
    args = parser.parse_args()
    checks = [audit(args.runtime / "jobs" / folder.name, folder)
              for folder in sorted(args.replay.glob("job-*"))]
    assert checks
    write_new(args.replay / "audit.json", dict(status="PASS", jobs=checks))


if __name__ == "__main__":
    main()
