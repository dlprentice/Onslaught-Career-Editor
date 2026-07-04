#!/usr/bin/env python3
"""Validate Wave1155 CFastVB Wave717-722 supersession evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1155-cfastvb-wave717-722-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1155-cfastvb-wave717-722-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1155_cfastvb_wave717_722_current_risk_supersession_2026-06-05.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FASTVB_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

PRIOR_READINESS = {
    "Wave717": ROOT / "release" / "readiness" / "ghidra_cfastvb_transform_dispatch_head_wave717_2026-05-22.md",
    "Wave718": ROOT / "release" / "readiness" / "ghidra_cfastvb_scalar_transform_core_wave718_2026-05-22.md",
    "Wave719": ROOT / "release" / "readiness" / "ghidra_cfastvb_matrix_quaternion_core_wave719_2026-05-22.md",
    "Wave720": ROOT / "release" / "readiness" / "ghidra_cfastvb_quaternion_tail_wave720_2026-05-22.md",
    "Wave721": ROOT / "release" / "readiness" / "ghidra_cfastvb_matrix_rotation_continuation_wave721_2026-05-22.md",
    "Wave722": ROOT / "release" / "readiness" / "ghidra_cfastvb_packed_vec2_quaternion_tail_wave722_2026-05-22.md",
}

PRIOR_BACKUPS = {
    "Wave717": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified",
    "Wave718": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified",
    "Wave719": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified",
    "Wave720": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified",
    "Wave721": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified",
    "Wave722": r"[maintainer-local-ghidra-backup-root]\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified",
}

LATEST_GHIDRA_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified"

TARGETS = [
    ("Wave717", "0x0059f360", "CFastVB__DispatchOp_TransformVec4_0059f360"),
    ("Wave717", "0x0059f3d9", "CFastVB__DispatchOp_NormalizeVec4_0059f3d9"),
    ("Wave717", "0x0059f473", "CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473"),
    ("Wave717", "0x0059f4f1", "CFastVB__DispatchOp_EulerToQuaternion_0059f4f1"),
    ("Wave717", "0x0059f5b3", "CFastVB__BuildOrthonormalBasisFromCovariance"),
    ("Wave717", "0x0059f6dd", "CFastVB__BroadcastMatrix4x4ToSIMDLanes"),
    ("Wave718", "0x005a0b22", "CFastVB__ConvertHalfToFloatArray_SSE"),
    ("Wave718", "0x005a0df6", "CFastVB__ComputeAdjugateVec4_PackedA"),
    ("Wave718", "0x005a0eb6", "CFastVB__NormalizeVec4_ReciprocalSqrt"),
    ("Wave718", "0x005a14a5", "CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5"),
    ("Wave718", "0x005a15a5", "CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5"),
    ("Wave718", "0x005a16b1", "CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1"),
    ("Wave718", "0x005a1786", "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786"),
    ("Wave718", "0x005a1889", "CFastVB__DispatchOp_NormalizeVec3_005a1889"),
    ("Wave718", "0x005a1979", "CFastVB__DispatchOp_NormalizeVec4_005a1979"),
    ("Wave718", "0x005a1a8e", "CFastVB__BuildMatrix4x4FromQuaternion"),
    ("Wave719", "0x005a298f", "CFastVB__ConvertHalfToFloatArray_SIMD"),
    ("Wave719", "0x005a2a61", "CFastVB__DispatchOp_TransformVec2ByMatrix4"),
    ("Wave719", "0x005a2b2d", "CFastVB__InvertMatrix4x4_WithDeterminant"),
    ("Wave719", "0x005a2e29", "CFastVB__ComputeAdjugateVec4_PackedB"),
    ("Wave719", "0x005a2ee9", "CFastVB__DispatchOp_Determinant4x4_005a2ee9"),
    ("Wave719", "0x005a2ff4", "CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4"),
    ("Wave719", "0x005a30f4", "CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4"),
    ("Wave719", "0x005a3200", "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200"),
    ("Wave719", "0x005a32d4", "CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4"),
    ("Wave719", "0x005a3508", "CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508"),
    ("Wave719", "0x005a36cf", "CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf"),
    ("Wave719", "0x005a3791", "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791"),
    ("Wave720", "0x005a47f2", "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle"),
    ("Wave720", "0x005a4d2c", "CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c"),
    ("Wave720", "0x005a4d98", "CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98"),
    ("Wave720", "0x005a5052", "CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052"),
    ("Wave721", "0x005a62bf", "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf"),
    ("Wave721", "0x005a7cf0", "CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector"),
    ("Wave721", "0x005a8f5d", "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d"),
    ("Wave721", "0x005a9637", "CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637"),
    ("Wave721", "0x005a99f8", "CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8"),
    ("Wave721", "0x005a9a5f", "CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f"),
    ("Wave721", "0x005a9ced", "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced"),
    ("Wave721", "0x005a9d78", "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78"),
    ("Wave721", "0x005a9f3f", "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f"),
    ("Wave722", "0x005aa480", "CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480"),
    ("Wave722", "0x005aa73b", "CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b"),
    ("Wave722", "0x005aa790", "CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790"),
    ("Wave722", "0x005aa7c9", "CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9"),
    ("Wave722", "0x005ab00b", "CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b"),
]

EXCLUDED_ALREADY_COUNTED = {
    "0x005a0f50",
    "0x005a1002",
    "0x005a1087",
    "0x005a112c",
    "0x005a11df",
    "0x005a1279",
    "0x005a13f7",
    "0x005a38c0",
    "0x005a3980",
    "0x005a40c0",
    "0x005a4ecf",
    "0x005a4f5c",
    "0x005a519e",
    "0x005a647f",
    "0x005a7e09",
    "0x0059f857",
    "0x0059fa5d",
    "0x0059fbeb",
    "0x0059fd51",
    "0x0059fe61",
    "0x005a009f",
    "0x005a026f",
    "0x005a04a0",
    "0x005a7617",
}

DOC_TOKENS = (
    "Wave1155",
    "wave1155-cfastvb-wave717-722-current-risk-supersession",
    "424/1179 = 35.96%",
    "46 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 755",
    "current risk candidates: 6166",
    "CFastVB Wave717-Wave722 current-risk supersession",
    "no new Ghidra export",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CFastVB__DispatchOp_TransformVec4_0059f360",
    "CFastVB__ConvertHalfToFloatArray_SSE",
    "CFastVB__ConvertHalfToFloatArray_SIMD",
    "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle",
    "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
    "CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b",
    PRIOR_BACKUPS["Wave717"],
    PRIOR_BACKUPS["Wave722"],
    LATEST_GHIDRA_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "rebuild parity proven",
    "exact layout proven",
    "hidden abi proven",
)

STALE_CURRENT_TOKENS = (
    "Current Ghidra RE status: Wave1154",
    "Wave1154 (`wave1154-unitai-deploy-target-current-risk-review`) is the latest completed Ghidra review",
    "Wave1108 current focused accounting is now `378/1179 = 32.06%`",
    "currently `378/1179 = 32.06%`",
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


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_current_focused_membership(failures: list[str]) -> None:
    _queue_rows, _ranked, focused_rows, _signal_counts = wave1108_current_risk_rank.build_rankings()
    focused = {normalize_address(str(row.get("address", ""))): row for row in focused_rows}
    require(len(focused) == 1178, "Wave1108 focused live row count mismatch", failures)
    target_addresses = {address for _, address, _ in TARGETS}
    require(len(target_addresses) == 46, "target set count mismatch", failures)
    require(not (target_addresses & EXCLUDED_ALREADY_COUNTED), "target set overlaps Wave1109/Wave1110 counted rows", failures)
    for wave, address, name in TARGETS:
        row = focused.get(address)
        require(row is not None, f"focused row missing for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"focused name mismatch at {address}", failures)
            require(str(row.get("score")) == "20", f"focused score mismatch at {address}", failures)
        require(wave in PRIOR_READINESS, f"unknown prior wave for {address}: {wave}", failures)


def check_prior_evidence(failures: list[str]) -> None:
    prior_texts = {wave: read_text(path) for wave, path in PRIOR_READINESS.items()}
    for wave, backup in PRIOR_BACKUPS.items():
        require(contains_token(prior_texts[wave], backup), f"missing backup token in {wave} readiness", failures)
        require("DiffCount=0" in prior_texts[wave] or "DiffCount=0" in prior_texts[wave].replace("`", ""), f"missing diff verification token in {wave}", failures)
    for wave, address, name in TARGETS:
        text = prior_texts[wave]
        require(address in text, f"missing prior evidence address in {wave}: {address}", failures)
        require(name in text, f"missing prior evidence name in {wave}: {name}", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1155 CFastVB Wave717-722 current-risk supersession", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1155-cfastvb-wave717-722-current-risk-supersession", "latest tag mismatch", failures)
    require(latest.get("backup") == LATEST_GHIDRA_BACKUP, "latest Ghidra backup mismatch", failures)
    require(latest.get("artifactCommit") == "pending Wave1155 commit", "latest artifact commit mismatch", failures)
    require(current.get("focusedReviewed") == 424, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "35.96%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 755, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1155 CFastVB Wave717-722 current-risk supersession", "progress latest review mismatch", failures)

    docs = {
        "wave1155 note": read_text(NOTE),
        "wave1155 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "function coverage": read_text(FUNCTION_COVERAGE),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "FastVB index": read_text(FASTVB_INDEX),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
        "progress": read_text(PROGRESS),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)
        for stale in STALE_CURRENT_TOKENS:
            require(stale not in text, f"stale current token in {name}: {stale}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1155 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1155-cfastvb-wave717-722-current-risk-supersession")
        == r"py -3 tools\wave1155_cfastvb_wave717_722_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_current_focused_membership(failures)
    check_prior_evidence(failures)
    check_docs_progress(failures)

    if failures:
        print("Wave1155 CFastVB Wave717-722 supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1155 CFastVB Wave717-722 supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
