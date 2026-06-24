#!/usr/bin/env python3
"""Validate Wave1068 CRTBuilding/CRTMesh read-only review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1068-rtbuilding-rtmesh-lifecycle-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_rtbuilding_rtmesh_lifecycle_review_wave1068_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1068_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified"
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
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "rtmesh.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

TARGETS = {
    "0x004db850": ("CRTBuilding__Destructor", "void __fastcall CRTBuilding__Destructor(void * this)"),
    "0x004db8d0": ("CRTBuilding__ScalarDeletingDestructor", "void * __thiscall CRTBuilding__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x004dba40": ("CRTBuilding__VFuncSlot10_PickRandomLinkedEntry", "void * __fastcall CRTBuilding__VFuncSlot10_PickRandomLinkedEntry(void * this)"),
    "0x004dc370": ("CRTMesh__Init", "void __thiscall CRTMesh__Init(void * this, void * init)"),
    "0x004dc950": ("CRTMesh__Destructor", "void __fastcall CRTMesh__Destructor(void * this)"),
    "0x004dcb00": ("CRTMesh__FreePoseData", "void __fastcall CRTMesh__FreePoseData(void * poseData)"),
    "0x004dcb70": ("CRTMesh__ScalarDeletingDestructor", "void * __thiscall CRTMesh__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x004dd0c0": ("CRTMesh__CleanupAllEffects", "void __cdecl CRTMesh__CleanupAllEffects(void)"),
    "0x004dd6b0": ("CRTMesh__SetQualityLevel", "void __cdecl CRTMesh__SetQualityLevel(int qualityLevel)"),
    "0x004dd770": ("CRTMesh__GetQualityLevel", "int __cdecl CRTMesh__GetQualityLevel(void)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "rtbuilding-rtmesh-wave496",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}

TAG_EXTRAS = {
    "0x004db850": {"rtbuilding", "rtmesh", "destructor", "vtable-referenced"},
    "0x004db8d0": {"rtbuilding", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected"},
    "0x004dba40": {"rtbuilding", "vtable-slot-10", "name-corrected", "linked-list", "random-selection"},
    "0x004dc370": {"rtmesh", "init", "vtable-slot-1", "console-vars", "mesh-pose", "imposter", "particle-effects"},
    "0x004dc950": {"rtmesh", "destructor", "linked-list", "particle-effects", "resource-free"},
    "0x004dcb00": {"rtmesh", "mesh-pose", "resource-free"},
    "0x004dcb70": {"rtmesh", "scalar-deleting-destructor", "vtable-slot-0"},
    "0x004dd0c0": {"rtmesh", "static-helper", "linked-list", "particle-effects", "resource-free"},
    "0x004dd6b0": {"rtmesh", "static-helper", "lod", "quality-level"},
    "0x004dd770": {"rtmesh", "static-helper", "lod", "quality-level"},
}

COMMENT_TOKENS = {
    "0x004db850": ("Wave496 signature/comment hardening", "0x005de9c0", "this+0x54 -> +0x170", "CRTMesh__Destructor"),
    "0x004db8d0": ("CRTBuilding vtable 0x005de9c0 slot 0", "flags bit 0", "CDXMemoryManager__Free"),
    "0x004dba40": ("CRTBuilding vtable 0x005de9c0 slot 10", "rand() % count", "entry+0x08 next pointer"),
    "0x004dc370": ("CRTMesh vtable 0x005deb1c slot 1", "one-time registers", "mesh-pose arrays", "optionally creates an imposter"),
    "0x004dc950": ("CRTMesh vtable to 0x005deb1c", "DAT_0083cd5c/DAT_0083cd60", "CRTMesh__FreePoseData", "mesh+0x170"),
    "0x004dcb00": ("+0x00/+0x04/+0x08/+0x0c", "CDXMemoryManager__Free", "nulling each slot"),
    "0x004dcb70": ("CRTMesh vtable 0x005deb1c slot 0", "flags bit 0", "CDXMemoryManager__Free"),
    "0x004dd0c0": ("DAT_0083cd5c", "DAT_0083cd60", "CParticleManager__RemoveFromGlobalList"),
    "0x004dd6b0": ("quality setter", "g_MeshQualityDistance", "g_MeshLodBias", "_g_MeshQualityScaleFactor"),
    "0x004dd770": ("g_MeshQualityDistance", "returns 0", "PauseMenu/CPauseMenu quality UI"),
}

EXPECTED_XREFS = {
    ("0x004db850", "0x004db8d3", "UNCONDITIONAL_CALL"),
    ("0x004db8d0", "0x005de9c0", "DATA"),
    ("0x004dba40", "0x005de9e8", "DATA"),
    ("0x004dc370", "0x005deb20", "DATA"),
    ("0x004dc370", "0x004db8f9", "UNCONDITIONAL_CALL"),
    ("0x004dc950", "0x004dcb73", "UNCONDITIONAL_CALL"),
    ("0x004dc950", "0x004db871", "UNCONDITIONAL_CALL"),
    ("0x004dcb00", "0x004dca04", "UNCONDITIONAL_CALL"),
    ("0x004dcb70", "0x005deb1c", "DATA"),
    ("0x004dd0c0", "0x0053e7c6", "UNCONDITIONAL_CALL"),
    ("0x004dd6b0", "0x004cef55", "UNCONDITIONAL_CALL"),
    ("0x004dd770", "0x004cead3", "UNCONDITIONAL_CALL"),
    ("0x004dd770", "0x004d11f3", "UNCONDITIONAL_CALL"),
    ("0x004dd770", "0x004cef60", "UNCONDITIONAL_CALL"),
}

EXPECTED_VTABLE = {
    ("005de9c0", "0", "004db8d0", "CRTBuilding__ScalarDeletingDestructor", "OK"),
    ("005de9c0", "10", "004dba40", "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry", "OK"),
    ("005deb1c", "0", "004dcb70", "CRTMesh__ScalarDeletingDestructor", "OK"),
    ("005deb1c", "1", "004dc370", "CRTMesh__Init", "OK"),
    ("005deb1c", "4", "004de060", "SharedVFunc__ReturnResourceField150_004de060", "OK"),
}

CONTEXT_MISSING = {"0x004dabb0", "0x004dabc0", "0x004dac10", "0x004dc0d0", "0x004dc2c0", "0x004dc560", "0x004dd810"}

DOC_TOKENS = (
    "Wave1068",
    "rtbuilding-rtmesh-lifecycle-review-wave1068",
    "0x004db850 CRTBuilding__Destructor",
    "0x004db8d0 CRTBuilding__ScalarDeletingDestructor",
    "0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
    "0x004dc370 CRTMesh__Init",
    "0x004dc950 CRTMesh__Destructor",
    "0x004dd0c0 CRTMesh__CleanupAllEffects",
    "0x004dd6b0 CRTMesh__SetQualityLevel",
    "0x004dd770 CRTMesh__GetQualityLevel",
    "812/1408 = 57.67%",
    "1258/1560 = 80.64%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime render behavior proven",
    "runtime rtmesh behavior proven",
    "runtime lod behavior proven",
    "rebuild parity proven",
    "exact source-layout identity proven",
    "exact source identity proven",
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
        "primary-metadata.tsv": 10,
        "primary-tags.tsv": 10,
        "primary-xrefs.tsv": 14,
        "primary-instructions.tsv": 788,
        "primary-decompile/index.tsv": 10,
        "context-metadata.tsv": 23,
        "context-tags.tsv": 23,
        "context-xrefs.tsv": 60,
        "context-instructions.tsv": 2661,
        "context-decompile/index.tsv": 23,
        "vtable.tsv": 48,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    xrefs = {(norm(row["target_addr"]), norm(row["from_addr"]), row["ref_type"]) for row in read_tsv(BASE / "primary-xrefs.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            expected = COMMON_TAGS | TAG_EXTRAS[address]
            require(expected.issubset(actual), f"tags missing at {address}: {expected - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref tuple: {expected}", failures)

    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    missing = {address for address, row in context.items() if row.get("status") == "MISSING"}
    require(missing == CONTEXT_MISSING, f"context missing set mismatch: {missing}", failures)

    vtable = {
        (row["vtable"], row["slot_index"], row["pointer_addr"], row["function_name"], row["status"])
        for row in read_tsv(BASE / "vtable.tsv")
    }
    for expected in EXPECTED_VTABLE:
        require(expected in vtable, f"missing vtable tuple: {expected}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=10 found=10 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "primary-xrefs.log": "Wrote 14 rows",
        "primary-instructions.log": "targets=10 missing=0",
        "primary-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=23 found=16 missing=7",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=7",
        "context-xrefs.log": "Wrote 60 rows",
        "context-instructions.log": "targets=23 missing=7",
        "context-decompile.log": "targets=23 dumped=16 missing=7 failed=0",
        "vtable.log": "ExportVtableSlots complete: targets=2 rows=48",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(float(backup.get("totalBytes")) == 174721927.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-rtbuilding-rtmesh-lifecycle-review-wave1068")
        == r"py -3 tools\ghidra_rtbuilding_rtmesh_lifecycle_review_wave1068_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1068-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1068 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1068 rtbuilding rtmesh lifecycle review" for row in ledger), "missing ledger row", failures)
    require(any(row.get("task") == "Wave1068 rtbuilding rtmesh lifecycle review" and row.get("attempt_id") == 20650 for row in attempts), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1068 CRTBuilding/CRTMesh lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1068 CRTBuilding/CRTMesh lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
