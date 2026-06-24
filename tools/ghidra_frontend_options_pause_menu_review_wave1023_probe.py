#!/usr/bin/env python3
"""Validate Wave1023 frontend options / pause-menu read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1023-frontend-options-pause-menu-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_options_pause_menu_review_wave1023_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1023_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
FEPOPTIONS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPOptions.cpp" / "_index.md"
MENUITEM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MenuItem.cpp" / "_index.md"
PAUSEMENU_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified"

TARGETS = {
    "0x004cdd70": ("GameControllers__RelinquishControlForTarget", "void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)", ("Wave479", "CController__RelinquishControl")),
    "0x004cddf0": ("Audio__ReinitializeSoundAndRestoreMusic", "void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)", ("Wave480", "CMusic__PlaySelection")),
    "0x004ceef0": ("LandscapeDetail_SetLevel", "void __stdcall LandscapeDetail_SetLevel(int detail_level)", ("Wave466", "g_LandscapeDetailLevel2")),
    "0x004cef30": ("LandscapeDetail_GetLevel", "int __cdecl LandscapeDetail_GetLevel(void)", ("Wave466", "g_LandscapeDetailLevel1")),
    "0x004cef50": ("CTreeDetail__SetQualityLevel", "void __stdcall CTreeDetail__SetQualityLevel(int quality_level)", ("Wave466", "CRTMesh__SetQualityLevel")),
    "0x004cf030": ("CMouseSensitivityMenuItem__scalar_deleting_dtor", "void * __thiscall CMouseSensitivityMenuItem__scalar_deleting_dtor(void * this, int flags)", ("Wave466", "CMenuItem__Destructor")),
    "0x004cf8e0": ("CMultiSample__GetSampleCountLabel", "void * __stdcall CMultiSample__GetSampleCountLabel(int available_sample_ordinal)", ("Wave466", "Localization__GetStringById")),
    "0x004cffd0": ("CVideoDetailLevel__GetCurrentPresetFromItems", "int __fastcall CVideoDetailLevel__GetCurrentPresetFromItems(void * video_detail_menu)", ("Wave466", "active display-profile defaults")),
    "0x004d01c0": ("CMenuItem__RestoreCompactVTable", "void __fastcall CMenuItem__RestoreCompactVTable(void * menu_item)", ("Wave465", "PTR_CMenuItem__scalar_deleting_dtor_005db440")),
    "0x004d0490": ("CMenuItem__shared_compact_scalar_deleting_dtor", "void * __thiscall CMenuItem__shared_compact_scalar_deleting_dtor(void * this, int flags)", ("Wave465", "CMenuItem__RestoreCompactVTable")),
    "0x004d04b0": ("CPauseMenu__scalar_deleting_dtor", "void * __thiscall CPauseMenu__scalar_deleting_dtor(void * this, int flags)", ("Wave465", "CPauseMenu__dtor_base")),
    "0x004d0510": ("CPauseMenu__LoadPauseTextures", "void __fastcall CPauseMenu__LoadPauseTextures(void * pause_menu)", ("Wave465", "FE_Blank.tga")),
    "0x004d05e0": ("CPauseMenu__dtor_base", "void __fastcall CPauseMenu__dtor_base(void * pause_menu)", ("Wave465", "CMonitor__Shutdown")),
    "0x004d11d0": ("CPauseMenu__Render", "short * __thiscall CPauseMenu__Render(void * this)", ("Wave481", "CDXEngine__PostRender")),
    "0x004d1730": ("CSimpleGameMenu__scalar_deleting_dtor", "void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags)", ("Wave474", "CSimpleGameMenu__dtor_base")),
    "0x004d1750": ("CSimpleGameMenu__dtor_base", "void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu)", ("Wave474", "CMenuItemRange")),
}

DOC_TOKENS = (
    "Wave1023",
    "frontend-options-pause-menu-review-wave1023",
    "0x004cdd70 GameControllers__RelinquishControlForTarget",
    "0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic",
    "0x004ceef0 LandscapeDetail_SetLevel",
    "0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems",
    "0x004d04b0 CPauseMenu__scalar_deleting_dtor",
    "0x004d11d0 CPauseMenu__Render",
    "0x004d1750 CSimpleGameMenu__dtor_base",
    "555/1408 = 39.42%",
    "784/1493 = 52.51%",
    "483/500 = 96.60%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    CONTROLLER_DOC: ("Wave1023", "frontend-options-pause-menu-review-wave1023", "0x004cdd70 GameControllers__RelinquishControlForTarget", BACKUP_PATH),
    SOUNDMANAGER_DOC: ("Wave1023", "frontend-options-pause-menu-review-wave1023", "0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic", BACKUP_PATH),
    FEPOPTIONS_DOC: ("Wave1023", "frontend-options-pause-menu-review-wave1023", "0x004ceef0 LandscapeDetail_SetLevel", "0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems", BACKUP_PATH),
    MENUITEM_DOC: ("Wave1023", "frontend-options-pause-menu-review-wave1023", "0x004d01c0 CMenuItem__RestoreCompactVTable", "0x004d0490 CMenuItem__shared_compact_scalar_deleting_dtor", BACKUP_PATH),
    PAUSEMENU_DOC: ("Wave1023", "frontend-options-pause-menu-review-wave1023", "0x004d04b0 CPauseMenu__scalar_deleting_dtor", "0x004d11d0 CPauseMenu__Render", "0x004d1750 CSimpleGameMenu__dtor_base", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime options-menu behavior proven",
    "runtime audio/music reset behavior proven",
    "runtime pause-menu behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 16,
        "tags.tsv": 16,
        "xrefs.tsv": 50,
        "instructions.tsv": 905,
        "decompile/index.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    text = read_text(BASE / "instructions.tsv") + "\n" + read_text(BASE / "xrefs.tsv")
    for token in ("CController__RelinquishControl", "CSoundManager__ReinitializeAfterDeviceLoss", "CRTMesh__SetQualityLevel", "FE_Blank.tga", "CMonitor__Shutdown", "CDXEngine__PostRender"):
        require(token in text or token in read_text(BASE / "metadata.tsv"), f"missing evidence token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=16 found=16 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "xrefs.log": "Wrote 50 rows",
        "instructions.log": "targets=16 missing=0",
        "decompile.log": "targets=16 dumped=16 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [NOTE, AGGREGATE_NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, FUNCTION_COVERAGE, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE, TRACKING_STATE]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-frontend-options-pause-menu-review-wave1023")
        == r"py -3 tools\ghidra_frontend_options_pause_menu_review_wave1023_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1023-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1023 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1023 frontend options pause menu review" for row in ledger), "missing Wave1023 ledger row", failures)
    require(any(row.get("task") == "Wave1023 frontend options pause menu review" and row.get("attempt_id") == 20605 for row in attempts), "missing Wave1023 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1023 frontend options / pause-menu review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1023 frontend options / pause-menu review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
