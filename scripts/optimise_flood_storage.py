"""Optimise use of one storage unit over independent hourly REFlEx maps."""
import argparse
import csv
from datetime import datetime
from itertools import chain
import math
from pathlib import Path
import shutil

import rasterio

from hazardia.flood_access import assess_edge
from hazardia.flood_road_depth import RoadDepth
from hazardia.io import load, sha256, write_new
from replay_flood_frames import render_frame

VOLUME_STEP_M3 = 100


def schedule(options, capacity):
    """Exact knapsack over the declared, conservatively rounded volume units."""
    budget = math.floor(capacity / VOLUME_STEP_M3)
    states = {0: (0, 0, ())}
    for hour, cost, roads_saved, cells_saved, rate in options:
        updated = dict(states)
        for used, (roads, cells, hours) in states.items():
            next_used = used + cost
            if next_used > budget:
                continue
            choice = roads + roads_saved, cells + cells_saved, hours + ((hour, rate),)
            if choice > updated.get(next_used, (0, 0, ())):
                updated[next_used] = choice
        states = updated
    return max(states.items(), key=lambda entry: (*entry[1][:2], -entry[0]))[1][2]


def optimise(job, replay, roads, study, output):
    view = load(study / "view.json")
    baseline = next(case for case in view["cases"] if case["id"] == view["baseline"])
    protocol = load(study / "protocol.json")
    source = load(replay / "frames.json")
    assert view["job_id"] == source["job_id"] == job.name
    assert sha256(roads) == protocol["roads_sha256"]
    assert sha256(replay / "frames.json") == protocol["source_frames_sha256"]
    assert all(sha256(job / file) == digest for file, digest in load(replay / "protocol.json")["inputs"].items())
    runtime = load(job / "runtime.json")
    settings = load(job / "flood-work/settings.json")
    native = job / "flood-work"
    engine = load(replay / "protocol.json")["engine_files"]
    assert all(sha256(Path(file)) == digest for file, digest in engine.items())
    segments = {e["id"].rsplit(":", 1)[0]: e for e in load(roads)["edges"] if not e["structure"]}
    capacity, rate = view["capacity_m3"], view["capture_m3_s"]
    # Predeclared domain: hours with closures in the no-intervention scenario.
    eligible = [f["index"] for f in baseline["frames"] if f["closed_roads"]]
    if shutil.disk_usage(output.parent).free < 3 * 1024**3:
        raise ValueError("Insufficient space for the bounded dispatch experiment")
    output.mkdir()
    for case in view["cases"]:
        (output / case["id"]).symlink_to((study / case["id"]).resolve(), target_is_directory=True)
    write_new(output / "protocol.json", dict(
        job=job.name, parent_sha256=sha256(study / "view.json"), roads_sha256=sha256(roads),
        source_frames_sha256=protocol["source_frames_sha256"],
        script_sha256=sha256(Path(__file__)), capacities_per_plan=1, capacity_m3=capacity,
        capture_rate_m3_s=rate, volume_rounding_m3=VOLUME_STEP_M3, eligible_hours=eligible,
        control="off or full feasible withdrawal, no release, same site for all hours",
        objective=["closed_road_segment_hours", "wet_cell_hours", "site_id"],
        qualification="HYPOTHETICAL_STORAGE_RESEARCH"))
    native_count = 0
    dispatch = []
    for site in protocol["sites"]:
        strategies = [case for case in view["cases"] if case["site"] == site]
        template = strategies[0]
        downstream = set(template["downstream"])
        key = f"dispatch-site-{site}"
        directory = output / key
        directory.mkdir()
        options = []
        variants = {}
        for hour in eligible:
            ref = source["frames"][hour]
            original = baseline["frames"][hour]
            table = replay / f"hour-{hour:02d}/discharge.csv"
            assert sha256(table) == ref["discharge_sha256"]
            with table.open() as stream:
                rows = [(int(r["stream"]), float(r["Q0"]), float(r["Q100"])) for r in csv.DictReader(stream)]
            capture = min(rate, min(max(0, q - base) for sid, base, q in rows if sid in downstream))
            if not capture:
                continue
            previous = next((case["frames"][hour] for case in strategies
                             if case["frames"][hour]["captured_m3_s"] == capture), None)
            if previous:
                assert sha256(output / previous["raster"]) == previous["raster_sha256"]
                frame = dict(previous)
            else:
                changed = [(sid, base, max(base, q - capture) if sid in downstream else q) for sid, base, q in rows]
                frame = render_frame(native, directory, hour, datetime.fromisoformat(ref["at"]), changed,
                                     settings, runtime, source["grid"])
                frame["raster"] = f"{key}/{frame['raster']}"
                with rasterio.open(output / frame["raster"]) as dataset:
                    depth = RoadDepth(dataset)
                    frame["closed_roads"] = sum(
                        assess_edge(dict(edge, **depth.segment(edge["a"], edge["b"])), view["threshold_m"])[0] == "closed"
                        for edge in segments.values())
                frame["png"] = f"{key}/{frame['png']}"
                native_count += 1
            options.append((hour, math.ceil(capture * 3600 / VOLUME_STEP_M3),
                            original["closed_roads"] - frame["closed_roads"],
                            original["positive_cells"] - frame["positive_cells"], capture))
            variants[hour] = frame
        decisions = dict(schedule(options, capacity))
        frames, stored = [], 0
        for base in baseline["frames"]:
            hour = base["index"]
            capture = decisions.get(hour, 0)
            frame = dict(variants[hour] if capture else base)
            stored += 3600 * capture
            assert stored <= capacity + 1e-8
            frames.append(dict(frame, stored_m3=stored, captured_m3_s=capture))
        dispatch.append(dict(template, id=key, strategy="dispatch", activation_hour=min(decisions, default=None),
                             active_hours=list(decisions), frames=frames,
                             closed_road_hours=sum(f["closed_roads"] for f in frames),
                             wet_cell_hours=sum(f["positive_cells"] for f in frames)))
        print(key, dispatch[-1]["closed_road_hours"], list(decisions), flush=True)
    candidates = list(chain(view["cases"][1:], dispatch))
    best = min(candidates, key=lambda case: (case["closed_road_hours"], case["wet_cell_hours"], case["site"]))
    assert all(sha256(Path(file)) == digest for file, digest in engine.items())
    write_new(output / "view.json", dict(view, cases=[baseline, *candidates], optimized=best["id"],
              extra_native_runs=native_count, control="hourly_dispatch"))
    print("Best", best["id"], best["closed_road_hours"], "extra runs", native_count, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("job", "replay", "roads", "study", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    optimise(*(getattr(args, name).resolve() for name in ("job", "replay", "roads", "study", "output")))
