#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile launch-command proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"
PATCH_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_launch_command_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"
LAUNCH_HELPER = ROOT / "tools" / "start_game_profile.ps1"

PROFILE_ID = "level100-clean-materialized-20260608-214752"
PRIVATE_PROFILE_ROOT = ROOT / "subagents" / "static-to-proof" / "level100-copied-profile-materialization" / PROFILE_ID
PRIVATE_EXE = PRIVATE_PROFILE_ROOT / "BEA.exe"
PRIVATE_BACKUP = PRIVATE_PROFILE_ROOT / "BEA.exe.original.backup"
LAUNCH_PROOF_DIR = PRIVATE_PROFILE_ROOT / "launch-command-proof.private"
PRIVATE_MANIFEST = LAUNCH_PROOF_DIR / "launch-command-manifest.private.json"
PRIVATE_SUMMARY = LAUNCH_PROOF_DIR / "launch-command-summary.private.json"

EXPECTED_CLEAN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PATCHED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan"
DIRECT_LEVEL100_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan"
FOLLOW_UP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan"
VISUAL_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan"
TEXT_OVERLAY_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan"
TIMED_FRAME_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan"
TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"

COMMAND_ROWS = [
    (
        "baseline-copied-profile-launch",
        [],
        "ready-unarmed",
        'Start-Process -FilePath "<COPIED_PROFILE>\\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>"',
    ),
    (
        "skip-fmv-copied-profile-launch",
        ["-skipfmv"],
        "ready-unarmed",
        'Start-Process -FilePath "<COPIED_PROFILE>\\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv"',
    ),
    (
        "direct-level100-candidate",
        ["-skipfmv", "-level", "100"],
        "candidate-unproven-unarmed",
        'Start-Process -FilePath "<COPIED_PROFILE>\\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv -level 100"',
    ),
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
    "launch behavior proven",
    "process started",
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


def run_print_only(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    argument_string = " ".join(arguments)
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCH_HELPER),
            "-GameRoot",
            str(PRIVATE_PROFILE_ROOT),
            "-Arguments",
            argument_string,
            "-PrintOnly",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def sanitized_preview(output: str) -> str:
    private = str(PRIVATE_PROFILE_ROOT)
    return output.strip().replace(private, "<COPIED_PROFILE>")


def command_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in rows}


def check_private_evidence(failures: list[str]) -> None:
    require(PRIVATE_EXE.is_file(), "private copied BEA.exe missing", failures)
    require(PRIVATE_BACKUP.is_file(), "private clean backup missing", failures)
    require(LAUNCH_PROOF_DIR.is_dir(), "private launch proof dir missing", failures)
    require(PRIVATE_MANIFEST.is_file(), "private launch manifest missing", failures)
    require(PRIVATE_SUMMARY.is_file(), "private launch summary missing", failures)
    require(PRIVATE_EXE.stat().st_size == 2506752, "private copied BEA.exe byte size mismatch", failures)
    require(PRIVATE_BACKUP.stat().st_size == 2506752, "private clean backup byte size mismatch", failures)
    require(sha256(PRIVATE_EXE) == PATCHED_SHA, "private copied BEA.exe patched hash mismatch", failures)
    require(sha256(PRIVATE_BACKUP) == EXPECTED_CLEAN_SHA, "private backup clean hash mismatch", failures)

    manifest = read_json(PRIVATE_MANIFEST)
    summary = read_json(PRIVATE_SUMMARY)
    require(manifest["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.private.v1", "private schema mismatch", failures)
    require(manifest["status"] == "READY_UNARMED", "private manifest status mismatch", failures)
    require(summary["status"] == "READY_UNARMED", "private summary status mismatch", failures)
    require(manifest["profileId"] == PROFILE_ID, "private manifest profile mismatch", failures)
    require(summary["profileId"] == PROFILE_ID, "private summary profile mismatch", failures)
    require(Path(manifest["profileRoot"]) == PRIVATE_PROFILE_ROOT, "private manifest profile root mismatch", failures)
    require(Path(manifest["executablePath"]) == PRIVATE_EXE, "private manifest executable mismatch", failures)
    require(Path(manifest["workingDirectory"]) == PRIVATE_PROFILE_ROOT, "private manifest working directory mismatch", failures)
    require(manifest["targetHash"] == PATCHED_SHA, "private manifest target hash mismatch", failures)
    require(manifest["backupHash"] == EXPECTED_CLEAN_SHA, "private manifest backup hash mismatch", failures)
    require(manifest["targetBytes"] == 2506752, "private manifest target bytes mismatch", failures)
    require(manifest["backupBytes"] == 2506752, "private manifest backup bytes mismatch", failures)
    require(manifest["beProcessesBefore"] == 0, "private manifest BEA process precheck mismatch", failures)
    require(summary["beProcessesBefore"] == 0, "private summary BEA process precheck mismatch", failures)

    for key in (
        "installedGameMutation",
        "originalExecutableMutation",
        "processStartAttempted",
        "beLaunch",
        "launchArmed",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(manifest[key] is False, f"private manifest flag must be false: {key}", failures)
    require(manifest["runtimeEvidenceRows"] == 0, "private manifest runtime rows mismatch", failures)

    required = {entry["name"]: entry for entry in manifest["requiredEntries"]}
    for name in ("data", "defaultoptions.bea", "savegames", "binkw32.dll", "ogg.dll", "vorbis.dll", "zlib.dll"):
        require(required.get(name, {}).get("exists") is True, f"private manifest missing required copied entry: {name}", failures)

    planned = command_by_id(manifest["plannedCommandClasses"])
    require(set(planned) == {row[0] for row in COMMAND_ROWS}, "private command class id mismatch", failures)
    for command_id, arguments, status, public_preview in COMMAND_ROWS:
        row = planned[command_id]
        require(row["arguments"] == arguments, f"private arguments mismatch: {command_id}", failures)
        require(row["status"] == status, f"private status mismatch: {command_id}", failures)
        require(row["publicPreview"] == public_preview, f"private public preview mismatch: {command_id}", failures)

    require(manifest["selectedInitialRoute"] == "skip-fmv-copied-profile-launch", "private selected route mismatch", failures)
    require(manifest["directLevel100Route"] == "direct-level100-candidate", "private direct Level100 route mismatch", failures)
    require(manifest["nextRuntimeProofMustChooseRoute"] is True, "private route choice gate mismatch", failures)
    require(manifest["nextRuntimeProofMustExplicitlyArmLaunch"] is True, "private launch arm gate mismatch", failures)
    require(manifest["launchHelper"] == "tools/start_game_profile.ps1", "private launch helper mismatch", failures)
    require(manifest["launchHelperMode"] == "PrintOnly", "private helper mode mismatch", failures)
    require(manifest["launchCommandExecuted"] is False, "private launch command executed mismatch", failures)
    require(manifest["processStarted"] is False, "private process started mismatch", failures)
    require(manifest["stopBeforeCreateProcess"] is True, "private stop-before-create-process mismatch", failures)
    require(manifest["launchArmGateSpecified"] is True, "private launch arm gate specified mismatch", failures)
    require(manifest["invalidArgumentProbe"]["arguments"] == ["-devmode"], "private invalid argument vector mismatch", failures)
    require(manifest["invalidArgumentProbe"]["exitCode"] != 0, "private invalid argument exit mismatch", failures)
    require(manifest["invalidArgumentProbe"]["rejected"] is True, "private invalid argument rejection mismatch", failures)
    require(manifest["invalidArgumentProbe"]["messageClass"] == "Unsupported launch argument", "private invalid argument message mismatch", failures)


def check_helper_print_only(failures: list[str]) -> None:
    for command_id, arguments, _status, public_preview in COMMAND_ROWS:
        result = run_print_only(arguments)
        require(result.returncode == 0, f"PrintOnly helper failed for {command_id}: {result.stderr}", failures)
        require("game-launch-process.v1" not in result.stdout, f"PrintOnly helper emitted process JSON for {command_id}", failures)
        require(sanitized_preview(result.stdout) == public_preview, f"PrintOnly preview mismatch for {command_id}", failures)

    invalid = run_print_only(["-devmode"])
    require(invalid.returncode != 0, "invalid -devmode probe unexpectedly succeeded", failures)
    require("Unsupported launch argument" in invalid.stderr, "invalid -devmode probe missing rejection message", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore launch-command result mirror mismatch", failures)
    require(read_json(PATCH_RESULT)["nextStaticSlice"] == THIS_SLICE, "copied-executable patch result does not point to launch-command lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "COMPLETE", "status mismatch", failures)
    require(result["launchCommandStatus"] == "ready-unarmed-command-proof", "launchCommandStatus mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    proof = result["launchCommandProof"]
    require(proof["profileId"] == PROFILE_ID, "profile id mismatch", failures)
    require(proof["artifactRootClass"] == "repo-local-ignored-private-evidence-root", "artifact root class mismatch", failures)
    require(proof["targetExecutableClass"] == "copied-profile-BEA.exe", "target executable class mismatch", failures)
    require(proof["workingDirectoryClass"] == "copied-profile-root", "working directory class mismatch", failures)
    require(proof["privatePathIncluded"] is False, "private path flag mismatch", failures)
    require(proof["rawArtifactIncluded"] is False, "raw artifact flag mismatch", failures)
    require(proof["targetHash"] == PATCHED_SHA, "target hash mismatch", failures)
    require(proof["backupHash"] == EXPECTED_CLEAN_SHA, "backup hash mismatch", failures)
    require(proof["targetBytes"] == 2506752, "target byte count mismatch", failures)
    require(proof["backupBytes"] == 2506752, "backup byte count mismatch", failures)
    require(proof["patchStatus"] == "stable-copied-executable-patched", "patch status mismatch", failures)
    require(proof["stablePatchRows"] == 4, "stable patch row count mismatch", failures)
    require(proof["skipAutoToggleArmed"] is False, "skip auto toggle mismatch", failures)
    require(proof["commandClassCount"] == 3, "command class count mismatch", failures)
    require(proof["selectedInitialRoute"] == "skip-fmv-copied-profile-launch", "selected initial route mismatch", failures)
    require(proof["directLevel100Route"] == "direct-level100-candidate", "direct Level100 route mismatch", failures)
    require(proof["directLevel100RouteStatus"] == "candidate-unproven-unarmed", "direct Level100 route status mismatch", failures)
    require(proof["launchHelper"] == "tools/start_game_profile.ps1", "launch helper mismatch", failures)
    require(proof["launchHelperMode"] == "PrintOnly", "launch helper mode mismatch", failures)
    require(proof["beProcessesBefore"] == 0, "BEA process precheck mismatch", failures)
    require(proof["launchArmGateSpecified"] is True, "launch arm gate mismatch", failures)
    require(proof["invalidArgumentRejected"] is True, "invalid argument rejected mismatch", failures)
    require(proof["launchCommandExecuted"] is False, "launchCommandExecuted mismatch", failures)
    require(proof["processStarted"] is False, "processStarted mismatch", failures)
    require(proof["stopBeforeCreateProcess"] is True, "stopBeforeCreateProcess mismatch", failures)

    rows = command_by_id(result["commandClasses"])
    require(set(rows) == {row[0] for row in COMMAND_ROWS}, "result command ids mismatch", failures)
    for command_id, arguments, status, public_preview in COMMAND_ROWS:
        row = rows.get(command_id)
        require(row is not None, f"missing result command row: {command_id}", failures)
        if row is not None:
            require(row["arguments"] == arguments, f"result arguments mismatch: {command_id}", failures)
            require(row["status"] == status, f"result status mismatch: {command_id}", failures)
            require(row["publicPreview"] == public_preview, f"result public preview mismatch: {command_id}", failures)

    guard = result["guardSummary"]
    require(guard["launchCommandProof"] is True, "launchCommandProof guard mismatch", failures)
    require(guard["copiedExecutablePatch"] is True, "copiedExecutablePatch guard mismatch", failures)
    for key in (
        "installedGameMutation",
        "originalExecutableMutation",
        "beLaunch",
        "launchArmed",
        "launchCommandExecuted",
        "processStarted",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(guard[key] is False, f"guard flag must be false: {key}", failures)
    require(guard["stopBeforeCreateProcess"] is True, "stopBeforeCreateProcess guard mismatch", failures)
    require(guard["runtimeEvidenceRows"] == 0, "runtime evidence rows mismatch", failures)
    require(guard["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(guard["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore launch-command plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore launch-command result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan",
        "complete launch-command proof, not BEA launch or runtime proof",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        "status=COMPLETE",
        "launchCommandStatus=ready-unarmed-command-proof",
        f"profileId={PROFILE_ID}",
        "artifactRootClass=repo-local-ignored-private-evidence-root",
        "targetExecutableClass=copied-profile-BEA.exe",
        "workingDirectoryClass=copied-profile-root",
        "launchHelper=tools/start_game_profile.ps1",
        "launchHelperMode=PrintOnly",
        "commandClassCount=3",
        "selectedInitialRoute=skip-fmv-copied-profile-launch",
        "directLevel100Route=direct-level100-candidate",
        "directLevel100RouteStatus=candidate-unproven-unarmed",
        "patchStatus=stable-copied-executable-patched",
        "stablePatchRows=4",
        "skipAutoToggleArmed=false",
        f"targetHash={PATCHED_SHA}",
        f"backupHash={EXPECTED_CLEAN_SHA}",
        "targetBytes=2506752",
        "backupBytes=2506752",
        "beProcessesBefore=0",
        "invalidArgumentRejected=true",
        "baseline-copied-profile-launch",
        "skip-fmv-copied-profile-launch",
        "direct-level100-candidate",
        "ready-unarmed",
        "candidate-unproven-unarmed",
        "-skipfmv",
        "-level",
        "100",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "beLaunch=false",
        "launchArmed=false",
        "launchCommandExecuted=false",
        "processStarted=false",
        "stopBeforeCreateProcess=true",
        "launchArmGateSpecified=true",
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

    front_door_tokens = (
        PLAN_LINK,
        RESULT_LINK,
        THIS_SLICE,
        NEXT_SLICE,
        PROFILE_ID,
        "ready-unarmed-command-proof",
        "commandClassCount=3",
        "selectedInitialRoute=skip-fmv-copied-profile-launch",
        "directLevel100Route=direct-level100-candidate",
        "directLevel100RouteStatus=candidate-unproven-unarmed",
        "launchHelperMode=PrintOnly",
        "launchCommandExecuted=false",
        "processStarted=false",
        "stopBeforeCreateProcess=true",
        "launchArmGateSpecified=true",
        "invalidArgumentRejected=true",
        "copied-profile-window-smoke-complete",
        "copied-profile-window-still-frame-captured",
        DIRECT_LEVEL100_SLICE,
        FOLLOW_UP_SLICE,
        VISUAL_FRAME_SLICE,
        TEXT_OVERLAY_SLICE,
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing launch-command token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed launch-command slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed launch-window smoke slice", failures)
    require(
        "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan" in backlog,
        "backlog missing completed screenshot capture slice",
        failures,
    )
    require(f"Completed {DIRECT_LEVEL100_SLICE}" in backlog, "backlog missing completed direct Level100 launch smoke slice", failures)
    require(f"Completed {FOLLOW_UP_SLICE}" in backlog, "backlog missing completed direct Level100 screenshot slice", failures)
    require(f"Completed {VISUAL_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 visual frame triage slice", failures)
    require(f"Completed {TEXT_OVERLAY_SLICE}" in backlog, "backlog missing completed direct Level100 text overlay correlation slice", failures)
    require(f"Completed {TIMED_FRAME_SLICE}" in backlog, "backlog missing completed direct Level100 timed-frame set slice", failures)
    require(f"The selected active static-to-proof slice is {TIMED_FRAME_TEXT_OVERLAY_PROGRESSION_SLICE}" in backlog, "backlog missing active direct Level100 timed-frame text-overlay progression slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks launch-command proof as selected active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_launch_command_probe.py --check",
        "missing package launch-command test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_private_evidence(failures)
    check_helper_print_only(failures)
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 launch-command probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 launch-command probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
