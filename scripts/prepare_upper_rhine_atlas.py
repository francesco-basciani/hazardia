"""Prepare the bounded Rhine Atlas context for the Upper Rhine replay."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import shutil

from PIL import Image
from shapely.geometry import MultiPolygon, mapping, shape
from shapely.validation import make_valid

RADIUS = 6378137
ATLAS = "https://geoportal.bafg.de/karten/rheinatlas/"
SERVICES = "https://geoportal.bafg.de/arcgis/rest/services/IKSR_RheinAtlas_2020/"
NAMES = {
    "erstein": "Rétention dynamique crues Rhin - Polder Erstein (VNF)",
    "altenheim": "Retentionspolder Altenheim",
    "soellingen": "Retentionspolder Söllingen/Greffern",
}
DEPTHS = [
    ("0–0.5 m", "#b7eef1"),
    ("0.5–2 m", "#5ba3e6"),
    ("2–4 m", "#1f58c7"),
    ("> 4 m", "#070791"),
]


def lonlat(x, y):
    return [math.degrees(math.atan(math.sinh(y/RADIUS))), math.degrees(x/RADIUS)]


def prepare(source, output):
    export = json.loads((source / "export.json").read_text())
    extent = export["extent"]
    assert extent["spatialReference"].get("latestWkid", extent["spatialReference"]["wkid"]) == 3857
    bounds = [lonlat(extent["xmin"], extent["ymin"]), lonlat(extent["xmax"], extent["ymax"])]
    raster = source / "atlas-frequent.png"
    with Image.open(raster) as image:
        assert image.mode == "RGBA" and image.size == (export["width"], export["height"])
        pixels = Counter(image.getdata())
    assert pixels[(0, 0, 0, 0)] > 0
    for _, colour in DEPTHS:
        rgb = bytes.fromhex(colour[1:])
        assert pixels[(*rgb, 255)] > 0, colour

    dataset = json.loads((source / "works.geojson").read_text())
    works = []
    for site_id, name in NAMES.items():
        [feature] = [item for item in dataset["features"] if item["properties"]["NAME"] == name]
        original = shape(feature["geometry"])
        polygon = original if original.is_valid else make_valid(original)
        if polygon.geom_type == "GeometryCollection":
            polygon = MultiPolygon([part for geom in polygon.geoms
                                    for part in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom])
                                    if part.geom_type == "Polygon"])
        assert polygon.geom_type in {"Polygon", "MultiPolygon"} and polygon.is_valid and polygon.area > 0
        # Put the control on the official footprint, including sites with several basins.
        largest = max(polygon.geoms, key=lambda part: part.area) if polygon.geom_type == "MultiPolygon" else polygon
        anchor = largest.representative_point()
        works.append({
            "type": "Feature", "geometry": mapping(polygon),
            "properties": {"id": site_id, "source_name": name, "anchor": [anchor.y, anchor.x],
                           "geometry_repaired": not original.is_valid},
        })
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(raster, output / "atlas-frequent.png")
    document = {
        "schema": "hazardia.upper-rhine-atlas/1",
        "source": ATLAS,
        "depth_service": SERVICES + "IKSR_Hazard_High_2020/MapServer/0",
        "works_service": SERVICES + "IKSR_FloodProtectionThemes_de_2020/MapServer/1",
        "depths": DEPTHS, "bounds": bounds,
        "works": {"type": "FeatureCollection", "features": works},
        "sha256": {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                   for name in ("export.json", "atlas-frequent.png", "works.geojson")},
    }
    (output / "atlas.json").write_text(json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"PASS: four depth classes, {sum(n for rgba,n in pixels.items() if rgba[3])} water pixels, "
          f"three valid selectable footprints, bounds {bounds}.")
    for feature in works:
        print(feature["properties"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
