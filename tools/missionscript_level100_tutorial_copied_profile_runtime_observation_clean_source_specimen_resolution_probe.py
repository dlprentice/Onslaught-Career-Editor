#!/usr/bin/env python3
"""Validate the MissionScript Level100 clean source specimen resolution proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"
PREFLIGHT_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_clean_source_specimen_resolution_proof_plan_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
CURRENT_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"

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
    "copied profile exists proven",
    "copied executable exists proven",
    "copied specimen hash checked proven",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore clean source specimen result mirror mismatch", failures)
    require(read_json(PREFLIGHT_RESULT)["nextStaticSlice"] == THIS_SLICE, "preflight result does not point to clean source specimen resolution lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["resolutionStatus"] == "clean-backup-specimen-verified", "resolutionStatus mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    specimen = result["specimenResolution"]
    require(specimen["expectedCleanSha256"] == EXPECTED_SHA, "expected clean hash mismatch", failures)
    require(specimen["cleanBackupSha256"] == EXPECTED_SHA, "clean backup hash mismatch", failures)
    require(specimen["cleanBackupSize"] == 2506752, "clean backup size mismatch", failures)
    require(specimen["cleanBackupMatchesExpected"] is True, "clean backup match flag mismatch", failures)
    require(specimen["cleanBackupAuthorityClass"] == "canonical-clean-retail-match", "clean backup authority class mismatch", failures)
    require(specimen["currentSpecimenSha256"] == CURRENT_SHA, "current specimen hash mismatch", failures)
    require(specimen["currentSpecimenSize"] == 2506752, "current specimen size mismatch", failures)
    require(specimen["currentSpecimenClass"] == "known-stable-patch-catalog-deltas-from-clean", "current specimen class mismatch", failures)
    require(specimen["sameLength"] is True, "sameLength mismatch", failures)
    require(specimen["byteDiffCount"] == 28, "byte diff count mismatch", failures)
    require(specimen["unknownDiffCount"] == 0, "unknown diff count mismatch", failures)
    require(specimen["publicPathPolicy"] == "no-local-path-in-public-evidence", "public path policy mismatch", failures)

    rows = {row["patchId"]: row for row in result["patchCatalogDeltaRows"]}
    expected_rows = {
        "resolution_gate": ("0x129696", "CC", "00", "patched"),
        "force_windowed": ("0x12A644", "A1 F0 2D 66 00", "B8 01 00 00 00", "patched"),
        "version_overlay_use_patched_format_pointer": ("0x06416F", "54 94 62 00", "44 A4 5A 00", "patched"),
        "version_overlay_patched_format_cave_string": ("0x1AA444", "CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC", "56 25 31 64 2E 25 30 32 64 20 2D 20 50 41 54 43 48 45 44 00", "patched"),
        "skip_auto_toggle": ("0x12BB97", "75 20", "75 20", "original"),
    }
    require(set(rows) == set(expected_rows), "patch delta row ids mismatch", failures)
    for patch_id, (offset, clean, current, state) in expected_rows.items():
        row = rows.get(patch_id, {})
        require(row.get("fileOffset") == offset, f"offset mismatch for {patch_id}", failures)
        require(row.get("cleanBytes") == clean, f"clean bytes mismatch for {patch_id}", failures)
        require(row.get("currentBytes") == current, f"current bytes mismatch for {patch_id}", failures)
        require(row.get("state") == state, f"state mismatch for {patch_id}", failures)

    summary = result["materializationSummary"]
    for key in (
        "materializationAttempted",
        "copiedProfileCreated",
        "copiedExecutableCreated",
        "copiedSpecimenHashChecked",
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
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore clean source specimen plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore clean source specimen result mirror mismatch", failures)

    core_tokens = (
        THIS_SLICE,
        "complete source-specimen authority resolution before copied-profile materialization",
        PLAN_LINK,
        RESULT_LINK,
        "status=COMPLETE",
        "resolutionStatus=clean-backup-specimen-verified",
        EXPECTED_SHA,
        CURRENT_SHA,
        "cleanBackupMatchesExpected=true",
        "cleanBackupAuthorityClass=canonical-clean-retail-match",
        "currentSpecimenClass=known-stable-patch-catalog-deltas-from-clean",
        "sameLength=true",
        "byteDiffCount=28",
        "unknownDiffCount=0",
        "resolution_gate",
        "force_windowed",
        "version_overlay_use_patched_format_pointer",
        "version_overlay_patched_format_cave_string",
        "skip_auto_toggle",
        "0x129696",
        "0x12A644",
        "0x06416F",
        "0x1AA444",
        "0x12BB97",
        "materializationAttempted=false",
        "copiedProfileCreated=false",
        "copiedExecutableCreated=false",
        "copiedSpecimenHashChecked=false",
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
        for token in (PLAN_LINK, RESULT_LINK, THIS_SLICE, NEXT_SLICE, "clean-backup-specimen-verified", "known-stable-patch-catalog-deltas-from-clean"):
            require(token in text, f"{path.relative_to(ROOT)} missing clean source specimen token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed clean source specimen slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed materialization slice", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog, "backlog missing active copied-executable patch slice", failures)
    require("Clean Source Specimen Resolution Proof Plan. Status: selected" not in backlog, "backlog still marks clean source specimen resolution as active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_clean_source_specimen_resolution_probe.py --check",
        "missing package clean source specimen resolution test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 clean source specimen resolution probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 clean source specimen resolution probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
