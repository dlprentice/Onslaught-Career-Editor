#!/usr/bin/env python3
"""Validate Wave1176 Mat34/Vec3 owner-neutral current-risk read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1176-mat34-vec3-owner-neutral-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1176-mat34-vec3-owner-neutral-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1176-mat34-vec3-owner-neutral-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1176_mat34_vec3_owner_neutral_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-084715_post_wave1176_mat34_vec3_owner_neutral_current_risk_review_verified"

TARGETS = {
    "0x0040d320": (
        "Mat34__MultiplyBasisToOut",
        "void * __thiscall Mat34__MultiplyBasisToOut(void * this, void * out_basis, void * rhs_basis)",
        ("Wave388", "owner-neutral Mat34-style 3x3 basis multiply", "out_basis", "rhs_basis", "0x30-byte output basis"),
    ),
    "0x0041ad10": (
        "Vec3__AddInPlace",
        "void __thiscall Vec3__AddInPlace(void * this, void * add_vec3)",
        ("Wave388", "owner-neutral Vec3 in-place add helper", "RET 0x4", "old CMCTentacle-only owner label too narrow"),
    ),
    "0x004f8140": (
        "Mat34__SetFromEulerDegrees",
        "void __thiscall Mat34__SetFromEulerDegrees(void * this, int yaw_deg, int pitch_deg, int roll_deg)",
        ("Wave548", "0x005dfb6c", "Vec3__SetXYZ", "Mat34__SetRows", "Mat34__MultiplyBasisToOut", "RET 0x0c"),
    ),
    "0x0040d1a0": (
        "Vec3__ElevationOrZero",
        "double __fastcall Vec3__ElevationOrZero(void * vec)",
        ("vector-angle helper", "near-zero input", "z over length", "OID__AcosWrapper", "tags"),
    ),
    "0x00477ba0": (
        "Vec3__MagnitudeSquared",
        "double __fastcall Vec3__MagnitudeSquared(void * this)",
        ("Wave446", "x*x + y*y + z*z", "stale Geometry__NoOpHook", "x87 stack"),
    ),
    "0x00490900": (
        "Vec3__SubtractInPlace",
        "void __thiscall Vec3__SubtractInPlace(void * this, void * rhs_vector)",
        ("Wave426", "RET 0x4", "rhs_vector", "subtracts rhs_vector from this"),
    ),
    "0x00495ed0": (
        "Mat34__ScaleByScalar",
        "void __thiscall Mat34__ScaleByScalar(void * this, void * outMatrix, float scalar)",
        ("matrix scale helper", "output matrix", "scalar float", "ret 0x8"),
    ),
    "0x004c7900": (
        "Vec3__NormalizeInPlace",
        "void __thiscall Vec3__NormalizeInPlace(void * this)",
        ("Wave469", "squared magnitude", "DAT_005d856c", "DAT_005d8568 / sqrt(length_sq)"),
    ),
    "0x004c7d90": (
        "Vec3__CopyXYZ",
        "void * __thiscall Vec3__CopyXYZ(void * this, void * src_vec3)",
        ("Wave469", "three-dword copy helper", "src_vec3", "EAX returns the destination pointer"),
    ),
}

EXPECTED_XREF_COUNTS = {
    "0x0040d320": 64,
    "0x0041ad10": 21,
    "0x004f8140": 5,
    "0x0040d1a0": 4,
    "0x00477ba0": 6,
    "0x00490900": 3,
    "0x00495ed0": 9,
    "0x004c7900": 1,
    "0x004c7d90": 9,
}

DECOMPILE_TOKENS = {
    "0x0040d320": ("return out_basis", "*(float *)out_basis", "*(float *)((int)rhs_basis + 0x20)"),
    "0x0041ad10": ("*(float *)this", "+ *(float *)this", "*(float *)((int)add_vec3 + 4)", "return"),
    "0x004f8140": ("0x005dfb6c", "Vec3__SetXYZ", "Mat34__SetRows", "Mat34__MultiplyBasisToOut"),
    "0x0040d1a0": ("SQRT", "CRT__AcosDispatch_ST0", "_DAT_005d856c"),
    "0x00477ba0": ("*(float *)this", "((int)this + 4)", "((int)this + 8)"),
    "0x00490900": ("- *(float *)rhs_vector", "- *(float *)((int)rhs_vector + 4)", "return"),
    "0x00495ed0": ("outMatrix", "scalar", "return"),
    "0x004c7900": ("SQRT", "_DAT_005d856c", "_DAT_005d8568"),
    "0x004c7d90": ("src_vec3", "return this"),
}

DOC_TOKENS = (
    "Wave1176",
    "wave1176-mat34-vec3-owner-neutral-current-risk-review",
    "692/1179 = 58.69%",
    "9 Mat34/Vec3 owner-neutral current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 487",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "Codex root final judgment",
    "prior Wave388/Wave426/Wave446/Wave469/Wave548/Wave973/Wave997/Wave1062 read-back evidence",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "122 xref rows",
    "333 instruction rows",
    "0x0040d320 Mat34__MultiplyBasisToOut",
    "0x0041ad10 Vec3__AddInPlace",
    "0x004f8140 Mat34__SetFromEulerDegrees",
    "0x0040d1a0 Vec3__ElevationOrZero",
    "0x00477ba0 Vec3__MagnitudeSquared",
    "0x00490900 Vec3__SubtractInPlace",
    "0x00495ed0 Mat34__ScaleByScalar",
    "0x004c7900 Vec3__NormalizeInPlace",
    "0x004c7d90 Vec3__CopyXYZ",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "exact vec3 layout proven",
    "exact mat34 layout proven",
    "runtime math behavior proven",
    "runtime render behavior proven",
    "runtime collision behavior proven",
    "runtime transform behavior proven",
    "rebuild parity proven",
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
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 122,
        "pre-instructions.tsv": 333,
        "pre-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        if tag_row and address != "0x0040d1a0":
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for tag in ("static-reaudit", "retail-binary-evidence"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)
        if tag_row and address == "0x0040d1a0":
            require(tag_row.get("tags", "") == "", "Vec3__ElevationOrZero tag gap was unexpectedly filled", failures)

        dec = decompile.get(address)
        require(
            dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )
        if dec is not None:
            decompile_path = BASE / "pre-decompile" / f"{address[2:]}_{name}.c"
            decompile_text = read_text(decompile_path)
            for token in DECOMPILE_TOKENS[address]:
                require(token in decompile_text, f"missing decompile token {address}: {token}", failures)

        observed_xrefs = [row for row in xrefs if normalize(row.get("target_addr", "")) == address]
        require(len(observed_xrefs) == EXPECTED_XREF_COUNTS[address], f"xref count mismatch {address}", failures)
        require(all(row.get("ref_type") == "UNCONDITIONAL_CALL" for row in observed_xrefs), f"xref type mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "rows=9 missing=0",
        "pre-xrefs.log": "Wrote 122 rows",
        "pre-instructions.log": "Wrote 333 instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176065415, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1176 Mat34 / Vec3 Owner-Neutral Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1176-mat34-vec3-owner-neutral-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 692, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "58.69%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 487, "remaining focused mismatch", failures)


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
        MATH_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1176 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1176-mat34-vec3-owner-neutral-current-risk-review")
        == r"py -3 tools\wave1176_mat34_vec3_owner_neutral_current_risk_review.py --check",
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
        print("Wave1176 Mat34/Vec3 owner-neutral probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1176 Mat34/Vec3 owner-neutral probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
