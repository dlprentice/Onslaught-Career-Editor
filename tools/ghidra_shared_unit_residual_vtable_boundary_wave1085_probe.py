#!/usr/bin/env python3
"""Validate Wave1085 shared unit residual vtable-boundary artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1085-shared-unit-residual-vtable-boundary-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_shared_unit_residual_vtable_boundary_wave1085_2026-06-02.md"
AGG_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1085_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-125900_post_wave1085_shared_unit_residual_vtable_boundary_verified"
TAG = "shared-unit-residual-vtable-boundary-review-wave1085"

TARGETS = {
    "0x00401550": {
        "name": "SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550",
        "signature": "void __thiscall SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550(void * this, void * outVector)",
        "comment": ("Wave1085", "this+0x1c/0x20/0x24", "this+0x8c/0x90/0x94", "RET 0x4"),
    },
    "0x004fd440": {
        "name": "SharedUnitVFunc__TestField17c19cReadiness_004fd440",
        "signature": "int __thiscall SharedUnitVFunc__TestField17c19cReadiness_004fd440(void * this)",
        "comment": ("Wave1085", "this+0x17c/0x19c", "0x004fd5e0"),
    },
    "0x004fc3c0": {
        "name": "SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0",
        "signature": "void __thiscall SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0(void * this, void * candidate, void * outA, void * outB, void * arg3, void * arg4)",
        "comment": ("Wave1085", "0x0044a850", "0x0044a930", "RET 0x14"),
    },
    "0x004f9a10": {
        "name": "SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10",
        "signature": "float __thiscall SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10(void * this)",
        "comment": ("Wave1085", "this+0x178", "this+0x164+0xc0", "0x005d856c"),
    },
    "0x004f9220": {
        "name": "SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220",
        "signature": "void __thiscall SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220(void * this, void * thing)",
        "comment": ("Wave1085", "0x3bc", "0x0083da30", "0x00452b60"),
    },
    "0x004fe4a0": {
        "name": "SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0",
        "signature": "void __thiscall SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0(void * this, void * source)",
        "comment": ("Wave1085", "0x0044adb0", "this+0x114", "this+0x120", "0x004019b0"),
    },
    "0x004fdc90": {
        "name": "SharedUnitVFunc__IsField13cNotMode2_004fdc90",
        "signature": "int __thiscall SharedUnitVFunc__IsField13cNotMode2_004fdc90(void * this)",
        "comment": ("Wave1085", "this+0x13c", "mode value 2"),
    },
    "0x004fdd60": {
        "name": "SharedUnitVFunc__PropagateNameToField18c19c_004fdd60",
        "signature": "void __thiscall SharedUnitVFunc__PropagateNameToField18c19c_004fdd60(void * this, void * name)",
        "comment": ("Wave1085", "this+0x18c", "this+0x19c", "+0xfc"),
    },
    "0x00417620": {
        "name": "SharedUnitVFunc__ReturnField164Float154_00417620",
        "signature": "float __thiscall SharedUnitVFunc__ReturnField164Float154_00417620(void * this)",
        "comment": ("Wave1085", "this+0x164+0x154", "0x00417630"),
    },
    "0x00417610": {
        "name": "SharedUnitVFunc__ReturnField164E4_00417610",
        "signature": "int __thiscall SharedUnitVFunc__ReturnField164E4_00417610(void * this)",
        "comment": ("Wave1085", "this+0x164+0xe4", "0x00417620"),
    },
    "0x00417600": {
        "name": "SharedUnitVFunc__SetField160_00417600",
        "signature": "void __thiscall SharedUnitVFunc__SetField160_00417600(void * this, int value)",
        "comment": ("Wave1085", "this+0x160", "RET 0x4"),
    },
    "0x004175e0": {
        "name": "SharedUnitVFunc__ReturnField13cCOrZero_004175e0",
        "signature": "int __thiscall SharedUnitVFunc__ReturnField13cCOrZero_004175e0(void * this)",
        "comment": ("Wave1085", "this+0x13c+0x0c", "otherwise returns zero"),
    },
    "0x00405e50": {
        "name": "SharedUnitVFunc__ReturnField210_00405e50",
        "signature": "int __thiscall SharedUnitVFunc__ReturnField210_00405e50(void * this)",
        "comment": ("Wave1085", "this+0x210", "0x00405e60"),
    },
    "0x00405e40": {
        "name": "SharedUnitVFunc__ReturnField15c_00405e40",
        "signature": "int __thiscall SharedUnitVFunc__ReturnField15c_00405e40(void * this)",
        "comment": ("Wave1085", "this+0x15c", "0x00405e50"),
    },
    "0x00405e20": {
        "name": "SharedUnitVFunc__ClearField1f0_00405e20",
        "signature": "void __thiscall SharedUnitVFunc__ClearField1f0_00405e20(void * this)",
        "comment": ("Wave1085", "this+0x1f0", "stores zero"),
    },
    "0x00405e10": {
        "name": "SharedUnitVFunc__SetField1f0One_00405e10",
        "signature": "void __thiscall SharedUnitVFunc__SetField1f0One_00405e10(void * this)",
        "comment": ("Wave1085", "this+0x1f0", "stores one"),
    },
    "0x00405de0": {
        "name": "SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0",
        "signature": "int __thiscall SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0(void * this)",
        "comment": ("Wave1085", "this+0x168", "this+0x214", "0x2c flag mask 0x4"),
    },
    "0x00405e30": {
        "name": "SharedUnitVFunc__SetField15c_00405e30",
        "signature": "void __thiscall SharedUnitVFunc__SetField15c_00405e30(void * this, int value)",
        "comment": ("Wave1085", "this+0x15c", "RET 0x4"),
    },
    "0x00401900": {
        "name": "SharedUnitVFunc__ForwardArgToThingBridge_00401900",
        "signature": "void __thiscall SharedUnitVFunc__ForwardArgToThingBridge_00401900(void * this, void * arg)",
        "comment": ("Wave1085", "0x004f3cb0", "RET 0x4"),
    },
    "0x00401910": {
        "name": "SharedUnitVFunc__CopyTransformAndNotify_00401910",
        "signature": "void __thiscall SharedUnitVFunc__CopyTransformAndNotify_00401910(void * this, void * sourceBlock)",
        "comment": ("Wave1085", "this+0x8c", "0x004f3ce0", "this+0x38"),
    },
    "0x004175c0": {
        "name": "SharedUnitVFunc__ReturnField164FloatF4_004175c0",
        "signature": "float __thiscall SharedUnitVFunc__ReturnField164FloatF4_004175c0(void * this)",
        "comment": ("Wave1085", "this+0x164+0xf4", "0x004175d0"),
    },
    "0x004175d0": {
        "name": "SharedUnitVFunc__ReturnField164FloatF8_004175d0",
        "signature": "float __thiscall SharedUnitVFunc__ReturnField164FloatF8_004175d0(void * this)",
        "comment": ("Wave1085", "this+0x164+0xf8", "0x004175e0"),
    },
    "0x004fce00": {
        "name": "SharedUnitVFunc__ForwardField208Slot10_004fce00",
        "signature": "void __thiscall SharedUnitVFunc__ForwardField208Slot10_004fce00(void * this, void * arg0, void * arg1, void * arg2, void * arg3, void * arg4)",
        "comment": ("Wave1085", "this+0x208", "slot +0x10", "RET 0x14"),
    },
    "0x004fb270": {
        "name": "SharedUnitVFunc__ReturnField114Float_004fb270",
        "signature": "float __thiscall SharedUnitVFunc__ReturnField114Float_004fb270(void * this)",
        "comment": ("Wave1085", "this+0x114", "0x004fb280"),
    },
}

VTABLES = {
    "0x005e3700",
    "0x005dd710",
    "0x005e4180",
    "0x005e1668",
    "0x005e325c",
    "0x005e26b4",
    "0x005dfcc4",
    "0x005dff14",
    "0x005e1418",
    "0x005e0868",
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave1085-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "comment-hardened",
    "signature-hardened",
    "shared-vfunc",
    "unit-family-vtable",
}

DOC_TOKENS = (
    "Wave1085",
    TAG,
    "0x00401550 SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550",
    "0x004fd440 SharedUnitVFunc__TestField17c19cReadiness_004fd440",
    "0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0",
    "0x004f9220 SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220",
    "0x004fe4a0 SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0",
    "0x00401900 SharedUnitVFunc__ForwardArgToThingBridge_00401900",
    "0x00401910 SharedUnitVFunc__CopyTransformAndNotify_00401910",
    "0x004fce00 SharedUnitVFunc__ForwardField208Slot10_004fce00",
    "1448/1560 = 92.82%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6331/6331 = 100.00%",
    BACKUP_PATH,
    "boundary recovery",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof complete",
    "rebuild parity proven",
    "gameplay outcomes proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def address_file_count(relative: str) -> int:
    return len([line for line in read_text(BASE / relative).splitlines() if line.strip() and not line.strip().startswith("#")])


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "targets.txt": 24,
        "vtable-targets.txt": 10,
        "pre-diagnose.tsv": 24,
        "pre-instructions-around.tsv": 888,
        "pre-instructions-long.tsv": 226,
        "pre-instructions-wide.tsv": 885,
        "pre-xrefs.tsv": 790,
        "pre-vtable-slots.tsv": 1600,
        "post-metadata.tsv": 24,
        "post-tags.tsv": 24,
        "post-xrefs.tsv": 790,
        "post-instructions.tsv": 431,
        "post-decompile/index.tsv": 24,
        "post-vtable-slots.tsv": 1600,
    }
    for relative, expected in expected_counts.items():
        actual = address_file_count(relative) if relative.endswith(".txt") else len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual}", failures)

    require({normalize_address(line) for line in read_text(BASE / "targets.txt").splitlines() if line.strip()} == set(TARGETS), "target set mismatch", failures)
    require({normalize_address(line) for line in read_text(BASE / "vtable-targets.txt").splitlines() if line.strip()} == VTABLES, "vtable target set mismatch", failures)

    diagnose = read_tsv(BASE / "pre-diagnose.tsv")
    require(all(row.get("status") == "INSTRUCTION_NO_FUNCTION" for row in diagnose), "pre diagnose status mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch for {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch for {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch for {address}", failures)
            for token in (*expected["comment"], "Static retail Ghidra", "separate proof"):
                require(token in row.get("comment", ""), f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing for {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch for {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch for {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch for {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch for {address}", failures)

        require(address in xref_targets, f"missing xrefs for {address}", failures)

    pre_slots = read_tsv(BASE / "pre-vtable-slots.tsv")
    post_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    pre_ok = sum(1 for row in pre_slots if row.get("status") == "OK")
    pre_no_function = sum(1 for row in pre_slots if row.get("status") == "NO_FUNCTION_AT_POINTER")
    post_ok = sum(1 for row in post_slots if row.get("status") == "OK")
    post_no_function = sum(1 for row in post_slots if row.get("status") == "NO_FUNCTION_AT_POINTER")
    selected_pre = sum(
        1
        for row in pre_slots
        if normalize_address(row.get("pointer_addr", "")) in TARGETS and row.get("status") == "NO_FUNCTION_AT_POINTER"
    )
    selected_post = sum(
        1
        for row in post_slots
        if normalize_address(row.get("pointer_addr", "")) in TARGETS and row.get("status") == "OK"
    )
    require((pre_ok, pre_no_function) == (1244, 356), f"pre slot counts mismatch: {(pre_ok, pre_no_function)}", failures)
    require((post_ok, post_no_function) == (1480, 120), f"post slot counts mismatch: {(post_ok, post_no_function)}", failures)
    require(selected_pre == 236, f"selected pre no-function count mismatch: {selected_pre}", failures)
    require(selected_post == 236, f"selected post OK count mismatch: {selected_post}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=24 found=0 missing=24",
        "pre-instructions-around.log": "Wrote 888 instruction rows",
        "pre-instructions-long.log": "Wrote 226 instruction rows",
        "pre-instructions-wide.log": "Wrote 885 instruction rows",
        "pre-xrefs.log": "Wrote 790 rows",
        "pre-vtable-slots.log": "ExportVtableSlots complete: targets=10 rows=1600",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=24 skipped=0 created=24 would_create=0 renamed=0 would_rename=0 signature_updated=24 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply-redry.log": "SUMMARY: updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=1 signature_updated=0 comment_only_updated=0 bad=0",
        "apply-reapply.log": "SUMMARY: updated=1 skipped=23 created=0 would_create=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply-refinal-dry.log": "SUMMARY: updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=24 found=24 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "post-xrefs.log": "Wrote 790 rows",
        "post-instructions.log": "Wrote 431 function-body instruction rows",
        "post-decompile.log": "targets=24 dumped=24 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=10 rows=1600",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("LockException" not in text, f"LockException in {relative}", failures)
        require("Traceback (most recent call last)" not in text, f"Traceback in {relative}", failures)
        if relative.startswith("apply") or relative.startswith("post"):
            for bad in ("BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
            require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)

    quality_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1085.log")
    require("total_functions=6331 commented_functions=6331" in quality_text, "missing Wave1085 queue export token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6331, "queue total mismatch", failures)
    require(queue.get("status") == "PASS", "queue status mismatch", failures)
    for key in (
        "commentlessFunctionCount",
        "undefinedSignatureCount",
        "paramSignatureCount",
        "legacyWeakNameCount",
        "uncertainOwnerNameCount",
        "helperAddressNameCount",
        "wrapperAddressNameCount",
    ):
        require(quality.get(key) == 0, f"queue quality mismatch for {key}: {quality.get(key)}", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6331, "quality TSV row count mismatch", failures)
    require(commented == 6331, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6331, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174918535, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGG_NOTE,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-shared-unit-residual-vtable-boundary-wave1085")
        == r"py -3 tools\ghidra_shared_unit_residual_vtable_boundary_wave1085_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1085-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1085 --check",
        "missing aggregate package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave1085-shared-unit-residual-vtable-boundary-review.json")
    args = parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    report = {
        "schema": "ghidra-shared-unit-residual-vtable-boundary-wave1085.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": sorted(TARGETS),
        "mutatedTargets": 24,
        "metadataRows": 24,
        "tagRows": 24,
        "xrefRows": 790,
        "instructionRows": 431,
        "decompileRows": 24,
        "preSlotStatus": {"OK": 1244, "NO_FUNCTION_AT_POINTER": 356},
        "postSlotStatus": {"OK": 1480, "NO_FUNCTION_AT_POINTER": 120},
        "selectedSlotOccurrencesRecovered": 236,
        "failures": failures,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Wave1085 shared unit residual vtable-boundary probe:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in failures:
        print("-", failure)
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
