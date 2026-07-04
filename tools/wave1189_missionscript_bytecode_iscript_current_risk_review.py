#!/usr/bin/env python3
"""Validate Wave1189 MissionScript bytecode/IScript current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1189-missionscript-bytecode-iscript-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1189-missionscript-bytecode-iscript-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1189-missionscript-bytecode-iscript-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1189_missionscript_bytecode_iscript_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
ASM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AsmInstruction.cpp.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
OBJECT_CODE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
APPLY_SCRIPT = ROOT / "tools" / "ApplyMissionScriptBytecodeIScriptCurrentRiskWave1189.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified"

TARGETS = {
    "0x0052e180": {
        "name": "CInstructionOP_PLUS__VFunc_00_0052e180",
        "signature": "void __thiscall CInstructionOP_PLUS__VFunc_00_0052e180(void * this, void * script_state, void * data_stack, void * object_code)",
        "comment_tokens": ("Wave1189 static read-back", "0x005e4d30", "datatype vtable slot +0x04", "data_stack", "clean-room/no-noticeable-difference parity remain separate proof"),
        "xref_set": {("0x005e4d30", "DATA")},
    },
    "0x0052e1d0": {
        "name": "CInstructionOP_MINUS__VFunc_00_0052e1d0",
        "signature": "void __thiscall CInstructionOP_MINUS__VFunc_00_0052e1d0(void * this, void * script_state, void * data_stack, void * object_code)",
        "comment_tokens": ("Wave1189 static read-back", "0x005e4d20", "datatype vtable slot +0x08", "data_stack", "clean-room/no-noticeable-difference parity remain separate proof"),
        "xref_set": {("0x005e4d20", "DATA")},
    },
    "0x0052e220": {
        "name": "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
        "signature": "void __thiscall CInstructionOP_MULTIPLY__VFunc_00_0052e220(void * this, void * script_state, void * data_stack, void * object_code)",
        "comment_tokens": ("Wave1189 static read-back", "0x005e4d10", "datatype vtable slot +0x0c", "data_stack", "clean-room/no-noticeable-difference parity remain separate proof"),
        "xref_set": {("0x005e4d10", "DATA")},
    },
    "0x0052e270": {
        "name": "CInstructionOP_DIVIDE__VFunc_00_0052e270",
        "signature": "void __thiscall CInstructionOP_DIVIDE__VFunc_00_0052e270(void * this, void * script_state, void * data_stack, void * object_code)",
        "comment_tokens": ("Wave1189 static read-back", "0x005e4d00", "datatype vtable slot +0x10", "data_stack", "clean-room/no-noticeable-difference parity remain separate proof"),
        "xref_set": {("0x005e4d00", "DATA")},
    },
    "0x0052e330": {
        "name": "CInstructionOP_CMP__VFunc_00_0052e330",
        "signature": "void __thiscall CInstructionOP_CMP__VFunc_00_0052e330(void * this, void * script_state, void * data_stack, void * object_code)",
        "comment_tokens": ("Wave1189 static read-back", "0x005e4c50", "CScriptObjectCode__GetTop", "script_state+0x218", "datatype vtable slot +0x18"),
        "xref_set": {("0x005e4c50", "DATA")},
    },
    "0x005333b0": {
        "name": "IScript__Constructor",
        "signature": "void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)",
        "comment_tokens": ("Wave1189 static read-back", "CComplexThing__SetScript", "0x004f42a8", "0x005e4f08", "script_object_code+0x68"),
        "xref_set": {("0x004f42a8", "UNCONDITIONAL_CALL")},
    },
    "0x00539f30": {
        "name": "CMissionScriptObjectCode__ClearFields_Thunk",
        "signature": "void __fastcall CMissionScriptObjectCode__ClearFields_Thunk(void * field_block)",
        "comment_tokens": ("Wave1189 static read-back", "CHud__ShutDown", "0x00481b44", "0x00539f40", "HUD script-field-block teardown bridge"),
        "xref_set": {("0x00481b44", "UNCONDITIONAL_CALL")},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1189-missionscript-bytecode-iscript-current-risk-review",
    "wave1189-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "mission-script",
    "source-identity-deferred",
    "exact-layout-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1189",
    "wave1189-missionscript-bytecode-iscript-current-risk-review",
    "808/1179 = 68.53%",
    "7 MissionScript bytecode/IScript current-risk rows",
    "current focused candidates: 1169",
    "live regenerated current focused candidates: 1169",
    "remaining active focused work: 371",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=7 skipped=0",
    "comment_only_updated=7",
    "tags_added=63",
    "final dry updated=0 skipped=7",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CAsmInstruction__SpawnFromOpcode already accounted by Wave1120",
    "CInstructionOP_PLUS__VFunc_00_0052e180",
    "CInstructionOP_MINUS__VFunc_00_0052e1d0",
    "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
    "CInstructionOP_DIVIDE__VFunc_00_0052e270",
    "CInstructionOP_CMP__VFunc_00_0052e330",
    "IScript__Constructor",
    "CMissionScriptObjectCode__ClearFields_Thunk",
    "CScriptObjectCode__GetTop",
    "CComplexThing__SetScript",
    "CHud__ShutDown",
    "datatype vtable slot +0x04",
    "datatype vtable slot +0x08",
    "datatype vtable slot +0x0c",
    "datatype vtable slot +0x10",
    "datatype vtable slot +0x18",
    "script_state+0x218",
    "script_object_code+0x68",
    "vtable 0x005e4f08",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "7 xref rows",
    "208 instruction rows",
    "7 decompile rows",
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
    "runtime missionscript behavior proven",
    "runtime hud/script teardown behavior proven",
    "exact missionscript vm layout proven",
    "exact datatype layout proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 208,
        "pre-decompile/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 7,
        "post-instructions.tsv": 208,
        "post-decompile/index.tsv": 7,
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "rows=7 missing=0",
        "post-xrefs.log": "Wrote 7 rows",
        "post-instructions.log": "Wrote 208 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1189_queue_probe.log")
    require("Status: PASS" in queue_log, "queue probe did not pass", failures)
    export_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1189.log")
    require("total_functions=6411 commented_functions=6411" in export_log, "quality export count mismatch", failures)
    rank_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1189-current-risk-rank-refresh.log")
    require("risk: 6166" in rank_log, "current-risk rank count mismatch", failures)
    require("focused: 1169" in rank_log, "current focused rank count mismatch", failures)

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
            require("Wave1189 static read-back" in row.get("comment", ""), f"quality TSV missing Wave1189 comment at {address}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176196487, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1189 MissionScript Bytecode / IScript Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1189-missionscript-bytecode-iscript-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    artifact_commit = str(latest.get("artifactCommit", ""))
    require(
        artifact_commit == "pending Wave1189 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", artifact_commit)),
        "latest artifact commit mismatch",
        failures,
    )
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 808, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "68.53%", "current focused percent mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1169, "live focused mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 371, "remaining focused mismatch", failures)
    require(current.get("latestReviewTag") == "wave1189-missionscript-bytecode-iscript-current-risk-review", "latest review tag mismatch", failures)
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
        ASM_DOC,
        ISCRIPT_DOC,
        OBJECT_CODE_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1189 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1189-missionscript-bytecode-iscript-current-risk-review")
        == r"py -3 tools\wave1189_missionscript_bytecode_iscript_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1189 apply script", failures)


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
        print("Wave1189 MissionScript bytecode/IScript current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1189 MissionScript bytecode/IScript current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
