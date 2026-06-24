#!/usr/bin/env python3
"""Validate Wave1020 projectile-burst spawn spine read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1020-projectile-burst-spawn-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_projectile_burst_spawn_spine_review_wave1020_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1020_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
ROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"
SHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Shell.cpp" / "_index.md"
GENERAL_VOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
SENTINEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified"

TARGETS = {
    "0x005069f0": ("ProjectileBurst__SpawnFromCurrentPreset", "int __fastcall ProjectileBurst__SpawnFromCurrentPreset(void * burstContext)"),
    "0x00506010": (
        "ProjectileBurst__SpawnFromPercentBucketFallback",
        "int __fastcall ProjectileBurst__SpawnFromPercentBucketFallback(void * burstContext)",
    ),
    "0x00506930": ("CWeapon__HandleFireBurstEvent", "void __thiscall CWeapon__HandleFireBurstEvent(void * this, void * eventRecord)"),
    "0x004d9f30": (
        "CRound__UpdateEffectTransformByMode_004d9f30",
        "void __thiscall CRound__UpdateEffectTransformByMode_004d9f30(void * this, int effectMode, void * context, void * targetOrOwner)",
    ),
    "0x004df530": ("CShell__CopyResourceNameToInlineBuffer", "void __thiscall CShell__CopyResourceNameToInlineBuffer(void * this, char * resource_name)"),
}

COMMENT_TOKENS = {
    "0x005069f0": ("current-preset projectile-burst", "burstContext +0xa0", "ProjectileBurstCallerBoundary_0044e020", "weapon_fire_breaks_stealth"),
    "0x00506010": ("percent-bucket fallback", "burstContext +0xa4", "event 0x1389", "ProjectileBurstCallerBoundary_004f4920"),
    "0x00506930": ("weapon burst event handler", "event id 0x1389", "current-preset projectile-burst", "not runtime stealth proof"),
    "0x004d9f30": ("Wave495", "RET 0x0c", "CRound-style thiscall", "effect transforms"),
    "0x004df530": ("Wave507", "CShell helper", "RET 0x4", "this+0x110"),
}

EXPECTED_TAG_TOKENS = {
    "0x004d9f30": ("static-reaudit", "round-wave495", "effect-transform", "signature-corrected"),
    "0x004df530": ("static-reaudit", "shell-unit-tail-wave507", "projectile-burst-shell", "stale-owner-corrected"),
}

CONTEXT_TARGETS = {
    "0x005078b0": "ProjectileBurstPreset__GetListEntryIdByIndex",
    "0x005068f0": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x004daa20": "CEngine__FindPresetIndexByName",
    "0x004db150": "CRound__SpawnConfiguredProjectile",
    "0x004dea50": "CSentinel__Init",
    "0x0044e020": "ProjectileBurstCallerBoundary_0044e020",
    "0x004f4920": "ProjectileBurstCallerBoundary_004f4920",
}

DOC_TOKENS = (
    "Wave1020",
    "projectile-burst-spawn-spine-review-wave1020",
    "0x005069f0 ProjectileBurst__SpawnFromCurrentPreset",
    "0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback",
    "0x00506930 CWeapon__HandleFireBurstEvent",
    "0x004d9f30 CRound__UpdateEffectTransformByMode_004d9f30",
    "0x004df530 CShell__CopyResourceNameToInlineBuffer",
    "528/1408 = 37.50%",
    "757/1493 = 50.70%",
    "456/500 = 91.20%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    BATTLEENGINE_DOC: ("Wave1020", "ProjectileBurst__SpawnFromPercentBucketFallback", "CWeapon__HandleFireBurstEvent", "0x005dfc94", BACKUP_PATH),
    ROUND_DOC: ("Wave1020", "CRound__UpdateEffectTransformByMode_004d9f30", "CRound__SpawnConfiguredProjectile", BACKUP_PATH),
    SHELL_DOC: ("Wave1020", "CShell__CopyResourceNameToInlineBuffer", "this+0x110", BACKUP_PATH),
    GENERAL_VOLUME_DOC: ("Wave1020", "ProjectileBurst__SpawnFromPercentBucketFallback", "CGeneralVolume__DispatchMode3BurstProgressAndSpawn", BACKUP_PATH),
    SENTINEL_DOC: ("Wave1020", "ProjectileBurst__SpawnFromPercentBucketFallback", "CSentinel__UpdateFlamethrowers", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime stealth behavior proven",
    "weapon_fire_breaks_stealth proven",
    "runtime projectile behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 5,
        "primary-tags.tsv": 5,
        "primary-xrefs.tsv": 22,
        "primary-instructions.tsv": 1651,
        "primary-decompile/index.tsv": 5,
        "context-metadata.tsv": 7,
        "context-xrefs.tsv": 9,
        "context-instructions.tsv": 970,
        "context-decompile/index.tsv": 7,
        "vtable-005dfc94.tsv": 48,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "primary-metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "primary-tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "primary-decompile" / "index.tsv"), "address")
    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for token in EXPECTED_TAG_TOKENS.get(address, ()):
                require(token in actual_tags, f"missing tag {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(address)
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xref_text = read_text(BASE / "primary-xrefs.tsv") + "\n" + read_text(BASE / "context-xrefs.tsv")
    for token in (
        "00506143",
        "005069b6",
        "0044e093",
        "004f4bd6",
        "00413ce2",
        "00413e9a",
        "005dfc94",
        "005076dc",
        "ProjectileBurstCallerBoundary_0044e020",
        "ProjectileBurstCallerBoundary_004f4920",
        "CRound__SpawnConfiguredProjectile",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    instruction_text = read_text(BASE / "primary-instructions.tsv") + "\n" + read_text(BASE / "context-instructions.tsv")
    for token in (
        "0x00506b75\tCALL\t0x005078b0",
        "0x005076dc\tCALL\t0x004df530",
        "0x00506143\tCALL\t0x005069f0",
        "0x005061ca\tPUSH\t0x1389",
        "0x00506937\tCMP\tword ptr [EAX + 0x4], 0x1389",
        "0x005069b6\tCALL\t0x005069f0",
        "0x005069d7\tPUSH\t0x1389",
        "0x004df54b\tRET\t0x4",
        "0x005078b0\tMOV\tEAX, dword ptr [ECX + 0x4c]",
        "0x0050691a\tTEST\tAH, 0x1",
        "0x0044e093\tCALL\t0x00506010",
        "0x004f4bd6\tCALL\t0x00506010",
    ):
        require(token in instruction_text, f"missing instruction token: {token}", failures)

    vtable_rows = read_tsv(BASE / "vtable-005dfc94.tsv")
    first = vtable_rows[0] if vtable_rows else {}
    second = vtable_rows[1] if len(vtable_rows) > 1 else {}
    require(first.get("slot") == "0" and first.get("ptr") == "00506930", "vtable slot 0 mismatch", failures)
    require(first.get("ptr_name") == "CWeapon__HandleFireBurstEvent", "vtable slot 0 name mismatch", failures)
    require(second.get("slot") == "1" and second.get("ptr_name") == "CWeapon__scalar_deleting_dtor", "vtable slot 1 mismatch", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "primary-metadata.log": "targets=5 found=5 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "primary-xrefs.log": "Wrote 22 rows",
        "primary-instructions.log": "Wrote 1651 function-body instruction rows",
        "primary-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-xrefs.log": "Wrote 9 rows",
        "context-instructions.log": "Wrote 970 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "vtable-005dfc94.log": "DumpPointerTable complete: rows=48",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    quality_rows = rows_by(read_tsv(QUALITY_TSV), "address")
    for address, (name, signature) in TARGETS.items():
        row = quality_rows.get(address)
        require(row is not None, f"missing quality row {address}", failures)
        if row:
            require(row.get("name") == name, f"quality name mismatch {address}", failures)
            require(row.get("signature") == signature, f"quality signature mismatch {address}", failures)
            require(row.get("comment", "").strip(), f"quality comment missing {address}", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-projectile-burst-spawn-spine-review-wave1020")
        == r"py -3 tools\ghidra_projectile_burst_spawn_spine_review_wave1020_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1020-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1020 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1020 projectile-burst spawn spine review" for row in ledger), "missing Wave1020 ledger row", failures)
    require(
        any(row.get("task") == "Wave1020 projectile-burst spawn spine review" and row.get("attempt_id") == 20602 for row in attempts),
        "missing Wave1020 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1020 projectile-burst spawn spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1020 projectile-burst spawn spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
