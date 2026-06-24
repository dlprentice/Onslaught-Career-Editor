#!/usr/bin/env python3
"""Validate Wave1067 destructable-controller lookup/damage read-only artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1067-destructable-controller-lookup-damage-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_destructable_controller_lookup_damage_review_wave1067_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1067_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

EXPECTED_SIGNATURES = {
    "0x00443fc0": ("CDestructableSegmentsController__Ctor", "void * __thiscall CDestructableSegmentsController__Ctor(void * this, void * field10Value, void * field14Value, void * field24Value, void * field28Value)"),
    "0x00444000": ("CDestructableSegmentsController__Dtor", "void __fastcall CDestructableSegmentsController__Dtor(void * this)"),
    "0x00444030": ("CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold", "void __thiscall CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold(void * this, int segmentIndex, float damageAmount, void * damageSource)"),
    "0x00444160": ("CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold", "void __fastcall CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold(void * this)"),
    "0x004442d0": ("CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex", "float __thiscall CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex(void * this, int segmentIndex)"),
    "0x00444300": ("CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex", "float __thiscall CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex(void * this, int segmentIndex)"),
    "0x00444330": ("CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive", "float __fastcall CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive(void * this)"),
    "0x00444370": ("CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive", "float __fastcall CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive(void * this)"),
    "0x004443b0": ("CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive", "float __fastcall CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive(void * this)"),
    "0x004443f0": ("CDestructableSegmentsController__TriggerCoreCascadeIfEligible", "void __fastcall CDestructableSegmentsController__TriggerCoreCascadeIfEligible(void * this)"),
    "0x00444450": ("CDestructableSegmentsController__SetSegmentField0CByName", "void __thiscall CDestructableSegmentsController__SetSegmentField0CByName(void * this, void * segmentName, float segmentValue)"),
    "0x004444b0": ("CDestructableSegmentsController__SetSegmentFields0C10ByName", "void __thiscall CDestructableSegmentsController__SetSegmentFields0C10ByName(void * this, void * segmentName, float segmentValue)"),
    "0x00444520": ("CDestructableSegmentsController__FindSegmentByName", "void * __thiscall CDestructableSegmentsController__FindSegmentByName(void * this, void * segmentName)"),
    "0x00444580": ("CDestructableSegmentsController__SetAllSegmentsField0C", "void __thiscall CDestructableSegmentsController__SetAllSegmentsField0C(void * this, float segmentValue)"),
    "0x004445b0": ("CDestructableSegmentsController__SetSegmentActiveFlagByName", "void __thiscall CDestructableSegmentsController__SetSegmentActiveFlagByName(void * this, void * segmentName, int activeFlag)"),
    "0x00444620": ("CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric", "void __thiscall CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric(void * this, int activeFlag)"),
}

EXPECTED_XREFS = {
    ("0x00443fc0", "0x0047fe99", "UNCONDITIONAL_CALL"),
    ("0x00444000", "0x004f977f", "UNCONDITIONAL_CALL"),
    ("0x00444030", "0x004f9ddc", "UNCONDITIONAL_CALL"),
    ("0x00444160", "0x004f943e", "UNCONDITIONAL_CALL"),
    ("0x004442d0", "0x004fd5fa", "UNCONDITIONAL_CALL"),
    ("0x004442d0", "0x004fd644", "UNCONDITIONAL_CALL"),
    ("0x00444300", "0x004fd619", "UNCONDITIONAL_CALL"),
    ("0x00444330", "0x004f99fc", "UNCONDITIONAL_CALL"),
    ("0x00444370", "0x004f9a53", "UNCONDITIONAL_CALL"),
    ("0x004443b0", "0x004f9a1c", "UNCONDITIONAL_CALL"),
    ("0x004443f0", "0x004fd1dc", "UNCONDITIONAL_CALL"),
    ("0x00444450", "0x005354b1", "UNCONDITIONAL_CALL"),
    ("0x004444b0", "0x005354f1", "UNCONDITIONAL_CALL"),
    ("0x00444520", "0x0047feff", "UNCONDITIONAL_CALL"),
    ("0x00444580", "0x00535525", "UNCONDITIONAL_CALL"),
    ("0x004445b0", "0x00534333", "UNCONDITIONAL_CALL"),
    ("0x00444620", "0x005343b7", "UNCONDITIONAL_CALL"),
}

COMMON_PRIMARY_TAGS = {
    "static-reaudit",
    "destructable-segments",
    "retail-binary-evidence",
}

COMMENT_TOKENS = {
    "0x00443fc0": ("constructor-like initializer", "fields +0x10/+0x14/+0x24/+0x28", "Static retail evidence only"),
    "0x00444030": ("Controller indexed damage path", "threshold", "runtime damage behavior"),
    "0x00444160": ("Controller random-damage burst path", "CSPtrSet", "threshold"),
    "0x004442d0": ("field +0x14", "Damage-style segment vfuncs", "runtime/UI semantics unproven"),
    "0x00444300": ("field +0x18", "damage amount", "runtime/UI semantics unproven"),
    "0x004443f0": ("Controller cascade trigger", "one-shot threshold flag", "runtime cascade behavior"),
    "0x00444450": ("Name-dispatch controller helper", "field +0x0c", "RET 0x8"),
    "0x00444520": ("Name-dispatch controller lookup", "fatal warning", "segment pointer"),
    "0x004445b0": ("activeFlag", "field +0x1c", "RET 0x8"),
    "0x00444620": ("Bulk controller active-flag helper", "cached active-value metric", "older CExplosionInitThing owner label"),
}

DOC_TOKENS = (
    "Wave1067",
    "destructable-controller-lookup-damage-review-wave1067",
    "0x00443fc0 CDestructableSegmentsController__Ctor",
    "0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
    "0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold",
    "0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex",
    "0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex",
    "0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible",
    "0x00444450 CDestructableSegmentsController__SetSegmentField0CByName",
    "0x00444520 CDestructableSegmentsController__FindSegmentByName",
    "0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName",
    "0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric",
    "812/1408 = 57.67%",
    "1248/1560 = 80.00%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime destructable-controller behavior proven",
    "runtime destructable controller behavior proven",
    "runtime cascade behavior proven",
    "runtime damage behavior proven",
    "runtime name-dispatch behavior proven",
    "rebuild parity proven",
    "exact source-layout identity proven",
)


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


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 16,
        "primary-tags.tsv": 16,
        "primary-xrefs.tsv": 17,
        "primary-instructions.tsv": 590,
        "primary-decompile/index.tsv": 16,
        "context-metadata.tsv": 20,
        "context-tags.tsv": 20,
        "context-xrefs.tsv": 142,
        "context-instructions.tsv": 1757,
        "context-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Static retail evidence only",)):
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    tags = {norm(row["address"]): set(row.get("tags", "").split(";")) for row in read_tsv(BASE / "primary-tags.tsv")}
    for address in EXPECTED_SIGNATURES:
        require(COMMON_PRIMARY_TAGS.issubset(tags.get(address, set())), f"primary tags missing {address}", failures)

    xrefs = {
        (norm(row.get("target_addr", "")), norm(row.get("from_addr", "")), row.get("ref_type"))
        for row in read_tsv(BASE / "primary-xrefs.tsv")
    }
    for target, source, ref_type in EXPECTED_XREFS:
        require((target, source, ref_type) in xrefs, f"missing xref {target} from {source} {ref_type}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=16 found=16 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "primary-xrefs.log": "Wrote 17 rows",
        "primary-instructions.log": "Wrote 590 function-body instruction rows",
        "primary-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "context-metadata.log": "targets=20 found=20 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "context-xrefs.log": "Wrote 142 rows",
        "context-instructions.log": "Wrote 1757 function-body instruction rows",
        "context-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174721927, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-destructable-controller-lookup-damage-review-wave1067")
        == r"py -3 tools\ghidra_destructable_controller_lookup_damage_review_wave1067_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1067-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1067 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    task = "Wave1067 destructable controller lookup damage review"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1067 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20649 for row in attempt_rows), "missing Wave1067 attempt row", failures)


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
        print("Wave1067 destructable-controller lookup/damage probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1067 destructable-controller lookup/damage probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
