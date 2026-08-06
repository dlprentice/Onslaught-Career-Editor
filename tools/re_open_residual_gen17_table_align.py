#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen17 remaining OPEN residuals: table+align-NOP and PROLOGUE_LIKE.

Exports OPEN_DARK (285) and OPEN_EXECUTED (108) from Generation 17:

  1. OPEN_DARK full-cover CODE_ADDRESS_TABLE + MSVC/Intel align-NOP lead/tail
     → residual-row TERMINAL_BOUNDED_AMBIGUITY (static shape only).
  2. OPEN_EXECUTED cohort with frozen PROLOGUE_LIKE TTD call-context
     RUNTIME_CALL_ENTRY (7) → residual-row TERMINAL_BOUNDED_AMBIGUITY
     (executed call-entry shape; no function name).

Does **not** mutate Gen17/Gen16/Gen10. Does **not** invent names or
claim REBUILD_READY. Emits MEASURED plate + READY formal pack when PE
rechecks and evidence joins survive.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.open-residual-gen17-table-align.v1"
PACK_SCHEMA = "bea.re.open-residual-gen17-table-align-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_TABLE_ALIGN_EXECUTED.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 285
EXPECTED_OPEN_EXECUTED = 108
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN17 = Path(
    "local-lab/residual-terminal-generation17-still-open-inbound-20260805-v1/"
    "generation-17-residual-terminal-still-open-inbound"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_PROLOGUE = Path("local-lab/ttd-call-context-prologue-like-20260805-v1")
DEFAULT_OUT = Path("local-lab/open-residual-gen17-table-align-20260805-v1")

PAD_KINDS = {
    "TINY_PAD_GAP",
    "ALIGN_PAD_PREFIX",
    "ZERO_RUN_PREFIX",
    "MSVC_ALIGN_NOP_RUN",
}
DATA_KINDS = {"CODE_ADDRESS_TABLE_PREFIX", "FLOAT32_TABLE_PREFIX", "INDEX_OR_BYTE_TABLE"}
CODE_KIND = "STATIC_CODE_DECODE_ENVELOPE"
EXEC_KIND = "EXECUTED_PROLOGUE_LIKE_CALL_ENTRY"

DEFAULT_FALSIFIER_TABLE = (
    "PE byte change; failed code-pointer table re-check; lead/tail not align-NOP; "
    "inbound reference proving non-table semantics; residual membership of a named body"
)
DEFAULT_FALSIFIER_EXEC = (
    "TTD call-context re-run on level521 open fails CALL+entry pair; residual not "
    "EXECUTED; PE body change; invented name/REBUILD_READY claim"
)


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def pe_map(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections = []
    for i in range(num_sections):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for _name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            if rva - sva >= rawsize:
                return None
            return rawptr + (rva - sva)
    return None


def span_bytes(data: bytes, start: int, end: int, ib: int, secs) -> bytes | None:
    if end <= start:
        return None
    o0 = va_to_off(start, ib, secs)
    if o0 is None or va_to_off(end - 1, ib, secs) is None:
        return None
    blob = data[o0 : o0 + (end - start)]
    if len(blob) != end - start:
        return None
    return blob


def pad_kind(blob: bytes, mass, inb) -> str:
    if mass.is_pure_pad(blob):
        return "TINY_PAD_GAP" if len(blob) <= 8 else "ALIGN_PAD_PREFIX"
    return "MSVC_ALIGN_NOP_RUN"


def is_align_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def code_ptr_run(blob: bytes, align: int = 0) -> int:
    if align < 0 or align > 3:
        return 0
    body = blob[align:]
    usable = len(body) - (len(body) % 4)
    n = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", body, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            n += 1
        else:
            break
    return n * 4


def best_code_ptr_run(blob: bytes) -> tuple[int, int]:
    best_align, best_run = 0, 0
    for a in range(4):
        run = code_ptr_run(blob, a)
        if run > best_run:
            best_align, best_run = a, run
    return best_align, best_run


def try_table_plus_align(
    data: bytes, start: int, end: int, ib: int, secs, mass, inb
) -> dict[str, Any] | None:
    blob = span_bytes(data, start, end, ib, secs)
    if blob is None:
        return None
    n = len(blob)
    align, cpr = best_code_ptr_run(blob)
    if cpr < 32:
        return None
    lead = blob[:align]
    mid = blob[align : align + cpr]
    tail = blob[align + cpr :]
    if lead and not is_align_pad(lead, mass, inb):
        return None
    if tail and not is_align_pad(tail, mass, inb):
        return None
    if not lead and not tail:
        return None  # pure table whole — not in this lane
    # Prior mass pack already closed pure 00/90/CC lead/tail tables. This plate
    # only admits when at least one pad side is MSVC multi-byte align-NOP.
    msvc_side = (
        bool(lead)
        and not mass.is_pure_pad(lead)
        and inb.is_full_align_nop_run(lead)
    ) or (
        bool(tail)
        and not mass.is_pure_pad(tail)
        and inb.is_full_align_nop_run(tail)
    )
    if not msvc_side:
        return None

    terms: list[dict[str, Any]] = []
    kinds: list[str] = []
    cur = start
    if lead:
        k = pad_kind(lead, mass, inb)
        terms.append(
            {
                "startVa": f"0x{cur:08x}",
                "endVa": f"0x{cur + len(lead):08x}",
                "bytes": len(lead),
                "kind": k,
            }
        )
        kinds.append(k)
        cur += len(lead)
    terms.append(
        {
            "startVa": f"0x{cur:08x}",
            "endVa": f"0x{cur + cpr:08x}",
            "bytes": cpr,
            "kind": "CODE_ADDRESS_TABLE_PREFIX",
        }
    )
    kinds.append("CODE_ADDRESS_TABLE_PREFIX")
    cur += cpr
    if tail:
        k = pad_kind(tail, mass, inb)
        terms.append(
            {
                "startVa": f"0x{cur:08x}",
                "endVa": f"0x{end:08x}",
                "bytes": len(tail),
                "kind": k,
            }
        )
        kinds.append(k)
    return {
        "lane": "TABLE_PLUS_ALIGN_PAD",
        "kinds": kinds,
        "terms": terms,
        "note": f"align={align} code_ptrs={cpr // 4}+align_pad",
        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
    }


def proposed_table(kinds: list[str]) -> dict[str, Any]:
    return {
        "classification": "DATA_OR_MIXED_SHAPE",
        "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": "+".join(kinds),
        "recoveryLane": "TABLE_PLUS_ALIGN_PAD",
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER_TABLE,
    }


def proposed_exec() -> dict[str, Any]:
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": "RUNTIME_CALL_ENTRY_CORROBORATED",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": EXEC_KIND,
        "recoveryLane": "EXECUTED_PROLOGUE_LIKE_CALL_ENTRY",
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER_EXEC,
    }


def load_prologue_entries(prologue_dir: Path) -> list[dict[str, Any]]:
    summary = json.loads((prologue_dir / "SUMMARY.json").read_text(encoding="utf-8"))
    if summary.get("status") != "MEASURED":
        raise SystemExit(f"prologue plate not MEASURED: {summary.get('status')}")
    if summary.get("specimen_sha256_static") != SPECIMEN_SHA256:
        raise SystemExit("prologue plate specimen mismatch")
    results = summary.get("results") or []
    if not results:
        raise SystemExit("prologue plate empty results")
    entries = []
    for r in results:
        if r.get("grade") != "RUNTIME_CALL_ENTRY":
            continue
        va = (r.get("entryVa") or "").lower()
        if not va:
            continue
        entries.append(
            {
                "entryVa": va,
                "entries": int(r.get("entries") or 0),
                "calls": int(r.get("calls") or 0),
                "pairs": int(r.get("pairs") or 0),
                "grade": r.get("grade"),
            }
        )
    if len(entries) != 7:
        raise SystemExit(f"expected 7 RUNTIME_CALL_ENTRY, got {len(entries)}")
    for e in entries:
        if e["entries"] < 1 or e["calls"] < 1 or e["pairs"] < 1:
            raise SystemExit(f"weak call-context {e}")
    return entries


def build(
    *,
    campaign: Path,
    specimen: Path,
    prologue_dir: Path,
    out_dir: Path,
) -> dict[str, Any]:
    mass = _load_mod("re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py")
    inb = _load_mod(
        "re_open_dark_still_open_inbound",
        ROOT / "tools" / "re_open_dark_still_open_inbound.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 17:
        raise SystemExit(f"expected Gen17, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_DARK_STILL_OPEN_INBOUND":
        raise SystemExit(f"unexpected parent advance {parent_advance}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    executed = [
        r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    ]
    if len(dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(dark)} != {EXPECTED_OPEN_DARK}")
    if len(executed) != EXPECTED_OPEN_EXECUTED:
        raise SystemExit(f"OPEN_EXECUTED {len(executed)} != {EXPECTED_OPEN_EXECUTED}")

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_tsv(
        out_dir / "open-dark.tsv",
        [
            "entityKey",
            "startVa",
            "endVa",
            "bytes",
            "observationState",
            "campaignState",
            "questionIds",
            "prevFunc",
            "nextFunc",
        ],
        dark,
    )
    _write_tsv(
        out_dir / "open-executed.tsv",
        [
            "entityKey",
            "startVa",
            "endVa",
            "bytes",
            "observationState",
            "campaignState",
            "questionIds",
            "prevFunc",
            "nextFunc",
        ],
        executed,
    )

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)

    prologue_entries = load_prologue_entries(prologue_dir)
    prologue_sha = _sha(prologue_dir / "SUMMARY.json")
    exec_by_start = {r["startVa"].lower(): r for r in executed}

    proofs: list[dict[str, Any]] = []
    still_dark: list[dict[str, Any]] = []
    still_exec: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    # --- OPEN_DARK table + align pad ---
    for r in dark:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        rec = try_table_plus_align(data, start, end, ib, secs, mass, inb)
        if rec is None:
            still_dark.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_DARK",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                }
            )
            lane_counts["STILL_OPEN_DARK"] += 1
            continue
        # PE recheck
        ok = True
        notes = [rec.get("note") or ""]
        for t in rec["terms"]:
            lo = int(t["startVa"], 16)
            hi = int(t["endVa"], 16)
            blob = span_bytes(data, lo, hi, ib, secs)
            if blob is None:
                ok = False
                notes.append(f"{t['kind']}:unmapped")
                continue
            k = t["kind"]
            if k in PAD_KINDS:
                if not is_align_pad(blob, mass, inb):
                    ok = False
                    notes.append(f"{k}:not_pad")
            elif k == "CODE_ADDRESS_TABLE_PREFIX":
                run = code_ptr_run(blob, 0)
                if run < 32:
                    ok = False
                    notes.append("table:too_short")
                elif run < len(blob) - (len(blob) % 4):
                    # trailing non-pointer dwords inside claimed table span
                    ok = False
                    notes.append("table:non_ptr_tail")
            else:
                ok = False
                notes.append(f"bad_kind:{k}")
        if not ok:
            still_dark.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_DARK",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "note": ";".join(notes),
                }
            )
            lane_counts["STILL_OPEN_DARK"] += 1
            continue

        prop = proposed_table(rec["kinds"])
        pe_sha = rec["peBytesSha256"]
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": int(r.get("bytes") or (end - start)),
                "kind": prop["shapeKind"],
                "subspanKinds": "+".join(rec["kinds"]),
                "composition": "+".join(rec["kinds"]),
                "recoveryLane": prop["recoveryLane"],
                "peBytesSha256": pe_sha,
                "recheckNote": ";".join(notes),
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "proposed": prop,
            }
        )
        recovery_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "source": "OPEN_DARK",
                "recoveryLane": prop["recoveryLane"],
                "subspanKinds": "+".join(rec["kinds"]),
                "proposedTerminalState": prop["terminalState"],
                "entityKey": r.get("entityKey") or "",
            }
        )
        lane_counts[prop["recoveryLane"]] += 1

    # --- OPEN_EXECUTED PROLOGUE_LIKE ---
    prologue_starts = {e["entryVa"] for e in prologue_entries}
    for e in prologue_entries:
        camp = exec_by_start.get(e["entryVa"])
        if camp is None:
            raise SystemExit(f"prologue entry missing from Gen17 EXECUTED: {e['entryVa']}")
        start = int(camp["startVa"], 16)
        end = int(camp["endVa"], 16)
        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            raise SystemExit(f"unmapped exec {e['entryVa']}")
        if camp.get("observationState") != "EXECUTED":
            raise SystemExit(f"not EXECUTED {e['entryVa']}")
        prop = proposed_exec()
        pe_sha = hashlib.sha256(blob).hexdigest()
        proofs.append(
            {
                "startVa": camp["startVa"],
                "endVa": camp["endVa"],
                "bytes": int(camp.get("bytes") or (end - start)),
                "kind": EXEC_KIND,
                "subspanKinds": EXEC_KIND,
                "composition": EXEC_KIND,
                "recoveryLane": prop["recoveryLane"],
                "peBytesSha256": pe_sha,
                "recheckNote": (
                    f"pairs={e['pairs']} entries={e['entries']} calls={e['calls']}"
                ),
                "entityKey": camp.get("entityKey") or "",
                "questionIds": camp.get("questionIds") or "",
                "sourceState": "OPEN_EXECUTED_RESIDUAL",
                "runtimeEvidence": {
                    "plate": str(prologue_dir).replace("\\", "/"),
                    "summarySha256": prologue_sha,
                    "grade": e["grade"],
                    "pairs": e["pairs"],
                    "entries": e["entries"],
                    "calls": e["calls"],
                },
                "proposed": prop,
            }
        )
        recovery_rows.append(
            {
                "startVa": camp["startVa"],
                "endVa": camp["endVa"],
                "bytes": camp.get("bytes"),
                "source": "OPEN_EXECUTED",
                "recoveryLane": prop["recoveryLane"],
                "subspanKinds": EXEC_KIND,
                "proposedTerminalState": prop["terminalState"],
                "entityKey": camp.get("entityKey") or "",
            }
        )
        lane_counts[prop["recoveryLane"]] += 1

    for r in executed:
        if r["startVa"].lower() in prologue_starts:
            continue
        still_exec.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "source": "OPEN_EXECUTED",
                "lane": "STILL_OPEN",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
            }
        )
        lane_counts["STILL_OPEN_EXECUTED"] += 1

    term_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    lane_proof = Counter(p["recoveryLane"] for p in proofs)
    source_counts = Counter(p["sourceState"] for p in proofs)

    hard: list[str] = []
    for p in proofs:
        if p["proposed"]["terminalState"] != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if p["proposed"]["terminalState"] == "TERMINAL_PADDING":
            hard.append(f"unexpected_pad {p['startVa']}")
        prop = p.get("proposed") or {}
        if prop.get("contractState") == "REBUILD_READY" or prop.get(
            "rebuildState"
        ) == "REBUILD_READY":
            hard.append(f"rebuild {p['startVa']}")
        if prop.get("terminalState") not in {
            "TERMINAL_BOUNDED_AMBIGUITY",
            "TERMINAL_PADDING",
            "TERMINAL_DATA",
        }:
            hard.append(f"bad_terminal_enum {p['startVa']}")

    n_table = sum(1 for p in proofs if p["recoveryLane"] == "TABLE_PLUS_ALIGN_PAD")
    n_exec = sum(
        1 for p in proofs if p["recoveryLane"] == "EXECUTED_PROLOGUE_LIKE_CALL_ENTRY"
    )

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
        "campaignGeneration": 17,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_table_align_proofs": n_table,
        "n_executed_prologue_proofs": n_exec,
        "n_still_open_dark": len(still_dark),
        "n_still_open_executed": len(still_exec),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "proposedTerminalStateCounts": dict(term_counts),
        "recoveryLaneCounts": dict(lane_proof),
        "sourceStateCounts": dict(source_counts),
        "prologuePlate": {
            "path": str(prologue_dir).replace("\\", "/"),
            "summarySha256": prologue_sha,
        },
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen17.",
            f"Table+align-NOP full-cover proofs: {n_table}.",
            f"EXECUTED PROLOGUE_LIKE RUNTIME_CALL_ENTRY proofs: {n_exec}.",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            "All proofs TERMINAL_BOUNDED_AMBIGUITY; question supersession required.",
            "No Gen17 ledger mutation; Gen18 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY",
            "Table+align is static PE shape only",
            "EXECUTED PROLOGUE_LIKE proves CALL+entry pair under level521 open only",
            "Does not close full argument/return contracts",
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
        "campaignGeneration": 17,
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
            "recoveryLaneCountsAll": dict(lane_counts),
            "formalPackProofs": len(proofs),
            "stillOpenDark": len(still_dark),
            "stillOpenExecuted": len(still_exec),
            "proposedTerminalStateCounts": dict(term_counts),
            "recoveryLaneProofCounts": dict(lane_proof),
            "sourceStateCounts": dict(source_counts),
            "n_table_align_proofs": n_table,
            "n_executed_prologue_proofs": n_exec,
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role DeepSeek direct (flash+pro max normal+adversarial) + Grok normal+adversarial subagents",
            "Gen18 apply only if READY and proofs > 0",
            "Remaining STILL_OPEN dark: CODE_LIKE_PARTIAL / LARGE_MIXED",
            "Remaining EXECUTED non-prologue: BODY_FRAGMENT / CASE / RET_SHAPED instruments",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
    }

    return {
        "summary": summary,
        "pack": pack,
        "still_dark": still_dark,
        "still_exec": still_exec,
        "recovery_rows": recovery_rows,
    }


def write_plate(
    result: dict[str, Any],
    out_dir: Path,
    *,
    campaign: Path,
    specimen: Path,
    prologue_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]

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
        "sourceState",
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
                    "sourceState": p["sourceState"],
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
        "source",
        "lane",
        "entityKey",
        "questionIds",
        "note",
    ]
    _write_tsv(out_dir / "still-open-dark.tsv", still_cols, result["still_dark"])
    _write_tsv(out_dir / "still-open-executed.tsv", still_cols, result["still_exec"])
    _write_tsv(
        out_dir / "recovery.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "source",
            "recoveryLane",
            "subspanKinds",
            "proposedTerminalState",
            "entityKey",
        ],
        result["recovery_rows"],
    )

    pack_summary = {k: pack[k] for k in pack if k not in {"proofs", "hardMismatches"}}
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    integrity = {
        "schema": "bea.re.open-residual-gen17-table-align.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_285": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_108": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "only_bounded_ambiguity": all(
                p["proposed"]["terminalState"] == "TERMINAL_BOUNDED_AMBIGUITY"
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen18_apply": True,
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
            "prologueSummary": _stamp(prologue_dir / "SUMMARY.json"),
        },
        "falsifier": [
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen17: counts 285/108",
            "Re-run build: proof set must match",
            "Gen17 campaign-residuals.tsv sha must equal ledger_sha_pre",
            "Any REBUILD_READY or invented name in proofs",
        ],
    }
    integrity["checks"]["gen17_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen17_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen17 OPEN residual table+align / PROLOGUE_LIKE

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK input: **{EXPECTED_OPEN_DARK}**
OPEN_EXECUTED input: **{EXPECTED_OPEN_EXECUTED}**
Proofs: **{len(pack['proofs'])}** (table {pack['n_table_align_proofs']} + exec {pack['n_executed_prologue_proofs']})
Still open dark: **{len(result['still_dark'])}**
Still open executed: **{len(result['still_exec'])}**

## Non-claims

- Not Gen18 applied
- Not names / not REBUILD_READY
- Table+align is static shape; PROLOGUE_LIKE is CALL+entry under level521 only
""",
        encoding="utf-8",
    )


def verify_plate(
    plate: Path, campaign: Path, specimen: Path, prologue_dir: Path
) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark count")
    if summary["counts"]["n_open_executed_input"] != EXPECTED_OPEN_EXECUTED:
        raise SystemExit("open executed count")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    rebuilt = build(
        campaign=campaign,
        specimen=specimen,
        prologue_dir=prologue_dir,
        out_dir=plate / "_scratch",
    )
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
                "n_open_executed": EXPECTED_OPEN_EXECUTED,
                "n_proofs": pack["n_proofs"],
                "n_table": pack["n_table_align_proofs"],
                "n_exec_prologue": pack["n_executed_prologue_proofs"],
                "stillOpenDark": pack["n_still_open_dark"],
                "stillOpenExecuted": pack["n_still_open_executed"],
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN17_TABLE_ALIGN_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN17)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--prologue-dir", type=Path, default=DEFAULT_PROLOGUE)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN17)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    v.add_argument("--prologue-dir", type=Path, default=DEFAULT_PROLOGUE)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            campaign=args.campaign,
            specimen=args.specimen,
            prologue_dir=args.prologue_dir,
            out_dir=args.out,
        )
        write_plate(
            result,
            args.out,
            campaign=args.campaign,
            specimen=args.specimen,
            prologue_dir=args.prologue_dir,
        )
        print(json.dumps(result["summary"], indent=2))
        print("OPEN_RESIDUAL_GEN17_TABLE_ALIGN_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen, args.prologue_dir)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
