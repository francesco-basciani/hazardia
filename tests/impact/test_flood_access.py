"""Controlled synthetic geometries and depths, independent of the saved replay."""
import unittest

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from hazardia.flood_access import assess_edge, compare_access
from hazardia.flood_road_depth import RoadDepth


def results(edges, threshold=.1):
    return compare_access(edges, [{"id": "settlement", "node": "a"}],
                          [{"id": "hospital", "node": "b"}], threshold)["pairs"][0]


def edge(name, u, v, depth=0, length=1, **metadata):
    return dict(id=name, u=u, v=v, length=length, max_depth_m=depth,
                structure={}, coverage=dict(valid=1, nodata=0, outside=0)) | metadata


class FloodAccessTest(unittest.TestCase):
    def test_detour_and_identical_endpoints(self):
        edges = [edge("short", "a", "b", .11), edge("long1", "a", "c"), edge("long2", "c", "b")]
        pair = results(edges)
        self.assertEqual(pair["status"], "detour")
        self.assertEqual(pair["reference"], dict(distance_m=1, arcs=["short"]))
        self.assertEqual(pair["scenario"], dict(distance_m=2, arcs=["long1", "long2"]))
        self.assertEqual(pair["explanatory_arcs"], ["short"])
        self.assertEqual(results(edges, .15)["status"], "available")

    def test_route_lost(self):
        pair = results([edge("closed", "a", "b", .2)])
        self.assertEqual(pair["status"], "interrupted")
        self.assertIsNone(pair["scenario"])
        self.assertIsNone(pair["possible"])

    def test_uncertain_nodata_path_after_closure(self):
        unknown = edge("gap", "a", "c", None, coverage=dict(valid=0, nodata=1, outside=0))
        pair = results([edge("short", "a", "b", .2), unknown, edge("last", "c", "b")])
        self.assertEqual(pair["status"], "indeterminate")
        self.assertIsNone(pair["scenario"])
        self.assertEqual(pair["possible"]["arcs"], ["gap", "last"])
        self.assertEqual(pair["explanatory_arcs"], ["short", "gap"])

    def test_direction_and_missing_reference(self):
        self.assertEqual(results([edge("one-way", "b", "a")])["status"], "no_reference")

    def test_structure_overrides_ground_depth(self):
        bridge = edge("bridge", "a", "b", .9, structure={"bridge": "viaduct"})
        self.assertEqual(assess_edge(bridge, .1), ("unknown", "structure_depth_unqualified"))
        self.assertEqual(results([bridge])["status"], "indeterminate")

    def test_dry_origin_wet_crossing_and_mask(self):
        with MemoryFile() as file:
            with file.open(driver="GTiff", width=4, height=1, count=1, dtype="float32",
                           crs="EPSG:4326", transform=from_origin(10, 43, .01, .01), nodata=-9999) as dataset:
                dataset.write(np.array([[0, .25, 0, -9999]], dtype="float32"), 1)
                depth = RoadDepth(dataset)
                a, b = (10.005, 42.995), (10.025, 42.995)
                self.assertEqual(depth.point(a)["depth_m"], 0)
                self.assertEqual(depth.point(b)["depth_m"], 0)
                support = depth.segment(a, b)
                self.assertEqual(support["max_depth_cell"], [0, 1])
                self.assertEqual(support["max_depth_m"], .25)
                self.assertEqual(results([edge("crossing", "a", "b", **support)])["status"], "interrupted")
                outside = depth.segment(b, (10.045, 42.995))
                self.assertAlmostEqual(outside["coverage"]["valid"], .25)
                self.assertAlmostEqual(outside["coverage"]["nodata"], .5)
                self.assertAlmostEqual(outside["coverage"]["outside"], .25)
                self.assertEqual(outside["max_depth_m"], 0)
                nodata = depth.segment(b, (10.035, 42.995))
                self.assertEqual(results([edge("nodata", "a", "b", **nodata)])["status"], "indeterminate")


if __name__ == "__main__":
    unittest.main()
