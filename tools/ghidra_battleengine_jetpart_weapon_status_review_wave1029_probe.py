#!/usr/bin/env python3
"""Validate Wave1029 BattleEngine JetPart weapon/status read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1029-battleengine-jetpart-weapon-status-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_jetpart_weapon_status_review_wave1029_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1029_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
JETPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineJetPart.cpp" / "_index.md"
WALKERPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified"

TARGETS = {
    "0x00411e70": (
        "CBattleEngineJetPart__ChangeWeapon",
        "void __thiscall CBattleEngineJetPart__ChangeWeapon(void * this)",
        ("CBattleEngineJetPart::ChangeWeapon", "clearing slow movement", "auto-zooming"),
    ),
    "0x00412000": (
        "CBattleEngineJetPart__LoseWeaponCharge",
        "void __thiscall CBattleEngineJetPart__LoseWeaponCharge(void * this)",
        ("CBattleEngine::Morph", "+0x57c", "+0x60 charge/progress"),
    ),
    "0x00412050": (
        "CBattleEngineJetPart__WeaponFired",
        "int __thiscall CBattleEngineJetPart__WeaponFired(void * this, void * weapon)",
        ("CBattleEngine__CanSpawnBurstForResolvedEntry", "ret 0x4", "stealth reset identity"),
    ),
    "0x004121b0": (
        "CBattleEngineJetPart__GetWeaponAmmoPercentage",
        "float __thiscall CBattleEngineJetPart__GetWeaponAmmoPercentage(void * this)",
        ("CBattleEngine__GetWeaponAmmoPercentage", "+0x52c", "+0x88"),
    ),
    "0x004122b0": (
        "CBattleEngineJetPart__IsEnergyWeapon",
        "int __thiscall CBattleEngineJetPart__IsEnergyWeapon(void * this)",
        ("JetPart IsEnergyWeapon", "+0x55c", "stale IsWeaponOverheated"),
    ),
    "0x00412310": (
        "CBattleEngineJetPart__IsWeaponOverheated",
        "int __thiscall CBattleEngineJetPart__IsWeaponOverheated(void * this)",
        ("JetPart IsWeaponOverheated", "+0x544", "stale IsEnergyWeapon"),
    ),
    "0x00412370": (
        "CBattleEngineJetPart__GetWeaponCharge",
        "float __thiscall CBattleEngineJetPart__GetWeaponCharge(void * this)",
        ("CBattleEngine__GetWeaponCharge", "+0x60 progress", "threshold bucket"),
    ),
    "0x00412480": (
        "CBattleEngineJetPart__GetWeaponPhysicsName",
        "char * __thiscall CBattleEngineJetPart__GetWeaponPhysicsName(void * this)",
        ("CBattleEngine__GetWeaponPhysicsName", "+0x00", "GetWeaponPhysicsName"),
    ),
    "0x004124d0": (
        "CBattleEngineJetPart__GetCurrentWeaponNameField04",
        "char * __thiscall CBattleEngineJetPart__GetCurrentWeaponNameField04(void * this)",
        ("CBattleEngine__ChangeWeapon", "+0x04", "runtime audio behavior"),
    ),
    "0x00412520": (
        "CBattleEngineJetPart__GetWeaponIconName",
        "char * __thiscall CBattleEngineJetPart__GetWeaponIconName(void * this)",
        ("CBattleEngine__GetWeaponIconName", "+0x38", "GetWeaponIconName"),
    ),
    "0x00412570": (
        "CBattleEngineJetPart__CanWeaponFire",
        "int __thiscall CBattleEngineJetPart__CanWeaponFire(void * this)",
        ("ammo/heat/overheat gates", "stealth reset identity", "fire-while-cloaked"),
    ),
    "0x00412610": (
        "CBattleEngineJetPart__GetCurrentWeapon",
        "void * __thiscall CBattleEngineJetPart__GetCurrentWeapon(void * this)",
        ("selected index", "current weapon pointer", "GetCurrentWeapon"),
    ),
    "0x00412650": (
        "CBattleEngineJetPart__ResetConfiguration",
        "void __thiscall CBattleEngineJetPart__ResetConfiguration(void * this)",
        ("CBattleEngineJetPart::ResetConfiguration", "config +0x50", "current weapon index"),
    ),
}

CONTEXT_TARGETS = {
    "0x00409e80": "CBattleEngine__AutoZoomOut",
    "0x00409f70": "CBattleEngine__ChangeWeapon",
    "0x0040a580": "CBattleEngine__Morph",
    "0x00410210": "CBattleEngineJetPart__ctor",
    "0x004102a0": "CBattleEngineJetPart__dtor_base",
    "0x0040c2e0": "CBattleEngine__CanSpawnBurstForResolvedEntry",
    "0x00413eb0": "CBattleEngineWalkerPart__ChangeWeapon",
    "0x004140d0": "CBattleEngineWalkerPart__WeaponFired",
    "0x004146b0": "CBattleEngineWalkerPart__ResetConfiguration",
    "0x005068f0": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x00506930": "CWeapon__HandleFireBurstEvent",
}

DOC_TOKENS = (
    "Wave1029",
    "battleengine-jetpart-weapon-status-review-wave1029",
    "0x00411e70 CBattleEngineJetPart__ChangeWeapon",
    "0x00412050 CBattleEngineJetPart__WeaponFired",
    "0x004122b0 CBattleEngineJetPart__IsEnergyWeapon",
    "0x00412310 CBattleEngineJetPart__IsWeaponOverheated",
    "0x00412650 CBattleEngineJetPart__ResetConfiguration",
    "618/1408 = 43.89%",
    "847/1493 = 56.73%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    JETPART_DOC: (
        "Wave1029",
        "battleengine-jetpart-weapon-status-review-wave1029",
        "0x00411e70 CBattleEngineJetPart__ChangeWeapon",
        "0x00412050 CBattleEngineJetPart__WeaponFired",
        "0x00412650 CBattleEngineJetPart__ResetConfiguration",
        BACKUP_PATH,
    ),
    BATTLEENGINE_DOC: (
        "Wave1029",
        "battleengine-jetpart-weapon-status-review-wave1029",
        "0x00409f70 CBattleEngine__ChangeWeapon",
        "0x0040c2e0 CBattleEngine__CanSpawnBurstForResolvedEntry",
        "0x00506930 CWeapon__HandleFireBurstEvent",
        BACKUP_PATH,
    ),
    WALKERPART_DOC: (
        "Wave1029",
        "battleengine-jetpart-weapon-status-review-wave1029",
        "0x004140d0 CBattleEngineWalkerPart__WeaponFired",
        "0x004146b0 CBattleEngineWalkerPart__ResetConfiguration",
        BACKUP_PATH,
    ),
}

OVERCLAIMS = (
    "runtime firing behavior proven",
    "runtime charging behavior proven",
    "runtime stealth behavior proven",
    "weapon_fire_breaks_stealth proven",
    "exact layout proven",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 13,
        "tags.tsv": 13,
        "xrefs.tsv": 19,
        "instructions.tsv": 790,
        "decompile/index.tsv": 13,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 20,
        "context-instructions.tsv": 1583,
        "context-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")
    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        require(address in xref_targets, f"missing xrefs for {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=13 found=13 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "xrefs.log": "Wrote 19 rows",
        "instructions.log": "Wrote 790 function-body instruction rows",
        "decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "context-xrefs.log": "Wrote 20 rows",
        "context-instructions.log": "Wrote 1583 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    bad_tokens = ("LockException", "Traceback", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1")
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-battleengine-jetpart-weapon-status-review-wave1029")
        == r"py -3 tools\ghidra_battleengine_jetpart_weapon_status_review_wave1029_probe.py --check",
        "missing Wave1029 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1029-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1029 --check",
        "missing Wave1029 aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1029 BattleEngine JetPart weapon status review" for row in ledger_rows), "missing Wave1029 ledger row", failures)
    require(
        any(row.get("task") == "Wave1029 BattleEngine JetPart weapon status review" and row.get("attempt_id") == 20611 for row in attempts),
        "missing Wave1029 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1029 BattleEngine JetPart weapon/status probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1029 BattleEngine JetPart weapon/status probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
