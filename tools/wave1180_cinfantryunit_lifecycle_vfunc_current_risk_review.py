#!/usr/bin/env python3
"""Validate Wave1180 CInfantryUnit lifecycle/vfunc current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1180-infantryunit-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
INFANTRY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-104634_post_wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review_verified"

TARGETS = {
    "0x00488f10": (
        "CInfantryUnit__VFunc38_HandleHitOrDispatchHit",
        "void __thiscall CInfantryUnit__VFunc38_HandleHitOrDispatchHit(void * this, void * otherThing, void * collisionReport)",
    ),
    "0x00488f60": (
        "CInfantryUnit__VFunc02_ClearParticleLinkAndForward",
        "void __fastcall CInfantryUnit__VFunc02_ClearParticleLinkAndForward(void * this)",
    ),
    "0x00488f80": (
        "CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius",
        "void __thiscall CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius(void * this, void * collisionOwner)",
    ),
    "0x00489090": (
        "CInfantryUnit__VFunc59_SelectAnimationMode",
        "int __thiscall CInfantryUnit__VFunc59_SelectAnimationMode(void * this, int requestedMode, int resetFrame, int forceLooped)",
    ),
    "0x004892c0": (
        "CInfantryUnit__VFunc65_UpdateMotionAnimationState",
        "void __fastcall CInfantryUnit__VFunc65_UpdateMotionAnimationState(void * this)",
    ),
    "0x00489650": (
        "CInfantryUnit__VFunc39_HandleCollisionDamageReaction",
        "void __thiscall CInfantryUnit__VFunc39_HandleCollisionDamageReaction(void * this, void * collisionContext, void * otherThing, void * impactContext, void * damageContext)",
    ),
    "0x00489b40": (
        "CInfantryUnit__VFunc49_HandleDeathPickupAndEffects",
        "int __fastcall CInfantryUnit__VFunc49_HandleDeathPickupAndEffects(void * this)",
    ),
    "0x0050f1a0": (
        "CInfantryUnit__Destructor_VFunc01",
        "void __fastcall CInfantryUnit__Destructor_VFunc01(void * this)",
    ),
}

XREFS = {
    "0x00488f10": ("0x005e27c8", "DATA"),
    "0x00488f60": ("0x005e2734", "DATA"),
    "0x00488f80": ("0x005e27b8", "DATA"),
    "0x00489090": ("0x005e281c", "DATA"),
    "0x004892c0": ("0x005e2834", "DATA"),
    "0x00489650": ("0x005e27cc", "DATA"),
    "0x00489b40": ("0x005e27f4", "DATA"),
    "0x0050f1a0": ("0x0050ee33", "UNCONDITIONAL_CALL"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened"}
TAG_REQUIREMENTS = {
    "0x00488f10": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x00488f60": {"infantryunit-vfunc02-wave805", "wave805-readback-verified", "infantry-unit", "particle-effect-link", "signature-hardened", "vtable-slot"},
    "0x00488f80": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x00489090": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x004892c0": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x00489650": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x00489b40": {"infantryunit-lifecycle-boundary-wave1076", "wave1076-readback-verified", "cinfantryunit", "function-boundary-recovered", "signature-hardened", "vtable-slot"},
    "0x0050f1a0": {"air-unit-lifecycle-wave557", "infantry-unit", "signature-corrected", "signature-recovered", "destructor-body"},
}

DOC_TOKENS = (
    "Wave1180",
    "wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review",
    "729/1179 = 61.83%",
    "8 CInfantryUnit lifecycle/vfunc current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 450",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "Codex root final judgment",
    "adversarial consult recommended already-counted CUnitAI door-wing rows",
    "root rejected duplicate Wave1116 accounting",
    "infantry consult recommended exact eight-row CInfantryUnit slice",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "8 xref rows",
    "1150 instruction rows",
    "CInfantryUnit__VFunc38_HandleHitOrDispatchHit",
    "CInfantryUnit__VFunc02_ClearParticleLinkAndForward",
    "CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius",
    "CInfantryUnit__VFunc59_SelectAnimationMode",
    "CInfantryUnit__VFunc65_UpdateMotionAnimationState",
    "CInfantryUnit__VFunc39_HandleCollisionDamageReaction",
    "CInfantryUnit__VFunc49_HandleDeathPickupAndEffects",
    "CInfantryUnit__Destructor_VFunc01",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime infantry behavior proven",
    "runtime hit/collision/damage/death/pickup/effect behavior proven",
    "exact concrete cinfantryunit/cunit/cunitai/layout semantics proven",
    "exact source virtual names proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "no noticeable difference proven",
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
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 1150,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("remain" in row.get("comment", "") or "unproven" in row.get("comment", ""), f"missing bounded comment token {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | TAG_REQUIREMENTS[address]
            require(required.issubset(actual), f"missing prior tags {address}: {required - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref row {address}", failures)
        if xref is not None:
            expected_from, expected_type = XREFS[address]
            require(normalize(xref.get("from_addr", "")) == expected_from, f"xref from mismatch {address}", failures)
            require(xref.get("ref_type") == expected_type, f"xref type mismatch {address}", failures)
            if address == "0x0050f1a0":
                require(xref.get("from_function") == "CInfantryUnit__scalar_deleting_dtor", "destructor xref caller mismatch", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "rows=8 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 1150 function-body instruction rows",
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
    require(latest.get("wave") == "Wave1180 CInfantryUnit Lifecycle / VFunc Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 729, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "61.83%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 450, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review", "latest review tag mismatch", failures)


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
        INFANTRY_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1180 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1180-cinfantryunit-lifecycle-vfunc-current-risk-review")
        == r"py -3 tools\wave1180_cinfantryunit_lifecycle_vfunc_current_risk_review.py --check",
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
        print("Wave1180 CInfantryUnit lifecycle/vfunc current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1180 CInfantryUnit lifecycle/vfunc current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
