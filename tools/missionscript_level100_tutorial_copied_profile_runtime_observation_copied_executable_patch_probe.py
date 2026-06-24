#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-executable patch proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"
MATERIALIZATION_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_copied_executable_patch_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

PROFILE_ID = "level100-clean-materialized-20260608-214752"
PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / PROFILE_ID
PRIVATE_EXE = PRIVATE_PROFILE_ROOT / "BEA.exe"
PRIVATE_BACKUP = PRIVATE_PROFILE_ROOT / "BEA.exe.original.backup"
PATCH_PROOF_DIR = PRIVATE_PROFILE_ROOT / "patch-proof.private"
DRY_RUN_JSON = PATCH_PROOF_DIR / "patch-dry-run.private.json"
APPLY_JSON = PATCH_PROOF_DIR / "patch-apply.private.json"
READBACK_JSON = PATCH_PROOF_DIR / "patch-readback.private.json"
SUMMARY_JSON = PATCH_PROOF_DIR / "patch-summary.private.json"

EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"

PATCH_ROWS = [
    ("resolution_gate", "0x129696"),
    ("force_windowed", "0x12A644"),
    ("version_overlay_use_patched_format_pointer", "0x6416F"),
    ("version_overlay_patched_format_cave_string", "0x1AA444"),
]

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<PRIVATE_PATH_REDACTED>\\",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "runtime text/audio behavior proven",
    "runtime hud flashing proven",
    "runtime observation proof complete",
    "bea launch proof complete",
    "bea launch authorized",
    "screenshot proof complete",
    "native input proof complete",
    "debugger observation proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in rows}


def check_row_states(data: dict[str, Any], expected_before: str, expected_after: str, failures: list[str], label: str) -> None:
    before = rows_by_id(data["before"])
    after = rows_by_id(data["after"])
    require(set(before) == {row_id for row_id, _ in PATCH_ROWS}, f"{label} before patch ids mismatch", failures)
    require(set(after) == {row_id for row_id, _ in PATCH_ROWS}, f"{label} after patch ids mismatch", failures)
    require("skip_auto_toggle" not in before, f"{label} accidentally includes skip_auto_toggle before row", failures)
    require("skip_auto_toggle" not in after, f"{label} accidentally includes skip_auto_toggle after row", failures)
    for row_id, offset in PATCH_ROWS:
        require(before[row_id]["track"] == "stable", f"{label} before track mismatch for {row_id}", failures)
        require(after[row_id]["track"] == "stable", f"{label} after track mismatch for {row_id}", failures)
        require(before[row_id]["fileOffset"] == offset, f"{label} before offset mismatch for {row_id}", failures)
        require(after[row_id]["fileOffset"] == offset, f"{label} after offset mismatch for {row_id}", failures)
        require(before[row_id]["state"] == expected_before, f"{label} before state mismatch for {row_id}", failures)
        require(after[row_id]["state"] == expected_after, f"{label} after state mismatch for {row_id}", failures)


def check_private_evidence(failures: list[str]) -> None:
    require(PRIVATE_EXE.is_file(), "private copied BEA.exe missing", failures)
    require(PRIVATE_BACKUP.is_file(), "private clean backup missing", failures)
    require(PATCH_PROOF_DIR.is_dir(), "private patch proof dir missing", failures)
    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(PRIVATE_BACKUP.stat().st_size == 2506752, "private clean backup byte size mismatch", failures)
    require(sha256(PRIVATE_EXE) == PATCHED_SHA, "private copied BEA.exe patched hash mismatch", failures)
    require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "private backup clean hash mismatch", failures)

    dry = read_json(DRY_RUN_JSON)
    apply = read_json(APPLY_JSON)
    readback = read_json(READBACK_JSON)
    summary = read_json(SUMMARY_JSON)

    expected_target = str(PRIVATE_EXE)
    require(dry["target"] == expected_target, "dry-run target mismatch", failures)
    require(apply["target"] == expected_target, "apply target mismatch", failures)
    require(readback["target"] == expected_target, "readback target mismatch", failures)
    require("Program Files" not in dry["target"], "dry-run target is not copied-profile scoped", failures)
    require("Program Files" not in apply["target"], "apply target is not copied-profile scoped", failures)
    require("Program Files" not in readback["target"], "readback target is not copied-profile scoped", failures)

    require(dry["success"] is True, "dry-run success mismatch", failures)
    require(dry["applied"] is False, "dry-run applied flag mismatch", failures)
    require(dry["message"] == "dry-run: no bytes were written", "dry-run message mismatch", failures)
    check_row_states(dry, "ready (original)", "ready (original)", failures, "dry-run")

    require(apply["success"] is True, "apply success mismatch", failures)
    require(apply["applied"] is True, "apply applied flag mismatch", failures)
    require(apply["message"] == "patch apply complete", "apply message mismatch", failures)
    require(Path(apply["backup"]).name == "BEA.exe.original.backup", "apply backup basename mismatch", failures)
    check_row_states(apply, "ready (original)", "already patched", failures, "apply")

    require(readback["success"] is True, "readback success mismatch", failures)
    require(readback["applied"] is False, "readback applied flag mismatch", failures)
    require(readback["message"] == "verified: no bytes were written", "readback message mismatch", failures)
    check_row_states(readback, "already patched", "already patched", failures, "readback")

    require(summary["targetBytes"] == 2506752, "summary target bytes mismatch", failures)
    require(summary["targetHash"] == PATCHED_SHA, "summary target hash mismatch", failures)
    require(summary["backupExists"] is True, "summary backup exists mismatch", failures)
    require(summary["backupBytes"] == 2506752, "summary backup bytes mismatch", failures)
    require(summary["backupHash"] == EXPECTED_CLEAN_SHA, "summary backup hash mismatch", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore copied-executable patch result mirror mismatch", failures)
    require(read_json(MATERIALIZATION_RESULT)["nextStaticSlice"] == THIS_SLICE, "materialization result does not point to copied-executable patch lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["patchStatus"] == "stable-copied-executable-patched", "patchStatus mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    patch = result["copiedExecutablePatch"]
    require(patch["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(patch["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(patch["targetExecutableClass"] == "copied-profile-BEA.exe", "target executable class mismatch", failures)
    require(patch["privatePathIncluded"] is False, "private path flag mismatch", failures)
    require(patch["rawArtifactIncluded"] is False, "raw artifact flag mismatch", failures)
    require(patch["patchTool"] == "tools/apply_bea_catalog_patch.py", "patch tool mismatch", failures)
    require(patch["catalog"] == "patches/catalog/patches.v2.json", "patch catalog mismatch", failures)
    require(patch["stablePatchRows"] == 4, "stable patch row count mismatch", failures)
    require(patch["expectedCleanSha256"] == EXPECTED_CLEAN_SHA, "expected clean hash mismatch", failures)
    require(patch["prePatchSha256"] == EXPECTED_CLEAN_SHA, "pre-patch hash mismatch", failures)
    require(patch["postPatchSha256"] == PATCHED_SHA, "post-patch hash mismatch", failures)
    require(patch["backupSha256"] == EXPECTED_CLEAN_SHA, "backup hash mismatch", failures)
    require(patch["targetBytes"] == 2506752, "target byte count mismatch", failures)
    require(patch["backupBytes"] == 2506752, "backup byte count mismatch", failures)
    require(patch["dryRunMessage"] == "dry-run: no bytes were written", "dry-run message mismatch in result", failures)
    require(patch["applyMessage"] == "patch apply complete", "apply message mismatch in result", failures)
    require(patch["readbackMessage"] == "verified: no bytes were written", "readback message mismatch in result", failures)
    require(patch["patchIdsApplied"] == [row_id for row_id, _ in PATCH_ROWS], "patchIdsApplied mismatch", failures)
    require(patch["experimentalPatchIdsNotArmed"] == ["skip_auto_toggle"], "experimental patch boundary mismatch", failures)
    require(patch["skipAutoToggleArmed"] is False, "skipAutoToggleArmed mismatch", failures)

    require(len(result["patchRows"]) == 4, "patchRows length mismatch", failures)
    rows = rows_by_id(result["patchRows"])
    for row_id, offset in PATCH_ROWS:
        row = rows.get(row_id)
        require(row is not None, f"missing patch row in result: {row_id}", failures)
        if row is not None:
            require(row["track"] == "stable", f"result row track mismatch: {row_id}", failures)
            require(row["fileOffset"] == offset, f"result row offset mismatch: {row_id}", failures)
            require(row["dryRunState"] == "ready (original)", f"result dry-run state mismatch: {row_id}", failures)
            require(row["applyBeforeState"] == "ready (original)", f"result apply-before state mismatch: {row_id}", failures)
            require(row["applyAfterState"] == "already patched", f"result apply-after state mismatch: {row_id}", failures)
            require(row["readbackState"] == "already patched", f"result readback state mismatch: {row_id}", failures)

    guard = result["guardSummary"]
    require(guard["copiedExecutablePatch"] is True, "copiedExecutablePatch guard mismatch", failures)
    for key in (
        "installedGameMutation",
        "originalExecutableMutation",
        "beLaunch",
        "launchArmed",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["runtimeEvidenceRows"] == 0, "runtime evidence rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore copied-executable patch plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore copied-executable patch result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof",
        "complete copied-executable stable patch proof, not launch or runtime proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "patchStatus=stable-copied-executable-patched",
        f"profileId={PROFILE_ID}",
        "artifactRootClass=repo-local-ignored-private-evidence-root",
        "targetExecutableClass=copied-profile-BEA.exe",
        "tools/apply_bea_catalog_patch.py",
        "patches/catalog/patches.v2.json",
        "stablePatchRows=4",
        "skipAutoToggleArmed=false",
        f"prePatchSha256={EXPECTED_CLEAN_SHA}",
        f"targetHash={PATCHED_SHA}",
        f"backupHash={EXPECTED_CLEAN_SHA}",
        "targetBytes=2506752",
        "backupBytes=2506752",
        "dryRunMessage=dry-run: no bytes were written",
        "applyMessage=patch apply complete",
        "readbackMessage=verified: no bytes were written",
        "resolution_gate",
        "force_windowed",
        "version_overlay_use_patched_format_pointer",
        "version_overlay_patched_format_cave_string",
        "skip_auto_toggle",
        "0x129696",
        "0x12A644",
        "0x6416F",
        "0x1AA444",
        "ready (original)",
        "already patched",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "beLaunch=false",
        "launchArmed=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "runtimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
        "0x00539dc0",
        "0x00539ca0",
        "CDXMemBuffer__InitFromFile",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in (
            PLAN_LINK,
            RESULT_LINK,
            THIS_SLICE,
            NEXT_SLICE,
            PROFILE_ID,
            "stable-copied-executable-patched",
            "stablePatchRows=4",
            "skipAutoToggleArmed=false",
            PATCHED_SHA,
            EXPECTED_CLEAN_SHA,
            "resolution_gate",
            "force_windowed",
            "version_overlay_use_patched_format_pointer",
            "version_overlay_patched_format_cave_string",
        ):
            require(token in text, f"{path.relative_to(ROOT)} missing copied-executable patch token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed copied-executable patch slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed launch-command follow-up slice", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan. Status: selected" not in backlog, "backlog still marks copied-executable patch as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_copied_executable_patch_probe.py --check",
        "missing package copied-executable patch test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_private_evidence(failures)
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 copied-executable patch probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-executable patch probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
