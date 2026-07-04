#!/usr/bin/env python3
"""Validate Wave1097 CUnit destructor/thunk lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1097-cunit-dtor-thunk-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_dtor_thunk_lifecycle_review_wave1097_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1097_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified"
WAVE_TAG = "cunit-dtor-thunk-lifecycle-review-wave1097"

TARGETS = {
    "0x004bfe00": (
        "CUnit__dtor_base_Thunk_004bfe00",
        "void __fastcall CUnit__dtor_base_Thunk_004bfe00(void * this)",
        ("Wave460", "jump thunk", "CUnit__dtor_base"),
    ),
    "0x004f84c0": (
        "CUnit__VFunc01_ScalarDeletingDtor",
        "void * __thiscall CUnit__VFunc01_ScalarDeletingDtor(void * this, byte flags)",
        ("Wave526", "scalar-deleting destructor-style", "CDXMemoryManager__Free"),
    ),
    "0x004f84e0": (
        "CUnit__dtor_base",
        "void __fastcall CUnit__dtor_base(void * this)",
        ("Wave477", "ParticleEffectLink__SetHandleStateAndClear", "CActor__dtor_base"),
    ),
    "0x0050ee90": (
        "CUnit__scalar_deleting_dtor",
        "void * __thiscall CUnit__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave460", "CUnit__dtor_base_Thunk_004bfe00", "RET 0x4"),
    ),
    "0x004f95d0": (
        "CUnit__VFunc02_CleanupWorldLinksAndForward",
        "void __fastcall CUnit__VFunc02_CleanupWorldLinksAndForward(void * this)",
        ("Wave526", "CComplexThing__Shutdown", "runtime cleanup order"),
    ),
    "0x004fcfa0": (
        "CUnit__ClearSpawnerSet",
        "void __fastcall CUnit__ClearSpawnerSet(void * this)",
        ("Wave525", "active reader", "+0x18c"),
    ),
    "0x004fcfe0": (
        "CUnit__ReleaseChildUnits",
        "void __fastcall CUnit__ReleaseChildUnits(void * this)",
        ("Wave525", "child reader nodes", "+0x19c"),
    ),
    "0x004fd040": (
        "CUnit__ResetDeploymentGraphAndScheduleEvent",
        "void __fastcall CUnit__ResetDeploymentGraphAndScheduleEvent(void * this)",
        ("Wave525", "CExplosionInitThing__ctor_like_004fd230", "event 2000"),
    ),
    "0x004fd140": (
        "CUnit__MarkDestroyedAndCleanupLinks",
        "int __fastcall CUnit__MarkDestroyedAndCleanupLinks(void * this)",
        ("Wave525", "destroyed flag bit 2", "script event id 5"),
    ),
    "0x004cb0b0": (
        "ParticleEffectLink__SetHandleStateAndClear",
        "void __thiscall ParticleEffectLink__SetHandleStateAndClear(void * this, int set_state_one)",
        ("Wave477", "owner-link cell", "old CUnit owner is too narrow"),
    ),
    "0x004013d0": (
        "CActor__dtor_base",
        "void __fastcall CActor__dtor_base(void * this)",
        ("Actor destructor-base", "CComplexThing__dtor_base"),
    ),
    "0x004f3f00": (
        "CComplexThing__dtor_base",
        "void __fastcall CComplexThing__dtor_base(void * this)",
        ("Wave517", "CComplexThing destructor-base", "CThing destructor-base"),
    ),
}

COMMON_DOC_TOKENS = (
    "Wave1097",
    WAVE_TAG,
    "0x004bfe00 CUnit__dtor_base_Thunk_004bfe00",
    "0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor",
    "0x004f84e0 CUnit__dtor_base",
    "0x0050ee90 CUnit__scalar_deleting_dtor",
    "0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward",
    "0x004fcfa0 CUnit__ClearSpawnerSet",
    "0x004fcfe0 CUnit__ReleaseChildUnits",
    "0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent",
    "0x004fd140 CUnit__MarkDestroyedAndCleanupLinks",
    "0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear",
    "0x004013d0 CActor__dtor_base",
    "0x004f3f00 CComplexThing__dtor_base",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-body identity proven",
    "exact source layout identity proven",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 190,
        "instructions.tsv": 656,
        "decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            if actual_tags:
                require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
                require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 190 rows",
        "instructions.log": "Wrote 656 function-body instruction rows",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (175541127, 175541127.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        UNIT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cunit-dtor-thunk-lifecycle-review-wave1097")
        == r"py -3 tools\ghidra_cunit_dtor_thunk_lifecycle_review_wave1097_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1097-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1097 --check",
        "missing aggregate package script",
        failures,
    )

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1097 CUnit destructor thunk lifecycle review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1097 CUnit destructor thunk lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1097 CUnit destructor thunk lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
