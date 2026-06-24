#!/usr/bin/env python3
"""Validate Wave1088 CRadar / Goodies boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1088-unit-family-residual-vtable-tail-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cradar_goodies_boundary_recovery_wave1088_2026-06-04.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-121500_post_wave1088_cradar_goodies_boundary_recovery_verified"
CRADAR_TAG = "cradar-residual-vtable-tail-wave1088"
GOODIES_TAG = "goodies-autoanalysis-boundary-recovery-wave1088"

CRADAR_TARGETS = {
    "0x004bfb00": (
        "CRadarVFunc__GetClassNameString_004bfb00",
        "char * __thiscall CRadarVFunc__GetClassNameString_004bfb00(void * this)",
        "0x005dd7a4",
        ("CRadar", "0x00630c44"),
    ),
    "0x0052ddb0": (
        "SharedUnitVFunc__ReturnInt10_0052ddb0",
        "int __thiscall SharedUnitVFunc__ReturnInt10_0052ddb0(void * this)",
        "0x005dd7a8",
        ("0x0a", "0x005ddbbc", "0x005e4ca8"),
    ),
    "0x004d6360": (
        "CRadarVFunc__FlagArg70AndSeedMotion280_004d6360",
        "void __thiscall CRadarVFunc__FlagArg70AndSeedMotion280_004d6360(void * this, void * arg)",
        "0x005dd7ac",
        ("arg+0x70", "0x0083c9d8", "this+0x280"),
    ),
    "0x004bfb20": (
        "CRadarVFunc__ReturnFloat005d8bb8_004bfb20",
        "float __thiscall CRadarVFunc__ReturnFloat005d8bb8_004bfb20(void * this)",
        "0x005dd7c8",
        ("0x005d8bb8",),
    ),
    "0x004bfb10": (
        "CRadarVFunc__ForwardArgWithLowFlag20_004bfb10",
        "void __thiscall CRadarVFunc__ForwardArgWithLowFlag20_004bfb10(void * this, int value)",
        "0x005dd820",
        ("0x20", "0x004fcdc0"),
    ),
    "0x004d63c0": (
        "CRadarVFunc__UpdateMotionVector250FromAngle280_004d63c0",
        "void __thiscall CRadarVFunc__UpdateMotionVector250FromAngle280_004d63c0(void * this)",
        "0x005dd890",
        ("this+0x280", "this+0x250..0x278"),
    ),
    "0x004f6560": (
        "CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560",
        "void __thiscall CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560(void * this, void * outTransform)",
        "0x005dd964",
        ("0x008406b8", "output buffer", "12-dword"),
    ),
}

GOODIES_TARGETS = {
    "0x0041c160": (
        "CCareer__GetKillCounterLow24ByType_0041c160",
        "int __thiscall CCareer__GetKillCounterLow24ByType_0041c160(void * this, int killType)",
        ("0x0045a940", "0x00ffffff", "RET 0x4"),
    ),
    "0x0045a940": (
        "CFEPGoodies__BuildGoodieRequirementText_0045a940",
        "void __thiscall CFEPGoodies__BuildGoodieRequirementText_0045a940(void * this, void * outText)",
        ("0x0045e906", "CText__GetStringById", "CCareer__GetKillCounterLow24ByType_0041c160"),
    ),
    "0x0045ff80": (
        "CFEPGoodies__ClassifyGoodieIndexForRender_0045ff80",
        "int __cdecl CFEPGoodies__ClassifyGoodieIndexForRender_0045ff80(int goodieIndex)",
        ("0x0045e930", "goodieIndex <= 7", "0x41"),
    ),
}

COMMON_CRADAR_TAGS = {
    "static-reaudit",
    CRADAR_TAG,
    "wave1088-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "function-boundary-recovered",
    "vtable-boundary",
    "cradar-vtable",
}

COMMON_GOODIES_TAGS = {
    "static-reaudit",
    GOODIES_TAG,
    "wave1088-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "frontend-goodies",
    "goodies-render",
    "autoanalysis-recovery",
}

DOC_TOKENS = (
    "Wave1088",
    CRADAR_TAG,
    GOODIES_TAG,
    "0x004bfb00 CRadarVFunc__GetClassNameString_004bfb00",
    "0x004d6360 CRadarVFunc__FlagArg70AndSeedMotion280_004d6360",
    "0x004f6560 CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560",
    "0x0041c160 CCareer__GetKillCounterLow24ByType_0041c160",
    "0x0045a940 CFEPGoodies__BuildGoodieRequirementText_0045a940",
    "0x0045ff80 CFEPGoodies__ClassifyGoodieIndexForRender_0045ff80",
    "1545",
    "55",
    "1492/1560 = 95.64%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6375/6375 = 100.00%",
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 created=7 would_create=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "goodies-recovery-apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=3 signature_updated=3 comment_only_updated=0 missing=0 bad=0",
        "goodies-recovery-apply.log": "SUMMARY: updated=3 skipped=0 renamed=3 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0",
        "goodies-recovery-apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-body-instructions.log": "Wrote 350 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-goodies-recovery-metadata.log": "targets=3 found=3 missing=0",
        "post-goodies-recovery-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-goodies-recovery-xrefs.log": "Wrote 4 rows",
        "post-goodies-recovery-body-instructions.log": "Wrote 263 function-body instruction rows",
        "post-goodies-recovery-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "BADADDR", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1088.log")
    require("total_functions=6375 commented_functions=6375" in quality_log, "quality export count mismatch", failures)


def check_artifacts(failures: list[str]) -> None:
    count_expectations = {
        "pre-vtable-slots.tsv": 1600,
        "post-vtable-slots.tsv": 1600,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 9,
        "post-body-instructions.tsv": 350,
        "post-decompile/index.tsv": 7,
        "post-goodies-recovery-metadata.tsv": 3,
        "post-goodies-recovery-tags.tsv": 3,
        "post-goodies-recovery-xrefs.tsv": 4,
        "post-goodies-recovery-body-instructions.tsv": 263,
        "post-goodies-recovery-decompile/index.tsv": 3,
    }
    for relative, expected_count in count_expectations.items():
        require(len(read_tsv(BASE / relative)) == expected_count, f"{relative} row count mismatch", failures)

    string_rows = read_tsv(BASE / "string-00630c44.tsv")
    require(string_rows and string_rows[0].get("cstring") == "CRadar", "CRadar string dump mismatch", failures)

    cradar_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    cradar_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    cradar_xrefs: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        cradar_xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)
    cradar_decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, xref, tokens) in CRADAR_TARGETS.items():
        row = cradar_metadata.get(address)
        require(row is not None, f"missing CRadar metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"CRadar name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"CRadar signature mismatch at {address}", failures)
            for token in tokens + (xref,):
                require(token in row.get("comment", ""), f"CRadar comment token missing at {address}: {token}", failures)
        tag_row = cradar_tags.get(address)
        require(tag_row is not None, f"missing CRadar tags for {address}", failures)
        if tag_row is not None:
            require(COMMON_CRADAR_TAGS.issubset(set(tag_row.get("tags", "").split(";"))), f"CRadar tag mismatch at {address}", failures)
        require(cradar_decompile.get(address, {}).get("signature") == signature, f"CRadar decompile signature mismatch at {address}", failures)
        xref_rows = cradar_xrefs.get(address, [])
        require(any(row.get("from_addr", "").lower() == xref[2:] for row in xref_rows), f"CRadar xref mismatch at {address}", failures)

    goodies_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-goodies-recovery-metadata.tsv")}
    goodies_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-goodies-recovery-tags.tsv")}
    goodies_decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-goodies-recovery-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in GOODIES_TARGETS.items():
        row = goodies_metadata.get(address)
        require(row is not None, f"missing Goodies metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"Goodies name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"Goodies signature mismatch at {address}", failures)
            for token in tokens:
                require(token in row.get("comment", ""), f"Goodies comment token missing at {address}: {token}", failures)
        tag_row = goodies_tags.get(address)
        require(tag_row is not None, f"missing Goodies tags for {address}", failures)
        if tag_row is not None:
            require(COMMON_GOODIES_TAGS.issubset(set(tag_row.get("tags", "").split(";"))), f"Goodies tag mismatch at {address}", failures)
        require(goodies_decompile.get(address, {}).get("signature") == signature, f"Goodies decompile signature mismatch at {address}", failures)

    vtable = read_tsv(BASE / "post-vtable-slots.tsv")
    ok_count = sum(1 for row in vtable if row.get("status") == "OK")
    no_fn_count = sum(1 for row in vtable if row.get("status") == "NO_FUNCTION_AT_POINTER")
    require(ok_count == 1545, "post vtable OK count mismatch", failures)
    require(no_fn_count == 55, "post vtable NO_FUNCTION count mismatch", failures)
    slots = {(row.get("vtable"), row.get("slot_index")): row for row in vtable}
    require(slots.get(("005dd710", "37"), {}).get("function_name") == "CRadarVFunc__GetClassNameString_004bfb00", "CRadar slot 37 mismatch", failures)
    require(slots.get(("005dd710", "149"), {}).get("function_name") == "CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560", "CRadar slot 149 mismatch", failures)
    require(slots.get(("005dd710", "29"), {}).get("status") == "NO_FUNCTION_AT_POINTER", "CRadar slot 29 non-function mismatch", failures)
    require(slots.get(("005dd710", "147"), {}).get("status") == "NO_FUNCTION_AT_POINTER", "CRadar slot 147 non-function mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["status"] == "PASS", "queue status mismatch", failures)
    require(queue["totalFunctions"] == 6375, "queue total mismatch", failures)
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
    require(len(rows) == 6375, "quality TSV row count mismatch", failures)
    require(sum(1 for row in rows if row.get("comment", "").strip()) == 6375, "quality TSV commented count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175344519 or backup.get("totalBytes") == 175344519.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
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
        scripts.get("test:ghidra-cradar-goodies-boundary-recovery-wave1088")
        == r"py -3 tools\ghidra_cradar_goodies_boundary_recovery_wave1088_probe.py --check",
        "missing Wave1088 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1088-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1088 --check",
        "missing Wave1088 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1088 CRadar / Goodies boundary recovery" for row in ledger_rows), "missing Wave1088 ledger row", failures)
    require(any(row.get("task") == "Wave1088 CRadar / Goodies boundary recovery" for row in attempt_rows), "missing Wave1088 attempt row", failures)
    tracking = read_json(TRACKING_STATE)
    require(tracking.get("last_completed", {}).get("task") == "Wave1088 CRadar / Goodies boundary recovery", "tracking last_completed mismatch", failures)


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
        print("Wave1088 CRadar / Goodies boundary recovery probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1088 CRadar / Goodies boundary recovery probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
