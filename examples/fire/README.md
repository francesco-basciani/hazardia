# Abruzzo wildfire — real PROPAGATOR adapter

Execute in the Linux VM. The immutable M1 snapshot uses real Copernicus DSM, Sentinel-2 and retrospective ERA5 wind near L'Aquila; ignition, uniform legacy5 fuel and moisture10% are synthetic. It is a conditional research scenario, not a detected fire or operational forecast. Source assets and their hashes remain in the VM run directory.

```sh
cd /home/hazardia/hazardia-runtime/app
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json submit --request ../runs/m1-abruzzo-20261015T161041Z/fire-request.json --snapshot-root ../runs/m1-abruzzo-20261015T161041Z
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json work-once
```

`submit` validates and copies prepared inputs into a unique job directory. `work-once` executes the oldest waiting job; inspect its returned `state`, `error_code` and `usable_product`. Exit0 from the CLI alone is not a simulation-success assertion. Use `status JOB_ID`, `events JOB_ID`, `cancel JOB_ID` or explicit `retry JOB_ID`. Success includes probability (unit1), earliest-realization arrival (seconds), independently read GeoTIFFs, immutable product and run manifests, original logs and provenance. Fresh runs create new job IDs and preserve earlier failures.

See `reports/M1-integration.md` for executed commands/results and installation/environment constraints. No dashboard or decision engine exists at M1.
