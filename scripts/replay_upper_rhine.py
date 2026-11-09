"""Build the bounded research comparison on the VM from report figure 26."""

import argparse
import itertools
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, vstack

HOURS = 168
SECONDS = 3600


def digitise(svg, axes):
    """Recover both vector paths on the first chart and sample its hourly grid."""
    left, right, top, bottom = axes
    curves = []
    for colour in ("rgb(100%, 0%, 0%)", "rgb(0%, 0%, 100%)"):
        points = []
        for path in ET.parse(svg).iter("{http://www.w3.org/2000/svg}path"):
            if path.get("stroke") != colour or path.get("fill") != "none":
                continue
            matrix = path.get("transform", "").removeprefix("matrix(").removesuffix(")")
            if not matrix:
                continue
            a, b, c, d, tx, ty = map(float, matrix.split(","))
            for x, y in re.findall(r"[ML] ([-\d.e]+) ([-\d.e]+)", path.get("d", "")):
                x, y = float(x), float(y)
                page_x, page_y = a*x + c*y + tx, b*x + d*y + ty
                if left - .03 <= page_x <= right + .03 and 150 < page_y < 310:
                    points.append((page_x, 1000 + (bottom-page_y) * 4000/(bottom-top)))
        if len(points) < 200:
            raise ValueError("Missing vector discharge curve")
        points = np.asarray(sorted(points))
        curves.append(np.interp(np.linspace(left, right, HOURS, endpoint=False), *points.T).round(1))
    return curves


def simulate(reference, sites, intake, release):
    """Apply the same volume balance and integer travel times to both plans."""
    river = reference.copy()
    states = []
    for site, take, give in zip(sites, intake, release):
        storage = np.cumsum(take - give) * SECONDS
        lag = site["lag_h"]
        if min(storage) < -0.1 or max(storage) > site["working_capacity_m3"] + 0.1:
            raise ValueError("Storage balance is outside capacity")
        if np.any(take[-lag:]) or np.any(give[-lag:]) or abs(storage[-1]) > 0.1:
            raise ValueError("Replay ends with water still stored or in transit")
        if abs(sum(take-give)) > .001:
            raise ValueError("Discharge imbalance")
        river[lag:] += (give - take)[:-lag]
        states.append({"intake": take.round(3).tolist(), "release": give.round(3).tolist(),
                       "storage": storage.round(1).clip(min=0).tolist()})
    if min(river) < 0 or abs(sum(river-reference)) > .001:
        raise ValueError("Outlet balance is invalid")
    return {"q": river.round(1).tolist(), "peak": round(float(max(river)), 1), "sites": states}


def manual_plan(reference, protocol, options):
    sites = protocol["sites"]
    intake = np.zeros((len(sites), HOURS))
    release = np.zeros_like(intake)
    for i, (site, option) in enumerate(zip(sites, options)):
        if not option:
            continue
        start, stop = protocol["manual_windows"][option - 1]
        remaining = site["working_capacity_m3"] / SECONDS
        for hour in range(start, stop):
            intake[i, hour] = min(remaining, site["intake_m3_s"])
            remaining -= intake[i, hour]
        remaining = sum(intake[i])
        for hour in range(protocol["release_start_hour"], HOURS - site["lag_h"]):
            release[i, hour] = min(remaining, site["release_m3_s"])
            remaining -= release[i, hour]
    return simulate(reference, sites, intake, release)


def optimise(reference, protocol, available):
    """Minimise Maxau's peak, then total withdrawn volume among peak minimisers."""
    sites = protocol["sites"]
    start = protocol["storage_start_hour"]
    end = protocol["release_start_hour"]
    max_intake_hour = max(stop for _, stop in protocol["manual_windows"])
    operations = []
    for i, site in enumerate(sites):
        if not available & (1 << i):
            continue
        for hour in range(start, max_intake_hour):
            operations.append((i, hour, 1, site["intake_m3_s"]))
        for hour in range(end, HOURS-site["lag_h"]):
            operations.append((i, hour, -1, site["release_m3_s"]))
    width = len(operations) + 1
    outlet = lil_matrix((HOURS, width))
    capacity = lil_matrix((len(sites), width))
    outlet[:, -1] = -1
    for column, (i, hour, sign, _) in enumerate(operations):
        outlet[hour+sites[i]["lag_h"], column] = -sign
        capacity[i, column] = sign == 1
    balance = lil_matrix((len(sites), width))
    for column, (i, _, sign, _) in enumerate(operations):
        balance[i, column] = sign
    constraints = vstack([outlet, capacity], format="csr")
    rhs = np.r_[-reference, [s["working_capacity_m3"]/SECONDS for s in sites]]
    bounds = [(0, limit) for _, _, _, limit in operations] + [(0, None)]
    objective = np.r_[np.zeros(width-1), 1]
    result = linprog(objective, A_ub=constraints, b_ub=rhs,
                     A_eq=balance.tocsr(), b_eq=np.zeros(len(sites)), bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    bounds[-1] = (0, result.fun + 1e-6)
    objective = [int(sign == 1) for _, _, sign, _ in operations] + [0]
    result = linprog(objective, A_ub=constraints, b_ub=rhs,
                     A_eq=balance.tocsr(), b_eq=np.zeros(len(sites)), bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    intake = np.zeros((len(sites), HOURS))
    release = np.zeros_like(intake)
    for value, (i, hour, sign, _) in zip(result.x, operations):
        (intake if sign == 1 else release)[i, hour] = value
    return simulate(reference, sites, intake, release)


def export(protocol, svg, output):
    reference, observed = digitise(svg, protocol["svg_axes"])
    for label, curve in (("reference", reference), ("observed", observed)):
        assert abs(max(curve) - protocol["published_peaks_m3_s"][label]) <= 20, (label, max(curve))
    output.mkdir(parents=True, exist_ok=True)
    def write(name, data):
        (output / f"{name}.json").write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")

    write("event", {**protocol, "schema": "hazardia.upper-rhine/1", "reference": reference.tolist(),
                    "observed": observed.tolist(), "default_manual": [2, 2, 2]})
    optimal = {mask: optimise(reference, protocol, mask) for mask in range(8)}
    for mask, plan in optimal.items():
        write(f"optimal-{mask}", plan)
    options_count = 1 + len(protocol["manual_windows"])
    best_manual = {}
    for options in itertools.product(range(options_count), repeat=len(protocol["sites"])):
        plan = manual_plan(reference, protocol, options)
        used = sum(1 << i for i, value in enumerate(options) if value)
        for mask, candidate in optimal.items():
            if mask & used == used:
                assert candidate["peak"] <= plan["peak"] + .1, (options, mask)
                if mask not in best_manual or plan["peak"] < best_manual[mask]["peak"]:
                    best_manual[mask] = {"options": options, "peak": plan["peak"]}
        write("manual-" + "".join(map(str, options)), plan)
    write("manual-benchmark", best_manual)
    print(f"PASS: {options_count ** len(protocol['sites'])} manual schedules, 8 optimal subsets, outlet and storage balances.")
    print(f"Digitised peaks: reference {max(reference)}, observed {max(observed)} m³/s.")
    print(f"Default comparison: manual {manual_plan(reference, protocol, [2, 2, 2])['peak']}, "
          f"optimised {optimal[7]['peak']} m³/s.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("svg", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    export(json.loads(args.protocol.read_text()), args.svg, args.output)
