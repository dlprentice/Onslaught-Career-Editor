#!/usr/bin/env python3
"""Validate Wave1027 BattleEngine WalkerPart weapon-spine read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1027-battleengine-walkerpart-weapon-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_walkerpart_weapon_spine_review_wave1027_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1027_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
WALKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
WEAPON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified"

TARGETS = {
    "0x00412bc0": ("CBattleEngineWalkerPart__ctor", "void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)", ("ResetConfiguration", "g_dash")),
    "0x00412cf0": ("CBattleEngineWalkerPart__dtor_base", "void __thiscall CBattleEngineWalkerPart__dtor_base(void * this)", ("weapon entries", "primary and augmented")),
    "0x00413cc0": ("CBattleEngineWalkerPart__FireWeapon", "void __thiscall CBattleEngineWalkerPart__FireWeapon(void * this)", ("0x588", "projectile-burst")),
    "0x00413cf0": ("CBattleEngineWalkerPart__ChargeWeapon", "void __thiscall CBattleEngineWalkerPart__ChargeWeapon(void * this)", ("charge/overheat", "projectile-burst")),
    "0x00414030": ("CBattleEngineWalkerPart__GetCurrentWeapon", "void * __thiscall CBattleEngineWalkerPart__GetCurrentWeapon(void * this)", ("primary/augmented", "current index")),
    "0x004140d0": ("CBattleEngineWalkerPart__WeaponFired", "int __thiscall CBattleEngineWalkerPart__WeaponFired(void * this, void * weapon)", ("ret 0x4", "store value/heat/overheat")),
    "0x00414410": ("CBattleEngineWalkerPart__GetWeaponAmmoPercentage", "float __thiscall CBattleEngineWalkerPart__GetWeaponAmmoPercentage(void * this)", ("0x52c", "0x4b0")),
    "0x00414470": ("CBattleEngineWalkerPart__GetWeaponAmmoCount", "int __thiscall CBattleEngineWalkerPart__GetWeaponAmmoCount(void * this)", ("rounded", "non-heat")),
    "0x004144c0": ("CBattleEngineWalkerPart__IsEnergyWeapon", "int __thiscall CBattleEngineWalkerPart__IsEnergyWeapon(void * this)", ("0x55c", "heat flag")),
    "0x004144f0": ("CBattleEngineWalkerPart__IsWeaponOverheated", "int __thiscall CBattleEngineWalkerPart__IsWeaponOverheated(void * this)", ("0x544", "overheat")),
    "0x00414520": ("CBattleEngineWalkerPart__GetWeaponCharge", "float __thiscall CBattleEngineWalkerPart__GetWeaponCharge(void * this)", ("0x60", "charge/progress")),
    "0x004145f0": ("CBattleEngineWalkerPart__GetCurrentWeaponZoomMode", "int __thiscall CBattleEngineWalkerPart__GetCurrentWeaponZoomMode(void * this)", ("zoom-mode", "ChangeWeapon")),
}

CONTEXT_TARGETS = {
    "0x0040a580": "CBattleEngine__Morph",
    "0x00413eb0": "CBattleEngineWalkerPart__ChangeWeapon",
    "0x004146b0": "CBattleEngineWalkerPart__ResetConfiguration",
    "0x005068f0": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x00506930": "CWeapon__HandleFireBurstEvent",
}

EVIDENCE_TOKENS = (
    "ProjectileBurst__SpawnFromPercentBucketFallback",
    "CBattleEngineWalkerPart__GetCurrentWeapon",
    "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "CBattleEngineWalkerPart__ChargeWeapon",
    "CBattleEngineWalkerPart__FireWeapon",
    "00409f5a",
    "00409f01",
    "0040c313",
    "0040c43f",
    "0040c48f",
    "00409ff4",
    "005dfc94",
)

DOC_TOKENS = (
    "Wave1027",
    "battleengine-walkerpart-weapon-spine-review-wave1027",
    "0x00412bc0 CBattleEngineWalkerPart__ctor",
    "0x00413cc0 CBattleEngineWalkerPart__FireWeapon",
    "0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon",
    "0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon",
    "0x004140d0 CBattleEngineWalkerPart__WeaponFired",
    "0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode",
    "600/1408 = 42.61%",
    "829/1493 = 55.53%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    WALKER_DOC: ("Wave1027", "battleengine-walkerpart-weapon-spine-review-wave1027", "0x00413cc0 CBattleEngineWalkerPart__FireWeapon", "0x004140d0 CBattleEngineWalkerPart__WeaponFired", BACKUP_PATH),
    BATTLEENGINE_DOC: ("Wave1027", "battleengine-walkerpart-weapon-spine-review-wave1027", "0x0040a580 CBattleEngine__Morph", "0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode", BACKUP_PATH),
    WEAPON_DOC: ("Wave1027", "battleengine-walkerpart-weapon-spine-review-wave1027", "0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned", "0x00506930 CWeapon__HandleFireBurstEvent", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime firing behavior proven",
    "runtime charge behavior proven",
    "runtime hud behavior proven",
    "weapon_fire_breaks_stealth proven",
    "exact cbattleengine::weaponfired identity proven",
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
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 39,
        "instructions.tsv": 704,
        "decompile/index.tsv": 12,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 13,
        "context-instructions.tsv": 718,
        "context-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context_metadata = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch {address}", failures)

    evidence = "\n".join(
        read_text(BASE / path)
        for path in (
            "xrefs.tsv",
            "context-xrefs.tsv",
            "instructions.tsv",
            "context-instructions.tsv",
        )
    )
    decompile_text = "\n".join(read_text(path) for path in (BASE / "decompile").glob("*.c"))
    context_decompile_text = "\n".join(read_text(path) for path in (BASE / "context-decompile").glob("*.c"))
    all_text = "\n".join((evidence, decompile_text, context_decompile_text))
    for token in EVIDENCE_TOKENS:
        require(token in all_text, f"missing evidence token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 39 rows",
        "instructions.log": "targets=12 missing=0",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "context-xrefs.log": "Wrote 13 rows",
        "context-instructions.log": "targets=5 missing=0",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
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
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-battleengine-walkerpart-weapon-spine-review-wave1027") == r"py -3 tools\ghidra_battleengine_walkerpart_weapon_spine_review_wave1027_probe.py --check", "missing Wave1027 package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1027-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1027 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1027 BattleEngine WalkerPart weapon spine review" for row in ledger_rows), "missing Wave1027 ledger row", failures)
    require(any(row.get("task") == "Wave1027 BattleEngine WalkerPart weapon spine review" and row.get("attempt_id") == 20609 for row in attempts), "missing Wave1027 attempt row", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    check_queue(failures)

    if failures:
        print("Wave1027 BattleEngine WalkerPart weapon-spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1027 BattleEngine WalkerPart weapon-spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
