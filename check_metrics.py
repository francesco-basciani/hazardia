"""Recompute the comparison metrics from the published run summaries."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def change_percent(candidate, reference):
    return 100 * (candidate - reference) / reference


def main():
    fire = read("wildfire-summary.json")
    _, west, selected = fire["displayed_plans"]
    for plan in fire["displayed_plans"]:
        print(f"Wildfire {plan['plan']}: {plan['interface_m2']:,} m² interface, "
              f"{plan['total_m2'] / 10_000:.4f} ha total")
    print(f"Wildfire total change vs. west flank: "
          f"{change_percent(selected['total_m2'], west['total_m2']):+.1f}%")

    flood = read("flood-hourly-metrics.json")
    totals = {}
    for plan in flood["plans"]:
        frames = plan["frames"]
        if [frame["hour"] for frame in frames] != list(range(flood["hourly_samples"])):
            raise ValueError(f"Unexpected hourly sequence in {plan['plan']}")
        road_hours = sum(frame["segments_at_threshold"] for frame in frames)
        cell_hours = sum(frame["wet_cells"] for frame in frames)
        totals[plan["plan"]] = (road_hours, cell_hours)
        print(f"Flood {plan['plan']}: {road_hours:,} segment-hours, {cell_hours:,} cell-hours")
        for hour in (25, 26):
            frame = frames[hour]
            print(f"  Hour {hour}: {frame['wet_cells']:,} wet cells, "
                  f"{frame['segments_at_threshold']:,} segments at threshold")
    continuous = totals["continuous_withdrawal"]
    scheduled = totals["scheduled_withdrawal"]
    print(f"Flood exposure change vs. continuous: {change_percent(scheduled[0], continuous[0]):+.1f}%")
    print(f"Flood inundation change vs. continuous: {change_percent(scheduled[1], continuous[1]):+.1f}%")


if __name__ == "__main__":
    main()
