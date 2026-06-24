#!/usr/bin/env python3
"""Build a fail-closed plan for the music audible-output two-run harness.

This script does not launch BEA or capture audio. It emits the public-safe
command contract for the next private live attempt.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-safe-copy-music-audible-output-two-run-plan.v1"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
LIVE_ARM = "LAUNCH SAFE COPY BEA"
CDB_ARM = "ATTACH CDB TO SAFE COPY BEA"
AUDIO_ARM = "CAPTURE LOOPBACK AUDIO"
DEFAULT_SOURCE_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")


class HarnessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HarnessError(message)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def loopback_command(stage_root: Path, role: str) -> list[str]:
    audio_root = stage_root / "audio"
    return [
        "py",
        "-3",
        r"tools\capture_audio_loopback.py",
        "--capture",
        "--allowed-output-root",
        rel(audio_root),
        "--output-wav",
        rel(audio_root / f"{role}.wav"),
        "--output-json",
        rel(audio_root / f"{role}.json"),
        "--duration-ms",
        "3000",
        "--arm-capture-audio",
        AUDIO_ARM,
    ]


def live_smoke_command(stage_root: Path, role: str, *, source_root: Path, staged: bool, mute: bool = False) -> list[str]:
    command = [
        "py",
        "-3",
        r"tools\winui_safe_copy_live_runtime_smoke.py",
        "--source-root",
        str(source_root),
        "--artifact-root",
        rel(stage_root / "live"),
        "--level-id",
        str(LEVEL_ID),
        "--capture-count",
        "2",
        "--enable-cdb-observer",
        "--arm-cdb-observer",
        CDB_ARM,
        "--cdb-command-file",
        r"tools\runtime-probes\safe-copy-music-selection-decode-observer.cdb.txt",
        "--arm-live-bea",
        LIVE_ARM,
    ]
    if staged:
        command.extend(["--stage-music-replacement", "--music-swap-preset-id", PRESET_ID])
    if mute:
        command.append("--launch-nomusic")
    _ = role
    return command


def stage(stage_root: Path, role: str, *, source_root: Path, staged: bool = False, mute: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "role": role,
        "artifactRoot": rel(stage_root),
        "audioCommand": loopback_command(stage_root, role),
        "ordering": "start audioCommand before liveSmokeCommand and stop/check after liveSmokeCommand exits",
        "noCalibrationTone": True,
        "expectedAudioSchema": "audio-loopback-capture.v1",
    }
    if role != "ambientNoBea":
        payload["liveSmokeCommand"] = live_smoke_command(stage_root, role, source_root=source_root, staged=staged, mute=mute)
        payload["expectedCdbCommandFile"] = r"tools\runtime-probes\safe-copy-music-selection-decode-observer.cdb.txt"
    else:
        payload["liveSmokeCommand"] = None
        payload["expectedCdbCommandFile"] = None
    return payload


def build_plan(artifact_root: Path, *, source_root: Path = DEFAULT_SOURCE_ROOT) -> dict[str, Any]:
    artifact_root = artifact_root.resolve()
    stages_root = artifact_root / "stages"
    return {
        "schemaVersion": SCHEMA,
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "runtimeAudibleOutputProof": False,
        "stages": [
            stage(stages_root / "ambient-no-bea", "ambientNoBea", source_root=source_root),
            stage(stages_root / "clean-baseline", "cleanBaseline", source_root=source_root),
            stage(stages_root / "staged-positive", "stagedPositive", source_root=source_root, staged=True),
            stage(stages_root / "mute-control", "muteControl", source_root=source_root, mute=True),
        ],
        "acceptedProofMaterializer": r"tools\winui_safe_copy_music_audible_output_materializer.py",
        "acceptedProofShapeChecker": r"tools\winui_safe_copy_music_audible_output_two_run_harness_check.py",
        "blockedUntil": [
            "live raw artifacts exist and pass the materializer plus final checker",
            "live capture-to-source correlation adapter artifact exists and passes the adapter checker",
            "mute-control runtime path is captured with -nomusic or -nosound",
        ],
        "claimBoundary": (
            "Plan only. It is not a BEA launch, CDB attach, audio capture, audible playback proof, "
            "source-audio correlation proof, all-cue proof, gameplay parity proof, or rebuild parity proof."
        ),
    }


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    require(plan.get("schemaVersion") == SCHEMA, "plan schema changed")
    require(plan.get("runtimeAudibleOutputProof") is False, "plan must not claim audible output proof")
    require(plan.get("presetId") == PRESET_ID, "plan preset changed")
    stages = plan.get("stages")
    require(isinstance(stages, list), "plan stages must be a list")
    roles = [stage.get("role") for stage in stages if isinstance(stage, dict)]
    require(roles == ["ambientNoBea", "cleanBaseline", "stagedPositive", "muteControl"], "plan stages changed")
    for item in stages:
        require(isinstance(item, dict), "stage must be an object")
        require(item.get("noCalibrationTone") is True, f"{item.get('role')} must not use calibration tone")
        audio_command = item.get("audioCommand")
        require(isinstance(audio_command, list), f"{item.get('role')} missing audio command")
        require("--play-calibration-tone" not in " ".join(str(part) for part in audio_command), "calibration tone is not allowed in proof plan")
    blockers = plan.get("blockedUntil")
    require(isinstance(blockers, list) and len(blockers) >= 3, "plan blockers missing")
    require(
        plan.get("acceptedProofMaterializer") == r"tools\winui_safe_copy_music_audible_output_materializer.py",
        "plan must route proof promotion through the raw materializer",
    )
    require(
        plan.get("acceptedProofShapeChecker") == r"tools\winui_safe_copy_music_audible_output_two_run_harness_check.py",
        "plan must keep the final shape checker as post-materializer validation",
    )
    return {
        "schema": SCHEMA,
        "stageCount": len(stages),
        "runtimeAudibleOutputProof": False,
        "blockedUntil": blockers,
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plan = build_plan(Path(temp_dir) / "music-audible")
        validate_plan(plan)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", default="", help="Root to reference in the emitted plan.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--output-json", default="", help="Optional plan JSON output path.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music audible-output two-run harness plan self-test: PASS")
            return 0
        require(args.artifact_root, "Provide --artifact-root or --self-test.")
        plan = build_plan(Path(args.artifact_root), source_root=Path(args.source_root))
        validate_plan(plan)
        text = json.dumps(plan, indent=2, sort_keys=True)
        if args.output_json:
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    except HarnessError as exc:
        print(f"WinUI safe-copy music audible-output two-run harness plan: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
