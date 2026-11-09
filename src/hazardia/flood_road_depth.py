"""Associate a depth grid with roads without making a routing decision."""
import math

METHOD = "pixel-line-intersection/1"


class RoadDepth:
    """Length fractions along a straight segment in the raster's pixel space.

    Projection is applied to the endpoints. Grid cells are half-open and
    corner-only contacts have zero length. Fractions are parameter lengths
    along the projected segment, not geodesic lengths.
    """

    def __init__(self, dataset):
        from pyproj import Transformer

        if dataset.count != 1 or not dataset.crs:
            raise ValueError("Expected a single-band, georeferenced depth grid")
        self.values = dataset.read(1)
        self.valid = dataset.read_masks(1) != 0
        self.height, self.width = dataset.shape
        self.inverse = ~dataset.transform
        self.project = Transformer.from_crs(4326, dataset.crs, always_xy=True)

    def pixel(self, point):
        col, row = self.inverse * self.project.transform(*point)
        if not all(map(math.isfinite, (col, row))):
            raise ValueError("Non-finite projected coordinates")
        return col, row

    def cell(self, col, row):
        if not (0 <= col < self.width and 0 <= row < self.height):
            return "outside", None
        value = float(self.values[row, col])
        if not self.valid[row, col] or not math.isfinite(value) or value < 0:
            return "nodata", None
        return "valid", value

    def point(self, point):
        col, row = map(math.floor, self.pixel(point))
        status, depth = self.cell(col, row)
        return dict(state=status, depth_m=depth, row=row, col=col)

    def segment(self, a, b):
        start, end = self.pixel(a), self.pixel(b)
        breaks = {0.0, 1.0}
        for first, last, limit in zip(start, end, (self.width, self.height)):
            if first == last:
                continue
            low, high = sorted((first, last))
            for boundary in range(max(0, math.floor(low) + 1), min(limit, math.ceil(high) - 1) + 1):
                breaks.add((boundary - first) / (last - first))
        fractions = dict(valid=0.0, nodata=0.0, outside=0.0)
        maximum = None
        max_cell = None
        intervals = sorted(breaks)
        for left, right in zip(intervals, intervals[1:]):
            mid = (left + right) / 2
            col, row = (math.floor(first + (last - first) * mid) for first, last in zip(start, end))
            state, value = self.cell(col, row)
            fractions[state] += right - left
            if value is not None and (maximum is None or value > maximum):
                maximum, max_cell = value, [row, col]
        return dict(coverage=fractions, max_depth_m=maximum, max_depth_cell=max_cell)
