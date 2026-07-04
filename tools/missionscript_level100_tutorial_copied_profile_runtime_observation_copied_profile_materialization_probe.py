#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile materialization proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"
CLEAN_SOURCE_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"
PREFLIGHT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_materialization_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"
PREPARE_HELPER = ROOT / "tools" / "prepare_game_profile.ps1"

PROFILE_ID = "level100-clean-materialized-20260608-214752"
PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / PROFILE_ID
PRIVATE_SUMMARY = PRIVATE_PROFILE_ROOT / "materialization-summary.private.json"
PRIVATE_EXE = PRIVATE_PROFILE_ROOT / "BEA.exe"
PRIVATE_BACKUP = PRIVATE_PROFILE_ROOT / "BEA.exe.original.backup"
PATCH_PROOF_DIR = PRIVATE_PROFILE_ROOT / "patch-proof.private"
LAUNCH_COMMAND_PROOF_DIR = PRIVATE_PROFILE_ROOT / "launch-command-proof.private"

EXPECTED_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
CURRENT_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"

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
    "bea patching behavior proven",
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


def check_private_evidence(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    require(PRIVATE_EXE.is_file(), "private copied BEA.exe missing", failures)
    target_hash = sha256(PRIVATE_EXE)
    clean_materialization_preserved = target_hash == EXPECTED_SHA
    downstream_patch_preserved_clean_backup = (
        target_hash == CURRENT_SHA and PRIVATE_BACKUP.is_file() and sha256(PRIVATE_BACKUP) == EXPECTED_SHA
    )
    require(
        clean_materialization_preserved or downstream_patch_preserved_clean_backup,
        "private copied BEA.exe hash mismatch",
        failures,
    )
    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(summary["profileName"] == PROFILE_ID, "private summary profile name mismatch", failures)
    require(summary["sourceCleanSha256"] == EXPECTED_SHA, "private source clean hash mismatch", failures)
    require(summary["sourceCurrentSha256"] == CURRENT_SHA, "private current hash mismatch", failures)
    require(summary["copiedExeSha256"] == EXPECTED_SHA, "private copied exe hash mismatch", failures)
    require(summary["copiedExeBytes"] == 2506752, "private copied exe byte count mismatch", failures)

    all_files = [
        path
        for path in PRIVATE_PROFILE_ROOT.rglob("*")
        if path.is_file()
        and path != PRIVATE_BACKUP
        and PATCH_PROOF_DIR not in path.parents
        and LAUNCH_COMMAND_PROOF_DIR not in path.parents
    ]
    payload_files = [path for path in all_files if not path.name.endswith(".private.json")]
    payload_bytes = sum(path.stat().st_size for path in payload_files)
    all_bytes = sum(path.stat().st_size for path in all_files)
    data_files = [path for path in (PRIVATE_PROFILE_ROOT / "data").rglob("*") if path.is_file()]
    savegame_root = PRIVATE_PROFILE_ROOT / "savegames"
    savegame_files = [path for path in savegame_root.rglob("*") if path.is_file()] if savegame_root.exists() else []

    require(len(payload_files) == 5479, "private payload file count mismatch", failures)
    require(payload_bytes == 696783748, "private payload byte count mismatch", failures)
    require(len(data_files) == 5464, "private data file count mismatch", failures)
    require(len(savegame_files) == 9, "private savegame file count mismatch", failures)
    require(len(all_files) == 5482, "private total file count mismatch", failures)
    require(all_bytes == 696793402, "private total byte count mismatch", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore materialization result mirror mismatch", failures)
    require(read_json(CLEAN_SOURCE_RESULT)["nextStaticSlice"] == "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan", "clean source result does not point to materialization lane", failures)
    require(read_json(PREFLIGHT_RESULT)["nextStaticSlice"] == PREVIOUS_SLICE, "preflight result does not point to clean source specimen lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["materializationStatus"] == "clean-copied-profile-created", "materializationStatus mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    profile = result["materializedProfile"]
    require(profile["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(profile["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(profile["privatePathIncluded"] is False, "private path flag mismatch", failures)
    require(profile["rawArtifactIncluded"] is False, "raw artifact flag mismatch", failures)
    require(profile["sourceExecutableClass"] == "canonical-clean-retail-backup-specimen", "source executable class mismatch", failures)
    require(profile["sourceResourceClass"] == "read-only-installed-game-resource-material", "source resource class mismatch", failures)
    require(profile["preparationHelper"] == "tools/prepare_game_profile.ps1", "preparation helper mismatch", failures)
    require(profile["executableOverrideUsed"] is True, "executable override flag mismatch", failures)
    require(profile["expectedCleanSha256"] == EXPECTED_SHA, "expected clean hash mismatch", failures)
    require(profile["copiedExecutableSha256"] == EXPECTED_SHA, "copied executable hash mismatch", failures)
    require(profile["copiedExecutableSha256Class"] == "matches-canonical-clean-retail", "copied hash class mismatch", failures)
    require(profile["copiedExecutableBytes"] == 2506752, "copied executable bytes mismatch", failures)
    require(profile["payloadFileCount"] == 5479, "payload file count mismatch", failures)
    require(profile["payloadTotalBytes"] == 696783748, "payload byte count mismatch", failures)
    require(profile["dataFileCount"] == 5464, "data file count mismatch", failures)
    require(profile["savegameFileCount"] == 9, "savegame file count mismatch", failures)
    require(profile["privateEvidenceFileCount"] == 3, "private evidence file count mismatch", failures)
    require(profile["localPrivateArtifactFileCount"] == 5482, "local private artifact file count mismatch", failures)
    require(profile["localPrivateArtifactTotalBytes"] == 696793402, "local private artifact byte count mismatch", failures)
    require(profile["prePatchState"] == "clean-unpatched", "pre-patch state mismatch", failures)
    require(profile["patchState"] == "not-run", "patch state mismatch", failures)

    summary = result["materializationSummary"]
    for key in ("materializationAttempted", "copiedProfileCreated", "copiedExecutableCreated", "copiedSpecimenHashChecked"):
        require(summary[key] is True, f"summary guard flag must be true: {key}", failures)
    for key in (
        "installedGameMutation",
        "originalExecutableMutation",
        "launchArmed",
        "beLaunch",
        "executablePatch",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(summary[key] is False, f"summary guard flag must be false: {key}", failures)
    require(summary["runtimeEvidenceRows"] == 0, "runtime evidence rows mismatch", failures)
    require(summary["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(summary["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    deferred = result["deferredPatchPlan"]
    require(deferred["nextPatchSlice"] == NEXT_SLICE, "next patch slice mismatch", failures)
    for patch_id in (
        "resolution_gate",
        "force_windowed",
        "version_overlay_use_patched_format_pointer",
        "version_overlay_patched_format_cave_string",
    ):
        require(patch_id in deferred["stablePatchIdsDeferred"], f"missing deferred patch id: {patch_id}", failures)
    require(deferred["experimentalPatchIdsNotArmed"] == ["skip_auto_toggle"], "experimental patch boundary mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore materialization plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore materialization result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof",
        "complete clean copied-profile materialization, not patch or runtime proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "materializationStatus=clean-copied-profile-created",
        f"profileId={PROFILE_ID}",
        "artifactRootClass=repo-local-ignored-private-evidence-root",
        "sourceExecutableClass=canonical-clean-retail-backup-specimen",
        "sourceResourceClass=read-only-installed-game-resource-material",
        "tools/prepare_game_profile.ps1",
        "Executable override used: `true`",
        EXPECTED_SHA,
        "matches-canonical-clean-retail",
        "copiedExecutableBytes=2506752",
        "payloadFileCount=5479",
        "payloadTotalBytes=696783748",
        "dataFileCount=5464",
        "savegameFileCount=9",
        "privateEvidenceFileCount=3",
        "localPrivateArtifactFileCount=5482",
        "localPrivateArtifactTotalBytes=696793402",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "beLaunch=false",
        "launchArmed=false",
        "executablePatch=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "runtimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
        "resolution_gate",
        "force_windowed",
        "version_overlay_use_patched_format_pointer",
        "version_overlay_patched_format_cave_string",
        "skip_auto_toggle",
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
        for token in (PLAN_LINK, RESULT_LINK, THIS_SLICE, NEXT_SLICE, PROFILE_ID, "clean-copied-profile-created", "matches-canonical-clean-retail", "payloadFileCount=5479"):
            require(token in text, f"{path.relative_to(ROOT)} missing materialization token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed materialization slice", failures)
    require(NEXT_SLICE in backlog, "backlog missing copied-executable patch follow-up slice", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan. Status: selected" not in backlog, "backlog still marks materialization as selected active", failures)


def check_package_and_helper(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_materialization_probe.py --check",
        "missing package copied-profile materialization test script",
        failures,
    )
    helper = read_text(PREPARE_HELPER)
    require("[string]$ExecutableOverridePath" in helper, "prepare helper missing executable override parameter", failures)
    require("executableOverride = [bool]$executableSource" in helper, "prepare helper missing executable override report field", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_private_evidence(failures)
    check_result(failures)
    check_docs(failures)
    check_package_and_helper(failures)

    if failures:
        print("MissionScript Level100 copied-profile materialization probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile materialization probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
