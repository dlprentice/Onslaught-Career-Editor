#!/usr/bin/env python3
"""Validate Wave1086 shared unit residual vtable-continuation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1086-shared-unit-residual-vtable-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_shared_unit_residual_vtable_continuation_wave1086_2026-06-02.md"
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
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-134022_post_wave1086_shared_unit_residual_vtable_continuation_verified"
TAG = "shared-unit-residual-vtable-continuation-wave1086"

TARGETS = {
    "0x00405dc0": ("SharedUnitVFunc__ReturnFloat005d858c_00405dc0", "float __thiscall SharedUnitVFunc__ReturnFloat005d858c_00405dc0(void * this)", ("0x005d858c", "slot 102")),
    "0x00401f70": ("SharedUnitVFunc__TestFieldCcDeltaBelow015_00401f70", "int __thiscall SharedUnitVFunc__TestFieldCcDeltaBelow015_00401f70(void * this)", ("0x00672fd0", "this+0xcc", "0x005d8588")),
    "0x00405dd0": ("SharedUnitVFunc__ReturnFloat005d8b9c_00405dd0", "float __thiscall SharedUnitVFunc__ReturnFloat005d8b9c_00405dd0(void * this)", ("0x005d8b9c", "slot 103")),
    "0x0047c8b0": ("SharedUnitVFunc__TestFieldCcDeltaBelowGroundThreshold_0047c8b0", "int __thiscall SharedUnitVFunc__TestFieldCcDeltaBelowGroundThreshold_0047c8b0(void * this)", ("0x005dbd84", "slot 97")),
    "0x004dfcb0": ("SharedUnitVFunc__ReturnInvertedFlag2cMask4_004dfcb0", "int __thiscall SharedUnitVFunc__ReturnInvertedFlag2cMask4_004dfcb0(void * this)", ("this+0x2c", "masks bit 0x4")),
    "0x0050e860": ("SharedUnitVFunc__ReturnFloat005dbe80_0050e860", "float __thiscall SharedUnitVFunc__ReturnFloat005dbe80_0050e860(void * this)", ("0x005dbe80", "slot 45")),
    "0x0050eb60": ("SharedUnitVFunc__ReturnFloat005d8cc4_0050eb60", "float __thiscall SharedUnitVFunc__ReturnFloat005d8cc4_0050eb60(void * this)", ("0x005d8cc4", "slots 102/103")),
    "0x004037a0": ("SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0", "void __thiscall SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0(void * this, void * hitContext, void * sourceThing, void * arg2, void * arg3)", ("CUnit__ApplyDamage", "selector 0x19", "RET 0x10")),
    "0x00403a90": ("SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90", "void __thiscall SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90(void * this, void * sourceVector, float phase, float limit, void * targetVector, void * callbackArg)", ("this+0x208", "0x0047ea20", "RET 0x14")),
    "0x00403b60": ("SharedUnitVFunc__ReturnFlag2cScaledSlot40Float_00403b60", "float __thiscall SharedUnitVFunc__ReturnFlag2cScaledSlot40Float_00403b60(void * this)", ("this+0x2c", "0x005d8614", "0x005d860c")),
    "0x00417660": ("SharedUnitVFunc__ForwardArgWithFlags40100120_00417660", "void __thiscall SharedUnitVFunc__ForwardArgWithFlags40100120_00417660(void * this, int value)", ("0x40100120", "0x004fcdc0")),
    "0x00417680": ("SharedUnitVFunc__ReturnField250_00417680", "int __thiscall SharedUnitVFunc__ReturnField250_00417680(void * this)", ("this+0x250", "slot 41")),
    "0x00417690": ("SharedUnitVFunc__SetField250_00417690", "void __thiscall SharedUnitVFunc__SetField250_00417690(void * this, int value)", ("this+0x250", "RET 0x4")),
    "0x00417df0": ("SharedUnitVFunc__HandleType1388Field74Resource_00417df0", "void __thiscall SharedUnitVFunc__HandleType1388Field74Resource_00417df0(void * this, void * eventRecord)", ("0x1388", "this+0x74", "0x004f9820")),
    "0x004284f0": ("CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0", "float __thiscall CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0(void * this)", ("this+0x40", "this+0x50", "FPATAN")),
    "0x004287c0": ("CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0", "void * __thiscall CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0(void * this, void * outVector)", ("this+0x26c", "slot +0x6c", "this+0x7c")),
    "0x00428be0": ("CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0", "void __thiscall CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0(void * this, void * currentVector, void * targetVector, void * arg2, void * arg3)", ("this+0x2c", "CUnit__SmoothEulerTowardTargetAndBuildMatrix", "RET 0x10")),
    "0x00428c30": ("CUnitAIVFunc__ReturnFloat005d9434_00428c30", "float __thiscall CUnitAIVFunc__ReturnFloat005d9434_00428c30(void * this)", ("0x005d9434", "slot 103")),
    "0x00428c40": ("CUnitAIVFunc__ReturnFloat005d8cb0_00428c40", "float __thiscall CUnitAIVFunc__ReturnFloat005d8cb0_00428c40(void * this)", ("0x005d8cb0", "slot 75")),
    "0x00428c50": ("CUnitAIVFunc__ReturnField164_198Present_00428c50", "int __thiscall CUnitAIVFunc__ReturnField164_198Present_00428c50(void * this)", ("this+0x164", "+0x198")),
    "0x00428c90": ("CUnitAIVFunc__CanDeployWhenField264Null_00428c90", "int __thiscall CUnitAIVFunc__CanDeployWhenField264Null_00428c90(void * this)", ("this+0x264", "CUnit__CanDeployNow")),
    "0x00428d30": ("CUnitAIVFunc__CopyVector1cToOut_00428d30", "void __thiscall CUnitAIVFunc__CopyVector1cToOut_00428d30(void * this, void * outVector)", ("this+0x1c", "RET 0x4")),
    "0x0047a730": ("CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730", "void __thiscall CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730(void * this, void * arg)", ("0x0062ca48", "idle", "0x004f4560")),
    "0x0047a9c0": ("CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0", "void __thiscall CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0(void * this, int mode)", ("mode value 4", "CUnit__SetEngagementModeAndMaybeClearTargetReader")),
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave1086-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "comment-hardened",
    "signature-hardened",
    "vtable-boundary",
    "shared-unit-vtable",
}

DOC_TOKENS = (
    "Wave1086",
    TAG,
    "0x00405dc0 SharedUnitVFunc__ReturnFloat005d858c_00405dc0",
    "0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0",
    "0x00403a90 SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90",
    "0x00428be0 CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0",
    "0x0047a730 CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
    "1472/1560 = 94.36%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6355/6355 = 100.00%",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def strict_count(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "candidate-targets.txt": 24,
        "vtable-targets.txt": 10,
        "pre-diagnose.tsv": 24,
        "pre-metadata.tsv": 24,
        "pre-instructions-around.tsv": 888,
        "pre-instructions-wide.tsv": 2424,
        "pre-instructions-deep.tsv": 6360,
        "pre-xrefs.tsv": 171,
        "pre-vtable-slots.tsv": 1600,
        "post-metadata.tsv": 24,
        "post-tags.tsv": 24,
        "post-xrefs.tsv": 171,
        "post-instructions.tsv": 448,
        "post-decompile/index.tsv": 24,
        "post-vtable-slots.tsv": 1600,
    }
    for relative, expected in expected_counts.items():
        path = BASE / relative
        if relative.endswith(".txt"):
            count = len([line for line in read_text(path).splitlines() if line.strip() and not line.startswith("#")])
        else:
            count = len(read_tsv(path))
        require(count == expected, f"{relative} row/count mismatch: {count} != {expected}", failures)

    diagnose = read_tsv(BASE / "pre-diagnose.tsv")
    require(all(row.get("memory_block") == ".text" for row in diagnose), "diagnose block mismatch", failures)
    require(all(row.get("status") == "INSTRUCTION_NO_FUNCTION" for row in diagnose), "diagnose status mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1086 static read-back", "exact source virtual name", *comment_tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"tags missing at {address}: {COMMON_TAGS - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    pre_slots = read_tsv(BASE / "pre-vtable-slots.tsv")
    post_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    require(sum(1 for row in pre_slots if row.get("status") == "OK") == 1480, "pre vtable OK mismatch", failures)
    require(sum(1 for row in pre_slots if row.get("status") == "NO_FUNCTION_AT_POINTER") == 120, "pre vtable NO_FUNCTION mismatch", failures)
    require(sum(1 for row in post_slots if row.get("status") == "OK") == 1528, "post vtable OK mismatch", failures)
    require(sum(1 for row in post_slots if row.get("status") == "NO_FUNCTION_AT_POINTER") == 72, "post vtable NO_FUNCTION mismatch", failures)
    target_ptrs = {address[2:] for address in TARGETS}
    require(sum(1 for row in pre_slots if row.get("status") == "NO_FUNCTION_AT_POINTER" and row.get("pointer_addr", "").lower() in target_ptrs) == 48, "selected pre vtable mismatch", failures)
    require(sum(1 for row in post_slots if row.get("status") == "OK" and row.get("pointer_addr", "").lower() in target_ptrs) == 48, "selected post vtable mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=24 skipped=0 created=24 would_create=0 renamed=0 would_rename=0 signature_updated=24 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=24 found=24 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "post-xrefs.log": "Wrote 171 rows",
        "post-instructions.log": "Wrote 448 function-body instruction rows",
        "post-decompile.log": "targets=24 dumped=24 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=10 rows=1600",
        "quality-refresh.log": "total_functions=6355 commented_functions=6355",
        "queue-probe.log": "Status: PASS",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1086.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1086_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6355, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain-owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "helper-address count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "wrapper-address count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = strict_count(rows)
    require(len(rows) == 6355, "quality TSV row count mismatch", failures)
    require(commented == 6355, "quality TSV commented mismatch", failures)
    require(strict == 6355, "quality TSV strict clean mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175082375, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, FUNCTION_COVERAGE, GHIDRA_REFERENCE, CAMPAIGN, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-shared-unit-residual-vtable-continuation-wave1086")
        == r"py -3 tools\ghidra_shared_unit_residual_vtable_continuation_wave1086_probe.py --check",
        "missing Wave1086 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1086-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1086 --check",
        "missing Wave1086 aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1086 shared unit residual vtable continuation" for row in ledger_rows), "missing Wave1086 ledger row", failures)
    require(any(row.get("task") == "Wave1086 shared unit residual vtable continuation" for row in attempt_rows), "missing Wave1086 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1086 shared unit residual vtable-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1086 shared unit residual vtable-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
