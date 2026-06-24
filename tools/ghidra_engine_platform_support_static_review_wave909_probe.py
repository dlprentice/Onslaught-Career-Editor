#!/usr/bin/env python3
"""Validate Wave909 engine/platform support static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave909-engine-platform-support-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_engine_platform_support_static_review_wave909_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "engine-platform-support-static-review-2026-05-26.md"
STATIC_SYSTEM = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified"

EXPECTED_FAMILIES = {
    "CDXEngine": 60,
    "CEngine": 55,
    "Math": 50,
    "CConsole": 31,
    "CMonitor": 27,
    "PCPlatform": 19,
    "CD3DApplication": 18,
    "SharedVFunc": 18,
    "Vec3": 18,
    "CMemoryHeap": 17,
    "CSPtrSet": 16,
    "CDXMemBuffer": 15,
    "OID": 14,
    "D3DStateCache": 11,
    "CDXMemoryManager": 10,
    "CFlexArray": 10,
    "Mat34": 10,
    "PLATFORM": 9,
    "Platform": 7,
    "CGenericActiveReader": 4,
    "MathMatrix3x3": 4,
    "MathMatrix3x4": 1,
    "CEulerAngles": 1,
}

EXPECTED_CLUSTERS = {
    "engine-core": 115,
    "math-vector": 84,
    "console-monitor": 78,
    "memory-buffer": 66,
    "platform-app": 53,
    "render-state-shared": 29,
}

REQUIRED_ANCHORS = (
    "CDXEngine__UpdateWrappedThingPositionsAndDistance",
    "CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite",
    "CDXEngine__SetProjectionMatrix",
    "CDXEngine__SetWorldMatrixElements",
    "CEngine__Init",
    "CEngine__Shutdown",
    "CEngine__GetViewMatrixFromCamera",
    "CD3DApplication__Init",
    "CD3DApplication__Create",
    "CD3DApplication__BuildDeviceList",
    "Platform__HandleDeviceLostAndRestore",
    "Platform__AsyncSaveCareer",
    "PLATFORM__ProcessSystemMessages",
    "PLATFORM__BeginScene",
    "PCPlatform__InitAsyncMusicStream",
    "PCPlatform__WriteSaveFile",
    "CConsole__RegisterBuiltinCommands",
    "CConsole__ExecuteBufferedCommandSlot",
    "CMonitor__AddDeletionEvent",
    "CMonitor__Process",
    "CGenericActiveReader__SetReader",
    "CSPtrSet__Clear",
    "CDXMemBuffer__OpenReadMode11",
    "CDXMemBuffer__SetBufferSize",
    "CDXMemoryManager__Alloc",
    "CDXMemoryManager__Free",
    "CMemoryHeap__Init",
    "CMemoryHeap__FreeTiny",
    "CFlexArray__Add",
    "OID__CreateObject",
    "OID__FreeObject_Callback",
    "Math__InvLerpClamp01",
    "Math__IsFloatDiffOutsideTolerance",
    "MathMatrix3x3__Determinant",
    "MathMatrix3x4__AssignFromEightScalars",
    "Mat34__TransformVec3ByBasisToOut",
    "Vec3__NormalizeInPlace",
    "Vec3__Dot",
    "D3DStateCache__SetStateCached",
    "SharedVFunc__ReturnZero_00405930",
)

CORE_ANCHORS = (
    "Wave909",
    "engine-platform-support-static-review-wave909",
    "static-coherent engine/platform/math/memory support core",
    "6113/6113 = 100.00%",
    "425",
    "23",
    "CDXEngine 60",
    "CEngine 55",
    "Math 50",
    "CConsole 31",
    "CMonitor 27",
    "PCPlatform 19",
    "CD3DApplication 18",
    "CMemoryHeap 17",
    "CSPtrSet 16",
    "CDXMemBuffer 15",
    BACKUP_PATH,
)

FUNCTION_DOCS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md": (
        "Wave909",
        "engine-platform-support-static-review-wave909",
        "CDXEngine__SetProjectionMatrix",
        "CEngine__Init",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Platform.cpp" / "_index.md": (
        "Wave909",
        "Platform__HandleDeviceLostAndRestore",
        "PLATFORM__ProcessSystemMessages",
        "Platform__AsyncSaveCareer",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md": (
        "Wave909",
        "PCPlatform__InitAsyncMusicStream",
        "PCPlatform__WriteSaveFile",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "d3dapp.cpp" / "_index.md": (
        "Wave909",
        "CD3DApplication__Init",
        "CD3DApplication__BuildDeviceList",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md": (
        "Wave909",
        "CConsole__RegisterBuiltinCommands",
        "CConsole__ExecuteBufferedCommandSlot",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md": (
        "Wave909",
        "CMonitor__AddDeletionEvent",
        "CGenericActiveReader__SetReader",
        "CSPtrSet__Clear",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SPtrSet.cpp" / "_index.md": (
        "Wave909",
        "CSPtrSet__Clear",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md": (
        "Wave909",
        "CDXMemoryManager__Alloc",
        "CMemoryHeap__Init",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md": (
        "Wave909",
        "Math__InvLerpClamp01",
        "Vec3__NormalizeInPlace",
        "MathMatrix3x3__Determinant",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md": (
        "Wave909",
        "OID__CreateObject",
        "OID__FreeObject_Callback",
        BACKUP_PATH,
    ),
}

OVERCLAIM_TOKENS = (
    "runtime device handling proven",
    "runtime allocator behavior proven",
    "runtime console behavior proven",
    "runtime monitor behavior proven",
    "every system is complete",
    "all systems complete",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6113, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6113, "quality TSV strict-clean count mismatch", failures)


def check_artifacts(failures: list[str]) -> None:
    baseline = read_json(BASE / "engine-platform-support-baseline.json")
    require(baseline.get("wave") == 909, "baseline wave mismatch", failures)
    require(baseline.get("tag") == "engine-platform-support-static-review-wave909", "baseline tag mismatch", failures)
    require(baseline.get("classification") == "static-coherent engine/platform/math/memory support core", "classification mismatch", failures)
    require(baseline.get("selectedRows") == 425, "selectedRows mismatch", failures)
    require(baseline.get("selectedFamilies") == 23, "selectedFamilies mismatch", failures)
    require(baseline.get("commentedRows") == 425, "commentedRows mismatch", failures)
    require(baseline.get("cleanSignatureRows") == 425, "cleanSignatureRows mismatch", failures)
    require(baseline.get("familyCounts") == EXPECTED_FAMILIES, "familyCounts mismatch", failures)
    require(baseline.get("clusterCounts") == EXPECTED_CLUSTERS, "clusterCounts mismatch", failures)
    require(baseline.get("missingRequiredAnchors") == [], "missing required anchors", failures)

    family_rows = read_tsv(BASE / "engine-platform-support-family-summary.tsv")
    cluster_rows = read_tsv(BASE / "engine-platform-support-cluster-summary.tsv")
    anchor_rows = read_tsv(BASE / "engine-platform-support-function-anchors.tsv")
    require(len(family_rows) == 23, "family summary row count mismatch", failures)
    require(len(cluster_rows) == 6, "cluster summary row count mismatch", failures)
    require(len(anchor_rows) == 425, "function anchor row count mismatch", failures)
    anchor_names = {row["name"] for row in anchor_rows}
    for name in REQUIRED_ANCHORS:
        require(name in anchor_names, f"missing function anchor: {name}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367 or backup.get("totalBytes") == 173247367.0, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in FUNCTION_DOCS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-engine-platform-support-static-review-wave909")
        == r"py -3 tools\ghidra_engine_platform_support_static_review_wave909_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_artifacts(failures)
    check_docs(failures)

    if failures:
        print("Wave909 engine/platform support static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave909 engine/platform support static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
