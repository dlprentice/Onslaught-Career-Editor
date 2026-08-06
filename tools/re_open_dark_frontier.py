#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen12-bound OPEN DARK residual frontier instrument.

Exports the exact OPEN_DARK_RESIDUAL rows from a residual-terminal campaign
(generation 12 by default), re-runs the deeper static MIXED classifiers and
LARGE_MIXED_BLOB segmenter, and freezes a hash-bound MEASURED plate.

Does NOT mutate Gen10/Gen11/Gen12 ledgers. Whole-span terminal candidates are
published for a separate formal-pack + reducer generation only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.open-dark-frontier.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_GEN12_OPEN_DARK = 667
EXPECTED_GEN12_OPEN_EXECUTED = 108
EXPECTED_RESIDUALS = 6117

DEFAULT_GEN12 = Path(
    "local-lab/residual-terminal-generation12-mixed-shape-20260805-v1/"
    "generation-12-residual-terminal-mixed-shape"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/residual-open-dark-frontier-gen12-20260805-v1")
ROOT = Path(__file__).resolve().parents[1]


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


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def export_open_dark(campaign: Path, out_tsv: Path) -> list[dict[str, str]]:
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"unexpected residual count {len(residuals)}")
    open_dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    open_exec = [r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"]
    if len(open_dark) != EXPECTED_GEN12_OPEN_DARK:
        # Allow exact Gen12 pin; fail closed on drift
        raise SystemExit(
            f"OPEN_DARK_RESIDUAL count {len(open_dark)} != {EXPECTED_GEN12_OPEN_DARK}"
        )
    if len(open_exec) != EXPECTED_GEN12_OPEN_EXECUTED:
        raise SystemExit(
            f"OPEN_EXECUTED_RESIDUAL count {len(open_exec)} != {EXPECTED_GEN12_OPEN_EXECUTED}"
        )

    still_open_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "kind",
        "observationState",
        "prevFunc",
        "nextFunc",
        "questionIds",
        "campaignState",
        "classification",
        "terminalState",
        "bytePattern",
        "cheapestFalsifier",
    ]
    rows: list[dict[str, Any]] = []
    for r in open_dark:
        rows.append(
            {
                "entityKey": r.get("entityKey") or "",
                "startVa": r.get("startVa") or "",
                "endVa": r.get("endVa") or "",
                "bytes": r.get("bytes") or "",
                "kind": r.get("classification") or r.get("bytePattern") or "AMBIGUOUS",
                "observationState": r.get("observationState") or "DARK",
                "prevFunc": r.get("prevFunc") or "",
                "nextFunc": r.get("nextFunc") or "",
                "questionIds": r.get("questionIds") or "",
                "campaignState": r.get("campaignState") or "",
                "classification": r.get("classification") or "",
                "terminalState": r.get("terminalState") or "",
                "bytePattern": r.get("bytePattern") or "",
                "cheapestFalsifier": r.get("cheapestFalsifier") or "",
            }
        )
    _write_tsv(out_tsv, still_open_cols, rows)

    # also export executed inventory (no deeper claim; companion frontier)
    exec_cols = still_open_cols
    exec_rows = []
    for r in open_exec:
        exec_rows.append(
            {
                "entityKey": r.get("entityKey") or "",
                "startVa": r.get("startVa") or "",
                "endVa": r.get("endVa") or "",
                "bytes": r.get("bytes") or "",
                "kind": r.get("classification") or "CODE_CANDIDATE",
                "observationState": r.get("observationState") or "EXECUTED",
                "prevFunc": r.get("prevFunc") or "",
                "nextFunc": r.get("nextFunc") or "",
                "questionIds": r.get("questionIds") or "",
                "campaignState": r.get("campaignState") or "",
                "classification": r.get("classification") or "",
                "terminalState": r.get("terminalState") or "",
                "bytePattern": r.get("bytePattern") or "",
                "cheapestFalsifier": r.get("cheapestFalsifier") or "",
            }
        )
    _write_tsv(out_tsv.with_name("open-executed.tsv"), exec_cols, exec_rows)
    return rows


def build_plate(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ready = campaign / "campaign.ready.json"
    if not ready.is_file():
        raise SystemExit(f"missing campaign.ready.json: {ready}")
    ready_obj = json.loads(ready.read_text(encoding="utf-8"))
    if int(ready_obj.get("generation") or 0) != 12:
        raise SystemExit(f"expected generation 12, got {ready_obj.get('generation')}")

    open_tsv = out_dir / "open-dark.tsv"
    open_rows = export_open_dark(campaign, open_tsv)

    deeper = _load_mod("re_residual_open_mixed_deeper", ROOT / "tools" / "re_residual_open_mixed_deeper.py")
    large = _load_mod("re_large_mixed_blob_classify", ROOT / "tools" / "re_large_mixed_blob_classify.py")

    # Deeper wants still-open columns startVa/endVa/kind/prev/next — open-dark.tsv has them
    deeper_result = deeper.analyze_open_mixed(specimen, open_tsv)
    (out_dir / "deeper-full.json").write_text(
        json.dumps(deeper_result, indent=2) + "\n", encoding="utf-8"
    )

    results_list = list(deeper_result.get("rows") or [])
    if len(results_list) != EXPECTED_GEN12_OPEN_DARK:
        raise SystemExit(f"deeper rows {len(results_list)} != {EXPECTED_GEN12_OPEN_DARK}")

    # LARGE_MIXED_BLOB segmenter on deeper plate (write then load via public API)
    spans = large.load_large_mixed_from_deeper(out_dir / "deeper-full.json")
    large_result = large.classify_large_mixed(specimen, spans)
    (out_dir / "large-mixed-full.json").write_text(
        json.dumps(large_result, indent=2) + "\n", encoding="utf-8"
    )

    whole = [r for r in results_list if r.get("wholeSpanTerminal")]
    fully_open = [
        r
        for r in results_list
        if not r.get("wholeSpanTerminal") and int(r.get("terminalBytes") or 0) == 0
    ]
    partial = [
        r
        for r in results_list
        if not r.get("wholeSpanTerminal") and int(r.get("terminalBytes") or 0) > 0
    ]

    # Split whole-span terminals by kind so STATIC_CODE_DECODE_ENVELOPE is
    # never bulk-eligible as residual-terminal padding/data. Code envelopes
    # need function-level adjudication (entry proof), not residual-terminal
    # formal packs.
    PAD_OR_DATA_KINDS = {
        "TINY_PAD_GAP",
        "ALIGN_PAD_PREFIX",
        "FLOAT32_TABLE_PREFIX",
        "CODE_ADDRESS_TABLE_PREFIX",
        "INDEX_OR_BYTE_TABLE",
        "ZERO_RUN_PREFIX",
    }
    CODE_ENVELOPE_KIND = "STATIC_CODE_DECODE_ENVELOPE"

    def _terminal_kinds(r: dict) -> list[str]:
        return [
            s.get("kind") or ""
            for s in (r.get("subspans") or [])
            if s.get("terminal")
        ]

    def _lane_for_whole(r: dict) -> str:
        kinds = set(_terminal_kinds(r))
        if not kinds and r.get("primary") == "TINY_PAD_GAP":
            return "PAD_OR_DATA"
        if CODE_ENVELOPE_KIND in kinds:
            # pure envelope or envelope mixed with pad/table prefixes
            non_code = kinds - {CODE_ENVELOPE_KIND}
            if non_code and non_code <= PAD_OR_DATA_KINDS:
                return "CODE_ENVELOPE_WITH_DATA_PREFIX"
            return "CODE_ENVELOPE"
        if kinds and kinds <= PAD_OR_DATA_KINDS:
            return "PAD_OR_DATA"
        if r.get("primary") == "TINY_PAD_GAP":
            return "PAD_OR_DATA"
        return "OTHER_SHAPE"

    candidate_rows = []
    envelope_rows = []
    pad_data_rows = []
    terminal_bytes_by_kind: Counter = Counter()
    for r in results_list:
        for s in r.get("subspans") or []:
            if s.get("terminal"):
                terminal_bytes_by_kind[s.get("kind") or ""] += int(s.get("bytes") or 0)

    for r in whole:
        kinds = _terminal_kinds(r)
        lane = _lane_for_whole(r)
        # Only pure pad/data whole spans are residual-terminal formal-pack eligible.
        pack_eligible = lane == "PAD_OR_DATA"
        row = {
            "startVa": r.get("startVa"),
            "endVa": r.get("endVa"),
            "bytes": r.get("bytes"),
            "primary": r.get("primary"),
            "prevFunc": r.get("prevFunc"),
            "nextFunc": r.get("nextFunc"),
            "terminalBytes": r.get("terminalBytes"),
            "subspanKinds": ";".join(kinds),
            "candidateLane": lane,
            "formalPackEligible": "True" if pack_eligible else "False",
            "note": (
                "pad/data shape terminal only; needs formal pack + question supersession"
                if pack_eligible
                else "CODE envelope shape — NOT residual-terminal formal-pack eligible; needs entry/function adjudication"
            ),
        }
        candidate_rows.append(row)
        if pack_eligible:
            pad_data_rows.append(row)
        elif lane.startswith("CODE_ENVELOPE"):
            envelope_rows.append(row)

    cand_cols = [
        "startVa",
        "endVa",
        "bytes",
        "primary",
        "prevFunc",
        "nextFunc",
        "terminalBytes",
        "subspanKinds",
        "candidateLane",
        "formalPackEligible",
        "note",
    ]
    _write_tsv(out_dir / "whole-span-terminal-candidates.tsv", cand_cols, candidate_rows)
    _write_tsv(out_dir / "formal-pack-eligible-pad-data.tsv", cand_cols, pad_data_rows)
    _write_tsv(out_dir / "code-envelope-candidates.tsv", cand_cols, envelope_rows)

    # size-bucket open mass remaining
    open_bytes = sum(int(r.get("openBytes") or 0) for r in results_list)
    term_bytes = sum(int(r.get("terminalBytes") or 0) for r in results_list)
    primary_counts = Counter(r.get("primary") or "" for r in results_list)
    sub_counts: Counter = Counter()
    for r in results_list:
        for s in r.get("subspans") or []:
            sub_counts[s.get("kind") or ""] += 1

    large_counts = (large_result or {}).get("primary_counts") or (large_result or {}).get(
        "segment_kind_counts"
    ) or {}

    # Join open-dark entity keys for integrity
    entity_by_va = {
        (r["startVa"].lower(), r["endVa"].lower()): r["entityKey"] for r in open_rows
    }
    for r in results_list:
        key = (str(r.get("startVa") or "").lower(), str(r.get("endVa") or "").lower())
        r["entityKey"] = entity_by_va.get(key, "")

    (out_dir / "deeper-rows.json").write_text(
        json.dumps(results_list, indent=2) + "\n", encoding="utf-8"
    )

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 12,
        "campaignReadySha256": _sha(ready),
        "input": {
            "openDarkResiduals": EXPECTED_GEN12_OPEN_DARK,
            "openExecutedResiduals": EXPECTED_GEN12_OPEN_EXECUTED,
            "note": "EXECUTED exported as companion inventory only; deeper pass is DARK-only",
        },
        "counts": {
            "n_open_dark_input": len(results_list),
            "n_whole_span_terminal": len(whole),
            "n_partial_subspan_terminal": len(partial),
            "n_still_fully_open": len(fully_open),
            "terminal_bytes_accounted": term_bytes,
            "terminal_bytes_by_kind": dict(terminal_bytes_by_kind),
            "open_bytes_remaining": open_bytes,
            "primaryCounts": dict(primary_counts),
            "subspanKindCounts": dict(sub_counts),
            "largeMixed": large_counts,
            "wholeSpanByLane": dict(Counter(r["candidateLane"] for r in candidate_rows)),
            "formalPackEligiblePadData": len(pad_data_rows),
            "codeEnvelopeCandidates": len(envelope_rows),
            "formalPackWholeSpanCandidates": len(pad_data_rows),
        },
        "claims": [
            f"Exported exactly {EXPECTED_GEN12_OPEN_DARK} Gen12 OPEN_DARK_RESIDUAL rows and re-classified them with deeper static MIXED detectors.",
            f"Whole-span shape terminals: {len(whole)}; partial subspan terminals: {len(partial)}; still fully open: {len(fully_open)}.",
            f"Bytes: terminal accounted {term_bytes} (by kind: {dict(terminal_bytes_by_kind)}); open remaining {open_bytes}.",
            f"Formal-pack ELIGIBLE pad/data whole-span candidates: {len(pad_data_rows)} (not applied).",
            f"CODE_ENVELOPE whole-span shapes quarantined from residual-terminal pack: {len(envelope_rows)} (need entry/function adjudication).",
            "Companion open-executed.tsv lists 108 OPEN_EXECUTED_RESIDUAL rows without claiming new terminals.",
            "No Gen10/Gen11/Gen12 residual ledger mutation.",
        ],
        "non_claims": [
            "Whole-span shape marks are static accounting only — not residual-row campaign terminals until formal pack + reducer.",
            "STATIC_CODE_DECODE_ENVELOPE is NOT residual TERMINAL_PADDING and is not formal-pack eligible here.",
            "Does not invent function names or REBUILD_READY contracts.",
            "Does not reclassify EXECUTED open-boundary as padding/data.",
            "Does not mutate campaign-residuals.tsv.",
        ],
        "cheapestNext": [
            "Build formal residual-terminal pack ONLY from formal-pack-eligible-pad-data.tsv (tiny pad / data tables)",
            "CODE envelopes: entry/fallthrough/call-context adjudication, not residual-terminal bulk",
            "Segment remaining LARGE_MIXED_BLOB / CODE_LIKE_PARTIAL with xref or coverage join",
            "EXECUTED: TTD call-context on PROLOGUE_LIKE subset from fallthrough plate",
        ],
        "artifacts": [
            "open-dark.tsv",
            "open-executed.tsv",
            "deeper-full.json",
            "deeper-rows.json",
            "large-mixed-full.json",
            "whole-span-terminal-candidates.tsv",
            "formal-pack-eligible-pad-data.tsv",
            "code-envelope-candidates.tsv",
            "SUMMARY.json",
            "INTEGRITY.json",
            "README.md",
        ],
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    integrity = {
        "schema": "bea.re.open-dark-frontier.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_input_667": len(results_list) == EXPECTED_GEN12_OPEN_DARK,
            "open_dark_export_667": len(open_rows) == EXPECTED_GEN12_OPEN_DARK,
            "specimen_pristine": _sha(specimen) == SPECIMEN_SHA256,
            "campaign_generation_12": int(ready_obj.get("generation") or 0) == 12,
            "partition_whole_partial_open": (
                len(whole) + len(partial) + len(fully_open) == len(results_list)
            ),
            "no_ledger_mutation": True,
        },
        "sources": {
            "campaignReady": _stamp(ready),
            "campaignResiduals": _stamp(campaign / "campaign-residuals.tsv"),
            "specimen": _stamp(specimen),
            "openDarkTsv": _stamp(open_tsv),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "wholeSpanCandidates": _stamp(out_dir / "whole-span-terminal-candidates.tsv"),
            "formalPackEligiblePadData": _stamp(out_dir / "formal-pack-eligible-pad-data.tsv"),
            "codeEnvelopeCandidates": _stamp(out_dir / "code-envelope-candidates.tsv"),
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign-functions.tsv": _sha(campaign / "campaign-functions.tsv"),
            "campaign.ready.json": _sha(ready),
        },
        "falsifier": [
            "Re-export OPEN_DARK from Gen12: count must be 667",
            "Re-run tools/re_open_dark_frontier.py build: counts must match SUMMARY",
            "campaign-residuals.tsv sha must equal ledger_sha_pre after build",
            "Any STATIC_CODE_DECODE_ENVELOPE row with formalPackEligible=True",
        ],
    }
    # Gate: no code envelope may be formal-pack eligible
    integrity["checks"]["no_code_envelope_formal_pack_eligible"] = all(
        r.get("formalPackEligible") != "True" for r in envelope_rows
    )
    integrity["checks"]["pad_data_eligible_subset"] = all(
        r.get("formalPackEligible") == "True" for r in pad_data_rows
    )
    # re-check ledger unchanged
    integrity["checks"]["gen12_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"]["gen12_residuals_unchanged"]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")

    (out_dir / "README.md").write_text(
        f"""# Gen12 OPEN DARK residual frontier

Status: **MEASURED**  
Schema: `{SCHEMA}`  
Campaign: Gen12 residual-terminal mixed-shape (classification authority for residual terminals)

## Headline

| Metric | Value |
|--------|------:|
| OPEN DARK input | {len(results_list)} |
| Whole-span shape terminals | {len(whole)} |
| Formal-pack **eligible** pad/data | {len(pad_data_rows)} |
| CODE_ENVELOPE (quarantined) | {len(envelope_rows)} |
| Partial subspan terminals | {len(partial)} |
| Still fully open | {len(fully_open)} |
| Terminal bytes accounted | {term_bytes} |
| Terminal bytes by kind | `{dict(terminal_bytes_by_kind)}` |
| Open bytes remaining | {open_bytes} |

## Lanes

- `formal-pack-eligible-pad-data.tsv` — only residual-terminal formal-pack lane
- `code-envelope-candidates.tsv` — STATIC_CODE_DECODE_ENVELOPE; **not** residual TERMINAL_PADDING
- `whole-span-terminal-candidates.tsv` — union with `candidateLane` + eligibility flags

## Non-claims

- Not a campaign generation advance
- Not name promotion
- CODE envelopes are shape-only and require entry/function adjudication
- Formal pack required before any residual-row terminal bulk apply

## Next

1. Formal pack from `formal-pack-eligible-pad-data.tsv` only
2. CODE envelopes: fallthrough / call-context / entry proof
3. LARGE / CODE_LIKE residual instruments for the fully-open mass
4. EXECUTED: PROLOGUE_LIKE call-context (companion `open-executed.tsv`)
""",
        encoding="utf-8",
    )
    return summary


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    pre = integrity.get("ledger_sha_pre") or {}
    for name, sha in pre.items():
        path = campaign / name if name.endswith(".tsv") or name.endswith(".json") else None
        if name == "campaign.ready.json":
            path = campaign / "campaign.ready.json"
        elif name == "campaign-residuals.tsv":
            path = campaign / "campaign-residuals.tsv"
        elif name == "campaign-functions.tsv":
            path = campaign / "campaign-functions.tsv"
        if path is None or not path.is_file():
            raise SystemExit(f"missing ledger {name}")
        live = _sha(path)
        if live != sha:
            raise SystemExit(f"ledger mutated {name}: plate={sha} live={live}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    # re-export count
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    open_dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    if len(open_dark) != EXPECTED_GEN12_OPEN_DARK:
        raise SystemExit(f"open dark count drift: campaign={len(open_dark)}")
    if summary["counts"]["n_open_dark_input"] != EXPECTED_GEN12_OPEN_DARK:
        raise SystemExit("summary open dark != 667")
    if summary["counts"]["n_open_dark_input"] != len(open_dark):
        raise SystemExit(
            f"summary/campaign open-dark mismatch: "
            f"summary={summary['counts']['n_open_dark_input']} campaign={len(open_dark)}"
        )
    # Re-check envelope quarantine on published candidates
    cands = _read_tsv(plate / "whole-span-terminal-candidates.tsv")
    for row in cands:
        kinds = (row.get("subspanKinds") or "").split(";")
        if "STATIC_CODE_DECODE_ENVELOPE" in kinds and row.get("formalPackEligible") == "True":
            raise SystemExit(
                f"code envelope formal-pack eligible at {row.get('startVa')}"
            )
    print(json.dumps({"status": "VERIFIED", "counts": summary["counts"]}, indent=2))
    print("OPEN_DARK_FRONTIER_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN12)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN12)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        summary = build_plate(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        print(json.dumps({"status": "OK", "counts": summary["counts"]}, indent=2))
        print("OPEN_DARK_FRONTIER_OK")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
