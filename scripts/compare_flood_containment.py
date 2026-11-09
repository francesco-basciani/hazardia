"""Evaluate a finite catalogue of hypothetical storage sites in the Linux VM."""
import argparse
import csv
from itertools import product as combinations
import math
import datetime as dt
from pathlib import Path
import shutil
import sys

import geopandas as gpd
import rasterio

from hazardia.flood_access import assess_edge
from hazardia.flood_road_depth import RoadDepth
from hazardia.io import load, sha256, write_new
from replay_flood_frames import render_frame

SITES = (18, 32, 50)
CAPACITY_M3 = 18_000
CAPTURE_M3_S = 1.5
THRESHOLD_M = .10


def compare(job, replay, road_file, output, *, sites=SITES, capacity=CAPACITY_M3,
            capture_rate=CAPTURE_M3_S, start_hour=2, alternative_starts=(), title=None):
    if (len(sites) != 3 or len(set(sites)) != 3 or not all(
            math.isfinite(value) and value > 0 for value in (capacity, capture_rate))):
        raise ValueError("Expected three distinct sites and positive storage parameters")
    runtime = load(job / "runtime.json")
    product = load(job / "product.json")
    original = load(replay / "frames.json")
    protocol = load(replay / "protocol.json")
    native = job / "flood-work"
    assert original["job_id"] == job.name == protocol["job_id"]
    assert original["source_product_sha256"] == sha256(job / "product.json")
    hours = len(original["frames"])
    starts = tuple(dict.fromkeys((start_hour, *alternative_starts)))
    if not 2 <= hours <= 48 or len(starts) > 4 or not all(0 <= hour < hours for hour in starts):
        raise ValueError("Expected up to four start hours within the simulation")
    strategies = list(combinations(sites, starts))
    objective = ["closed_road_segment_hours", "wet_cell_hours", "site_id", "activation_hour"]
    assert shutil.disk_usage(output.parent).free > 2 * 1024**3 + 600 * 1024**2
    assert all(sha256(job / file) == digest for file, digest in protocol["inputs"].items())
    assert all(sha256(Path(file)) == digest for file, digest in protocol["engine_files"].items())
    network = gpd.read_file(native / "data_static/vct/v_abruzzo_1arcsec_streams_features.shp")
    successors = dict(zip(map(int, network.stream), map(int, network.next_strea)))
    sections = {x["stream"]: x for x in load(job / "hmc-input-mapping.json")["sections"]}
    if not set(sites) <= sections.keys():
        raise ValueError("Candidate not in HMC river network")
    roads = load(road_file)
    assert roads["schema"] == "hazardia.flood-road-depth/1"
    segments = {edge["id"].rsplit(":", 1)[0]: edge for edge in roads["edges"]}
    settings = load(native / "settings.json")
    output.mkdir(exist_ok=False)
    write_new(output / "protocol.json", dict(
        job=job.name, source_frames_sha256=sha256(replay / "frames.json"),
        roads_sha256=sha256(road_file), script_sha256=sha256(Path(__file__)),
        sites=sites, capacity_m3=capacity, capture_m3_s=capture_rate, depth_threshold_m=THRESHOLD_M,
        maximum_native_runs=sum(hours - start for _, start in strategies),
        activation_hours=starts, manual=dict(site=sites[0], activation_hour=start_hour),
        objective=objective,
        qualification="HYPOTHETICAL_STORAGE_RESEARCH"))

    def measure(raster):
        closed = 0
        with rasterio.open(raster) as ds:
            depth = RoadDepth(ds)
            for edge in segments.values():
                observation = dict(edge, **depth.segment(edge["a"], edge["b"]))
                closed += assess_edge(observation, THRESHOLD_M)[0] == "closed"
        return closed

    cases = []
    closed_by_raster = {}
    native_frames = {}
    for site, activation in [(None, None), *strategies]:
        key = f"site-{site}" if site else "baseline"
        if site and len(starts) > 1:
            key += f"-h{activation:02d}"
        case_folder = output / key
        case_folder.mkdir()
        downstream = []
        current = site
        while current in successors:
            assert current not in downstream
            downstream.append(current)
            current = successors[current]
        remaining = capacity
        frames = []
        for source in original["frames"]:
            hour = source["index"]
            raster = replay / source["raster"]
            assert sha256(raster) == source["raster_sha256"]
            table = replay / f"hour-{hour:02d}/discharge.csv"
            assert sha256(table) == source["discharge_sha256"]
            with table.open() as stream:
                rows = [(int(r["stream"]), float(r["Q0"]), float(r["Q100"])) for r in csv.DictReader(stream)]
            assert set(s for s, _, _ in rows) == set(successors)
            capture = 0
            if downstream and hour >= activation:
                capture = min(capture_rate, remaining / 3600,
                              min(max(0, q - base) for s, base, q in rows if s in downstream))
            remaining -= capture * 3600
            assert remaining >= -1e-8
            if capture:
                cache_key = (site, hour, capture)
                if cache_key in native_frames:
                    frame, origin = native_frames[cache_key]
                    frame = dict(frame)
                    shutil.copyfile(origin / frame["png"], case_folder / frame["png"])
                    raster = origin / frame["raster"]
                else:
                    changed = [(s, base, max(base, q - capture) if s in downstream else q)
                               for s, base, q in rows]
                    frame = render_frame(native, case_folder, hour, dt.datetime.fromisoformat(source["at"]),
                                         changed, settings, runtime, product["grid"])
                    native_frames[cache_key] = (dict(frame), case_folder)
                    raster = case_folder / frame["raster"]
            else:
                frame = dict(source)
                shutil.copyfile(replay / source["png"], case_folder / frame["png"])
            assert sha256(case_folder / frame["png"]) == frame["png_sha256"]
            frame["raster"] = str(raster.relative_to(output)) if raster.is_relative_to(output) else None
            digest = frame["raster_sha256"]
            if digest not in closed_by_raster:
                closed_by_raster[digest] = measure(raster)
            frames.append(dict(frame, png=key + "/" + frame["png"],
                               closed_roads=closed_by_raster[digest], stored_m3=capacity - remaining,
                               captured_m3_s=capture))
        position = [sections[site]["latitude"], sections[site]["longitude"]] if site else None
        cases.append(dict(id=key, site=site, point=position, activation_hour=activation,
                          resources=int(site is not None), downstream=downstream, frames=frames,
                          closed_road_hours=sum(f["closed_roads"] for f in frames),
                          wet_cell_hours=sum(f["positive_cells"] for f in frames)))
        print(key, cases[-1]["closed_road_hours"], cases[-1]["wet_cell_hours"], flush=True)
    assert all(sha256(job / file) == digest for file, digest in protocol["inputs"].items())
    assert all(sha256(Path(file)) == digest for file, digest in protocol["engine_files"].items())
    best = min(cases[1:], key=lambda c: (c["closed_road_hours"], c["wet_cell_hours"], c["site"], c["activation_hour"]))
    write_new(output / "view.json", dict(schema="hazardia.flood-containment-view/1", job_id=job.name,
        baseline="baseline", manual=cases[1]["id"], optimized=best["id"], cases=cases,
        capacity_m3=capacity, capture_m3_s=capture_rate, capture_start_hour=start_hour,
        final_valid_until=original["final_valid_until"], title=title, threshold_m=THRESHOLD_M,
        activation_hours=starts, native_runs=len(native_frames)))
    print("Optimized site:", best["site"], flush=True)


if __name__ == "__main__":
    if sys.platform != "linux":
        raise RuntimeError("Use the existing Linux VM")
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("job", "replay", "roads", "output"):
        parser.add_argument(field, type=Path)
    parser.add_argument("--sites", type=int, nargs=3, default=SITES)
    parser.add_argument("--capacity", type=float, default=CAPACITY_M3)
    parser.add_argument("--capture-rate", type=float, default=CAPTURE_M3_S)
    parser.add_argument("--start-hour", type=int, default=2)
    parser.add_argument("--alternative-starts", type=int, nargs="*", default=())
    parser.add_argument("--title")
    args = parser.parse_args()
    compare(*(getattr(args, field).resolve() for field in ("job", "replay", "roads", "output")),
            sites=args.sites, capacity=args.capacity, capture_rate=args.capture_rate,
            start_hour=args.start_hour, alternative_starts=args.alternative_starts, title=args.title)
