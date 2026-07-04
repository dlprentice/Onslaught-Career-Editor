#!/usr/bin/env python3
"""Validate Wave1182 CUnitAI vfunc residual current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1182-cunitai-vfunc-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1182-cunitai-vfunc-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1182-cunitai-vfunc-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1182_cunitai_vfunc_residual_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-115151_post_wave1182_cunitai_vfunc_residual_current_risk_review_verified"

TARGETS = {
    "0x004284f0": ("CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0", "float __thiscall CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0(void * this)"),
    "0x004287c0": ("CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0", "void * __thiscall CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0(void * this, void * outVector)"),
    "0x00428be0": ("CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0", "void __thiscall CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0(void * this, void * currentVector, void * targetVector, void * arg2, void * arg3)"),
    "0x00428c30": ("CUnitAIVFunc__ReturnFloat005d9434_00428c30", "float __thiscall CUnitAIVFunc__ReturnFloat005d9434_00428c30(void * this)"),
    "0x00428c40": ("CUnitAIVFunc__ReturnFloat005d8cb0_00428c40", "float __thiscall CUnitAIVFunc__ReturnFloat005d8cb0_00428c40(void * this)"),
    "0x00428c50": ("CUnitAIVFunc__ReturnField164_198Present_00428c50", "int __thiscall CUnitAIVFunc__ReturnField164_198Present_00428c50(void * this)"),
    "0x00428c90": ("CUnitAIVFunc__CanDeployWhenField264Null_00428c90", "int __thiscall CUnitAIVFunc__CanDeployWhenField264Null_00428c90(void * this)"),
    "0x00428d30": ("CUnitAIVFunc__CopyVector1cToOut_00428d30", "void __thiscall CUnitAIVFunc__CopyVector1cToOut_00428d30(void * this, void * outVector)"),
}

EXPECTED_XREFS = {
    "0x004284f0": {"0x005e4368", "0x005e410c", "0x005e3eb0"},
    "0x004287c0": {"0x005e4264", "0x005e4008", "0x005e3dac"},
    "0x00428be0": {"0x005e432c", "0x005e40d0", "0x005e3e74"},
    "0x00428c30": {"0x005e431c", "0x005e40c0", "0x005e3e64"},
    "0x00428c40": {"0x005e42ac", "0x005e4050", "0x005e3df4"},
    "0x00428c50": {"0x005e42a8", "0x005e404c", "0x005e3df0"},
    "0x00428c90": {"0x005e4348", "0x005e40ec", "0x005e3e90"},
    "0x00428d30": {"0x005e4360", "0x005e3ea8"},
}

COMMON_TAGS = {
    "static-reaudit",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "function-boundary-recovered",
    "shared-unit-residual-vtable-continuation-wave1086",
    "wave1086-readback-verified",
    "shared-unit-vtable",
    "vtable-boundary",
}

DOC_TOKENS = (
    "Wave1182",
    "wave1182-cunitai-vfunc-residual-current-risk-review",
    "758/1179 = 64.29%",
    "8 CUnitAI vfunc residual current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 421",
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
    "one consult recommended exact eight-row CUnitAI vfunc slice",
    "PhysicsScript value-list/registry/lifetime slice deferred as future candidate",
    "Codex root final judgment",
    "no Cursor/Composer",
    "shared unit-family vtable",
    "CUnitAI vfunc residual",
    "Wave1086",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "23 xref rows",
    "88 instruction rows",
    "CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0",
    "CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0",
    "CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0",
    "CUnitAIVFunc__ReturnFloat005d9434_00428c30",
    "CUnitAIVFunc__ReturnFloat005d8cb0_00428c40",
    "CUnitAIVFunc__ReturnField164_198Present_00428c50",
    "CUnitAIVFunc__CanDeployWhenField264Null_00428c90",
    "CUnitAIVFunc__CopyVector1cToOut_00428d30",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime ai behavior proven",
    "runtime deploy behavior proven",
    "exact source virtual names proven",
    "concrete cunitai layout proven",
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
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 88,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xref_by_target: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize(row.get("target_addr", ""))
        xref_by_target.setdefault(target, set()).add(normalize(row.get("from_addr", "")))
        require(row.get("ref_type") == "DATA", f"xref type mismatch {target}", failures)

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Wave1086 static read-back" in comment, f"missing Wave1086 comment token {address}", failures)
            require("Static retail Ghidra vtable/xref/instruction evidence only" in comment, f"missing static boundary {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        require(xref_by_target.get(address) == EXPECTED_XREFS[address], f"xref set mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "rows=8 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 88 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1182 CUnitAI VFunc Residual Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1182-cunitai-vfunc-residual-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(artifact_commit == "pending Wave1182 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)), "latest artifact commit mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 758, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "64.29%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 421, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1182-cunitai-vfunc-residual-current-risk-review", "latest review tag mismatch", failures)


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
        UNITAI_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1182 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1182-cunitai-vfunc-residual-current-risk-review")
        == r"py -3 tools\wave1182_cunitai_vfunc_residual_current_risk_review.py --check",
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
        print("Wave1182 CUnitAI vfunc residual current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1182 CUnitAI vfunc residual current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
