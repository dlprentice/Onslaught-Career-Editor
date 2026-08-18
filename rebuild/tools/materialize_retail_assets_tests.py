#!/usr/bin/env python3
"""Focused regressions for the local retail-asset materializer."""

from __future__ import annotations

import struct
import tempfile
import unittest
import zlib
import json
from pathlib import Path
from unittest import mock

import materialize_retail_assets as materializer


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind)
    crc = zlib.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _png(
    width: int,
    height: int,
    *,
    idat: bytes | None = None,
    last_pixel: int = 0,
) -> bytes:
    signature = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = bytearray(b"".join(b"\0" + bytes(width * 3) for _ in range(height)))
    pixels[-1] = last_pixel
    return (
        signature
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(pixels) if idat is None else idat)
        + _chunk(b"IEND", b"")
    )


class StartupMediaCacheTests(unittest.TestCase):
    def test_complete_rgb_png_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3))
            self.assertEqual((2, 3), materializer._png_dimensions(path))

    def test_header_only_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3)[:33])
            self.assertIsNone(materializer._png_dimensions(path))

    def test_framed_but_invalid_idat_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "frame.png"
            path.write_bytes(_png(2, 3, idat=b"\x01"))
            self.assertIsNone(materializer._png_dimensions(path))

    def test_non_object_manifest_is_not_a_ready_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            (media / "startup-media.json").write_text("[]", encoding="utf-8")
            self.assertFalse(materializer._startup_media_ready(root, media))

    def test_legacy_v2_cache_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            (media / "startup-media.json").write_text(
                '{"schema":"onslaught-startup-media.v2","clips":{},"stills":{}}',
                encoding="utf-8",
            )
            self.assertFalse(materializer._startup_media_ready(root, media))

    def test_ready_cache_rejects_a_corrupt_middle_frame(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            frames = media / "clip"
            frames.mkdir(parents=True)
            source = root / "clip.vid"
            splash_source = root / "splash.tga"
            source.write_bytes(b"clip-source")
            splash_source.write_bytes(b"splash-source")
            frame_paths = []
            for frame in range(1, 4):
                path = frames / f"f{frame:05d}.png"
                path.write_bytes(_png(2, 3))
                frame_paths.append(path)
            (media / "splash.png").write_bytes(_png(512, 512))
            manifest = {
                "schema": materializer.STARTUP_MEDIA_SCHEMA,
                "clips": {
                    "Logo": {
                        "source": "clip.vid",
                        "sourceSha256": materializer._sha256(source.read_bytes()),
                        "width": 2,
                        "height": 3,
                        "fpsNumerator": 25,
                        "fpsDenominator": 1,
                        "frameCount": 3,
                        "framePathFormat": "clip/f{0:D5}.png",
                        "framesSha256": materializer._startup_frame_set_sha256(
                            frame_paths
                        ),
                    }
                },
                "stills": {
                    "Splash": {
                        "source": "splash.tga",
                        "sourceSha256": materializer._sha256(
                            splash_source.read_bytes()
                        ),
                        "path": "splash.png",
                        "outputSha256": materializer._sha256(
                            (media / "splash.png").read_bytes()
                        ),
                    }
                },
            }
            (media / "startup-media.json").write_text(
                __import__("json").dumps(manifest),
                encoding="utf-8",
            )
            with (
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_CLIPS",
                    (("Logo", "clip.vid", "clip", 2, 3, 25, 3),),
                ),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
            ):
                self.assertTrue(materializer._startup_media_ready(root, media))
                frame_paths[1].write_bytes(b"corrupt-middle-frame")
                self.assertFalse(materializer._startup_media_ready(root, media))

    def test_ready_cache_rejects_a_valid_but_different_splash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            splash_source = root / "splash.tga"
            splash_source.write_bytes(b"splash-source")
            splash_path = media / "splash.png"
            splash_path.write_bytes(_png(512, 512))
            manifest = {
                "schema": materializer.STARTUP_MEDIA_SCHEMA,
                "clips": {},
                "stills": {
                    "Splash": {
                        "source": "splash.tga",
                        "sourceSha256": materializer._sha256(
                            splash_source.read_bytes()
                        ),
                        "path": "splash.png",
                        "outputSha256": materializer._sha256(
                            splash_path.read_bytes()
                        ),
                    }
                },
            }
            (media / "startup-media.json").write_text(
                __import__("json").dumps(manifest),
                encoding="utf-8",
            )
            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
            ):
                self.assertTrue(materializer._startup_media_ready(root, media))
                del manifest["stills"]["Splash"]["outputSha256"]
                (media / "startup-media.json").write_text(
                    json.dumps(manifest),
                    encoding="utf-8",
                )
                self.assertFalse(materializer._startup_media_ready(root, media))
                manifest["stills"]["Splash"]["outputSha256"] = (
                    materializer._sha256(splash_path.read_bytes())
                )
                (media / "startup-media.json").write_text(
                    json.dumps(manifest),
                    encoding="utf-8",
                )
                splash_path.write_bytes(_png(512, 512, last_pixel=1))
                self.assertFalse(materializer._startup_media_ready(root, media))

    def test_generation_rejects_a_malformed_splash_before_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            (root / "splash.tga").write_bytes(b"splash-source")
            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
                mock.patch.object(materializer.subprocess, "run"),
                mock.patch.object(
                    materializer,
                    "_png_dimensions",
                    return_value=None,
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "invalid 512x512 PNG"):
                    materializer._materialize_startup_media(root, media)
            self.assertFalse((media / "startup-media.json").exists())

    def test_generation_receipts_exact_splash_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            source = root / "splash.tga"
            source.write_bytes(b"splash-source")

            def write_splash(arguments: list[str], **_kwargs: object) -> None:
                Path(arguments[-1]).write_bytes(_png(512, 512))

            with (
                mock.patch.object(materializer, "STARTUP_MEDIA_CLIPS", ()),
                mock.patch.object(
                    materializer,
                    "STARTUP_MEDIA_SPLASH_SOURCE",
                    "splash.tga",
                ),
                mock.patch.object(
                    materializer.subprocess,
                    "run",
                    side_effect=write_splash,
                ),
            ):
                manifest_path = materializer._materialize_startup_media(root, media)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            splash_path = media / "splash.png"
            self.assertEqual("onslaught-startup-media.v4", manifest["schema"])
            self.assertEqual(
                materializer._sha256(splash_path.read_bytes()),
                manifest["stills"]["Splash"]["outputSha256"],
            )


def _bink_header(track_ids: list[int], sample_rate: int = 44100) -> bytes:
    """A Bink header carrying only what _bink_audio_tracks reads."""
    count = len(track_ids)
    header = bytearray(b"BIKi")
    header += struct.pack("<I", 0)          # 0x04 file size
    header += struct.pack("<I", 3095)       # 0x08 frame count
    header += struct.pack("<I", 0)          # 0x0C largest frame
    header += struct.pack("<I", 3095)       # 0x10 frame count again
    header += struct.pack("<II", 480, 300)  # 0x14 width / 0x18 height
    header += struct.pack("<II", 25, 1)     # 0x1C fps num / 0x20 den
    header += struct.pack("<I", 0)          # 0x24 video flags
    header += struct.pack("<I", count)      # 0x28 audio track count
    header += b"".join(struct.pack("<I", 0) for _ in range(count))
    header += b"".join(struct.pack("<HH", sample_rate, 0xE000) for _ in range(count))
    header += b"".join(struct.pack("<I", track) for track in track_ids)
    return bytes(header)


def _pcm_wav(sample_frames: int, rate: int = 44100, channels: int = 2) -> bytes:
    block_align = channels * 2
    data = bytes(sample_frames * block_align)
    return (
        b"RIFF"
        + struct.pack("<I", 36 + len(data))
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, channels, rate, rate * block_align, block_align, 16)
        + b"data"
        + struct.pack("<I", len(data))
        + data
    )


class CutsceneVoiceTrackTests(unittest.TestCase):
    """The two laws that connect "English is Bink track 0" to bytes on disk.

    Everything else in that chain is a property of BEA.exe and was read out of
    the pristine specimen. These are the parts that are properties of the .vid
    and of the decode, so they are the parts this script can check on any
    machine and the parts a wrong edit here would silently break.
    """

    # Real numbers from cutscenes/01.vid: 3095 video frames at 25 fps is
    # 5,459,580 sample frames at 44.1 kHz, and the decode produces 5,460,480 —
    # an overhang of 900, well inside one 2048-sample binkaudio frame.
    VIDEO_FRAMES = 3095
    FPS = 25
    DECODED_SAMPLE_FRAMES = 5_460_480

    def _run(self, temporary: str, track_ids: list[int], sample_frames: int):
        root = Path(temporary)
        destination = root / "clip"
        destination.mkdir(parents=True, exist_ok=True)
        source = root / "01.vid"
        source.write_bytes(_bink_header(track_ids))

        def write_audio(arguments: list[str], **_kwargs: object) -> None:
            Path(arguments[-1]).write_bytes(_pcm_wav(sample_frames))

        with mock.patch.object(
            materializer.subprocess, "run", side_effect=write_audio
        ):
            return materializer._materialize_clip_audio(
                source,
                "data/video/cutscenes/01.vid",
                "clip",
                destination,
                self.VIDEO_FRAMES,
                self.FPS,
                (0, "voice-track00.wav", 44100, 2, 16),
            )

    def test_identity_track_table_and_measured_length_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            entry = self._run(temporary, [0, 1, 2, 3, 4], self.DECODED_SAMPLE_FRAMES)

        self.assertEqual(0, entry["track"])
        self.assertEqual("clip/voice-track00.wav", entry["path"])
        self.assertEqual(44100, entry["sampleRate"])
        self.assertEqual(2, entry["channels"])
        self.assertEqual(self.DECODED_SAMPLE_FRAMES, entry["sampleFrameCount"])
        self.assertEqual(64, len(entry["outputSha256"]))

    def test_a_non_identity_track_table_is_refused(self) -> None:
        # BinkSetSoundTrack takes a track ID; `-map 0:a:N` takes an ordinal.
        # They coincide only while the shipped table is the identity. If it ever
        # is not, ordinal 0 stops being the track the game would have played and
        # the decode must fail rather than quietly ship another language.
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "not the identity"):
                self._run(temporary, [4, 3, 2, 1, 0], self.DECODED_SAMPLE_FRAMES)

    def test_an_audio_track_that_does_not_match_the_video_length_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            # One binkaudio frame too long.
            with self.assertRaisesRegex(RuntimeError, r"sample frames"):
                self._run(
                    temporary,
                    [0, 1, 2, 3, 4],
                    self.DECODED_SAMPLE_FRAMES + materializer.BINK_AUDIO_FRAME_SAMPLES,
                )

        with tempfile.TemporaryDirectory() as temporary:
            # Short of the video: the movie would outlive its voice.
            with self.assertRaisesRegex(RuntimeError, r"sample frames"):
                self._run(temporary, [0, 1, 2, 3, 4], self.VIDEO_FRAMES * 44100 // self.FPS - 1)


class FrontendLoadingBarAssetsTests(unittest.TestCase):
    def test_barl_barc_barr_are_hash_pinned(self) -> None:
        rows = {
            destination.as_posix(): (source, expected)
            for destination, source, expected in materializer.FRONTEND_ASSETS
        }
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-l.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarL.tga(0)A8R8G8B8.aya",
                "fbd28ca720ebe91cb8f58a9f5be5e4e9ee5c013fc42052fd1bec6b41dfd094bd",
            ),
        )
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-c.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarC.tga(0)A8R8G8B8.aya",
                "347828edf9f97dd3463ce7374e167e57f8bd837113cbfad71cb8cbc6bcde68a5",
            ),
        )
        self.assertEqual(
            rows["rebuild/OnslaughtRebuild.Godot/Assets/Frontend/bar-r.texture.aya"],
            (
                "data/resources/dxtntextures/FrontEnd%BarR.tga(0)A8R8G8B8.aya",
                "9995d4a41ff140d3d33004086e82f940db946c0db45635b5c853662ace6c6199",
            ),
        )


if __name__ == "__main__":
    unittest.main()
