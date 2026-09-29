from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

from solar_reference import (
    decode_surface_class,
    dequantize_unorm,
    encode_surface_class,
    normalize_lightmap_coord,
    oct_decode,
    oct_encode,
    pack_light_pair,
    project_view_position,
    quantize_unorm,
    reconstruct_view_position,
    unpack_light_pair,
)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _normalize(v):
    length = math.sqrt(_dot(v, v))
    return tuple(x / length for x in v)


def _perspective(fov_y, aspect, near, far):
    f = 1.0 / math.tan(fov_y * 0.5)
    return (
        (f / aspect, 0.0, 0.0, 0.0),
        (0.0, f, 0.0, 0.0),
        (0.0, 0.0, (far + near) / (near - far), (2.0 * far * near) / (near - far)),
        (0.0, 0.0, -1.0, 0.0),
    )


def _invert4(m):
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(4)] for i, row in enumerate(m)]
    for col in range(4):
        pivot = max(range(col, 4), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("singular")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(4):
            if row == col:
                continue
            factor = a[row][col]
            a[row] = [x - factor * y for x, y in zip(a[row], a[col])]
    return tuple(tuple(row[4:]) for row in a)


class SolarReferenceTests(unittest.TestCase):
    def test_oct_axes_round_trip_after_10bit_quantization(self):
        axes = [
            (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0), (0.0, -1.0, 0.0),
            (0.0, 0.0, 1.0), (0.0, 0.0, -1.0),
        ]
        for normal in axes:
            encoded = oct_encode(normal)
            quantized = tuple(dequantize_unorm(quantize_unorm(v, 10), 10) for v in encoded)
            decoded = oct_decode(quantized)
            self.assertGreaterEqual(_dot(normal, decoded), 0.9998)

    def test_oct_arbitrary_normals_keep_dot_at_least_0_9998(self):
        normals = [
            _normalize((0.3, 0.8, 0.5)),
            _normalize((-0.7, 0.2, 0.68)),
            _normalize((0.01, -0.999, 0.04)),
            _normalize((-0.31, -0.47, -0.826)),
        ]
        for normal in normals:
            encoded = oct_encode(normal)
            quantized = tuple(dequantize_unorm(quantize_unorm(v, 10), 10) for v in encoded)
            decoded = oct_decode(quantized)
            self.assertGreaterEqual(_dot(normal, decoded), 0.9998)

    def test_light_pair_round_trip_error_is_at_most_half_5bit_step(self):
        tolerance = 0.5 / 31.0 + 1e-6
        for block, sky in [(0.0, 0.0), (1.0, 1.0), (0.2, 0.8), (0.51, 0.49)]:
            rb, rs = unpack_light_pair(pack_light_pair(block, sky))
            self.assertLessEqual(abs(rb - block), tolerance)
            self.assertLessEqual(abs(rs - sky), tolerance)

    def test_lightmap_normalization_matches_documented_formula_endpoints(self):
        scale = 30.0 / 32.0
        offset = 1.0 / 32.0
        raw_zero = offset * scale
        raw_one = (1.0 + offset) * scale
        self.assertEqual(normalize_lightmap_coord((raw_zero, raw_zero)), (0.0, 0.0))
        self.assertEqual(normalize_lightmap_coord((raw_one, raw_one)), (1.0, 1.0))

    def test_lightmap_normalization_clamps_outside_documented_endpoints(self):
        low, high = normalize_lightmap_coord((-1.0, 2.0))
        self.assertEqual(low, 0.0)
        self.assertEqual(high, 1.0)

    def test_surface_classes_zero_through_three_round_trip_exactly(self):
        for value in range(4):
            self.assertEqual(decode_surface_class(encode_surface_class(value)), value)

    def test_reconstruction_round_trips_center_near_and_far_points(self):
        projection = _perspective(math.radians(70.0), 16.0 / 9.0, 0.1, 512.0)
        inverse = _invert4(projection)
        points = [(0.0, 0.0, -0.11), (0.0, 0.0, -5.0), (0.0, 0.0, -400.0)]
        for point in points:
            screen = project_view_position(point, projection)
            recovered = reconstruct_view_position(screen, inverse)
            for actual, expected in zip(recovered, point):
                self.assertAlmostEqual(actual, expected, places=5)

    def test_reconstruction_round_trips_viewport_corners(self):
        projection = _perspective(math.radians(70.0), 16.0 / 9.0, 0.1, 512.0)
        inverse = _invert4(projection)
        for point in [(-2.0, -1.0, -4.0), (2.0, 1.0, -4.0), (-8.0, 3.0, -20.0), (8.0, -3.0, -20.0)]:
            screen = project_view_position(point, projection)
            recovered = reconstruct_view_position(screen, inverse)
            for actual, expected in zip(recovered, point):
                self.assertAlmostEqual(actual, expected, places=5)

    def test_reconstruction_outputs_only_finite_values_for_valid_depths(self):
        projection = _perspective(math.radians(70.0), 16.0 / 9.0, 0.1, 512.0)
        inverse = _invert4(projection)
        for screen in [(0.5, 0.5, 0.1), (0.0, 0.0, 0.5), (1.0, 1.0, 0.999)]:
            recovered = reconstruct_view_position(screen, inverse)
            self.assertTrue(all(math.isfinite(value) for value in recovered))


if __name__ == "__main__":
    unittest.main()
