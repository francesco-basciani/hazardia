# Abruzzo flood — real HMC → REFlEx adapter

Execute in the same Linux VM as wildfire. Real Copernicus DSM and Sentinel-2 cover a small L'Aquila AOI; ERA5 provides retrospective meteorology. Rain pulse, soil/default parameters and Q0zero are explicitly synthetic/uncalibrated. The AOI is not a complete catchment. Q100/return_period100 is an upstream column label, not an estimated recurrence. Maximum-depth output does not imply flood arrival time.

```sh
cd /home/hazardia/hazardia-runtime/app
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json submit --request ../runs/m1-abruzzo-20261015T161041Z/flood-request.json --snapshot-root ../runs/m1-abruzzo-20261015T161041Z
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json work-once
```

The bounded worker runs genuine REFlEx0–3, prepares HMC static/forcing fields on the same grid, executes HMC, validates six discharge grids/units/times and per-reach mapping, then invokes REFlEx4. An independent reader validates the actual maximum-depth GeoTIFF and publishes a versioned product only on technical success. The declared experimental REFlEx copy has a HAND halo and bounded merge patch; upstream originals remain unchanged. Shallow optimization lower bound1e-6m avoids imposing0.1m water on small scenario volumes; the residual check remains1%. This is technical coupling evidence, not validated hydrological prediction.

`status JOB_ID` exposes the actual terminal result; a CLI exit0 is insufficient. Logs, typed errors, failed attempts and retry-parent links are retained. No M2 shared event/consequence model or M3 decision/UI implementation is included.
