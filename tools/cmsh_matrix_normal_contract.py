#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the public-safe CMSH typed matrix/normal deformation receipt."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

import cmsh_skinning_contract as p1

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

from cmsh_static_preview import inflate_aya, parse_cmsh_stream  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402

SCHEMA = "onslaught.cmsh-matrix-normal-deformation.v1"
SENTINEL_BIG_SHA256 = "3c9092f3b7b16289e09e16e475303bef3fc072994ebf67b3ab7d88ed544a6967"
EXPECTED_SHADER_INFO = {
    "1fb683058f29fe7cb5a4df4581d55fa6ba54b6edf4ef72526c4a2bc2401a4045": {
        "dwords": 143,
        "normal": False,
    },
    "f3b90c830f566d2d19a9f801925d400510bbe7fab5397ae9825f867d9a0d596c": {
        "dwords": 173,
        "normal": True,
    },
}

STATIC_RANGE_PINS: tuple[tuple[str, int, int, str], ...] = (
    ("per-bone builder", 0x0054A727, 2331, "d872ab8436e562f24429b155660a1f78968a3596d2e515a64edd8091de7a4800"),
    ("final affine chain", 0x0054AE71, 465, "1c4304a434d4bb5b176741e2d6afd52518609573aac51c1fde0e9c8f704d9b49"),
    ("palette scale/copy", 0x0054B0AD, 376, "362f12c6af54fcff8a238c5badfee7d5f7794b362af58a6585099e74821ebee2"),
    ("scalar inverse", 0x00576E10, 927, "e9f99f35e7a5a193a075114b62abe9633114bbadba211802e16494e1a53392b1"),
    ("translation builder", 0x0057726D, 92, "02322e3ea8810906597f2d023267fb74577ebe41b2cd6b2fe91c3411a8eda970"),
    ("scalar multiply", 0x005961D0, 227, "7045ca54660b7851e8281e7e4e478343850b97b2f370d8d3b08cfe34e15b2463"),
    ("dispatch seed", 0x00596341, 69, "533ef6677a9f9dffe6293d46908d38b035e8f85ad06d082134370ee6550a2150"),
    ("dispatch variant A", 0x005980BE, 366, "7bced89f65536aae128a2c67ea642d1c690410e6d6108f46e1ef9cb4e0460278"),
    ("dispatch variant B", 0x0059822C, 356, "914cb170b9b0065d3d84ae50313c69e636fc460f17bf5513acd0d6221341e673"),
    ("feature overrides", 0x00598474, 654, "d950ed192ea544298c00354b401737e5223b4990e638d3872f97fe8026dfe80a"),
    ("SIMD inverse", 0x005A2B2D, 764, "8ba6e637fa2a5ff897b1647c15cd00b95654dbf07c373dc1c38b177839b2e660"),
    ("SIMD multiply", 0x005A0CC2, 308, "e389c06c3e25676d5beedf8497b611893f3bad76968cd2b1443ba416408dd00b"),
    ("packed multiply", 0x005A5BD7, 562, "c4a9b44401f014cb18140a458292a02753bb9a0631a798b4e3a5d97e8b21aaa2"),
    ("packed inverse", 0x005A8F5D, 738, "b295e761b709b6017e8d285e5c5152ca8fe7fd8dd317abc51c6b8c77d79c9b3d"),
    ("packed inverse wrapper", 0x005A996B, 28, "7a3db866d271eeb57d307293732d8a0f6df78792434900be0c16455cf5bcc9f9"),
)

MATRIX_CALL_PINS: tuple[tuple[str, int, int], ...] = (
    ("frame-zero sample", 0x0054A74E, 0x004B0FB0),
    ("current sample", 0x0054A786, 0x004B0FB0),
    ("invert bind rotation", 0x0054AF39, 0x00576E0A),
    ("build current translation", 0x0054AF55, 0x00577267),
    ("build bind translation", 0x0054AF7A, 0x00577267),
    ("invert bind translation", 0x0054AF91, 0x00576E0A),
    ("multiply bind inverse", 0x0054AFAE, 0x005768FE),
    ("multiply current rotation", 0x0054AFE0, 0x005768FE),
    ("multiply current translation", 0x0054B012, 0x005768FE),
)

DISPATCH_POINTER_PINS: tuple[tuple[str, int, int], ...] = (
    ("seed multiply", 0x0059635D, 0x005961D0),
    ("variant A multiply", 0x005980E5, 0x005A0CC2),
    ("variant B multiply", 0x00598253, 0x005A0CC2),
    ("feature multiply", 0x005984A7, 0x005A5BD7),
    ("variant A inverse", 0x0059814E, 0x005A2B2D),
    ("variant B inverse", 0x005982BC, 0x005A2B2D),
    ("feature inverse", 0x00598509, 0x005A996B),
    ("feature inverse override", 0x0059868E, 0x005A8F5D),
)


MATRIX_OPERATION_TABLE: tuple[dict[str, object], ...] = (
    {
        "rowId": "MATRIX-001",
        "va": "0x0054a74e",
        "operation": "sample_pose",
        "input": "frame_zero",
        "outRotation": "R_bind",
        "outTranslation": "t_bind",
    },
    {
        "rowId": "MATRIX-002",
        "va": "0x0054a786",
        "operation": "sample_pose",
        "input": "current_interpolated",
        "outRotation": "R_current",
        "outTranslation": "t_current",
    },
    {
        "rowId": "MATRIX-003",
        "va": "0x0054af39",
        "operation": "inverse",
        "input": "R_bind",
        "out": "inverse(R_bind)",
    },
    {
        "rowId": "MATRIX-004",
        "va": "0x0054af55",
        "operation": "build_translation",
        "input": "t_current",
        "out": "T_current",
    },
    {
        "rowId": "MATRIX-005",
        "va": "0x0054af7a",
        "operation": "build_translation",
        "input": "t_bind",
        "out": "T_bind",
    },
    {
        "rowId": "MATRIX-006",
        "va": "0x0054af91",
        "operation": "inverse",
        "input": "T_bind",
        "out": "inverse(T_bind)",
    },
    {
        "rowId": "MATRIX-007",
        "va": "0x0054afae",
        "operation": "multiply",
        "left": "inverse(T_bind)",
        "right": "inverse(R_bind)",
        "out": "bind_inverse",
    },
    {
        "rowId": "MATRIX-008",
        "va": "0x0054afe0",
        "operation": "multiply",
        "left": "bind_inverse",
        "right": "R_current",
        "out": "rotation_delta",
    },
    {
        "rowId": "MATRIX-009",
        "va": "0x0054b012",
        "operation": "multiply",
        "left": "rotation_delta",
        "right": "T_current",
        "out": "P_unscaled",
    },
    {
        "rowId": "MATRIX-010",
        "va": "0x0054b0c3..0x0054b217",
        "operation": "scale_then_copy",
        "input": "P_unscaled",
        "scalarBits": "0x3eaaaaab",
        "out": "palette_global_0x009c69d4",
    },
)

RETAIL_NORMAL_TYPED_OPERATIONS: tuple[dict[str, object], ...] = (
    {"opcode": "dp3", "dst": "r4", "sources": ["v3", "c89"]},
    {"opcode": "lit", "dst": "r4", "sources": ["r4"]},
    {"opcode": "mad", "dst": "r4", "sources": ["r4.y", "c90", "r2"]},
    {"opcode": "dp3", "dst": "r0", "sources": ["v3", "c91"]},
    {"opcode": "lit", "dst": "r0", "sources": ["r0"]},
    {"opcode": "mad", "dst": "r0", "sources": ["r0.y", "c92", "r4"]},
    {"opcode": "mul", "dst": "oD0", "sources": ["r0", "v5"]},
)

VS11_OPCODE_OPERANDS: dict[int, tuple[str, int]] = {
    0x0001: ("mov", 2),
    0x0002: ("add", 3),
    0x0004: ("mad", 4),
    0x0005: ("mul", 3),
    0x0006: ("rcp", 2),
    0x0007: ("rsq", 2),
    0x0008: ("dp3", 3),
    0x0009: ("dp4", 3),
    0x0010: ("lit", 2),
    0x001F: ("dcl", 2),
}


def decode_vs11_tokens(tokens: Sequence[int]) -> dict[str, object]:
    """Decode the complete instruction envelope of one exact vs_1_1 token stream."""

    values = tuple(tokens)
    if not values or values[0] != 0xFFFE0101:
        raise ValueError("shader is not vs_1_1")
    if len(values) < 2 or values[-1] != 0x0000FFFF:
        raise ValueError("shader END token is absent or misplaced")
    cursor = 1
    opcodes: Counter[str] = Counter()
    instruction_rows: list[dict[str, object]] = []
    while cursor < len(values) - 1:
        opcode_value = values[cursor] & 0xFFFF
        definition = VS11_OPCODE_OPERANDS.get(opcode_value)
        if definition is None:
            raise ValueError(
                f"unclassified shader opcode 0x{opcode_value:04x} at token {cursor}"
            )
        opcode, operand_count = definition
        end = cursor + 1 + operand_count
        if end > len(values) - 1:
            raise ValueError(f"truncated {opcode} instruction at token {cursor}")
        instruction_rows.append(
            {
                "tokenIndex": cursor,
                "opcode": opcode,
                "tokens": 1 + operand_count,
            }
        )
        opcodes[opcode] += 1
        cursor = end
    if cursor != len(values) - 1:
        raise ValueError("shader instruction accounting did not reach END")
    return {
        "tokenCount": len(values),
        "instructionTokenCount": len(values) - 2,
        "instructionCount": len(instruction_rows),
        "opcodeCounts": dict(sorted(opcodes.items())),
        "instructions": instruction_rows,
        "unclassifiedTokens": 0,
        "unclassifiedInstructions": 0,
    }


def classify_normal_deformation_block(
    operations: Sequence[dict[str, object]],
) -> dict[str, object]:
    """Classify the exact normal-consuming linked-shader block, fail closed on drift."""

    values = tuple(operations)
    if len(values) != len(RETAIL_NORMAL_TYPED_OPERATIONS):
        raise ValueError("normal instruction drift")
    normal_consumers = [
        row for row in values if "v3" in row.get("sources", [])
    ]
    if any(row.get("opcode") == "dp4" for row in normal_consumers):
        raise ValueError("normal translation leakage through dp4")
    if any(
        source.startswith("c[") or source.startswith("c10")
        for row in normal_consumers
        for source in row.get("sources", [])
        if isinstance(source, str)
    ):
        raise ValueError("normal palette read or relative-address drift")
    if values != RETAIL_NORMAL_TYPED_OPERATIONS:
        raise ValueError("normal instruction drift")
    return {
        "instructions": 7,
        "tokens": 28,
        "serializedNormalConsumers": 2,
        "normalInputRegister": "v3",
        "consumerOpcodes": ["dp3", "dp3"],
        "lightingConstantRegisters": [89, 91],
        "paletteRows": [],
        "slotCoefficients": [0.0, 0.0, 0.0],
        "normalizationInstructions": 0,
        "translationIncluded": False,
        "deformation": "identity: serialized normal v3 reaches lighting dp3 instructions directly",
    }


def interpret_normal_consumer_block(
    normal: Sequence[float],
    constants: dict[int, Sequence[float]],
    *,
    position_lighting_base: Sequence[float],
    diffuse: Sequence[float],
    palette: Sequence[Sequence[float]],
) -> dict[str, object]:
    """Interpret the exact normal consumers and prove palette-invariant output."""

    classify_normal_deformation_block(RETAIL_NORMAL_TYPED_OPERATIONS)
    if len(normal) != 3:
        raise ValueError("normal must contain three elements")
    if len(position_lighting_base) != 4 or len(diffuse) != 4:
        raise ValueError("lighting base and diffuse inputs must contain four elements")
    if any(len(row) != 4 for row in palette):
        raise ValueError("palette rows must contain four elements")
    for register in (89, 90, 91, 92):
        if register not in constants or len(constants[register]) != 4:
            raise ValueError(f"synthetic constant c{register} is absent or malformed")
    dots = tuple(
        sum(float(normal[index]) * float(constants[register][index]) for index in range(3))
        for register in (89, 91)
    )
    first_lit_y = max(dots[0], 0.0)
    first = tuple(
        first_lit_y * float(constants[90][lane]) + float(position_lighting_base[lane])
        for lane in range(4)
    )
    second_lit_y = max(dots[1], 0.0)
    second = tuple(
        second_lit_y * float(constants[92][lane]) + first[lane]
        for lane in range(4)
    )
    return {
        "normalDotProducts": dots,
        "finalColor": tuple(second[lane] * float(diffuse[lane]) for lane in range(4)),
        "paletteReads": 0,
        "normalizationInstructions": 0,
    }


def validate_matrix_operation_table(rows: Sequence[dict[str, object]]) -> None:
    """Refuse matrix-order, inverse/transpose, and final scale-owner drift."""

    if len(rows) != len(MATRIX_OPERATION_TABLE):
        raise ValueError("matrix operation row denominator drift")
    for index, (actual, expected) in enumerate(zip(rows, MATRIX_OPERATION_TABLE)):
        if actual == expected:
            continue
        if index in (2, 5) and actual.get("operation") != "inverse":
            raise ValueError("matrix inverse/transpose mutation")
        if index in (6, 7, 8) and (
            actual.get("left") != expected.get("left")
            or actual.get("right") != expected.get("right")
        ):
            raise ValueError("matrix product order mutation")
        if index == 9:
            raise ValueError("matrix palette scale owner mutation")
        raise ValueError(f"matrix operation table drift at row {index + 1}")


def float32_from_bits(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def validate_preserved_position_contract(
    slot_coefficients: Sequence[float],
    *,
    scale_owner: str,
    scale_bits: int,
) -> None:
    """Keep the already-closed P1 scale owner and asymmetric slot combine exact."""

    scale = float32_from_bits(0x3EAAAAAB)
    actual = list(slot_coefficients)
    if actual == [scale, scale, scale]:
        raise ValueError("symmetric slot combine mutation")
    if actual != [0.0, 2.0 * scale, scale]:
        raise ValueError("position slot coefficient drift")
    if scale_owner != "CMeshRenderer__RenderMeshCore":
        raise ValueError("palette scale owner mutation")
    if scale_bits != 0x3EAAAAAB:
        raise ValueError("palette scale bits drift")


def multiply_matrix4x4(left: Sequence[float], right: Sequence[float]) -> tuple[float, ...]:
    """Multiply two row-major 4x4 matrices as the retail dispatch ABI does."""

    if len(left) != 16 or len(right) != 16:
        raise ValueError("matrix operands must each contain 16 elements")
    return tuple(
        sum(left[row * 4 + inner] * right[inner * 4 + column] for inner in range(4))
        for row in range(4)
        for column in range(4)
    )


def transpose_matrix4x4(matrix: Sequence[float]) -> tuple[float, ...]:
    if len(matrix) != 16:
        raise ValueError("matrix must contain 16 elements")
    return tuple(matrix[column * 4 + row] for row in range(4) for column in range(4))


def invert_matrix4x4(matrix: Sequence[float]) -> tuple[float, ...]:
    """Invert one nonsingular 4x4 matrix with deterministic Gauss-Jordan elimination."""

    if len(matrix) != 16:
        raise ValueError("matrix must contain 16 elements")
    rows = [
        [float(matrix[row * 4 + column]) for column in range(4)]
        + [1.0 if row == column else 0.0 for column in range(4)]
        for row in range(4)
    ]
    for column in range(4):
        pivot = max(range(column, 4), key=lambda row: abs(rows[row][column]))
        if rows[pivot][column] == 0.0:
            raise ValueError("matrix is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(4):
            if row == column:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[column])
            ]
    return tuple(rows[row][column + 4] for row in range(4) for column in range(4))


def translation_matrix4x4(translation: Sequence[float]) -> tuple[float, ...]:
    """Build the retail row-vector affine translation layout (translation in the last row)."""

    if len(translation) != 3:
        raise ValueError("translation must contain three elements")
    x, y, z = map(float, translation)
    return (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        x, y, z, 1.0,
    )


def matrix_order_adverse_control(
    bind_rotation: Sequence[float],
    bind_translation: Sequence[float],
    current_rotation: Sequence[float],
    current_translation: Sequence[float],
) -> dict[str, object]:
    """Evaluate the byte-selected chain and adverse product/transpose/inverse alternatives."""

    bind_t = translation_matrix4x4(bind_translation)
    current_t = translation_matrix4x4(current_translation)
    inverse_bind_t = invert_matrix4x4(bind_t)
    inverse_bind_r = invert_matrix4x4(bind_rotation)
    selected = multiply_matrix4x4(
        multiply_matrix4x4(
            multiply_matrix4x4(inverse_bind_t, inverse_bind_r),
            current_rotation,
        ),
        current_t,
    )
    reversed_product = multiply_matrix4x4(
        multiply_matrix4x4(
            multiply_matrix4x4(current_t, current_rotation),
            inverse_bind_r,
        ),
        inverse_bind_t,
    )
    missing_inverse = multiply_matrix4x4(
        multiply_matrix4x4(multiply_matrix4x4(bind_t, bind_rotation), current_rotation),
        current_t,
    )
    return {
        "selectedFormula": "inverse(T_bind) * inverse(R_bind) * R_current * T_current",
        "selected": selected,
        "reversedProduct": reversed_product,
        "transposeMutation": transpose_matrix4x4(selected),
        "missingInverse": missing_inverse,
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return _sha256_bytes(payload.encode("utf-8"))


def _register_name(token: int, *, destination: bool) -> str:
    register_number = token & 0x7FF
    register_type = (token >> 28) & 0x7
    prefixes = {0: "r", 1: "v", 2: "c", 3: "a", 4: "oPos", 5: "oD", 6: "oT"}
    prefix = prefixes.get(register_type, f"reg{register_type}_")
    if prefix == "oPos":
        base = "oPos"
    else:
        base = f"{prefix}{register_number}"
    if not destination and register_type == 2 and (token & 0x2000):
        base = f"c[10+a0.x+{register_number - 10}]"
    if destination:
        mask = (token >> 16) & 0xF
        if mask != 0xF:
            base += "." + "".join(
                lane for bit, lane in ((1, "x"), (2, "y"), (4, "z"), (8, "w")) if mask & bit
            )
        return base
    swizzle_bits = (token >> 16) & 0xFF
    lanes = tuple((swizzle_bits >> (index * 2)) & 0x3 for index in range(4))
    if lanes != (0, 1, 2, 3):
        lane_names = "xyzw"
        if len(set(lanes)) == 1:
            base += "." + lane_names[lanes[0]]
        else:
            base += "." + "".join(lane_names[index] for index in lanes)
    if ((token >> 24) & 0xF) == 1:
        base = "-" + base
    return base


def _decode_vs11_typed_operations(tokens: Sequence[int]) -> list[dict[str, object]]:
    values = tuple(tokens)
    decode_vs11_tokens(values)
    semantic_names = {
        0: "position",
        1: "blendweight",
        2: "blendindices",
        3: "normal",
        5: "texcoord",
        10: "color",
    }
    rows: list[dict[str, object]] = []
    cursor = 1
    while cursor < len(values) - 1:
        opcode, operand_count = VS11_OPCODE_OPERANDS[values[cursor] & 0xFFFF]
        operands = values[cursor + 1 : cursor + 1 + operand_count]
        if opcode == "dcl":
            rows.append(
                {
                    "opcode": opcode,
                    "semantic": semantic_names.get(operands[0] & 0x1F, f"usage{operands[0] & 0x1F}"),
                    "dst": _register_name(operands[1], destination=True),
                }
            )
        else:
            rows.append(
                {
                    "opcode": opcode,
                    "dst": _register_name(operands[0], destination=True),
                    "sources": [
                        _register_name(token, destination=False) for token in operands[1:]
                    ],
                }
            )
        cursor += 1 + operand_count
    return rows


def _contains_typed_block(
    operations: Sequence[dict[str, object]],
    expected: Sequence[dict[str, object]],
) -> bool:
    width = len(expected)
    return any(
        tuple(operations[start : start + width]) == tuple(expected)
        for start in range(len(operations) - width + 1)
    )


def _shader_tokens_from_text(text: str) -> list[tuple[int, ...]]:
    streams: list[tuple[int, ...]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("VS create "):
            continue
        match = re.search(r"\bdwords=(\d+)\s+tok=([0-9A-Fa-f,]+)$", line)
        if match is None:
            raise ValueError(f"line {line_number}: malformed VS create row")
        tokens = tuple(int(value, 16) for value in match.group(2).split(","))
        if len(tokens) != int(match.group(1)):
            raise ValueError(f"line {line_number}: declared dword count disagrees with token stream")
        streams.append(tokens)
    return streams


def _analyze_linked_shader(tokens: tuple[int, ...]) -> dict[str, object]:
    digest = _sha256_bytes(b"".join(value.to_bytes(4, "little") for value in tokens))
    expected = EXPECTED_SHADER_INFO.get(digest)
    if expected is None:
        raise ValueError(f"linked skinning shader identity drift: {digest}")
    if len(tokens) != expected["dwords"]:
        raise ValueError("linked skinning shader token denominator drift")
    if p1.classify_shader_tokens(tokens) != "RETAIL_SLOT0_DEAD":
        raise ValueError("prior position core drift")
    accounting = decode_vs11_tokens(tokens)
    operations = _decode_vs11_typed_operations(tokens)
    has_normal = _contains_typed_block(operations, RETAIL_NORMAL_TYPED_OPERATIONS)
    if has_normal != expected["normal"]:
        raise ValueError("normal-bearing shader classification drift")
    normal_sources = [
        row
        for row in operations
        if any(source == "v3" for source in row.get("sources", []))
    ]
    normal_declarations = [
        row for row in operations if row.get("opcode") == "dcl" and row.get("semantic") == "normal"
    ]
    if has_normal:
        classify_normal_deformation_block(RETAIL_NORMAL_TYPED_OPERATIONS)
        if len(normal_sources) != 2 or len(normal_declarations) != 1:
            raise ValueError("normal register consumer/declaration denominator drift")
    elif normal_sources or normal_declarations:
        raise ValueError("no-normal shader unexpectedly consumes or declares a normal")
    return {
        "shaderSha256": digest,
        "dwords": len(tokens),
        "instructionCount": accounting["instructionCount"],
        "opcodeCounts": accounting["opcodeCounts"],
        "normalBearing": has_normal,
        "normalConsumerInstructions": len(normal_sources),
        "normalPaletteReads": 0,
        "unclassifiedTokens": 0,
        "unclassifiedInstructions": 0,
    }


def _analyze_capture_shaders(
    capture_text_by_label: dict[str, str],
    capture_hash_by_label: dict[str, str],
) -> dict[str, object]:
    instances: list[dict[str, object]] = []
    unique_rows: dict[str, dict[str, object]] = {}
    capture_rows: list[dict[str, object]] = []
    for label in sorted(capture_text_by_label):
        rows: list[dict[str, object]] = []
        for tokens in _shader_tokens_from_text(capture_text_by_label[label]):
            digest = _sha256_bytes(b"".join(value.to_bytes(4, "little") for value in tokens))
            if digest not in EXPECTED_SHADER_INFO:
                continue
            analysis = _analyze_linked_shader(tokens)
            rows.append(analysis)
            instances.append(analysis)
            prior = unique_rows.setdefault(digest, analysis)
            if prior != analysis:
                raise ValueError("same shader identity decoded inconsistently across captures")
        if {str(row["shaderSha256"]) for row in rows} != set(EXPECTED_SHADER_INFO):
            raise ValueError(f"capture {label} does not contain both exact linked shaders")
        if len(rows) != 2:
            raise ValueError(f"capture {label} linked shader instance denominator drift")
        capture_rows.append(
            {
                "label": label,
                "logSha256": capture_hash_by_label[label],
                "shaderInstances": len(rows),
                "shaderSha256": sorted(str(row["shaderSha256"]) for row in rows),
            }
        )
    if len(instances) != 6 or len(unique_rows) != 2:
        raise ValueError("six-instance/two-identity shader denominator drift")
    return {
        "instances": len(instances),
        "uniqueShaders": len(unique_rows),
        "normalBearingInstances": sum(bool(row["normalBearing"]) for row in instances),
        "noNormalInstances": sum(not bool(row["normalBearing"]) for row in instances),
        "totalTokens": sum(int(row["dwords"]) for row in instances),
        "totalInstructions": sum(int(row["instructionCount"]) for row in instances),
        "unclassifiedTokens": sum(int(row["unclassifiedTokens"]) for row in instances),
        "unclassifiedInstructions": sum(
            int(row["unclassifiedInstructions"]) for row in instances
        ),
        "shaders": [unique_rows[key] for key in sorted(unique_rows)],
        "captures": capture_rows,
    }


def _verify_static_matrix_contract(pe: p1.PeImage) -> dict[str, object]:
    range_rows: list[dict[str, object]] = []
    for role, va, size, expected_hash in STATIC_RANGE_PINS:
        actual = pe.range_sha256(va, size)
        if actual != expected_hash:
            raise ValueError(f"{role} range hash drift: {actual}")
        range_rows.append(
            {
                "role": role,
                "va": f"0x{va:08x}",
                "bytes": size,
                "sha256": actual,
            }
        )
    call_rows: list[dict[str, str]] = []
    for role, call_va, expected_target in MATRIX_CALL_PINS:
        target = pe.rel32_call_target(call_va)
        if target != expected_target:
            raise ValueError(f"{role} target drift at 0x{call_va:08x}")
        call_rows.append(
            {
                "role": role,
                "callVa": f"0x{call_va:08x}",
                "targetVa": f"0x{target:08x}",
            }
        )
    dispatch_rows: list[dict[str, str]] = []
    for role, pointer_va, expected_target in DISPATCH_POINTER_PINS:
        target = struct.unpack("<I", pe.read_va(pointer_va, 4))[0]
        if target != expected_target:
            raise ValueError(f"{role} pointer drift at 0x{pointer_va:08x}")
        dispatch_rows.append(
            {
                "role": role,
                "pointerVa": f"0x{pointer_va:08x}",
                "targetVa": f"0x{target:08x}",
            }
        )
    validate_matrix_operation_table(MATRIX_OPERATION_TABLE)
    palette_scale = p1.verify_renderer_palette_scale(pe)
    return {
        "ranges": range_rows,
        "calls": call_rows,
        "dispatchImplementations": dispatch_rows,
        "paletteScale": palette_scale,
    }


def _first_palette_block(text: str) -> tuple[tuple[float, float, float, float], ...]:
    pending: dict[int, tuple[float, float, float, float]] | None = None
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("VSC "):
            continue
        match = re.search(r"\breg=(\d+)\s+count=(\d+)\s+v=([^ ]+)$", line)
        if match is None:
            raise ValueError(f"line {line_number}: malformed VSC row")
        register = int(match.group(1))
        values = tuple(float(value) for value in match.group(3).split(","))
        if int(match.group(2)) != 1 or len(values) != 4 or not all(map(math.isfinite, values)):
            raise ValueError(f"line {line_number}: unsupported VSC row")
        row = values  # type: ignore[assignment]
        if register == 7 and abs(values[0] - 1 / 3) < 1e-7:
            pending = {register: row}
        elif pending is not None and 8 <= register <= 51:
            pending[register] = row
            if register == 51 and all(index in pending for index in range(7, 52)):
                return tuple(pending[index] for index in range(10, 52))
    raise ValueError("capture has no complete c10-c51 palette block")


def _read_sample_normal(data_root: Path) -> tuple[tuple[float, float, float], str]:
    path = data_root / "resources" / "meshes" / "m_Sentinel Arm Big.msh.aya"
    source = p1._read(path)
    digest = _sha256_bytes(source)
    if digest != SENTINEL_BIG_SHA256:
        raise ValueError(f"Sentinel Big source hash drift: {digest}")
    mesh = parse_cmsh_stream(inflate_aya(source))
    carrier = next(part for part in mesh.file_parts() if part.bones)
    normal = carrier.vertices[0].normal
    if normal is None or len(normal) != 3:
        raise ValueError("Sentinel Big sample vertex has no serialized normal")
    return tuple(float(value) for value in normal), digest


def _adverse_matrix_receipt() -> dict[str, object]:
    control = matrix_order_adverse_control(
        (
            1.0, 2.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 2.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ),
        (3.0, -2.0, 5.0),
        (
            0.0, 1.0, 0.0, 0.0,
            -1.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ),
        (-7.0, 11.0, 13.0),
    )
    hashes = {
        key: _hash_json(control[key])
        for key in ("selected", "reversedProduct", "transposeMutation", "missingInverse")
    }
    if len(set(hashes.values())) != len(hashes):
        raise ValueError("adverse matrices do not discriminate all typed alternatives")
    return {
        "inputClass": "synthetic non-commuting shear/rotation/scale plus adverse translations",
        "selectedFormula": control["selectedFormula"],
        "outputSha256": hashes,
        "allAlternativesDistinct": True,
    }


def build_contract(
    data_root: Path,
    mirror_index: Path,
    pristine_exe: Path,
    capture_logs: list[Path],
) -> dict[str, object]:
    """Build the focused extension while replaying the complete landed P1 contract."""

    data_root = Path(os.path.abspath(data_root))
    mirror_index = Path(os.path.abspath(mirror_index))
    pristine_exe = Path(os.path.abspath(pristine_exe))
    capture_logs = [Path(os.path.abspath(path)) for path in capture_logs]
    prior = p1.build_contract(data_root, mirror_index, pristine_exe, capture_logs)
    slot_coefficients = [float(value) for value in prior["formula"]["executedSlotWeights"]]
    validate_preserved_position_contract(
        slot_coefficients,
        scale_owner=str(prior["staticRuntime"]["rendererPaletteScale"]["owner"]),
        scale_bits=int(str(prior["formula"]["paletteScaleBits"]), 16),
    )
    exe_bytes = p1._read(pristine_exe)
    if _sha256_bytes(exe_bytes) != p1.PRISTINE_SHA256:
        raise ValueError("pristine executable identity drift")
    static = _verify_static_matrix_contract(p1.PeImage(exe_bytes))

    capture_text_by_label: dict[str, str] = {}
    capture_hash_by_label: dict[str, str] = {}
    for path in capture_logs:
        payload = p1._read(path)
        digest = _sha256_bytes(payload)
        expected = p1.EXPECTED_CAPTURE_LOGS.get(digest)
        if expected is None:
            raise ValueError(f"capture log is not in the pinned evidence set: {digest}")
        label = expected[0]
        capture_text_by_label[label] = payload.decode("utf-8")
        capture_hash_by_label[label] = digest
    if set(capture_hash_by_label.values()) != set(p1.EXPECTED_CAPTURE_LOGS):
        raise ValueError("capture set is incomplete or duplicated")
    linked_shaders = _analyze_capture_shaders(capture_text_by_label, capture_hash_by_label)

    normal, sample_mesh_hash = _read_sample_normal(data_root)
    palette = _first_palette_block(capture_text_by_label["vskin-lvl800"])
    adverse_palette = tuple(
        (-row[0], row[1] + 9.0, row[2] - 11.0, row[3] + 1000.0)
        for row in palette
    )
    synthetic_constants = {
        89: (1.0, 0.0, 0.0, 0.0),
        90: (0.2, 0.3, 0.4, 0.5),
        91: (0.0, 1.0, 0.0, 0.0),
        92: (0.7, 0.6, 0.5, 0.4),
    }
    control_args = {
        "position_lighting_base": (0.1, 0.2, 0.3, 0.4),
        "diffuse": (0.8, 0.7, 0.6, 0.5),
    }
    base_output = interpret_normal_consumer_block(
        normal,
        synthetic_constants,
        palette=palette,
        **control_args,
    )
    adverse_output = interpret_normal_consumer_block(
        normal,
        synthetic_constants,
        palette=adverse_palette,
        **control_args,
    )
    if base_output != adverse_output:
        raise ValueError("normal output changed under adverse palette/translation mutation")
    normal_hash = _sha256_bytes(struct.pack("<3f", *normal))
    palette_hash = _sha256_bytes(
        b"".join(struct.pack("<4f", *row) for row in palette)
    )
    output_hash = _hash_json(base_output)
    normal_law = classify_normal_deformation_block(RETAIL_NORMAL_TYPED_OPERATIONS)

    return {
        "schema": SCHEMA,
        "specimens": {
            "pristineExeSha256": p1.PRISTINE_SHA256,
            "mirrorIndexSha256": p1.EXPECTED_INDEX_SHA256,
            "captureLogSha256": sorted(p1.EXPECTED_CAPTURE_LOGS),
            "linkedShaderSha256": sorted(EXPECTED_SHADER_INFO),
        },
        "matrixOrder": {
            "storage": "row-major 4x4",
            "vectorConvention": "row-vector affine; translation occupies the final row",
            "rowVectorFormula": "inverse(T_bind) * inverse(R_bind) * R_current * T_current",
            "equivalentColumnVectorFormula": "T_current_col * R_current_col * inverse(R_bind_col) * inverse(T_bind_col)",
            "operationTable": [dict(row) for row in MATRIX_OPERATION_TABLE],
            "staticEvidence": static,
            "adverseControl": _adverse_matrix_receipt(),
        },
        "linkedShaders": linked_shaders,
        "normalLaw": normal_law,
        "normalControl": {
            "sampleMeshSha256": sample_mesh_hash,
            "sampleVertexIndex": 0,
            "serializedNormalSha256": normal_hash,
            "sourcePaletteCaptureSha256": capture_hash_by_label["vskin-lvl800"],
            "sourcePaletteBlockSha256": palette_hash,
            "paletteRows": len(palette),
            "paletteReads": int(base_output["paletteReads"]),
            "baseOutputSha256": output_hash,
            "adversePaletteOutputSha256": _hash_json(adverse_output),
            "paletteInvariant": True,
            "controlClass": "exact token interpreter with synthetic lighting constants and an adverse mutation of all 42 captured palette rows",
        },
        "priorPositionContract": {
            "schema": prior["schema"],
            "slotCoefficients": slot_coefficients,
            "paletteScale": prior["formula"]["paletteScale"],
            "paletteScaleBits": prior["formula"]["paletteScaleBits"],
            "paletteScaleOwner": prior["staticRuntime"]["rendererPaletteScale"]["owner"],
            "meshSummary": prior["meshFamily"]["summary"],
            "runtimeReadback": prior["runtimeVertexReadback"],
        },
        "reuseLedger": [
            {"disposition": "REUSED", "path": "reverse-engineering/asset-formats/cmsh-matrix-palette-skinning.md", "sha256": "39a4979104f5a07b5db276f085a8344822f2e90e4014ec075a0e19cf9bf6d90d"},
            {"disposition": "REUSED", "path": "reverse-engineering/asset-formats/cmsh-matrix-palette-skinning.tsv", "sha256": "f98b2c7e501cf90702aba65481f3e879eadcc30a51f40dfa2d08c74b8b76a3af"},
            {"disposition": "REUSED", "path": "tools/cmsh_skinning_contract.py", "sha256": "f54cbcf75fc4548c4227c695d229cbf9b212f41c7538063357d5c9cc7a30395a"},
            {"disposition": "REUSED", "path": "tools/cmsh_skinning_contract_tests.py", "sha256": "90cc3487565470a7e489cd4e3f2310c9ecd4beefcf8d40c8c29c726faa2b94d9"},
            {"disposition": "REUSED", "path": "reverse-engineering/source-code/aya-resource-extractor-source-audit.md", "sha256": "b08368a114069eae78b7dc61b00a085588188af575c74bb672ec1d5598b98af0"},
            {"disposition": "REUSED", "path": "reverse-engineering/source-code/aya-resource-extractor-contract.tsv", "sha256": "0a4a58c68f8c9d91cac27fba89d7c49a25948ac4ef5616c10fb6b0ae300a024e"},
            {"disposition": "REUSED", "path": "reverse-engineering/binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md", "sha256": "8cc27f8d467628d158b3595813ad5e0c98ef123da273ceb22b38f686daf85259"},
            {"disposition": "REUSED", "path": "rebuild/tools/cmsh_static_preview.py", "sha256": "efd14ff88315408d656e5b3605e1b3dab4a3e323118f5997934cb936f48f1cc7"},
            {"disposition": "REUSED", "path": "tools/cmsh_animation_usage_census.py", "sha256": "510e03e5066f71ba1a89d604eefccb126589fcc16d27f339b90007526b02ec6c"},
            {"disposition": "EXTENDED", "path": "local-lab/PUZZLE-SKIN-WEIGHTS-2026-07-31.md", "sha256": "f894982b2d2bc71a1eadcf0990ecb588170313a9637706035a818b6d339150c5"},
            {"disposition": "EXTENDED", "path": "local-lab/ghidra-fullpass-2026-07-23/exports/W010/decompile/00549570_CMeshRenderer__RenderMeshCore.c", "sha256": "1fef07d87011225eaf5edfd307eaf10c83f32d4008f46ede6cf8378f0f631c71"},
            {"disposition": "EXTENDED", "path": "local-lab/ds-deep-review/bundles/shard-0210/00549570/disasm.tsv", "sha256": "fb88f2ca3e4a84e2c93539df428a4db15d461af11a2202f5ab73028cb21b3fbf"},
            {"disposition": "NEW_MEASUREMENT", "path": "tools/cmsh_matrix_normal_contract.py", "sha256": _sha256_bytes(Path(__file__).read_bytes())},
        ],
        "unknowns": [
            "The exact runtime-selected CPU dispatch implementation address was not captured; the pinned scalar, SIMD, and packed implementations share the typed ABI/equation, while low-order evaluation differences remain unmeasured.",
            "No transformed normal or pixel was observed at runtime; the closed law is the exact linked-token dataflow plus a synthetic interpreter control.",
            "Matrix handedness and semantic axis naming are not established by row-major storage and row-vector product order.",
        ],
        "completion": {
            "matrixOperationRows": len(MATRIX_OPERATION_TABLE),
            "linkedShaderInstances": linked_shaders["instances"],
            "unclassifiedShaderTokens": linked_shaders["unclassifiedTokens"],
            "unclassifiedShaderInstructions": linked_shaders["unclassifiedInstructions"],
            "normalPaletteReads": len(normal_law["paletteRows"]),
        },
    }


def _tsv_cell(value: object) -> str:
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def render_tsv(report: dict[str, object]) -> str:
    """Render typed operations, hashes, counts, boundaries, and falsifiers only."""

    columns = (
        "row_id", "row_kind", "subject", "evidence_class", "specimen_sha256",
        "denominator", "classified", "result", "evidence_boundary",
        "remaining_unknown", "falsifier",
    )
    rows: list[tuple[object, ...]] = []
    pristine = report["specimens"]["pristineExeSha256"]
    for operation in report["matrixOrder"]["operationTable"]:
        rows.append(
            (
                operation["rowId"], "matrix-operation", operation["operation"], "RETAIL_STATIC",
                pristine, "one typed operation", "all inputs/output/order classified",
                json.dumps(operation, sort_keys=True, separators=(",", ":")), operation["va"],
                "CPU implementation address and low-order evaluation differ by selected dispatch mode",
                "range/call/pointer hash drift or a non-commuting control matching an alternative",
            )
        )
    for index, static_range in enumerate(report["matrixOrder"]["staticEvidence"]["ranges"], 1):
        rows.append(
            (
                f"STATIC-{index:03d}", "retail-range", static_range["role"], "RETAIL_STATIC",
                static_range["sha256"], f"{static_range['bytes']} bytes", "exact range classified",
                static_range["va"], "hash-pinned pristine bytes; no payload tracked",
                "runtime reachability is not implied for every dispatch variant",
                "one byte or range-boundary change",
            )
        )
    for index, shader in enumerate(report["linkedShaders"]["shaders"], 1):
        rows.append(
            (
                f"SHADER-{index:03d}", "linked-shader", "normal-bearing" if shader["normalBearing"] else "no-normal variant",
                "COPIED_RUNTIME_MEASURED", shader["shaderSha256"],
                f"{shader['dwords']} tokens; {shader['instructionCount']} instructions",
                "zero unclassified tokens/instructions", json.dumps(shader["opcodeCounts"], sort_keys=True, separators=(",", ":")),
                f"normalBearing={shader['normalBearing']}; normalConsumers={shader['normalConsumerInstructions']}",
                "no runtime normal output or pixel observation",
                "token hash/count/opcode drift or any additional v3 consumer",
            )
        )
    normal = report["normalLaw"]
    rows.append(
        (
            "NORMAL-LAW", "normal-law", "released linked normal dataflow", "COPIED_RUNTIME_MEASURED",
            "+".join(report["specimens"]["linkedShaderSha256"]), "six shader instances; two identities",
            "two direct v3 dp3 consumers; zero palette rows, slot coefficients, translation, or normalization",
            normal["deformation"], "v3 is lit directly by c89/c91; the no-normal variant has no v3 declaration/use",
            "no runtime transformed normal output or pixels observed",
            "one relative c10 read, dp4 normal consumer, normalize dependency, or token identity drift",
        )
    )
    control = report["normalControl"]
    rows.append(
        (
            "NORMAL-CONTROL", "synthetic-control", "hash-pinned serialized normal", "STATIC_PLUS_SYNTHETIC",
            control["serializedNormalSha256"], f"{control['paletteRows']} captured palette rows plus adverse mutation",
            "base/adverse output hashes equal; zero palette reads",
            f"output={control['baseOutputSha256']}; invariant={control['paletteInvariant']}",
            f"mesh={control['sampleMeshSha256']}; palette={control['sourcePaletteBlockSha256']}",
            "synthetic lighting constants are not a runtime output observation",
            "base/adverse output mismatch or a nonzero palette read",
        )
    )
    prior = report["priorPositionContract"]
    rows.append(
        (
            "P1-PRESERVED", "prior-contract", "released position law and scale owner", "REUSED_VERIFIED",
            report["specimens"]["pristineExeSha256"], "landed P1 full replay",
            "slot coefficients and renderer owner exact",
            f"coefficients={prior['slotCoefficients']}; owner={prior['paletteScaleOwner']}; bits={prior['paletteScaleBits']}",
            "position law is reused, not reopened",
            "bug-versus-intent remains unknown",
            "symmetric slot mutation, wrong owner, wrong scale bits, or P1 replay failure",
        )
    )
    for index, unknown in enumerate(report["unknowns"], 1):
        rows.append(
            (
                f"UNKNOWN-{index:03d}", "unknown", f"residual {index}", "UNKNOWN", "NOT_APPLICABLE",
                "NOT_APPLICABLE", "explicitly outside closed denominator", unknown,
                "claim boundary", unknown, "use the focused falsifier in the contract document",
            )
        )
    return "\t".join(columns) + "\n" + "".join(
        "\t".join(_tsv_cell(value) for value in row) + "\n" for row in rows
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--mirror-index", type=Path, required=True)
    parser.add_argument("--pristine-exe", type=Path, required=True)
    parser.add_argument("--capture-log", type=Path, action="append", required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--tsv-out", type=Path)
    args = parser.parse_args(argv)
    outputs = [Path(os.path.abspath(args.json_out))]
    if args.tsv_out is not None:
        outputs.append(Path(os.path.abspath(args.tsv_out)))
    if any(not p1.output_is_local(path) for path in outputs):
        parser.error("generated receipts must stay under local-lab or .artifacts")
    protected = [args.data_root, args.mirror_index, args.pristine_exe, *args.capture_log]
    try:
        report = build_contract(
            args.data_root,
            args.mirror_index,
            args.pristine_exe,
            args.capture_log,
        )
        json_payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        with SecuredOutputRoot(outputs[0].parent, protected_sources=protected) as secured:
            with secured.atomic_text_writer(outputs[0]) as writer:
                writer.write(json_payload)
        if len(outputs) == 2:
            with SecuredOutputRoot(outputs[1].parent, protected_sources=protected) as secured:
                with secured.atomic_text_writer(outputs[1]) as writer:
                    writer.write(render_tsv(report))
    except (OSError, ValueError, RuntimeError) as error:
        print(f"CMSH matrix/normal contract failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report["completion"], sort_keys=True))
    print(outputs[0])
    if len(outputs) == 2:
        print(outputs[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
