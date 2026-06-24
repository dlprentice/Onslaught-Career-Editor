#!/usr/bin/env python3
"""Validate Wave1188 BattleEngine/WalkerPart support current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1188-battleengine-walkerpart-support-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1188-battleengine-walkerpart-support-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1188-battleengine-walkerpart-support-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1188_battleengine_walkerpart_support_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
WALKERPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
APPLY_SCRIPT = ROOT / "tools" / "ApplyBattleEngineWalkerPartSupportCurrentRiskWave1188.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified"

TARGETS = {
    "0x00405a40": {
        "name": "CBattleEngine__dtor_base",
        "signature": "void __fastcall CBattleEngine__dtor_base(void * this)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "this+0x620",
            "this+0x294",
            "this+0x2a4",
            "this+0x578",
            "this+0x57c",
            "CUnit__dtor_base",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x00405f63", "UNCONDITIONAL_CALL")},
    },
    "0x00405f60": {
        "name": "CBattleEngine__scalar_deleting_dtor",
        "signature": "void * __thiscall CBattleEngine__scalar_deleting_dtor(void * this, byte flags)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "0x005d89c8",
            "CBattleEngine__dtor_base",
            "delete flag bit 0",
            "CDXMemoryManager__Free",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x005d89c8", "DATA")},
    },
    "0x004063b0": {
        "name": "CBattleEngine__UpdateWeaponEffect",
        "signature": "void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CBattleEngine__HandleEvent",
            "0x0040c1db",
            "0x0040c27f",
            "BattleEngine.cpp line 0x1f5",
            "this+0x38",
            "vfunc +0x24",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {
            ("0x0040c1db", "UNCONDITIONAL_CALL"),
            ("0x0040c27f", "UNCONDITIONAL_CALL"),
        },
    },
    "0x00406460": {
        "name": "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        "signature": "void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(void * this)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CBattleEngine__Init",
            "CUnit__ProcessStateSwapAndDeathChecks",
            "CBattleEngine__Morph",
            "CGeneralVolume__ResetAndSetActiveReader",
            "this+0x260",
            "this+0x5f0",
            "this+0x5ec",
            "this+0x30",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {
            ("0x00405863", "UNCONDITIONAL_CALL"),
            ("0x00408153", "UNCONDITIONAL_CALL"),
            ("0x0040a75d", "UNCONDITIONAL_CALL"),
            ("0x0040c724", "UNCONDITIONAL_CALL"),
        },
    },
    "0x00406fc0": {
        "name": "CBattleEngine__AddProjectile",
        "signature": "void __thiscall CBattleEngine__AddProjectile(void * this, void * target, float lifetime, int modeFlag)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            "0x004068d9",
            "0x00406a51",
            "0x00406aae",
            "0x00406d06",
            "target+0x2c",
            "this+0x294",
            "BattleEngine.cpp line 0x332",
            "weapon_fire_breaks_stealth closure",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {
            ("0x004068d9", "UNCONDITIONAL_CALL"),
            ("0x00406a51", "UNCONDITIONAL_CALL"),
            ("0x00406aae", "UNCONDITIONAL_CALL"),
            ("0x00406d06", "UNCONDITIONAL_CALL"),
        },
    },
    "0x004080f0": {
        "name": "CGame__IsWalkerGroundedOrCollision",
        "signature": "bool __fastcall CGame__IsWalkerGroundedOrCollision(void * battleEngine)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CGame__Update",
            "0x0046eb8d",
            "CPlayer__ReceiveButtonAction",
            "0x004d31d3",
            "battleEngine+0x260 == 2",
            "vfunc at +0x10c",
            "HeightDelta__Below015_D4",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {
            ("0x0046eb8d", "UNCONDITIONAL_CALL"),
            ("0x004d31d3", "UNCONDITIONAL_CALL"),
        },
    },
    "0x004145d0": {
        "name": "CBattleEngineWalkerPart__GetWeaponPhysicsName",
        "signature": "char * __thiscall CBattleEngineWalkerPart__GetWeaponPhysicsName(void * this)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CBattleEngine__GetWeaponPhysicsName",
            "0x0040c57f",
            "CBattleEngineWalkerPart__GetCurrentWeapon",
            "currentWeapon+0xa4",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x0040c57f", "UNCONDITIONAL_CALL")},
    },
    "0x00414610": {
        "name": "CBattleEngineWalkerPart__GetWeaponIconName",
        "signature": "char * __thiscall CBattleEngineWalkerPart__GetWeaponIconName(void * this)",
        "comment_tokens": (
            "Wave1188 static read-back",
            "CBattleEngine__GetWeaponIconName",
            "0x0040c59f",
            "CBattleEngineWalkerPart__GetCurrentWeapon",
            "weapon-data+0x38",
            "currentWeapon+0xa4",
            "clean-room/no-noticeable-difference parity remain separate proof",
        ),
        "xref_set": {("0x0040c59f", "UNCONDITIONAL_CALL")},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1188-battleengine-walkerpart-support-current-risk-review",
    "wave1188-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "battleengine",
    "walkerpart",
    "source-identity-deferred",
    "exact-layout-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1188",
    "wave1188-battleengine-walkerpart-support-current-risk-review",
    "801/1179 = 67.94%",
    "8 BattleEngine/WalkerPart support current-risk rows",
    "current focused candidates: 1169",
    "live regenerated current focused candidates: 1169",
    "remaining active focused work: 378",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=8 skipped=0",
    "comment_only_updated=8",
    "tags_added=128",
    "final dry updated=0 skipped=8",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "CBattleEngine__dtor_base",
    "CBattleEngine__scalar_deleting_dtor",
    "CBattleEngine__UpdateWeaponEffect",
    "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
    "CBattleEngine__AddProjectile",
    "CGame__IsWalkerGroundedOrCollision",
    "CBattleEngineWalkerPart__GetWeaponPhysicsName",
    "CBattleEngineWalkerPart__GetWeaponIconName",
    "CBattleEngine__HandleEvent",
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CGame__Update",
    "CPlayer__ReceiveButtonAction",
    "CBattleEngine__GetWeaponPhysicsName",
    "CBattleEngine__GetWeaponIconName",
    "BattleEngine.cpp line 0x1f5",
    "BattleEngine.cpp line 0x332",
    "this+0x294",
    "this+0x5ec",
    "this+0x30",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "16 xref rows",
    "478 instruction rows",
    "8 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime weapon/effect/projectile/morph/reader/grounded behavior proven",
    "weapon_fire_breaks_stealth closure proven",
    "exact battleengine layout proven",
    "exact walkerpart layout proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 16,
        "pre-instructions.tsv": 478,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 16,
        "post-instructions.tsv": 478,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, set[tuple[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize(row["target_addr"]), set()).add((normalize(row["from_addr"]), row.get("ref_type", "")))

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata target {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment_tokens"]:
                require(contains_token(comment, token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(xrefs_by_target.get(address, set()) == expected["xref_set"], f"xref set mismatch at {address}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 tags_added=128 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "rows=8 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
        "post-instructions.log": "Wrote 478 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1188_queue_probe.log")
    require("Status: PASS" in queue_log, "queue probe did not pass", failures)
    export_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1188.log")
    require("total_functions=6411 commented_functions=6411" in export_log, "quality export count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless queue mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined queue mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N queue mismatch", failures)

    quality_rows = {normalize(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    for address, expected in TARGETS.items():
        row = quality_rows.get(address)
        require(row is not None, f"target missing from quality TSV {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"quality TSV name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"quality TSV signature mismatch at {address}", failures)
            require("Wave1188 static read-back" in row.get("comment", ""), f"quality TSV missing Wave1188 comment at {address}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176163719, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1188 BattleEngine / WalkerPart Support Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1188-battleengine-walkerpart-support-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(
        artifact_commit == "pending Wave1188 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)),
        "latest artifact commit mismatch",
        failures,
    )
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 801, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "67.94%", "current focused percent mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1169, "live focused mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 378, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1188-battleengine-walkerpart-support-current-risk-review", "latest review tag mismatch", failures)
    target = progress.get("staticCompletionDefinition", {}).get("targetOutcome", "")
    require("no noticeable difference from the original game" in target, "static completion target outcome mismatch", failures)


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
        BINARY_INDEX,
        RE_INDEX,
        BATTLEENGINE_DOC,
        WALKERPART_DOC,
        GAME_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1188 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1188-battleengine-walkerpart-support-current-risk-review")
        == r"py -3 tools\wave1188_battleengine_walkerpart_support_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1188 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1188 BattleEngine/WalkerPart support current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1188 BattleEngine/WalkerPart support current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
