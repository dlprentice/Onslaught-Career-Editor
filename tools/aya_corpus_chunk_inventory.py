"""Corpus-wide AYA chunk inventory.

Read-only. Walks every ``.aya`` under a retail ``data/resources`` tree, inflates
it, and enumerates every tagged chunk with its total byte volume, occurrence
count, container family, and parent tag.

This answers "what does the retail format contain" independently of what any
extraction path chooses to read. It reports framing and byte volume only and
makes no claim about the semantics of any tag.

Framing rules established empirically against the retail corpus:

* An AYA file is a sequence of ``<u32 compressedLength><zlib member>`` records.
* An inflated payload is a stream of ``<4-byte tag><u32 payloadSize><payload>``
  records. Tag bytes are printable ASCII; ``MAP!`` shows the alphabet is not
  restricted to ``[A-Z]``.
* Some container payloads carry a fixed header before the record stream
  (4 bytes for ``ENGN``/``MAP!``/``SURF``, 8 for ``HFLD``, 24 for ``CSSD``,
  20 for ``SSPT``). The walker recovers those by trying a small set of header
  sizes and accepting the first that consumes the payload exactly.

Usage:
    python ./tools/aya_corpus_chunk_inventory.py --resources <path> --json out.json
"""

from __future__ import annotations

import argparse
import json
import struct
import time
import zlib
from collections import Counter
from pathlib import Path

MAX_SOURCE = 64 * 1024 * 1024
MAX_INFLATED = 256 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_DEPTH = 10
HEADER_CANDIDATES = (0, 4, 8, 20, 24)

# Tags whose payload is bulk data, not a record stream. Treating them as
# containers risks framing noise. Membership is asserted by the mesh-format
# contract in rebuild/tools/aya_battleengine_identity_analyzer.py and by the
# world parsers in rebuild/tools/materialize_retail_assets.py.
OPAQUE_TAGS = frozenset(
    {
        b"VBUF", b"IBUF", b"TEXR", b"CMVB", b"CMSP", b"CMST", b"TEXB",
        b"HORI", b"HPOS", b"HFOV", b"VHFM", b"CHLD", b"PRNT", b"NMIC",
        b"REFR", b"CPOS", b"CORI", b"CEMT", b"PMS2", b"CAMD",
        b"BONE", b"BONW", b"BONS",
        b"DATA", b"PALT", b"MSHD", b"MXRS", b"CTEX", b"TFRM",
        b"RLWD", b"BSWD", b"WDAT", b"OUTL", b"IMPO", b"GDAT", b"DXFT",
        b"FGEN", b"AYAD", b"LVLR", b"TARG", b"LNDS", b"VSDS", b"PMIB",
        b"DMKR", b"CHFD", b"CMTX", b"CMCL", b"SMAP",
    }
)


def _valid_tag(tag: bytes) -> bool:
    return (
        len(tag) == 4
        and 65 <= tag[0] <= 90
        and all(32 <= byte < 127 for byte in tag)
    )


def inflate_aya(source: bytes) -> bytes:
    if len(source) > MAX_SOURCE:
        raise ValueError("source limit")
    out = bytearray()
    pos = 0
    members = 0
    while pos < len(source):
        if members >= MAX_MEMBERS:
            raise ValueError("member limit")
        if len(source) - pos < 4:
            raise ValueError("truncated member header")
        length = struct.unpack_from("<I", source, pos)[0]
        pos += 4
        if length == 0 or length > len(source) - pos:
            raise ValueError("member length")
        member = source[pos : pos + length]
        pos += length
        dec = zlib.decompressobj()
        remaining = MAX_INFLATED - len(out)
        inflated = dec.decompress(member, remaining + 1)
        if len(inflated) > remaining or dec.unconsumed_tail:
            raise ValueError("inflate limit")
        if not dec.eof:
            raise ValueError("incomplete zlib member")
        out.extend(inflated + dec.flush())
        members += 1
    return bytes(out)


def frame_records(data: bytes, start: int) -> list[tuple[bytes, int, int]] | None:
    """Return [(tag, payloadOffset, payloadSize)] when ``data[start:]`` frames exactly."""
    pos = start
    records: list[tuple[bytes, int, int]] = []
    while pos < len(data):
        if pos + 8 > len(data):
            return None
        tag = data[pos : pos + 4]
        if not _valid_tag(tag):
            return None
        size = struct.unpack_from("<I", data, pos + 4)[0]
        end = pos + 8 + size
        if end > len(data) or end < pos + 8:
            return None
        records.append((tag, pos + 8, size))
        pos = end
        if len(records) > 500_000:
            return None
    return records if records else None


def frame_any(data: bytes) -> tuple[int, list[tuple[bytes, int, int]]] | None:
    for header in HEADER_CANDIDATES:
        if header >= len(data):
            continue
        records = frame_records(data, header)
        if records is not None:
            return header, records
    return None


def walk(data: bytes, start: int, family: str, out: dict, depth: int, parent: str) -> None:
    records = frame_records(data, start)
    if records is None:
        return
    for tag, offset, size in records:
        name = tag.decode("ascii", "replace")
        rec = out.setdefault(
            name,
            {
                "count": 0,
                "payloadBytes": 0,
                "leafBytes": 0,
                "families": Counter(),
                "parents": Counter(),
                "children": Counter(),
                "sizes": Counter(),
                "container": False,
                "headerBytes": Counter(),
            },
        )
        rec["count"] += 1
        rec["payloadBytes"] += size
        rec["families"][family] += 1
        rec["parents"][parent] += 1
        if len(rec["sizes"]) < 40:
            rec["sizes"][size] += 1
        payload = data[offset : offset + size]
        framed = None
        if depth < MAX_DEPTH and tag not in OPAQUE_TAGS and size >= 8:
            framed = frame_any(payload)
        if framed is None:
            rec["leafBytes"] += size
        else:
            header, children = framed
            rec["container"] = True
            rec["headerBytes"][header] += 1
            rec["leafBytes"] += header
            for child_tag, _, _ in children:
                rec["children"][child_tag.decode("ascii", "replace")] += 1
            walk(payload, header, family, out, depth + 1, name)


def classify(inflated: bytes) -> tuple[str, int]:
    head = inflated[:4]
    if head == b"DDS ":
        return "DDS", -1
    if head == b"CMSH":
        return "CMSH", 380
    if head == b"LVLR":
        return "LVLR", 0
    return "OTHER:" + head.decode("ascii", "replace"), 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resources", required=True, type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    started = time.perf_counter()
    tags: dict[str, dict] = {}
    families = Counter()
    family_bytes = Counter()
    family_compressed = Counter()
    dds_fourcc = Counter()
    inflate_seconds = 0.0
    total_files = 0

    for path in sorted(args.resources.rglob("*.aya")):
        raw = path.read_bytes()
        t0 = time.perf_counter()
        data = inflate_aya(raw)
        inflate_seconds += time.perf_counter() - t0
        total_files += 1
        family, start = classify(data)
        families[family] += 1
        family_bytes[family] += len(data)
        family_compressed[family] += len(raw)
        if family == "DDS":
            dds_fourcc[data[84:88].decode("ascii", "replace")] += 1
            continue
        if family == "CMSH":
            tags.setdefault(
                "CMSH:header",
                {
                    "count": 0, "payloadBytes": 0, "leafBytes": 0,
                    "families": Counter(), "parents": Counter(), "children": Counter(),
                    "sizes": Counter(), "container": False, "headerBytes": Counter(),
                },
            )
            rec = tags["CMSH:header"]
            rec["count"] += 1
            rec["payloadBytes"] += 380
            rec["leafBytes"] += 380
            rec["families"]["CMSH"] += 1
            rec["parents"]["<file>"] += 1
        walk(data, start, family, tags, 0, "<file>")

    elapsed = time.perf_counter() - started
    report = {
        "files": total_files,
        "elapsedSeconds": round(elapsed, 3),
        "inflateSeconds": round(inflate_seconds, 3),
        "families": dict(families),
        "familyInflatedBytes": dict(family_bytes),
        "familyCompressedBytes": dict(family_compressed),
        "ddsFourCC": dict(dds_fourcc),
        "tags": {
            name: {
                "count": rec["count"],
                "payloadBytes": rec["payloadBytes"],
                "leafBytes": rec["leafBytes"],
                "container": rec["container"],
                "families": dict(rec["families"]),
                "parents": dict(rec["parents"]),
                "children": dict(rec["children"]),
                "headerBytes": dict(rec["headerBytes"]),
                "distinctSizes": len(rec["sizes"]),
                "commonSizes": rec["sizes"].most_common(4),
            }
            for name, rec in sorted(tags.items(), key=lambda kv: -kv[1]["leafBytes"])
        },
    }
    text = json.dumps(report, indent=2)
    if args.json:
        args.json.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
