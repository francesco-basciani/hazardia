"""Distance routing for a bounded directed graph under a flood scenario."""
from collections import defaultdict
from heapq import heappop, heappush
import math

METRIC = "sum_of_road_segment_lengths_m"


def assess_edge(observation, threshold_m):
    if observation["structure"]:
        return "unknown", "structure_depth_unqualified"
    maximum = observation["max_depth_m"]
    if maximum is not None and maximum >= threshold_m:
        return "closed", "maximum_at_or_above_threshold"
    coverage = observation["coverage"]
    if coverage["outside"] > 0:
        return "unknown", "outside_grid"
    if coverage["nodata"] > 0:
        return "unknown", "nodata"
    return "open", "full_valid_coverage_below_threshold"


def adjacency(edges):
    graph = defaultdict(list)
    for edge in sorted(edges, key=lambda edge: edge["id"]):
        graph[edge["u"]].append(edge)
    return graph


def shortest_tree(graph, start):
    distance = {start: 0.0}
    previous = {}
    pending = [(0.0, start)]
    while pending:
        length, node = heappop(pending)
        if length != distance[node]:
            continue
        for edge in graph.get(node, ()):
            other = edge["v"]
            candidate = length + edge["length"]
            if candidate < distance.get(other, math.inf):
                distance[other] = candidate
                previous[other] = edge
                heappush(pending, (candidate, other))
    return distance, previous


def path_from(tree, destination):
    distance, previous = tree
    if destination not in distance:
        return None
    arcs = []
    current = destination
    while current in previous:
        edge = previous[current]
        arcs.append(edge["id"])
        current = edge["u"]
    return dict(distance_m=distance[destination], arcs=list(reversed(arcs)))


def compare_access(edges, origins, destinations, threshold_m):
    """Return reference, verified and optimistic paths with identical endpoints."""
    if not math.isfinite(threshold_m) or threshold_m <= 0:
        raise ValueError("Threshold must be finite and positive")
    statuses = {edge["id"]: assess_edge(edge, threshold_m) for edge in edges}
    graphs = (
        adjacency(edges),
        adjacency(edge for edge in edges if statuses[edge["id"]][0] == "open"),
        adjacency(edge for edge in edges if statuses[edge["id"]][0] != "closed"),
    )
    pairs = []
    for origin in origins:
        trees = [shortest_tree(graph, origin["node"]) for graph in graphs] if origin["node"] is not None else None
        for destination in destinations:
            result = dict(origin=origin["id"], destination=destination["id"], reference=None,
                          scenario=None, possible=None, explanatory_arcs=[])
            if trees is None or destination["node"] is None:
                result["status"] = "unsnapped"
            else:
                reference, verified, optimistic = [path_from(tree, destination["node"]) for tree in trees]
                result["reference"] = reference
                result["scenario"] = verified
                if reference is None:
                    result["status"] = "no_reference"
                elif verified is not None:
                    # Prefer the same reference path when it is fully evaluated,
                    # including equal-length alternatives.
                    changed = [arc for arc in reference["arcs"] if statuses[arc][0] != "open"]
                    result["status"] = "detour" if changed else "available"
                    result["scenario"] = verified if changed else reference
                elif optimistic is not None:
                    result["status"] = "indeterminate"
                    result["possible"] = optimistic
                else:
                    result["status"] = "interrupted"
                if reference:
                    witnesses = [arc for arc in reference["arcs"] if statuses[arc][0] != "open"]
                    if result["possible"]:
                        witnesses.extend(arc for arc in optimistic["arcs"] if statuses[arc][0] == "unknown")
                    result["explanatory_arcs"] = list(dict.fromkeys(witnesses))
            pairs.append(result)
    return dict(threshold_m=threshold_m, metric=METRIC, pairs=pairs,
                edges={key: dict(state=state, reason=reason) for key, (state, reason) in statuses.items()})
