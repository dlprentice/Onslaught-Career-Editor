#!/usr/bin/env python3
"""Classify Gen10-style DARK PADDING_LIKE residuals from a pristine PE.

Pure uniform 0x90 / 0xCC / 0x00 spans between functions are terminal padding.
Does not mutate campaign ledgers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)


def read_residual_rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
    cols = lines[header_i].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[header_i + 1 :]:
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        rows.append({cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))})
    return rows


def pe_sections(data: bytes) -> tuple[int, list[tuple[int, int, int, int]]]:
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections: list[tuple[int, int, int, int]] = []
    for i in range(num_sections):
        o = sec_off + i * 40
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(
    va: int, image_base: int, sections: list[tuple[int, int, int, int]]
) -> int | None:
    """Map VA to file offset. Refuse RVAs past the section's raw size (no zero-pad alias)."""
    rva = va - image_base
    for sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            delta = rva - sva
            if delta >= rawsize:
                return None
            return rawptr + delta
    return None


def classify_span(
    data: bytes,
    start: int,
    end: int,
    image_base: int,
    sections: list[tuple[int, int, int, int]],
) -> tuple[str, int]:
    o0 = va_to_off(start, image_base, sections)
    o1 = va_to_off(end, image_base, sections)
    if o0 is None or o1 is None or o1 <= o0:
        return "UNMAPPED", 0
    blob = data[o0:o1]
    n = len(blob)
    if n == 0:
        return "EMPTY", 0
    if all(b == 0x90 for b in blob):
        return "NOP_PADDING", n
    if all(b == 0xCC for b in blob):
        return "INT3_PADDING", n
    if all(b == 0x00 for b in blob):
        return "ZERO_PADDING", n
    if all(b in (0x00, 0xCC) for b in blob):
        return "ZERO_OR_INT3_PADDING", n
    if all(b in (0x00, 0x90, 0xCC) for b in blob):
        return "MIXED_ALIGN_BYTES", n
    return "NON_UNIFORM", n


def classify_padding_dark(
    specimen: Path, residuals_tsv: Path
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_sections(data)
    rows = read_residual_rows(residuals_tsv)
    pad = [
        r
        for r in rows
        if r.get("bytePattern") == "PADDING_LIKE_BYTES"
        and r.get("observationState") == "DARK"
    ]
    results = []
    byte_total = 0
    for r in pad:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        kind, n = classify_span(data, start, end, image_base, sections)
        byte_total += n
        results.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r["bytes"],
                "kind": kind,
                "prevFunc": r.get("prevFunc", ""),
                "nextFunc": r.get("nextFunc", ""),
                "questionIds": r.get("questionIds", ""),
            }
        )
    counts = Counter(x["kind"] for x in results)
    terminal = sum(
        1
        for x in results
        if x["kind"] in ("NOP_PADDING", "INT3_PADDING", "ZERO_PADDING")
    )
    return {
        "schema": "bea.re.residual-padding-static-full.v1",
        "status": "PASS" if terminal == len(results) and len(results) > 0 else "PARTIAL",
        "specimen_sha256": sha,
        "n_total_padding_dark": len(results),
        "counts": dict(counts),
        "n_terminal_pure_padding": terminal,
        "bytes_classified": byte_total,
        "rows": results,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--residuals-tsv", type=Path, required=True)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    result = classify_padding_dark(args.specimen, args.residuals_tsv)
    # drop rows for stdout size unless writing file
    summary = {k: v for k, v in result.items() if k != "rows"}
    text = json.dumps(summary, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("RESIDUAL_PADDING_CLASSIFY_" + result["status"])
    return 0 if result["status"] in ("PASS", "PARTIAL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
