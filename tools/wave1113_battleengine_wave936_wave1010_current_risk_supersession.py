#!/usr/bin/env python3
"""Validate Wave1113 BattleEngine current-risk supersession evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
WAVE936_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave936-battleengine-init-morph-volume-review"
WAVE1010_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1010-battleengine-zoom-autoaim-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1113-battleengine-wave936-wave1010-current-risk-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1113-battleengine-wave936-wave1010-current-risk-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1113_battleengine_wave936_wave1010_current_risk_supersession_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
BATTLEENGINE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE936_BACKUP = r"G:\GhidraBackups\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified"
WAVE1010_BACKUP = r"G:\GhidraBackups\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified"
LATEST_BACKUP = r"G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

TARGETS = {
    "0x00404dd0": {
        "name": "CBattleEngine__Init",
        "signature": "void __thiscall CBattleEngine__Init(void * this, void * init)",
        "score": "26",
        "source": "Wave936",
        "artifact_base": WAVE936_BASE,
        "metadata": "metadata.tsv",
        "tags": "tags.tsv",
        "xrefs": "xrefs.tsv",
        "instructions": "instructions.tsv",
        "decompile": "decompile/index.tsv",
        "comment_tokens": ("CBattleEngine init", "+0x5d4/+0x5d8/+0x5dc", "weapon_fire_breaks_stealth"),
        "xref_expectations": (("0x005d89e8", "<no_function>", "DATA"),),
        "instruction_tokens": (("0x004058f7", "RET", "0x4"),),
        "decompile_file": "decompile/00404dd0_CBattleEngine__Init.c",
        "decompile_tokens": ("CBattleEngine__Init", "0x578", "0x57c", "CBattleEngine__SwapPrimarySecondaryPartReadersForState"),
    },
    "0x00406da0": {
        "name": "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
        "signature": "void * __thiscall CBattleEngine__SelectNearestForwardTargetFromGlobalSet(void * this, void * profile, float originX, float originY, float originZ, float originW, float rangeScale)",
        "score": "27",
        "source": "Wave936",
        "artifact_base": WAVE936_BASE,
        "metadata": "metadata.tsv",
        "tags": "tags.tsv",
        "xrefs": "xrefs.tsv",
        "instructions": "instructions.tsv",
        "decompile": "decompile/index.tsv",
        "comment_tokens": ("DAT_008550d0", "+0x294", "originW"),
        "xref_expectations": (
            ("0x004068bf", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
            ("0x00406a8b", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
            ("0x00406b0c", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
        ),
        "instruction_tokens": (("0x00406fae", "RET", "0x18"),),
        "decompile_file": "decompile/00406da0_CBattleEngine__SelectNearestForwardTargetFromGlobalSet.c",
        "decompile_tokens": ("DAT_008550d0", "CUnit__IsCandidateSideCompatibleForTargeting", "CWeapon__GetDistanceProfileField98"),
    },
    "0x0040b6d0": {
        "name": "CBattleEngine__HandleAutoAim",
        "signature": "void __thiscall CBattleEngine__HandleAutoAim(void * this, void * event)",
        "score": "27",
        "source": "Wave1010",
        "artifact_base": WAVE1010_BASE,
        "metadata": "post-metadata.tsv",
        "tags": "post-tags.tsv",
        "xrefs": "post-xrefs.tsv",
        "instructions": "post-instructions.tsv",
        "decompile": "post-decompile/index.tsv",
        "comment_tokens": ("CBattleEngine::HandleAutoAim", "allowed-auto-aim gate", "event 0x1773"),
        "xref_expectations": (("0x0040c2ad", "CBattleEngine__HandleEvent", "UNCONDITIONAL_CALL"),),
        "instruction_tokens": (("0x0040bfbf", "RET", "0x4"),),
        "decompile_file": "post-decompile/0040b6d0_CBattleEngine__HandleAutoAim.c",
        "decompile_tokens": ("CBattleEngine__HandleAutoAim", "CGenericActiveReader__SetReader", "CMapWho__GetFirst", "CWorld__FindFirstThingToHitLine"),
    },
    "0x0040dc30": {
        "name": "CBattleEngine__EnableVolumeEntryGroupsByName",
        "signature": "void __thiscall CBattleEngine__EnableVolumeEntryGroupsByName(void * this, void * entryName)",
        "score": "26",
        "source": "Wave936",
        "artifact_base": WAVE936_BASE,
        "metadata": "metadata.tsv",
        "tags": "tags.tsv",
        "xrefs": "xrefs.tsv",
        "instructions": "instructions.tsv",
        "decompile": "decompile/index.tsv",
        "comment_tokens": ("+0x578", "CGeneralVolume__EnableEntriesByName", "+0x57c"),
        "xref_expectations": (("0x005d8b5c", "<no_function>", "DATA"),),
        "instruction_tokens": (("0x0040dc52", "RET", "0x4"),),
        "decompile_file": "decompile/0040dc30_CBattleEngine__EnableVolumeEntryGroupsByName.c",
        "decompile_tokens": ("CGeneralVolume__EnableEntriesByName", "CGeneralVolume__EnableLinkedEntriesByName"),
    },
    "0x0040dc60": {
        "name": "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect",
        "signature": "void __thiscall CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect(void * this, void * entryName)",
        "score": "26",
        "source": "Wave936",
        "artifact_base": WAVE936_BASE,
        "metadata": "metadata.tsv",
        "tags": "tags.tsv",
        "xrefs": "xrefs.tsv",
        "instructions": "instructions.tsv",
        "decompile": "decompile/index.tsv",
        "comment_tokens": ("+0x578", "CGeneralVolume__DisableEntriesByNameAndReselect", "+0x57c"),
        "xref_expectations": (("0x005d8b60", "<no_function>", "DATA"),),
        "instruction_tokens": (("0x0040dc82", "RET", "0x4"),),
        "decompile_file": "decompile/0040dc60_CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect.c",
        "decompile_tokens": ("CGeneralVolume__DisableEntriesByNameAndReselect", "CGeneralVolume__DisableLinkedEntriesByNameAndReselect"),
    },
}

DOC_TOKENS = (
    "Wave1113",
    "wave1113-battleengine-wave936-wave1010-current-risk-supersession",
    "33/1179 = 2.80%",
    "5 rows",
    "current focused candidates: 1179",
    "Wave936",
    "battleengine-init-morph-volume-review-wave936",
    "Wave1010",
    "battleengine-weapon-autoaim-review-wave1010",
    "0x00404dd0 CBattleEngine__Init",
    "0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
    "0x0040b6d0 CBattleEngine__HandleAutoAim",
    "0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName",
    "0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect",
    WAVE936_BACKUP,
    WAVE1010_BACKUP,
    LATEST_BACKUP,
    "no new Ghidra export",
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime targeting behavior proven",
    "runtime auto-aim behavior proven",
    "runtime volume behavior proven",
    "runtime init behavior proven",
    "weapon_fire_breaks_stealth closed",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def check_wave1108_membership(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused = row_map(FOCUSED_TSV)
    require(len(focused) == 1179, "Wave1108 focused row count mismatch", failures)
    for address, expected in TARGETS.items():
        row = focused.get(address)
        require(row is not None, f"Wave1108 focused row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"Wave1108 name mismatch: {address}", failures)
        require(row.get("score") == expected["score"], f"Wave1108 score mismatch: {address}", failures)
        for signal in ("stale_or_corrected", "runtime_or_rebuild_deferred", "critical_family"):
            require(signal in row.get("signals", ""), f"Wave1108 missing signal {address}: {signal}", failures)


def check_current_queue(failures: list[str]) -> None:
    queue = row_map(QUEUE_TSV)
    for address, expected in TARGETS.items():
        row = queue.get(address)
        require(row is not None, f"current queue row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"current queue name mismatch: {address}", failures)
        require(row.get("signature") == expected["signature"], f"current queue signature mismatch: {address}", failures)
        require(row.get("status") == "OK", f"current queue status mismatch: {address}", failures)
        for token in expected["comment_tokens"]:
            require(token in row.get("comment", ""), f"current queue missing comment token {address}: {token}", failures)


def check_artifact_counts_and_logs(failures: list[str]) -> None:
    wave936_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 12,
        "instructions.tsv": 938,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 22,
        "context-instructions.tsv": 828,
        "context-decompile/index.tsv": 7,
    }
    wave1010_counts = {
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 2044,
        "post-decompile/index.tsv": 9,
        "vtable-slots.tsv": 192,
        "vtable-types.tsv": 4,
    }
    for relative, expected in wave936_counts.items():
        actual = len(read_tsv(WAVE936_BASE / relative))
        require(actual == expected, f"Wave936 {relative} row count {actual} != {expected}", failures)
    for relative, expected in wave1010_counts.items():
        actual = len(read_tsv(WAVE1010_BASE / relative))
        require(actual == expected, f"Wave1010 {relative} row count {actual} != {expected}", failures)

    logs = {
        WAVE936_BASE: {
            "metadata.log": "targets=6 found=6 missing=0",
            "tags.log": "rows=6 missing=0",
            "xrefs.log": "Wrote 12 rows",
            "instructions.log": "Wrote 938 function-body instruction rows",
            "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
            "context-metadata.log": "targets=7 found=7 missing=0",
            "context-tags.log": "rows=7 missing=0",
            "context-xrefs.log": "Wrote 22 rows",
            "context-instructions.log": "Wrote 828 function-body instruction rows",
            "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        },
        WAVE1010_BASE: {
            "post-metadata.log": "targets=9 found=9 missing=0",
            "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
            "post-xrefs.log": "Wrote 12 rows",
            "post-instructions.log": "Wrote 2044 function-body instruction rows",
            "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
            "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0",
            "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0",
        },
    }
    for base, expected_logs in logs.items():
        for relative, token in expected_logs.items():
            text = read_text(base / relative)
            require(token in text, f"missing log token {base.name}/{relative}: {token}", failures)
            for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token {base.name}/{relative}: {bad}", failures)
            if "pre-boundary" not in relative:
                require("missing=1" not in text, f"unexpected missing=1 {base.name}/{relative}", failures)


def check_target_artifacts(failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        base = expected["artifact_base"]
        metadata = row_map(base / expected["metadata"])
        tags = row_map(base / expected["tags"])
        decompile = row_map(base / expected["decompile"])
        xrefs = read_tsv(base / expected["xrefs"])
        instructions = read_tsv(base / expected["instructions"])

        row = metadata.get(address)
        require(row is not None, f"{expected['source']} metadata missing: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"{expected['source']} metadata name mismatch: {address}", failures)
            require(row.get("signature") == expected["signature"], f"{expected['source']} metadata signature mismatch: {address}", failures)
            require(row.get("status") == "OK", f"{expected['source']} metadata status mismatch: {address}", failures)
            for token in expected["comment_tokens"]:
                require(token in row.get("comment", ""), f"{expected['source']} metadata missing token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"{expected['source']} tags missing: {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"{expected['source']} tag status mismatch: {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"{expected['source']} decompile missing: {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"{expected['source']} decompile name mismatch: {address}", failures)
            require(dec.get("signature") == expected["signature"], f"{expected['source']} decompile signature mismatch: {address}", failures)
            require(dec.get("status") == "OK", f"{expected['source']} decompile status mismatch: {address}", failures)

        for from_addr, from_function, ref_type in expected["xref_expectations"]:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == from_addr
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"{expected['source']} missing xref {from_addr} -> {address}",
                failures,
            )

        for instr_addr, mnemonic, operand_token in expected["instruction_tokens"]:
            require(
                any(
                    normalize_address(row.get("instruction_addr", "")) == instr_addr
                    and row.get("mnemonic") == mnemonic
                    and operand_token in row.get("operands", "")
                    and row.get("function_name") == expected["name"]
                    for row in instructions
                ),
                f"{expected['source']} missing instruction {instr_addr} {mnemonic} {operand_token}",
                failures,
            )

        decompile_text = read_text(base / expected["decompile_file"])
        for token in expected["decompile_tokens"]:
            require(token in decompile_text, f"{expected['source']} decompile file missing token {address}: {token}", failures)


def check_backups(failures: list[str]) -> None:
    wave936 = read_json(WAVE936_BASE / "backup-summary.json")
    require(wave936.get("backupPath") == WAVE936_BACKUP, "Wave936 backup path mismatch", failures)
    require(wave936.get("fileCount") == 19, "Wave936 backup file count mismatch", failures)
    require(int(wave936.get("totalBytes", -1)) == 173247367, "Wave936 backup byte count mismatch", failures)
    require(wave936.get("diffCount") == 0, "Wave936 backup diff mismatch", failures)

    wave1010 = read_json(WAVE1010_BASE / "backup-summary.json")
    require(wave1010.get("backupPath") == WAVE1010_BACKUP, "Wave1010 backup path mismatch", failures)
    require(wave1010.get("fileCount") == 19, "Wave1010 backup file count mismatch", failures)
    require(int(wave1010.get("totalBytes", -1)) == 173935495, "Wave1010 backup byte count mismatch", failures)
    require(wave1010.get("diffCount") == 0, "Wave1010 backup diff mismatch", failures)
    require(wave1010.get("hashDiffCount") == 0, "Wave1010 backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1113 note": read_text(NOTE),
        "wave1113 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "BattleEngine index": read_text(BATTLEENGINE_INDEX),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1113 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)
    current = read_json(PROGRESS).get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 33, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "2.80%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1113-battleengine-wave936-wave1010-current-risk-supersession")
        == r"py -3 tools\wave1113_battleengine_wave936_wave1010_current_risk_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_membership(failures)
    check_current_queue(failures)
    check_artifact_counts_and_logs(failures)
    check_target_artifacts(failures)
    check_backups(failures)
    check_docs(failures)

    if failures:
        print("Wave1113 BattleEngine current-risk supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1113 BattleEngine current-risk supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
