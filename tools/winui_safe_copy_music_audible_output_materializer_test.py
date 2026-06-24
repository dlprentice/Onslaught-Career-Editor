#!/usr/bin/env python3
"""Tests for trusted music audible-output proof materialization."""

from __future__ import annotations

import copy
import hashlib
import json
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_materializer as materializer
import winui_safe_copy_music_audible_output_two_run_harness_check as final_check
import winui_safe_copy_music_capture_source_correlation_check as capture_correlation


TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SELECTION_ID = 2


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def log_text() -> str:
    return "\n".join(
        [
            "2026-06-22T00:00:01.100Z CGame__PlayMusicForCurrentLevel this=008a9a98 level=100 raw=00000064",
            "2026-06-22T00:00:01.200Z CMusic__PlaySelection entry this=00889a48 caller=0046dc2c globalGame=008a9a98 globalLevel=100 globalRaw=00000064 selection=2 fade=0 playing=0 head=04400000 current=00000000",
            r"2026-06-22T00:00:01.300Z CMusic__PlaySelectionResolved this=00889a48 selection=2 selected=04400300 path=data\music\BEA_04(Master).ogg playing=0 fadeArg=0 current=00000000 pending=00000000 mode=0",
            r"2026-06-22T00:00:01.400Z PCPlatform__KickAsyncMusicStreamRead path=data\music\BEA_04(Master).ogg",
            r"2026-06-22T00:00:01.500Z COggFileRead__OpenFileAndPrimeDecoder this=0440a000 path=data\music\BEA_04(Master).ogg",
            "2026-06-22T00:00:01.600Z COggFileRead__ReadDecodedPcm this=0440a000 request=4096 out=04500000 outBytes=0019f4b0",
        ]
    )


def restart_loop_direct_log_text() -> str:
    return "\n".join(
        [
            "2026-06-22T00:00:01.200Z CMusic__PlaySelection entry this=00889a48 caller=0046e0bf globalGame=008a9a98 globalLevel=100 globalRaw=00000064 selection=2 fade=0 playing=0 head=04400000 current=00000000",
            r"2026-06-22T00:00:01.300Z CMusic__PlaySelectionResolved this=00889a48 selection=2 selected=04400300 path=data\music\BEA_04(Master).ogg playing=0 fadeArg=0 current=00000000 pending=00000000 mode=0",
            r"2026-06-22T00:00:01.400Z PCPlatform__KickAsyncMusicStreamRead path=data\music\BEA_04(Master).ogg",
            r"2026-06-22T00:00:01.500Z COggFileRead__OpenFileAndPrimeDecoder this=0440a000 path=data\music\BEA_04(Master).ogg",
            "2026-06-22T00:00:01.600Z COggFileRead__ReadDecodedPcm this=0440a000 request=4096 out=04500000 outBytes=0019f4b0",
        ]
    )


def untimestamped_log_text() -> str:
    return "\n".join(line.split(" ", 1)[1] for line in log_text().splitlines())


def live_payload(log_path: Path, *, role: str, staged: bool, mute: bool = False) -> dict[str, Any]:
    launch_args = ["-skipfmv", "-level", str(LEVEL_ID)]
    if mute:
        launch_args.append("-nomusic")
    payload: dict[str, Any] = {
        "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
        "source": {
            "sourceRoot": r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila",
            "installedHashBefore": "1" * 64,
            "installedHashAfter": "1" * 64,
            "installedHashUnchanged": True,
            "overrideHashBefore": "2" * 64,
            "overrideHashAfter": "2" * 64,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {
            "TargetGameRoot": r"G:\OnslaughtRuntimeProofArchive\sample\profile",
            "patchKeys": ["resolution_gate", "force_windowed"],
        },
        "musicReplacement": None,
        "launch": {
            "processId": 4242,
            "observedAlive": True,
            "arguments": launch_args,
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "cdbObserver": {
            "enabled": True,
            "commandFile": r"tools\runtime-probes\safe-copy-music-selection-decode-observer.cdb.txt",
            "logPath": str(log_path),
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
            "cleanup": {"status": "stopped"},
        },
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "stop": {"Success": True},
        "claimBoundary": "Optional music replacement does not prove audible playback.",
        "testRole": role,
    }
    if staged:
        payload["musicReplacement"] = {
            "SchemaVersion": "winui-safe-copy-music-replacement.v1",
            "MusicSwapPresetId": "use-bea02-for-bea04",
            "TargetMusicFileName": TARGET,
            "TargetRelativePath": r"data\Music\BEA_04(Master).ogg",
            "SourceTargetFileName": TARGET,
            "SourceTargetHashBefore": "3" * 64,
            "SourceTargetHashAfter": "3" * 64,
            "SourceTargetHashUnchanged": True,
            "SourceReplacementFileName": REPLACEMENT,
            "SourceReplacementHashBefore": "4" * 64,
            "SourceReplacementHashAfter": "4" * 64,
            "SourceReplacementHashUnchanged": True,
            "OriginalSha256": "a" * 64,
            "ReplacementSha256": "b" * 64,
            "targetNowMatchesReplacement": True,
            "backupMatchesOriginal": True,
        }
    return payload


def audio_payload(
    *,
    output_wav: Path,
    output_json: Path,
    start: str,
    end: str,
    stats: dict[str, Any],
    non_silent: bool,
    endpoint_id: str = "endpoint-1",
) -> dict[str, Any]:
    wav_size = output_wav.stat().st_size
    return {
        "schemaVersion": "audio-loopback-capture.v1",
        "status": "captured",
        "captureKind": "wasapi-loopback",
        "captureStartedUtc": start,
        "captureEndedUtc": end,
        "outputWav": str(output_wav),
        "outputJson": str(output_json),
        "rawWavSha256": sha256_file(output_wav),
        "requestedDurationMs": 3000,
        "observedDurationMs": 3000,
        "device": {
            "friendlyName": "Speakers (Private Device)",
            "id": endpoint_id,
            "dataFlow": "render",
            "role": "multimedia",
        },
        "calibration": {"played": False},
        "waveFormat": {"sampleRate": 48000, "channels": 2, "bitsPerSample": 16},
        "audioStats": {
            "bytesRecorded": stats["bytesRecorded"],
            "wavFileBytes": wav_size,
            "sampleCount": stats["sampleCount"],
            "nonZeroSampleCount": stats["nonZeroSampleCount"],
            "peakAbs": stats["peakAbs"],
            "rms": stats["rms"],
            "nonSilent": non_silent,
        },
        "claimBoundary": "Loopback capture only.",
        "nonClaims": ["BEA audible playback"],
    }


def write_pcm16_wav(path: Path, *, non_silent: bool) -> dict[str, Any]:
    sample_value = 1000 if non_silent else 0
    samples = [sample_value] * 1000
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(48000)
        handle.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    normalized = abs(sample_value) / 32768.0
    return {
        "bytesRecorded": len(samples) * 2,
        "sampleCount": len(samples),
        "nonZeroSampleCount": len(samples) if non_silent else 0,
        "peakAbs": normalized,
        "rms": normalized,
    }


def write_audio_json(
    path: Path,
    *,
    start: str,
    end: str,
    non_silent: bool,
    endpoint_id: str = "endpoint-1",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    wav = path.with_suffix(".wav")
    stats = write_pcm16_wav(wav, non_silent=non_silent)
    return write_json(
        path,
        audio_payload(
            output_wav=wav,
            output_json=path,
            start=start,
            end=end,
            stats=stats,
            non_silent=non_silent,
            endpoint_id=endpoint_id,
        ),
    )


def timeline_payload(
    live_path: Path,
    log_path: Path,
    *,
    role: str,
    provenance: str = "cgame-wrapper",
) -> dict[str, Any]:
    wrapper_provenance = provenance == "cgame-wrapper"
    restart_direct_provenance = provenance == "cgame-restart-loop-direct"
    return {
        "schemaVersion": "winui-safe-copy-music-cdb-decode-timeline.v1",
        "role": role,
        "timestampSource": "timestamped-cdb-log",
        "cdbLogTimestamped": True,
        "liveArtifactSha256": sha256_file(live_path),
        "cdbLogSha256": sha256_file(log_path),
        "exactPidCdbObserver": True,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "musicSelectionProvenance": provenance,
        "playMusicForCurrentLevelObserved": wrapper_provenance,
        "restartLoopDirectMusicSelectionObserved": restart_direct_provenance,
        "playSelectionObserved": True,
        "asyncKickPathMatched": True,
        "oggOpenPathMatched": True,
        "decodedPcmPositiveRequestObserved": True,
        "decodeWindowStartUtc": "2026-06-22T00:00:01Z",
        "decodeWindowEndUtc": "2026-06-22T00:00:02Z",
    }


def timeline_payload_with_timestamped_sidecar(
    live_path: Path,
    raw_log_path: Path,
    timestamped_log_path: Path,
    *,
    role: str,
) -> dict[str, Any]:
    payload = timeline_payload(live_path, timestamped_log_path, role=role)
    payload["rawCdbLogSha256"] = sha256_file(raw_log_path)
    payload["timestampedCdbLogPath"] = str(timestamped_log_path)
    payload["timestampedCdbLogSha256"] = sha256_file(timestamped_log_path)
    return payload


def source_music_safety_payload(live_path: Path, *, role: str) -> dict[str, Any]:
    return {
        "schemaVersion": "winui-safe-copy-source-music-safety.v1",
        "role": role,
        "liveArtifactSha256": sha256_file(live_path),
        "target": TARGET,
        "replacement": REPLACEMENT,
        "sourceTargetHashBefore": "3" * 64,
        "sourceTargetHashAfter": "3" * 64,
        "sourceTargetHashUnchanged": True,
        "sourceReplacementHashBefore": "4" * 64,
        "sourceReplacementHashAfter": "4" * 64,
        "sourceReplacementHashUnchanged": True,
    }


class MusicAudibleOutputMaterializerTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> dict[str, Path]:
        clean_log = root / "clean" / "windbg.log"
        staged_log = root / "staged" / "windbg.log"
        mute_log = root / "mute" / "windbg.log"
        clean_log.parent.mkdir(parents=True, exist_ok=True)
        staged_log.parent.mkdir(parents=True, exist_ok=True)
        mute_log.parent.mkdir(parents=True, exist_ok=True)
        clean_log.write_text(log_text(), encoding="utf-8")
        staged_log.write_text(log_text(), encoding="utf-8")
        mute_log.write_text(log_text(), encoding="utf-8")

        clean_live = write_json(root / "clean" / "live.json", live_payload(clean_log, role="cleanBaseline", staged=False))
        staged_live = write_json(root / "staged" / "live.json", live_payload(staged_log, role="stagedPositive", staged=True))
        mute_live = write_json(root / "mute" / "live.json", live_payload(mute_log, role="muteControl", staged=False, mute=True))

        ambient_audio = write_audio_json(root / "ambient" / "audio.json", start="2026-06-22T00:00:00Z", end="2026-06-22T00:00:03Z", non_silent=False)
        clean_audio = write_audio_json(root / "clean" / "audio.json", start="2026-06-22T00:00:00Z", end="2026-06-22T00:00:03Z", non_silent=True)
        staged_audio = write_audio_json(root / "staged" / "audio.json", start="2026-06-22T00:00:00Z", end="2026-06-22T00:00:03Z", non_silent=True)
        mute_audio = write_audio_json(root / "mute" / "audio.json", start="2026-06-22T00:00:00Z", end="2026-06-22T00:00:03Z", non_silent=False)
        ambient_wav = Path(json.loads(ambient_audio.read_text(encoding="utf-8"))["outputWav"])
        clean_wav = Path(json.loads(clean_audio.read_text(encoding="utf-8"))["outputWav"])
        staged_wav = Path(json.loads(staged_audio.read_text(encoding="utf-8"))["outputWav"])
        correlation = capture_correlation.fixture()
        correlation["inputBindings"] = {
            "cleanAudioJsonSha256": sha256_file(clean_audio),
            "cleanAudioWavSha256": sha256_file(clean_wav),
            "stagedAudioJsonSha256": sha256_file(staged_audio),
            "stagedAudioWavSha256": sha256_file(staged_wav),
        }

        paths = {
            "clean_live": clean_live,
            "staged_live": staged_live,
            "mute_live": mute_live,
            "clean_timeline": write_json(root / "clean" / "timeline.json", timeline_payload(clean_live, clean_log, role="cleanBaseline")),
            "staged_timeline": write_json(root / "staged" / "timeline.json", timeline_payload(staged_live, staged_log, role="stagedPositive")),
            "clean_source_music_safety": write_json(root / "clean" / "source-music-safety.json", source_music_safety_payload(clean_live, role="cleanBaseline")),
            "mute_source_music_safety": write_json(root / "mute" / "source-music-safety.json", source_music_safety_payload(mute_live, role="muteControl")),
            "ambient_census": write_json(
                root / "ambient" / "no-bea-census.json",
                {
                    "schemaVersion": "winui-safe-copy-no-bea-process-census.v1",
                    "role": "ambientNoBea",
                    "noBeaProcessObserved": True,
                    "censusStartUtc": "2026-06-22T00:00:00Z",
                    "censusEndUtc": "2026-06-22T00:00:03Z",
                    "audioArtifactSha256": sha256_file(ambient_audio),
                    "audioWavSha256": sha256_file(ambient_wav),
                },
            ),
            "ambient_audio": ambient_audio,
            "clean_audio": clean_audio,
            "staged_audio": staged_audio,
            "mute_audio": mute_audio,
            "capture_source_correlation": write_json(root / "correlation.json", correlation),
            "output": root / "audible-proof.json",
        }
        return paths

    def materialize(self, paths: dict[str, Path]) -> dict[str, Any]:
        return materializer.materialize_from_paths(**paths)

    def test_materializes_sanitized_proof_that_passes_final_checker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            proof = self.materialize(paths)

            summary = final_check.validate_artifact(proof)
            self.assertTrue(summary["runtimeAudibleOutputProof"])
            rendered = json.dumps(proof)
            self.assertNotIn("outputWav", rendered)
            self.assertNotIn("outputJson", rendered)
            self.assertNotIn("device", rendered)
            self.assertNotIn("_rawWavSha256", rendered)
            self.assertNotIn(r"C:\Program Files", rendered)
            self.assertTrue(paths["output"].is_file())

    def test_accepts_plus_zero_utc_inputs_and_normalizes_public_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            for key in ("ambient_audio", "clean_audio", "staged_audio", "mute_audio"):
                audio = json.loads(paths[key].read_text(encoding="utf-8"))
                audio["captureStartedUtc"] = "2026-06-22T00:00:00+00:00"
                audio["captureEndedUtc"] = "2026-06-22T00:00:03+00:00"
                write_json(paths[key], audio)
            census = json.loads(paths["ambient_census"].read_text(encoding="utf-8"))
            census["censusStartUtc"] = "2026-06-22T00:00:00+00:00"
            census["censusEndUtc"] = "2026-06-22T00:00:03+00:00"
            census["audioArtifactSha256"] = sha256_file(paths["ambient_audio"])
            write_json(paths["ambient_census"], census)
            correlation = json.loads(paths["capture_source_correlation"].read_text(encoding="utf-8"))
            correlation["inputBindings"]["cleanAudioJsonSha256"] = sha256_file(paths["clean_audio"])
            correlation["inputBindings"]["stagedAudioJsonSha256"] = sha256_file(paths["staged_audio"])
            write_json(paths["capture_source_correlation"], correlation)

            proof = self.materialize(paths)
            final_check.validate_artifact(proof)

            for run in proof["runs"].values():
                audio = run["audioCapture"]
                self.assertTrue(audio["captureStartedUtc"].endswith("Z"))
                self.assertTrue(audio["captureEndedUtc"].endswith("Z"))

    def test_materializes_with_separate_timestamped_cdb_log_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            root = Path(temp_dir)
            clean_live = json.loads(paths["clean_live"].read_text(encoding="utf-8"))
            clean_raw_log = Path(clean_live["cdbObserver"]["logPath"])
            clean_raw_log.write_text(untimestamped_log_text(), encoding="utf-8")
            clean_timestamped_log = root / "clean" / "windbg.timestamped.log"
            clean_timestamped_log.write_text(log_text(), encoding="utf-8")
            paths["clean_timeline"] = write_json(
                paths["clean_timeline"],
                timeline_payload_with_timestamped_sidecar(
                    paths["clean_live"],
                    clean_raw_log,
                    clean_timestamped_log,
                    role="cleanBaseline",
                ),
            )

            staged_live = json.loads(paths["staged_live"].read_text(encoding="utf-8"))
            staged_raw_log = Path(staged_live["cdbObserver"]["logPath"])
            staged_raw_log.write_text(untimestamped_log_text(), encoding="utf-8")
            staged_timestamped_log = root / "staged" / "windbg.timestamped.log"
            staged_timestamped_log.write_text(log_text(), encoding="utf-8")
            paths["staged_timeline"] = write_json(
                paths["staged_timeline"],
                timeline_payload_with_timestamped_sidecar(
                    paths["staged_live"],
                    staged_raw_log,
                    staged_timestamped_log,
                    role="stagedPositive",
                ),
            )

            proof = self.materialize(paths)

            self.assertTrue(final_check.validate_artifact(proof)["runtimeAudibleOutputProof"])

    def test_materializes_with_restart_loop_direct_music_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            clean_live = json.loads(paths["clean_live"].read_text(encoding="utf-8"))
            clean_log = Path(clean_live["cdbObserver"]["logPath"])
            clean_log.write_text(restart_loop_direct_log_text(), encoding="utf-8")
            paths["clean_timeline"] = write_json(
                paths["clean_timeline"],
                timeline_payload(
                    paths["clean_live"],
                    clean_log,
                    role="cleanBaseline",
                    provenance="cgame-restart-loop-direct",
                ),
            )

            staged_live = json.loads(paths["staged_live"].read_text(encoding="utf-8"))
            staged_log = Path(staged_live["cdbObserver"]["logPath"])
            staged_log.write_text(restart_loop_direct_log_text(), encoding="utf-8")
            paths["staged_timeline"] = write_json(
                paths["staged_timeline"],
                timeline_payload(
                    paths["staged_live"],
                    staged_log,
                    role="stagedPositive",
                    provenance="cgame-restart-loop-direct",
                ),
            )

            proof = self.materialize(paths)
            summary = final_check.validate_artifact(proof)

            self.assertTrue(summary["runtimeAudibleOutputProof"])
            clean_cdb = proof["runs"]["cleanBaseline"]["cdbSelectionDecode"]
            self.assertEqual(clean_cdb["musicSelectionProvenance"], "cgame-restart-loop-direct")
            self.assertFalse(clean_cdb["playMusicForCurrentLevelObserved"])
            self.assertTrue(clean_cdb["restartLoopDirectMusicSelectionObserved"])

    def test_rejects_restart_loop_direct_provenance_without_matching_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            clean_live = json.loads(paths["clean_live"].read_text(encoding="utf-8"))
            clean_log = Path(clean_live["cdbObserver"]["logPath"])
            paths["clean_timeline"] = write_json(
                paths["clean_timeline"],
                timeline_payload(
                    paths["clean_live"],
                    clean_log,
                    role="cleanBaseline",
                    provenance="cgame-restart-loop-direct",
                ),
            )

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_missing_timestamped_cdb_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            paths["clean_timeline"].unlink()

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_output_outside_private_input_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self.build_fixture(root / "bundle")
            paths["output"] = root / "escaped-proof.json"

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_decode_window_outside_audio_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            timeline = json.loads(paths["staged_timeline"].read_text(encoding="utf-8"))
            timeline["decodeWindowEndUtc"] = "2026-06-22T00:00:05Z"
            write_json(paths["staged_timeline"], timeline)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_cdb_log_without_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            clean_live = json.loads(paths["clean_live"].read_text(encoding="utf-8"))
            log_path = Path(clean_live["cdbObserver"]["logPath"])
            log_path.write_text("\n".join(line.split(" ", 1)[1] for line in log_text().splitlines()), encoding="utf-8")
            timeline = json.loads(paths["clean_timeline"].read_text(encoding="utf-8"))
            timeline["cdbLogSha256"] = sha256_file(log_path)
            write_json(paths["clean_timeline"], timeline)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_endpoint_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            audio = json.loads(paths["staged_audio"].read_text(encoding="utf-8"))
            audio["device"]["id"] = "endpoint-2"
            write_json(paths["staged_audio"], audio)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_missing_raw_wav(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            audio = json.loads(paths["clean_audio"].read_text(encoding="utf-8"))
            Path(audio["outputWav"]).unlink()

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_stale_audio_summary_size(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            audio = json.loads(paths["staged_audio"].read_text(encoding="utf-8"))
            audio["audioStats"]["wavFileBytes"] += 1
            write_json(paths["staged_audio"], audio)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_stale_capture_source_correlation_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            correlation = json.loads(paths["capture_source_correlation"].read_text(encoding="utf-8"))
            correlation["inputBindings"]["stagedAudioJsonSha256"] = "0" * 64
            write_json(paths["capture_source_correlation"], correlation)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_music_disabled_on_positive_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            clean = json.loads(paths["clean_live"].read_text(encoding="utf-8"))
            clean["launch"]["arguments"].append("-nomusic")
            write_json(paths["clean_live"], clean)
            timeline = json.loads(paths["clean_timeline"].read_text(encoding="utf-8"))
            timeline["liveArtifactSha256"] = sha256_file(paths["clean_live"])
            write_json(paths["clean_timeline"], timeline)
            source_safety = json.loads(paths["clean_source_music_safety"].read_text(encoding="utf-8"))
            source_safety["liveArtifactSha256"] = sha256_file(paths["clean_live"])
            write_json(paths["clean_source_music_safety"], source_safety)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_missing_ambient_no_bea_census(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            census = json.loads(paths["ambient_census"].read_text(encoding="utf-8"))
            census["noBeaProcessObserved"] = False
            write_json(paths["ambient_census"], census)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_stale_ambient_census_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            census = json.loads(paths["ambient_census"].read_text(encoding="utf-8"))
            census["audioArtifactSha256"] = "0" * 64
            write_json(paths["ambient_census"], census)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_ambient_census_outside_audio_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            census = json.loads(paths["ambient_census"].read_text(encoding="utf-8"))
            census["censusEndUtc"] = "2026-06-22T00:00:01Z"
            write_json(paths["ambient_census"], census)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_rejects_missing_clean_source_music_safety(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            safety = json.loads(paths["clean_source_music_safety"].read_text(encoding="utf-8"))
            safety["sourceTargetHashUnchanged"] = False
            write_json(paths["clean_source_music_safety"], safety)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)

    def test_redacts_private_paths_from_cli_errors(self) -> None:
        text = materializer.sanitize_error_message(r"Missing JSON input: C:\private\proof\artifact.json")
        self.assertNotIn(r"C:\private", text)
        self.assertIn("<path>", text)

    def test_rejects_calibration_tone_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.build_fixture(Path(temp_dir))
            audio = json.loads(paths["clean_audio"].read_text(encoding="utf-8"))
            audio["calibration"]["played"] = True
            write_json(paths["clean_audio"], audio)

            with self.assertRaises(materializer.MaterializerError):
                self.materialize(paths)


if __name__ == "__main__":
    unittest.main()
