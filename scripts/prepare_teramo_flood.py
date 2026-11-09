"""Stage and run the bounded 48-hour Teramo flood exercise in the Linux VM."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil

import numpy as np
import rasterio
from rasterio.windows import from_bounds, Window

from hazardia.ingest.range_cache import RangeCache
from hazardia.io import sha256, utcnow, write_new
from hazardia.jobs import JobStore

BOUNDS = (13.675, 42.643, 13.735, 42.683)
HOURS = 48
DEM_NAME = "Copernicus_DSM_COG_10_N42_00_E013_00_DEM"
DEM_URL = f"https://copernicus-dem-30m.s3.amazonaws.com/{DEM_NAME}/{DEM_NAME}.tif"


def prepare(runtime, work):
    if shutil.disk_usage(runtime).free < 3 * 1024**3:
        raise ValueError("Insufficient disk reserve")
    work.mkdir()
    gateway = RangeCache(runtime / "cog-cache", cap=8 * 1024**2).start()
    dem = work / "dem.tif"
    try:
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MULTIRANGE="NO"):
            with rasterio.open(gateway.local(DEM_URL)) as source:
                window = from_bounds(*BOUNDS, source.transform)
                col, row = int(window.col_off), int(window.row_off)
                crop = Window(col, row, int(np.ceil(window.col_off + window.width)) - col,
                              int(np.ceil(window.row_off + window.height)) - row)
                z = source.read(1, window=crop, masked=True)
                if source.crs.to_epsg() != 4326 or z.count() != z.size or not np.isfinite(z).all() or gateway.error:
                    raise ValueError(f"Incomplete native DEM coverage: {gateway.error}")
                transform = source.window_transform(crop)
                with rasterio.open(dem, "w", driver="GTiff", height=z.shape[0], width=z.shape[1], count=1,
                                   dtype="float32", crs=source.crs, transform=transform, nodata=-9999,
                                   compress="deflate") as target:
                    target.write(z.astype(np.float32), 1)
    finally:
        gateway.close()

    start = datetime(2024, 7, 13, tzinfo=timezone.utc)
    stamp = lambda hour: (start + timedelta(hours=hour)).isoformat().replace("+00:00", "Z")
    rain = [0] * (HOURS + 1)
    pulse = [3, 5, 8, 14, 20, 25, 23, 18, 14, 9, 6, 3, 1]
    rain[5:5 + len(pulse)] = pulse
    units = dict(precipitation="mm", wind_speed_10m="m/s", wind_direction_10m="°", temperature_2m="°C",
                 relative_humidity_2m="%", surface_pressure="hPa", shortwave_radiation="W/m²")
    records = [dict(at=stamp(hour), values=dict(precipitation=mm, wind_speed_10m=1, wind_direction_10m=0,
                    temperature_2m=18, relative_humidity_2m=75, surface_pressure=1000, shortwave_radiation=0))
               for hour, mm in enumerate(rain)]
    weather = work / "weather.json"
    write_new(weather, dict(schema_version="0.2.0", kind="weather", data_kind="SYNTHETIC",
              id="teramo-synthetic-rain-48h", issued_at=None, available_at=utcnow(), valid_from=stamp(0),
              valid_until=stamp(HOURS), units=units, records=records, source=dict(provider="HAZARDIA exercise"),
              license="Synthetic forcing"))
    grid = dict(crs="EPSG:4326", shape=list(z.shape), transform=list(transform)[:6], nodata=-9999,
                vertical_datum="EGM2008_DSM_UNQUALIFIED")
    bounds = list(rasterio.transform.array_bounds(*z.shape, transform))
    request = dict(schema_version="0.2.0", kind="simulation_request", id="teramo-flood-48h",
        hazard="FLOOD", mode="RESEARCH_RETROSPECTIVE", territory=dict(id="teramo-tordino-vezzola",
        region="Abruzzo", bbox_wgs84=bounds, work_crs="EPSG:4326", timezone="Europe/Rome",
        calibration="UNKNOWN", complete_catchment=False), grid=grid, snapshot_at=utcnow(),
        valid_from=stamp(0), valid_until=stamp(HOURS), timeout_s=600, max_log_bytes=32*1024**2,
        assets=[dict(role=role, path=path.name, sha256=sha256(path)) for role,path in (("dem",dem),("weather",weather))],
        assumptions=["Partial urban domain, not a complete catchment", "Hypothetical rainfall and initial state",
                     "Uncalibrated HMC soil parameters", "Zero synthetic bankfull reference", "No return-period claim",
                     "Date indexes a hypothetical event", "REFlEx compatibility build"],
        options=dict(hours=HOURS, rain_mm=rain, q0_m3_s=0, q0_evidence="SYNTHETIC_RESEARCH_REFERENCE",
                     flow_threshold_cells=500, allow_experimental_patch=True))
    write_new(work / "dem-source.json", dict(url=DEM_URL, bounded_download_bytes=gateway.bytes, grid=grid, sha256=sha256(dem)))
    write_new(work / "request.json", request)
    store = JobStore(work / "jobs", runtime / "runtime-v2.json")
    job = store.submit(request, work)
    (work / "job-id.txt").write_text(job + "\n")
    print("Accepted:", job, flush=True)
    state = store.work_once()
    print(state, flush=True)
    if state["state"] != "SUCCEEDED":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("work", type=Path)
    args = parser.parse_args()
    prepare(args.runtime.resolve(), args.work.resolve())
