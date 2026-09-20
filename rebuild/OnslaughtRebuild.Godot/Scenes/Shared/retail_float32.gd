# SPDX-License-Identifier: GPL-3.0-or-later
@tool
class_name RetailFloat32
extends RefCounted

# Presentation ports retain the old C# single-precision stores and ties-to-even
# rounding. This helper does not introduce a second simulation or clock owner.
const _SINGLE_PRECISION_VECTORS: bool = Vector3(16777217.0, 0.0, 0.0).x == 16777216.0

static func value(number: float) -> float:
    # The pinned official engine stores Vector3 components as binary32. This
    # avoids allocating a packed array for every intermediate terrain value.
    # Retain the portable store if a caller uses a double-precision engine.
    if _SINGLE_PRECISION_VECTORS:
        return Vector3(number, 0.0, 0.0).x
    return PackedFloat32Array([number])[0]

static func round_even(number: float) -> float:
    var lower: float = floor(number)
    var fraction: float = number - lower
    if fraction < 0.5:
        return lower
    if fraction > 0.5:
        return lower + 1.0
    return lower if int(lower) % 2 == 0 else lower + 1.0
