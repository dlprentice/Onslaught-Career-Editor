#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen22 remaining OPEN residuals: partial data-shape + honest open.

Exports OPEN_DARK (135) and OPEN_EXECUTED (4) from Generation 22.

OPEN_DARK lane PARTIAL_DATA_SHAPE_COMPOSE (extends Gen21 data-shape):
  greedy full cover with pad + code-ptr tables + float + SSE/const +
  INDEX_OR_BYTE_TABLE (relaxed: allows sparse 0x90 cells, max non-pad ≤0x90)
  + SHORT_DATA_TAIL (1–15B after a data terminal; non-control, max≤0x90).

Terminals:
  TERMINAL_BOUNDED_AMBIGUITY for all multi-kind / short-tail mixes
  TERMINAL_DATA only for pure single data-kind spans (none expected here
  if Gen21 already closed pure SSE).

OPEN_EXECUTED: freeze honest OPEN with cheapest falsifiers (no new shape
terminals without TTD unit split).

Does **not** mutate Gen22/Gen21/Gen10. Does **not** invent names or
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

SCHEMA = "bea.re.open-residual-gen22-partial-data.v1"
PACK_SCHEMA = "bea.re.open-residual-gen22-partial-data-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_PARTIAL_DATA.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 135
EXPECTED_OPEN_EXECUTED = 4
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN22 = Path(
    "local-lab/residual-terminal-generation22-data-shape-20260805-v1/"
    "generation-22-residual-terminal-data-shape"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen22-partial-data-20260805-v1")

PAD_KINDS = {
    "TINY_PAD_GAP",
    "ALIGN_PAD_PREFIX",
    "MSVC_ALIGN_NOP_RUN",
}
DATA_KINDS = {
    "CODE_ADDRESS_TABLE_PREFIX",
    "FLOAT32_TABLE_PREFIX",
    "SSE_OR_CONST_POOL",
    "INDEX_OR_BYTE_TABLE",
    "SHORT_DATA_TAIL",
    "INT16_QUANT_TABLE",
}

DEFAULT_FALSIFIER = (
    "PE byte change; partial data-shape re-check fails; short tail gains "
    "control flow; residual membership of a named function body; "
    "REBUILD_READY claim"
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


def index_full_or_none(blob: bytes, md, mass) -> bool:
    """Full-span relaxed INDEX_OR_BYTE_TABLE (allows sparse pad cells)."""
    if not blob or len(blob) < 16:
        return False
    # reject control-dense code
    insns = list(md.disasm(blob, 0x1000))
    n_ret = sum(1 for i in insns if i.mnemonic in {"ret", "retn"})
    n_call = sum(1 for i in insns if i.mnemonic == "call")
    n_ctrl = sum(1 for i in insns if i.mnemonic in mass.CONTROL)
    if n_ret >= 1 and n_ctrl >= 2:
        return False
    if n_call >= 2:
        return False
    a, cpr = mass.best_code_ptr_run(blob)
    if cpr >= 16:
        return False
    if mass.float_run(blob) >= 32:
        return False
    printable = sum(1 for b in blob if 32 <= b < 127) / len(blob)
    if printable >= 0.55:
        return False
    small = sum(1 for b in blob if b <= 0x40) / len(blob)
    uniq = len(set(blob))
    nonpad = [b for b in blob if b not in (0x00, 0x90, 0xCC)]
    if not nonpad:
        return False
    max_np = max(nonpad)
    if small >= 0.80 and uniq <= max(32, len(blob) // 4) and max_np <= 0x50:
        return True
    le31 = sum(1 for b in blob if b <= 0x31) / len(blob)
    if le31 >= 0.85 and uniq <= max(40, len(blob) // 3) and max_np <= 0x90:
        return True
    usable = len(blob) - (len(blob) % 4)
    if usable >= 16:
        dwords = usable // 4
        low = sum(
            1
            for i in range(0, usable, 4)
            if struct.unpack_from("<I", blob, i)[0] <= 0xFFFF
        )
        if low / dwords >= 0.80 and uniq / len(blob) <= 0.55:
            return True
    return False


def short_data_tail_ok(blob: bytes, md, mass) -> bool:
    """1–15B tail after data: non-control, max≤0x90."""
    if not blob or not (1 <= len(blob) <= 15):
        return False
    if any(b > 0x90 for b in blob):
        return False
    insns = list(md.disasm(blob, 0x1000))
    if any(i.mnemonic in {"ret", "retn", "call", "jmp"} for i in insns):
        return False
    n_ctrl = sum(1 for i in insns if i.mnemonic in mass.CONTROL)
    if n_ctrl >= 1:
        return False
    return True


def compose_partial_data(
    blob: bytes, base: int, md, mass, inb, large_mod, ds_mod
) -> dict[str, Any] | None:
    """Greedy full-cover; skip residuals already closed by Gen21 strict compose."""
    if not blob or len(blob) < 16:
        return None
    if is_pad(blob, mass, inb):
        return None
    # must NOT be Gen21-strict recoverable (those already applied)
    if ds_mod.compose_data_shape(blob, base, md, mass, inb, large_mod):
        return None

    pos = 0
    terms: list[dict[str, Any]] = []
    saw_data = False
    guard = 0
    while pos < len(blob) and guard < 500:
        guard += 1
        rest = blob[pos:]
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
            break

        lead = ds_mod.leading_pad_len(rest, mass, inb)
        if lead >= 1 and lead < len(rest):
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
            continue

        align, cpr = mass.best_code_ptr_run(rest)
        if cpr >= 32:
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
                continue
            ok = True
            for i in range(0, cpr, 4):
                v = struct.unpack_from("<I", rest, i)[0]
                if not (TEXT_LO <= v < TEXT_HI):
                    ok = False
                    break
            if not ok:
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
            saw_data = True
            continue

        fr = mass.float_run(rest)
        if fr >= 32:
            terms.append(
                {
                    "kind": "FLOAT32_TABLE_PREFIX",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + fr:08x}",
                    "bytes": fr,
                }
            )
            pos += fr
            saw_data = True
            continue

        sse = large_mod.sse_const_pool_run(rest)
        if sse >= 32:
            terms.append(
                {
                    "kind": "SSE_OR_CONST_POOL",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + sse:08x}",
                    "bytes": sse,
                }
            )
            pos += sse
            saw_data = True
            continue

        if index_full_or_none(rest, md, mass):
            terms.append(
                {
                    "kind": "INDEX_OR_BYTE_TABLE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
            saw_data = True
            break

        iq = large_mod.int16_quant_like_run(rest)
        if iq >= 128:
            terms.append(
                {
                    "kind": "INT16_QUANT_TABLE",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + pos + iq:08x}",
                    "bytes": iq,
                }
            )
            pos += iq
            saw_data = True
            continue

        # short data tail only after at least one data kind
        if saw_data and short_data_tail_ok(rest, md, mass):
            terms.append(
                {
                    "kind": "SHORT_DATA_TAIL",
                    "startVa": f"0x{base + pos:08x}",
                    "endVa": f"0x{base + len(blob):08x}",
                    "bytes": len(rest),
                }
            )
            pos = len(blob)
            break

        return None

    if pos != len(blob) or not terms or not saw_data:
        return None

    kinds = [t["kind"] for t in terms]
    if not any(k in DATA_KINDS for k in kinds):
        return None

    return {
        "lane": "PARTIAL_DATA_SHAPE_COMPOSE",
        "terms": terms,
        "kinds": kinds,
        "shapeKind": "+".join(kinds),
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "classification": "DATA_OR_MIXED_SHAPE",
        "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        "note": f"n_terms={len(terms)} kinds={'+'.join(kinds)}",
    }


def recheck_terms(
    blob: bytes, base: int, terms: list[dict], md, mass, inb, large_mod
) -> bool:
    for t in terms:
        lo = int(t["startVa"], 16) - base
        hi = int(t["endVa"], 16) - base
        if lo < 0 or hi > len(blob) or hi <= lo:
            return False
        piece = blob[lo:hi]
        k = t["kind"]
        if k in PAD_KINDS:
            if not is_pad(piece, mass, inb):
                return False
        elif k == "CODE_ADDRESS_TABLE_PREFIX":
            if len(piece) < 32 or len(piece) % 4:
                return False
            for i in range(0, len(piece), 4):
                v = struct.unpack_from("<I", piece, i)[0]
                if not (TEXT_LO <= v < TEXT_HI):
                    return False
        elif k == "FLOAT32_TABLE_PREFIX":
            if mass.float_run(piece) < 32:
                return False
        elif k == "SSE_OR_CONST_POOL":
            run = large_mod.sse_const_pool_run(piece)
            if run < 32 or run < len(piece):
                return False
        elif k == "INDEX_OR_BYTE_TABLE":
            if not index_full_or_none(piece, md, mass):
                return False
        elif k == "INT16_QUANT_TABLE":
            if large_mod.int16_quant_like_run(piece) < len(piece):
                return False
        elif k == "SHORT_DATA_TAIL":
            if not short_data_tail_ok(piece, md, mass):
                return False
        else:
            return False
    return True


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": rec["classification"],
        "classificationVerdict": "STATIC_PARTIAL_DATA_SHAPE_COMPOSE",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
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

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 22:
        raise SystemExit(f"expected Gen22, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_DATA_SHAPE":
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
        rec = compose_partial_data(
            blob, start, md, mass, inb, large_mod, ds_mod
        )
        if rec is None or not recheck_terms(
            blob, start, rec["terms"], md, mass, inb, large_mod
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
                        "No partial data-shape full cover; false-decode CODE_LIKE "
                        "without table/index/SSE compose; need inbound ownership, "
                        "TTD, or residual-split policy"
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
                "proposedTerminalState": prop["terminalState"],
                "entityKey": r.get("entityKey") or "",
            }
        )
        lane_counts[prop["recoveryLane"]] += 1

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
        if prop.get("terminalState") != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if prop.get("contractState") == "REBUILD_READY":
            hard.append(f"rebuild {p['startVa']}")
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
        "campaignGeneration": 22,
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
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen22.",
            f"Partial data-shape proofs: {len(proofs)} (all TERMINAL_BOUNDED_AMBIGUITY).",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            "No EXECUTED promotions; no CODE envelope kinds.",
            "Question supersession required for all proofs.",
            "No Gen22 ledger mutation; Gen23 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY / CALL entry",
            "Partial data-shape is static PE table/index/const only",
            "SHORT_DATA_TAIL is residual-row shape only (≤15B after data)",
            "OPEN_EXECUTED fragments frozen OPEN with falsifiers",
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
        "campaignGeneration": 22,
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
            "Gen23 apply only if READY and proofs > 0",
            "Remaining OPEN_DARK: inbound/TTD or residual-split policy",
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
        "schema": "bea.re.open-residual-gen22-partial-data.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_135": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_4": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "no_code_envelope_terms": all(
                "ENVELOPE" not in (p.get("subspanKinds") or "")
                and "STATIC_CODE" not in (p.get("subspanKinds") or "")
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen23_apply": True,
            "no_executed_proofs": pack["n_executed_proofs"] == 0,
            "only_new_vs_gen21_strict": True,
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
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen22: 135/4",
            "Re-run build: proof set must match",
            "Gen22 residuals sha must equal ledger_sha_pre",
            "Any CODE envelope kind; any EXECUTED proof",
        ],
    }
    integrity["checks"]["gen22_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen22_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen22 OPEN residual partial data-shape

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK: **{EXPECTED_OPEN_DARK}** → proofs **{len(pack['proofs'])}**
OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}** → proofs **0**
Still open: dark **{len(result['still_dark'])}**, executed **{len(result['still_exec'])}**

## Non-claims
- Not Gen23 applied
- Not names / not REBUILD_READY / not CALL entry
- Partial data-shape is static table/index/const only
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
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            raise SystemExit(f"non-dark {p['startVa']}")
        if "ENVELOPE" in (p.get("subspanKinds") or "") or "STATIC_CODE" in (
            p.get("subspanKinds") or ""
        ):
            raise SystemExit(f"code launder {p['startVa']}")
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
    print("OPEN_RESIDUAL_GEN22_PARTIAL_DATA_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN22)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN22)
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
        print("OPEN_RESIDUAL_GEN22_PARTIAL_DATA_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
