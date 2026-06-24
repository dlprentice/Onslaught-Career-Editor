#!/usr/bin/env python3
"""Validate Wave1142 mixed score22 current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1142-mixed-score22-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1142-mixed-score22-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1142-mixed-score22-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1142_mixed_score22_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
OIDS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified"

TARGETS = {
    "0x004443f0": (
        "CDestructableSegmentsController__TriggerCoreCascadeIfEligible",
        "void __fastcall CDestructableSegmentsController__TriggerCoreCascadeIfEligible(void * this)",
        ("Controller cascade trigger", "threshold flag", "runtime cascade behavior"),
    ),
    "0x0047eb80": (
        "CStaticShadows__SampleShadowHeightBilinear",
        "double __fastcall CStaticShadows__SampleShadowHeightBilinear(void * this, void * world_pos)",
        ("world-position pointer from EDX", "signed 16-bit height data", "runtime shadow/terrain behavior"),
    ),
    "0x004b6df0": (
        "COggLoader__readerSubobject_scalar_deleting_dtor",
        "void * __thiscall COggLoader__readerSubobject_scalar_deleting_dtor(void * this, byte flags)",
        ("reader-subobject vtable", "COggLoader__readerSubobject_dtor_body", "runtime streaming behavior"),
    ),
    "0x004bfd80": (
        "CSpawnerThng__scalar_deleting_dtor",
        "void * __thiscall CSpawnerThng__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave1022 owner-prefix normalization", "old CSpawnerThing prefix was stale spelling", "RET 0x4"),
    ),
    "0x004bfed0": (
        "CSpawnerThng__dtor_base",
        "void __fastcall CSpawnerThng__dtor_base(void * this)",
        ("Wave1022 owner-prefix normalization", "CSpawnerThng__scalar_deleting_dtor", "CComplexThing__dtor_base"),
    ),
    "0x004c4ae0": (
        "CPDMesh__scalar_deleting_dtor",
        "void * __thiscall CPDMesh__scalar_deleting_dtor(void * this, byte flags)",
        ("CPDMesh vtable slot 0", "CPDMesh__dtor_base", "Runtime mesh cleanup behavior"),
    ),
    "0x004cffd0": (
        "CVideoDetailLevel__GetCurrentPresetFromItems",
        "int __fastcall CVideoDetailLevel__GetCurrentPresetFromItems(void * video_detail_menu)",
        ("Video-detail preset recognizer", "display-profile defaults", "runtime device/menu behavior"),
    ),
    "0x005018b0": (
        "CVertexShader__dtor",
        "void __thiscall CVertexShader__dtor(void * this)",
        ("Wave533 stale-destructor-body correction", "device shader pointer", "runtime shader behavior"),
    ),
    "0x00506010": (
        "ProjectileBurst__SpawnFromPercentBucketFallback",
        "int __fastcall ProjectileBurst__SpawnFromPercentBucketFallback(void * burstContext)",
        ("shared percent-bucket fallback dispatcher", "ProjectileBurst__SpawnFromCurrentPreset", "weapon_fire_breaks_stealth"),
    ),
    "0x00527c90": (
        "CReconnectInterface__ctor",
        "void * __thiscall CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)",
        ("CTweak-derived reconnect interface", "RET 0x8", "source identity"),
    ),
}

EXPECTED_XREFS = {
    "0x004443f0": ("0x004fd1dc", "CUnit__MarkDestroyedAndCleanupLinks", "UNCONDITIONAL_CALL"),
    "0x0047eb80": ("0x0053a4fe", "CDXBattleLine__UpdateHeightmap", "UNCONDITIONAL_CALL"),
    "0x004b6df0": ("0x005dc690", "<no_function>", "DATA"),
    "0x004bfd80": ("0x005dd170", "<no_function>", "DATA"),
    "0x004bfed0": ("0x004bfd83", "CSpawnerThng__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    "0x004c4ae0": ("0x005ddb3c", "<no_function>", "DATA"),
    "0x004cffd0": ("0x005de598", "<no_function>", "DATA"),
    "0x005018b0": ("0x00501893", "CVertexShader__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    "0x00506010": ("0x00413ce2", "CBattleEngineWalkerPart__FireWeapon", "UNCONDITIONAL_CALL"),
    "0x00527c90": ("0x0053aa1c", "<no_function>", "UNCONDITIONAL_CALL"),
}

PROJECTILE_CALLSITES = {
    "0x0044e093": ("ProjectileBurstCallerBoundary_0044e020", "CALL", "0x00506010"),
    "0x004f4bd6": ("ProjectileBurstCallerBoundary_004f4920", "CALL", "0x00506010"),
    "0x00411e0f": ("CGeneralVolume__DispatchMode3BurstProgressAndSpawn", "CALL", "0x00506010"),
    "0x00413d5f": ("CBattleEngineWalkerPart__ChargeWeapon", "CALL", "0x00506010"),
    "0x00413ce2": ("CBattleEngineWalkerPart__FireWeapon", "JMP", "0x00506010"),
}

RECONNECT_CALLSITES = ("0x0053aa1c", "0x0054556c", "0x0054d4dc", "0x0054d50c", "0x00551ecc", "0x0055643c", "0x0055b08c", "0x0055b0bc")
STATIC_SHADOW_NO_FUNCTION_SITES = ("0x00415310", "0x0041930c", "0x004194b7", "0x004807d8", "0x004f61dd")

DOC_TOKENS = (
    "Wave1142",
    "wave1142-mixed-score22-current-risk-review",
    "261/1179 = 22.14%",
    "10 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 918",
    "current risk candidates: 6166",
    "mixed score22 current-risk residual review",
    "fresh Ghidra export",
    "xref-site windows",
    "static-shadow no-function boundary candidates",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CSpawnerThng__scalar_deleting_dtor",
    "CSpawnerThng__dtor_base",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime shadow/terrain behavior proven",
    "runtime projectile behavior proven",
    "weapon_fire_breaks_stealth proven",
    "runtime stealth behavior proven",
    "runtime reconnect-interface behavior proven",
    "runtime ogg streaming behavior proven",
    "runtime spawner cleanup behavior proven",
    "runtime shader behavior proven",
    "runtime video-menu behavior proven",
    "runtime cascade behavior proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 135,
        "pre-instructions.tsv": 582,
        "pre-decompile/index.tsv": 10,
        "xref-site-windows.tsv": 625,
        "static-shadow-no-function-windows.tsv": 805,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None and address == "0x00506010":
            require(tag_row.get("tags", "") == "", "projectile fallback tags should remain empty in saved state", failures)
        elif tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        from_addr, from_function, ref_type = EXPECTED_XREFS[address]
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )


def check_window_exports(failures: list[str]) -> None:
    xref_rows = read_tsv(BASE / "xref-site-windows.tsv")
    static_rows = read_tsv(BASE / "static-shadow-no-function-windows.tsv")

    xref_by_instruction = {normalize_address(row["instruction_addr"]): row for row in xref_rows}
    for address, (function_name, mnemonic, operand) in PROJECTILE_CALLSITES.items():
        row = xref_by_instruction.get(address)
        require(row is not None, f"missing projectile callsite window row {address}", failures)
        if row is not None:
            require(row.get("function_name") == function_name, f"projectile callsite function mismatch {address}", failures)
            require(row.get("mnemonic") == mnemonic, f"projectile callsite mnemonic mismatch {address}", failures)
            require(normalize_address(row.get("operands", "")) == operand, f"projectile callsite operand mismatch {address}", failures)

    for address in RECONNECT_CALLSITES:
        row = xref_by_instruction.get(address)
        require(row is not None, f"missing reconnect callsite window row {address}", failures)
        if row is not None:
            require(row.get("function_name") == "<no_function>", f"reconnect callsite should remain no-function {address}", failures)
            require(row.get("mnemonic") == "CALL", f"reconnect callsite mnemonic mismatch {address}", failures)
            require(normalize_address(row.get("operands", "")) == "0x00527c90", f"reconnect callsite operand mismatch {address}", failures)

    static_by_instruction = {normalize_address(row["instruction_addr"]): row for row in static_rows}
    for address in STATIC_SHADOW_NO_FUNCTION_SITES:
        row = static_by_instruction.get(address)
        require(row is not None, f"missing static-shadow no-function callsite {address}", failures)
        if row is not None:
            require(row.get("function_name") == "<no_function>", f"static-shadow callsite should remain no-function {address}", failures)
            require(row.get("mnemonic") == "CALL", f"static-shadow callsite mnemonic mismatch {address}", failures)
            require(normalize_address(row.get("operands", "")) == "0x0047eb80", f"static-shadow callsite operand mismatch {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-xrefs.log": "Wrote 135 rows",
        "pre-instructions.log": "Wrote 582 function-body instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "xref-site-windows.log": "targets=27 missing=4",
        "static-shadow-no-function-windows.log": "targets=5 missing=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    require("Wrote 625 instruction rows" in read_text(BASE / "xref-site-windows.log"), "xref-site window row log mismatch", failures)
    require("Wrote 805 instruction rows" in read_text(BASE / "static-shadow-no-function-windows.log"), "static-shadow window row log mismatch", failures)


def check_queue_progress_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)

    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    require(risk.get("totalFunctions") == 6411, "current risk total mismatch", failures)
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["latestWave"]["wave"] == "Wave1142 mixed score22 current-risk review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress latest backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 261, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "22.14%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 918, "progress remaining mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "progress broad candidates mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        OIDS_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    active_docs = [FUNCTION_INDEX, OIDS_DOC]
    for path in active_docs:
        text = read_text(path)
        require("CSpawnerThing__scalar_deleting_dtor" not in text, f"stale CSpawnerThing scalar dtor in {path.relative_to(ROOT)}", failures)
        require("CSpawnerThing__dtor_base" not in text, f"stale CSpawnerThing base dtor in {path.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1142-mixed-score22-current-risk-review") == r"py -3 tools\wave1142_mixed_score22_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_window_exports(failures)
    check_logs(failures)
    check_queue_progress_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1142 mixed score22 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1142 mixed score22 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
