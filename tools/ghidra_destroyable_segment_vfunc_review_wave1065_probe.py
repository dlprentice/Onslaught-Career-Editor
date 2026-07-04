#!/usr/bin/env python3
"""Validate Wave1065 destroyable-segment vfunc read-only artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1065-destroyable-segment-vfunc-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_destroyable_segment_vfunc_review_wave1065_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1065_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified"
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
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

EXPECTED_SIGNATURES = {
    "0x00442870": ("CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields", "void __thiscall CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields(void * this, float scaleFactor, float divisor)"),
    "0x00442960": ("CDestroyableSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * sourceThing)"),
    "0x00442b00": ("CDestroyableSegment__VFunc_06_CheckParentBreakGate", "int __fastcall CDestroyableSegment__VFunc_06_CheckParentBreakGate(void * this)"),
    "0x00442b20": ("CDestroyableSegment__VFunc_08_HandleSegmentBreak", "void __fastcall CDestroyableSegment__VFunc_08_HandleSegmentBreak(void * this)"),
    "0x00442f60": ("CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "void __fastcall CDestroyableSegment__VFunc_10_SpawnRubbleEffects(void * this)"),
    "0x00443460": ("CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch", "void __thiscall CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch(void * this, void * eventRecord)"),
    "0x004434c0": ("CDestroyableCoreSegment__VFunc_07_GetCoreField48", "float __fastcall CDestroyableCoreSegment__VFunc_07_GetCoreField48(void * this)"),
    "0x00443590": ("CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields", "void __thiscall CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields(void * this, float scaleFactor, float divisor)"),
    "0x004435c0": ("CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate", "int __fastcall CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate(void * this)"),
    "0x004435f0": ("CDestroyableCoreSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableCoreSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)"),
    "0x00443660": ("CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade", "void __fastcall CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade(void * this)"),
    "0x004436d0": ("CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch", "void __thiscall CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch(void * this, void * eventRecord)"),
    "0x00443780": ("CDestroyableSwapSegment__VFunc_03_ApplyDamage", "void __thiscall CDestroyableSwapSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)"),
    "0x00443810": ("CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak", "void __fastcall CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak(void * this)"),
    "0x00443830": ("CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex", "int __fastcall CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex(void * this)"),
    "0x00443890": ("CDestroyableSegmentVariant__VFunc_03_ApplyDamage", "void __thiscall CDestroyableSegmentVariant__VFunc_03_ApplyDamage(void * this, float damageAmount, void * sourceThing)"),
    "0x004439c0": ("CDestroyableSegment__SharedVFunc_08_HandleChildBreak", "void __fastcall CDestroyableSegment__SharedVFunc_08_HandleChildBreak(void * this)"),
    "0x004439f0": ("CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields", "void __thiscall CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields(void * this, float scaleFactor, float divisor)"),
    "0x00443a20": ("CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects", "void __fastcall CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects(void * this)"),
    "0x00443ea0": ("CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak", "void __fastcall CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak(void * this)"),
}

EXPECTED_DATA_XREFS = {
    ("0x00442870", "0x005db058"),
    ("0x00442870", "0x005db0d8"),
    ("0x00442870", "0x005db140"),
    ("0x00442870", "0x005db174"),
    ("0x00442960", "0x005db038"),
    ("0x00442b00", "0x005db044"),
    ("0x00442b00", "0x005db0c4"),
    ("0x00442b00", "0x005db0f8"),
    ("0x00442b00", "0x005db12c"),
    ("0x00442b00", "0x005db160"),
    ("0x00442b20", "0x005db04c"),
    ("0x00442f60", "0x005db054"),
    ("0x00442f60", "0x005db094"),
    ("0x00442f60", "0x005db13c"),
    ("0x00442f60", "0x005db170"),
    ("0x00443460", "0x005db02c"),
    ("0x00443460", "0x005db0ac"),
    ("0x00443460", "0x005db0e0"),
    ("0x00443460", "0x005db114"),
    ("0x00443460", "0x005db148"),
    ("0x004436d0", "0x005db06c"),
    ("0x00443890", "0x005db0ec"),
    ("0x00443890", "0x005db120"),
    ("0x00443ea0", "0x005db0cc"),
}

COMMON_PRIMARY_TAGS = {
    "static-reaudit",
    "destructable-segments",
    "retail-binary-evidence",
    "vtable-slot",
}

DOC_TOKENS = (
    "Wave1065",
    "destroyable-segment-vfunc-review-wave1065",
    "0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields",
    "0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage",
    "0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak",
    "0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects",
    "0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch",
    "0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch",
    "0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage",
    "0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak",
    "812/1408 = 57.67%",
    "1219/1560 = 78.14%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime destructable-segment behavior proven",
    "runtime destroyable-segment behavior proven",
    "runtime rubble behavior proven",
    "runtime cascade behavior proven",
    "runtime component behavior proven",
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
        "primary-metadata.tsv": 20,
        "primary-tags.tsv": 20,
        "primary-xrefs.tsv": 41,
        "primary-instructions.tsv": 1253,
        "primary-decompile/index.tsv": 20,
        "context-metadata.tsv": 38,
        "context-tags.tsv": 38,
        "context-xrefs.tsv": 73,
        "context-instructions.tsv": 1948,
        "context-decompile/index.tsv": 38,
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
    for target, source in EXPECTED_DATA_XREFS:
        require((target, source, "DATA") in xrefs, f"missing DATA xref {target} from {source}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=20 found=20 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "primary-xrefs.log": "Wrote 41 rows",
        "primary-instructions.log": "Wrote 1253 function-body instruction rows",
        "primary-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
        "context-metadata.log": "targets=38 found=38 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=38 missing=0",
        "context-xrefs.log": "Wrote 73 rows",
        "context-instructions.log": "Wrote 1948 function-body instruction rows",
        "context-decompile.log": "targets=38 dumped=38 missing=0 failed=0",
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
        scripts.get("test:ghidra-destroyable-segment-vfunc-review-wave1065")
        == r"py -3 tools\ghidra_destroyable_segment_vfunc_review_wave1065_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1065-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1065 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    task = "Wave1065 destroyable segment vfunc review"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1065 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20647 for row in attempt_rows), "missing Wave1065 attempt row", failures)


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
        print("Wave1065 destroyable-segment vfunc probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1065 destroyable-segment vfunc probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
