#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen16 remaining OPEN_DARK (335) via MSVC align-NOP + inbound xref.

Exports OPEN_DARK from Generation 16, classifies full-span compiler alignment
NOPs (Intel multi-byte NOPs + MSVC lea/hotpatch pads) as residual-row
TERMINAL_PADDING when PE rechecks survive, and freezes an inbound E8/E9/abs
census for the still-open set. Emits a MEASURED plate and optional
READY_FOR_GENERATION formal pack.

Does **not** mutate Gen16/Gen15/Gen10. Does **not** invent function names or
claim CALL entry / REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.open-dark-still-open-inbound.v1"
PACK_SCHEMA = "bea.re.open-dark-still-open-inbound-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_DARK_STILL_OPEN_INBOUND.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 335
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN16 = Path(
    "local-lab/residual-terminal-generation16-code-like-mass-20260805-v1/"
    "generation-16-residual-terminal-code-like-mass"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-dark-still-open-inbound-gen16-20260805-v1")

# Intel SDM multi-byte NOPs + classic MSVC alignment / hotpatch pads.
# Matched longest-first as a pure concatenation covering the residual.
ALIGN_NOP_PATTERNS: tuple[bytes, ...] = tuple(
    sorted(
        {
            bytes.fromhex("90"),
            bytes.fromhex("6690"),
            bytes.fromhex("0f1f00"),
            bytes.fromhex("0f1f4000"),
            bytes.fromhex("0f1f440000"),
            bytes.fromhex("660f1f440000"),
            bytes.fromhex("0f1f8000000000"),
            bytes.fromhex("0f1f840000000000"),
            bytes.fromhex("660f1f840000000000"),
            bytes.fromhex("cc"),
            bytes.fromhex("00"),
            bytes.fromhex("8bff"),  # mov edi,edi
            bytes.fromhex("87c0"),  # xchg eax,eax
            bytes.fromhex("8d4900"),  # lea ecx,[ecx]
            bytes.fromhex("8d5b00"),  # lea ebx,[ebx]
            bytes.fromhex("8d6d00"),  # lea ebp,[ebp]
            bytes.fromhex("8d7600"),  # lea esi,[esi]
            bytes.fromhex("8d7f00"),  # lea edi,[edi]
            bytes.fromhex("8d642400"),  # lea esp,[esp]
            bytes.fromhex("8da42400000000"),  # lea esp,[esp+0]
            bytes.fromhex("8d9b00000000"),  # lea ebx,[ebx+0]
            bytes.fromhex("8db600000000"),  # lea esi,[esi+0]
            bytes.fromhex("8dbf00000000"),  # lea edi,[edi+0]
            bytes.fromhex("8d2d00000000"),
        },
        key=len,
        reverse=True,
    )
)

PAD_KIND = "MSVC_ALIGN_NOP_RUN"
DEFAULT_FALSIFIER = (
    "PE byte change; residual no longer pure known align-NOP concat; "
    "inbound reference proving non-pad semantics; residual membership of a "
    "named function body"
)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stamp(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    }


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def pe_map(data: bytes) -> tuple[int, list[tuple[str, int, int, int, int]]]:
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections: list[tuple[str, int, int, int, int]] = []
    for i in range(num_sections):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(
    va: int, image_base: int, sections: list[tuple[str, int, int, int, int]]
) -> int | None:
    rva = va - image_base
    for _name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            if rva - sva >= rawsize:
                return None
            return rawptr + (rva - sva)
    return None


def span_bytes(
    data: bytes,
    start: int,
    end: int,
    ib: int,
    secs: list[tuple[str, int, int, int, int]],
) -> bytes | None:
    if end <= start:
        return None
    o0 = va_to_off(start, ib, secs)
    if o0 is None or va_to_off(end - 1, ib, secs) is None:
        return None
    blob = data[o0 : o0 + (end - start)]
    if len(blob) != end - start:
        return None
    return blob


def consume_align_nops(blob: bytes) -> int:
    """Bytes of pure known align-NOP / pad concat from offset 0."""
    i = 0
    while i < len(blob):
        matched = False
        for pat in ALIGN_NOP_PATTERNS:
            if blob.startswith(pat, i):
                i += len(pat)
                matched = True
                break
        if not matched:
            break
    return i


def is_full_align_nop_run(blob: bytes) -> bool:
    return bool(blob) and consume_align_nops(blob) == len(blob)


def is_pure_pad_legacy(blob: bytes) -> bool:
    return bool(blob) and all(b in (0x00, 0x90, 0xCC) for b in blob)


def export_open_dark(campaign: Path, out_tsv: Path) -> list[dict[str, str]]:
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals cardinality {len(residuals)}")
    open_rows = [
        r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"
    ]
    if len(open_rows) != EXPECTED_OPEN_DARK:
        raise SystemExit(
            f"OPEN_DARK count {len(open_rows)} != {EXPECTED_OPEN_DARK}"
        )
    cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "classification",
        "campaignState",
        "bytePattern",
        "prevFunc",
        "nextFunc",
        "questionIds",
        "terminalState",
    ]
    _write_tsv(out_tsv, cols, open_rows)
    return open_rows


def scan_inbound(
    data: bytes, ib: int, secs: list[tuple[str, int, int, int, int]]
) -> tuple[Counter, Counter, Counter]:
    """Return (e8_targets, e9_targets, abs_aligned_targets) counting hits."""
    text = next((s for s in secs if s[0].startswith(".text")), None)
    if text is None:
        raise SystemExit("no .text")
    _name, sva, vsize, rawptr, rawsize = text
    text_lo = ib + sva
    e8: Counter = Counter()
    e9: Counter = Counter()
    for i in range(max(0, rawsize - 5)):
        op = data[rawptr + i]
        if op not in (0xE8, 0xE9):
            continue
        rel = struct.unpack_from("<i", data, rawptr + i + 1)[0]
        src = text_lo + i
        tgt = src + 5 + rel
        if op == 0xE8:
            e8[tgt] += 1
        else:
            e9[tgt] += 1
    abs_c: Counter = Counter()
    for name, sva, vsize, rawptr, rawsize in secs:
        if not (
            name.startswith(".text")
            or name.startswith(".rdata")
            or name.startswith(".data")
        ):
            continue
        for i in range(0, max(0, rawsize - 3), 4):
            val = struct.unpack_from("<I", data, rawptr + i)[0]
            if TEXT_LO <= val < TEXT_HI:
                abs_c[val] += 1
    return e8, e9, abs_c


def proposed_align_nop() -> dict[str, Any]:
    return {
        "terminalState": "TERMINAL_PADDING",
        "campaignState": "TERMINAL_PADDING",
        "contractState": "TERMINAL_STATIC",
        "classification": "PADDING",
        "classificationVerdict": "STATIC_FORMAL_PROOF",
        "bytePattern": "MSVC_ALIGN_NOP_BYTES",
        "shapeKind": PAD_KIND,
        "recoveryLane": "MSVC_ALIGN_NOP_FULL",
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 16:
        raise SystemExit(f"expected Gen16, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_DARK_CODE_LIKE_MASS":
        raise SystemExit(f"unexpected parent advance {parent_advance}")

    out_dir.mkdir(parents=True, exist_ok=True)
    open_tsv = out_dir / "open-dark.tsv"
    open_rows = export_open_dark(campaign, open_tsv)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)
    e8, e9, abs_c = scan_inbound(data, ib, secs)

    proofs: list[dict[str, Any]] = []
    still_open: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    inbound_rows: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()
    byte_buckets: Counter = Counter()

    for r in open_rows:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        n = end - start
        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            raise SystemExit(f"unmapped {r['startVa']}")
        byte_buckets[
            "1"
            if n == 1
            else "2-4"
            if n <= 4
            else "5-16"
            if n <= 16
            else "17-64"
            if n <= 64
            else "65-256"
            if n <= 256
            else "257-1024"
            if n <= 1024
            else "1k+"
        ] += 1

        e8n = int(e8.get(start, 0))
        e9n = int(e9.get(start, 0))
        absn = int(abs_c.get(start, 0))
        inbound_grade = (
            "E8_TARGET"
            if e8n
            else "E9_TARGET"
            if e9n
            else "ABS_PTR_ONLY"
            if absn
            else "NO_INBOUND"
        )
        inbound_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": n,
                "e8Count": e8n,
                "e9Count": e9n,
                "absAlignedCount": absn,
                "inboundGrade": inbound_grade,
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
            }
        )

        if is_full_align_nop_run(blob):
            # refuse if this residual is only non-pad that was already pure-legacy
            # (already closed by prior gens) — still allow MSVC multi-byte.
            pe_sha = hashlib.sha256(blob).hexdigest()
            prop = proposed_align_nop()
            # legacy pure pad should already be closed; if any remain, still terminal
            if is_pure_pad_legacy(blob):
                prop["shapeKind"] = "TINY_PAD_GAP"
                prop["bytePattern"] = "PADDING_LIKE_BYTES"
                prop["recoveryLane"] = "PURE_PAD_LEGACY"
            proofs.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": n,
                    "kind": prop["shapeKind"],
                    "subspanKinds": prop["shapeKind"],
                    "composition": f"1x{prop['shapeKind']}",
                    "recoveryLane": prop["recoveryLane"],
                    "peBytesSha256": pe_sha,
                    "recheckNote": "align_nop_full_span",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "proposed": prop,
                }
            )
            recovery_rows.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": n,
                    "primary": "ALIGN_NOP",
                    "recoveryLane": prop["recoveryLane"],
                    "subspanKinds": prop["shapeKind"],
                    "proposedTerminalState": prop["terminalState"],
                    "entityKey": r.get("entityKey") or "",
                    "inboundGrade": inbound_grade,
                }
            )
            lane_counts[prop["recoveryLane"]] += 1
            continue

        still_open.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": n,
                "primary": "STILL_OPEN",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "lane": "STILL_OPEN",
                "openBytes": n,
                "terminalBytes": 0,
                "inboundGrade": inbound_grade,
                "alignNopPrefix": consume_align_nops(blob),
                "note": "",
            }
        )
        recovery_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": n,
                "primary": "STILL_OPEN",
                "recoveryLane": "STILL_OPEN",
                "subspanKinds": "",
                "proposedTerminalState": "",
                "entityKey": r.get("entityKey") or "",
                "inboundGrade": inbound_grade,
            }
        )
        lane_counts["STILL_OPEN"] += 1

    term_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    lane_proof_counts = Counter(p["recoveryLane"] for p in proofs)
    inbound_still = Counter(r["inboundGrade"] for r in still_open)
    inbound_all = Counter(r["inboundGrade"] for r in inbound_rows)

    hard: list[str] = []
    for p in proofs:
        if p["proposed"]["terminalState"] != "TERMINAL_PADDING":
            hard.append(f"non_pad {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if p["proposed"].get("terminalState") == "TERMINAL_PADDING" and (
            "CODE" in (p.get("subspanKinds") or "")
            or "ENVELOPE" in (p.get("subspanKinds") or "")
        ):
            hard.append(f"pad+code {p['startVa']}")

    pack: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "status": (
            "READY_FOR_GENERATION"
            if proofs and not hard
            else "EMPTY"
            if not proofs and not hard
            else "BLOCKED"
        ),
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 16,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_proofs": len(proofs),
        "n_still_open": len(still_open),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "proposedTerminalStateCounts": dict(term_counts),
        "recoveryLaneCounts": dict(lane_proof_counts),
        "claims": [
            f"Exported exactly {EXPECTED_OPEN_DARK} Gen16 OPEN_DARK residuals.",
            (
                f"Recovered formal-pack residual-row proofs: {len(proofs)} "
                f"({dict(term_counts)}; lanes {dict(lane_proof_counts)})."
            ),
            f"Still open: {len(still_open)}.",
            f"Inbound grades (all 335): {dict(inbound_all)}.",
            f"Inbound grades (still open): {dict(inbound_still)}.",
            "Question supersession required for all proofs.",
            "No Gen16 ledger mutation; Gen17 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim CALL entry / REBUILD_READY",
            "Align-NOP terminal is static PE shape only (compiler padding)",
            "Inbound census is not a function-entry promotion",
            "Partial align-NOP prefixes without full residual cover stay OPEN",
        ],
        "proofs": proofs,
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 16,
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "byteBuckets": dict(byte_buckets),
            "recoveryLaneCountsAll": dict(lane_counts),
            "formalPackProofs": len(proofs),
            "stillOpen": len(still_open),
            "proposedTerminalStateCounts": dict(term_counts),
            "recoveryLaneProofCounts": dict(lane_proof_counts),
            "inboundAll": dict(inbound_all),
            "inboundStillOpen": dict(inbound_still),
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role DeepSeek direct (flash+pro max normal+adversarial) + Grok normal+adversarial subagents",
            "Gen17 apply only if READY and proofs > 0",
            "Remaining STILL_OPEN: coverage/TTD, deeper CODE_LIKE islands, LARGE_MIXED",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
    }

    return {
        "summary": summary,
        "pack": pack,
        "still_open": still_open,
        "recovery_rows": recovery_rows,
        "inbound_rows": inbound_rows,
        "open_rows": open_rows,
    }


def write_plate(
    result: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]
    still = result["still_open"]

    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    proof_cols = [
        "startVa",
        "endVa",
        "bytes",
        "kind",
        "subspanKinds",
        "composition",
        "recoveryLane",
        "peBytesSha256",
        "recheckNote",
        "entityKey",
        "questionIds",
        "proposedTerminalState",
        "requiresQuestionSupersession",
    ]
    with (out_dir / "proofs.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {PACK_SCHEMA}\n")
        w = csv.DictWriter(
            handle, fieldnames=proof_cols, delimiter="\t", lineterminator="\n"
        )
        w.writeheader()
        for p in pack["proofs"]:
            w.writerow(
                {
                    "startVa": p["startVa"],
                    "endVa": p["endVa"],
                    "bytes": p["bytes"],
                    "kind": p["kind"],
                    "subspanKinds": p["subspanKinds"],
                    "composition": p["composition"],
                    "recoveryLane": p["recoveryLane"],
                    "peBytesSha256": p["peBytesSha256"],
                    "recheckNote": p["recheckNote"],
                    "entityKey": p["entityKey"],
                    "questionIds": p["questionIds"],
                    "proposedTerminalState": p["proposed"]["terminalState"],
                    "requiresQuestionSupersession": p["proposed"][
                        "requiresQuestionSupersession"
                    ],
                }
            )

    still_cols = [
        "startVa",
        "endVa",
        "bytes",
        "primary",
        "entityKey",
        "questionIds",
        "lane",
        "openBytes",
        "terminalBytes",
        "inboundGrade",
        "alignNopPrefix",
        "note",
    ]
    _write_tsv(out_dir / "still-open.tsv", still_cols, still)
    _write_tsv(
        out_dir / "recovery.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "primary",
            "recoveryLane",
            "subspanKinds",
            "proposedTerminalState",
            "entityKey",
            "inboundGrade",
        ],
        result["recovery_rows"],
    )
    _write_tsv(
        out_dir / "inbound.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "e8Count",
            "e9Count",
            "absAlignedCount",
            "inboundGrade",
            "entityKey",
            "questionIds",
        ],
        result["inbound_rows"],
    )

    pack_summary = {
        k: pack[k]
        for k in pack
        if k not in {"proofs", "hardMismatches"}
    }
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    integrity = {
        "schema": "bea.re.open-dark-still-open-inbound.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_335": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "no_pad_with_code": all(
                "CODE" not in (p.get("subspanKinds") or "")
                and "ENVELOPE" not in (p.get("subspanKinds") or "")
                for p in pack["proofs"]
                if p["proposed"]["terminalState"] == "TERMINAL_PADDING"
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen17_apply": True,
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign-functions.tsv": _sha(campaign / "campaign-functions.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "specimen": _stamp(specimen),
            "campaignReady": _stamp(campaign / "campaign.ready.json"),
        },
        "falsifier": [
            "Re-export OPEN_DARK from Gen16: count must be 335",
            "Re-run tools/re_open_dark_still_open_inbound.py build: proof set must match",
            "Gen16 campaign-residuals.tsv sha must equal ledger_sha_pre",
            "Any TERMINAL_PADDING proof containing code envelope kinds",
        ],
    }
    integrity["checks"]["gen16_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen16_residuals_unchanged"
    ]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen16 OPEN_DARK still-open inbound / MSVC align-NOP

Status: **MEASURED** / formal pack **{pack['status']}**
Input: **{EXPECTED_OPEN_DARK}** OPEN_DARK
Proofs: **{len(pack['proofs'])}**
Still open: **{len(still)}**

## Recovery lanes (proofs)

| Lane | Count |
|------|------:|
{chr(10).join(f'| {k} | {v} |' for k, v in sorted(pack['recoveryLaneCounts'].items())) or '| (none) | 0 |'}

## Inbound (all input)

| Grade | Count |
|-------|------:|
{chr(10).join(f'| {k} | {v} |' for k, v in sorted(summary['counts']['inboundAll'].items())) or '| (none) | 0 |'}

## Non-claims

- Not Gen17 applied
- Not CALL entry / not names / not REBUILD_READY
- Align-NOP is compiler padding shape only
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark count")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    for p in pack["proofs"]:
        if p["proposed"]["terminalState"] == "TERMINAL_PADDING" and (
            "CODE" in (p.get("subspanKinds") or "")
            or "ENVELOPE" in (p.get("subspanKinds") or "")
        ):
            raise SystemExit(f"pad+code {p['startVa']}")
    rebuilt = build(campaign=campaign, specimen=specimen, out_dir=plate / "_scratch")
    import shutil

    shutil.rmtree(plate / "_scratch", ignore_errors=True)
    a = {
        (p["startVa"].lower(), p["peBytesSha256"], p["proposed"]["terminalState"])
        for p in pack["proofs"]
    }
    b = {
        (p["startVa"].lower(), p["peBytesSha256"], p["proposed"]["terminalState"])
        for p in rebuilt["pack"]["proofs"]
    }
    if a != b:
        raise SystemExit(f"proof drift only_plate={len(a - b)} only_rebuild={len(b - a)}")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "n_open_dark": EXPECTED_OPEN_DARK,
                "n_proofs": pack["n_proofs"],
                "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
                "recoveryLaneCounts": pack["recoveryLaneCounts"],
                "stillOpen": pack["n_still_open"],
                "inboundStillOpen": summary["counts"].get("inboundStillOpen"),
            },
            indent=2,
        )
    )
    print("OPEN_DARK_STILL_OPEN_INBOUND_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN16)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN16)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            campaign=args.campaign, specimen=args.specimen, out_dir=args.out
        )
        write_plate(
            result, args.out, campaign=args.campaign, specimen=args.specimen
        )
        print(json.dumps(result["summary"], indent=2))
        print("OPEN_DARK_STILL_OPEN_INBOUND_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        print(f"n_still_open={result['pack']['n_still_open']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
