# Wildfire and flood scenario comparisons

These records allow the numerical comparisons to be checked from the archived simulation summaries. They are research scenarios, with hypothetical interventions and controlled inputs.

- [Wildfire summary](wildfire-summary.json) reports areas in square metres at hour 12, averaged over four PROPAGATOR realizations. The interface is the area within 100 m of eight mapped built-up clusters. The candidate list includes all four tied combined placements and the alternative ground-only reference. The displayed west-flank reference is the later replay with its aircraft drop relocated.
- [Flood hourly metrics](flood-hourly-metrics.json) gives 48 samples per plan. The two intervention plans share a 240,000 m³ capacity and an 8 m³/s maximum withdrawal rate. A segment-hour counts a road segment at or above the hypothetical 0.10 m depth threshold in one hourly sample. Sum the hourly counts for the full-window metric. Hour 25 is the tabulated comparison, while hour 26 is the displayed snapshot.

Run the following command from the repository root to recompute the summary numbers using Python's standard library:

```sh
python3 reproducibility/scenario-comparisons/check_metrics.py
```

The release includes the application and flood preparation and scoring scripts. The metric files are derived from retained model outputs. Re-executing the published cases requires the original run inputs and simulator environment. The raw rasters, archives and VM state are outside this release.
