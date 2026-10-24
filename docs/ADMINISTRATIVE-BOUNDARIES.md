# Administrative display layers

In Monitoring, open **Boundaries** in the left list. Its right-hand panel has independent **Countries**, **Regions** and **Provinces** switches. Regions start enabled; countries/provinces load only on first activation. All maps retain the existing `regionBoundaries` entry point; in a document without the switches only the pre-existing regional default is active.

| Level | Source and coverage | Display |
|---|---|---|
| Countries | Natural Earth50m v5.1.1, global,242 polygon records in the pinned archive | Warm white lines; country labels at overview zoom |
| Regions | Istat1January2026,20 Italian regions | White lines; region labels |
| Provinces | Istat1January2026,110 Italian province/metropolitan/equivalent statistical units | Fine cyan dashed lines; labels at regional zoom |

Regions/provinces outside Italy are **not provided by these assets**. Country boundaries are generalized de facto cartography, not legal adjudication. Province includes metropolitan and equivalent statistical units. This display context is never passed to physical simulators, dispatch, optimizer or scientific exposure calculations.

Natural Earth data are [public domain](https://www.naturalearthdata.com/about/terms-of-use/); the [50m country theme](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/) is the source. Istat uses the existing pinned [generalized2026 archive](https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/) and its existing CC BY4.0 receipt. Credits remain available through map Info.

## Recreate assets in the Linux VM

Use the existing geospatial environment; no new dependencies are needed. First prepare the pre-existing Istat archive/regions if absent:

```sh
cd /home/hazardia/hazardia-runtime/app
PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python scripts/prepare_region_boundaries.py --runtime /home/hazardia/hazardia-runtime
PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python scripts/prepare_administrative_levels.py --runtime /home/hazardia/hazardia-runtime
```

The second script reuses the archive and downloads only799734bytes for Natural Earth, capped at2MiB. Both archives are checksum-pinned. The first script, when needed on a new installation, has a16MiB Istat download cap. No extraction to arbitrary archive paths, no geometry repair or relaxed invalid-geometry acceptance. GeoJSON coordinates are rounded to6decimal places for countries and7for provinces; validity is checked after rounding. This does not increase the accuracy of either generalized source.

Generated `web-assets/administrative-{countries,provinces}.json` are about2.28MB/3.01MB, respectively, below the4MiB per-asset cap; regions remain unchanged. Shared browser promises avoid separate downloads for each map in the same document. Canvas renders boundary lines, labels are limited by zoom and spacing. A failed fetch is visible and can be retried by switching off/on; no forever-rejected cache promise. This is not an FPS or memory benchmark.

Verification: `node tests/web/administrative-levels.test.mjs`, `node tests/browser/i18n.mjs`, `reports/ADMIN-LEVELS-20261024.md`. Tests use synthetic cartographic fixtures; real geometry/projection checks execute in the VM preparation script. Existing browser/region-boundaries.cjs targets obsolete historical UI and is not a current end-to-end acceptance test.
