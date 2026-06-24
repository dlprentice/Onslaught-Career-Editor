#!/usr/bin/env python3
"""Validate Wave1056 BattleEngine Jet/Walker residual review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1056-battleengine-jet-walker-residual-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_jet_walker_residual_review_wave1056_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1056_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
JETPART_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineJetPart.cpp" / "_index.md"
WALKERPART_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
BATTLEENGINE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified"

TARGETS = {
    "0x004114d0": {
        "name": "CBattleEngineJetPart__Gravity",
        "signature": "float __thiscall CBattleEngineJetPart__Gravity(void * this)",
        "comment": ("small gravity factor", "0.0"),
        "decompile": ("+ 0xfc", "_DAT_005d8cb0", "_DAT_005d856c"),
    },
    "0x00411500": {
        "name": "CBattleEngineJetPart__HandleSkimming",
        "signature": "void __thiscall CBattleEngineJetPart__HandleSkimming(void * this)",
        "comment": ("terrain/water-style height", "CBattleEngine__HostileEnvironment"),
        "decompile": ("CBattleEngine__HostileEnvironment", "this + 0x18"),
    },
    "0x004145a0": {
        "name": "CBattleEngineWalkerPart__GetWeaponName",
        "signature": "short * __thiscall CBattleEngineWalkerPart__GetWeaponName(void * this)",
        "comment": ("CText__GetStringById", "language-name"),
        "decompile": ("CBattleEngineWalkerPart__GetCurrentWeapon", "CText__GetStringById", "+ 0x3c"),
    },
    "0x004145d0": {
        "name": "CBattleEngineWalkerPart__GetWeaponPhysicsName",
        "signature": "char * __thiscall CBattleEngineWalkerPart__GetWeaponPhysicsName(void * this)",
        "comment": ("current weapon data name pointer",),
        "decompile": ("CBattleEngineWalkerPart__GetCurrentWeapon", "+ 0xa4"),
    },
    "0x00414610": {
        "name": "CBattleEngineWalkerPart__GetWeaponIconName",
        "signature": "char * __thiscall CBattleEngineWalkerPart__GetWeaponIconName(void * this)",
        "comment": ("+0x38", "icon-name"),
        "decompile": ("CBattleEngineWalkerPart__GetCurrentWeapon", "+ 0x38"),
    },
    "0x00414630": {
        "name": "CBattleEngineWalkerPart__CanWeaponFire",
        "signature": "int __thiscall CBattleEngineWalkerPart__CanWeaponFire(void * this)",
        "comment": ("+0x52c", "+0x55c", "+0x544", "weapon_fire_breaks_stealth"),
        "decompile": ("+ 0x52c", "+ 0x55c", "+ 0x544", "+ 0x4b0", "+ 0x88"),
    },
}

CONTEXT_NAMES = {
    "0x00409f70": "CBattleEngine__ChangeWeapon",
    "0x0040c2e0": "CBattleEngine__CanSpawnBurstForResolvedEntry",
    "0x0040c3c0": "CBattleEngine__GetWeaponAmmoPercentage",
    "0x0040c460": "CBattleEngine__GetWeaponAmmoCount",
    "0x0040c4a0": "CBattleEngine__GetWeaponCharge",
    "0x0040c550": "CBattleEngine__GetWeaponName",
    "0x0040c570": "CBattleEngine__GetWeaponPhysicsName",
    "0x0040c590": "CBattleEngine__GetWeaponIconName",
    "0x00410210": "CBattleEngineJetPart__ctor",
    "0x004102a0": "CBattleEngineJetPart__dtor_base",
    "0x00411e70": "CBattleEngineJetPart__ChangeWeapon",
    "0x00412610": "CBattleEngineJetPart__GetCurrentWeapon",
    "0x00413eb0": "CBattleEngineWalkerPart__ChangeWeapon",
    "0x00414030": "CBattleEngineWalkerPart__GetCurrentWeapon",
}

DOC_TOKENS = (
    "Wave1056",
    "battleengine-jet-walker-residual-review-wave1056",
    "0x004114d0 CBattleEngineJetPart__Gravity",
    "0x00411500 CBattleEngineJetPart__HandleSkimming",
    "0x004145a0 CBattleEngineWalkerPart__GetWeaponName",
    "0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName",
    "0x00414610 CBattleEngineWalkerPart__GetWeaponIconName",
    "0x00414630 CBattleEngineWalkerPart__CanWeaponFire",
    "CBattleEngine__GetWeaponName",
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CText__GetStringById",
    "CBattleEngine__HostileEnvironment",
    "weapon_fire_breaks_stealth",
    "775/1408 = 55.04%",
    "1097/1509 = 72.70%",
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


def decompile_body_text(directory: Path, row: dict[str, str], address: str, name: str) -> str | None:
    for key in ("file", "path", "relative_path", "output_file", "decompile_file"):
        value = row.get(key, "").strip()
        if not value:
            continue
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = directory / candidate
        if candidate.is_file():
            return read_text(candidate)

    expected = directory / f"{address[2:]}_{name}.c"
    if expected.is_file():
        return read_text(expected)

    matches = list(directory.glob(f"{address[2:]}_*.c"))
    if len(matches) == 1:
        return read_text(matches[0])
    return None


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 7,
        "instructions.tsv": 157,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 14,
        "context-tags.tsv": 14,
        "context-xrefs.tsv": 48,
        "context-instructions.tsv": 1142,
        "context-decompile/index.tsv": 14,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    for address, info in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == info["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == info["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in info["comment"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == info["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            body = decompile_body_text(BASE / "decompile", dec, address, info["name"])
            require(body is not None, f"missing decompile body for {address}", failures)
            if body is not None:
                for token in info["decompile"]:
                    require(token in body, f"missing decompile token at {address}: {token}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT_NAMES.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    xref_text = read_text(BASE / "xrefs.tsv")
    for token in (
        "00411500\tCBattleEngineJetPart__HandleSkimming\t004114bd\t00410c50\tCMonitor__UpdateMovementTransitionAndEffects",
        "004145a0\tCBattleEngineWalkerPart__GetWeaponName\t0040c55f\t0040c550\tCBattleEngine__GetWeaponName",
        "004145d0\tCBattleEngineWalkerPart__GetWeaponPhysicsName\t0040c57f\t0040c570\tCBattleEngine__GetWeaponPhysicsName",
        "00414610\tCBattleEngineWalkerPart__GetWeaponIconName\t0040c59f\t0040c590\tCBattleEngine__GetWeaponIconName",
        "00414630\tCBattleEngineWalkerPart__CanWeaponFire\t004065db\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    source_text = "\n".join(
        read_text(path)
        for path in (
            ROOT / "references" / "Onslaught" / "BattleEngineJetPart.cpp",
            ROOT / "references" / "Onslaught" / "BattleEngineWalkerPart.cpp",
            ROOT / "references" / "Onslaught" / "BattleEngine.cpp",
        )
    )
    for token in (
        "CBattleEngineJetPart::Gravity",
        "mMainPart->mEnergy==0",
        "CBattleEngineJetPart::HandleSkimming",
        "mMainPart->HostileEnvironment",
        "CBattleEngineWalkerPart::GetWeaponName",
        "TEXT_DB.GetString(weapon->GetLanguageName())",
        "CBattleEngineWalkerPart::GetWeaponPhysicsName",
        "CBattleEngineWalkerPart::GetWeaponIconName",
        "CBattleEngineWalkerPart::CanWeaponFire",
        "return mWalkerPart->GetWeaponName()",
        "return mJetPart->Gravity()",
    ):
        require(token in source_text, f"missing source token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "xrefs.log": "Wrote 7 rows",
        "instructions.log": "Wrote 157 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=14 found=14 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "context-xrefs.log": "Wrote 48 rows",
        "context-instructions.log": "Wrote 1142 function-body instruction rows",
        "context-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
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
    require(backup.get("totalBytes") == 174656391 or backup.get("totalBytes") == 174656391.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        JETPART_INDEX: (
            "Wave1056",
            "battleengine-jet-walker-residual-review-wave1056",
            "0x004114d0 CBattleEngineJetPart__Gravity",
            "0x00411500 CBattleEngineJetPart__HandleSkimming",
            BACKUP_PATH,
        ),
        WALKERPART_INDEX: (
            "Wave1056",
            "battleengine-jet-walker-residual-review-wave1056",
            "0x004145a0 CBattleEngineWalkerPart__GetWeaponName",
            "0x00414630 CBattleEngineWalkerPart__CanWeaponFire",
            "weapon_fire_breaks_stealth",
            BACKUP_PATH,
        ),
        BATTLEENGINE_INDEX: (
            "Wave1056",
            "battleengine-jet-walker-residual-review-wave1056",
            "CBattleEngine__GetWeaponName",
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            BACKUP_PATH,
        ),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-battleengine-jet-walker-residual-review-wave1056")
        == r"py -3 tools\ghidra_battleengine_jet_walker_residual_review_wave1056_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1056-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1056 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1056 battleengine jet walker residual review" for row in ledger_rows), "missing Wave1056 ledger row", failures)
    require(
        any(row.get("task") == "Wave1056 battleengine jet walker residual review" and row.get("attempt_id") == 20638 for row in attempts),
        "missing Wave1056 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1056 BattleEngine Jet/Walker residual review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1056 BattleEngine Jet/Walker residual review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
