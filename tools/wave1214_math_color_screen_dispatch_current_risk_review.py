#!/usr/bin/env python3
"""Validate Wave1214 math/color/screen dispatch current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1214-math-color-screen-dispatch-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1214-math-color-screen-dispatch-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1214-math-color-screen-dispatch-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1214_math_color_screen_dispatch_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RENDER_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified"

TARGETS = {
    "0x004cab30": (
        "Color32__LerpArgb",
        "int __cdecl Color32__LerpArgb(uint from_argb, uint to_argb, float t)",
        ("004ca15d", "1.0 - t", "no clamp"),
    ),
    "0x004cac40": (
        "Math__InvLerpClamp01",
        "double __cdecl Math__InvLerpClamp01(float value, float min_value, float max_value)",
        ("004ca14c", "0..1", "no visible divide-by-zero guard"),
    ),
    "0x004cac80": (
        "CPDSelector__ConvertNormalizedToScreenCoords",
        "void __cdecl CPDSelector__ConvertNormalizedToScreenCoords(float normalized_x, float normalized_y)",
        ("004c9f2a", "004c9f43", "CRT__RoundDoubleWithFpuChecks"),
    ),
    "0x0055dcb0": (
        "CRT__AcosDispatch_ST0",
        "void CRT__AcosDispatch_ST0(void)",
        ("CRT__ExtractFiniteExponentMaskOrPassThrough", "CRT__Acos", "CBattleEngine__HandleAutoAim"),
    ),
    "0x00577267": (
        "Math__BuildTranslationMatrix4x4_Dispatch_Thunk",
        "void __stdcall Math__BuildTranslationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)",
        ("JMP", "0x00656f98", "CMeshRenderer__RenderMeshCore"),
    ),
    "0x005775bd": (
        "Math__BuildQuaternionRotationMatrix_Dispatch_Thunk",
        "void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch_Thunk(void * out_matrix4x4, void * quaternion_xyzw)",
        ("JMP", "0x00656fc8", "CTexture__BuildTransformMatrixWithOptionalOffsets"),
    ),
    "0x00577a38": (
        "Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk",
        "void __stdcall Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk(void * out_quaternion_xyzw, float angle_x, float angle_y, float angle_z)",
        ("JMP", "0x00656f94", "BuildQuaternionFromEulerAngles"),
    ),
    "0x00577ea4": (
        "Math__InterpolateVec4ByRatio_Dispatch_Thunk",
        "void __stdcall Math__InterpolateVec4ByRatio_Dispatch_Thunk(void * out_vec4, void * from_vec4, void * to_vec4, float ratio)",
        ("JMP", "0x00656fbc", "Math__BezierBlendVec4"),
    ),
}

TARGET_XREFS = {
    "0x004cab30": (("004ca15d", "UNCONDITIONAL_CALL"),),
    "0x004cac40": (("004ca14c", "UNCONDITIONAL_CALL"),),
    "0x004cac80": (("004c9f2a", "UNCONDITIONAL_CALL"), ("004c9f43", "UNCONDITIONAL_CALL")),
    "0x0055dcb0": (
        ("0040b772", "UNCONDITIONAL_CALL"),
        ("0040b3e3", "UNCONDITIONAL_CALL"),
        ("0040d1d9", "UNCONDITIONAL_CALL"),
        ("00509686", "UNCONDITIONAL_CALL"),
        ("004bd8b4", "UNCONDITIONAL_CALL"),
        ("00419c16", "UNCONDITIONAL_CALL"),
        ("004db3e7", "UNCONDITIONAL_CALL"),
    ),
    "0x00577267": (("0054af55", "UNCONDITIONAL_CALL"), ("0054af7a", "UNCONDITIONAL_CALL")),
    "0x005775bd": (
        ("00577773", "UNCONDITIONAL_CALL"),
        ("00579267", "UNCONDITIONAL_CALL"),
        ("00579300", "UNCONDITIONAL_CALL"),
        ("005794a9", "UNCONDITIONAL_CALL"),
    ),
    "0x00577a38": (("0057925b", "UNCONDITIONAL_CALL"),),
    "0x00577ea4": (
        ("00577fce", "UNCONDITIONAL_CALL"),
        ("00577fe4", "UNCONDITIONAL_CALL"),
        ("00578002", "UNCONDITIONAL_CALL"),
        ("00578099", "UNCONDITIONAL_CALL"),
        ("005780af", "UNCONDITIONAL_CALL"),
        ("005780c9", "UNCONDITIONAL_CALL"),
    ),
}

DOC_TOKENS = (
    "Wave1214",
    "wave1214-math-color-screen-dispatch-current-risk-review",
    "8 math/color/screen transform dispatch current-risk rows",
    "1133/1179 = 96.10%",
    "remaining active focused work: 46",
    "1164/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
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
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "58 xref rows",
    "175 instruction rows",
    "8 decompile rows",
    "43 context xref rows",
    "3821 context instruction rows",
    "20 context decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "mesh-resource-render-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    PARTICLE_DOC: ("Wave1214", "Color32__LerpArgb", "Math__InvLerpClamp01", "CPDSelector__ConvertNormalizedToScreenCoords", BACKUP),
    MATH_DOC: (
        "Wave1214",
        "Math__BuildTranslationMatrix4x4_Dispatch_Thunk",
        "Math__BuildQuaternionRotationMatrix_Dispatch_Thunk",
        "Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk",
        "Math__InterpolateVec4ByRatio_Dispatch_Thunk",
        BACKUP,
    ),
    FASTVB_DOC: ("Wave1214", "CFastVB__BuildTransformMatrixWithOffsets", "Math__BuildQuaternionRotationMatrix_Dispatch_Thunk", BACKUP),
    CRT_DOC: ("Wave1214", "CRT__AcosDispatch_ST0", "x87 ST0", BACKUP),
    RENDER_CONTRACT: ("Wave1214", "CMeshRenderer__RenderMeshCore", "CTexture__BuildTransformMatrixWithOptionalOffsets", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime particle rendering behavior proven",
    "runtime screen-coordinate output proven",
    "runtime cpu feature dispatch proven",
    "exact layout proven",
    "exact source identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 58,
        "pre-instructions.tsv": 175,
        "pre-decompile/index.tsv": 8,
        "context-metadata.tsv": 20,
        "context-tags.tsv": 20,
        "context-xrefs.tsv": 43,
        "context-instructions.tsv": 3821,
        "context-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    evidence_text = (
        read_text(BASE / "pre-metadata.tsv")
        + read_text(BASE / "pre-xrefs.tsv")
        + read_text(BASE / "pre-instructions.tsv")
        + read_text(BASE / "context-metadata.tsv")
        + read_text(BASE / "context-xrefs.tsv")
        + read_text(BASE / "context-instructions.tsv")
        + "".join(read_text(path) for path in sorted((BASE / "pre-decompile").glob("*.c")))
        + "".join(read_text(path) for path in sorted((BASE / "context-decompile").glob("*.c")))
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Static", "evidence only"):
                require(token in row.get("comment", ""), f"missing bounded comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        for from_addr, ref_type in TARGET_XREFS[address]:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and row.get("from_addr") == from_addr
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref {from_addr} {ref_type} for {address}",
                failures,
            )
        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)

    logs = {
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "rows=8 missing=0",
        "pre-xrefs.log": "Wrote 58 rows",
        "pre-instructions.log": "Wrote 175 function-body instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=20 found=20 missing=0",
        "context-tags.log": "rows=20 missing=0",
        "context-xrefs.log": "Wrote 43 rows",
        "context-instructions.log": "Wrote 3821 function-body instruction rows",
        "context-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for relative, token in logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING", "FAIL", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1133, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "96.10%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 46, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1214-math-color-screen-dispatch-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1133, "ledger reviewed mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "96.10%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 46, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1214-math-color-screen-dispatch-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RENDER_CONTRACT,
        RANK,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1214-math-color-screen-dispatch-current-risk-review")
        == r"py -3 tools\wave1214_math_color_screen_dispatch_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1214 math/color/screen dispatch current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1214 math/color/screen dispatch current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
