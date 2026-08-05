#!/usr/bin/env python3
"""Join OPEN EXECUTED residuals to existing TTD coverage + static callback-slot evidence.

For each campaign residual with observationState=EXECUTED:

  1. Coverage join — bytes of [start,end) present in a union of existing
     coverage.jsonl indexes (discover under G:/bea-ttd and local-lab).
  2. Callback-slot / CALL-reg join — re_callreg_imm_peephole.analyze over the
     residual start VA as candidate (imm32 install / near CALL-reg).
  3. Absolute-pointer inbound — image dwords equal to start (or interior) from
     .text/.rdata (not .data, to reduce coincidence).
  4. Envelope pilot grade — optional prior ENVELOPE.json spanSummaries.

Grades (conservative, no names):

  CALLBACK_SLOT_INSTALL   imm32(=entry) written to memory (slot fill)
  CALL_REG_NEAR_IMM       CALL reg near imm32(=entry)
  SLOT_CONSUMER_NEAR_IMM  CALL [mem] near non-install imm
  ABS_PTR_TEXT_RDATA      abs image dword in .text/.rdata points at entry/span
  TRACE_EXECUTED_CORROBORATED  coverage union covers ≥1 byte (and residual already EXECUTED)
  TRACE_EXECUTED_LEDGER_ONLY   residual EXECUTED but zero coverage hits in joined indexes
  STILL_OPEN_NO_INBOUND    no slot/call/abs evidence beyond execution

Does not invent names. Does not mutate Gen10/Gen11 ledgers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# Import shipped helpers (no reimplementation of classify algorithms)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_callreg_imm_peephole as callreg  # noqa: E402
import re_coverage_ledger as cov  # noqa: E402


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    import csv

    return list(csv.DictReader(rows, delimiter="\t"))


def pe_map(data: bytes):
    return callreg.pe_map(data)


def va_to_off(va: int, image_base: int, sections):
    return callreg.va_to_off(va, image_base, sections)


def load_executed_residuals(campaign_residuals: Path) -> list[dict]:
    rows = _read_tsv(campaign_residuals)
    return [r for r in rows if r.get("observationState") == "EXECUTED"]


def build_coverage_union(roots: list[Path], limit: int | None = None) -> tuple[object, list[dict]]:
    """Load and merge coverage.jsonl indexes from discoverable roots."""
    paths: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        paths.extend(cov.discover_coverage_indexes([root]))
    paths = sorted(set(paths), key=lambda p: str(p))
    if limit is not None:
        paths = paths[:limit]
    all_ranges = []
    stamps = []
    for path in paths:
        try:
            loaded = cov.load_coverage_index(path)
            # load_coverage_index returns (ranges, meta)
            ranges = loaded[0] if isinstance(loaded, tuple) else loaded
        except Exception as exc:  # noqa: BLE001 — skip bad indexes, record
            stamps.append({"path": str(path), "error": str(exc)})
            continue
        all_ranges.extend(ranges)
        stamps.append(
            {
                "path": str(path),
                "sha256": cov.sha256_of(path),
                "bytes": path.stat().st_size,
                "nRangesRaw": len(ranges),
            }
        )
    index = cov.CoverageIndex(all_ranges)
    return index, stamps


def abs_ptr_inbound_text_rdata(
    data: bytes,
    image_base: int,
    sections,
    spans: list[tuple[int, int, str]],
) -> dict[str, list[dict]]:
    """Absolute image dwords in .text/.rdata pointing into residual spans."""
    # interval index
    spans = sorted(spans)
    by_start = {s: (s, e, key) for s, e, key in spans}

    def find_span(va: int):
        lo, hi = 0, len(spans)
        while lo < hi:
            mid = (lo + hi) // 2
            a, b, key = spans[mid]
            if va < a:
                hi = mid
            elif va >= b:
                lo = mid + 1
            else:
                return a, b, key
        return None

    hits: dict[str, list[dict]] = defaultdict(list)
    for name, sva, vsize, rawptr, rawsize in sections:
        if name not in (".text", ".rdata"):
            continue
        sec = data[rawptr : rawptr + rawsize]
        base = image_base + sva
        for off in range(0, len(sec) - 3, 4):
            val = struct.unpack_from("<I", sec, off)[0]
            hit = find_span(val)
            if hit is None:
                continue
            a, b, key = hit
            src = base + off
            if a <= src < b:
                continue  # interior self-ref
            hits[key].append(
                {
                    "srcVa": f"0x{src:08x}",
                    "targetVa": f"0x{val:08x}",
                    "section": name,
                }
            )
    return hits


def envelope_grades(envelope_json: Path | None) -> dict[str, dict]:
    if envelope_json is None or not envelope_json.is_file():
        return {}
    data = json.loads(envelope_json.read_text(encoding="utf-8"))
    out = {}
    for s in data.get("spanSummaries") or []:
        key = s.get("startVa", "").lower()
        out[key] = {
            "anyProved": s.get("anyProved"),
            "gradeCounts": s.get("gradeCounts") or {},
            "externalCallEdgesIntoSpan": s.get("externalCallEdgesIntoSpan"),
            "absolutePtrCountIntoSpan": s.get("absolutePtrCountIntoSpan"),
            "prevBodyEndsAtSpanStart": s.get("prevBodyEndsAtSpanStart"),
            "bestCandidates": s.get("bestCandidates") or [],
        }
    return out


def grade_row(
    *,
    residual: dict,
    callreg_grade: str | None,
    callreg_detail: dict | None,
    abs_hits: list[dict],
    cov_bytes: int,
    env: dict | None,
) -> dict:
    start = residual["startVa"]
    end = residual["endVa"]
    nbytes = int(residual.get("bytes") or "0")
    obs = int(residual.get("observedBytes") or "0")
    reasons = []
    primary = "STILL_OPEN_NO_INBOUND"

    if callreg_grade == "CALLBACK_SLOT_INSTALL":
        primary = "CALLBACK_SLOT_INSTALL"
        reasons.append("imm32(=entry) installed via mov [mem],imm32")
    elif callreg_grade == "CALL_REG_NEAR_IMM":
        primary = "CALL_REG_NEAR_IMM"
        reasons.append("CALL reg near imm32(=entry)")
    elif callreg_grade == "SLOT_CONSUMER_NEAR_IMM":
        primary = "SLOT_CONSUMER_NEAR_IMM"
        reasons.append("CALL [mem] near imm32(=entry)")
    elif callreg_grade and callreg_grade not in ("NO_IMM", "IMM_ONLY_NO_NEAR_CALL", None):
        primary = callreg_grade
        reasons.append(f"callreg grade {callreg_grade}")

    if abs_hits and primary == "STILL_OPEN_NO_INBOUND":
        primary = "ABS_PTR_TEXT_RDATA"
        reasons.append(f"{len(abs_hits)} abs dword(s) in .text/.rdata into span")
    elif abs_hits:
        reasons.append(f"also {len(abs_hits)} abs dword(s) .text/.rdata")

    if cov_bytes > 0:
        if primary == "STILL_OPEN_NO_INBOUND":
            primary = "TRACE_EXECUTED_CORROBORATED"
        reasons.append(f"coverage_union covers {cov_bytes}/{nbytes} bytes")
    else:
        if primary == "STILL_OPEN_NO_INBOUND":
            primary = "TRACE_EXECUTED_LEDGER_ONLY"
        reasons.append("coverage_union covers 0 bytes (ledger EXECUTED only)")

    if env:
        if env.get("prevBodyEndsAtSpanStart"):
            reasons.append("FALLTHROUGH_AFTER_PREV_RET")
        gc = env.get("gradeCounts") or {}
        if gc:
            reasons.append("envelope:" + ",".join(f"{k}={v}" for k, v in gc.items()))

    falsifiers = {
        "CALLBACK_SLOT_INSTALL": (
            "Show the imm32 site is not a slot fill, or that the residual entry is never "
            "loaded/called from that slot under controlled runtime."
        ),
        "CALL_REG_NEAR_IMM": (
            "Show CALL-reg does not target the residual entry (different reg/value) at runtime."
        ),
        "SLOT_CONSUMER_NEAR_IMM": (
            "Show CALL [mem] does not load the residual entry address."
        ),
        "ABS_PTR_TEXT_RDATA": (
            "Show the absolute dword is not a live code pointer (constant collision) "
            "or is never used as a control-flow target."
        ),
        "TRACE_EXECUTED_CORROBORATED": (
            "Independent disassembly + call-graph: prove interior fragment / shared tail / "
            "fallthrough rather than a discrete function entry (lever already names this)."
        ),
        "TRACE_EXECUTED_LEDGER_ONLY": (
            "Re-run coverage join on the full corpus; if still 0 covered bytes, refute the "
            "EXECUTED ledger bit or name the missing coverage index."
        ),
        "STILL_OPEN_NO_INBOUND": (
            "Find any inbound E8/CALL-reg/slot install/abs consumer or prove non-entry fragment."
        ),
    }

    return {
        "startVa": start,
        "endVa": end,
        "bytes": nbytes,
        "observedBytesLedger": obs,
        "coverageBytesJoined": cov_bytes,
        "coverageFrac": round(cov_bytes / nbytes, 4) if nbytes else 0.0,
        "entityKey": residual.get("entityKey", ""),
        "prevFunc": residual.get("prevFunc", ""),
        "nextFunc": residual.get("nextFunc", ""),
        "questionIds": residual.get("questionIds", ""),
        "callregGrade": callreg_grade,
        "callregDetail": callreg_detail,
        "absPtrHitsTextRdata": abs_hits[:8],
        "nAbsPtrHitsTextRdata": len(abs_hits),
        "envelope": env,
        "joinGrade": primary,
        "reasons": reasons,
        "cheapestFalsifier": falsifiers.get(primary, falsifiers["STILL_OPEN_NO_INBOUND"]),
        "terminalCandidate": primary
        in ("CALLBACK_SLOT_INSTALL", "CALL_REG_NEAR_IMM", "SLOT_CONSUMER_NEAR_IMM"),
        "namePromotion": False,
    }


def run_join(
    *,
    specimen: Path,
    campaign_residuals: Path,
    gen10_functions: Path | None,
    envelope_json: Path | None,
    coverage_roots: list[Path],
    coverage_limit: int | None,
    window: int,
) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")

    residuals = load_executed_residuals(campaign_residuals)
    if not residuals:
        raise SystemExit("no EXECUTED residuals in campaign ledger")

    # Coverage union
    cov_index, cov_stamps = build_coverage_union(coverage_roots, limit=coverage_limit)
    image_base, sections = pe_map(data)

    # Candidates = residual starts
    candidates = [int(r["startVa"], 16) for r in residuals]
    callreg_result = callreg.analyze(
        specimen,
        candidates,
        window,
        gen10_functions if gen10_functions and gen10_functions.is_file() else None,
    )
    # map candidate VA -> grade row (candidateVa is hex string)
    callreg_by_va: dict[int, dict] = {}
    for row in callreg_result.get("rows") or []:
        va = row.get("candidateVa") or row.get("candidate") or row.get("va")
        if isinstance(va, str):
            va = int(va, 16)
        if va is not None:
            callreg_by_va[int(va)] = row

    # Build abs ptr hits for all spans
    spans = [
        (int(r["startVa"], 16), int(r["endVa"], 16), r["startVa"].lower())
        for r in residuals
    ]
    abs_map = abs_ptr_inbound_text_rdata(data, image_base, sections, spans)
    env_map = envelope_grades(envelope_json)

    # RVA conversion for coverage: coverage indexes typically use RVA
    # re_coverage_ledger load uses RVAs; residual VAs need - image_base
    rows_out = []
    for r in residuals:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        lo_rva, hi_rva = start - image_base, end - image_base
        cov_bytes = int(cov_index.covered_in(lo_rva, hi_rva))
        cr = callreg_by_va.get(start)
        cgrade = None
        if cr:
            cgrade = cr.get("grade") or cr.get("primaryGrade")
        abs_hits = abs_map.get(r["startVa"].lower(), [])
        env = env_map.get(r["startVa"].lower())
        rows_out.append(
            grade_row(
                residual=r,
                callreg_grade=cgrade,
                callreg_detail=cr,
                abs_hits=abs_hits,
                cov_bytes=cov_bytes,
                env=env,
            )
        )

    grades = Counter(r["joinGrade"] for r in rows_out)
    summary = {
        "schema": "bea.re.executed-residual-join.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_executed_residuals": len(rows_out),
        "gradeCounts": dict(grades),
        "n_terminal_candidates": sum(1 for r in rows_out if r["terminalCandidate"]),
        "n_coverage_corroborated": sum(
            1 for r in rows_out if r["coverageBytesJoined"] > 0
        ),
        "n_coverage_zero": sum(1 for r in rows_out if r["coverageBytesJoined"] == 0),
        "coverageIndexesUsed": len([s for s in cov_stamps if "error" not in s]),
        "coverageIndexErrors": len([s for s in cov_stamps if "error" in s]),
        "coverageTotalBytesInUnion": cov_index.total(),
        "callregWindow": window,
        "callregSummary": {
            k: callreg_result.get(k)
            for k in (
                "schema",
                "status",
                "gradeCounts",
                "n_callback_install",
                "n_call_reg_near",
                "n_slot_consumer",
                "windowBytes",
            )
            if k in callreg_result
        },
        "envelopePilot": str(envelope_json) if envelope_json else None,
        "non_claims": [
            "No function names invented",
            "No Gen10/Gen11 residual ledger mutation",
            "CALLBACK_SLOT_INSTALL is install-site evidence, not a proved live call",
            "TRACE_EXECUTED_* does not close OPEN_CODE_BOUNDARY alone",
        ],
        "cheapestNextInstrument": (
            "For CALLBACK_SLOT_INSTALL rows: runtime read of slot after install; "
            "for TRACE_EXECUTED_* majority: independent disasm fragment proof + "
            "fallthrough classification; for ABS_PTR_TEXT_RDATA: prove live load."
        ),
    }
    return {
        "summary": summary,
        "rows": rows_out,
        "coverageStamps": cov_stamps,
        }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--campaign-residuals", type=Path, required=True)
    p.add_argument("--gen10-functions-tsv", type=Path, default=None)
    p.add_argument("--envelope-json", type=Path, default=None)
    p.add_argument(
        "--coverage-root",
        type=Path,
        action="append",
        default=None,
        help="Root(s) to discover coverage.jsonl (repeatable). Default: G:/bea-ttd + local-lab",
    )
    p.add_argument(
        "--coverage-limit",
        type=int,
        default=None,
        help="Optional max number of coverage indexes (debug)",
    )
    p.add_argument("--window", type=int, default=48)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)

    roots = args.coverage_root or [Path("G:/bea-ttd"), Path("local-lab")]
    result = run_join(
        specimen=args.specimen,
        campaign_residuals=args.campaign_residuals,
        gen10_functions=args.gen10_functions_tsv,
        envelope_json=args.envelope_json,
        coverage_roots=roots,
        coverage_limit=args.coverage_limit,
        window=args.window,
    )

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary_path = args.json_out.with_name("SUMMARY.json")
    summary_path.write_text(json.dumps(result["summary"], indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print("EXECUTED_RESIDUAL_JOIN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
