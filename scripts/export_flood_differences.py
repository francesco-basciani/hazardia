"""Export signed depth differences from the archived containment and reference rasters."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
import rasterio

from hazardia.io import load, sha256, write_new

THRESHOLD_M = .01
BICUBIC = getattr(Image, "Resampling", Image).BICUBIC


def difference(reference, variant, image_path):
    with rasterio.open(reference) as base, rasterio.open(variant) as case:
        if (base.crs, base.transform, base.shape) != (case.crs, case.transform, case.shape):
            raise ValueError("Reference and case grids differ")
        before = base.read(1, masked=True).astype(np.float64).filled(np.nan)
        after = case.read(1, masked=True).astype(np.float64).filled(np.nan)
    valid = np.isfinite(before) & np.isfinite(after)
    if not valid.any():
        raise ValueError("No common valid cells")
    delta = after - before
    shallower = valid & (delta <= -THRESHOLD_M)
    deeper = valid & (delta >= THRESHOLD_M)
    changed = shallower | deeper
    png = None
    if changed.any():
        # Soften the presentation only. All metrics use the native cells above.
        size = (before.shape[1] * 4, before.shape[0] * 4)
        image = Image.new("RGBA", size)
        for mask, colour in ((shallower, (77, 224, 195)), (deeper, (255, 174, 52))):
            if not mask.any():
                continue
            alpha = Image.fromarray(mask.astype(np.uint8) * 190).resize(size, BICUBIC)
            layer = Image.new("RGBA", size, colour)
            layer.putalpha(alpha.filter(ImageFilter.GaussianBlur(1.3)))
            image = Image.alpha_composite(image, layer)
        image.save(image_path)
        png = f"differences/{image_path.name}"
    return dict(
        png=png,
        png_sha256=sha256(image_path) if png else None,
        shallower_cells=int(shallower.sum()),
        deeper_cells=int(deeper.sum()),
        dried_cells=int((valid & (before > 0) & (after == 0)).sum()),
        newly_wet_cells=int((valid & (before == 0) & (after > 0)).sum()),
        comparable_cells=int(valid.sum()),
        max_reduction_m=max(0, -float(delta[valid].min())),
        max_increase_m=max(0, float(delta[valid].max())),
    )


def export(containment, replay, output):
    view_file = containment / "view.json"
    view = load(view_file)
    source_file = replay / "frames.json"
    source = load(source_file)
    protocol = load(containment / "protocol.json")
    if view["job_id"] != source["job_id"] or sha256(source_file) != protocol["source_frames_sha256"]:
        raise ValueError("Reference replay does not match the containment experiment")
    output.mkdir()
    cases = {}
    for case in view["cases"]:
        if case["id"] == view["baseline"]:
            continue
        series = []
        for reference, frame in zip(source["frames"], case["frames"], strict=True):
            index = frame["index"]
            if (reference["index"], reference["at"]) != (index, frame["at"]):
                raise ValueError("Reference and case timestamps differ")
            original = replay / reference["raster"]
            variant = original
            if frame["captured_m3_s"]:
                saved_path = frame.get("raster") or f"{case['id']}/hour-{index:02d}/flood/T100/rst/flood_map_T100_m.tif"
                variant = containment / saved_path
            if sha256(original) != reference["raster_sha256"] or sha256(variant) != frame["raster_sha256"]:
                raise ValueError("Raster checksum mismatch")
            stats = difference(original, variant, output / f"{case['id']}-{index:02d}.png")
            series.append(dict(stats, at=frame["at"], index=index,
                               reference_sha256=reference["raster_sha256"], variant_sha256=frame["raster_sha256"]))
        cases[case["id"]] = series
    write_new(output / "index.json", dict(schema="hazardia.flood-depth-differences/1",
              job_id=view["job_id"], threshold_m=THRESHOLD_M, containment_view_sha256=sha256(view_file), cases=cases))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("containment", "replay", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    export(args.containment, args.replay, args.output)
