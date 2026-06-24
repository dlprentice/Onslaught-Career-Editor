#!/usr/bin/env python3
"""Validate the Engine / Platform / Math / Memory support proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "engine-platform-math-memory-support-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "engine-platform-math-memory-support-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "engine_platform_math_memory_support_proof_plan_2026-06-08.md"
ENGINE_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "engine-platform-support-static-review-2026-05-26.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "engine-platform-math-memory-support-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

ANCHOR_TOKENS = (
    "Engine / Platform / Math / Memory Support Proof Plan",
    "Status: active public-safe proof plan, not runtime proof",
    "engine-platform-math-memory-support-proof-plan",
    "engine-platform-support-static-review-wave909",
    "crt-fpu-runtime-tail-review-wave1041",
    "memory-heap-allocator-review-wave1042",
    "render-state-matrix-support-review-wave1095",
    "wave1214-math-color-screen-dispatch-current-risk-review",
    "`425` selected function rows",
    "`23` families",
    "engine-core 115",
    "math-vector 84",
    "console-monitor 78",
    "memory-buffer 66",
    "platform-app 53",
    "render-state-shared 29",
    "CEngine__Init",
    "CEngine__Shutdown",
    "CDXEngine__SetProjectionMatrix",
    "CDXEngine__SetWorldMatrixElements",
    "CD3DApplication__BuildDeviceList",
    "Platform__HandleDeviceLostAndRestore",
    "PLATFORM__ProcessSystemMessages",
    "PCPlatform__WriteSaveFile",
    "CConsole__RegisterBuiltinCommands",
    "CConsole__ExecuteBufferedCommandSlot",
    "CMonitor__AddDeletionEvent",
    "CMonitor__Process",
    "CSPtrSet__Clear",
    "CDXMemoryManager__Alloc",
    "CDXMemoryManager__Free",
    "CMemoryHeap__Init",
    "CMemoryHeap__Alloc",
    "CMemoryHeap__Free",
    "CMemoryHeap__AddToFreeList",
    "OID__CreateObject",
    "OID__FreeObject_Callback",
    "Math__InvLerpClamp01",
    "MathMatrix3x3__Determinant",
    "Mat34__TransformVec3ByBasisToOut",
    "Vec3__NormalizeInPlace",
    "Vec3__Dot",
    "Color32__LerpArgb",
    "D3DStateCache__SetStateCached",
    "D3DStateCache__SetSlotMode4or5",
    "CDXEngine__ApplyPendingRenderState",
    "CDXEngine__ApplyCachedLight",
    "CRT__InitRuntimeFromStoredFrameGlobals",
    "CRT__FpuIntrinsicDispatch2Thunk",
    "CRT__SetErrnoForFpSourceKind",
    "CRT__FloatDispatchAmsgExitCode2Thunk",
    "CRT__AcosDispatch_ST0",
    "pure math helper equivalence",
    "render-state/matrix support",
    "Memory allocator proof design",
    "Monitor/safe-pointer proof design",
    "Platform/file I/O proof design",
    "Console command proof design",
    "CRT/FPU side-effect proof design",
    r"G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified",
    r"G:\GhidraBackups\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified",
    r"G:\GhidraBackups\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified",
    r"G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified",
    r"G:\GhidraBackups\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified",
)

READINESS_TOKENS = (
    "Engine / Platform / Math / Memory Support Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a runtime test",
    "not a screenshot/capture proof",
    "not a Direct3D device proof",
    "not an allocator/OOM proof",
    "not a console execution proof",
    "not a platform filesystem/registry proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
    "No runtime device handling",
    "runtime platform I/O",
    "allocator/OOM behavior",
    "console command execution behavior",
    "monitor/safe-pointer behavior",
    "FPU/CRT side effects",
)

FORBIDDEN_PHRASES = (
    "runtime device handling proven",
    "runtime platform i/o proven",
    "runtime allocator behavior proven",
    "allocator/oom behavior proven",
    "runtime console command execution behavior proven",
    "runtime monitor/safe-pointer behavior proven",
    "runtime fpu/crt side effects proven",
    "visual qa complete",
    "exact source-body identity proven",
    "bea patching behavior proven",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "runtime proof complete",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    lower = text.lower()
    for token in (*STATIC_TOKENS, *ANCHOR_TOKENS):
        require(token in text, f"plan missing token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"plan overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"plan leaks public-forbidden token: {token}", failures)
    require(read_text(LORE_PLAN) == text, "lore proof-plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    lower = text.lower()
    for token in (*STATIC_TOKENS, *READINESS_TOKENS):
        require(token in text, f"readiness missing token: {token}", failures)
    for token in (
        "engine-platform-support-static-review-wave909",
        "crt-fpu-runtime-tail-review-wave1041",
        "memory-heap-allocator-review-wave1042",
        "render-state-matrix-support-review-wave1095",
        "wave1214-math-color-screen-dispatch-current-risk-review",
        "copied-profile, copied-file, or app-owned artifact-root work",
        "Stop on installed-game mutation need",
    ):
        require(token in text, f"readiness missing anchor token: {token}", failures)
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"readiness overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"readiness leaks public-forbidden token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (ENGINE_STATIC, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        for phrase in FORBIDDEN_PHRASES:
            require(phrase not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require("Engine / platform / math / memory support proof plan" in backlog, "backlog missing engine/platform slice", failures)
    require("proof plan complete, not runtime proof" in backlog, "backlog missing engine/platform proof-plan status", failures)
    require("Completed Engine / platform / math / memory support proof-plan slice" in backlog, "backlog missing completed engine/platform slice", failures)
    require("Completed Audio / media / cutscene / camera proof-plan slice" in backlog, "backlog missing completed audio/media slice", failures)
    require("Do not broaden into device handling, platform I/O, allocator/OOM, console execution, monitor/safe-pointer behavior, CRT/FPU side effects, visual QA, Godot, patching, broad runtime proof, or rebuild parity." in backlog, "backlog missing engine/platform broadening boundary", failures)

    mapped = read_text(MAPPED)
    require("Completed Engine / platform / math / memory support proof-plan slice" in mapped, "mapped systems missing completed engine/platform slice", failures)
    require("Completed Audio / media / cutscene / camera proof-plan slice" in mapped, "mapped systems missing completed audio/media slice", failures)
    require("Engine / platform / memory / CRT" in mapped and PLAN_LINK in mapped, "mapped systems missing engine/platform row link", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\engine_platform_math_memory_support_proof_plan_probe.py --check"
    actual = package["scripts"].get("test:engine-platform-math-memory-support-proof-plan")
    require(actual == expected, "missing package Engine/platform proof-plan script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_readiness(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("Engine / Platform / Math / Memory support proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Engine / Platform / Math / Memory support proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
