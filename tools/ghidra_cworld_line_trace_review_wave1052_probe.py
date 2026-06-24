#!/usr/bin/env python3
"""Validate Wave1052 CWorld line-trace review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1052-cworld-line-trace-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_line_trace_review_wave1052_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1052_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
WORLD_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified"
ADDRESS = "0x0050b030"
NAME = "CWorld__FindFirstThingToHitLine"
SIGNATURE = (
    "int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, "
    "undefined4 line_04, undefined4 line_08, undefined4 line_0c, undefined4 line_10, "
    "undefined4 line_14, undefined4 line_18, undefined4 line_1c, undefined4 line_20, "
    "undefined4 line_24, undefined4 line_28, undefined4 line_2c, undefined4 line_30, "
    "void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, "
    "int child_trace_mode, int collision_mode, uint reject_flags, "
    "int heightfield_trace_flags, uint required_thing_flags)"
)

PRIMARY_TAGS = {
    "static-reaudit",
    "cworld",
    "cworld-find-first-thing-to-hit-line-wave843",
    "heightfield",
    "line-trace",
    "mapwho",
    "retail-binary-evidence",
    "signature-hardened",
    "wave843-readback-verified",
}

EXPECTED_XREFS = {
    "0x0053eafb": "CDXEngine__Render",
    "0x0040bf1d": "CBattleEngine__HandleAutoAim",
    "0x00499cfd": "CMCMech__GetFootHeight",
    "0x0040954e": "CMonitor__Process",
    "0x0040b023": "CBattleEngine__CalcUnitOverCrossHair",
    "0x00426be0": "CCollisionSeekingRound__CreateEffect",
    "0x00507ff0": "OID__CanFireAtTarget_BallisticArcA",
    "0x0050856e": "OID__CanFireAtTarget_BallisticArcA",
    "0x005085d9": "OID__CanFireAtTarget_BallisticArcA",
    "0x00508860": "OID__CanFireAtTarget_BallisticArcA",
    "0x005090ea": "OID__CanFireAtTarget_BallisticArcB",
    "0x004f9d03": "CUnit__ApplyDamage",
}

CONTEXT_NAMES = {
    "0x0040acc0": "CBattleEngine__CalcUnitOverCrossHair",
    "0x0040b6d0": "CBattleEngine__HandleAutoAim",
    "0x00490a40": "CHeightField__TraceLineAgainstHeightfield",
    "0x00492110": "CMapWho__GetFirstEntryWithinLine",
    "0x004925a0": "CMapWho__GetNextEntryWithinLine",
    "0x00492c90": "CMapWhoEntry__GetOwner",
    "0x004f3d10": "CThing__GetPersistentCollisionSeekingThing",
    "0x004f9a90": "CUnit__ApplyDamage",
    "0x004fb500": "CUnit__CanFireAtTarget_BallisticArcA",
    "0x004fb5a0": "CUnit__CanFireAtTarget_BallisticArcB",
    "0x00507ab0": "OID__CanFireAtTarget_BallisticArcA",
    "0x005088b0": "OID__CanFireAtTarget_BallisticArcB",
    "0x0053e2e0": "CDXEngine__Render",
}

DOC_TOKENS = (
    "Wave1052",
    "cworld-line-trace-review-wave1052",
    "0x0050b030 CWorld__FindFirstThingToHitLine",
    "CHeightField__TraceLineAgainstHeightfield",
    "CMapWho__GetFirstEntryWithinLine",
    "CMapWho__GetNextEntryWithinLine",
    "CThing__GetPersistentCollisionSeekingThing",
    "CBattleEngine__CalcUnitOverCrossHair",
    "CBattleEngine__HandleAutoAim",
    "CUnit__ApplyDamage",
    "CDXEngine__Render",
    "references/Onslaught/BattleEngine.cpp",
    "references/Onslaught/DXEngine.cpp",
    "references/Onslaught/PCEngine.cpp",
    "745/1408 = 52.91%",
    "1033/1509 = 68.46%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 1,
        "tags.tsv": 1,
        "xrefs.tsv": 12,
        "instructions.tsv": 321,
        "decompile/index.tsv": 1,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 105,
        "context-instructions.tsv": 4547,
        "context-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    row = metadata.get(ADDRESS)
    require(row is not None, "missing primary metadata row", failures)
    if row is not None:
        require(row.get("name") == NAME, "primary name mismatch", failures)
        require(row.get("signature") == SIGNATURE, "primary signature mismatch", failures)
        require(row.get("status") == "OK", "primary metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave843 static read-back/signature/comment hardening",
            "renamed from OID__TraceLineAndSelectBestTargetHit",
            "RET 0x54",
            "CHeightField__TraceLineAgainstHeightfield",
            "CMapWho__GetFirstEntryWithinLine",
            "CMapWho__GetNextEntryWithinLine",
            "CThing__GetPersistentCollisionSeekingThing",
            "stop_on_first_valid_hit",
            "line_00..line_30",
            "runtime collision/targeting behavior",
        ):
            require(token in comment, f"missing primary comment token: {token}", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, "missing primary tags row", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(PRIMARY_TAGS.issubset(actual_tags), f"primary tags missing: {PRIMARY_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "primary tag status mismatch", failures)

    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    dec = decompile.get(ADDRESS)
    require(dec is not None, "missing primary decompile index", failures)
    if dec is not None:
        require(dec.get("name") == NAME, "primary decompile name mismatch", failures)
        require(dec.get("signature") == SIGNATURE, "primary decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "primary decompile status mismatch", failures)

    xrefs = {normalize_address(row["from_addr"]): row for row in read_tsv(BASE / "xrefs.tsv")}
    for from_addr, function_name in EXPECTED_XREFS.items():
        xref = xrefs.get(from_addr)
        require(xref is not None, f"missing xref from {from_addr}", failures)
        if xref is not None:
            require(xref.get("from_function") == function_name, f"xref function mismatch at {from_addr}", failures)
            require(xref.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch at {from_addr}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    context_decompile = {
        normalize_address(row["address"]): row for row in read_tsv(BASE / "context-decompile" / "index.tsv")
    }
    for address, name in CONTEXT_NAMES.items():
        ctx = context.get(address)
        require(ctx is not None, f"missing context metadata for {address}", failures)
        if ctx is not None:
            require(ctx.get("name") == name, f"context name mismatch at {address}", failures)
            require(ctx.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
        dec_ctx = context_decompile.get(address)
        require(dec_ctx is not None, f"missing context decompile for {address}", failures)
        if dec_ctx is not None:
            require(dec_ctx.get("name") == name, f"context decompile name mismatch at {address}", failures)
            require(dec_ctx.get("status") == "OK", f"context decompile status mismatch at {address}", failures)

    body = read_text(BASE / "decompile" / "0050b030_CWorld__FindFirstThingToHitLine.c")
    for token in (
        "CHeightField__TraceLineAgainstHeightfield",
        "CMapWho__GetFirstEntryWithinLine",
        "CMapWho__GetNextEntryWithinLine",
        "CThing__GetPersistentCollisionSeekingThing",
        "stop_on_first_valid_hit",
        "heightfield_trace_flags",
        "required_thing_flags",
        "hit_result",
    ):
        require(token in body, f"missing decompile body token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=1 found=1 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "xrefs.log": "Wrote 12 rows",
        "instructions.log": "Wrote 321 function-body instruction rows",
        "decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "context-xrefs.log": "Wrote 105 rows",
        "context-instructions.log": "Wrote 4547 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_source_and_queue(failures: list[str]) -> None:
    sources = {
        ROOT / "references" / "Onslaught" / "BattleEngine.cpp": (
            "WORLD.FindFirstThingToHitLine(ray, this , &wlcr,FALSE,TRUE, ECL_MESH",
            "WORLD.FindFirstThingToHitLine(ray, this , wlcr,FALSE,inMeshCollision,collisionLevel",
            "WORLD.FindFirstThingToHitLine(line,this,&wlcr,FALSE)==kCollideThing",
        ),
        ROOT / "references" / "Onslaught" / "DXEngine.cpp": (
            "WORLD.FindFirstThingToHitLine(line_of_sight,to_ignore, &wlcr, TRUE)==kCollideNothing",
        ),
        ROOT / "references" / "Onslaught" / "PCEngine.cpp": (
            "WORLD.FindFirstThingToHitLine(line_of_sight,to_ignore, &wlcr, TRUE)==kCollideNothing",
        ),
        ROOT / "references" / "Onslaught" / "InitThing.h": ("ECL_MESH = 2", "kCollideThing"),
    }
    for path, tokens in sources.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"missing source token in {path.relative_to(ROOT)}: {token}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV contains commentless row", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174623623 or backup.get("totalBytes") == 174623623.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        WORLD_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cworld-line-trace-review-wave1052")
        == r"py -3 tools\ghidra_cworld_line_trace_review_wave1052_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1052-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1052 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1052 cworld line trace review" for row in ledger_rows), "missing Wave1052 ledger row", failures)
    require(
        any(row.get("task") == "Wave1052 cworld line trace review" and row.get("attempt_id") == 20634 for row in attempts),
        "missing Wave1052 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_source_and_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1052 CWorld line-trace review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1052 CWorld line-trace review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
