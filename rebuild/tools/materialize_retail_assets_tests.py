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
            self.assertEqual("onslaught-startup-media.v3", manifest["schema"])
            self.assertEqual(
                materializer._sha256(splash_path.read_bytes()),
                manifest["stills"]["Splash"]["outputSha256"],
            )


if __name__ == "__main__":
    unittest.main()
