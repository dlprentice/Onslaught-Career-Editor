#!/usr/bin/env python3
"""Tests for the music source-file safety sidecar producer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import winui_safe_copy_music_source_music_safety_sidecar as producer


TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_source_music(root: Path, *, target_bytes: bytes = b"target-v1", replacement_bytes: bytes = b"replacement-v1") -> None:
    music = root / "data" / "Music"
    music.mkdir(parents=True, exist_ok=True)
    (music / TARGET).write_bytes(target_bytes)
    (music / REPLACEMENT).write_bytes(replacement_bytes)


def live_payload(*, mute: bool = False) -> dict[str, Any]:
    args = ["-skipfmv", "-level", "100"]
    if mute:
        args.append("-nomusic")
    return {
        "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {"patchKeys": ["resolution_gate", "force_windowed"]},
        "musicReplacement": None,
        "launch": {"arguments": args},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
    }


class MusicSourceSafetySidecarTests(unittest.TestCase):
    def test_builds_sidecar_from_before_snapshot_and_current_source_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-source-safety-") as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            write_source_music(source_root)
            live_path = write_json(root / "clean" / "live.json", live_payload())
            before_path = root / "before.json"
            sidecar_path = root / "clean" / "source-music-safety.json"

            producer.write_json(before_path, producer.build_snapshot(source_root=source_root))
            sidecar = producer.build_sidecar_from_paths(
                live_path=live_path,
                before_snapshot=before_path,
                source_root=source_root,
                output=sidecar_path,
                role="cleanBaseline",
            )

            summary = producer.validate_artifact(sidecar, artifact_path=sidecar_path, live_path=live_path)
            self.assertEqual("winui-safe-copy-source-music-safety.v1", sidecar["schemaVersion"])
            self.assertEqual("cleanBaseline", summary["role"])
            self.assertTrue(summary["sourceTargetHashUnchanged"])
            self.assertTrue(summary["sourceReplacementHashUnchanged"])
            self.assertTrue(sidecar_path.is_file())
            rendered = json.dumps(sidecar)
            self.assertNotIn(str(source_root), rendered)
            self.assertNotIn("sourceRoot", rendered)

    def test_rejects_source_mutation_after_before_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-source-safety-") as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            write_source_music(source_root)
            live_path = write_json(root / "clean" / "live.json", live_payload())
            before_path = root / "before.json"
            producer.write_json(before_path, producer.build_snapshot(source_root=source_root))
            (source_root / "data" / "Music" / TARGET).write_bytes(b"target-v2")

            with self.assertRaises(producer.SourceMusicSafetyError):
                producer.build_sidecar_from_paths(
                    live_path=live_path,
                    before_snapshot=before_path,
                    source_root=source_root,
                    output=root / "clean" / "source-music-safety.json",
                    role="cleanBaseline",
                )

    def test_rejects_mute_sidecar_without_mute_launch_argument(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-source-safety-") as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            write_source_music(source_root)
            live_path = write_json(root / "mute" / "live.json", live_payload(mute=False))
            before_path = root / "before.json"
            producer.write_json(before_path, producer.build_snapshot(source_root=source_root))

            with self.assertRaises(producer.SourceMusicSafetyError):
                producer.build_sidecar_from_paths(
                    live_path=live_path,
                    before_snapshot=before_path,
                    source_root=source_root,
                    output=root / "mute" / "source-music-safety.json",
                    role="muteControl",
                )

    def test_rejects_output_inside_source_game_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="music-source-safety-") as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            write_source_music(source_root)
            live_path = write_json(root / "clean" / "live.json", live_payload())
            before_path = root / "before.json"
            producer.write_json(before_path, producer.build_snapshot(source_root=source_root))

            with self.assertRaises(producer.SourceMusicSafetyError):
                producer.build_sidecar_from_paths(
                    live_path=live_path,
                    before_snapshot=before_path,
                    source_root=source_root,
                    output=source_root / "data" / "Music" / "source-music-safety.json",
                    role="cleanBaseline",
                )

    def test_cli_self_test_passes(self) -> None:
        result = producer.run_self_test()
        self.assertEqual(
            {
                "schemaVersion": "winui-safe-copy-source-music-safety.v1",
                "rolesChecked": ["cleanBaseline", "muteControl"],
                "sourceTargetHashUnchanged": True,
                "sourceReplacementHashUnchanged": True,
            },
            result,
        )


if __name__ == "__main__":
    unittest.main()
