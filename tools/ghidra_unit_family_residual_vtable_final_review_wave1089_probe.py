#!/usr/bin/env python3
"""Validate Wave1089 unit-family residual vtable boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1089-unit-family-residual-vtable-final-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_family_residual_vtable_final_review_wave1089_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1089_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified"
WAVE_TAG = "unit-family-residual-vtable-final-review-wave1089"

TARGETS = {
    "0x00489ed0": ("CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0", "float __thiscall CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0(void * this)", "0x005e2710"),
    "0x004bfc50": ("SharedUnitVFunc__ReturnFloat005d85cc_004bfc50", "float __thiscall SharedUnitVFunc__ReturnFloat005d85cc_004bfc50(void * this)", "0x005dffc8"),
    "0x004d35d0": ("CPodVFunc__FlagArg70AndSeedMotion250_004d35d0", "void __thiscall CPodVFunc__FlagArg70AndSeedMotion250_004d35d0(void * this, void * arg)", "0x005dffb0"),
    "0x004d3650": ("CPodVFunc__InitializeVector7cWhenField250Clear_004d3650", "void __thiscall CPodVFunc__InitializeVector7cWhenField250Clear_004d3650(void * this)", "0x005e009c"),
    "0x004d3890": ("CPodVFunc__ForwardArgWithFlag00200000_004d3890", "void __thiscall CPodVFunc__ForwardArgWithFlag00200000_004d3890(void * this, int value)", "0x005e0024"),
    "0x004d38b0": ("CPodVFunc__ReturnFloat005d8580_004d38b0", "float __thiscall CPodVFunc__ReturnFloat005d8580_004d38b0(void * this)", "0x005e0040"),
    "0x004dbc20": ("SharedUnitVFunc__ReturnInt5_004dbc20", "int __thiscall SharedUnitVFunc__ReturnInt5_004dbc20(void * this)", "0x005e2700"),
    "0x004dedc0": ("CSentinelVFunc__BuildDispatchArgsFromField220_004dedc0", "void __thiscall CSentinelVFunc__BuildDispatchArgsFromField220_004dedc0(void * this, void * arg)", "0x005e0aa4"),
    "0x004deec0": ("CSentinelVFunc__BuildField164ContextAndDispatch_004deec0", "void __thiscall CSentinelVFunc__BuildField164ContextAndDispatch_004deec0(void * this)", "0x005e0a5c"),
    "0x004dfc60": ("CSimpleBuildingVFunc__ResetVectorAndDispatchSlot70_004dfc60", "void __thiscall CSimpleBuildingVFunc__ResetVectorAndDispatchSlot70_004dfc60(void * this)", "0x005dfe4c"),
    "0x004dfcc0": ("CSimpleBuildingVFunc__ReturnFlag2cFloat005d8bbcOrZero_004dfcc0", "float __thiscall CSimpleBuildingVFunc__ReturnFlag2cFloat005d8bbcOrZero_004dfcc0(void * this)", "0x005dfdf0"),
    "0x004eee80": ("CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80", "void __thiscall CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80(void * this)", "0x005e1598"),
    "0x004ef070": ("CSubmarineVFunc__IsField250NonNull_004ef070", "int __thiscall CSubmarineVFunc__IsField250NonNull_004ef070(void * this)", "0x005e1634"),
    "0x004ef080": ("CSubmarineVFunc__ResetField14cCopyField114To120_004ef080", "void __thiscall CSubmarineVFunc__ResetField14cCopyField114To120_004ef080(void * this)", "0x005e1590"),
    "0x004f84b0": ("CGroundUnitVFunc__ReturnFloat005d8604_004f84b0", "float __thiscall CGroundUnitVFunc__ReturnFloat005d8604_004f84b0(void * this)", "0x005e3310"),
    "0x0050e870": ("CAirUnitVFunc__ForwardArgWithFlags40000400_0050e870", "void __thiscall CAirUnitVFunc__ForwardArgWithFlags40000400_0050e870(void * this, int value)", "0x005e3810"),
    "0x0050e890": ("CAirUnitVFunc__ReturnFloat005d85ec_0050e890", "float __thiscall CAirUnitVFunc__ReturnFloat005d85ec_0050e890(void * this)", "0x005e375c"),
    "0x0050e940": ("CGroundUnitVFunc__ReturnFloat005d85bc_0050e940", "float __thiscall CGroundUnitVFunc__ReturnFloat005d85bc_0050e940(void * this)", "0x005e3334"),
    "0x0050e9d0": ("CInfantryUnitVFunc__GetClassNameString_0050e9d0", "char * __thiscall CInfantryUnitVFunc__GetClassNameString_0050e9d0(void * this)", "0x005e2748"),
    "0x0050e9e0": ("CInfantryUnitVFunc__ForwardArgWithFlags40004200_0050e9e0", "void __thiscall CInfantryUnitVFunc__ForwardArgWithFlags40004200_0050e9e0(void * this, int value)", "0x005e27c4"),
    "0x0050ea00": ("CInfantryUnitVFunc__ReturnField260Float_0050ea00", "float __thiscall CInfantryUnitVFunc__ReturnField260Float_0050ea00(void * this)", "0x005e278c"),
    "0x0050eb50": ("CSubmarineVFunc__GetClassNameString_0050eb50", "char * __thiscall CSubmarineVFunc__GetClassNameString_0050eb50(void * this)", "0x005e14ac"),
    "0x0050eb70": ("CSubmarineVFunc__ForwardArgWithFlags50108000_0050eb70", "void __thiscall CSubmarineVFunc__ForwardArgWithFlags50108000_0050eb70(void * this, int value)", "0x005e1528"),
    "0x0050eb90": ("CSubmarineVFunc__ReturnField164B4Float_0050eb90", "float __thiscall CSubmarineVFunc__ReturnField164B4Float_0050eb90(void * this)", "0x005e14cc"),
    "0x0050ec60": ("CSentinelVFunc__GetClassNameString_0050ec60", "char * __thiscall CSentinelVFunc__GetClassNameString_0050ec60(void * this)", "0x005e08fc"),
    "0x0050ec70": ("CSentinelVFunc__ForwardArgWithFlags40140220_0050ec70", "void __thiscall CSentinelVFunc__ForwardArgWithFlags40140220_0050ec70(void * this, int value)", "0x005e0978"),
    "0x0050ecf0": ("CPodVFunc__GetClassNameString_0050ecf0", "char * __thiscall CPodVFunc__GetClassNameString_0050ecf0(void * this)", "0x005dffa8"),
    "0x0050ed00": ("CSimpleBuildingVFunc__GetClassNameString_0050ed00", "char * __thiscall CSimpleBuildingVFunc__GetClassNameString_0050ed00(void * this)", "0x005dfd58"),
    "0x0050ed30": ("CGroundUnitVFunc__GetClassNameString_0050ed30", "char * __thiscall CGroundUnitVFunc__GetClassNameString_0050ed30(void * this)", "0x005e32f0"),
    "0x0050ed40": ("CGroundUnitVFunc__ForwardArgWithFlags40000200_0050ed40", "void __thiscall CGroundUnitVFunc__ForwardArgWithFlags40000200_0050ed40(void * this, int value)", "0x005e336c"),
    "0x0050f120": ("CAirUnitVFunc__GetClassNameString_0050f120", "char * __thiscall CAirUnitVFunc__GetClassNameString_0050f120(void * this)", "0x005e3794"),
    "0x0050fca0": ("CGillMHeadVFunc__IsField1f4NonNull_0050fca0", "int __thiscall CGillMHeadVFunc__IsField1f4NonNull_0050fca0(void * this)", "0x005e439c"),
    "0x0050fcd0": ("CGillMHeadVFunc__ReturnField26cSlot3cOrFallbackFloat_0050fcd0", "float __thiscall CGillMHeadVFunc__ReturnField26cSlot3cOrFallbackFloat_0050fcd0(void * this)", "0x005e4234"),
    "0x0050fd00": ("CGillMHeadVFunc__GetClassNameString_0050fd00", "char * __thiscall CGillMHeadVFunc__GetClassNameString_0050fd00(void * this)", "0x005e4214"),
    "0x0050fd10": ("CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10", "void __thiscall CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10(void * this, int value)", "0x005e4290"),
}

STRING_EXPECTATIONS = {
    "string-0063d804.tsv": "CInfantryUnit",
    "string-0063d850.tsv": "CSubmarine",
    "string-0063d888.tsv": "CSentinel",
    "string-0063d8b8.tsv": "CPod",
    "string-0063d8c0.tsv": "CSimpleBuilding",
    "string-0063d8d0.tsv": "CGroundUnit",
    "string-0063d8e8.tsv": "CAirUnit",
    "string-0063d9d8.tsv": "CGillMHead",
}

COMMON_TAGS = {
    "static-reaudit",
    WAVE_TAG,
    "wave1089-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "function-boundary-recovered",
    "vtable-boundary",
    "unit-family-vtable",
}

DOC_TOKENS = (
    "Wave1089",
    WAVE_TAG,
    "0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0",
    "0x004d35d0 CPodVFunc__FlagArg70AndSeedMotion250_004d35d0",
    "0x004deec0 CSentinelVFunc__BuildField164ContextAndDispatch_004deec0",
    "0x004eee80 CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80",
    "0x0050e9d0 CInfantryUnitVFunc__GetClassNameString_0050e9d0",
    "0x0050fd10 CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10",
    "1580",
    "20",
    "1527/1560 = 97.88%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof complete",
    "rebuild parity proven",
    "fully reverse-engineered",
    "exact source-layout identity proven",
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=35 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=35 skipped=0 created=35 would_create=0 renamed=0 would_rename=0 signature_updated=35 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=35 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-code-metadata.log": "targets=35 found=35 missing=0",
        "post-code-tags.log": "ExportFunctionTagsByAddress complete: rows=35 missing=0",
        "post-code-xrefs.log": "Wrote 70 rows",
        "post-code-body-instructions.log": "Wrote 468 function-body instruction rows",
        "post-code-decompile.log": "targets=35 dumped=35 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=10 rows=1600",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "BADADDR", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1089.log")
    require("total_functions=6410 commented_functions=6410" in quality_log, "quality export count mismatch", failures)


def check_artifacts(failures: list[str]) -> None:
    count_expectations = {
        "pre-code-diagnose.tsv": 35,
        "pre-data-diagnose.tsv": 20,
        "pre-code-xrefs.tsv": 70,
        "pre-code-instructions-around.tsv": 1715,
        "pre-code-instructions-wide.tsv": 6335,
        "pre-vtable-slots.tsv": 1600,
        "post-code-metadata.tsv": 35,
        "post-code-tags.tsv": 35,
        "post-code-xrefs.tsv": 70,
        "post-code-body-instructions.tsv": 468,
        "post-code-decompile/index.tsv": 35,
        "post-vtable-slots.tsv": 1600,
    }
    for relative, expected_count in count_expectations.items():
        require(len(read_tsv(BASE / relative)) == expected_count, f"{relative} row count mismatch", failures)

    for relative, expected_string in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected_string, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-code-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-code-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-code-decompile" / "index.tsv")}
    xrefs: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-code-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)

    for address, (name, signature, primary_xref) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            for token in ("Wave1089 static read-back", primary_xref, "Static retail Ghidra vtable/xref/instruction/string evidence only"):
                require(token in row.get("comment", ""), f"comment token missing at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(COMMON_TAGS.issubset(set(tag_row.get("tags", "").split(";"))), f"tag mismatch at {address}", failures)

        require(decompile.get(address, {}).get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        require(
            any(normalize_address(xref.get("from_addr", "")) == primary_xref for xref in xrefs.get(address, [])),
            f"primary xref mismatch at {address}",
            failures,
        )

    vtable = read_tsv(BASE / "post-vtable-slots.tsv")
    ok_count = sum(1 for row in vtable if row.get("status") == "OK")
    no_fn_count = sum(1 for row in vtable if row.get("status") == "NO_FUNCTION_AT_POINTER")
    require(ok_count == 1580, "post vtable OK count mismatch", failures)
    require(no_fn_count == 20, "post vtable NO_FUNCTION count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["status"] == "PASS", "queue status mismatch", failures)
    require(queue["totalFunctions"] == 6410, "queue total mismatch", failures)
    for key in (
        "legacyWeakNameCount",
        "commentlessFunctionCount",
        "undefinedSignatureCount",
        "paramSignatureCount",
        "uncertainOwnerNameCount",
        "helperAddressNameCount",
        "wrapperAddressNameCount",
    ):
        require(quality[key] == 0, f"queue quality signal mismatch: {key}", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6410, "quality TSV row count mismatch", failures)
    require(sum(1 for row in rows if row.get("comment", "").strip()) == 6410, "quality TSV commented count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        FUNCTION_COVERAGE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-unit-family-residual-vtable-final-review-wave1089")
        == r"py -3 tools\ghidra_unit_family_residual_vtable_final_review_wave1089_probe.py --check",
        "missing Wave1089 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1089-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1089 --check",
        "missing Wave1089 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1089 unit-family residual vtable final review" for row in ledger_rows), "missing Wave1089 ledger row", failures)
    require(any(row.get("task") == "Wave1089 unit-family residual vtable final review" for row in attempt_rows), "missing Wave1089 attempt row", failures)
    tracking = read_json(TRACKING_STATE)
    require(tracking.get("last_completed", {}).get("task") == "Wave1089 unit-family residual vtable final review", "tracking last_completed mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_logs(failures)
    check_artifacts(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1089 unit-family residual vtable final review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1089 unit-family residual vtable final review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
