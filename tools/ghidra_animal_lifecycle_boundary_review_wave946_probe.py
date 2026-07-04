#!/usr/bin/env python3
"""Validate Wave946 CAnimal lifecycle/vtable-boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave946-animal-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_animal_lifecycle_boundary_review_wave946_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
ANIMAL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Animal.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-062816_post_wave946_animal_lifecycle_boundary_review_verified"
SCRIPT_NAME = "test:ghidra-animal-lifecycle-boundary-review-wave946"
SCRIPT_VALUE = r"py -3 tools\ghidra_animal_lifecycle_boundary_review_wave946_probe.py --check"

TARGETS = {
    "0x0044c140": ("CAnimal__HandleEvent3000Dispatch", "void __thiscall CAnimal__HandleEvent3000Dispatch(void * this, void * event)", ("event 3000", "vtable byte offset +0x108")),
    "0x0043e9f0": ("CThing__GetRenderPos", "void __thiscall CThing__GetRenderPos(void * this, void * outRenderPos)", ("this+0x1c", "CThing::GetRenderPos")),
    "0x0043ea20": ("CComplexThing__GetRenderOrientation", "void __thiscall CComplexThing__GetRenderOrientation(void * this, void * outRenderOrientation)", ("this+0x3c", "CComplexThing::GetRenderOrientation")),
    "0x00405e80": ("SharedVFunc__WriteZeroVectorRet04_00405e80", "void __thiscall SharedVFunc__WriteZeroVectorRet04_00405e80(void * this, void * outVector)", ("three zero dwords", "RET 0x4")),
    "0x004040f0": ("CAnimal__GetClassNameString", "char * __thiscall CAnimal__GetClassNameString(void * this)", ("0x00622d70", "CAnimal")),
    "0x00404100": ("CAnimal__GetTypeId1D", "int __thiscall CAnimal__GetTypeId1D(void * this)", ("literal 0x1d",)),
    "0x00401420": ("CThing__GetCueFactorFromRenderThing", "float __thiscall CThing__GetCueFactorFromRenderThing(void * this)", ("this+0x30", "CThing::GetCueFactor")),
    "0x00401440": ("CThing__GetRenderRadiusFromRenderThing", "float __thiscall CThing__GetRenderRadiusFromRenderThing(void * this)", ("vtable byte offset +0x18", "CThing::GetRenderRadius")),
    "0x00401460": ("CThing__MakeVisible", "void __thiscall CThing__MakeVisible(void * this)", ("clears bit 0x10", "CThing::MakeVisible")),
    "0x00401470": ("CThing__MakeInvisible", "void __thiscall CThing__MakeInvisible(void * this)", ("sets bit 0x10", "CThing::MakeInvisible")),
    "0x00401490": ("CThing__Damage_NoOp", "void __thiscall CThing__Damage_NoOp(void * this, float amount, void * byThing, int damageShields, int meshPartNo)", ("single RET 0x10", "CThing::Damage")),
    "0x004014b0": ("CThing__GravityDefault", "float __thiscall CThing__GravityDefault(void * this)", ("0x005d8574", "CThing::Gravity")),
    "0x004014e0": ("CComplexThing__IsObjectiveFlagSet", "int __thiscall CComplexThing__IsObjectiveFlagSet(void * this)", ("masks bit 0x20", "CComplexThing::IsObjective")),
    "0x00401510": ("SharedVFunc__ReturnField78_00401510", "int __thiscall SharedVFunc__ReturnField78_00401510(void * this)", ("this+0x78",)),
    "0x00401520": ("SharedVFunc__NoOpFiveArgs_00401520", "void __thiscall SharedVFunc__NoOpFiveArgs_00401520(void * this, void * arg1, void * arg2, void * arg3, void * arg4, void * arg5)", ("single RET 0x14",)),
    "0x00404110": ("CAnimal__SetThingTypeMask80000001", "void __thiscall CAnimal__SetThingTypeMask80000001(void * this, int thingType)", ("0x80000001", "this+0x34")),
    "0x00404120": ("CAnimal__CopyVector7CToOut", "void __thiscall CAnimal__CopyVector7CToOut(void * this, void * outVector)", ("this+0x7c",)),
    "0x00404150": ("CAnimal__SetVector7CFromInput", "void __thiscall CAnimal__SetVector7CFromInput(void * this, void * inVector)", ("this+0x7c",)),
    "0x00404170": ("CAnimal__AddVectorTo7C", "void __thiscall CAnimal__AddVectorTo7C(void * this, void * deltaVector)", ("this+0x7c", "three-float vector")),
    "0x004041a0": ("CAnimal__CopyVector8CToOut", "void __thiscall CAnimal__CopyVector8CToOut(void * this, void * outVector)", ("this+0x8c",)),
    "0x004041d0": ("CAnimal__CopyMatrix9CToOut", "void __thiscall CAnimal__CopyMatrix9CToOut(void * this, void * outMatrix)", ("this+0x9c", "0x30 bytes")),
    "0x004045d0": ("CAnimal__RenderViaCThingRender", "void __thiscall CAnimal__RenderViaCThingRender(void * this, int renderFlags)", ("CThing__Render", "RET 0x4")),
    "0x004f3d30": ("CThing__DrawDebugStuff3d", "void __thiscall CThing__DrawDebugStuff3d(void * this)", ("CThing__RenderDebugVolumeOverlay", "CThing::DrawDebugStuff3d")),
}

VTABLE_SLOTS = {
    "0": "CAnimal__HandleEvent3000Dispatch",
    "3": "CThing__GetRenderPos",
    "4": "CComplexThing__GetRenderOrientation",
    "5": "SharedVFunc__WriteZeroVectorRet04_00405e80",
    "7": "CAnimal__GetClassNameString",
    "8": "CAnimal__GetTypeId1D",
    "13": "CThing__GetCueFactorFromRenderThing",
    "16": "CThing__GetRenderRadiusFromRenderThing",
    "26": "CComplexThing__IsObjectiveFlagSet",
    "27": "CAnimal__CopyVector7CToOut",
    "30": "CAnimal__CopyVector8CToOut",
    "31": "CAnimal__CopyMatrix9CToOut",
    "32": "CThing__MakeVisible",
    "33": "CThing__MakeInvisible",
    "36": "CAnimal__RenderViaCThingRender",
    "38": "CAnimal__SetThingTypeMask80000001",
    "40": "CThing__Damage_NoOp",
    "41": "SharedVFunc__ReturnField78_00401510",
    "45": "CThing__GravityDefault",
    "52": "CThing__DrawDebugStuff3d",
    "61": "SharedVFunc__NoOpFiveArgs_00401520",
    "67": "CAnimal__SetVector7CFromInput",
    "68": "CAnimal__AddVectorTo7C",
}

CORE_TOKENS = (
    "Wave946",
    "animal-lifecycle-boundary-wave946",
    "CAnimal__HandleEvent3000Dispatch",
    "CThing__GetRenderRadiusFromRenderThing",
    "CThing__MakeVisible",
    "CAnimal__CopyMatrix9CToOut",
    "CThing__DrawDebugStuff3d",
    "0x0044c140 CAnimal__HandleEvent3000Dispatch",
    "0x00401440 CThing__GetRenderRadiusFromRenderThing",
    "0x004041d0 CAnimal__CopyMatrix9CToOut",
    "0x004f3d30 CThing__DrawDebugStuff3d",
    "6139/6139 = 100.00%",
    "232/1408 = 16.48%",
    BACKUP,
)

OVERCLAIMS = (
    "runtime animal behavior proven",
    "runtime render behavior proven",
    "exact source virtual names proven",
    "exact animal layout proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalize_raw(value: str) -> str:
    return normalize_address(value)[2:]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def rows_by_address(path: Path) -> dict[str, dict[str, str]]:
    return {normalize_address(row["address"]): row for row in read_tsv(path)}


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 195,
        "pre-decompile/index.tsv": 3,
        "created-boundary-targets.txt": 23,
        "post-targets.txt": 26,
        "post-metadata.tsv": 26,
        "post-tags.tsv": 26,
        "post-xrefs.tsv": 1005,
        "post-instructions.tsv": 389,
        "post-decompile/index.tsv": 26,
        "vtable-slots-69-post.tsv": 69,
    }
    for rel, count in expected_counts.items():
        path = BASE / rel
        actual = len(read_text(path).splitlines()) if path.suffix == ".txt" else len(read_tsv(path))
        require(actual == count, f"{rel} row count mismatch: {actual} != {count}", failures)

    metadata = rows_by_address(BASE / "post-metadata.tsv")
    tags = rows_by_address(BASE / "post-tags.tsv")
    decompile = rows_by_address(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in ("Wave946", *comment_tokens):
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        if tag_row:
            for tag in ("animal-lifecycle-boundary-wave946", "wave946-readback-verified"):
                require(tag in tag_row.get("tags", ""), f"missing tag {address}: {tag}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)

    vtable_rows = read_tsv(BASE / "vtable-slots-69-post.tsv")
    require(all(row.get("status") == "OK" for row in vtable_rows), "post CAnimal vtable has bad slot status", failures)
    for slot, name in VTABLE_SLOTS.items():
        require(
            any(row.get("slot_index") == slot and row.get("function_name") == name and row.get("status") == "OK" for row in vtable_rows),
            f"missing vtable slot {slot}: {name}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 created=7 would_create=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-expanded-dry.log": "SUMMARY: updated=0 skipped=7 created=0 would_create=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-expanded.log": "SUMMARY: updated=16 skipped=7 created=16 would_create=0 renamed=0 would_rename=0 signature_updated=16 comment_only_updated=0 missing=0 bad=0",
        "apply-expanded-final-dry.log": "SUMMARY: updated=0 skipped=23 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=26 found=26 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=26 missing=0",
        "post-xrefs.log": "Wrote 1005 rows",
        "post-instructions.log": "Wrote 389 function-body instruction rows",
        "post-decompile.log": "targets=26 dumped=26 missing=0 failed=0",
        "vtable-slots-69-post.log": "ExportVtableSlots complete: targets=1 rows=69",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {rel}: {bad}", failures)

    quality_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave946.log"
    queue_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave946_queue_probe.log"
    require("total_functions=6139 commented_functions=6139" in read_text(quality_log), "quality refresh mismatch", failures)
    require("Total functions: 6139" in read_text(queue_log), "queue probe total mismatch", failures)

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6139, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 0, "queue param mismatch", failures)
    require(len(read_tsv(QUEUE_TSV)) == 6139, "queue TSV row count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173476743, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, ANIMAL_DOC, THING_DOC, BACKLOG, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave946 CAnimal lifecycle boundary review" for row in ledger_rows), "missing ledger row", failures)
    require(any(row.get("task") == "Wave946 CAnimal lifecycle boundary review" for row in attempt_rows), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave946 CAnimal lifecycle boundary review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave946 CAnimal lifecycle boundary review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
