#!/usr/bin/env python3
"""Validate Wave1179 input/audio support current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1179-input-audio-support-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1179-input-audio-support-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1179-input-audio-support-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1179_input_audio_support_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FRONTEND_INPUT_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-static-review-2026-05-26.md"
AUDIO_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-static-review-2026-05-26.md"
INPUT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Input.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
PCSOUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "pcsoundmanager.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified"

TARGETS = {
    "0x0042da00": ("Input__UpdateCursorCenterWithWindowScale", "void __cdecl Input__UpdateCursorCenterWithWindowScale(bool recenterNow)"),
    "0x00523db0": ("Input__ResetMouseTransientState", "void __cdecl Input__ResetMouseTransientState(void)"),
    "0x004cdd70": ("GameControllers__RelinquishControlForTarget", "void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)"),
    "0x004cddf0": ("Audio__ReinitializeSoundAndRestoreMusic", "void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)"),
    "0x005054e0": ("CWaveSoundRead__ScalarDeletingDestructor", "void * __thiscall CWaveSoundRead__ScalarDeletingDestructor(void * this, byte delete_flags)"),
    "0x00517290": ("CPCSoundManager__LoadSampleFromBuffer_StubFail", "void * __stdcall CPCSoundManager__LoadSampleFromBuffer_StubFail(void * mem_buffer, int music)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1179-input-audio-support-current-risk-review",
    "wave1179-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "input-audio-support",
    "tag-normalized",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1179",
    "wave1179-input-audio-support-current-risk-review",
    "721/1179 = 61.15%",
    "6 input/controller/audio support current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 458",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "tag-only normalization",
    "updated=6 skipped=0",
    "tags_added=56",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "Codex root final judgment",
    "consult recommended four-row split",
    "root kept six-row input/audio support slice",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "13 xref rows",
    "152 instruction rows",
    "Input__UpdateCursorCenterWithWindowScale",
    "Input__ResetMouseTransientState",
    "GameControllers__RelinquishControlForTarget",
    "Audio__ReinitializeSoundAndRestoreMusic",
    "CWaveSoundRead__ScalarDeletingDestructor",
    "CPCSoundManager__LoadSampleFromBuffer_StubFail",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime input behavior proven",
    "runtime controller/menu behavior proven",
    "runtime audio/device-loss/sample-reader behavior proven",
    "exact concrete input/controller/audio layouts proven",
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 152,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 152,
        "post-decompile/index.tsv": 6,
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
            require("remain unproven" in row.get("comment", "") or "remain deferred" in row.get("comment", ""), f"missing bounded comment token {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing Wave1179 tags {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "rows=6 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 152 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1179 Input / Audio Support Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1179-input-audio-support-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 721, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "61.15%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 458, "remaining focused mismatch", failures)


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
        FRONTEND_INPUT_REVIEW,
        AUDIO_REVIEW,
        INPUT_DOC,
        CONTROLLER_DOC,
        SOUNDMANAGER_DOC,
        PCSOUND_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1179 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1179-input-audio-support-current-risk-review")
        == r"py -3 tools\wave1179_input_audio_support_current_risk_review.py --check",
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
        print("Wave1179 input/audio support current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1179 input/audio support current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
