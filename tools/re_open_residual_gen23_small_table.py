#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen23 remaining OPEN residuals: small code-ptr tables.

Exports OPEN_DARK (125) and OPEN_EXECUTED (4) from Generation 23.

OPEN_DARK lane SMALL_CODE_PTR_TABLE:
  Full residual cover by optional pad lead + consecutive .text dwords
  (min 4 dwords / 16B, max below Gen21's 32B threshold so these are new)
  + optional pure/MSVC pad trail, or INDEX_OR_BYTE_TABLE / SHORT_DATA_TAIL
  on the remainder (same gates as partial-data).

Terminals: TERMINAL_BOUNDED_AMBIGUITY (table+pad/index mixes) or
TERMINAL_DATA (pure table whole residual with no pad).

OPEN_EXECUTED: frozen OPEN with cheapest falsifiers (no small-table path).

Does **not** mutate Gen23/Gen22/Gen10. Does **not** invent names or
claim REBUILD_READY / CALL entry.
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

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen23-small-table.v1"
PACK_SCHEMA = "bea.re.open-residual-gen23-small-table-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 125
EXPECTED_OPEN_EXECUTED = 4
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000
MIN_TABLE_BYTES = 16  # 4 dwords
MAX_TABLE_BYTES_EXCL = 32  # Gen21 already closes >=32; require cpr < 32 for "new"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN23 = Path(
    "local-lab/residual-terminal-generation23-partial-data-20260805-v1/"
    "generation-23-residual-terminal-partial-data"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen23-small-table-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE byte change; small code-ptr table re-check fails (non-.text dword); "
    "residual membership of a named function body; REBUILD_READY claim"
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


def is_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def pad_kind(blob: bytes, mass) -> str:
    if mass.is_pure_pad(blob):
        return "TINY_PAD_GAP" if len(blob) <= 8 else "ALIGN_PAD_PREFIX"
    return "MSVC_ALIGN_NOP_RUN"


def code_ptr_run_min(
    blob: bytes, min_dwords: int = 4
) -> tuple[int, int] | None:
    """Best (align, run_bytes) with run_bytes >= min_dwords*4."""
    best_a, best_run = 0, 0
    for a in range(4):
        body = blob[a:]
        usable = len(body) - (len(body) % 4)
        cnt = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", body, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                cnt += 1
            else:
                break
        run = cnt * 4
        if run > best_run:
            best_a, best_run = a, run
    if best_run < min_dwords * 4:
        return None
    return best_a, best_run


def compose_small_table(
    blob: bytes,
    base: int,
    md,
    mass,
    inb,
    large_mod,
    ds_mod,
    pd_mod,
) -> dict[str, Any] | None:
    """Small code-ptr table (16–31B) + pad/index/short-tail full cover."""
    if not blob or len(blob) < 12:
        return None
    # skip if any prior shape instrument closes it
    if ds_mod.compose_data_shape(blob, base, md, mass, inb, large_mod):
        return None
    if pd_mod.compose_partial_data(blob, base, md, mass, inb, large_mod, ds_mod):
        return None

    pos = 0
    terms: list[dict[str, Any]] = []
    rest = blob

    lead = ds_mod.leading_pad_len(rest, mass, inb)
    if lead >= 1 and lead < len(rest) and is_pad(rest[:lead], mass, inb):
        piece = rest[:lead]
        terms.append(
            {
                "kind": pad_kind(piece, mass),
                "startVa": f"0x{base + pos:08x}",
                "endVa": f"0x{base + pos + lead:08x}",
                "bytes": lead,
            }
        )
        pos += lead
        rest = blob[pos:]

    cp = code_ptr_run_min(rest, min_dwords=4)
    if cp is None:
        return None
    align, cpr = cp

    # require cpr < 32 so these are strictly new vs Gen21 32B threshold
    if cpr >= MAX_TABLE_BYTES_EXCL:
        return None

    if align > 0:
        lead_b = rest[:align]
        if not is_pad(lead_b, mass, inb):
            return None
        terms.append(
            {
                "kind": pad_kind(lead_b, mass),
                "startVa": f"0x{base + pos:08x}",
                "endVa": f"0x{base + pos + align:08x}",
                "bytes": align,
            }
        )
        pos += align
        rest = blob[pos:]
        cp2 = code_ptr_run_min(rest, min_dwords=4)
        if cp2 is None or cp2[0] != 0:
            return None
        align, cpr = cp2
        if cpr >= MAX_TABLE_BYTES_EXCL:
            return None

    # verify every dword
    for i in range(0, cpr, 4):
        v = struct.unpack_from("<I", rest, i)[0]
        if not (TEXT_LO <= v < TEXT_HI):
            return None

    terms.append(
        {
            "kind": "CODE_ADDRESS_TABLE_PREFIX",
            "startVa": f"0x{base + pos:08x}",
            "endVa": f"0x{base + pos + cpr:08x}",
            "bytes": cpr,
        }
    )
    pos += cpr
    rest = blob[pos:]

    if rest:
        if is_pad(rest, mass, inb):
            terms.append(
                {
                    "kind": pad_kind(rest, mass),
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
        elif pd_mod.index_full_or_none(rest, md, mass):
            # Refuse bulk INDEX after a *small* table peel (Gen24 police):
            # e.g. 28B table + ~140B INDEX on 171B residual Gen22 left STILL_OPEN.
            if len(rest) > max(cpr, 32):
                return None
            terms.append(
                {
                    "kind": "INDEX_OR_BYTE_TABLE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
        elif pd_mod.short_data_tail_ok(rest, md, mass):
            terms.append(
                {
                    "kind": "SHORT_DATA_TAIL",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
        else:
            return None

    if pos != len(blob) or not terms:
        return None
    if not any(t["kind"] == "CODE_ADDRESS_TABLE_PREFIX" for t in terms):
        return None

    kinds = [t["kind"] for t in terms]
    only_table = kinds == ["CODE_ADDRESS_TABLE_PREFIX"]
    terminal = "TERMINAL_DATA" if only_table else "TERMINAL_BOUNDED_AMBIGUITY"
    classification = "DATA" if only_table else "DATA_OR_MIXED_SHAPE"

    return {
        "lane": "SMALL_CODE_PTR_TABLE",
        "terms": terms,
        "kinds": kinds,
        "shapeKind": "+".join(kinds),
        "terminalState": terminal,
        "classification": classification,
        "tableBytes": cpr,
        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        "note": f"cpr={cpr} n_terms={len(terms)} kinds={'+'.join(kinds)}",
    }


def recheck_terms(blob: bytes, base: int, terms: list[dict], md, mass, inb, pd_mod) -> bool:
    for t in terms:
        lo = int(t["startVa"], 16) - base
        hi = int(t["endVa"], 16) - base
        if lo < 0 or hi > len(blob) or hi <= lo:
            return False
        piece = blob[lo:hi]
        k = t["kind"]
        if k in {"TINY_PAD_GAP", "ALIGN_PAD_PREFIX", "MSVC_ALIGN_NOP_RUN"}:
            if not is_pad(piece, mass, inb):
                return False
        elif k == "CODE_ADDRESS_TABLE_PREFIX":
            if len(piece) < MIN_TABLE_BYTES or len(piece) % 4 or len(piece) >= MAX_TABLE_BYTES_EXCL:
                return False
            for i in range(0, len(piece), 4):
                v = struct.unpack_from("<I", piece, i)[0]
                if not (TEXT_LO <= v < TEXT_HI):
                    return False
        elif k == "INDEX_OR_BYTE_TABLE":
            if not pd_mod.index_full_or_none(piece, md, mass):
                return False
        elif k == "SHORT_DATA_TAIL":
            if not pd_mod.short_data_tail_ok(piece, md, mass):
                return False
        else:
            return False
    return True


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    term = rec["terminalState"]
    return {
        "classification": rec["classification"],
        "classificationVerdict": "STATIC_SMALL_CODE_PTR_TABLE",
        "terminalState": term,
        "campaignState": term,
        "bytePattern": (
            "DATA_TABLE_BYTES" if term == "TERMINAL_DATA" else "MIXED_OR_CODE_LIKE_BYTES"
        ),
        "contractState": term,
        "shapeKind": rec["shapeKind"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": "OPEN_DARK_RESIDUAL",
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )
    inb = _load_mod(
        "re_open_dark_still_open_inbound",
        ROOT / "tools" / "re_open_dark_still_open_inbound.py",
    )
    large_mod = _load_mod(
        "re_large_mixed_blob_classify", ROOT / "tools" / "re_large_mixed_blob_classify.py"
    )
    ds_mod = _load_mod(
        "re_open_residual_gen21_data_shape",
        ROOT / "tools" / "re_open_residual_gen21_data_shape.py",
    )
    pd_mod = _load_mod(
        "re_open_residual_gen22_partial_data",
        ROOT / "tools" / "re_open_residual_gen22_partial_data.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 23:
        raise SystemExit(f"expected Gen23, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_PARTIAL_DATA":
        raise SystemExit(f"unexpected parent advance {parent_advance}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    executed = [
        r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    ]
    if len(dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(dark)}")
    if len(executed) != EXPECTED_OPEN_EXECUTED:
        raise SystemExit(f"OPEN_EXECUTED {len(executed)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "prevFunc",
        "nextFunc",
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)
    _write_tsv(out_dir / "open-executed.tsv", export_cols, executed)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    proofs: list[dict[str, Any]] = []
    still_dark: list[dict[str, Any]] = []
    still_exec: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    for r in dark:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            raise SystemExit(f"unmapped {r['startVa']}")
        rec = compose_small_table(
            blob, start, md, mass, inb, large_mod, ds_mod, pd_mod
        )
        if rec is None or not recheck_terms(
            blob, start, rec["terms"], md, mass, inb, pd_mod
        ):
            still_dark.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_DARK_RESIDUAL",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "No small code-ptr table full cover; need inbound ownership, "
                        "TTD, residual-split, or new shape instrument"
                    ),
                }
            )
            lane_counts["STILL_OPEN_OPEN_DARK_RESIDUAL"] += 1
            continue

        prop = proposed_for(rec)
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": int(r.get("bytes") or (end - start)),
                "kind": prop["shapeKind"],
                "subspanKinds": prop["shapeKind"],
                "composition": "+".join(rec["kinds"]),
                "recoveryLane": prop["recoveryLane"],
                "peBytesSha256": rec["peBytesSha256"],
                "recheckNote": rec["note"],
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "tableBytes": rec["tableBytes"],
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
            }
        )
        recovery_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "source": "OPEN_DARK_RESIDUAL",
                "recoveryLane": prop["recoveryLane"],
                "subspanKinds": prop["shapeKind"],
                "tableBytes": rec["tableBytes"],
                "proposedTerminalState": prop["terminalState"],
                "entityKey": r.get("entityKey") or "",
            }
        )
        lane_counts[prop["recoveryLane"]] += 1
        lane_counts[prop["terminalState"]] += 1

    for r in executed:
        still_exec.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "source": "OPEN_EXECUTED_RESIDUAL",
                "lane": "STILL_OPEN",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "cheapestFalsifier": (
                    "EXECUTED body/noise fragment; need TTD call-context unit split "
                    "or inbound ownership (coverage join alone is not residual-row "
                    "terminal)"
                ),
            }
        )
        lane_counts["STILL_OPEN_OPEN_EXECUTED_RESIDUAL"] += 1

    term_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    lane_proof = Counter(p["recoveryLane"] for p in proofs)

    hard: list[str] = []
    for p in proofs:
        prop = p.get("proposed") or {}
        if prop.get("terminalState") not in {
            "TERMINAL_DATA",
            "TERMINAL_BOUNDED_AMBIGUITY",
        }:
            hard.append(f"bad_term {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        tb = int(p.get("tableBytes") or 0)
        if tb < MIN_TABLE_BYTES or tb >= MAX_TABLE_BYTES_EXCL:
            hard.append(f"table_bytes {p['startVa']}={tb}")
        if "ENVELOPE" in (p.get("subspanKinds") or "") or "STATIC_CODE" in (
            p.get("subspanKinds") or ""
        ):
            hard.append(f"code_launder {p['startVa']}")
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            hard.append(f"non_dark {p['startVa']}")

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
        "campaignGeneration": 23,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_dark_proofs": len(proofs),
        "n_executed_proofs": 0,
        "n_still_open_dark": len(still_dark),
        "n_still_open_executed": len(still_exec),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "proposedTerminalStateCounts": dict(term_counts),
        "recoveryLaneCounts": dict(lane_proof),
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen23.",
            f"Small code-ptr table proofs: {len(proofs)} ({dict(term_counts)}).",
            f"All table runs are 16–31B (strictly below Gen21 32B threshold).",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            "No EXECUTED promotions; no CODE envelope kinds.",
            "Question supersession required for all proofs.",
            "No Gen23 ledger mutation; Gen24 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY / CALL entry",
            "Small tables are static PE pointer-table shape only",
            "OPEN_EXECUTED fragments frozen OPEN with falsifiers",
            "Does not prove table consumers or switch ownership",
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
        "campaignGeneration": 23,
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
            "recoveryLaneCountsAll": dict(lane_counts),
            "formalPackProofs": len(proofs),
            "stillOpenDark": len(still_dark),
            "stillOpenExecuted": len(still_exec),
            "proposedTerminalStateCounts": dict(term_counts),
            "recoveryLaneProofCounts": dict(lane_proof),
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role DeepSeek direct (flash+pro max normal+adversarial) + Grok normal+adversarial subagents",
            "Gen24 apply only if READY and proofs > 0",
            "Remaining OPEN_DARK: inbound/TTD/residual-split",
            "Remaining OPEN_EXECUTED: TTD unit-split ownership",
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
    result: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path
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
        "tableBytes",
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
                    "tableBytes": p["tableBytes"],
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
        "cheapestFalsifier",
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
            "tableBytes",
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
        "schema": "bea.re.open-residual-gen23-small-table.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_125": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_4": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "table_bytes_16_31": all(
                MIN_TABLE_BYTES <= int(p.get("tableBytes") or 0) < MAX_TABLE_BYTES_EXCL
                for p in pack["proofs"]
            ),
            "no_code_envelope_terms": all(
                "ENVELOPE" not in (p.get("subspanKinds") or "")
                and "STATIC_CODE" not in (p.get("subspanKinds") or "")
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen24_apply": True,
            "no_executed_proofs": pack["n_executed_proofs"] == 0,
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
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen23: 125/4",
            "Re-run build: proof set must match",
            "Gen23 residuals sha must equal ledger_sha_pre",
            "Any tableBytes >= 32 (Gen21 domain) or CODE envelope kinds",
        ],
    }
    integrity["checks"]["gen23_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen23_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen23 OPEN residual small code-ptr tables

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK: **{EXPECTED_OPEN_DARK}** → proofs **{len(pack['proofs'])}**
OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}** → proofs **0**
Still open: dark **{len(result['still_dark'])}**, executed **{len(result['still_exec'])}**

## Non-claims
- Not Gen24 applied
- Not names / not REBUILD_READY / not CALL entry
- Tables are 16–31B pointer runs (below Gen21 32B gate)
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
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
    for p in pack["proofs"]:
        tb = int(p.get("tableBytes") or 0)
        if tb < MIN_TABLE_BYTES or tb >= MAX_TABLE_BYTES_EXCL:
            raise SystemExit(f"tableBytes {p['startVa']}")
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            raise SystemExit(f"non-dark {p['startVa']}")
    rebuilt = build(
        campaign=campaign, specimen=specimen, out_dir=plate / "_scratch"
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
        raise SystemExit(f"proof drift only_plate={len(a-b)} only_rebuild={len(b-a)}")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "n_open_dark": EXPECTED_OPEN_DARK,
                "n_open_executed": EXPECTED_OPEN_EXECUTED,
                "n_proofs": pack["n_proofs"],
                "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
                "stillOpenDark": pack["n_still_open_dark"],
                "stillOpenExecuted": pack["n_still_open_executed"],
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN23_SMALL_TABLE_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN23)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN23)
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
        print("OPEN_RESIDUAL_GEN23_SMALL_TABLE_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
