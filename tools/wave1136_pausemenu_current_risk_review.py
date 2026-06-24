#!/usr/bin/env python3
"""Validate Wave1136 PauseMenu current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1136-pausemenu-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1136-pausemenu-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1136-pausemenu-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1136_pausemenu_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PAUSEMENU_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified"

TARGETS = {
    "0x004d0290": (
        "CControllerBackMenuItem__RenderBindingCapacityWarning",
        "void __thiscall CControllerBackMenuItem__RenderBindingCapacityWarning(void * this, float x, float y, int render_flags)",
        ("Controls__FindFirstFreeBindingSlot", "0xe8/0xe9", "CMenuItem__RenderWithColor"),
        (("0x005de604", "<no_function>", "DATA"),),
        ("controller-back", "menu-item", "pausemenu-tail-wave465", "static-reaudit"),
    ),
    "0x004d04b0": (
        "CPauseMenu__scalar_deleting_dtor",
        "void * __thiscall CPauseMenu__scalar_deleting_dtor(void * this, int flags)",
        ("CPauseMenu__dtor_base", "flags bit 0", "returns this"),
        (("0x005de700", "<no_function>", "DATA"),),
        ("destructor", "pause-menu", "pausemenu-tail-wave465", "static-reaudit"),
    ),
    "0x004d0510": (
        "CPauseMenu__LoadPauseTextures",
        "void __fastcall CPauseMenu__LoadPauseTextures(void * pause_menu)",
        ("CMenuItemRange__LoadTexture", "pause_circle01/02", "FE_Blank.tga"),
        (("0x0046e3b2", "CGame__RunLevel", "UNCONDITIONAL_CALL"),),
        ("pause-menu", "pausemenu-tail-wave465", "texture-load", "static-reaudit"),
    ),
    "0x004d06e0": (
        "CPauseMenu__ResumeGameAndPersistOptions",
        "void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * pause_menu)",
        ("relinquishes controllers", "defaultoptions.bea", "timestamps the pause menu"),
        (
            ("0x004d16f9", "CPauseMenu__VFunc_03_HandleMenuControlInput", "UNCONDITIONAL_CALL"),
            ("0x004d0c8a", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
        ),
        ("options-persist", "pause-menu", "pausemenu-tail-wave465", "static-reaudit"),
    ),
    "0x004d0db0": (
        "CPauseMenu__InitBindingPromptAction",
        "void * __thiscall CPauseMenu__InitBindingPromptAction(void * this, void * menu_item, void * pause_menu, int action_id)",
        ("CPauseMenu__InitAndSetActiveReader", "RET 0x0c", "three stack arguments"),
        (
            ("0x004d09fe", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
            ("0x004d0aa5", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
        ),
        ("binding-prompt", "pause-menu", "pausemenu-tail-wave465", "static-reaudit"),
    ),
    "0x004d11d0": (
        "CPauseMenu__Render",
        "short * __thiscall CPauseMenu__Render(void * this)",
        ("CDXEngine__PostRender", "CFEPOptions__Update", "title text pointer"),
        (
            ("0x0053ee24", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
            ("0x0051f71d", "CFEPOptions__Update", "UNCONDITIONAL_CALL"),
        ),
        ("frontend-menu", "pause-menu", "pausemenu-render-wave481", "static-reaudit"),
    ),
    "0x004d15d0": (
        "CPauseMenu__VFunc_03_HandleMenuControlInput",
        "void __thiscall CPauseMenu__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)",
        ("this+0x2c", "button 0x2e", "RET 0x0c"),
        (("0x005de708", "<no_function>", "DATA"),),
        ("control-input", "pause-menu", "pausemenu-vfunc-tail-wave474", "static-reaudit"),
    ),
    "0x004d1730": (
        "CSimpleGameMenu__scalar_deleting_dtor",
        "void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags)",
        ("CSimpleGameMenu__dtor_base", "flags bit 0", "RET 0x4"),
        (("0x005de720", "<no_function>", "DATA"),),
        ("destructor", "simple-game-menu", "pausemenu-vfunc-tail-wave474", "static-reaudit"),
    ),
}

CONTEXT_TARGETS = {
    "0x004d04d0": "CPauseMenu__ReloadSharedBlankTexture",
    "0x004d05e0": "CPauseMenu__dtor_base",
    "0x004d0810": "CPauseMenu__ButtonPressed",
    "0x004d0de0": "CPauseMenu__GetBindingCapacityWarningText",
    "0x004d0e40": "CGameMenu__InitBase",
    "0x004d0ff0": "CPauseMenu__InitPauseSession",
    "0x004d1750": "CSimpleGameMenu__dtor_base",
}

DOC_TOKENS = (
    "Wave1136",
    "wave1136-pausemenu-current-risk-review",
    "204/1179 = 17.30%",
    "8 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 975",
    "PauseMenu/SimpleGameMenu current-risk cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime pause-menu behavior proven",
    "runtime controller-binding behavior proven",
    "runtime options persistence proven",
    "runtime render behavior proven",
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


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs_and_counts(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 11 rows",
        "pre-instructions.log": "Wrote 670 function-body instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "context-xrefs.log": "Wrote 10 rows",
        "context-instructions.log": "Wrote 624 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    expected_counts = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 11,
        "pre-instructions.tsv": 670,
        "pre-decompile/index.tsv": 8,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 10,
        "context-instructions.tsv": 624,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}

    for address, (name, signature, comment_tokens, xref_specs, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens:
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        require((BASE / "pre-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)

        for from_addr, from_function, ref_type in xref_specs:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref for {address}: {(from_addr, from_function, ref_type)}",
                failures,
            )

    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        PAUSEMENU_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    context_tokens = tuple(f"context {address} {name}" for address, name in CONTEXT_TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    note_text = read_text(NOTE)
    for token in context_tokens:
        require(contains_token(note_text, token), f"missing context token in note: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1136 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)

    for label, data in (("progress", read_json(PROGRESS)), ("progress mirror", read_json(PROGRESS_MIRROR))):
        latest = data["latestWave"]
        current = data["post100Reaudit"]["currentRiskRank"]
        require(latest["wave"] == "Wave1136 PauseMenu current-risk review", f"{label} latest wave mismatch", failures)
        require(latest["tag"] == "wave1136-pausemenu-current-risk-review", f"{label} latest tag mismatch", failures)
        require(latest["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = latest.get("artifactCommit")
        require(
            artifact_commit == "pending Wave1136 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 204, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "17.30%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1136-pausemenu-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 975, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1136_pausemenu_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1136-pausemenu-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs_and_counts(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1136 PauseMenu current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1136 PauseMenu current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
