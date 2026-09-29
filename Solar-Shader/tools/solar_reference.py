from __future__ import annotations

import math
from typing import Sequence

Vec3 = tuple[float, float, float]
Mat4 = Sequence[Sequence[float]]


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def quantize_unorm(value: float, bits: int) -> int:
    if bits <= 0:
        raise ValueError("bits must be positive")
    maximum = (1 << bits) - 1
    return int(round(_clamp01(value) * maximum))


def dequantize_unorm(code: int, bits: int) -> float:
    if bits <= 0:
        raise ValueError("bits must be positive")
    maximum = (1 << bits) - 1
    return max(0, min(maximum, int(code))) / float(maximum)


def _normalize3(value: Vec3) -> Vec3:
    length_sq = sum(component * component for component in value)
    if length_sq <= 1e-30:
        raise ValueError("zero-length vector")
    inv = 1.0 / math.sqrt(length_sq)
    return tuple(component * inv for component in value)  # type: ignore[return-value]


def _sign_not_zero(value: float) -> float:
    return -1.0 if value < 0.0 else 1.0


def oct_encode(normal: Vec3) -> tuple[float, float]:
    x, y, z = _normalize3(normal)
    inv_l1 = 1.0 / (abs(x) + abs(y) + abs(z))
    x *= inv_l1
    y *= inv_l1
    z *= inv_l1
    if z < 0.0:
        old_x = x
        x = (1.0 - abs(y)) * _sign_not_zero(old_x)
        y = (1.0 - abs(old_x)) * _sign_not_zero(y)
    return (_clamp01(x * 0.5 + 0.5), _clamp01(y * 0.5 + 0.5))


def oct_decode(encoded: tuple[float, float]) -> Vec3:
    x = _clamp01(encoded[0]) * 2.0 - 1.0
    y = _clamp01(encoded[1]) * 2.0 - 1.0
    z = 1.0 - abs(x) - abs(y)
    t = max(0.0, min(1.0, -z))
    x += -t if x >= 0.0 else t
    y += -t if y >= 0.0 else t
    return _normalize3((x, y, z))


def pack_light_pair(block_light: float, sky_light: float) -> float:
    block = quantize_unorm(block_light, 5)
    sky = quantize_unorm(sky_light, 5)
    packed = block | (sky << 5)
    return packed / 1023.0


def unpack_light_pair(encoded: float) -> tuple[float, float]:
    packed = int(round(_clamp01(encoded) * 1023.0))
    block = packed & 31
    sky = (packed >> 5) & 31
    return (block / 31.0, sky / 31.0)


def encode_surface_class(surface_class: int) -> float:
    return max(0, min(3, int(surface_class))) / 3.0


def decode_surface_class(encoded: float) -> int:
    return max(0, min(3, int(round(_clamp01(encoded) * 3.0))))


def normalize_lightmap_coord(raw_uv: tuple[float, float]) -> tuple[float, float]:
    scale = 30.0 / 32.0
    offset = 1.0 / 32.0
    return tuple(_clamp01(component / scale - offset) for component in raw_uv)  # type: ignore[return-value]


def _mat4_mul_vec4(matrix: Mat4, vector: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
        raise ValueError("matrix must be 4x4")
    return tuple(sum(float(matrix[row][col]) * vector[col] for col in range(4)) for row in range(4))  # type: ignore[return-value]


def project_view_position(position: Vec3, projection: Mat4) -> tuple[float, float, float]:
    clip = _mat4_mul_vec4(projection, (position[0], position[1], position[2], 1.0))
    if abs(clip[3]) <= 1e-15:
        raise ValueError("projection produced w=0")
    ndc = (clip[0] / clip[3], clip[1] / clip[3], clip[2] / clip[3])
    return (
        ndc[0] * 0.5 + 0.5,
        ndc[1] * 0.5 + 0.5,
        ndc[2] * 0.5 + 0.5,
    )


def reconstruct_view_position(
    screen: tuple[float, float, float],
    projection_inverse: Mat4,
) -> Vec3:
    clip = (
        screen[0] * 2.0 - 1.0,
        screen[1] * 2.0 - 1.0,
        screen[2] * 2.0 - 1.0,
        1.0,
    )
    view = _mat4_mul_vec4(projection_inverse, clip)
    if abs(view[3]) <= 1e-15:
        raise ValueError("reconstruction produced w=0")
    inv_w = 1.0 / view[3]
    return (view[0] * inv_w, view[1] * inv_w, view[2] * inv_w)
