#!/usr/bin/env python3
"""Build a formal residual-terminal evidence pack (padding pure-pad cohort).

Does **not** mutate Generation 10. Produces hash-bound per-row PE proof and
proposed campaign field updates for a future residual-terminal generation.

Gate reminder (from Gen10 re_campaign padding_valid):
  classification=PADDING, classificationVerdict=FORMAL_STATIC_PROOF_SURVIVED,
  terminalState=campaignState=TERMINAL_PADDING, empty questionIds, contract
  TERMINAL_PADDING + refuter SURVIVED. Byte purity alone is insufficient.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)


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
    rva = va - image_base
    for sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            delta = rva - sva
            if delta >= rawsize:
                return None
            return rawptr + delta
    return None


def span_bytes(
    data: bytes,
    start: int,
    end: int,
    image_base: int,
    sections: list[tuple[int, int, int, int]],
) -> bytes | None:
    """Read [start, end) PE bytes. end is exclusive."""
    if end <= start:
        return None
    o0 = va_to_off(start, image_base, sections)
    if o0 is None:
        return None
    n = end - start
    # ensure last byte maps
    if va_to_off(end - 1, image_base, sections) is None:
        return None
    blob = data[o0 : o0 + n]
    if len(blob) != n:
        return None
    return blob


def kind_of(blob: bytes) -> str | None:
    if not blob:
        return None
    if all(b == 0x90 for b in blob):
        return "NOP_PADDING"
    if all(b == 0xCC for b in blob):
        return "INT3_PADDING"
    if all(b == 0x00 for b in blob):
        return "ZERO_PADDING"
    return None


def build_pack(specimen: Path, terminal_tsv: Path, campaign_residuals: Path) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    image_base, sections = pe_sections(data)

    # campaign residual index
    lines = campaign_residuals.read_text(encoding="utf-8").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
    cols = lines[header_i].split("\t")
    by_start: dict[str, dict[str, str]] = {}
    for line in lines[header_i + 1 :]:
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        row = {cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))}
        by_start[row["startVa"].lower()] = row

    cand = list(csv.DictReader(terminal_tsv.open(encoding="utf-8"), delimiter="\t"))
    proofs = []
    mismatches = 0
    for c in cand:
        start = int(c["startVa"], 16)
        end = int(c["endVa"], 16)
        blob = span_bytes(data, start, end, image_base, sections)
        if blob is None:
            mismatches += 1
            continue
        kind = kind_of(blob)
        if kind is None or kind != c.get("kind"):
            mismatches += 1
            continue
        camp = by_start.get(c["startVa"].lower(), {})
        proofs.append(
            {
                "startVa": c["startVa"],
                "endVa": c["endVa"],
                "bytes": len(blob),
                "kind": kind,
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "entityKey": camp.get("entityKey", ""),
                "questionIds": camp.get("questionIds", ""),
                "campaignState": camp.get("campaignState", ""),
                "classificationVerdict": camp.get("classificationVerdict", ""),
                "proposed": {
                    "classification": "PADDING",
                    "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
                    "terminalState": "TERMINAL_PADDING",
                    "campaignState": "TERMINAL_PADDING",
                    "bytePattern": "PADDING_LIKE_BYTES",
                    "cheapestFalsifier": (
                        "Any non-matching pad byte, instruction/function membership, "
                        "or inbound reference into the span"
                    ),
                    "requiresQuestionSupersession": bool(
                        (camp.get("questionIds") or "").strip()
                    ),
                },
            }
        )

    needs_q = sum(1 for p in proofs if p["proposed"]["requiresQuestionSupersession"])
    pack = {
        "schema": "bea.re.residual-terminal-formal-pack.v1",
        "status": "READY_FOR_GENERATION" if mismatches == 0 and proofs else "BLOCKED",
        "specimen_sha256": sha,
        "n_proofs": len(proofs),
        "n_mismatches": mismatches,
        "n_require_question_supersession": needs_q,
        "n_already_clean": len(proofs) - needs_q,
        "advance_kind_proposed": "RESIDUAL_TERMINAL_PADDING_BULK.v1",
        "parent_generation": 10,
        "non_claims": [
            "Does not mutate Gen10",
            "Does not close questions without an explicit supersession ledger",
            "Does not invent function names",
            "Admitting without question supersession is laundering (refuted by DeepSeek adversarial)",
        ],
        "proofs": proofs,
    }
    return pack


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--terminal-tsv", type=Path, required=True)
    p.add_argument("--campaign-residuals", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)
    pack = build_pack(args.specimen, args.terminal_tsv, args.campaign_residuals)
    # write full pack and a summary without proofs
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(pack) + "\n", encoding="utf-8")
    summary = {k: v for k, v in pack.items() if k != "proofs"}
    summary_path = args.json_out.with_name("SUMMARY.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("RESIDUAL_TERMINAL_FORMAL_PACK_" + pack["status"])
    return 0 if pack["status"] == "READY_FOR_GENERATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
