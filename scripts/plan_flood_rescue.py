"""Bounded rescue exercise on archived OSM arcs and the six native flood maps."""
import argparse
from collections import Counter
from itertools import product
import math
from pathlib import Path
import sys

from hazardia.flood_access import adjacency, assess_edge, path_from, shortest_tree
from hazardia.io import load, sha256, write_new

# Inventories and times are exercise assumptions. Nodes identify mapped road
# points, not calls, people, actual depots or an operating medical facility.
BASE = "738159103"
THRESHOLD_M = .10
PICKUP_MIN = 8
HANDOFF_MIN = 4
VEHICLES = [
    dict(id="V1", name="Veicolo leggero", ready=60, capacity=2, speed_kmh=30),
    dict(id="V2", name="Minibus", ready=120, capacity=4, speed_kmh=25),
]
CALLS = [
    dict(id="R1", name="SS 615 · richiesta ordinaria", node="738159401", people=2,
         priority="ordinary", release=55, deadline=300),
    dict(id="R2", name="Via Mariana · richiesta prioritaria", node="5437648796", people=2,
         priority="critical", release=60, deadline=180),
    dict(id="R3", name="SS 615 · gruppo di quattro", node="738159177", people=4,
         priority="ordinary", release=120, deadline=240),
    dict(id="R4", name="SS 615 · seconda richiesta", node="5530049189", people=2,
         priority="ordinary", release=180, deadline=300),
]


def route_geometry(arcs, edges):
    return [edges[arcs[0]]["a"], *[edges[arc]["b"] for arc in arcs]] if arcs else []


def build(folder, roads_file):
    import rasterio
    from hazardia.flood_road_depth import RoadDepth

    series = load(folder / "frames.json")
    roads = load(roads_file)
    edges = {edge["id"]: edge for edge in roads["edges"]}
    nodes = {edge["u"]: edge["a"] for edge in edges.values()}
    demands = [dict(call, point=nodes[call["node"]]) for call in CALLS]
    candidates = []
    assessments = []
    base_routes = {}
    for frame in series["frames"]:
        hour = frame["index"]
        minute = hour * 60
        path = folder / frame["raster"]
        assert sha256(path) == frame["raster_sha256"]
        with rasterio.open(path) as ds:
            depth = RoadDepth(ds)
            support = {}
            states = {}
            for key, edge in edges.items():
                segment = key.rsplit(":", 1)[0]
                if segment not in support:
                    support[segment] = depth.segment(edge["a"], edge["b"])
                state, reason = assess_edge(dict(edge, **support[segment]), THRESHOLD_M)
                states[key] = dict(state=state, reason=reason, **support[segment])
            points = {item["id"]: depth.point(item["point"]) for item in demands}
        opened = [edge for key, edge in edges.items() if states[key]["state"] == "open"]
        graph = adjacency(opened)
        from_base = shortest_tree(graph, BASE)
        calls = {}
        for demand in demands:
            outbound = path_from(from_base, demand["node"])
            back = path_from(shortest_tree(graph, demand["node"]), BASE) if outbound is not None else None
            arcs = outbound["arcs"] + back["arcs"] if back is not None else None
            if hour == 0:
                base_routes[demand["id"]] = arcs
            blockers = [key for key in base_routes[demand["id"]] or [] if states[key]["state"] != "open"]
            calls[demand["id"]] = dict(round_trip=arcs is not None, depth=points[demand["id"]],
                                      reference_blockers=blockers,
                                      blocker_geometry=[dict(a=edges[key]["a"], b=edges[key]["b"],
                                                             name=edges[key]["name"], id=key,
                                                             **states[key]) for key in blockers])
            if arcs is None:
                continue
            length = outbound["distance_m"] + back["distance_m"]
            for vehicle in VEHICLES:
                travel = math.ceil(length / (vehicle["speed_kmh"] * 1000 / 60))
                delivery = minute + travel + PICKUP_MIN + HANDOFF_MIN
                if (minute < max(vehicle["ready"], demand["release"]) or vehicle["capacity"] < demand["people"]
                        or delivery > min(minute + 60, demand["deadline"])):
                    continue
                candidates.append(dict(id=f'{vehicle["id"]}-{demand["id"]}-{hour}', vehicle=vehicle["id"],
                    call=demand["id"], hour=hour, departure=minute, delivery=delivery, distance_m=length,
                    travel_min=travel, outbound=outbound["arcs"], back=back["arcs"],
                    outbound_line=route_geometry(outbound["arcs"], edges),
                    return_line=route_geometry(back["arcs"], edges)))
        assessments.append(dict(hour=hour, calls=calls, states=states,
                                counts=dict(Counter(value["state"] for value in states.values()))))
    write_new(folder / "road-assessments.json", assessments)
    write_new(folder / "rescue-problem.json", dict(schema="hazardia.flood-rescue-problem/1",
        qualification="SYNTHETIC_RESEARCH_REQUESTS_AND_FLEET", source_roads_sha256=sha256(roads_file),
        assessments_sha256=sha256(folder / "road-assessments.json"), frames_sha256=sha256(folder / "frames.json"),
        base=nodes[BASE], base_node=BASE, calls=demands, vehicles=VEHICLES, options=candidates,
        threshold_m=THRESHOLD_M, pickup_min=PICKUP_MIN, handoff_min=HANDOFF_MIN))


def score(missions, problem):
    calls = {call["id"]: call for call in problem["calls"]}
    critical = sum(calls[m["call"]]["people"] for m in missions if calls[m["call"]]["priority"] == "critical")
    people = sum(calls[m["call"]]["people"] for m in missions)
    return critical, people, -sum(m["travel_min"] for m in missions)


def solve(folder):
    import highspy

    problem = load(folder / "rescue-problem.json")
    options = problem["options"]
    h = highspy.Highs()
    for key, value in (("output_flag", False), ("threads", 1), ("time_limit", 5.0), ("random_seed", 1729)):
        assert h.setOptionValue(key, value) == highspy.HighsStatus.kOk
    variables = {item["id"]: h.addVariable(lb=0, ub=1, type=highspy.HighsVarType.kInteger, name=item["id"])
                 for item in options}
    for call in problem["calls"]:
        h.addConstr(h.qsum(variables[item["id"]] for item in options if item["call"] == call["id"]) <= 1)
    for vehicle, hour in sorted({(item["vehicle"], item["hour"]) for item in options}):
        h.addConstr(h.qsum(variables[item["id"]] for item in options
                          if (item["vehicle"], item["hour"]) == (vehicle, hour)) <= 1)
    calls = {call["id"]: call for call in problem["calls"]}
    stages = [
        lambda item: calls[item["call"]]["people"] if calls[item["call"]]["priority"] == "critical" else 0,
        lambda item: calls[item["call"]]["people"],
        lambda item: -item["travel_min"],
    ]
    for index, coefficient in enumerate(stages):
        expr = h.qsum(coefficient(item) * variables[item["id"]] for item in options)
        h.maximize(expr)
        assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal
        if index < len(stages) - 1:
            h.addConstr(expr == round(h.getObjectiveValue()))
    optimal = [item for item in options if h.val(variables[item["id"]]) > .5]
    fifo = []
    booked = set()
    for item in sorted(options, key=lambda m: (m["departure"], calls[m["call"]]["release"],
                                               m["delivery"], m["vehicle"], m["call"])):
        slot = item["vehicle"], item["hour"]
        if slot not in booked and all(m["call"] != item["call"] for m in fifo):
            fifo.append(item)
            booked.add(slot)
    plans = [dict(id=name, missions=missions, objective=score(missions, problem))
             for name, missions in (("none", []), ("fifo", fifo), ("optimized", optimal))]
    write_new(folder / "plans.json", dict(solver="HiGHS " + h.version(), termination="OPTIMAL",
                                         problem_sha256=sha256(folder / "rescue-problem.json"), plans=plans))


def verify(folder, roads_file):
    problem = load(folder / "rescue-problem.json")
    plans = load(folder / "plans.json")
    frames = load(folder / "frames.json")
    observations = load(folder / "road-assessments.json")
    assert plans["problem_sha256"] == sha256(folder / "rescue-problem.json")
    assert problem["assessments_sha256"] == sha256(folder / "road-assessments.json")
    assert problem["frames_sha256"] == sha256(folder / "frames.json")
    assert problem["source_roads_sha256"] == sha256(roads_file)
    edges = {edge["id"]: edge for edge in load(roads_file)["edges"]}
    calls = {call["id"]: call for call in problem["calls"]}
    vehicles = {vehicle["id"]: vehicle for vehicle in problem["vehicles"]}
    options = {item["id"]: item for item in problem["options"]}
    for mission in options.values():
        call = calls[mission["call"]]
        vehicle = vehicles[mission["vehicle"]]
        hour = mission["hour"]
        assert mission["departure"] == hour * 60 >= max(call["release"], vehicle["ready"])
        assert vehicle["capacity"] >= call["people"]
        distance = 0
        for leg, start, end in (("outbound", problem["base_node"], call["node"]),
                                ("back", call["node"], problem["base_node"])):
            at = start
            for key in mission[leg]:
                edge = edges[key]
                assert edge["u"] == at and observations[hour]["states"][key]["state"] == "open"
                distance += edge["length"]
                at = edge["v"]
            assert at == end
        assert math.isclose(distance, mission["distance_m"], abs_tol=1e-8)
        assert mission["travel_min"] == math.ceil(distance / (vehicle["speed_kmh"] * 1000 / 60))
        assert mission["delivery"] == mission["departure"] + mission["travel_min"] + PICKUP_MIN + HANDOFF_MIN
        assert mission["delivery"] <= min((hour + 1) * 60, call["deadline"])

    def feasible(items):
        return (len({item["call"] for item in items}) == len(items)
                and len({(item["vehicle"], item["hour"]) for item in items}) == len(items))

    best = (0, 0, 0)
    checked = 0
    for selection in product(*[[None, *[item for item in options.values() if item["call"] == call]]
                               for call in calls]):
        items = [item for item in selection if item is not None]
        if feasible(items):
            checked += 1
            best = max(best, score(items, problem))
    for plan in plans["plans"]:
        assert all(options.get(item["id"]) == item for item in plan["missions"])
        assert feasible(plan["missions"]) and tuple(plan["objective"]) == score(plan["missions"], problem)
    assert tuple(plans["plans"][-1]["objective"]) == best
    assert observations[1]["calls"]["R2"]["round_trip"] and not observations[2]["calls"]["R2"]["round_trip"]
    assert observations[2]["calls"]["R2"]["depth"]["depth_m"] == 0
    assert any(edge["state"] == "closed" for edge in observations[2]["calls"]["R2"]["blocker_geometry"])
    assert plans["plans"][1]["objective"][:2] == [0, 8] and plans["plans"][2]["objective"][:2] == [2, 10]
    write_new(folder / "audit.json", dict(status="PASS", feasible_schedules_checked=checked,
                                          routes_verified=len(options), optimum=best, hourly_maps=len(frames["frames"])))
    write_new(folder / "view.json", dict(schema="hazardia.flood-rescue-view/1",
        **{key: value for key, value in frames.items() if key != "schema"},
        problem={key: value for key, value in problem.items() if key not in ("options", "schema")},
        plans=plans["plans"], solver=plans["solver"],
        roads=[{key: value for key, value in hour.items() if key != "states"} for hour in observations]))


if __name__ == "__main__":
    if sys.platform != "linux":
        raise RuntimeError("Use the existing Linux VM")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["build", "solve", "verify"])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--roads", type=Path)
    args = parser.parse_args()
    if args.stage == "solve":
        solve(args.folder)
    else:
        if args.roads is None:
            parser.error("--roads required")
        {"build": build, "verify": verify}[args.stage](args.folder, args.roads)
