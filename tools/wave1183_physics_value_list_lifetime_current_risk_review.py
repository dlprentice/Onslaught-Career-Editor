#!/usr/bin/env python3
"""Validate Wave1183 PhysicsScript value-list lifetime current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1183-physics-value-list-lifetime-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1183-physics-value-list-lifetime-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1183-physics-value-list-lifetime-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1183_physics_value_list_lifetime_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PHYSICS_FUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-123452_post_wave1183_physics_value_list_lifetime_current_risk_review_verified"

TARGETS = {
    "0x0042f4b0": ("CPhysicsUnitValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsUnitValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042f980": ("CPhysicsWeaponValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsWeaponValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x0042fea0": ("CPhysicsWeaponModeValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsWeaponModeValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x00430410": ("CPhysicsRoundValueList__scalar_deleting_dtor", "void * __thiscall CPhysicsRoundValueList__scalar_deleting_dtor(void * this, int flags)"),
    "0x00430e60": ("CComponentStatement__CreateAndRegisterByName", "void __cdecl CComponentStatement__CreateAndRegisterByName(char * name)"),
    "0x00431350": ("CFeatureStatement__CreateAndRegisterByName", "void __cdecl CFeatureStatement__CreateAndRegisterByName(char * name)"),
    "0x004317a0": ("CHazardStatement__CreateAndRegisterByName", "void __cdecl CHazardStatement__CreateAndRegisterByName(char * name)"),
    "0x00432cc0": ("CPhysicsUnitValue__dtor_base", "void __fastcall CPhysicsUnitValue__dtor_base(void * this)"),
    "0x004347a0": ("CPhysicsWeaponValue__dtor_base", "void __fastcall CPhysicsWeaponValue__dtor_base(void * this)"),
    "0x004380c0": ("CPhysicsRoundValue__dtor_base", "void __fastcall CPhysicsRoundValue__dtor_base(void * this)"),
    "0x00438400": ("CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043a040": ("CPhysicsSpawnerValue__dtor_base", "void __fastcall CPhysicsSpawnerValue__dtor_base(void * this)"),
    "0x0043a840": ("CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043af80": ("CPhysicsExplosionValue__dtor_base", "void __fastcall CPhysicsExplosionValue__dtor_base(void * this)"),
    "0x0043b970": ("CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043be00": ("CPhysicsFeatureValue__dtor_base", "void __fastcall CPhysicsFeatureValue__dtor_base(void * this)"),
    "0x0043bff0": ("CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043c230": ("CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043c310": ("CPhysicsHazardValue__dtor_base", "void __fastcall CPhysicsHazardValue__dtor_base(void * this)"),
    "0x0043d5a0": ("CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor", "void * __thiscall CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)"),
    "0x0043dcc0": ("CPhysicsComponentValue__dtor_base", "void __fastcall CPhysicsComponentValue__dtor_base(void * this)"),
}

CORRECTED = {
    "0x00438400": ("CPhysicsRoundValue__dtor_base", "round-value"),
    "0x0043a840": ("CPhysicsSpawnerValue__dtor_base", "spawner-value"),
    "0x0043b970": ("CPhysicsExplosionValue__dtor_base", "explosion-value"),
    "0x0043bff0": ("CPhysicsFeatureValue__dtor_base", "feature-value"),
    "0x0043c230": ("CPhysicsHazardValue__dtor_base", "hazard-value"),
    "0x0043d5a0": ("CPhysicsComponentValue__dtor_base", "component-value"),
}

COMMON_CORRECTED_TAGS = {
    "static-reaudit",
    "wave1183-physics-value-list-lifetime-current-risk-review",
    "wave1183-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "physics-script",
    "value-lifetime",
    "comment-corrected",
    "memory-manager-free",
    "shared-vtable-slot",
    "destructor",
}

DOC_TOKENS = (
    "Wave1183",
    "wave1183-physics-value-list-lifetime-current-risk-review",
    "779/1179 = 66.07%",
    "21 PhysicsScript value-list/registry/lifetime current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 400",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag correction",
    "updated=6 skipped=0",
    "comment_only_updated=6",
    "tags_added=41",
    "final dry updated=0 skipped=6",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "one consult recommended four value-list rows",
    "second consult recommended widened 21-row PhysicsScript slice",
    "Codex root final judgment",
    "no Cursor/Composer",
    "PhysicsScript value-list",
    "registry",
    "value-lifetime",
    "CDXMemoryManager__Free",
    "DAT_009c3df0",
    "0x00549220",
    "not OID__FreeObject",
    "stale OID wording corrected",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "120 xref rows",
    "404 instruction rows",
    "21 decompile rows",
    "CPhysicsUnitValueList__scalar_deleting_dtor",
    "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor",
    "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor",
    "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor",
    "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor",
    "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor",
    "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor",
    "CComponentStatement__CreateAndRegisterByName",
    "CFeatureStatement__CreateAndRegisterByName",
    "CHazardStatement__CreateAndRegisterByName",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime gameplay proven",
    "serialized file-format completeness proven",
    "exact statement/value-list/concrete record layouts proven",
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
        "post-xrefs.tsv": 120,
        "post-instructions.tsv": 404,
        "post-decompile/index.tsv": 21,
        "post-helper-metadata.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    for address, (base_dtor, owner_tag) in CORRECTED.items():
        comment = metadata[address].get("comment", "")
        for token in (
            "Wave1183 static correction",
            base_dtor,
            "CDXMemoryManager__Free(&DAT_009c3df0, this)",
            "0x00549220",
            "not OID__FreeObject",
            "clean-room replacement parity",
            "remain separate proof",
        ):
            require(token in comment, f"missing corrected comment token {address}: {token}", failures)
        require("optionally frees this via OID__FreeObject" not in comment, f"stale OID wording survived {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_CORRECTED_TAGS.issubset(actual_tags), f"tags missing {address}: {COMMON_CORRECTED_TAGS - actual_tags}", failures)
            require(owner_tag in actual_tags, f"owner tag missing {address}: {owner_tag}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

    helper = read_tsv(BASE / "post-helper-metadata.tsv")[0]
    require(normalize(helper.get("address", "")) == "0x00549220", "helper address mismatch", failures)
    require(helper.get("name") == "CDXMemoryManager__Free", "helper name mismatch", failures)
    require(helper.get("signature") == "void __thiscall CDXMemoryManager__Free(void * this, void * mem)", "helper signature mismatch", failures)
    require(helper.get("status") == "OK", "helper status mismatch", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=21 found=21 missing=0",
        "post-tags.log": "rows=21 missing=0",
        "post-xrefs.log": "Wrote 120 rows",
        "post-instructions.log": "Wrote 404 function-body instruction rows",
        "post-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
        "post-helper-metadata.log": "targets=1 found=1 missing=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save token missing", failures)

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
    require(latest.get("wave") == "Wave1183 Physics Value-List Lifetime Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1183-physics-value-list-lifetime-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(artifact_commit == "pending Wave1183 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)), "latest artifact commit mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 779, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "66.07%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 400, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1183-physics-value-list-lifetime-current-risk-review", "latest review tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        PHYSICS_CONTRACT,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        PHYSICS_FUNCTION_DOC,
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

    function_doc = read_text(PHYSICS_FUNCTION_DOC)
    for address in CORRECTED:
        line = next((line for line in function_doc.splitlines() if address in line), "")
        require("CDXMemoryManager__Free(&DAT_009c3df0, this)" in line, f"function doc missing corrected free path {address}", failures)
        require("0x00549220" in line, f"function doc missing free call {address}", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1183 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1183-physics-value-list-lifetime-current-risk-review")
        == r"py -3 tools\wave1183_physics_value_list_lifetime_current_risk_review.py --check",
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
        print("Wave1183 Physics value-list lifetime current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1183 Physics value-list lifetime current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
