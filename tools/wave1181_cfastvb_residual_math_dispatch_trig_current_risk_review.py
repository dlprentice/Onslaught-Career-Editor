#!/usr/bin/env python3
"""Validate Wave1181 CFastVB residual math/dispatch/trig current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1181-cfastvb-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1181_cfastvb_residual_math_dispatch_trig_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-111618_post_wave1181_cfastvb_residual_current_risk_review_verified"

TARGETS = {
    "0x00575dc9": ("CFastVB__HermiteInterpolateVec3", "int CFastVB__HermiteInterpolateVec3(void)"),
    "0x0057770b": ("CFastVB__BuildTransformMatrixWithOffsets", "int CFastVB__BuildTransformMatrixWithOffsets(void)"),
    "0x00596589": (
        "CFastVB__SolveScalarEndpointPairFromSamples",
        "void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)",
    ),
    "0x005a3a40": ("CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40", "int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40(void)"),
    "0x005a3ca0": ("CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0", "int CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0(void)"),
    "0x005a3f00": ("CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00", "int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00(void)"),
    "0x005a4160": ("CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160", "int CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160(void)"),
    "0x005a4480": ("CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480", "int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480(void)"),
    "0x005a46fc": ("CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc", "int CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc(void)"),
    "0x005a4795": ("CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795", "int CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795(void)"),
    "0x005a4836": ("CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836", "int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836(void)"),
    "0x005a4a52": ("CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52", "int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52(void)"),
    "0x005a4fee": ("CFastVB__DispatchOp_SlotB0_005a4fee", "int CFastVB__DispatchOp_SlotB0_005a4fee(void)"),
    "0x005a50f9": ("CFastVB__DispatchOp_SlotE0_005a50f9", "int CFastVB__DispatchOp_SlotE0_005a50f9(void)"),
    "0x005a5bd7": ("CFastVB__DispatchOp_Slot0C_005a5bd7", "int CFastVB__DispatchOp_Slot0C_005a5bd7(void)"),
    "0x005a5e09": ("CFastVB__DispatchOp_Slot2C_005a5e09", "int CFastVB__DispatchOp_Slot2C_005a5e09(void)"),
    "0x005a5ed8": ("CFastVB__DispatchOp_Slot68_005a5ed8", "int CFastVB__DispatchOp_Slot68_005a5ed8(void)"),
    "0x005a5f28": ("CFastVB__DispatchOp_Slot6C_005a5f28", "int CFastVB__DispatchOp_Slot6C_005a5f28(void)"),
    "0x005a6013": ("CFastVB__DispatchOp_Slot70_005a6013", "int CFastVB__DispatchOp_Slot70_005a6013(void)"),
    "0x005b8ca0": ("CFastVB__FastTrigPairApprox_Scalar", "uint CFastVB__FastTrigPairApprox_Scalar(void)"),
    "0x005b8da0": ("CFastVB__FastSinApprox_Scalar_005b8da0", "uint CFastVB__FastSinApprox_Scalar_005b8da0(void)"),
}

EXPECTED_DATA_XREFS = {
    "0x00575dc9": "0x00657114",
    "0x0057770b": "0x006570f4",
    "0x005a3a40": "0x005986cf",
    "0x005a3ca0": "0x005986d9",
    "0x005a3f00": "0x005986e3",
    "0x005a4160": "0x005986bb",
    "0x005a4480": "0x005986c5",
    "0x005a46fc": "0x0059850d",
    "0x005a4795": "0x00598514",
    "0x005a4836": "0x00598530",
    "0x005a4a52": "0x005986a6",
    "0x005a4fee": "0x005985e0",
    "0x005a50f9": "0x00598630",
    "0x005a5bd7": "0x005984a4",
    "0x005a5e09": "0x005984d5",
    "0x005a5ed8": "0x0059853e",
    "0x005a5f28": "0x00598545",
    "0x005a6013": "0x0059854c",
}

DOC_TOKENS = (
    "Wave1181",
    "wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review",
    "750/1179 = 63.61%",
    "21 CFastVB residual math/dispatch/trig current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 429",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "Codex root final judgment",
    "no Cursor/Composer",
    "residual CFastVB",
    "hidden EBX",
    "unreliable packed-register return",
    "0x005a4980 internal branch target",
    "Wave969",
    "Wave970",
    "Wave971",
    "Wave737",
    "Wave887",
    "Wave888",
    "Wave701",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "40 xref rows",
    "2013 instruction rows",
    "CFastVB__HermiteInterpolateVec3",
    "CFastVB__BuildTransformMatrixWithOffsets",
    "CFastVB__SolveScalarEndpointPairFromSamples",
    "CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40",
    "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836",
    "CFastVB__DispatchOp_SlotB0_005a4fee",
    "CFastVB__FastTrigPairApprox_Scalar",
    "CFastVB__FastSinApprox_Scalar_005b8da0",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime math/render behavior proven",
    "exact dispatch-table schema proven",
    "hidden abi is complete",
    "rebuild parity proven",
    "no noticeable difference proven",
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


def normalize(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "post-metadata.tsv": 21,
        "post-tags.tsv": 21,
        "post-xrefs.tsv": 40,
        "post-instructions.tsv": 2013,
        "post-decompile/index.tsv": 21,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_by_target = {}
    xref_counts = Counter()
    for row in xrefs:
        target = normalize(row.get("target_addr", ""))
        xref_counts[target] += 1
        xref_by_target.setdefault(target, []).append(row)

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Static retail Ghidra" in row.get("comment", "") or "Static metadata only" in row.get("comment", ""), f"missing static-boundary comment {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in tag_row.get("tags", ""), f"missing retail evidence tag {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    for address, expected_from in EXPECTED_DATA_XREFS.items():
        rows = xref_by_target.get(address, [])
        require(len(rows) == 1, f"expected one DATA xref for {address}", failures)
        if rows:
            require(normalize(rows[0].get("from_addr", "")) == expected_from, f"data xref source mismatch {address}", failures)
            require(rows[0].get("ref_type") == "DATA", f"data xref type mismatch {address}", failures)

    scalar_xrefs = xref_by_target.get("0x00596589", [])
    require(len(scalar_xrefs) == 1, "scalar endpoint xref count mismatch", failures)
    if scalar_xrefs:
        require(normalize(scalar_xrefs[0].get("from_addr", "")) == "0x00597cfb", "scalar endpoint xref source mismatch", failures)
        require(scalar_xrefs[0].get("from_function") == "CFastVB__PackScalarBlock_InterpolatedEndpoints", "scalar endpoint caller mismatch", failures)

    require(xref_counts["0x005b8ca0"] == 14, "fast trig-pair call count mismatch", failures)
    require(xref_counts["0x005b8da0"] == 7, "fast sine call count mismatch", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "post-metadata.log": "targets=21 found=21 missing=0",
        "post-tags.log": "rows=21 missing=0",
        "post-xrefs.log": "Wrote 40 rows",
        "post-instructions.log": "Wrote 2013 function-body instruction rows",
        "post-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176098183, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1181 CFastVB Residual Math / Dispatch / Trig Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 750, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "63.61%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 429, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review", "latest review tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        FASTVB_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1181 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review")
        == r"py -3 tools\wave1181_cfastvb_residual_math_dispatch_trig_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1181 CFastVB residual math/dispatch/trig current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1181 CFastVB residual math/dispatch/trig current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
