#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Unit tests for tools/mod_starter.py (zero retail files required)."""
from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import struct
import sys
import tempfile
import unittest
import zlib
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import mod_starter  # noqa: E402


class ModStarterValidationTests(unittest.TestCase):
    def test_valid_world_fixture_scaffold_and_sha256_integrity(self):
        with tempfile.TemporaryDirectory(prefix="mod-starter-world-") as tmp:
            out = Path(tmp) / "mods"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod_starter.main(
                    [
                        "--out", str(out),
                        "--id", "ce-example-starter",
                        "--name", "CE Example Starter",
                        "--version", "1.0.0",
                        "--author", "Unit Test",
                        "--description", "Self-contained world starter fixture.",
                        "--ce-min", "0.1.14",
                        "--world-level", "100",
                        "--world-fixture",
                        "--json",
                    ]
                )
            self.assertEqual(0, rc)
            summary = json.loads(buf.getvalue())
            mod_dir = out / "ce-example-starter"
            manifest_path = mod_dir / "mod.json"
            wrd_path = mod_dir / "data/worlds/world100.wrd"
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(wrd_path.is_file())

            manifest = json.loads(manifest_path.read_text(encoding="ascii"))
            self.assertEqual(1, manifest["schema"])
            self.assertEqual("ce-example-starter", manifest["id"])
            self.assertEqual("CE Example Starter", manifest["name"])
            self.assertEqual("1.0.0", manifest["version"])
            self.assertEqual("0.1.14", manifest["ce_min"])
            self.assertEqual(1, len(manifest["files"]))
            entry = manifest["files"][0]
            raw = wrd_path.read_bytes()
            self.assertEqual("data/worlds/world100.wrd", entry["path"])
            self.assertEqual(len(raw), entry["size"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
            self.assertEqual(summary["files"][0]["sha256"], entry["sha256"])
            self.assertTrue(raw.startswith(b"WRES"))

    def _pack_aya(self, payload: bytes) -> bytes:
        out = bytearray()
        for start in range(0, len(payload), mod_starter.AYA_BLOCK_BYTES):
            comp = zlib.compress(payload[start : start + mod_starter.AYA_BLOCK_BYTES], 9)
            out += struct.pack("<I", len(comp)) + comp
        return bytes(out)

    def test_game_dir_default_target_and_archive_wres_extraction(self):
        with tempfile.TemporaryDirectory(prefix="mod-starter-game-") as tmp:
            root = Path(tmp)
            game = root / "game"
            (game / "data/language").mkdir(parents=True)
            lang_bytes = b"AUTHORED_LANGUAGE_TABLE_V1"
            (game / "data/language/english.dat").write_bytes(lang_bytes)

            # Authentic PC .aya framing ([u32_le len][zlib_blob]) with sibling top-level LVLR and
            # WRES -> WRLD -> (WDAT, BSWD, RLWD) chunks (matching world_resources_encode.py).
            (game / "data/resources").mkdir(parents=True)
            lvlr_chunk = b"LVLR" + struct.pack("<I", 4) + b"HEAD"
            wdat_chunk = b"WDAT" + struct.pack("<I", 8) + struct.pack("<ii", 100, 100)
            bswd_chunk = b"BSWD" + struct.pack("<I", 12) + b"BASE_WORLD01"
            rlwd_payload = b"SYNTHETIC_RLWD_REAL_WORLD_100_BODY"
            rlwd_chunk = b"RLWD" + struct.pack("<I", len(rlwd_payload)) + rlwd_payload
            wrld_body = wdat_chunk + bswd_chunk + rlwd_chunk
            wrld_chunk = b"WRLD" + struct.pack("<I", len(wrld_body)) + wrld_body
            wres_chunk = b"WRES" + struct.pack("<I", len(wrld_chunk)) + wrld_chunk
            (game / "data/resources/100_res_PC.aya").write_bytes(self._pack_aya(lvlr_chunk + wres_chunk))

            # Also verify multi-block (> 1 MiB) .aya inflation succeeds and unframed raw zlib is rejected.
            pad = b"A" * (mod_starter.AYA_BLOCK_BYTES + 16)
            lvlr_big = b"LVLR" + struct.pack("<I", len(pad)) + pad
            (game / "data/resources/110_res_PC.aya").write_bytes(self._pack_aya(lvlr_big + wres_chunk))
            (game / "data/resources/120_res_PC.aya").write_bytes(zlib.compress(lvlr_chunk + wres_chunk))

            out = root / "out"
            with redirect_stdout(io.StringIO()):
                rc = mod_starter.main(
                    ["--out", str(out), "--id", "lang-starter", "--game-dir", str(game), "--json"]
                )
            self.assertEqual(0, rc)
            staged = out / "lang-starter/data/language/english.dat"
            self.assertEqual(lang_bytes, staged.read_bytes())

            with redirect_stdout(io.StringIO()):
                rc2 = mod_starter.main(
                    [
                        "--out", str(out),
                        "--id", "world-from-aya",
                        "--game-dir", str(game),
                        "--world-level", "100",
                        "--json",
                    ]
                )
            self.assertEqual(0, rc2)
            self.assertEqual(rlwd_payload, (out / "world-from-aya/data/worlds/world100.wrd").read_bytes())

            with redirect_stdout(io.StringIO()):
                rc3 = mod_starter.main(
                    [
                        "--out", str(out),
                        "--id", "world-multiblock",
                        "--game-dir", str(game),
                        "--world-level", "110",
                        "--json",
                    ]
                )
            self.assertEqual(0, rc3)
            self.assertEqual(rlwd_payload, (out / "world-multiblock/data/worlds/world110.wrd").read_bytes())

            with self.assertRaises(mod_starter.ModStarterError):
                mod_starter.extract_wres_from_level_archive(game, 120)

            # Game dir must remain untouched.
            self.assertEqual(lang_bytes, (game / "data/language/english.dat").read_bytes())

    def test_invalid_mod_ids_rejected(self):
        for bad_id in ("", "UpperCase", "bad space", "bad/slash", "a" * 49, "con", "nul", "com1", "lpt9", "aux"):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(mod_starter.ModStarterError):
                    mod_starter.check_mod_id(bad_id)

    def test_invalid_paths_rejected(self):
        bad_paths = (
            "",
            "english.dat",
            "BEA.exe",
            "data/",
            "data/../escape.dat",
            "data/./same.dat",
            "data//double.dat",
            "data\\backslash.dat",
            "data/wild*card.dat",
            "data/trailing_dot./file.dat",
            "data/ leading.dat",
            "data/short~1/file.dat",
            "data/con/file.dat",
            "data/nul.dat",
            "data/conin$.dat",
            "data/CONOUT$.dat",
            "data/con .dat",
            "data/com1 .dat",
            "data/lpt9   .wrd",
            "data/" + "/".join(["a"] * 12) + "/too_deep.dat",
            "data/" + "a" * 240,
            "data/non\x7fascii.dat",
        )
        for bad_path in bad_paths:
            with self.subTest(bad_path=bad_path):
                with self.assertRaises(mod_starter.ModStarterError):
                    mod_starter.check_mod_path(bad_path)

    def test_invalid_identity_and_version_bounds_rejected(self):
        with self.assertRaises(mod_starter.ModStarterError):
            mod_starter.check_identity("valid-id", "", "1.0")
        with self.assertRaises(mod_starter.ModStarterError):
            mod_starter.check_identity("valid-id", "NonAscii\u00e9", "1.0")
        with self.assertRaises(mod_starter.ModStarterError):
            mod_starter.check_identity("valid-id", "Name", "1.0", ce_min="0.2.0", ce_max="0.1.9")
        with self.assertRaises(mod_starter.ModStarterError):
            mod_starter.build_manifest("valid-id", "Name", "1.0", {})
        with self.assertRaises(mod_starter.ModStarterError):
            mod_starter.build_manifest(
                "valid-id",
                "Name",
                "1.0",
                {"data/language/english.dat": b"a", "data/language/ENGLISH.dat": b"b"},
            )

    def test_refuses_writing_inside_game_dir_or_existing_folder(self):
        with tempfile.TemporaryDirectory(prefix="mod-starter-safety-") as tmp:
            root = Path(tmp)
            game = root / "game"
            (game / "data/language").mkdir(parents=True)
            (game / "data/language/english.dat").write_bytes(b"DATA")

            err = io.StringIO()
            with redirect_stderr(err):
                rc = mod_starter.main(
                    ["--out", str(game / "mods"), "--id", "inside-game", "--game-dir", str(game)]
                )
            self.assertEqual(2, rc)
            self.assertIn("refused", err.getvalue().casefold())

            out = root / "mods"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    0,
                    mod_starter.main(
                        ["--out", str(out), "--id", "existing-mod", "--world-level", "100", "--world-fixture"]
                    ),
                )
            err2 = io.StringIO()
            with redirect_stderr(err2):
                rc2 = mod_starter.main(
                    ["--out", str(out), "--id", "existing-mod", "--world-level", "100", "--world-fixture"]
                )
            self.assertEqual(2, rc2)
            self.assertIn("already contains", err2.getvalue())


class CatalogDiscoveryTests(unittest.TestCase):
    def test_catalog_jsonl_directory_and_json_formats(self):
        records = [
            {
                "type": "texture",
                "source": {"container": "data/resources/dxtntextures/meshtex%BE_texA.tga(0)A1R5G5B5.aya"},
            },
            {
                "type": "mesh",
                "source": {"container": "data/resources/meshes/be_torso.aya"},
            },
            {
                "type": "level",
                "level": {"number": 100},
                "source": {"container": "data/resources/100_res_PC.aya"},
            },
            {
                "type": "table",
                "source": {"container": "data/language/english.dat"},
            },
            # Non-data entries must never be listed as valid mod targets.
            {
                "type": "executable",
                "source": {"container": "BEA.exe"},
            },
            {
                "type": "manual",
                "source": {"container": "manuals/readme.html"},
            },
        ]
        with tempfile.TemporaryDirectory(prefix="mod-starter-cat-") as tmp:
            cat_dir = Path(tmp) / "catalog"
            cat_dir.mkdir()
            (cat_dir / "assets.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8"
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod_starter.main(["--catalog", str(cat_dir), "--list-targets", "--json"])
            self.assertEqual(0, rc)
            report = json.loads(buf.getvalue())
            self.assertEqual([100], report["levels"])
            paths = {row["path"] for row in report["targets"]}
            self.assertIn("data/resources/dxtntextures/meshtex%BE_texA.tga(0)A1R5G5B5.aya", paths)
            self.assertIn("data/resources/meshes/be_torso.aya", paths)
            self.assertIn("data/resources/100_res_PC.aya", paths)
            self.assertIn("data/worlds/world100.wrd", paths)
            self.assertIn("data/language/english.dat", paths)
            self.assertNotIn("BEA.exe", paths)
            self.assertNotIn("manuals/readme.html", paths)

            # Filter by type + query + JSON single-file catalog format.
            single_json = Path(tmp) / "content_catalog.json"
            single_json.write_text(json.dumps({"assets": records}), encoding="utf-8")
            filtered = mod_starter.discover_catalog_targets(
                single_json, target_type="texture", query="be_texa", limit=5
            )
            self.assertEqual(1, filtered["matchingTargets"])
            self.assertEqual(
                "data/resources/dxtntextures/meshtex%BE_texA.tga(0)A1R5G5B5.aya",
                filtered["targets"][0]["path"],
            )


class ValidateWithBeaTests(unittest.TestCase):
    def _write_mock_bea(self, path: Path, body: str) -> Path:
        path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_validate_with_bea_passing_and_refusing_exit_codes(self):
        with tempfile.TemporaryDirectory(prefix="mod-starter-bea-") as tmp:
            root = Path(tmp)
            mock_ok = self._write_mock_bea(
                root / "bea-ok",
                """import os, sys
from pathlib import Path
assert sys.argv[1:] == ["--check-mods", "ce-example-starter"], sys.argv
assert "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ
assert os.environ.get("SDL_VIDEO_DRIVER") == "offscreen"
mod_json = Path(os.environ["BEA_USER_DIR"]) / "mods" / "ce-example-starter" / "mod.json"
assert mod_json.is_file() and not mod_json.is_symlink()
print("mod ce-example-starter: ok")
print("result: 1 passed, 0 refused")
sys.exit(0)
""",
            )
            mock_fail = self._write_mock_bea(
                root / "bea-fail",
                """import sys
print("refused ce-example-starter: sha256 mismatch")
print("result: 0 passed, 1 refused")
sys.exit(1)
""",
            )
            mock_bad_marker = self._write_mock_bea(
                root / "bea-wrong-text",
                """import sys
print("result: 0 passed, 0 refused")
sys.exit(0)
""",
            )

            out = root / "stage"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod_starter.main(
                    [
                        "--out", str(out),
                        "--id", "ce-example-starter",
                        "--world-level", "100",
                        "--world-fixture",
                        "--validate-with", str(mock_ok),
                        "--json",
                    ]
                )
            self.assertEqual(0, rc)
            summary = json.loads(buf.getvalue())
            self.assertTrue(summary["validation"]["ok"])

            with self.assertRaises(mod_starter.ModStarterError) as ctx:
                mod_starter.validate_with_bea(mock_fail, out / "ce-example-starter", "ce-example-starter")
            self.assertIn("exit 1", str(ctx.exception))

            with self.assertRaises(mod_starter.ModStarterError):
                mod_starter.validate_with_bea(mock_bad_marker, out / "ce-example-starter", "ce-example-starter")

    def test_discover_bea_runtime_libs_requires_dxvk_present(self):
        from unittest import mock
        clean_env = {k: v for k, v in os.environ.items() if k != "BEA_PORT_DATA"}
        with mock.patch.dict(os.environ, clean_env, clear=True), \
             tempfile.TemporaryDirectory(prefix="mod-starter-libs-") as tmp:
            root = Path(tmp)
            exe = root / "bea"
            exe.write_bytes(b"")
            (root / "lib").mkdir()
            # Without libdxvk_d3d9.so.0, sibling lib/ is not injected.
            self.assertEqual([], mod_starter._discover_bea_runtime_libs(exe))
            (root / "lib/libdxvk_d3d9.so.0").write_bytes(b"")
            self.assertEqual([str(root / "lib")], mod_starter._discover_bea_runtime_libs(exe))

    def test_cli_returns_nonzero_on_missing_args(self):
        err = io.StringIO()
        with redirect_stderr(err):
            rc = mod_starter.main([])
        self.assertEqual(2, rc)
        err2 = io.StringIO()
        with redirect_stderr(err2):
            rc2 = mod_starter.main(["--list-targets"])
        self.assertEqual(2, rc2)


if __name__ == "__main__":
    unittest.main()
