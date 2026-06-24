#!/usr/bin/env python3
"""
Inventory Battle Engine Aquila packed resource archives (*.aya).

This tool targets the higher-level chunker archives in `data/resources`,
not the lower-level raw mesh payloads under `data/resources/meshes`.

AYA resource archives are chunked-zlib files:

    [u32 compressed_part_size][zlib blob][u32 size][zlib blob]...

After inflation, the payload is a tagged chunk stream:

    [4-byte ASCII tag][u32 chunk_size][chunk_data]...

Examples:
    python tools/aya_archive_inventory.py game/data/resources/852_res_PC.aya
    python tools/aya_archive_inventory.py game/data/resources --glob "*_res_PC.aya"
    python tools/aya_archive_inventory.py game/data/resources/852_res_PC.aya --show-chunks 6
    python tools/aya_archive_inventory.py game/data/resources/852_res_PC.aya --dump-tag TEXT --dump-tag MESH --dump-dir subagents/aya_dump
    python tools/aya_archive_inventory.py game/data/resources/852_res_PC.aya --dump-index 255 --carve-from-tag CMSH --dump-dir subagents/aya_dump
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


COMMON_TAG_SCAN = (
    "AYAD",
    "CMSH",
    "CMST",
    "CMSP",
    "CTEX",
    "DXTX",
    "GDAT",
    "IBUF",
    "MESP",
    "MMPT",
    "MSHT",
    "MESH",
    "PMSH",
    "PMS2",
    "TEXB",
    "TFRM",
    "TXTR",
    "VBUF",
)

EMBEDDED_TAG_PRIORITY = (
    "CMSH",
    "DXTX",
    "GDAT",
    "PMS2",
)

@dataclass(frozen=True)
class ChunkEntry:
    index: int
    tag: str
    size: int
    offset: int


@dataclass(frozen=True)
class ArchiveSummary:
    path: str
    compressed_size: int
    compressed_sha256: str
    raw_size: int
    raw_sha256: str
    chunk_count: int
    unique_tag_count: int
    tag_counts: dict[str, int]
    first_tags: list[str]


@dataclass(frozen=True)
class AssetResolver:
    resource_root: str
    texture_index: dict[str, list[str]]
    mesh_index: dict[str, list[str]]


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def _decode_tag(tag_bytes: bytes) -> str:
    return "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in tag_bytes)


def _ascii_preview(data: bytes, limit: int) -> str:
    return "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in data[:limit])


def _hex_preview(data: bytes, limit: int) -> str:
    return data[:limit].hex()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in value)


def _normalize_asset_ref(value: str) -> str:
    return value.lstrip("?").replace("/", "\\").strip().lower()


def _texture_refs_from_loose_name(file_name: str) -> set[str]:
    lower = file_name.lower()
    base: str | None = None
    if ".tga" in lower:
        base = lower[: lower.index(".tga") + 4]
    elif ".t" in lower:
        base = f"{lower[: lower.index('.t') + 2]}ga"
    if base is None:
        return set()

    candidates = {base}
    if base.startswith("mustbe_"):
        candidates.add(base[len("mustbe_") :])

    refs: set[str] = set()
    for candidate in candidates:
        refs.add(candidate.replace("%", "\\"))
    return refs


def build_asset_resolver(resource_root: Path) -> AssetResolver:
    texture_index: dict[str, list[str]] = {}
    mesh_index: dict[str, list[str]] = {}

    for texture_dir_name in ("dxtntextures", "textures"):
        texture_root = resource_root / texture_dir_name
        if not texture_root.exists():
            continue
        for path in sorted(texture_root.glob("*.aya")):
            refs = _texture_refs_from_loose_name(path.name)
            for ref in refs:
                texture_index.setdefault(ref, []).append(str(path))

    mesh_root = resource_root / "meshes"
    if mesh_root.exists():
        for path in sorted(mesh_root.glob("*.aya")):
            name = path.name.lower()
            if not name.endswith(".aya"):
                continue
            stem = name[:-4]
            aliases = {stem}
            if stem.startswith("m_"):
                aliases.add(stem[2:])
            for alias in aliases:
                mesh_index.setdefault(alias, []).append(str(path))

    return AssetResolver(
        resource_root=str(resource_root),
        texture_index=texture_index,
        mesh_index=mesh_index,
    )


def _all_offsets(data: bytes, marker: bytes) -> list[int]:
    out: list[int] = []
    start = 0

    while True:
        pos = data.find(marker, start)
        if pos < 0:
            return out
        out.append(pos)
        start = pos + 1


def _find_pmsh_wrapper_offsets(payload: bytes) -> list[int]:
    offsets: list[int] = []
    for pos in _all_offsets(payload, b"PMSH"):
        if payload[pos + 8 : pos + 12] == b"PMS2":
            offsets.append(pos)
    return offsets


def _payload_bytes(raw: bytes, chunk: ChunkEntry, *, base_offset: int = 0) -> bytes:
    payload_off = (chunk.offset - base_offset) + 8
    return raw[payload_off : payload_off + chunk.size]


def _inner_tag(payload: bytes) -> str | None:
    if len(payload) < 4 or not all(0x20 <= b < 0x7F for b in payload[:4]):
        return None
    return _decode_tag(payload[:4])


def _extract_c_strings(payload: bytes, *, min_len: int = 4, limit: int = 4) -> list[str]:
    out: list[str] = []
    current = bytearray()

    for b in payload:
        if 0x20 <= b < 0x7F:
            current.append(b)
            continue

        if b == 0 and len(current) >= min_len:
            out.append(current.decode("ascii", errors="replace"))
            if len(out) >= limit:
                return out

        current.clear()

    if len(current) >= min_len and len(out) < limit:
        out.append(current.decode("ascii", errors="replace"))

    return out


def _scan_name_hints(payload: bytes, *, limit: int = 6) -> list[str]:
    hints: list[str] = []
    current = bytearray()

    for b in payload:
        if 0x20 <= b < 0x7F:
            current.append(b)
            continue

        if b == 0 and len(current) >= 4:
            candidate = current.decode("ascii", errors="replace")
            if "\\" in candidate or "/" in candidate or "." in candidate:
                hints.append(candidate)
                if len(hints) >= limit:
                    return hints

        current.clear()

    if len(current) >= 4 and len(hints) < limit:
        candidate = current.decode("ascii", errors="replace")
        if "\\" in candidate or "/" in candidate or "." in candidate:
            hints.append(candidate)

    return hints[:limit]


def _find_tag_offsets(payload: bytes, tags: Iterable[str] = COMMON_TAG_SCAN) -> dict[str, int]:
    offsets: dict[str, int] = {}
    for tag in tags:
        pos = payload.find(tag.encode("ascii"))
        if pos >= 0:
            offsets[tag] = pos
    return offsets


def _scan_asset_refs(payload: bytes) -> tuple[list[str], list[str]]:
    hints = [_normalize_asset_ref(h) for h in _scan_name_hints(payload, limit=64)]
    texture_refs = sorted({h for h in hints if h.endswith(".tga")})
    mesh_refs = sorted({h for h in hints if h.endswith(".msh")})
    return texture_refs, mesh_refs


def _resolve_asset_refs(
    resolver: AssetResolver | None,
    *,
    texture_refs: list[str],
    mesh_refs: list[str],
) -> dict[str, object] | None:
    if resolver is None:
        return None

    texture_matches = [{"ref": ref, "matches": resolver.texture_index.get(ref, [])} for ref in texture_refs]
    mesh_matches = [{"ref": ref, "matches": resolver.mesh_index.get(ref, [])} for ref in mesh_refs]
    return {
        "texture_refs_resolved": sum(1 for item in texture_matches if item["matches"]),
        "mesh_refs_resolved": sum(1 for item in mesh_matches if item["matches"]),
        "texture_matches": texture_matches,
        "mesh_matches": mesh_matches,
    }


def _classify_gdie(texture_refs: list[str], mesh_refs: list[str]) -> str:
    if texture_refs and mesh_refs:
        return "texture_mesh"
    if texture_refs:
        return "texture_only"
    if mesh_refs:
        return "mesh_only"
    return "metadata_only"


def _read_fixed_c_string(data: bytes, off: int, length: int) -> str:
    return data[off : off + length].split(b"\0", 1)[0].decode("ascii", errors="replace")


def _probe_importer_mesh_body(body: bytes) -> dict[str, object]:
    probe: dict[str, object] = {
        "plausible": False,
        "cmst_offset": body.find(b"CMST"),
        "mesp_offset": body.find(b"MESP"),
    }

    try:
        if len(body) < 380:
            raise ValueError(f"body too short: {len(body)} bytes")
        if body[:4] != b"CMSH":
            raise ValueError(f"body does not start with CMSH (got {body[:4]!r})")

        num_textures = _u32(body, 12)
        mesh_name = _read_fixed_c_string(body, 44, 300)
        num_parts = _u32(body, 356)
        cmst_tag = body[380:384]
        if cmst_tag != b"CMST":
            raise ValueError(f"expected CMST at 0x17C, got {cmst_tag!r}")

        index = 388 + num_textures * 36
        texture_names: list[str] = []
        for texture_index in range(num_textures):
            if body[index : index + 4] != b"MSHT":
                raise ValueError(f"texture {texture_index}: expected MSHT at 0x{index:X}")
            index += 8
            if body[index : index + 4] != b"TEXB":
                raise ValueError(f"texture {texture_index}: expected TEXB at 0x{index:X}")
            index += 8
            index += 20
            texture_names.append(_read_fixed_c_string(body, index, 128))
            index += 128

        first_part_tag = body[index : index + 4]
        if num_parts > 0 and first_part_tag != b"MESP":
            raise ValueError(f"expected MESP at 0x{index:X}, got {first_part_tag!r}")

        probe.update(
            {
                "plausible": True,
                "num_textures": num_textures,
                "mesh_name": mesh_name,
                "num_parts": num_parts,
                "first_texture_names": texture_names[:4],
                "first_part_offset": index,
            }
        )
    except Exception as exc:
        probe["error"] = str(exc)

    return probe


def _extract_embedded_mesh_bodies(payload: bytes, *, preview_bytes: int) -> list[tuple[bytes, dict[str, object]]]:
    wrapper_offsets = _find_pmsh_wrapper_offsets(payload)
    cmsh_offsets = _all_offsets(payload, b"CMSH")
    bodies: list[tuple[bytes, dict[str, object]]] = []

    if not cmsh_offsets:
        return bodies

    for body_index, cmsh_offset in enumerate(cmsh_offsets):
        next_wrapper = next((offset for offset in wrapper_offsets if offset > cmsh_offset), len(payload))
        wrapper_start = max((offset for offset in wrapper_offsets if offset < cmsh_offset), default=None)
        body = payload[cmsh_offset:next_wrapper]
        record: dict[str, object] = {
            "body_index": body_index,
            "cmsh_offset": cmsh_offset,
            "end_offset": next_wrapper,
            "length": len(body),
            "sha256": _sha256_hex(body),
            "preview_hex": _hex_preview(body, preview_bytes),
            "preview_ascii": _ascii_preview(body, preview_bytes),
            "wrapper_start_offset": wrapper_start,
            "body_boundary_rule": "CMSH_to_next_sibling_PMSH_or_EOF",
            "importer_probe": _probe_importer_mesh_body(body),
        }
        bodies.append((body, record))

    return bodies


def inflate_aya(path: Path) -> bytes:
    data = path.read_bytes()
    out = bytearray()
    index = 0

    while index < len(data):
        if index + 4 > len(data):
            raise ValueError(f"{path}: truncated 4-byte compressed-part header at 0x{index:X}")

        size = _u32(data, index)
        index += 4
        end = index + size

        if end > len(data):
            raise ValueError(
                f"{path}: compressed-part header overruns file (part size 0x{size:X}, index 0x{index:X}, len 0x{len(data):X})"
            )

        out.extend(zlib.decompress(data[index:end]))
        index = end

    return bytes(out)


def parse_chunk_stream(raw: bytes, *, base_offset: int = 0) -> list[ChunkEntry]:
    chunks: list[ChunkEntry] = []
    index = 0
    chunk_index = 0

    while index < len(raw):
        if index + 8 > len(raw):
            raise ValueError(f"truncated chunk header at raw offset 0x{base_offset + index:X}")

        tag = _decode_tag(raw[index : index + 4])
        size = _u32(raw, index + 4)
        payload_off = index + 8
        end = payload_off + size

        if end > len(raw):
            raise ValueError(
                f"chunk {chunk_index} ({tag}) overruns payload "
                f"(payload_off 0x{base_offset + payload_off:X}, size 0x{size:X}, raw_len 0x{len(raw):X})"
            )

        chunks.append(ChunkEntry(index=chunk_index, tag=tag, size=size, offset=base_offset + index))
        chunk_index += 1
        index = end

    return chunks


def parse_top_level_chunks(raw: bytes) -> list[ChunkEntry]:
    return parse_chunk_stream(raw)


def _nested_chunk_tree(payload: bytes, *, base_offset: int = 0, depth: int = 4, max_children: int = 24) -> list[dict[str, object]]:
    if depth <= 0:
        return []

    try:
        chunks = parse_chunk_stream(payload, base_offset=base_offset)
    except Exception:
        return []

    out: list[dict[str, object]] = []
    for chunk in chunks[:max_children]:
        child_payload = _payload_bytes(payload, chunk, base_offset=base_offset)
        item: dict[str, object] = {
            "index": chunk.index,
            "tag": chunk.tag,
            "size": chunk.size,
            "offset": chunk.offset,
            "payload_offset": chunk.offset + 8,
            "preview_ascii": _ascii_preview(child_payload, 24),
            "name_hints": _scan_name_hints(child_payload, limit=4),
        }
        if depth > 1:
            children = _nested_chunk_tree(
                child_payload,
                base_offset=chunk.offset + 8,
                depth=depth - 1,
                max_children=max_children,
            )
            if children:
                item["children"] = children
        out.append(item)

    return out


def _embedded_chunk_tree(payload: bytes, *, base_offset: int = 0, depth: int = 4, max_children: int = 24) -> dict[str, object] | None:
    tag_offsets = _find_tag_offsets(payload)
    ranked_offsets = sorted(
        ((tag, pos) for tag, pos in tag_offsets.items() if pos > 0),
        key=lambda item: (
            EMBEDDED_TAG_PRIORITY.index(item[0]) if item[0] in EMBEDDED_TAG_PRIORITY else len(EMBEDDED_TAG_PRIORITY),
            item[1],
            item[0],
        ),
    )

    for tag, pos in ranked_offsets:
        candidate = payload[pos:]
        try:
            chunks = parse_chunk_stream(candidate, base_offset=base_offset + pos)
        except Exception:
            continue

        if not chunks:
            continue

        return {
            "start_tag": tag,
            "stream_offset": base_offset + pos,
            "chunks": _nested_chunk_tree(
                candidate,
                base_offset=base_offset + pos,
                depth=depth,
                max_children=max_children,
            ),
        }

    return None


def _chunk_record(
    raw: bytes,
    chunk: ChunkEntry,
    *,
    preview_bytes: int,
    include_nested: bool = False,
    resolver: AssetResolver | None = None,
) -> dict[str, object]:
    payload = _payload_bytes(raw, chunk)
    texture_refs, mesh_refs = _scan_asset_refs(payload)
    record: dict[str, object] = {
        "index": chunk.index,
        "tag": chunk.tag,
        "size": chunk.size,
        "offset": chunk.offset,
        "payload_offset": chunk.offset + 8,
        "end_offset": chunk.offset + 8 + chunk.size,
        "sha256": _sha256_hex(payload),
        "inner_tag": _inner_tag(payload),
        "preview_hex": _hex_preview(payload, preview_bytes),
        "preview_ascii": _ascii_preview(payload, preview_bytes),
        "c_strings": _extract_c_strings(payload),
        "name_hints": _scan_name_hints(payload),
        "tag_offsets": _find_tag_offsets(payload),
        "texture_refs": texture_refs,
        "mesh_refs": mesh_refs,
    }
    resolution = _resolve_asset_refs(resolver, texture_refs=texture_refs, mesh_refs=mesh_refs)
    if resolution is not None and (texture_refs or mesh_refs):
        record["resolution"] = resolution
    if chunk.tag == "GDIE":
        record["gdie_family"] = _classify_gdie(texture_refs, mesh_refs)
    if include_nested:
        nested = _nested_chunk_tree(payload, base_offset=chunk.offset + 8)
        if nested:
            record["nested_chunks"] = nested
        embedded = _embedded_chunk_tree(payload, base_offset=chunk.offset + 8)
        if embedded:
            record["embedded_chunks"] = embedded
    return record


def summarize_archive(path: Path) -> tuple[ArchiveSummary, bytes, list[ChunkEntry]]:
    compressed = path.read_bytes()
    raw = inflate_aya(path)
    chunks = parse_top_level_chunks(raw)
    counts = Counter(chunk.tag for chunk in chunks)

    summary = ArchiveSummary(
        path=str(path),
        compressed_size=len(compressed),
        compressed_sha256=_sha256_hex(compressed),
        raw_size=len(raw),
        raw_sha256=_sha256_hex(raw),
        chunk_count=len(chunks),
        unique_tag_count=len(counts),
        tag_counts=dict(sorted(counts.items())),
        first_tags=[chunk.tag for chunk in chunks[:12]],
    )
    return summary, raw, chunks


def iter_archive_paths(inputs: Iterable[Path], glob_pattern: str) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_file():
            out.append(item)
            continue
        if item.is_dir():
            out.extend(sorted(p for p in item.glob(glob_pattern) if p.is_file()))
            continue
        raise FileNotFoundError(str(item))
    return sorted(dict.fromkeys(out))


def print_summary(summary: ArchiveSummary) -> None:
    counts = ", ".join(f"{tag}:{count}" for tag, count in sorted(summary.tag_counts.items()))
    first_tags = ", ".join(summary.first_tags)
    print(f"{summary.path}")
    print(f"  compressed_size: {summary.compressed_size}")
    print(f"  raw_size       : {summary.raw_size}")
    print(f"  chunk_count    : {summary.chunk_count}")
    print(f"  unique_tags    : {summary.unique_tag_count}")
    print(f"  first_tags     : {first_tags}")
    print(f"  tag_counts     : {counts}")


def print_chunk_table(raw: bytes, chunks: list[ChunkEntry], limit: int, *, preview_bytes: int) -> None:
    print("  chunks:")
    for chunk in chunks[:limit]:
        record = _chunk_record(raw, chunk, preview_bytes=preview_bytes)
        inner = f" inner={record['inner_tag']}" if record["inner_tag"] else ""
        preview = record["preview_ascii"]
        print(
            f"    [{chunk.index:03d}] tag={chunk.tag} size=0x{chunk.size:X} ({chunk.size}) "
            f"raw_off=0x{chunk.offset:X}{inner} preview={preview}"
        )


def _select_chunks(
    chunks: list[ChunkEntry],
    *,
    dump_tags: set[str],
    dump_indices: set[int],
    dump_limit_per_tag: int,
) -> list[ChunkEntry]:
    selected: list[ChunkEntry] = []
    selected_indices: set[int] = set()
    per_tag_counts: Counter[str] = Counter()

    for chunk in chunks:
        by_index = chunk.index in dump_indices
        by_tag = chunk.tag in dump_tags and (dump_limit_per_tag <= 0 or per_tag_counts[chunk.tag] < dump_limit_per_tag)

        if not by_index and not by_tag:
            continue

        if chunk.index in selected_indices:
            continue

        selected.append(chunk)
        selected_indices.add(chunk.index)

        if chunk.tag in dump_tags:
            per_tag_counts[chunk.tag] += 1

    return selected


def dump_selected_chunks(
    archive_path: Path,
    raw: bytes,
    chunks: list[ChunkEntry],
    *,
    dump_dir: Path,
    dump_tags: set[str],
    dump_indices: set[int],
    dump_limit_per_tag: int,
    dump_with_header: bool,
    carve_tags: set[str],
    extract_embedded_mesh_bodies: bool,
    resolver: AssetResolver | None,
    preview_bytes: int,
) -> list[dict[str, object]]:
    selected = _select_chunks(
        chunks,
        dump_tags=dump_tags,
        dump_indices=dump_indices,
        dump_limit_per_tag=dump_limit_per_tag,
    )

    dumped: list[dict[str, object]] = []
    archive_dir = dump_dir / _safe_name(archive_path.stem)
    archive_dir.mkdir(parents=True, exist_ok=True)

    for chunk in selected:
        payload = _payload_bytes(raw, chunk)
        if dump_with_header:
            blob = raw[chunk.offset : chunk.offset + 8 + chunk.size]
            suffix = "with_header"
        else:
            blob = payload
            suffix = "payload"

        file_stem = f"{chunk.index:03d}_{_safe_name(chunk.tag)}_{suffix}"
        blob_path = archive_dir / f"{file_stem}.bin"
        meta_path = archive_dir / f"{file_stem}.json"
        blob_path.write_bytes(blob)

        record = _chunk_record(
            raw,
            chunk,
            preview_bytes=preview_bytes,
            include_nested=True,
            resolver=resolver,
        )
        record["dump_path"] = str(blob_path)
        record["metadata_path"] = str(meta_path)
        record["bytes_written"] = len(blob)
        record["includes_header"] = dump_with_header

        carved_streams: list[dict[str, object]] = []
        for carve_tag in sorted(carve_tags):
            marker = carve_tag.encode("ascii")
            carve_off = payload.find(marker)
            if carve_off < 0:
                continue

            carve_blob = payload[carve_off:]
            carve_stem = f"{file_stem}_carve_{_safe_name(carve_tag)}"
            carve_path = archive_dir / f"{carve_stem}.bin"
            carve_path.write_bytes(carve_blob)
            carved_streams.append(
                {
                    "tag": carve_tag,
                    "offset": carve_off,
                    "length": len(carve_blob),
                    "sha256": _sha256_hex(carve_blob),
                    "dump_path": str(carve_path),
                    "preview_hex": _hex_preview(carve_blob, preview_bytes),
                    "preview_ascii": _ascii_preview(carve_blob, preview_bytes),
                }
            )

        if carved_streams:
            record["carved_streams"] = carved_streams

        if extract_embedded_mesh_bodies and chunk.tag == "MESH":
            embedded_bodies = _extract_embedded_mesh_bodies(payload, preview_bytes=preview_bytes)
            if embedded_bodies:
                body_records: list[dict[str, object]] = []
                for body, body_record in embedded_bodies:
                    body_stem = f"{file_stem}_embedded_body{body_record['body_index']:02d}_CMSH"
                    body_path = archive_dir / f"{body_stem}.bin"
                    body_path.write_bytes(body)
                    body_record["dump_path"] = str(body_path)
                    body_records.append(body_record)

                record["embedded_mesh_bodies"] = body_records

        meta_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        dumped.append(record)

    return dumped


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        default=[Path("game/data/resources")],
        help="AYA files and/or directories to scan (default: game/data/resources)",
    )
    ap.add_argument(
        "--glob",
        default="*_res_PC.aya",
        help="Glob when an input is a directory (default: *_res_PC.aya)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of archives to process after collection (0 = no limit)",
    )
    ap.add_argument(
        "--show-chunks",
        type=int,
        default=0,
        help="Show the first N top-level chunks for each archive",
    )
    ap.add_argument(
        "--preview-bytes",
        type=int,
        default=24,
        help="Byte count for ASCII/hex previews in detailed chunk output and metadata (default: 24)",
    )
    ap.add_argument(
        "--resource-root",
        type=Path,
        default=Path("game/data/resources"),
        help="Resource root used for loose mesh/texture resolution (default: game/data/resources)",
    )
    ap.add_argument(
        "--resolve-assets",
        action="store_true",
        help="Resolve packed texture/mesh references against loose payload files under --resource-root",
    )
    ap.add_argument(
        "--json-include-chunks",
        action="store_true",
        help="Include full top-level chunk metadata in JSON output",
    )
    ap.add_argument(
        "--dump-dir",
        type=Path,
        help="Optional root directory where selected chunk payloads will be dumped",
    )
    ap.add_argument(
        "--dump-tag",
        action="append",
        default=[],
        help="Top-level tag to dump (repeatable, e.g. --dump-tag TEXT --dump-tag MESH)",
    )
    ap.add_argument(
        "--dump-index",
        type=int,
        action="append",
        default=[],
        help="Specific top-level chunk index to dump (repeatable)",
    )
    ap.add_argument(
        "--dump-limit-per-tag",
        type=int,
        default=0,
        help="Max chunks to dump per requested tag per archive (0 = no limit)",
    )
    ap.add_argument(
        "--dump-with-header",
        action="store_true",
        help="Dump selected chunks with the outer 8-byte tag/size header instead of payload-only bytes",
    )
    ap.add_argument(
        "--carve-from-tag",
        action="append",
        default=[],
        help="Within each dumped payload, also dump bytes from the first occurrence of this inner tag to EOF (repeatable, e.g. --carve-from-tag CMSH)",
    )
    ap.add_argument(
        "--extract-embedded-mesh-bodies",
        action="store_true",
        help="For selected top-level MESH payloads, emit bounded embedded CMSH bodies using the current composite-wrapper rule (CMSH -> next sibling PMSH or EOF)",
    )
    ap.add_argument(
        "--json-out",
        type=Path,
        help="Optional JSON output path for machine-readable summaries",
    )
    ap.add_argument(
        "--asset-manifest-out",
        type=Path,
        help="Optional JSON output path for an aggregate packed-ref resolution manifest and GDIE family table",
    )
    return ap.parse_args(argv)


def _append_ref_counts(counter: Counter[str], refs: list[str]) -> None:
    for ref in refs:
        counter[ref] += 1


def build_asset_manifest(
    archives: list[tuple[Path, bytes, list[ChunkEntry]]],
    *,
    resolver: AssetResolver | None,
) -> dict[str, object]:
    text_texture_refs: Counter[str] = Counter()
    reference_mesh_refs: Counter[str] = Counter()
    gdie_texture_refs: Counter[str] = Counter()
    gdie_mesh_refs: Counter[str] = Counter()
    gdie_families: list[dict[str, object]] = []

    for archive_path, raw, chunks in archives:
        for chunk in chunks:
            payload = _payload_bytes(raw, chunk)
            texture_refs, mesh_refs = _scan_asset_refs(payload)
            if chunk.tag == "TEXT":
                _append_ref_counts(text_texture_refs, texture_refs)
            elif chunk.tag == "MESH" and payload.find(b"CMSH") < 0:
                _append_ref_counts(reference_mesh_refs, mesh_refs)
            elif chunk.tag == "GDIE":
                _append_ref_counts(gdie_texture_refs, texture_refs)
                _append_ref_counts(gdie_mesh_refs, mesh_refs)
                family_record = {
                    "archive": str(archive_path),
                    "chunk_index": chunk.index,
                    "family": _classify_gdie(texture_refs, mesh_refs),
                    "texture_refs": texture_refs,
                    "mesh_refs": mesh_refs,
                }
                resolution = _resolve_asset_refs(resolver, texture_refs=texture_refs, mesh_refs=mesh_refs)
                if resolution is not None and (texture_refs or mesh_refs):
                    family_record["resolution"] = resolution
                gdie_families.append(family_record)

    def _emit(counter: Counter[str], index: dict[str, list[str]] | None) -> list[dict[str, object]]:
        out: list[dict[str, object]] = []
        for ref, count in sorted(counter.items()):
            matches = index.get(ref, []) if index is not None else []
            out.append(
                {
                    "ref": ref,
                    "count": count,
                    "match_count": len(matches),
                    "matches": matches,
                }
            )
        return out

    texture_index = resolver.texture_index if resolver is not None else None
    mesh_index = resolver.mesh_index if resolver is not None else None

    text_records = _emit(text_texture_refs, texture_index)
    ref_mesh_records = _emit(reference_mesh_refs, mesh_index)
    gdie_texture_records = _emit(gdie_texture_refs, texture_index)
    gdie_mesh_records = _emit(gdie_mesh_refs, mesh_index)

    return {
        "resource_root": resolver.resource_root if resolver is not None else None,
        "summary": {
            "text_texture_refs": len(text_records),
            "text_texture_refs_resolved": sum(1 for item in text_records if item["match_count"] > 0),
            "reference_mesh_refs": len(ref_mesh_records),
            "reference_mesh_refs_resolved": sum(1 for item in ref_mesh_records if item["match_count"] > 0),
            "gdie_texture_refs": len(gdie_texture_records),
            "gdie_texture_refs_resolved": sum(1 for item in gdie_texture_records if item["match_count"] > 0),
            "gdie_mesh_refs": len(gdie_mesh_records),
            "gdie_mesh_refs_resolved": sum(1 for item in gdie_mesh_records if item["match_count"] > 0),
            "gdie_family_counts": dict(sorted(Counter(item["family"] for item in gdie_families).items())),
        },
        "text_texture_refs": text_records,
        "reference_mesh_refs": ref_mesh_records,
        "gdie_texture_refs": gdie_texture_records,
        "gdie_mesh_refs": gdie_mesh_records,
        "gdie_families": gdie_families,
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    dump_tags = {tag.upper() for tag in args.dump_tag}
    dump_indices = set(args.dump_index)
    carve_tags = {tag.upper() for tag in args.carve_from_tag}
    resolver = build_asset_resolver(args.resource_root) if args.resolve_assets else None

    try:
        paths = iter_archive_paths(args.inputs, args.glob)
    except Exception as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    if args.dump_dir is not None and not dump_tags and not dump_indices:
        print("[ERR] --dump-dir requires at least one --dump-tag or --dump-index selector", file=sys.stderr)
        return 1

    if not paths:
        print("[ERR] no .aya archives matched the requested inputs", file=sys.stderr)
        return 1

    if args.limit > 0:
        paths = paths[: args.limit]

    manifest: list[dict[str, object]] = []
    archive_cache: list[tuple[Path, bytes, list[ChunkEntry]]] = []
    had_error = False

    for path in paths:
        try:
            summary, raw, chunks = summarize_archive(path)
            print_summary(summary)
            if args.show_chunks > 0:
                print_chunk_table(raw, chunks, args.show_chunks, preview_bytes=args.preview_bytes)

            item = asdict(summary)
            if args.json_include_chunks:
                item["chunks"] = [
                    _chunk_record(raw, chunk, preview_bytes=args.preview_bytes, resolver=resolver)
                    for chunk in chunks
                ]
            elif args.show_chunks > 0:
                item["chunks"] = [
                    _chunk_record(raw, chunk, preview_bytes=args.preview_bytes, resolver=resolver)
                    for chunk in chunks[: args.show_chunks]
                ]

            if args.dump_dir is not None:
                dumped = dump_selected_chunks(
                    path,
                    raw,
                    chunks,
                    dump_dir=args.dump_dir,
                    dump_tags=dump_tags,
                    dump_indices=dump_indices,
                    dump_limit_per_tag=args.dump_limit_per_tag,
                    dump_with_header=args.dump_with_header,
                    carve_tags=carve_tags,
                    extract_embedded_mesh_bodies=args.extract_embedded_mesh_bodies,
                    resolver=resolver,
                    preview_bytes=args.preview_bytes,
                )
                if dumped:
                    print(f"  dumped_chunks : {len(dumped)} -> {args.dump_dir / _safe_name(path.stem)}")
                    item["dumped_chunks"] = dumped

            print("")
            manifest.append(item)
            archive_cache.append((path, raw, chunks))
        except Exception as exc:
            had_error = True
            print(f"{path}")
            print(f"  [ERR] {exc}")
            print("")

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"[OK] wrote JSON manifest: {args.json_out}")

    if args.asset_manifest_out is not None:
        asset_manifest = build_asset_manifest(archive_cache, resolver=resolver)
        args.asset_manifest_out.write_text(json.dumps(asset_manifest, indent=2), encoding="utf-8")
        print(f"[OK] wrote asset manifest: {args.asset_manifest_out}")

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
