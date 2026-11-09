"""Run pinned REFlEx step 4 independently on each archived HMC hourly sample."""
import argparse
import csv
import datetime as dt
import gzip
import math
from pathlib import Path
import shutil
import subprocess
import sys

from netCDF4 import Dataset
import numpy as np
from PIL import Image
import rasterio

from hazardia.adapters.flood_checks import verify_dry_map
from hazardia.io import load, sha256, utcnow, write_new


def render_frame(native, output, index, when, rows, settings, runtime, expected_grid):
    folders = ("dem_conditioning", "hydro_derivatives", "data_static", "hand")
    frame = output / f"hour-{index:02d}"
    frame.mkdir()
    for name in folders:
        shutil.copytree(native / name, frame / name)
    table = frame / "discharge.csv"
    with table.open("x") as stream:
        writer = csv.writer(stream)
        writer.writerow(("stream", "Q0", "Q100"))
        writer.writerows(rows)
    settings["step_4"]["volume_file_path"] = str(table)
    configuration = frame / "settings.json"
    write_new(configuration, settings)
    script = Path(runtime["reflex_source"]) / "reflex_step4_flood_mapping.py"
    with (frame / "console.log").open("xb") as log:
        subprocess.run([runtime["geo_python"], str(script), "-settings_file", str(configuration),
                        "-base_path", str(frame), "-log_file", str(frame / "reflex.log")],
                       check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    raster = frame / "flood/T100/rst/flood_map_T100_m.tif"
    stats = frame / "flood/T100/txt/flood_stats_T100_m.csv"
    with stats.open() as stream:
        fitted = list(csv.DictReader(stream))
    residual = max((float(row["diff_final"]) / max(float(row["V_cut"]), 1) for row in fitted), default=0)
    assert math.isfinite(residual) and residual <= .01
    with rasterio.open(raster) as ds:
        assert ds.crs.to_string() == expected_grid["crs"] and list(ds.shape) == expected_grid["shape"]
        assert np.allclose(list(ds.transform)[:6], expected_grid["transform"], rtol=0, atol=1e-12)
        depth = ds.read(1, masked=True)
        valid = depth.compressed()
        assert valid.size and np.isfinite(valid).all() and (valid >= 0).all()
        if not fitted:
            # All source volumes are recorded by the pinned step. A dry
            # raster must contain valid zeros rather than absent data.
            import geopandas as gpd
            features = gpd.read_file(frame / "data_static/vct/v_abruzzo_1arcsec_streams_features.shp")
            volume = {sid: max(0, value - base) for sid, base, value in rows}
            eligible = sum(round(volume[int(sid)] * tc / 2) >= settings["step_4"]["minimum_volume_included"]
                           for sid, tc in zip(features.stream, features.tconc))
            verify_dry_map(eligible, valid)
        rgba = np.zeros((*depth.shape, 4), dtype=np.uint8)
        water = depth.filled(0) > 0
        rgba[water, :3] = [20, 129, 235]
        rgba[water, 3] = np.clip(110 + depth.filled(0)[water] * 700, 110, 235).astype(np.uint8)
        Image.fromarray(rgba).save(output / f"depth-{index:02d}.png")
        bounds = [[ds.bounds.bottom, ds.bounds.left], [ds.bounds.top, ds.bounds.right]]
    return dict(index=index, at=when.isoformat(), positive_cells=int((valid > 0).sum()),
                       max_depth_m=float(valid.max()), max_discharge_m3_s=max(r[2] for r in rows),
                       residual=residual, raster=str(raster.relative_to(output)), bounds=bounds,
                       raster_sha256=sha256(raster), discharge_sha256=sha256(table),
                       png=f"depth-{index:02d}.png", png_sha256=sha256(output / f"depth-{index:02d}.png"))


def replay(job, output):
    runtime = load(job / "runtime.json")
    manifest = load(job / "manifest.json")
    product = load(job / "product.json")
    assert manifest["status"] == "SUCCEEDED" and product["hazard"] == "FLOOD"
    assert shutil.disk_usage(job).free > 2 * 1024**3 + 256 * 1024**2
    native = job / "flood-work"
    # Verify inputs against the original receipt, including shapefile sidecars.
    folders = ("dem_conditioning", "hydro_derivatives", "data_static", "hand")
    files = [job / name for name in ("hmc-reflex-bridge.json", "hmc-input-mapping.json",
                                     "flood-work/settings.json", "products/maximum-depth.tif")]
    files += sorted((native / "hmc/output").glob("hmc.output-grid.*.nc.gz"))
    for folder in folders:
        files.extend(path for path in (native / folder).rglob("*") if path.is_file())
    hashes = {str(path.relative_to(job)): sha256(path) for path in files}
    assert all(manifest["artifacts"].get(name) == value for name, value in hashes.items())
    engine = {path: digest for path, digest in runtime["engine_files"].items()
              if Path(path).is_relative_to(runtime["reflex_source"])}
    assert engine and all(sha256(Path(path)) == digest for path, digest in engine.items())
    settings = load(native / "settings.json")
    mapping = load(job / "hmc-input-mapping.json")
    bridge = load(job / "hmc-reflex-bridge.json")
    sections = mapping["sections"]
    q0 = {row["stream"]: row["Q0"] for row in bridge["reach_rows"]}
    records = {(v["time"], v["stream"]): v["Q_m3_s"] for v in bridge["records"]}
    start = dt.datetime.fromisoformat(product["valid_from"].replace("Z", "+00:00"))
    until = dt.datetime.fromisoformat(product["valid_until"].replace("Z", "+00:00"))
    samples = sorted((native / "hmc/output").glob("hmc.output-grid.*.nc.gz"))
    assert len(samples) == (until - start).total_seconds() / 3600 <= 48
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "protocol.json", dict(
        at=utcnow(), job_id=job.name, code_base="5d20f93", script_sha256=sha256(Path(__file__)),
        inputs=hashes, engine_files=engine, temporal_method="independent_hourly_discharge_conditioned_maps",
        native_runs=len(samples), hypotheses="Hourly HMC flow differences may change the independently mapped extent.",
        threshold_m=.10, duration_assumption="hold each snapshot for one hour in the rescue exercise only"))
    frames = []
    expected_grid = product["grid"]
    for index, sample in enumerate(samples):
        when = start + dt.timedelta(hours=index)
        stamp = when.strftime("%Y-%m-%d_%H:%M:%S")
        with Dataset("memory", memory=gzip.decompress(sample.read_bytes())) as ds:
            assert ds.time_coverage_end == stamp and ds["Discharge"].units == "m^3/s"
            discharge = ds["Discharge"][:]
            assert list(discharge.shape) == expected_grid["shape"]
            lon = np.asarray(ds["Longitude"][:])
            lat = np.asarray(ds["Latitude"][:])
            rows = []
            for section in sections:
                sid = section["stream"]
                delta = (lon - section["longitude"])**2 + (lat - section["latitude"])**2
                cell = np.unravel_index(np.argmin(delta), delta.shape)
                assert np.sqrt(delta[cell]) <= expected_grid["transform"][0] * .1
                assert not np.ma.is_masked(discharge[cell])
                value = float(discharge[cell])
                assert math.isfinite(value) and value >= 0 and value == records[(stamp, sid)]
                rows.append((sid, q0[sid], value))
        frames.append(render_frame(native, output, index, when, rows, settings, runtime, expected_grid))
        print(frames[-1], flush=True)
    assert all(sha256(job / path) == digest for path, digest in hashes.items())
    assert all(sha256(Path(path)) == digest for path, digest in engine.items())
    write_new(output / "frames.json", dict(schema="hazardia.flood-hourly-snapshots/1", job_id=job.name,
              engine=product["engine"], source_product_sha256=sha256(job / "product.json"),
              grid=expected_grid, unit="m", qualification="RESEARCH_HOURLY_QUASI_STATIC",
              final_valid_until=product["valid_until"], frames=frames))


if __name__ == "__main__":
    if sys.platform != "linux":
        raise RuntimeError("Use the existing Linux VM")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    replay(args.job.resolve(), args.output.resolve())
