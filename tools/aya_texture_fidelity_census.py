#!/usr/bin/env python3
"""Build a fail-closed PC/USA-Xbox AYA texture-fidelity census.

The existing cross-platform comparator owns top-level resource pairing.  This
instrument consumes one frozen geometry output from that comparator, reopens
the named retail archives, and validates the complete nested
DXTX/CTEX/TFRM/TMIP geometry for every paired TEXT occurrence.  It then joins
the PC records to the installed loose DDS shelf and compares stored mip bytes
only where the two platform encodings have the same byte layout.

Generated rows are local evidence.  They contain names and hashes, never retail
payload bytes, and must be written to an explicit ignored output root.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from zipfile import ZipFile, ZipInfo

import aya_archive_inventory as aya
import aya_cross_platform_compare as cross
from safe_generated_output import SecuredOutputRoot


SCHEMA = "bea.pc-xbox-aya-texture-fidelity-census.v1"
OCCURRENCE_SCHEMA = "bea.pc-xbox-aya-texture-occurrence.v1"
FRAME_SCHEMA = "bea.pc-xbox-aya-texture-frame.v1"
MIP_SCHEMA = "bea.pc-xbox-aya-texture-mip.v1"
VARIANT_SCHEMA = "bea.xbox-aya-texture-source-frame-variants.v1"

CTEX_BODY_SIZE = 344
CTEX_START = 8
CTEX_BODY_START = 16
CTEX_END = CTEX_BODY_START + CTEX_BODY_SIZE
CTEX_NAME_OFFSET = 0x18
CTEX_NAME_LENGTH = 128
CTEX_WIDTH_OFFSET = 0xBC
CTEX_HEIGHT_OFFSET = 0xC0
CTEX_FRAME_COUNT_OFFSET = 0x148
CTEX_FORMAT_OFFSET = 0x154

DDS_HEADER_LENGTH = 128
DDS_FILENAME_RE = re.compile(
    r"^(?P<name>.*)\((?P<frame>[0-9]+)\)(?P<format>[A-Za-z0-9]+)\.aya$",
    re.IGNORECASE,
)
SOURCE_FORMAT_CODES = {
    "a1r5g5b5": 1,
    "a4r4g4b4": 2,
    "x8r8g8b8": 3,
    "a8r8g8b8": 4,
    "r5g6b5": 5,
}
SOURCE_FORMAT_NAMES = {value: key.upper() for key, value in SOURCE_FORMAT_CODES.items()}
XBOX_FORMAT_NAMES = {
    3: "BPP32_CODE3",
    4: "BPP32_CODE4",
    6: "DXT1_BLOCKS",
    7: "DXT_COMPATIBLE_16_BYTE_BLOCKS",
}
COMPARABLE_LAYOUTS = {
    ("DXT1", 6),
    ("DXT2", 7),
    ("A8R8G8B8", 4),
}

KNOWN_PROFILE = "pc-retail-usa-xbox-2026-08-14"
KNOWN_GEOMETRY_SHA256 = (
    "2462f7453fb3b3ec252a0ab4e8f0f08891c3e6338b585e910f289d0a6edd8165"
)
KNOWN_XBOX_ZIP_LENGTH = 1_943_296_611
KNOWN_XBOX_ZIP_SHA256 = (
    "7a83dcc73fecfc701306bcaf78c96f55c4ecd47ef5d1ab10e9e20766a25281ae"
)
KNOWN_RESOURCE_ACCUMULATOR_SHA256 = (
    "4f78480aeb6caae9854295ae09a9b322a7a83264da3f3e19a95723505414f1b2"
)
KNOWN_DXT_MANIFEST_SHA256 = (
    "2746bfad722edf964f5abc6ac0094b9987d2d8cb615df7748cebc555cb67e410"
)
KNOWN_TEXTURES_MANIFEST_SHA256 = (
    "7a524b05321fcf8aefce4254fa2982e9040a1dbe1e2c22ad409a61fdbb1c865d"
)
KNOWN_MUSTBE_NAMES = (
    "frontend\\v2\\fe_white_ring.tga",
    "hud\\v2\\battleenginemarker.tga",
    "shadowblob.tga",
    "sunblob.tga",
    "sunreflect.tga",
)
KNOWN_UNPARSED_DXT_FILENAMES = (
    "goodies%ca_cutscene_locations%ca_cl_f_command_room_interior.t.aya",
    "goodies%ca_cutscene_locations%ca_cl_f_research_compound.tga(0.aya",
)

GEOMETRY_REQUIRED_FIELDS = (
    "schemaVersion",
    "resourceId",
    "platform",
    "archiveRawSha256",
    "chunkIndex",
    "tag",
    "offset",
    "payloadOffset",
    "declaredSize",
    "endOffset",
    "payloadSha256",
    "logicalKey",
    "logicalDisplay",
    "logicalKeyMethod",
    "logicalOccurrence",
    "joinConfidence",
    "counterpartIndex",
    "counterpartDeclaredSize",
    "counterpartPayloadSha256",
    "sameDeclaredSize",
    "samePayloadSha256",
)


@dataclass(frozen=True)
class MipRecord:
    width: int
    height: int
    data: bytes

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.data)


@dataclass(frozen=True)
class TextureFrame:
    mips: tuple[MipRecord, ...]

    @property
    def payload(self) -> bytes:
        return b"".join(mip.data for mip in self.mips)

    @property
    def payload_sha256(self) -> str:
        return sha256_bytes(self.payload)


@dataclass(frozen=True)
class SerializedTexture:
    name: str
    normalized_name: str
    width: int
    height: int
    format_code: int
    frames: tuple[TextureFrame, ...]


@dataclass(frozen=True)
class DdsFrame:
    logical_name: str
    frame_index: int
    source_format_code: int
    source_format_name: str
    storage_format: str
    width: int
    height: int
    mips: tuple[MipRecord, ...]

    @property
    def payload_sha256(self) -> str:
        return sha256_bytes(b"".join(mip.data for mip in self.mips))


@dataclass(frozen=True)
class GeometryPair:
    resource_id: str
    logical_name: str
    logical_occurrence: int
    pc: dict[str, str]
    xbox: dict[str, str]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(lines: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for line in lines:
        digest.update(line.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise ValueError("u32 outside bounded texture data")
    return struct.unpack_from("<I", data, offset)[0]


def normalize_name(value: str) -> str:
    return value.replace("/", "\\").casefold()


def read_fixed_c_string(data: bytes, offset: int, length: int) -> str:
    if offset < 0 or length <= 0 or offset + length > len(data):
        raise ValueError("fixed string field escapes its owner")
    field = data[offset : offset + length]
    end = field.find(b"\0")
    if end < 0:
        raise ValueError("fixed string field has no NUL terminator")
    try:
        value = field[:end].decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError("fixed string field is not ASCII") from error
    if not value or any(ord(character) < 0x20 for character in value):
        raise ValueError("fixed string field is empty or contains a control byte")
    return value


def mip_extent(width: int, height: int, level: int) -> tuple[int, int]:
    if width <= 0 or height <= 0 or level < 0:
        raise ValueError("invalid mip extent request")
    return max(1, width >> level), max(1, height >> level)


def dxt_size(width: int, height: int, block_bytes: int) -> int:
    return max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_bytes


def xbox_mip_size(format_code: int, width: int, height: int) -> int:
    if format_code in (3, 4):
        return width * height * 4
    if format_code == 6:
        return dxt_size(width, height, 8)
    if format_code == 7:
        return dxt_size(width, height, 16)
    raise ValueError(f"unsupported Xbox CTEX format code {format_code}")


def dds_mip_size(storage_format: str, width: int, height: int) -> int:
    if storage_format == "DXT1":
        return dxt_size(width, height, 8)
    if storage_format in ("DXT2", "DXT3", "DXT5"):
        return dxt_size(width, height, 16)
    if storage_format in ("A8R8G8B8", "X8R8G8B8"):
        return width * height * 4
    if storage_format in ("A1R5G5B5", "A4R4G4B4", "R5G6B5"):
        return width * height * 2
    raise ValueError(f"unsupported DDS storage format {storage_format}")


def parse_serialized_texture(payload: bytes, *, platform: str) -> SerializedTexture:
    """Parse one complete TEXT payload and reject every unowned byte."""

    if platform not in ("PC", "XBOX"):
        raise ValueError("texture platform must be PC or XBOX")
    if len(payload) < CTEX_END or payload[:4] != b"DXTX":
        raise ValueError("TEXT is missing its DXTX owner")
    if u32(payload, 4) != len(payload) - 8:
        raise ValueError("DXTX does not cover the complete TEXT payload")
    if payload[CTEX_START : CTEX_START + 4] != b"CTEX":
        raise ValueError("DXTX is missing its CTEX prefix")
    if u32(payload, CTEX_START + 4) != CTEX_BODY_SIZE:
        raise ValueError("CTEX body size is not the measured 344 bytes")

    name = read_fixed_c_string(payload, CTEX_NAME_OFFSET, CTEX_NAME_LENGTH)
    width = u32(payload, CTEX_WIDTH_OFFSET)
    height = u32(payload, CTEX_HEIGHT_OFFSET)
    frame_count = u32(payload, CTEX_FRAME_COUNT_OFFSET)
    format_code = u32(payload, CTEX_FORMAT_OFFSET)
    if width <= 0 or height <= 0 or width > 16_384 or height > 16_384:
        raise ValueError("CTEX dimensions are outside the bounded texture profile")
    if frame_count <= 0 or frame_count > 256:
        raise ValueError("CTEX frame count is outside the bounded texture profile")
    if platform == "XBOX" and format_code not in XBOX_FORMAT_NAMES:
        raise ValueError("Xbox CTEX format code is outside the measured profile")
    if platform == "PC" and format_code not in SOURCE_FORMAT_NAMES:
        raise ValueError("PC CTEX source format code is outside the measured profile")

    frames: list[TextureFrame] = []
    offset = CTEX_END
    for frame_index in range(frame_count):
        if offset + 8 > len(payload) or payload[offset : offset + 4] != b"TFRM":
            raise ValueError(f"missing TFRM {frame_index}")
        frame_size = u32(payload, offset + 4)
        frame_end = offset + 8 + frame_size
        if frame_end > len(payload) or frame_size < 4:
            raise ValueError("TFRM escapes DXTX or lacks its mip count")
        body = payload[offset + 8 : frame_end]
        mip_count = u32(body, 0)
        if mip_count <= 0 or mip_count > 32:
            raise ValueError("TFRM mip count is outside the bounded profile")

        mips: list[MipRecord] = []
        nested = 4
        if platform == "PC":
            if frame_size != 4:
                raise ValueError("PC TFRM contains bytes beyond its mip count")
            for level in range(mip_count):
                mip_width, mip_height = mip_extent(width, height, level)
                mips.append(MipRecord(mip_width, mip_height, b""))
        else:
            for level in range(mip_count):
                if nested + 8 > len(body) or body[nested : nested + 4] != b"TMIP":
                    raise ValueError(f"missing TMIP {level} in TFRM {frame_index}")
                mip_size = u32(body, nested + 4)
                mip_end = nested + 8 + mip_size
                if mip_end > len(body):
                    raise ValueError("TMIP escapes its TFRM owner")
                mip_width, mip_height = mip_extent(width, height, level)
                expected = xbox_mip_size(format_code, mip_width, mip_height)
                if mip_size != expected:
                    raise ValueError(
                        "TMIP length disagrees with CTEX format and inferred extent"
                    )
                mips.append(
                    MipRecord(mip_width, mip_height, body[nested + 8 : mip_end])
                )
                nested = mip_end
            if nested != len(body):
                raise ValueError("TFRM has unowned bytes after its TMIP sequence")
        frames.append(TextureFrame(tuple(mips)))
        offset = frame_end

    if offset != len(payload):
        raise ValueError("DXTX has unowned bytes after its TFRM sequence")
    return SerializedTexture(
        name=name,
        normalized_name=normalize_name(name),
        width=width,
        height=height,
        format_code=format_code,
        frames=tuple(frames),
    )


def identify_dds_storage(data: bytes) -> str:
    pixel_flags = u32(data, 80)
    fourcc = data[84:88]
    if pixel_flags & 0x4:
        try:
            value = fourcc.decode("ascii")
        except UnicodeDecodeError as error:
            raise ValueError("DDS FourCC is not ASCII") from error
        if value not in ("DXT1", "DXT2", "DXT3", "DXT5"):
            raise ValueError(f"unsupported DDS FourCC {value!r}")
        return value

    bit_count = u32(data, 88)
    red = u32(data, 92)
    green = u32(data, 96)
    blue = u32(data, 100)
    alpha = u32(data, 104)
    masks = (red, green, blue, alpha)
    if bit_count == 32 and masks == (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
        return "A8R8G8B8"
    if bit_count == 32 and masks == (0x00FF0000, 0x0000FF00, 0x000000FF, 0):
        return "X8R8G8B8"
    if bit_count == 16 and masks == (0x00007C00, 0x000003E0, 0x0000001F, 0x00008000):
        return "A1R5G5B5"
    if bit_count == 16 and masks == (0x00000F00, 0x000000F0, 0x0000000F, 0x0000F000):
        return "A4R4G4B4"
    if bit_count == 16 and masks == (0x0000F800, 0x000007E0, 0x0000001F, 0):
        return "R5G6B5"
    raise ValueError(f"unsupported DDS bit layout {bit_count}/{masks!r}")


def parse_dds(data: bytes) -> tuple[str, int, int, tuple[MipRecord, ...]]:
    if len(data) < DDS_HEADER_LENGTH or data[:4] != b"DDS ":
        raise ValueError("inflated loose texture is not a complete DDS")
    if u32(data, 4) != 124 or u32(data, 76) != 32:
        raise ValueError("DDS fixed headers have unexpected sizes")
    height = u32(data, 12)
    width = u32(data, 16)
    mip_count = u32(data, 28) or 1
    if width <= 0 or height <= 0 or width > 16_384 or height > 16_384:
        raise ValueError("DDS dimensions are outside the bounded profile")
    if mip_count <= 0 or mip_count > 32:
        raise ValueError("DDS mip count is outside the bounded profile")
    storage = identify_dds_storage(data)
    mips: list[MipRecord] = []
    offset = DDS_HEADER_LENGTH
    for level in range(mip_count):
        mip_width, mip_height = mip_extent(width, height, level)
        size = dds_mip_size(storage, mip_width, mip_height)
        end = offset + size
        if end > len(data):
            raise ValueError("DDS mip escapes the inflated file")
        mips.append(MipRecord(mip_width, mip_height, data[offset:end]))
        offset = end
    if offset != len(data):
        raise ValueError("DDS has bytes beyond its declared mip chain")
    return storage, width, height, tuple(mips)


def parse_dds_filename(
    filename: str, *, mustbe: bool
) -> tuple[str, int, int, str] | None:
    value = filename
    if mustbe:
        if not value.casefold().startswith("mustbe_"):
            return None
        value = value[len("mustbe_") :]
    match = DDS_FILENAME_RE.fullmatch(value)
    if match is None:
        return None
    source_format_name = match.group("format").casefold()
    # Windows truncated several long retail filenames from the right.  The
    # logical name and frame remain recoverable for 798/800 files, while 19 of
    # those names retain only a prefix of the source-format suffix.  Preserve
    # that partial suffix and let the serialized PC CTEX format code select it;
    # do not guess a code from a short prefix such as ``A``.
    source_format_code = SOURCE_FORMAT_CODES.get(source_format_name, 0)
    return (
        normalize_name(match.group("name").replace("%", "\\")),
        int(match.group("frame")),
        source_format_code,
        source_format_name.upper() + ("?" if source_format_code == 0 else ""),
    )


def scan_dds_shelves(
    pc_resource_root: Path,
    selected_names: frozenset[str],
) -> tuple[dict[tuple[str, int, int], DdsFrame], dict[str, object]]:
    dxt_root = pc_resource_root / "dxtntextures"
    mustbe_root = pc_resource_root / "textures"
    if not dxt_root.is_dir() or not mustbe_root.is_dir():
        raise ValueError("PC resource root lacks dxtntextures/textures")

    selected: dict[tuple[str, int, int], DdsFrame] = {}
    manifests: dict[str, list[str]] = {"dxtntextures": [], "textures": []}
    shelf_counts: dict[str, Counter[str]] = {
        "dxtntextures": Counter(),
        "textures": Counter(),
    }
    unparsed: dict[str, list[str]] = {"dxtntextures": [], "textures": []}

    for shelf, root, mustbe in (
        ("dxtntextures", dxt_root, False),
        ("textures", mustbe_root, True),
    ):
        paths = sorted(root.glob("*.aya"), key=lambda path: path.name.casefold())
        for path in paths:
            stored = aya.read_held_archive(path)
            inflated = aya.inflate_aya_bytes(stored)
            storage, width, height, mips = parse_dds(inflated)
            parsed = parse_dds_filename(path.name, mustbe=mustbe)
            shelf_counts[shelf]["fileCount"] += 1
            shelf_counts[shelf][f"storage:{storage}"] += 1
            if parsed is None:
                unparsed[shelf].append(path.name.casefold())
                logical_name = "<unparsed>"
                frame_index = -1
                source_code = -1
                source_name = "<unparsed>"
            else:
                logical_name, frame_index, source_code, source_name = parsed
                shelf_counts[shelf]["parsedFilenameCount"] += 1
                if logical_name in selected_names:
                    key = (logical_name, frame_index, source_code)
                    if key in selected:
                        raise ValueError("duplicate selected DDS frame/source-format key")
                    selected[key] = DdsFrame(
                        logical_name=logical_name,
                        frame_index=frame_index,
                        source_format_code=source_code,
                        source_format_name=source_name,
                        storage_format=storage,
                        width=width,
                        height=height,
                        mips=mips,
                    )
                    shelf_counts[shelf]["selectedFileCount"] += 1
            manifests[shelf].append(
                "\t".join(
                    (
                        path.name.casefold(),
                        str(len(stored)),
                        sha256_bytes(stored),
                        str(len(inflated)),
                        sha256_bytes(inflated),
                        logical_name,
                        str(frame_index),
                        str(source_code),
                        source_name,
                        storage,
                        str(width),
                        str(height),
                        str(len(mips)),
                    )
                )
            )

    summary: dict[str, object] = {
        shelf: {
            **dict(sorted(shelf_counts[shelf].items())),
            "unparsedFilenames": sorted(unparsed[shelf]),
            "canonicalManifestSha256": canonical_sha256(manifests[shelf]),
        }
        for shelf in ("dxtntextures", "textures")
    }
    by_frame: dict[tuple[str, int], list[DdsFrame]] = defaultdict(list)
    for frame in selected.values():
        by_frame[(frame.logical_name, frame.frame_index)].append(frame)
    summary["selectedFrameSourceVariantGroups"] = [
        {
            "logicalName": logical_name,
            "frameIndex": frame_index,
            "candidates": [
                {
                    "sourceFormatCode": frame.source_format_code,
                    "sourceFormatName": frame.source_format_name,
                    "storageFormat": frame.storage_format,
                    "width": frame.width,
                    "height": frame.height,
                    "mipCount": len(frame.mips),
                }
                for frame in sorted(
                    frames,
                    key=lambda item: (
                        item.source_format_code,
                        item.source_format_name,
                        item.storage_format,
                    ),
                )
            ],
        }
        for (logical_name, frame_index), frames in sorted(by_frame.items())
        if len(frames) > 1
    ]
    return selected, summary


def dds_candidates(
    frames: dict[tuple[str, int, int], DdsFrame],
    logical_name: str,
    frame_index: int,
) -> tuple[DdsFrame, ...]:
    return tuple(
        sorted(
            (
                frame
                for (name, index, _format_code), frame in frames.items()
                if name == logical_name and index == frame_index
            ),
            key=lambda item: (
                item.source_format_code,
                item.source_format_name,
                item.storage_format,
            ),
        )
    )


def select_dds_frame(
    frames: dict[tuple[str, int, int], DdsFrame],
    logical_name: str,
    frame_index: int,
    *,
    ctex_format_code: int | None,
) -> tuple[DdsFrame, tuple[DdsFrame, ...]]:
    """Select one loose DDS only with an explicit serialized-format oracle.

    A basename-only caller may use a unique candidate.  It must refuse two or
    more candidates rather than inheriting directory enumeration order.
    """

    candidates = dds_candidates(frames, logical_name, frame_index)
    if not candidates:
        raise ValueError("paired PC TEXT has no loose DDS frame")
    if ctex_format_code is None:
        if len(candidates) != 1:
            raise ValueError("basename-only loose DDS selection is ambiguous")
        return candidates[0], candidates

    exact = [
        frame for frame in candidates if frame.source_format_code == ctex_format_code
    ]
    if len(exact) == 1:
        return exact[0], candidates
    if exact:
        raise ValueError("CTEX format selects duplicate loose DDS candidates")
    expected_name = SOURCE_FORMAT_NAMES[ctex_format_code]
    partial = [
        frame
        for frame in candidates
        if frame.source_format_code == 0
        and expected_name.startswith(frame.source_format_name.rstrip("?"))
    ]
    if len(partial) == 1:
        return partial[0], candidates
    raise ValueError("CTEX format does not select exactly one loose DDS candidate")


def select_conservative_basename_candidate(
    candidates: tuple[DdsFrame, ...],
) -> DdsFrame:
    """Apply the explicit historical name-only lower-bound rule.

    Unique basenames are unambiguous.  The measured retail duplicate shape is
    exactly source codes 2 and 5; the historical census chose the code-5
    R5G6B5-request file.  Any other duplicate shape refuses instead of falling
    back to enumeration order.
    """

    if len(candidates) == 1:
        return candidates[0]
    by_code = {frame.source_format_code: frame for frame in candidates}
    if len(by_code) == len(candidates) == 2 and set(by_code) == {2, 5}:
        return by_code[5]
    raise ValueError("unsupported basename-only loose DDS candidate shape")


def classify_one_frame(
    *,
    dds: DdsFrame,
    xbox_format_code: int,
    xbox_frame: TextureFrame,
    shift: int,
) -> tuple[bool, bool | None, str]:
    comparable = (dds.storage_format, xbox_format_code) in COMPARABLE_LAYOUTS
    aligned_equal: bool | None = None
    if comparable:
        aligned_equal = all(
            dds.mips[level + shift].data == xbox_mip.data
            for level, xbox_mip in enumerate(xbox_frame.mips)
        )
    if not comparable:
        comparison = "format-changed"
    elif shift:
        comparison = (
            "shifted-comparable-exact"
            if aligned_equal
            else "shifted-comparable-different"
        )
    else:
        comparison = (
            "comparable-full-topology-exact"
            if aligned_equal
            else "comparable-full-topology-different"
        )
    return comparable, aligned_equal, comparison


def classify_frame_comparison(
    *,
    dds: DdsFrame,
    candidates: tuple[DdsFrame, ...],
    xbox_format_code: int,
    xbox_frame: TextureFrame,
    shift: int,
) -> tuple[bool, bool | None, str, DdsFrame, bool | None, str]:
    """Return CTEX-selected and conservative comparison classifications."""

    comparable, aligned_equal, resolved = classify_one_frame(
        dds=dds,
        xbox_format_code=xbox_format_code,
        xbox_frame=xbox_frame,
        shift=shift,
    )
    conservative_dds = select_conservative_basename_candidate(candidates)
    (
        conservative_comparable,
        conservative_equal,
        conservative,
    ) = classify_one_frame(
        dds=conservative_dds,
        xbox_format_code=xbox_format_code,
        xbox_frame=xbox_frame,
        shift=shift,
    )

    # Eight logical frame identities have two source-format files.  Seven have
    # both DXT1 and DXT2 storage; their 462 CTEX-code-2/Xbox-code-7 rows are
    # comparable only after CTEX selects the A4R4G4B4-suffixed DXT2 file.  The
    # conservative population keeps those rows explicitly unresolved so it
    # reproduces the earlier 11,332 exact-chain lower bound.
    source_variant_ambiguous = (
        conservative_dds is not dds
        and comparable
        and not conservative_comparable
        and xbox_format_code == 7
    )
    if source_variant_ambiguous:
        conservative = "source-variant-ambiguous"
    return (
        comparable,
        aligned_equal,
        resolved,
        conservative_dds,
        conservative_equal,
        conservative,
    )


def read_geometry_pairs(
    geometry_path: Path,
) -> tuple[list[GeometryPair], dict[str, object]]:
    pc: dict[tuple[str, str, int], dict[str, str]] = {}
    xbox: dict[tuple[str, str, int], dict[str, str]] = {}
    row_count = 0
    with geometry_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if tuple(reader.fieldnames or ()) != GEOMETRY_REQUIRED_FIELDS:
            raise ValueError("pair geometry columns do not match v2")
        for row in reader:
            row_count += 1
            if row["schemaVersion"] != cross.GEOMETRY_SCHEMA:
                raise ValueError("pair geometry schema changed")
            if row["tag"] != "TEXT" or not row["counterpartIndex"]:
                continue
            if row["logicalKeyMethod"] != "DXTX/CTEX:name@0x18":
                raise ValueError("paired TEXT key method changed")
            key = (
                row["resourceId"],
                row["logicalKey"],
                int(row["logicalOccurrence"]),
            )
            owner = pc if row["platform"] == "PC" else xbox if row["platform"] == "XBOX" else None
            if owner is None:
                raise ValueError("pair geometry contains an unknown platform")
            if key in owner:
                raise ValueError("duplicate paired TEXT geometry row")
            owner[key] = row

    if set(pc) != set(xbox):
        raise ValueError("paired TEXT geometry is asymmetric")
    pairs: list[GeometryPair] = []
    for resource_id, logical_name, occurrence in sorted(pc):
        pc_row = pc[(resource_id, logical_name, occurrence)]
        xbox_row = xbox[(resource_id, logical_name, occurrence)]
        if pc_row["counterpartIndex"] != xbox_row["chunkIndex"]:
            raise ValueError("PC paired TEXT counterpart index changed")
        if xbox_row["counterpartIndex"] != pc_row["chunkIndex"]:
            raise ValueError("Xbox paired TEXT counterpart index changed")
        if pc_row["counterpartPayloadSha256"] != xbox_row["payloadSha256"]:
            raise ValueError("PC paired TEXT counterpart hash changed")
        if xbox_row["counterpartPayloadSha256"] != pc_row["payloadSha256"]:
            raise ValueError("Xbox paired TEXT counterpart hash changed")
        pairs.append(
            GeometryPair(
                resource_id=resource_id,
                logical_name=logical_name,
                logical_occurrence=occurrence,
                pc=pc_row,
                xbox=xbox_row,
            )
        )
    return pairs, {
        "schemaVersion": cross.GEOMETRY_SCHEMA,
        "rowCount": row_count,
        "pairedTextOccurrenceCount": len(pairs),
        "sha256": sha256_file(geometry_path),
    }


def index_actual_text_chunks(
    raw: bytes, chunks: Sequence[aya.ChunkEntry]
) -> dict[tuple[str, int], tuple[aya.ChunkEntry, bytes]]:
    result: dict[tuple[str, int], tuple[aya.ChunkEntry, bytes]] = {}
    occurrences: Counter[str] = Counter()
    for chunk in chunks:
        if chunk.tag != "TEXT":
            continue
        payload = raw[chunk.offset + 8 : chunk.offset + 8 + chunk.size]
        key, _display, method = cross.logical_key("TEXT", payload)
        if method != "DXTX/CTEX:name@0x18":
            raise ValueError("actual TEXT logical-key contract changed")
        occurrence = occurrences[key]
        occurrences[key] += 1
        result[(key, occurrence)] = (chunk, payload)
    return result


def validate_geometry_row(
    row: dict[str, str],
    raw: bytes,
    chunk: aya.ChunkEntry,
    payload: bytes,
) -> None:
    if row["archiveRawSha256"] != sha256_bytes(raw):
        raise ValueError("resource raw hash disagrees with frozen pair geometry")
    expected = {
        "chunkIndex": chunk.index,
        "offset": chunk.offset,
        "payloadOffset": chunk.offset + 8,
        "declaredSize": chunk.size,
        "endOffset": chunk.offset + 8 + chunk.size,
    }
    for field, value in expected.items():
        if int(row[field]) != value:
            raise ValueError(f"TEXT {field} disagrees with frozen pair geometry")
    if row["payloadSha256"] != sha256_bytes(payload):
        raise ValueError("TEXT payload hash disagrees with frozen pair geometry")


def topology_shift(pc: SerializedTexture, xbox: SerializedTexture) -> int:
    if len(pc.frames) != len(xbox.frames):
        raise ValueError("paired texture frame counts differ")
    pc_counts = tuple(len(frame.mips) for frame in pc.frames)
    xbox_counts = tuple(len(frame.mips) for frame in xbox.frames)
    for shift in range(min(pc_counts)):
        shifted_width, shifted_height = mip_extent(pc.width, pc.height, shift)
        if (xbox.width, xbox.height) != (shifted_width, shifted_height):
            continue
        if all(xbox_count == pc_count - shift for pc_count, xbox_count in zip(pc_counts, xbox_counts)):
            return shift
    raise ValueError("paired texture topology is not a suffix of the PC mip chain")


def compact_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def process_corpus(
    *,
    pc_resource_root: Path,
    xbox_zip: Path,
    pairs: list[GeometryPair],
    dds_frames: dict[tuple[str, int, int], DdsFrame],
) -> tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    by_resource: dict[str, list[GeometryPair]] = defaultdict(list)
    for pair in pairs:
        by_resource[pair.resource_id].append(pair)

    pc_paths: dict[str, Path] = {}
    for path in pc_resource_root.glob("*_res_PC.aya"):
        key = cross.resource_id(path.name, "_res_pc.aya")
        if key in pc_paths:
            raise ValueError("duplicate PC resource id")
        pc_paths[key] = path

    occurrence_rows: list[dict[str, object]] = []
    frame_rows: list[dict[str, object]] = []
    mip_rows: list[dict[str, object]] = []
    resource_rows: list[dict[str, object]] = []
    variant_payloads: dict[tuple[str, int, int], set[str]] = defaultdict(set)
    variant_resources: dict[tuple[str, int, int], set[str]] = defaultdict(set)
    source_resource_payloads: dict[tuple[str, int, int, str], set[str]] = (
        defaultdict(set)
    )
    aggregate: Counter[str] = Counter()
    format_codes: Counter[str] = Counter()
    transitions: Counter[str] = Counter()
    resolved_comparisons: Counter[str] = Counter()
    conservative_comparisons: Counter[str] = Counter()
    source_selections: Counter[str] = Counter()
    duplicate_source_selections: Counter[str] = Counter()
    one_mip_names: set[str] = set()
    one_mip_resources: set[str] = set()
    sky_rows: list[tuple[str, str, int]] = []
    code7_extent: Counter[str] = Counter()
    used_dds_keys: set[tuple[str, int, int]] = set()

    with ZipFile(xbox_zip) as archive:
        xbox_members: dict[str, ZipInfo] = {}
        for info in archive.infolist():
            if not info.filename.casefold().endswith("_res_xbox.aya"):
                continue
            key = cross.resource_id(info.filename, "_res_xbox.aya")
            if key in xbox_members:
                raise ValueError("duplicate Xbox resource id")
            xbox_members[key] = info

        for resource_id in sorted(by_resource):
            if resource_id not in pc_paths or resource_id not in xbox_members:
                raise ValueError("frozen TEXT pair references a missing resource")
            pc_source = aya.read_held_archive(pc_paths[resource_id])
            pc_raw, pc_chunks, _pc_members, pc_envelope = aya.decode_archive_envelope(
                pc_source, "pc-chunked-zlib"
            )
            if pc_envelope != "pc-chunked-zlib":
                raise ValueError("PC resource envelope changed")
            xbox_source = cross.read_zip_member(archive, xbox_members[resource_id])
            xbox_raw, xbox_chunks, _xbox_members, xbox_envelope = aya.decode_archive_envelope(
                xbox_source, "raw-tag-stream"
            )
            if xbox_envelope != "raw-tag-stream":
                raise ValueError("Xbox resource envelope changed")
            pc_actual = index_actual_text_chunks(pc_raw, pc_chunks)
            xbox_actual = index_actual_text_chunks(xbox_raw, xbox_chunks)
            resource_counter: Counter[str] = Counter()

            for pair in sorted(
                by_resource[resource_id],
                key=lambda item: (item.logical_name, item.logical_occurrence),
            ):
                key = (pair.logical_name, pair.logical_occurrence)
                if key not in pc_actual or key not in xbox_actual:
                    raise ValueError("frozen paired TEXT row is absent from actual resource")
                pc_chunk, pc_payload = pc_actual[key]
                xbox_chunk, xbox_payload = xbox_actual[key]
                validate_geometry_row(pair.pc, pc_raw, pc_chunk, pc_payload)
                validate_geometry_row(pair.xbox, xbox_raw, xbox_chunk, xbox_payload)
                pc_texture = parse_serialized_texture(pc_payload, platform="PC")
                xbox_texture = parse_serialized_texture(xbox_payload, platform="XBOX")
                if pc_texture.normalized_name != pair.logical_name:
                    raise ValueError("PC CTEX name disagrees with frozen logical key")
                if xbox_texture.normalized_name != pair.logical_name:
                    raise ValueError("Xbox CTEX name disagrees with frozen logical key")
                shift = topology_shift(pc_texture, xbox_texture)
                if shift not in (0, 1):
                    raise ValueError("retail proof profile admits only zero/one top-mip shifts")
                aggregate["pairedTextOccurrenceCount"] += 1
                aggregate["dimensionEqualCount" if shift == 0 else "dimensionDifferentCount"] += 1
                aggregate["mipTopologyEqualCount" if shift == 0 else "oneTopMipDroppedCount"] += 1
                resource_counter["pairedTextOccurrenceCount"] += 1
                resource_counter["dimensionEqualCount" if shift == 0 else "oneTopMipDroppedCount"] += 1
                if shift == 1:
                    one_mip_names.add(pair.logical_name)
                    one_mip_resources.add(resource_id)

                occurrence_rows.append(
                    {
                        "schemaVersion": OCCURRENCE_SCHEMA,
                        "resourceId": resource_id,
                        "logicalName": pair.logical_name,
                        "logicalOccurrence": pair.logical_occurrence,
                        "pcChunkIndex": pc_chunk.index,
                        "xboxChunkIndex": xbox_chunk.index,
                        "pcWidth": pc_texture.width,
                        "pcHeight": pc_texture.height,
                        "xboxWidth": xbox_texture.width,
                        "xboxHeight": xbox_texture.height,
                        "frameCount": len(pc_texture.frames),
                        "pcMipCounts": ",".join(str(len(frame.mips)) for frame in pc_texture.frames),
                        "xboxMipCounts": ",".join(str(len(frame.mips)) for frame in xbox_texture.frames),
                        "pcCtexFormatCode": pc_texture.format_code,
                        "xboxCtexFormatCode": xbox_texture.format_code,
                        "topMipsDropped": shift,
                    }
                )

                for frame_index, (pc_frame, xbox_frame) in enumerate(
                    zip(pc_texture.frames, xbox_texture.frames)
                ):
                    dds_key = (pair.logical_name, frame_index, pc_texture.format_code)
                    dds, candidates = select_dds_frame(
                        dds_frames,
                        pair.logical_name,
                        frame_index,
                        ctex_format_code=pc_texture.format_code,
                    )
                    used_dds_keys.add(dds_key)
                    if (dds.width, dds.height) != (pc_texture.width, pc_texture.height):
                        raise ValueError("PC CTEX dimensions disagree with selected DDS")
                    if len(dds.mips) != len(pc_frame.mips):
                        raise ValueError("PC TFRM mip count disagrees with selected DDS")
                    if any(
                        (left.width, left.height) != (right.width, right.height)
                        for left, right in zip(dds.mips, pc_frame.mips)
                    ):
                        raise ValueError("PC TFRM inferred extents disagree with selected DDS")

                    (
                        comparable,
                        aligned_equal,
                        comparison,
                        conservative_dds,
                        conservative_equal,
                        conservative_comparison,
                    ) = classify_frame_comparison(
                        dds=dds,
                        candidates=candidates,
                        xbox_format_code=xbox_texture.format_code,
                        xbox_frame=xbox_frame,
                        shift=shift,
                    )
                    resolved_comparisons[comparison] += 1
                    conservative_comparisons[conservative_comparison] += 1
                    resource_counter[comparison] += 1
                    aggregate["occurrenceFrameCount"] += 1
                    format_codes[str(xbox_texture.format_code)] += 1
                    transition = f"{dds.storage_format}->code{xbox_texture.format_code}"
                    transitions[transition] += 1
                    source_selection = (
                        f"code{pc_texture.format_code}:"
                        f"{dds.source_format_name}:stored-{dds.storage_format}"
                        f"->xbox-code{xbox_texture.format_code}"
                    )
                    source_selections[source_selection] += 1
                    if len(candidates) > 1:
                        duplicate_source_selections[source_selection] += 1

                    if dds.storage_format == "DXT1" and xbox_texture.format_code == 3:
                        if not pair.logical_name.startswith("cubes\\cube"):
                            raise ValueError("DXT1-to-code3 frame is not a measured cube texture")
                        sky_rows.append((resource_id, pair.logical_name, frame_index))

                    if xbox_texture.format_code == 7:
                        ambiguous = all(
                            len(mip.data) == mip.width * mip.height
                            for mip in xbox_frame.mips
                        )
                        code7_extent["bpp8-extent-ambiguous" if ambiguous else "dxt16-extent-unambiguous"] += 1

                    variant_key = (
                        pair.logical_name,
                        frame_index,
                        pc_texture.format_code,
                    )
                    variant_payloads[variant_key].add(xbox_frame.payload_sha256)
                    variant_resources[variant_key].add(resource_id)
                    source_resource_payloads[(*variant_key, resource_id)].add(
                        xbox_frame.payload_sha256
                    )
                    frame_rows.append(
                        {
                            "schemaVersion": FRAME_SCHEMA,
                            "resourceId": resource_id,
                            "logicalName": pair.logical_name,
                            "logicalOccurrence": pair.logical_occurrence,
                            "frameIndex": frame_index,
                            "pcWidth": pc_texture.width,
                            "pcHeight": pc_texture.height,
                            "pcMipCount": len(dds.mips),
                            "pcSourceFormatCode": pc_texture.format_code,
                            "pcSourceFormatName": dds.source_format_name,
                            "pcStorageFormat": dds.storage_format,
                            "pcPayloadSha256": dds.payload_sha256,
                            "conservativePcSourceFormatCode": conservative_dds.source_format_code,
                            "conservativePcSourceFormatName": conservative_dds.source_format_name,
                            "conservativePcStorageFormat": conservative_dds.storage_format,
                            "conservativePcPayloadSha256": conservative_dds.payload_sha256,
                            "xboxWidth": xbox_texture.width,
                            "xboxHeight": xbox_texture.height,
                            "xboxMipCount": len(xbox_frame.mips),
                            "xboxCtexFormatCode": xbox_texture.format_code,
                            "xboxStorageClass": XBOX_FORMAT_NAMES[xbox_texture.format_code],
                            "xboxPayloadSha256": xbox_frame.payload_sha256,
                            "topMipsDropped": shift,
                            "looseDdsCandidateCount": len(candidates),
                            "looseDdsCandidateStorageFormats": ",".join(
                                sorted({candidate.storage_format for candidate in candidates})
                            ),
                            "rawBlocksComparable": int(comparable),
                            "alignedPayloadEqual": "" if aligned_equal is None else int(aligned_equal),
                            "conservativeAlignedPayloadEqual": (
                                "" if conservative_equal is None else int(conservative_equal)
                            ),
                            "ctexSelectedComparisonClass": comparison,
                            "conservativeComparisonClass": conservative_comparison,
                        }
                    )
                    for xbox_level, xbox_mip in enumerate(xbox_frame.mips):
                        pc_level = xbox_level + shift
                        pc_mip = dds.mips[pc_level]
                        same_bytes: bool | None = None
                        if comparable:
                            same_bytes = pc_mip.data == xbox_mip.data
                        mip_rows.append(
                            {
                                "schemaVersion": MIP_SCHEMA,
                                "resourceId": resource_id,
                                "logicalName": pair.logical_name,
                                "logicalOccurrence": pair.logical_occurrence,
                                "frameIndex": frame_index,
                                "xboxMipIndex": xbox_level,
                                "pcMipIndex": pc_level,
                                "width": xbox_mip.width,
                                "height": xbox_mip.height,
                                "pcStoredBytes": len(pc_mip.data),
                                "xboxStoredBytes": len(xbox_mip.data),
                                "rawBlocksComparable": int(comparable),
                                "sameStoredBytes": "" if same_bytes is None else int(same_bytes),
                                "pcMipSha256": pc_mip.sha256,
                                "xboxMipSha256": xbox_mip.sha256,
                            }
                        )

            resource_rows.append(
                {
                    "resourceId": resource_id,
                    **{key: resource_counter[key] for key in sorted(resource_counter)},
                }
            )

    selected_source_frame_identities = set(used_dds_keys)
    if selected_source_frame_identities != set(variant_payloads):
        raise ValueError("PC selected-source-frame and Xbox variant populations differ")
    selected_frame_identities = {
        (name, frame_index)
        for name, frame_index, _source_code in selected_source_frame_identities
    }
    variant_rows: list[dict[str, object]] = []
    variant_histogram: Counter[str] = Counter()
    for logical_name, frame_index, source_code in sorted(variant_payloads):
        variant_key = (logical_name, frame_index, source_code)
        count = len(variant_payloads[variant_key])
        variant_histogram[str(count)] += 1
        variant_rows.append(
            {
                "schemaVersion": VARIANT_SCHEMA,
                "logicalName": logical_name,
                "frameIndex": frame_index,
                "pcSourceFormatCode": source_code,
                "pcSourceFormatName": SOURCE_FORMAT_NAMES[source_code],
                "resourceCount": len(variant_resources[variant_key]),
                "xboxPayloadVariantCount": count,
                "xboxPayloadVariantSha256": ",".join(
                    sorted(variant_payloads[variant_key])
                ),
            }
        )

    source_resource_histogram: Counter[str] = Counter()
    resource_source_frames: Counter[str] = Counter()
    resource_multi_payload_frames: Counter[str] = Counter()
    for (*_source_key, resource_id), payloads in sorted(source_resource_payloads.items()):
        count = len(payloads)
        source_resource_histogram[str(count)] += 1
        resource_source_frames[resource_id] += 1
        if count > 1:
            resource_multi_payload_frames[resource_id] += 1
    for row in resource_rows:
        resource_id = str(row["resourceId"])
        row["xboxSourceFrameIdentityCount"] = resource_source_frames[resource_id]
        row["xboxMultiPayloadSourceFrameIdentityCount"] = (
            resource_multi_payload_frames[resource_id]
        )

    metrics = {
        **dict(sorted(aggregate.items())),
        "logicalTextureCount": len({pair.logical_name for pair in pairs}),
        "selectedPcFrameIdentityCount": len(selected_frame_identities),
        "usedSelectedDdsKeyCount": len(used_dds_keys),
        "oneTopMipDroppedUniqueNameCount": len(one_mip_names),
        "oneTopMipDroppedResourceCount": len(one_mip_resources),
        "oneTopMipDroppedNames": sorted(one_mip_names),
        "xboxFormatCodeFrameCounts": compact_counter(format_codes),
        "pcStorageToXboxCodeFrameCounts": compact_counter(transitions),
        "pcCtexSourceSelectionFrameCounts": compact_counter(source_selections),
        "duplicateFrameCtexSourceSelectionCounts": compact_counter(
            duplicate_source_selections
        ),
        "ctexSelectedFrameComparisonCounts": compact_counter(resolved_comparisons),
        "conservativeFrameComparisonCounts": compact_counter(conservative_comparisons),
        "ctexSelectedFullTopologyExactComparableFrameCount": resolved_comparisons[
            "comparable-full-topology-exact"
        ],
        "conservativeFullTopologyExactComparableFrameCount": conservative_comparisons[
            "comparable-full-topology-exact"
        ],
        "conservativeSourceVariantAmbiguousFrameCount": conservative_comparisons[
            "source-variant-ambiguous"
        ],
        "conservativeNonComparableOrFormatChangedFrameCount": (
            conservative_comparisons["format-changed"]
            + conservative_comparisons["source-variant-ambiguous"]
        ),
        "skyCubePcDxt1ToXboxCode3FrameCount": len(sky_rows),
        "skyCubePcDxt1ToXboxCode3Resources": sorted({row[0] for row in sky_rows}),
        "xboxCode7ExtentClassification": compact_counter(code7_extent),
        "xboxPayloadVariantHistogram": compact_counter(variant_histogram),
        "xboxSourceFrameIdentityCount": len(variant_payloads),
        "xboxMultiPayloadVariantSourceFrameCount": sum(
            count for variants, count in variant_histogram.items() if int(variants) > 1
        ),
        "xboxSourceResourceGroupCount": len(source_resource_payloads),
        "xboxWithinResourcePayloadVariantHistogram": compact_counter(
            source_resource_histogram
        ),
        "xboxWithinResourceMultiPayloadGroupCount": sum(
            count
            for variants, count in source_resource_histogram.items()
            if int(variants) > 1
        ),
    }
    return metrics, occurrence_rows, frame_rows, mip_rows, variant_rows, resource_rows


def validate_known_profile(
    *,
    geometry: dict[str, object],
    xbox_zip: Path,
    source_file: Path,
    pc_resource_count: int,
    dds_summary: dict[str, object],
    metrics: dict[str, object],
) -> None:
    if geometry != {
        "schemaVersion": cross.GEOMETRY_SCHEMA,
        "rowCount": 47_657,
        "pairedTextOccurrenceCount": 18_612,
        "sha256": KNOWN_GEOMETRY_SHA256,
    }:
        raise ValueError("known profile: frozen pair geometry changed")
    if xbox_zip.stat().st_size != KNOWN_XBOX_ZIP_LENGTH:
        raise ValueError("known profile: Xbox ZIP length changed")
    if sha256_file(xbox_zip) != KNOWN_XBOX_ZIP_SHA256:
        raise ValueError("known profile: Xbox ZIP hash changed")
    if sha256_file(source_file) != KNOWN_RESOURCE_ACCUMULATOR_SHA256:
        raise ValueError("known profile: ResourceAccumulator.cpp hash changed")
    if pc_resource_count != 301:
        raise ValueError("known profile: PC resource shelf count changed")

    dxt = dds_summary["dxtntextures"]
    textures = dds_summary["textures"]
    expected_dxt = {
        "fileCount": 800,
        "parsedFilenameCount": 798,
        "selectedFileCount": 595,
        "storage:DXT1": 212,
        "storage:DXT2": 588,
        "unparsedFilenames": list(KNOWN_UNPARSED_DXT_FILENAMES),
        "canonicalManifestSha256": KNOWN_DXT_MANIFEST_SHA256,
    }
    for key, value in expected_dxt.items():
        if dxt.get(key) != value:
            raise ValueError(f"known profile: dxtntextures {key} changed")
    expected_textures = {
        "fileCount": 47,
        "parsedFilenameCount": 47,
        "storage:A1R5G5B5": 38,
        "storage:A8R8G8B8": 9,
        "selectedFileCount": 5,
        "unparsedFilenames": [],
        "canonicalManifestSha256": KNOWN_TEXTURES_MANIFEST_SHA256,
    }
    for key, value in expected_textures.items():
        if textures.get(key) != value:
            raise ValueError(f"known profile: textures {key} changed")

    expected_scalars = {
        "pairedTextOccurrenceCount": 18_612,
        "logicalTextureCount": 589,
        "selectedPcFrameIdentityCount": 592,
        "usedSelectedDdsKeyCount": 600,
        "occurrenceFrameCount": 18_669,
        "dimensionEqualCount": 18_579,
        "dimensionDifferentCount": 33,
        "mipTopologyEqualCount": 18_579,
        "oneTopMipDroppedCount": 33,
        "oneTopMipDroppedUniqueNameCount": 13,
        "oneTopMipDroppedResourceCount": 16,
        "ctexSelectedFullTopologyExactComparableFrameCount": 11_762,
        "conservativeFullTopologyExactComparableFrameCount": 11_332,
        "conservativeSourceVariantAmbiguousFrameCount": 462,
        "conservativeNonComparableOrFormatChangedFrameCount": 4_564,
        "skyCubePcDxt1ToXboxCode3FrameCount": 25,
        "xboxSourceFrameIdentityCount": 600,
        "xboxMultiPayloadVariantSourceFrameCount": 357,
        "xboxSourceResourceGroupCount": 18_669,
        "xboxWithinResourceMultiPayloadGroupCount": 0,
    }
    for key, value in expected_scalars.items():
        if metrics.get(key) != value:
            raise ValueError(f"known profile: metric {key} changed")
    expected_maps = {
        "xboxFormatCodeFrameCounts": {"3": 25, "4": 265, "6": 10_282, "7": 8_097},
        "pcStorageToXboxCodeFrameCounts": {
            "A8R8G8B8->code4": 265,
            "DXT1->code3": 25,
            "DXT1->code6": 6_205,
            "DXT2->code6": 4_077,
            "DXT2->code7": 8_097,
        },
        "ctexSelectedFrameComparisonCounts": {
            "comparable-full-topology-different": 2_797,
            "comparable-full-topology-exact": 11_762,
            "format-changed": 4_102,
            "shifted-comparable-different": 2,
            "shifted-comparable-exact": 6,
        },
        "conservativeFrameComparisonCounts": {
            "comparable-full-topology-different": 2_765,
            "comparable-full-topology-exact": 11_332,
            "format-changed": 4_102,
            "shifted-comparable-different": 2,
            "shifted-comparable-exact": 6,
            "source-variant-ambiguous": 462,
        },
        "duplicateFrameCtexSourceSelectionCounts": {
            "code2:A4R4G4B4:stored-DXT1->xbox-code6": 66,
            "code2:A4R4G4B4:stored-DXT2->xbox-code7": 462,
            "code5:R5G6B5:stored-DXT1->xbox-code6": 529,
        },
        "xboxCode7ExtentClassification": {
            "bpp8-extent-ambiguous": 6_931,
            "dxt16-extent-unambiguous": 1_166,
        },
        "xboxPayloadVariantHistogram": {"1": 243, "2": 334, "3": 20, "4": 3},
        "xboxWithinResourcePayloadVariantHistogram": {"1": 18_669},
    }
    for key, value in expected_maps.items():
        if metrics.get(key) != value:
            raise ValueError(f"known profile: metric map {key} changed")
    variant_groups = dds_summary.get("selectedFrameSourceVariantGroups")
    if not isinstance(variant_groups, list) or len(variant_groups) != 8:
        raise ValueError("known profile: loose DDS source-variant group count changed")
    expected_variant_names = {
        "particle\\alparticle4.tga",
        "particle\\blood.tga",
        "particle\\blue spark 2.tga",
        "particle\\fireball.tga",
        "particle\\muspell bullet.tga",
        "particle\\particles.tga",
        "particle\\small puff.tga",
        "particle\\smoke trail.tga",
    }
    if {row.get("logicalName") for row in variant_groups} != expected_variant_names:
        raise ValueError("known profile: loose DDS source-variant names changed")
    for row in variant_groups:
        candidates = row.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 2:
            raise ValueError("known profile: loose DDS source-variant shape changed")
        by_code = {candidate.get("sourceFormatCode"): candidate for candidate in candidates}
        if set(by_code) != {2, 5}:
            raise ValueError("known profile: loose DDS source-variant codes changed")
        if by_code[2].get("sourceFormatName") != "A4R4G4B4":
            raise ValueError("known profile: CTEX code-2 source suffix changed")
        if by_code[5].get("sourceFormatName") != "R5G6B5":
            raise ValueError("known profile: CTEX code-5 source suffix changed")
        expected_code2_storage = (
            "DXT1"
            if row.get("logicalName") == "particle\\muspell bullet.tga"
            else "DXT2"
        )
        if by_code[2].get("storageFormat") != expected_code2_storage:
            raise ValueError("known profile: code-2 selected DDS storage changed")
        if by_code[5].get("storageFormat") != "DXT1":
            raise ValueError("known profile: code-5 selected DDS storage changed")
    if sorted(metrics["skyCubePcDxt1ToXboxCode3Resources"]) != [
        "331",
        "332",
        "710",
        "741",
        "742",
    ]:
        raise ValueError("known profile: uncompressed sky resource set changed")


def write_tsv(
    secured: SecuredOutputRoot,
    path: Path,
    rows: list[dict[str, object]],
) -> None:
    if not rows:
        raise ValueError("refusing to write an empty census table")
    fields = list(rows[0])
    if any(list(row) != fields for row in rows):
        raise ValueError("census table row shape changed")
    with secured.atomic_text_writer(path) as stream:
        writer = csv.DictWriter(
            stream, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(
    *,
    output_root: Path,
    prefix: str,
    summary: dict[str, object],
    occurrence_rows: list[dict[str, object]],
    frame_rows: list[dict[str, object]],
    mip_rows: list[dict[str, object]],
    variant_rows: list[dict[str, object]],
    protected_sources: tuple[Path, ...],
) -> list[Path]:
    paths = [
        output_root / f"{prefix}-summary.json",
        output_root / f"{prefix}-occurrences.tsv",
        output_root / f"{prefix}-frames.tsv",
        output_root / f"{prefix}-mips.tsv",
        output_root / f"{prefix}-variants.tsv",
    ]
    with SecuredOutputRoot(output_root, protected_sources=protected_sources) as secured:
        secured.atomic_write_text(
            paths[0], json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        write_tsv(secured, paths[1], occurrence_rows)
        write_tsv(secured, paths[2], frame_rows)
        write_tsv(secured, paths[3], mip_rows)
        write_tsv(secured, paths[4], variant_rows)
    return paths


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pc-resource-root", required=True, type=Path)
    parser.add_argument("--xbox-zip", required=True, type=Path)
    parser.add_argument("--pair-geometry", required=True, type=Path)
    parser.add_argument("--resource-accumulator-source", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--proof-profile", choices=(KNOWN_PROFILE,))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.prefix or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-"
        for character in args.prefix
    ):
        raise ValueError("prefix must contain only lowercase ASCII letters, digits, and hyphens")
    pc_resource_root = args.pc_resource_root.resolve(strict=True)
    xbox_zip = args.xbox_zip.resolve(strict=True)
    geometry_path = args.pair_geometry.resolve(strict=True)
    source_file = args.resource_accumulator_source.resolve(strict=True)
    output_root = args.output_root.resolve()

    pairs, geometry = read_geometry_pairs(geometry_path)
    selected_names = frozenset(pair.logical_name for pair in pairs)
    dds_frames, dds_summary = scan_dds_shelves(pc_resource_root, selected_names)
    (
        metrics,
        occurrence_rows,
        frame_rows,
        mip_rows,
        variant_rows,
        resource_rows,
    ) = process_corpus(
        pc_resource_root=pc_resource_root,
        xbox_zip=xbox_zip,
        pairs=pairs,
        dds_frames=dds_frames,
    )
    pc_resource_count = len(list(pc_resource_root.glob("*_res_PC.aya")))
    source_sha256 = sha256_file(source_file)
    xbox_sha256 = sha256_file(xbox_zip)
    if args.proof_profile == KNOWN_PROFILE:
        validate_known_profile(
            geometry=geometry,
            xbox_zip=xbox_zip,
            source_file=source_file,
            pc_resource_count=pc_resource_count,
            dds_summary=dds_summary,
            metrics=metrics,
        )

    selected_mustbe = sorted(
        name
        for name in selected_names
        if any(key[0] == name for key in dds_frames)
        and name in KNOWN_MUSTBE_NAMES
    )
    summary = {
        "schemaVersion": SCHEMA,
        "proofProfile": args.proof_profile,
        "sources": {
            "pairGeometry": geometry,
            "pc": {
                "resourceArchiveCount": pc_resource_count,
                "ddsShelves": dds_summary,
                "selectedMustbeNames": selected_mustbe,
            },
            "xbox": {
                "zipLength": xbox_zip.stat().st_size,
                "zipSha256": xbox_sha256,
            },
            "resourceAccumulator": {
                "sha256": source_sha256,
                "mipBudgetLines": "389-470",
                "kempyNameLines": "208-228",
                "kempyBudgetLines": "472-496",
            },
        },
        "metrics": metrics,
        "resources": resource_rows,
    }
    paths = write_outputs(
        output_root=output_root,
        prefix=args.prefix,
        summary=summary,
        occurrence_rows=occurrence_rows,
        frame_rows=frame_rows,
        mip_rows=mip_rows,
        variant_rows=variant_rows,
        protected_sources=(
            pc_resource_root,
            xbox_zip,
            geometry_path,
            source_file,
        ),
    )
    for path in paths:
        print(f"READY {path.name} {path.stat().st_size} {sha256_file(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
