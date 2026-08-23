#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the public-safe CMSH matrix-palette skinning contract receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
from collections import Counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rebuild" / "tools"))

from cmsh_static_preview import inflate_aya, parse_cmsh_stream  # noqa: E402
from aya_archive_inventory import read_held_archive  # noqa: E402
from safe_generated_output import SecuredOutputRoot  # noqa: E402


SCHEMA = "onslaught.cmsh-matrix-palette-skinning.v1"
INDEX_SCHEMA = "onslaught.asset-mirror-index.v1"
EXPECTED_INDEX_SHA256 = "c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9"
PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
CAPTURE_TARGET_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
CAPTURE_PROXY_SHA256 = "6ddb1e67be87b79bc1b7a2aff8c503237299459766cd017c1ab86e0380fd0514"
EXPECTED_SKIN_SHADER_SHA256 = frozenset(
    {
        "1fb683058f29fe7cb5a4df4581d55fa6ba54b6edf4ef72526c4a2bc2401a4045",
        "f3b90c830f566d2d19a9f801925d400510bbe7fab5397ae9825f867d9a0d596c",
    }
)
EXPECTED_CAPTURE_LOGS = {
    "5847b187e5ac8306219552a4ec56c3f48f76b453c09f74717b0c7eabaa8088fb": ("vsdump-lvl800", 800, 20),
    "d2966a4ec72af0dd7e8517bf51192cfd67fdde4efc575a36bf905c45b8aef88a": ("vskin-lvl800", 800, 12),
    "8caff0c638978be90ab15530bb74321200abc0725fcc1812ee634338eb32800d": ("vsdump-lvl611", 611, 0),
}
FUNCTION_PINS = (
    ("CMeshPart__LoadVerticesWithBones", 0x004AFBB0, 3139, "2e2541a66ff58b4e6fff4aced3fdbfb685c6628e641134d600fd395dd3a7b316"),
    ("CMCMech__BuildInterpolatedPoseAndAnchor", 0x004B0FB0, 2692, "54997c37d712cfcdb7ab8cb6980eb5c4624fa387a227ad442dd984d13ddf1d4c"),
    ("CVertexShader__ApplyCustomRenderStateShaderConstants", 0x00502920, 4512, "f5625793a5e4493280d3d380ec81488e9fb7e10f4d1a2b5ce8ab94c4b9bd5e34"),
    ("CMeshRenderer__RenderMeshCore", 0x00549570, 8844, "e1371a73aaa0da2f502b54d4eb830f50b6913662cce6416ac057a361b298d2fb"),
    ("CDXMeshVB__BuildSkeletalVB", 0x0054C920, 2254, "fa71ca9eee533a891fbf1658145f70578546e7be43a4ef294d89db07a73ef8f0"),
)
EXPECTED_MESH_SUMMARY = {
    "meshesScanned": 213,
    "skinnedMeshes": 7,
    "rigidControlMeshes": 206,
    "boneCarriers": 7,
    "skinnedVertices": 3203,
    "slotWords": 9609,
    "slotPatternCounts": {"AAA": 2252, "AAB": 135, "ABA": 809, "BAA": 0, "ABC": 7},
    "executedVsMultiplicityDiscriminators": 816,
    "classifiedFieldWordsPerVertex": 12,
    "unclassifiedFieldWordsPerVertex": 0,
    "classifiedFieldWords": 38436,
    "unusedBoneSlots": 0,
}

RETAIL_SKINNING_CORE_TOKENS = (
    0x00000001, 0x80080000, 0xA0000000,
    0x00000001, 0xB0010000, 0x9000000B,
    0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
    0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
    0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
    0x00000001, 0xB0010000, 0x9055000B,
    0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
    0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
    0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
    0x00000002, 0x800F0001, 0x80E40000, 0x80E40000,
    0x00000001, 0xB0010000, 0x90AA000B,
    0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
    0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
    0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
    0x00000002, 0x800F0001, 0x80E40001, 0x80E40000,
    0x00000001, 0x80080001, 0xA0550000,
)


class PeImage:
    """Minimal fail-closed PE32 VA reader for exact static byte pins."""

    def __init__(self, data: bytes) -> None:
        if len(data) < 0x40:
            raise ValueError("PE image is truncated before the DOS header")
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_offset + 24 > len(data) or data[pe_offset:pe_offset + 4] != b"PE\0\0":
            raise ValueError("PE signature is absent or truncated")
        section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
        optional_offset = pe_offset + 24
        if optional_offset + optional_size > len(data) or optional_size < 32:
            raise ValueError("PE optional header is truncated")
        if struct.unpack_from("<H", data, optional_offset)[0] != 0x10B:
            raise ValueError("only PE32 images are supported")
        self.image_base = struct.unpack_from("<I", data, optional_offset + 28)[0]
        section_offset = optional_offset + optional_size
        if section_count == 0 or section_offset + section_count * 40 > len(data):
            raise ValueError("PE section table is absent or truncated")
        self.data = data
        self.sections: list[tuple[int, int, int, int]] = []
        for index in range(section_count):
            offset = section_offset + index * 40
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", data, offset + 8
            )
            if raw_offset + raw_size > len(data):
                raise ValueError("PE section raw data overruns the image")
            self.sections.append((virtual_address, virtual_size, raw_offset, raw_size))

    def read_va(self, va: int, size: int) -> bytes:
        if size < 0 or va < self.image_base:
            raise ValueError("invalid PE VA range")
        rva = va - self.image_base
        for virtual_address, virtual_size, raw_offset, raw_size in self.sections:
            span = max(virtual_size, raw_size)
            if virtual_address <= rva and rva + size <= virtual_address + span:
                delta = rva - virtual_address
                if delta + size > raw_size:
                    raise ValueError("PE VA range is not backed by file bytes")
                return self.data[raw_offset + delta:raw_offset + delta + size]
        raise ValueError(f"PE VA range is outside mapped sections: 0x{va:08x}+{size}")

    def range_sha256(self, va: int, size: int) -> str:
        return hashlib.sha256(self.read_va(va, size)).hexdigest()

    def rel32_call_target(self, call_va: int) -> int:
        instruction = self.read_va(call_va, 5)
        if instruction[0] != 0xE8:
            raise ValueError(f"0x{call_va:08x} is not an E8 rel32 call")
        displacement = struct.unpack_from("<i", instruction, 1)[0]
        return call_va + 5 + displacement


def classify_shader_tokens(tokens: tuple[int, ...]) -> str | None:
    """Recognize the exact executed three-slot core inside a linked shader."""

    width = len(RETAIL_SKINNING_CORE_TOKENS)
    for start in range(len(tokens) - width + 1):
        if tokens[start : start + width] == RETAIL_SKINNING_CORE_TOKENS:
            return "RETAIL_SLOT0_DEAD"
    return None


def _shader_token_sha256(tokens: tuple[int, ...]) -> str:
    return hashlib.sha256(
        b"".join(value.to_bytes(4, "little") for value in tokens)
    ).hexdigest()


def parse_capture_text(text: str) -> dict[str, object]:
    """Parse only public-safe shader/constant/vertex rows from one proxy log."""

    shader_tokens: list[tuple[int, ...]] = []
    palette_blocks: list[tuple[tuple[float, float, float, float], ...]] = []
    pending_palette: dict[int, tuple[float, float, float, float]] | None = None
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.startswith("VS create "):
            match = re.search(r"\bdwords=(\d+)\s+tok=([0-9A-Fa-f,]+)$", line)
            if match is None:
                raise ValueError(f"line {line_number}: malformed VS create row")
            tokens = tuple(int(value, 16) for value in match.group(2).split(","))
            if len(tokens) != int(match.group(1)):
                raise ValueError(f"line {line_number}: declared dword count disagrees with token stream")
            shader_tokens.append(tokens)
        elif line.startswith("VSC "):
            match = re.search(r"\breg=(\d+)\s+count=(\d+)\s+v=([^ ]+)$", line)
            if match is None:
                raise ValueError(f"line {line_number}: malformed VSC row")
            register = int(match.group(1))
            values = tuple(float(value) for value in match.group(3).split(","))
            if int(match.group(2)) != 1 or len(values) != 4 or not all(math.isfinite(value) for value in values):
                raise ValueError(f"line {line_number}: unsupported VSC row shape")
            row = values  # type: ignore[assignment]
            if register == 7 and abs(values[0] - 1 / 3) < 1e-7 and values[1:] == (0.0, 0.0, 0.0):
                pending_palette = {register: row}
            elif pending_palette is not None and 8 <= register <= 51:
                pending_palette[register] = row
                if register == 51 and all(index in pending_palette for index in range(7, 52)):
                    expected_diagonal = {
                        7: (1 / 3, 0.0, 0.0, 0.0),
                        8: (0.0, 1 / 3, 0.0, 0.0),
                        9: (0.0, 0.0, 1 / 3, 0.0),
                    }
                    for index, expected in expected_diagonal.items():
                        if max(abs(actual - wanted) for actual, wanted in zip(pending_palette[index], expected)) > 1e-7:
                            raise ValueError("palette scale preamble is not diag(1/3,1/3,1/3)")
                    palette_blocks.append(tuple(pending_palette[index] for index in range(10, 52)))
                    pending_palette = None
    skinning = [tokens for tokens in shader_tokens if classify_shader_tokens(tokens) is not None]
    unique = {_shader_token_sha256(tokens) for tokens in skinning}
    row_norms = [
        math.sqrt(row[0] * row[0] + row[1] * row[1] + row[2] * row[2])
        for block in palette_blocks
        for row in block
    ]
    return {
        "shaderCreates": len(shader_tokens),
        "retailSkinningShaders": len(skinning),
        "uniqueRetailSkinningShaders": len(unique),
        "retailSkinningShaderSha256": sorted(unique),
        "paletteBlocks": len(palette_blocks),
        "paletteRows": len(row_norms),
        "paletteLinearRowNormMin": min(row_norms) if row_norms else None,
        "paletteLinearRowNormMax": max(row_norms) if row_norms else None,
        "paletteLinearRowNormMaxDeviationFromThird": (
            max(abs(value - 1 / 3) for value in row_norms) if row_norms else None
        ),
    }


def validate_capture_metrics(
    parsed: dict[str, object],
    *,
    expected_palette_blocks: int,
) -> None:
    """Refuse semantic-core false positives or capture denominator drift."""

    actual_shader_hashes = frozenset(
        str(value) for value in parsed["retailSkinningShaderSha256"]
    )
    if actual_shader_hashes != EXPECTED_SKIN_SHADER_SHA256:
        raise ValueError("linked skinning shader identity drift")
    expected_counts = {
        "shaderCreates": 48,
        "retailSkinningShaders": 2,
        "uniqueRetailSkinningShaders": 2,
        "paletteBlocks": expected_palette_blocks,
        "paletteRows": expected_palette_blocks * 42,
    }
    for key, expected in expected_counts.items():
        if parsed.get(key) != expected:
            raise ValueError(
                f"capture denominator drift for {key}: "
                f"expected {expected}, got {parsed.get(key)!r}"
            )


def pinned_skinning_shader_pointers(text: str) -> set[str]:
    """Join exact linked shader token hashes back to capture object pointers."""

    pointers: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("VS create "):
            continue
        match = re.search(
            r"\bptr=(0x[0-9A-Fa-f]+)\s+dwords=(\d+)\s+tok=([0-9A-Fa-f,]+)$",
            line,
        )
        if match is None:
            raise ValueError(f"line {line_number}: malformed VS create row")
        tokens = tuple(int(value, 16) for value in match.group(3).split(","))
        if len(tokens) != int(match.group(2)):
            raise ValueError(
                f"line {line_number}: declared dword count disagrees with token stream"
            )
        token_sha256 = _shader_token_sha256(tokens)
        if token_sha256 in EXPECTED_SKIN_SHADER_SHA256:
            if classify_shader_tokens(tokens) != "RETAIL_SLOT0_DEAD":
                raise ValueError("pinned linked shader no longer contains the executed core")
            pointers.add(match.group(1).upper())
    if len(pointers) != len(EXPECTED_SKIN_SHADER_SHA256):
        raise ValueError("capture does not expose both pinned skinning shader pointers")
    return pointers


def classify_slot_pattern(slots: tuple[int, int, int]) -> str:
    """Classify one three-slot tuple by equality shape without renaming its values."""

    first, second, third = slots
    if first == second == third:
        return "AAA"
    if first == second:
        return "AAB"
    if first == third:
        return "ABA"
    if second == third:
        return "BAA"
    return "ABC"


def summarize_parsed_meshes(
    parsed_meshes: list[tuple[str, str, Any]],
) -> dict[str, object]:
    """Classify every bone-bearing vertex while retaining rigid meshes as controls."""

    pattern_order = ("AAA", "AAB", "ABA", "BAA", "ABC")
    aggregate: Counter[str] = Counter()
    mesh_rows: list[dict[str, object]] = []
    for file_name, source_sha256, mesh in parsed_meshes:
        parts = mesh.file_parts()
        carriers = [(index, part) for index, part in enumerate(parts) if part.bones]
        if not carriers:
            if any(vertex.bone_slots is not None for part in parts for vertex in part.vertices):
                raise ValueError(f"{file_name}: rigid mesh exposes bone slots")
            continue
        if len(carriers) != 1:
            raise ValueError(f"{file_name}: expected exactly one BONE carrier")
        carrier_index, carrier = carriers[0]
        if any(index >= len(parts) for index in carrier.bones):
            raise ValueError(f"{file_name}: BONE part index is out of range")
        if len(carrier.raw_cmvb) != 296:
            raise ValueError(f"{file_name}: BONE carrier has no bounded CMVB")
        stride, fvf, topology = struct.unpack_from("<III", carrier.raw_cmvb, 276)
        if (stride, fvf, topology) != (48, 0, 4):
            raise ValueError(f"{file_name}: BONE carrier is not the 48/0/4 profile")
        patterns: Counter[str] = Counter()
        used_slots: Counter[int] = Counter()
        for vertex in carrier.vertices:
            if vertex.bone_slots is None:
                raise ValueError(f"{file_name}: skinned vertex has no three-slot tuple")
            if any(slot >= len(carrier.bones) for slot in vertex.bone_slots):
                raise ValueError(f"{file_name}: vertex slot is outside the BONE array")
            pattern = classify_slot_pattern(vertex.bone_slots)
            patterns[pattern] += 1
            aggregate[pattern] += 1
            used_slots.update(vertex.bone_slots)
        unused = sorted(set(range(len(carrier.bones))) - set(used_slots))
        mesh_rows.append(
            {
                "file": file_name,
                "sourceSha256": source_sha256,
                "carrierPartIndex": carrier_index,
                "carrierPartName": carrier.name,
                "bones": len(carrier.bones),
                "bonePartIndices": list(carrier.bones),
                "bonePartNames": [parts[index].name for index in carrier.bones],
                "vertices": len(carrier.vertices),
                "slotWords": len(carrier.vertices) * 3,
                "slotPatternCounts": {key: patterns[key] for key in pattern_order},
                "executedVsMultiplicityDiscriminators": patterns["ABA"] + patterns["ABC"],
                "unusedBoneSlots": unused,
            }
        )
    mesh_rows.sort(key=lambda row: str(row["file"]).casefold())
    vertices = sum(int(row["vertices"]) for row in mesh_rows)
    return {
        "meshes": mesh_rows,
        "summary": {
            "meshesScanned": len(parsed_meshes),
            "skinnedMeshes": len(mesh_rows),
            "rigidControlMeshes": len(parsed_meshes) - len(mesh_rows),
            "boneCarriers": len(mesh_rows),
            "skinnedVertices": vertices,
            "slotWords": vertices * 3,
            "slotPatternCounts": {key: aggregate[key] for key in pattern_order},
            "executedVsMultiplicityDiscriminators": aggregate["ABA"] + aggregate["ABC"],
            "classifiedFieldWordsPerVertex": 12,
            "unclassifiedFieldWordsPerVertex": 0,
            "classifiedFieldWords": vertices * 12,
            "unusedBoneSlots": sum(len(row["unusedBoneSlots"]) for row in mesh_rows),
        },
    }


def validate_exact_mesh_summary(summary: dict[str, object]) -> None:
    """Refuse denominator or classification drift in the bounded retail family."""

    for key, expected in EXPECTED_MESH_SUMMARY.items():
        actual = summary.get(key)
        if actual != expected:
            raise ValueError(
                f"mesh-family denominator/classification drift for {key}: "
                f"expected {expected!r}, got {actual!r}"
            )


def _float_tuple(value: str, width: int, role: str) -> tuple[float, ...]:
    result = tuple(float(item) for item in value.split(","))
    if len(result) != width or not all(math.isfinite(item) for item in result):
        raise ValueError(f"invalid {role}")
    return result


def compare_runtime_vertex_rows(
    text: str,
    expected_by_vertex_count: dict[int, tuple[str, tuple[Any, ...]]],
    *,
    allowed_shader_pointers: set[str],
    tolerance: float = 1e-3,
) -> dict[str, object]:
    """Compare one complete printed runtime VB per named bounded retail mesh."""

    draws: dict[tuple[int, int], dict[str, object]] = {}
    rows: dict[tuple[int, int], dict[int, tuple[tuple[float, ...], tuple[float, ...], int, tuple[float, ...]]]] = {}
    static_buffers: dict[tuple[int, int], dict[str, object]] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        draw_match = re.match(r"D (\d+) (\d+) .*\bverts=(\d+) .*\bfvf=0x15A\b.*\bvs=(0x[0-9A-Fa-f]+)\b.*s0=\(vb=(0x[0-9A-Fa-f]+),off=\d+,stride=48\)", line)
        if draw_match:
            key = (int(draw_match.group(1)), int(draw_match.group(2)))
            if int(draw_match.group(4), 16) == 0:
                raise ValueError(f"line {line_number}: skinned draw has no vertex shader")
            draws[key] = {
                "vertices": int(draw_match.group(3)),
                "vertexShader": draw_match.group(4).upper(),
                "vertexBuffer": draw_match.group(5).upper(),
            }
            rows.setdefault(key, {})
            continue
        geometry_match = re.match(
            r"G (\d+) (\d+) vb .*\bn=(\d+)\s+bytes=(\d+)\s+h=([0-9A-Fa-f]+)\s+"
            r"unlocks=(\d+)\s+lastunlock=(\d+)\s+stride=48\b",
            line,
        )
        if geometry_match:
            key = (int(geometry_match.group(1)), int(geometry_match.group(2)))
            static_buffers[key] = {
                "vertices": int(geometry_match.group(3)),
                "bytes": int(geometry_match.group(4)),
                "digestFnv1a64": geometry_match.group(5).upper(),
                "unlocks": int(geometry_match.group(6)),
                "lastUnlockFrame": int(geometry_match.group(7)),
            }
            continue
        vertex_match = re.match(
            r"V (\d+) (\d+) (\d+) xyzb3=\(([^)]+)\) n=\(([^)]+)\) "
            r"diff=0x([0-9A-Fa-f]{8}) t0=\(([^)]+)\)$",
            line,
        )
        if vertex_match:
            key = (int(vertex_match.group(1)), int(vertex_match.group(2)))
            rows.setdefault(key, {})[int(vertex_match.group(3))] = (
                _float_tuple(vertex_match.group(4), 6, "xyzb3"),
                _float_tuple(vertex_match.group(5), 3, "normal"),
                int(vertex_match.group(6), 16),
                _float_tuple(vertex_match.group(7), 2, "texture coordinate"),
            )

    comparisons: list[dict[str, object]] = []
    used_keys: set[tuple[int, int]] = set()
    total_mismatches = 0
    for vertex_count, (file_name, expected_vertices) in sorted(expected_by_vertex_count.items()):
        if len(expected_vertices) != vertex_count:
            raise ValueError(f"{file_name}: expected vertex denominator disagrees with its key")
        candidates = [
            key
            for key, draw in draws.items()
            if int(draw["vertices"]) == vertex_count
            and str(draw["vertexShader"]) in allowed_shader_pointers
            and len(rows.get(key, {})) == vertex_count
            and set(rows[key]) == set(range(vertex_count))
            and key in static_buffers
        ]
        if not candidates:
            raise ValueError(
                f"{file_name}: no complete runtime vertex dump using a pinned skinning shader"
            )
        key = sorted(candidates)[0]
        used_keys.add(key)
        geometry = static_buffers[key]
        if int(geometry["vertices"]) != vertex_count or int(geometry["bytes"]) != vertex_count * 48:
            raise ValueError(f"{file_name}: runtime geometry denominator drift")
        if int(geometry["unlocks"]) != 1:
            raise ValueError(f"{file_name}: runtime vertex buffer is not static")
        mismatch_counts: Counter[str] = Counter()
        for index, expected in enumerate(expected_vertices):
            xyzb3, normal, diffuse, uv = rows[key][index]
            expected_slots = tuple(float(slot * 3) for slot in expected.bone_slots)
            actual_groups = (xyzb3[:3], xyzb3[3:], normal, uv)
            expected_groups = (expected.position, expected_slots, expected.normal, expected.uv)
            roles = ("position", "paletteSlot", "normal", "uv")
            for role, actual_group, expected_group in zip(roles, actual_groups, expected_groups):
                if expected_group is None:
                    raise ValueError(f"{file_name}: expected {role} is absent")
                mismatch_counts[role] += sum(
                    abs(actual - wanted) > tolerance
                    for actual, wanted in zip(actual_group, expected_group)
                )
            mismatch_counts["diffuse"] += diffuse != expected.raw_color_u32
        mismatches = sum(mismatch_counts.values())
        total_mismatches += mismatches
        comparisons.append(
            {
                "file": file_name,
                "vertices": vertex_count,
                "testedFieldWords": vertex_count * 12,
                "mismatchedFieldWords": mismatches,
                "mismatchCounts": dict(sorted(mismatch_counts.items())),
                "vertexBufferDigestFnv1a64": geometry["digestFnv1a64"],
                "vertexBufferUnlocks": geometry["unlocks"],
            }
        )
    return {
        "comparisons": comparisons,
        "matchedVertices": sum(int(row["vertices"]) for row in comparisons),
        "testedFieldWords": sum(int(row["testedFieldWords"]) for row in comparisons),
        "mismatchedFieldWords": total_mismatches,
        "staticVertexBuffers": len(used_keys),
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path) -> bytes:
    return read_held_archive(path)


def _verify_mesh_corpus(data_root: Path, mirror_index: Path) -> tuple[dict[str, object], dict[str, Any]]:
    index_bytes = _read(mirror_index)
    index_sha256 = _sha256_bytes(index_bytes)
    if index_sha256 != EXPECTED_INDEX_SHA256:
        raise ValueError(f"mirror index hash mismatch: {index_sha256}")
    lines = index_bytes.decode("utf-8").splitlines()
    if not lines:
        raise ValueError("mirror index is empty")
    header = json.loads(lines[0])
    if header.get("schema") != INDEX_SCHEMA:
        raise ValueError(f"unsupported mirror index schema: {header.get('schema')!r}")
    by_path: dict[str, dict[str, object]] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        row = json.loads(line)
        key = str(row["sourcePath"]).replace("\\", "/").casefold()
        if key in by_path:
            raise ValueError(f"mirror index repeats source path: {row['sourcePath']}")
        by_path[key] = row
    mesh_root = data_root / "resources" / "meshes"
    if not mesh_root.is_dir():
        raise ValueError("data root has no resources/meshes directory")
    mesh_paths = sorted(mesh_root.glob("*.msh.aya"), key=lambda path: path.name.casefold())
    parsed: list[tuple[str, str, Any]] = []
    by_file: dict[str, Any] = {}
    for path in mesh_paths:
        relative = path.relative_to(data_root).as_posix()
        index_row = by_path.get(relative.casefold())
        if index_row is None:
            raise ValueError(f"mesh is absent from mirror index: {relative}")
        source = _read(path)
        source_sha256 = _sha256_bytes(source)
        if source_sha256 != str(index_row.get("sourceSha256", "")).casefold():
            raise ValueError(f"mesh hash disagrees with mirror index: {relative}")
        mesh = parse_cmsh_stream(inflate_aya(source))
        parsed.append((path.name, source_sha256, mesh))
        by_file[path.name.casefold()] = mesh
    result = summarize_parsed_meshes(parsed)
    validate_exact_mesh_summary(result["summary"])
    result["inputVerification"] = {
        "indexSchema": INDEX_SCHEMA,
        "indexSha256": index_sha256,
        "verifiedMeshFiles": len(mesh_paths),
    }
    return result, by_file


def _verify_executable(path: Path) -> dict[str, object]:
    data = _read(path)
    sha256 = _sha256_bytes(data)
    if sha256 != PRISTINE_SHA256:
        raise ValueError(f"pristine executable hash mismatch: {sha256}")
    pe = PeImage(data)
    functions: list[dict[str, object]] = []
    for name, va, size, expected_sha256 in FUNCTION_PINS:
        actual = pe.range_sha256(va, size)
        if actual != expected_sha256:
            raise ValueError(f"{name} body hash mismatch: {actual}")
        functions.append(
            {
                "name": name,
                "va": f"0x{va:08x}",
                "bytes": size,
                "bodySha256": actual,
            }
        )
    opcode_pins = (
        ("greedy-third-subtract", 0x004B0390, bytes.fromhex("d82580c65d00")),
        ("slot-index-times-three", 0x0054CBF3, bytes.fromhex("db4407fcd80dc08c5d00")),
    )
    opcodes: list[dict[str, object]] = []
    for role, va, expected in opcode_pins:
        actual = pe.read_va(va, len(expected))
        if actual != expected:
            raise ValueError(f"{role} opcode mismatch at 0x{va:08x}")
        opcodes.append({"role": role, "va": f"0x{va:08x}", "bytesHex": actual.hex()})
    constants = (
        ("one-third", 0x005DC680, 0x3EAAAAAB),
        ("slot-stride-three", 0x005D8CC0, 0x40400000),
    )
    constant_rows: list[dict[str, object]] = []
    for role, va, expected_bits in constants:
        bits = struct.unpack("<I", pe.read_va(va, 4))[0]
        if bits != expected_bits:
            raise ValueError(f"{role} constant mismatch at 0x{va:08x}")
        constant_rows.append(
            {
                "role": role,
                "va": f"0x{va:08x}",
                "float32": struct.unpack("<f", struct.pack("<I", bits))[0],
                "bits": f"0x{bits:08x}",
            }
        )
    for va in (0x00502ECF, 0x00502F06, 0x00502F3D, 0x00502F74):
        instruction = pe.read_va(va, 11)
        if instruction[:3] != bytes.fromhex("c78424") or instruction[-4:] != bytes.fromhex("abaaaa3e"):
            raise ValueError(f"diag(1/3) immediate store mismatch at 0x{va:08x}")
    call_pins = (
        ("bind-pose-sample", 0x0054A74E, 0x004B0FB0),
        ("current-pose-sample", 0x0054A786, 0x004B0FB0),
        ("layer-render-primary", 0x0054A4B6, 0x0054D530),
        ("layer-render-secondary", 0x0054B265, 0x0054D530),
        ("skeletal-build-dispatch", 0x0054D3AC, 0x0054C920),
    )
    calls: list[dict[str, str]] = []
    for role, call_va, expected_target in call_pins:
        target = pe.rel32_call_target(call_va)
        if target != expected_target:
            raise ValueError(f"{role} call target drift at 0x{call_va:08x}")
        calls.append(
            {
                "role": role,
                "callVa": f"0x{call_va:08x}",
                "targetVa": f"0x{target:08x}",
            }
        )
    return {
        "specimenSha256": sha256,
        "functions": functions,
        "opcodes": opcodes,
        "constants": constant_rows,
        "calls": calls,
    }


def _capture_record(path: Path) -> tuple[dict[str, object], str]:
    data = _read(path)
    sha256 = _sha256_bytes(data)
    expected = EXPECTED_CAPTURE_LOGS.get(sha256)
    if expected is None:
        raise ValueError(f"capture log is not in the pinned evidence set: {sha256}")
    label, level, expected_palette_blocks = expected
    parsed = parse_capture_text(data.decode("utf-8"))
    validate_capture_metrics(parsed, expected_palette_blocks=expected_palette_blocks)
    run_path = path.with_name("run.json")
    run_bytes = _read(run_path)
    run = json.loads(run_bytes.decode("utf-8"))
    if (
        run.get("name") != label
        or int(run.get("level", -1)) != level
        or str(run.get("exeSha256", "")).casefold() != CAPTURE_TARGET_SHA256
        or str(run.get("proxySha256", "")).casefold() != CAPTURE_PROXY_SHA256
    ):
        raise ValueError(f"capture run metadata disagrees with pinned identity: {label}")
    record: dict[str, object] = {
        "label": label,
        "level": level,
        "logSha256": sha256,
        "runSha256": _sha256_bytes(run_bytes),
        **parsed,
    }
    return record, data.decode("utf-8")


def build_contract(
    data_root: Path,
    mirror_index: Path,
    pristine_exe: Path,
    capture_logs: list[Path],
) -> dict[str, object]:
    """Reproduce the closed serialized/static/runtime skinning evidence family."""

    data_root = Path(os.path.abspath(data_root))
    mirror_index = Path(os.path.abspath(mirror_index))
    pristine_exe = Path(os.path.abspath(pristine_exe))
    capture_logs = [Path(os.path.abspath(path)) for path in capture_logs]
    mesh_family, mesh_lookup = _verify_mesh_corpus(data_root, mirror_index)
    if set(mesh_family["summary"]["slotPatternCounts"]) != {"AAA", "AAB", "ABA", "BAA", "ABC"}:
        raise ValueError("slot-pattern denominator is not exhaustively classified")
    static = _verify_executable(pristine_exe)
    capture_records: list[dict[str, object]] = []
    capture_text_by_label: dict[str, str] = {}
    for path in capture_logs:
        record, text = _capture_record(path)
        label = str(record["label"])
        if label in capture_text_by_label:
            raise ValueError(f"capture label repeated: {label}")
        capture_records.append(record)
        capture_text_by_label[label] = text
    if {str(row["logSha256"]) for row in capture_records} != set(EXPECTED_CAPTURE_LOGS):
        raise ValueError("capture set is incomplete or contains a duplicate")
    capture_records.sort(key=lambda row: str(row["label"]))
    capture_summary = {
        "captures": len(capture_records),
        "levels": sorted({int(row["level"]) for row in capture_records}),
        "shaderCreates": sum(int(row["shaderCreates"]) for row in capture_records),
        "retailSkinningShaders": sum(int(row["retailSkinningShaders"]) for row in capture_records),
        "uniqueRetailSkinningShadersByCapture": sum(
            int(row["uniqueRetailSkinningShaders"]) for row in capture_records
        ),
        "paletteBlocks": sum(int(row["paletteBlocks"]) for row in capture_records),
        "paletteRows": sum(int(row["paletteRows"]) for row in capture_records),
        "paletteLinearRowNormMin": min(
            float(row["paletteLinearRowNormMin"])
            for row in capture_records
            if row["paletteLinearRowNormMin"] is not None
        ),
        "paletteLinearRowNormMax": max(
            float(row["paletteLinearRowNormMax"])
            for row in capture_records
            if row["paletteLinearRowNormMax"] is not None
        ),
        "paletteLinearRowNormMaxDeviationFromThird": max(
            float(row["paletteLinearRowNormMaxDeviationFromThird"])
            for row in capture_records
            if row["paletteLinearRowNormMaxDeviationFromThird"] is not None
        ),
    }
    sentinel_by_count: dict[int, tuple[str, tuple[Any, ...]]] = {}
    for file_name in ("m_Sentinel Arm Small.msh.aya", "m_Sentinel Arm Big.msh.aya"):
        mesh = mesh_lookup[file_name.casefold()]
        carrier = next(part for part in mesh.file_parts() if part.bones)
        count = len(carrier.vertices)
        if count in sentinel_by_count:
            raise ValueError("runtime Sentinel vertex denominators are not unique")
        sentinel_by_count[count] = (file_name, carrier.vertices)
    runtime_readback = compare_runtime_vertex_rows(
        capture_text_by_label["vskin-lvl800"],
        sentinel_by_count,
        allowed_shader_pointers=pinned_skinning_shader_pointers(
            capture_text_by_label["vskin-lvl800"]
        ),
    )
    unclassified = int(mesh_family["summary"]["unclassifiedFieldWordsPerVertex"])
    mismatches = int(runtime_readback["mismatchedFieldWords"])
    if unclassified or mismatches:
        raise ValueError("bounded tested-field family is not closed")
    return {
        "schema": SCHEMA,
        "meshFamily": mesh_family,
        "staticRuntime": static,
        "runtimeCaptures": {"captures": capture_records, "summary": capture_summary},
        "runtimeVertexReadback": runtime_readback,
        "formula": {
            "paletteAddress": "c[10 + storedSlot + row], storedSlot = 3 * BONE-array index",
            "executedPosition": "2 * T[slot1] * position + T[slot2] * position",
            "executedSlotWeights": [0.0, 2.0 / 3.0, 1.0 / 3.0],
            "bindRole": "renderer samples each BONE part at frame zero and again at the current interpolated pose before building the palette",
            "paletteScale": 1.0 / 3.0,
        },
        "unknowns": [
            "The dense retail matrix-construction body proves frame-zero/current-pose roles, but its exact row/column multiplication order is not promoted beyond those calls.",
            "The captured runtime VB agrees field-by-field at printed precision; low-order raw-byte identity remains unproved.",
            "Whether slot-zero loss is an intended convention or a linker bug remains unknown.",
            "The two Sentinel arms are runtime-observed; the five infantry meshes share the serialized family and linked shader but were not observed drawing in these captures.",
            "The position combine is decoded exactly; the shader's normal-transform combine remains outside this contract.",
        ],
        "completion": {
            "testedFieldFamily": "seven BONE carriers plus two runtime-readback Sentinel instances",
            "unclassifiedTestedFields": 0,
            "runtimeReadbackMismatches": 0,
        },
    }


def _tsv_cell(value: object) -> str:
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def render_tsv(report: dict[str, object]) -> str:
    """Render the public receipt without local paths or retail payload bytes."""

    columns = (
        "row_id", "row_kind", "subject", "evidence_class", "specimen_sha256",
        "denominator", "classified", "result", "evidence_boundary",
        "remaining_unknown", "falsifier",
    )
    rows: list[tuple[object, ...]] = []
    mesh_family = report["meshFamily"]
    mesh_summary = mesh_family["summary"]
    rows.append(
        (
            "FAMILY-SERIALIZED", "family", "loose CMSH BONE carriers", "CORPUS_MEASURED",
            mesh_family["inputVerification"]["indexSha256"],
            f"{mesh_summary['meshesScanned']} meshes; {mesh_summary['skinnedVertices']} skinned vertices; {mesh_summary['slotWords']} slot words",
            f"{mesh_summary['classifiedFieldWords']} field words; zero unclassified",
            f"patterns={json.dumps(mesh_summary['slotPatternCounts'], sort_keys=True, separators=(',', ':'))}",
            "all 213 loose CMSH inputs hash-verified; exactly seven one-part BONE carriers; 48/0/4 vertex profile",
            "runtime draw is observed only for the two Sentinel arms",
            "one hash-verified BONE carrier outside this denominator or one unclassified 48-byte word",
        )
    )
    for index, mesh in enumerate(mesh_family["meshes"], 1):
        rows.append(
            (
                f"MESH-{index:03d}", "serialized-mesh", mesh["file"], "CORPUS_MEASURED",
                mesh["sourceSha256"],
                f"{mesh['vertices']} vertices; {mesh['bones']} bones; {mesh['slotWords']} slots",
                "all vertex fields and BONE slots classified",
                f"patterns={json.dumps(mesh['slotPatternCounts'], sort_keys=True, separators=(',', ':'))}; discriminators={mesh['executedVsMultiplicityDiscriminators']}",
                f"carrier part {mesh['carrierPartIndex']} {mesh['carrierPartName']}; same-mesh part-index BONE array",
                "no per-vertex scalar weight field is serialized",
                "one out-of-range slot, unused declared bone, or non-48/0/4 carrier",
            )
        )
    formula = report["formula"]
    rows.extend(
        [
            (
                "FORMULA-ADDRESS", "formula", "matrix-palette addressing", "STATIC_PLUS_RUNTIME",
                report["staticRuntime"]["specimenSha256"], "three stored slot floats per vertex",
                "all 9,609 are exact 3 * BONE-array index", formula["paletteAddress"],
                "vs_1_1 relative c10 palette; three registers per bone",
                "none inside the seven-mesh family",
                "one stored slot not equal to three times an in-range BONE index",
            ),
            (
                "FORMULA-EXECUTED", "formula", "three-slot position combine", "RUNTIME_MEASURED",
                "+".join(row["logSha256"] for row in report["runtimeCaptures"]["captures"]),
                f"{report['runtimeCaptures']['summary']['retailSkinningShaders']} linked skinning shaders across {report['runtimeCaptures']['summary']['captures']} captures",
                "all exact executed cores classified", formula["executedPosition"],
                "slot0 result is overwritten; slot1 is doubled; slot2 is added",
                "bug-versus-intended-convention is unknown",
                "a pinned linked skinning shader with a different combine core",
            ),
            (
                "FORMULA-SCALE", "formula", "palette weight scale", "STATIC_PLUS_RUNTIME",
                report["staticRuntime"]["specimenSha256"],
                f"{report['runtimeCaptures']['summary']['paletteRows']} captured palette rows",
                "all measured linear rows at one-third scale",
                f"palette scale={formula['paletteScale']}; slot weights={formula['executedSlotWeights']}",
                "renderer scales every 4x4 palette element; shader sums 2+1 terms",
                "raw float capture precision remains bounded by logger output",
                "one palette row outside the float32 one-third envelope or an unscaled renderer path",
            ),
            (
                "BIND-CURRENT", "bind-current", "retail palette construction", "RETAIL_STATIC",
                report["staticRuntime"]["specimenSha256"],
                "one frame-zero and one current-pose sample per BONE part",
                "roles and call sites classified", formula["bindRole"],
                "CMeshRenderer__RenderMeshCore samples frame zero and current interpolation before scaling/upload",
                report["unknowns"][0],
                "a typed instruction-level reduction or controlled trace that yields different bind/current algebra",
            ),
        ]
    )
    for index, capture in enumerate(report["runtimeCaptures"]["captures"], 1):
        rows.append(
            (
                f"CAPTURE-{index:03d}", "runtime-capture", capture["label"],
                "COPIED_RUNTIME_MEASURED", capture["logSha256"],
                f"{capture['shaderCreates']} shader creates; {capture['paletteBlocks']} palette blocks",
                f"{capture['retailSkinningShaders']} skinning shaders classified",
                f"level={capture['level']}; uniqueSkinning={capture['uniqueRetailSkinningShaders']}; paletteRows={capture['paletteRows']}",
                f"run={capture['runSha256']}; target={CAPTURE_TARGET_SHA256}; proxy={CAPTURE_PROXY_SHA256}",
                "capture proves only the named level/session",
                "hash drift, shader-core drift, or incomplete palette preamble",
            )
        )
    for index, comparison in enumerate(report["runtimeVertexReadback"]["comparisons"], 1):
        rows.append(
            (
                f"READBACK-{index:03d}", "runtime-readback", comparison["file"],
                "COPIED_RUNTIME_MEASURED", comparison["vertexBufferDigestFnv1a64"],
                f"{comparison['vertices']} vertices; {comparison['testedFieldWords']} field words",
                f"{comparison['testedFieldWords']} compared; {comparison['mismatchedFieldWords']} mismatched",
                f"mismatches={json.dumps(comparison['mismatchCounts'], sort_keys=True, separators=(',', ':'))}; unlocks={comparison['vertexBufferUnlocks']}",
                "position, three palette offsets, normal, diffuse, and UV compared at logged precision",
                "raw byte identity below printed precision is unknown",
                "one field-word mismatch above 1e-3 or a vertex-buffer unlock count other than one",
            )
        )
    for index, function in enumerate(report["staticRuntime"]["functions"], 1):
        rows.append(
            (
                f"STATIC-{index:03d}", "retail-function", function["name"], "RETAIL_STATIC",
                function["bodySha256"], f"{function['bytes']} bytes",
                "exact range classified for this contract", function["va"],
                "raw range hash against pristine 74154bfa specimen",
                "static bytes alone do not prove every runtime path executes",
                "body/range/hash or direct-call target drift",
            )
        )
    for index, unknown in enumerate(report["unknowns"], 1):
        rows.append(
            (
                f"UNKNOWN-{index:03d}", "unknown", f"residual {index}", "UNKNOWN",
                "NOT_APPLICABLE", "NOT_APPLICABLE",
                "explicitly outside tested field denominator", unknown, "claim boundary", unknown,
                "use the focused falsifier stated in the contract document",
            )
        )
    return "\t".join(columns) + "\n" + "".join(
        "\t".join(_tsv_cell(value) for value in row) + "\n" for row in rows
    )


def output_is_local(path: Path) -> bool:
    candidate = os.path.normcase(os.path.abspath(path))
    for root in (ROOT / "local-lab", ROOT / ".artifacts"):
        allowed = os.path.normcase(os.path.abspath(root))
        try:
            if os.path.commonpath((candidate, allowed)) == allowed:
                return True
        except ValueError:
            continue
    return False


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
    if any(not output_is_local(path) for path in outputs):
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
        print(f"CMSH skinning contract failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report["meshFamily"]["summary"], sort_keys=True))
    print(json.dumps(report["runtimeCaptures"]["summary"], sort_keys=True))
    print(outputs[0])
    if len(outputs) == 2:
        print(outputs[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
