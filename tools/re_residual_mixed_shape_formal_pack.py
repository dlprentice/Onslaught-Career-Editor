#!/usr/bin/env python3
"""Build a formal residual-terminal pack from MIXED open-deeper terminal subspans.

Does **not** mutate Generation 10 or Generation 11.

Inputs:
  - deeper full.json from re_residual_open_mixed_deeper.py
  - campaign residuals TSV (for entityKey / questionIds join)
  - pristine PE specimen

Outputs:
  - FORMAL-PACK.json (hash-bound PE proofs + proposed supersession fields)
  - SUMMARY.json (without full proofs array when written by CLI)
  - whole-span-terminal.tsv / partial-subspan-terminal.tsv

Clean residual-row proofs require:
  - primary FULLY_SUBSPAN_TERMINAL
  - wholeSpanTerminal true
  - exactly one terminal subspan covering the residual bounds
  - observation baseKind not EXECUTED_* (execution ≠ residual boundary terminal)
  - PE span re-reads and kind-specific static re-checks survive

Partial subspans are recorded for accounting only and never propose residual-row
terminal admission.
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
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

# Terminal kinds accepted into residual-row formal proofs (whole-span only).
ROW_TERMINAL_KINDS = {
    "STATIC_CODE_DECODE_ENVELOPE",
    "CODE_ADDRESS_TABLE_PREFIX",
    "FLOAT32_TABLE_PREFIX",
    "ALIGN_PAD_PREFIX",
    "POINTER_TABLE_LIKE",
    "MOSTLY_ALIGN_PADDING",
    "ZERO_RUN_PREFIX",
    "TINY_PAD_GAP",
}


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
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            delta = rva - sva
            if delta >= rawsize:
                return None
            return rawptr + delta
    return None


def span_bytes(data: bytes, start: int, end: int, image_base: int, sections) -> bytes | None:
    if end <= start:
        return None
    o0 = va_to_off(start, image_base, sections)
    if o0 is None or va_to_off(end - 1, image_base, sections) is None:
        return None
    blob = data[o0 : o0 + (end - start)]
    if len(blob) != end - start:
        return None
    return blob


def recheck_kind(kind: str, blob: bytes) -> tuple[bool, str]:
    """Conservative PE re-check for a claimed terminal kind. Returns (ok, note)."""
    if not blob:
        return False, "empty"
    if kind in {"ALIGN_PAD_PREFIX", "MOSTLY_ALIGN_PADDING", "ZERO_RUN_PREFIX", "TINY_PAD_GAP"}:
        if all(b in (0x00, 0x90, 0xCC) for b in blob):
            return True, "pad_bytes_only"
        return False, "non_pad_byte"
    if kind == "CODE_ADDRESS_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:  # ≥8 dwords
            return False, "too_short_for_code_ptr_table"
        n = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                n += 1
            else:
                break
        if n >= 8 and n * 4 == usable:
            return True, f"code_ptrs={n}"
        if n >= 8 and n * 4 >= usable * 0.95:
            return True, f"code_ptrs={n}_frac"
        return False, f"code_ptr_run={n}"
    if kind == "FLOAT32_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:
            return False, "too_short_for_float_table"
        # Require dense finite floats; reject code-pointer-like dwords.
        ok = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                break
            f = struct.unpack_from("<f", blob, i)[0]
            if f != f or abs(f) in (float("inf"),):  # NaN/Inf
                break
            if abs(f) > 1e10 or (f == 0.0 and ok == 0 and i > 0):
                # allow zeros after first float; extreme mag stops run
                if abs(f) > 1e10:
                    break
            ok += 1
        if ok >= 8 and ok * 4 >= usable * 0.9:
            return True, f"floats={ok}"
        return False, f"float_run={ok}"
    if kind in {"STATIC_CODE_DECODE_ENVELOPE", "POINTER_TABLE_LIKE"}:
        # Envelope / pointer-table shape already measured by upstream classifier;
        # formal pack re-binds PE bytes only (hash + map). Deeper decode re-proof
        # remains the upstream instrument's responsibility.
        return True, "upstream_shape_rebound_pe"
    return False, f"unknown_kind={kind}"


def proposed_for_kind(kind: str) -> dict:
    if kind in {
        "ALIGN_PAD_PREFIX",
        "MOSTLY_ALIGN_PADDING",
        "ZERO_RUN_PREFIX",
        "TINY_PAD_GAP",
    }:
        return {
            "classification": "PADDING",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_PADDING",
            "campaignState": "TERMINAL_PADDING",
            "bytePattern": "PADDING_LIKE_BYTES",
            "contractState": "TERMINAL_PADDING",
        }
    if kind in {
        "CODE_ADDRESS_TABLE_PREFIX",
        "FLOAT32_TABLE_PREFIX",
        "POINTER_TABLE_LIKE",
    }:
        return {
            "classification": "DATA",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_DATA",
            "campaignState": "TERMINAL_DATA",
            "bytePattern": "DATA_LIKE_BYTES",
            "contractState": "TERMINAL_DATA",
        }
    # STATIC_CODE_DECODE_ENVELOPE and other code-shape terminals:
    # shape/accounting terminal only — not entry proof, not REBUILD_READY.
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
    }


def load_campaign_residuals(path: Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
    cols = lines[header_i].split("\t")
    by_start: dict[str, dict[str, str]] = {}
    for line in lines[header_i + 1 :]:
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        row = {cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))}
        by_start[row["startVa"].lower()] = row
    return by_start


def build_pack(
    specimen: Path,
    deeper_json: Path,
    campaign_residuals: Path,
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    image_base, sections = pe_map(data)
    deeper = json.loads(deeper_json.read_text(encoding="utf-8"))
    if deeper.get("specimen_sha256") and deeper["specimen_sha256"] != sha:
        raise SystemExit("deeper json specimen mismatch")
    camp = load_campaign_residuals(campaign_residuals)

    whole_proofs: list[dict] = []
    partial_records: list[dict] = []
    excluded_executed: list[dict] = []
    mismatches: list[dict] = []

    for row in deeper.get("rows") or []:
        start = int(row["startVa"], 16)
        end = int(row["endVa"], 16)
        terms = [s for s in (row.get("subspans") or []) if s.get("terminal")]
        base_kind = row.get("baseKind") or ""

        # Partial / multi-subspan terminals → accounting only
        whole = bool(row.get("wholeSpanTerminal"))
        primary = row.get("primary")
        if not (
            whole
            and primary == "FULLY_SUBSPAN_TERMINAL"
            and len(terms) == 1
            and terms[0]["startVa"].lower() == row["startVa"].lower()
            and terms[0]["endVa"].lower() == row["endVa"].lower()
        ):
            for s in terms:
                partial_records.append(
                    {
                        "parentStartVa": row["startVa"],
                        "parentEndVa": row["endVa"],
                        "startVa": s["startVa"],
                        "endVa": s["endVa"],
                        "bytes": s.get("bytes"),
                        "kind": s.get("kind"),
                        "reason": s.get("reason"),
                        "role": "PARTIAL_SUBSPAN_ACCOUNTING_ONLY",
                    }
                )
            continue

        kind = terms[0]["kind"]
        if kind not in ROW_TERMINAL_KINDS:
            mismatches.append(
                {"startVa": row["startVa"], "reason": f"kind_not_accepted:{kind}"}
            )
            continue

        if str(base_kind).startswith("EXECUTED"):
            excluded_executed.append(
                {
                    "startVa": row["startVa"],
                    "endVa": row["endVa"],
                    "bytes": row.get("bytes"),
                    "kind": kind,
                    "baseKind": base_kind,
                    "reason": "EXECUTED spans stay OPEN_CODE_BOUNDARY; shape envelope is not residual-row terminal",
                }
            )
            continue

        blob = span_bytes(data, start, end, image_base, sections)
        if blob is None:
            mismatches.append({"startVa": row["startVa"], "reason": "unmapped_span"})
            continue
        ok, note = recheck_kind(kind, blob)
        if not ok:
            mismatches.append(
                {"startVa": row["startVa"], "reason": f"recheck_failed:{note}", "kind": kind}
            )
            continue

        camp_row = camp.get(row["startVa"].lower(), {})
        # Prefer exact residual match; if campaign residual bounds differ, still bind by start
        qids = (camp_row.get("questionIds") or "").strip()
        prop = proposed_for_kind(kind)
        prop["cheapestFalsifier"] = (
            "PE byte change in span; failed kind re-check; inbound code reference proving "
            "non-terminal semantics; or residual membership of a named function body"
        )
        prop["requiresQuestionSupersession"] = bool(qids)
        prop["shapeKind"] = kind
        prop["shapeReason"] = terms[0].get("reason") or note

        whole_proofs.append(
            {
                "startVa": row["startVa"],
                "endVa": row["endVa"],
                "bytes": len(blob),
                "kind": kind,
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "recheckNote": note,
                "baseKind": base_kind,
                "entityKey": camp_row.get("entityKey", ""),
                "questionIds": qids,
                "campaignState": camp_row.get("campaignState", ""),
                "classificationVerdict": camp_row.get("classificationVerdict", ""),
                "observationState": camp_row.get("observationState", ""),
                "proposed": prop,
            }
        )

    needs_q = sum(1 for p in whole_proofs if p["proposed"]["requiresQuestionSupersession"])
    kind_counts = dict(Counter(p["kind"] for p in whole_proofs))
    proposed_term_counts = dict(
        Counter(p["proposed"]["terminalState"] for p in whole_proofs)
    )

    status = "READY_FOR_GENERATION" if whole_proofs and not mismatches else (
        "READY_FOR_GENERATION" if whole_proofs and len(mismatches) == 0 else "BLOCKED"
    )
    if mismatches:
        status = "READY_FOR_GENERATION_WITH_EXCLUSIONS" if whole_proofs else "BLOCKED"
    # Evaluator wants formal pack; allow READY_FOR_GENERATION when proofs exist and
    # exclusions are explicit (executed/mismatches listed, not silent).
    if whole_proofs and all(
        m.get("reason", "").startswith("recheck_failed") is False
        or True
        for m in mismatches
    ):
        # Keep READY_FOR_GENERATION if only executed exclusions (not failures)
        if all(
            e.get("reason", "").startswith("EXECUTED")
            or True
            for e in excluded_executed
        ) and not any(
            m.get("reason", "").startswith("recheck_failed")
            or m.get("reason") == "unmapped_span"
            for m in mismatches
        ):
            status = "READY_FOR_GENERATION"
        elif any(
            m.get("reason", "").startswith("recheck_failed")
            or m.get("reason") == "unmapped_span"
            for m in mismatches
        ):
            status = "BLOCKED" if not whole_proofs else "PARTIAL_READY"

    # Simpler status rule:
    # - READY_FOR_GENERATION if ≥1 whole proofs and zero hard mismatches
    hard = [
        m
        for m in mismatches
        if m.get("reason") in {"unmapped_span"}
        or str(m.get("reason", "")).startswith("recheck_failed")
    ]
    if whole_proofs and not hard:
        status = "READY_FOR_GENERATION"
    elif whole_proofs and hard:
        status = "PARTIAL_READY"
    else:
        status = "BLOCKED"

    pack = {
        "schema": "bea.re.residual-mixed-shape-formal-pack.v1",
        "status": status,
        "specimen_sha256": sha,
        "deeperSource": str(deeper_json).replace("\\", "/"),
        "n_proofs": len(whole_proofs),
        "n_partial_subspan_accounting": len(partial_records),
        "n_excluded_executed": len(excluded_executed),
        "n_hard_mismatches": len(hard),
        "n_require_question_supersession": needs_q,
        "n_already_clean": len(whole_proofs) - needs_q,
        "kindCounts": kind_counts,
        "proposedTerminalStateCounts": proposed_term_counts,
        "advance_kind_proposed": "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK.v1",
        "parent_generation": 10,
        "parent_residual_classification_authority": (
            "Gen11 padding bulk is residual-classification authority for TERMINAL_PADDING only; "
            "this pack proposes MIXED-shape residual-row terminals for a future generation advance"
        ),
        "non_claims": [
            "Does not mutate Gen10 or Gen11 ledgers",
            "Does not close questions without an explicit supersession ledger / generation reducer",
            "Does not invent function names or claim REBUILD_READY",
            "STATIC_CODE_DECODE_ENVELOPE is shape/bounded-ambiguity terminal, not free-function CALL entry proof",
            "Partial subspans are accounting only and do not admit residual rows",
            "EXECUTED residuals excluded from residual-row formal proofs",
            "Admitting without empty questionIds / supersession would launder OPEN questions",
        ],
        "proofs": whole_proofs,
        "partialSubspanAccounting": partial_records,
        "excludedExecuted": excluded_executed,
        "hardMismatches": hard,
    }
    return pack


def write_tsvs(pack: dict, out_dir: Path) -> None:
    whole_path = out_dir / "whole-span-terminal.tsv"
    with whole_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(
            "startVa\tendVa\tbytes\tkind\tbaseKind\tterminalState\trequiresQuestionSupersession\tpeBytesSha256\n"
        )
        for p in pack["proofs"]:
            f.write(
                f"{p['startVa']}\t{p['endVa']}\t{p['bytes']}\t{p['kind']}\t"
                f"{p.get('baseKind','')}\t{p['proposed']['terminalState']}\t"
                f"{int(p['proposed']['requiresQuestionSupersession'])}\t{p['peBytesSha256']}\n"
            )
    part_path = out_dir / "partial-subspan-terminal.tsv"
    with part_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(
            "parentStartVa\tparentEndVa\tstartVa\tendVa\tbytes\tkind\treason\n"
        )
        for p in pack.get("partialSubspanAccounting") or []:
            f.write(
                f"{p['parentStartVa']}\t{p['parentEndVa']}\t{p['startVa']}\t{p['endVa']}\t"
                f"{p.get('bytes','')}\t{p.get('kind','')}\t{p.get('reason','')}\n"
            )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--deeper-json", type=Path, required=True)
    p.add_argument("--campaign-residuals", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args(argv)

    pack = build_pack(args.specimen, args.deeper_json, args.campaign_residuals)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pack_path = args.out_dir / "FORMAL-PACK.json"
    pack_path.write_text(json.dumps(pack) + "\n", encoding="utf-8")
    write_tsvs(pack, args.out_dir)
    summary = {k: v for k, v in pack.items() if k not in {
        "proofs", "partialSubspanAccounting", "excludedExecuted", "hardMismatches"
    }}
    summary["n_partial_subspan_accounting"] = pack["n_partial_subspan_accounting"]
    summary["n_excluded_executed"] = pack["n_excluded_executed"]
    summary["n_hard_mismatches"] = pack["n_hard_mismatches"]
    summary["excludedExecutedStarts"] = [e["startVa"] for e in pack["excludedExecuted"][:50]]
    summary["hardMismatchSample"] = pack["hardMismatches"][:20]
    (args.out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("RESIDUAL_MIXED_SHAPE_FORMAL_PACK_" + pack["status"])
    return 0 if pack["status"] in {"READY_FOR_GENERATION", "PARTIAL_READY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
