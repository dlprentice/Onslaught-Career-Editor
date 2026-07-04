#!/usr/bin/env python3
"""Validate Wave1151 mixed score21 current-risk tag-normalization artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1151-mixed-score21-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1151-mixed-score21-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1151-mixed-score21-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1151_mixed_score21_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified"

COMMON_TAGS = {
    "static-reaudit",
    "wave1151-mixed-score21-current-risk-review",
    "wave1151-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score-21-current-risk",
    "mixed-score21-current-risk-review",
}

TARGETS = {
    "0x00403ff0": (
        "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
        "void __thiscall CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk(void * this)",
        ("CRT__EhVectorDestructorIterator_WithUnwind", "CResourceDescriptor__dtor", "resource-descriptor"),
    ),
    "0x00405990": (
        "CDXCockpit__dtor_base_thunk",
        "void __fastcall CDXCockpit__dtor_base_thunk(void * this)",
        ("CCockpit__dtor_base", "CDXCockpit__scalar_deleting_dtor"),
    ),
    "0x004059a0": (
        "CCylinder__VFunc_01_004059a0",
        "int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)",
        ("dispatchObject", "+0x8"),
    ),
    "0x004098c0": (
        "CLine__VFunc_01_004098c0",
        "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)",
        ("dispatch_target", "+0x10"),
    ),
    "0x00417870": (
        "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
        "void __fastcall CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward(void * this)",
        ("CWorld__RemoveUnitFromOccupancyGrid", "0x004f95d0", "static-shadow"),
    ),
    "0x004661c0": (
        "DeviceObject__dtor_thunk",
        "void __thiscall DeviceObject__dtor_thunk(void * this)",
        ("DeviceObject", "0x00512d50", "DAT_00889074"),
    ),
    "0x0046a220": (
        "FrontEndText__GetMultiplayerLevelDescriptionByType",
        "short * __cdecl FrontEndText__GetMultiplayerLevelDescriptionByType(int level_type)",
        ("Unknown Multiplayer Level Description", "CText__GetStringById", "multiplayer"),
    ),
    "0x004bd5c0": (
        "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
        "void __cdecl CWorld__RasterizeFootprintIntoOccupancyBitplanes(int min_world_x, int min_world_y, int max_world_x, int max_world_y, int skip_shadow_rebuild)",
        ("CHeightField__GetHeightSamplePacked16", "CWorld__SetOrClearOccupancyBit", "static-shadow"),
    ),
    "0x004cf050": (
        "CMenuItem__Destructor_Thunk",
        "void __thiscall CMenuItem__Destructor_Thunk(void * this)",
        ("CMenuItem__Destructor", "CMouseSensitivityMenuItem__scalar_deleting_dtor"),
    ),
    "0x004dba40": (
        "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
        "void * __fastcall CRTBuilding__VFuncSlot10_PickRandomLinkedEntry(void * this)",
        ("rand", "0x54", "0x58"),
    ),
    "0x0055e3ea": (
        "CRT__FpuIntrinsicDispatch2Thunk",
        "void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)",
        ("__cintrindisp2", "44 broad math"),
    ),
    "0x00564a0b": (
        "CRT__SpawnSearchPathWithFallbackExtensions",
        "int __cdecl CRT__SpawnSearchPathWithFallbackExtensions(int spawnMode, char * commandPath, void * argv, void * envp)",
        ("CRT__SpawnResolvedPathWithBuiltCommandEnv", "fallback extensions", "path-probe"),
    ),
    "0x00569cb8": (
        "CRT__FloatDispatchAmsgExitCode2Thunk",
        "void CRT__FloatDispatchAmsgExitCode2Thunk(void)",
        ("__amsg_exit", "runtime error code 2", "float-conversion"),
    ),
}

DOC_TOKENS = (
    "Wave1151",
    "wave1151-mixed-score21-current-risk-review",
    "368/1179 = 31.21%",
    "13 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 811",
    "current risk candidates: 6166",
    "mixed score21 current-risk review",
    "fresh Ghidra export",
    "tag-only normalization",
    "81 tags",
    "resource descriptor cleanup thunk, cockpit destructor thunk, primitive collision vfunc wrappers, building occupancy/static-shadow vfunc, DeviceObject destructor thunk, frontend multiplayer text helper, world occupancy rasterizer, menu-item destructor thunk, RTBuilding random linked entry, and CRT runtime thunk/path/float-dispatch helpers",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
    "CDXCockpit__dtor_base_thunk",
    "CCylinder__VFunc_01_004059a0",
    "CLine__VFunc_01_004098c0",
    "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
    "DeviceObject__dtor_thunk",
    "FrontEndText__GetMultiplayerLevelDescriptionByType",
    "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
    "CMenuItem__Destructor_Thunk",
    "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
    "CRT__FpuIntrinsicDispatch2Thunk",
    "CRT__SpawnSearchPathWithFallbackExtensions",
    "CRT__FloatDispatchAmsgExitCode2Thunk",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime resource cleanup proven",
    "runtime cockpit behavior proven",
    "runtime collision behavior proven",
    "runtime building behavior proven",
    "runtime deviceobject behavior proven",
    "runtime frontend behavior proven",
    "runtime world occupancy behavior proven",
    "runtime menu behavior proven",
    "runtime crt behavior proven",
    "exact layout proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 89,
        "pre-instructions.tsv": 593,
        "pre-decompile/index.tsv": 13,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 89,
        "post-instructions.tsv": 593,
        "post-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "post-xrefs.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "post-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "post-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, evidence_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in evidence_tokens:
                token_ok = token.lower().replace(" ", "") in compact or token in evidence
                require(token_ok, f"missing evidence token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xref_targets, f"missing xrefs for {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 89 rows",
        "pre-instructions.log": "Wrote 593 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=81 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=81 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 89 rows",
        "post-instructions.log": "Wrote 593 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative == "apply.log":
            require("REPORT: Save succeeded" in text, "apply log missing save report", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_progress(failures: list[str]) -> None:
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
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1151 mixed score21 current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1151-mixed-score21-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 368, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "31.21%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 811, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)


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
        PROGRESS,
        PROGRESS_MIRROR,
        README,
        AGENTS,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1151 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1151-mixed-score21-current-risk-review")
        == r"py -3 tools\wave1151_mixed_score21_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_progress(failures)
    check_docs(failures)
    if failures:
        print("Wave1151 mixed score21 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1151 mixed score21 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
