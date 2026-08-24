#!/usr/bin/env python3
"""Self-tests for the patch-surface LOD attribution comparator."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import validate_lod_attribution as subject

FIXTURES = HERE / "testdata" / "lod-attribution"
PRISTINE = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PRODUCT = "b49378d659ca3272b9599369cb50d2bd8295293c5c39e1b405aaf5c9ce0df30c"
STAGED = "c771c1c15d5130b131b1bd443eb7390132030997b73d11bfe0938d376e1c1d54"
OPTIONS = "6ffcd7b639c236f329e0349a0b5fc1159c6900872171488570b7cbfa19397f04"
SAVE = "9aec08aca2df5d0a42b723ef17bb3e04961cef36746eecba69e5b25e8dc96853"
ROW = {
    "va": "0x00631E8C",
    "original_bytes": "00002041",
    "patched_bytes": "0000a041",
}
IDENTITY_MATRIX = (
    "1.000000,0.000000,0.000000,0.000000,"
    "0.000000,1.000000,0.000000,0.000000,"
    "0.000000,0.000000,1.000000,0.000000,"
    "0.000000,0.000000,0.000000,1.000000"
)
SCALED_TEXTURE_MATRIX = (
    "2.000000,0.000000,0.000000,0.000000,"
    "0.000000,2.000000,0.000000,0.000000,"
    "0.000000,0.000000,1.000000,0.000000,"
    "0.500000,0.500000,0.000000,1.000000"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_draw_fields(text: str, fields: str) -> str:
    lines = [line + fields if line.startswith("D ") else line for line in text.splitlines()]
    return "\n".join(lines) + "\n"


def add_texture_transform(text: str, matrix_id: int, values: str, *,
                          slot: str = "tex0", flags: str = "2",
                          derived: bool = False) -> str:
    lines = text.splitlines()
    world_index = next(index for index, line in enumerate(lines) if " world0 m=" in line)
    marker = " mul" if derived else ""
    lines.insert(world_index, f"M {matrix_id} {slot}{marker} m={values}")
    return append_draw_fields("\n".join(lines) + "\n", f" tm0={matrix_id} tmflags={flags}")


def sidecar(role: str, log: Path) -> dict[str, object]:
    is_stock = role == "stock"
    pid = 1111 if is_stock else 2222
    exe = PRODUCT if is_stock else STAGED
    applied = ROW["original_bytes"] if is_stock else ROW["patched_bytes"]
    rows = [] if is_stock else [{**ROW, "applied_bytes": applied}]
    return {
        "schema": "bea-lod-attribution-run.v1",
        "role": role,
        "label": f"fixture-{role}",
        "pid": pid,
        "level": 100,
        "quality": "high",
        "game_args": ["-skipfmv", "-level", "100"],
        "checkpoint": "level100-static-camera-v1",
        "row": {**ROW, "applied_bytes": applied},
        "hashes": {
            "pristine": PRISTINE,
            "product": PRODUCT,
            "exe": exe,
            "options": OPTIONS,
            "saves": {"BEA 1.bes": SAVE, "BEA 2.bes": SAVE},
            "log": sha256(log),
        },
        "stage_rows": rows,
        "capture": {
            "proxy_version": 2,
            "firstframe": 100 if is_stock else 210,
            "maxframes": 3,
            "digest": True,
            "texhash": True,
            "strictcov": True,
        },
        "guard": {
            "copied_profile": True,
            "collision": False,
            "process_count_peak": 1,
            "terminal_processes": [],
            "proxy_removed": True,
        },
    }


class LodAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.stock_log = self.root / "stock.log"
        self.staged_log = self.root / "staged.log"
        self.stock_log.write_bytes((FIXTURES / "stock.synthetic-fixture.txt").read_bytes())
        self.staged_log.write_bytes((FIXTURES / "staged.synthetic-fixture.txt").read_bytes())
        self.stock_run = self.root / "stock.json"
        self.staged_run = self.root / "staged.json"
        self.write_sidecars()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_sidecars(self, stock: dict[str, object] | None = None,
                       staged: dict[str, object] | None = None) -> None:
        stock = stock or sidecar("stock", self.stock_log)
        staged = staged or sidecar("staged", self.staged_log)
        self.stock_run.write_text(json.dumps(stock), encoding="utf-8")
        self.staged_run.write_text(json.dumps(staged), encoding="utf-8")

    def analyze(self, **kwargs: object) -> dict[str, object]:
        return subject.analyze_pair(
            self.stock_log,
            self.stock_run,
            self.staged_log,
            self.staged_run,
            row_va="0x00631E8C",
            min_stable_frames=3,
            min_matched_draws=1,
            **kwargs,
        )

    def assert_error(self, receipt: dict[str, object], code: str) -> None:
        self.assertFalse(receipt["ok"], receipt)
        self.assertIn(code, receipt["error_codes"], receipt)

    def test_process_local_ids_normalize_to_one_camera_and_draw_identity(self) -> None:
        receipt = self.analyze()
        self.assertTrue(receipt["ok"], receipt)
        self.assertEqual(receipt["checkpoint"]["stock_frames"], [100, 101, 102])
        self.assertEqual(receipt["checkpoint"]["staged_frames"], [210, 211, 212])
        self.assertEqual(receipt["summary"]["matched_draws"], 1)
        self.assertEqual(receipt["summary"]["changed_meshes"], 1)
        self.assertEqual(receipt["verdict"], "staged_finer_geometry_at_matched_camera")
        match = receipt["matched_draws"][0]
        self.assertEqual(match["detail_order"], "staged_higher")
        self.assertNotEqual(match["stock"]["mesh_identity"], match["staged"]["mesh_identity"])

    def test_receipt_is_deterministic_and_does_not_embed_absolute_paths(self) -> None:
        first = self.analyze()
        second = self.analyze()
        self.assertEqual(first, second)
        body = json.dumps(first, sort_keys=True)
        self.assertNotIn(str(self.root), body)

    def test_no_geometry_delta_is_a_valid_exact_negative(self) -> None:
        staged = self.staged_log.read_text(encoding="utf-8")
        staged = staged.replace("primc=140 verts=100", "primc=100 verts=80")
        staged = staged.replace("n=100 bytes=3600 h=CCCCCCCCCCCCCCCC", "n=80 bytes=2880 h=AAAAAAAAAAAAAAAA")
        staged = staged.replace("n=420 bytes=840 h=DDDDDDDDDDDDDDDD", "n=300 bytes=600 h=BBBBBBBBBBBBBBBB")
        self.staged_log.write_text(staged, encoding="utf-8")
        self.write_sidecars()
        receipt = self.analyze()
        self.assertTrue(receipt["ok"], receipt)
        self.assertEqual(receipt["verdict"], "no_geometry_delta_at_matched_camera")
        self.assertEqual(receipt["summary"]["changed_meshes"], 0)

    def test_sidecar_log_hash_mismatch_fails_closed(self) -> None:
        staged = sidecar("staged", self.staged_log)
        staged["hashes"]["log"] = "0" * 64
        self.write_sidecars(staged=staged)
        self.assert_error(self.analyze(), "staged_log_hash_mismatch")

    def test_capture_with_zero_draw_window_fails_closed(self) -> None:
        text = self.stock_log.read_text(encoding="utf-8").replace("maxframes=3", "maxframes=0", 1)
        self.stock_log.write_text(text, encoding="utf-8")
        stock = sidecar("stock", self.stock_log)
        stock["capture"]["maxframes"] = 0
        self.write_sidecars(stock=stock)
        self.assert_error(self.analyze(), "stock_capture_maxframes_not_positive")

    def test_missing_referenced_matrix_fails_closed(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(" v=910 p=911", " v=999 p=911")
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_missing_matrix")

    def test_nonzero_untracked_matrix_state_rejects_the_run(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            " p=911", " p=911 mtxuntracked=1"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_mtxuntracked_nonzero")

    def test_invalid_untracked_matrix_state_rejects_the_run(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            " p=911", " p=911 mtxuntracked=?"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_mtxuntracked_invalid")

    def test_active_texture_matrix_values_are_part_of_the_draw_anchor(self) -> None:
        stock = add_texture_transform(
            self.stock_log.read_text(encoding="utf-8"), 13, IDENTITY_MATRIX
        )
        staged = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"), 913, SCALED_TEXTURE_MATRIX
        )
        self.stock_log.write_text(stock, encoding="utf-8")
        self.staged_log.write_text(staged, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_matched_draws")

    def test_texture_transform_flags_are_part_of_the_draw_anchor(self) -> None:
        stock = add_texture_transform(
            self.stock_log.read_text(encoding="utf-8"), 13, IDENTITY_MATRIX, flags="2"
        )
        staged = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"), 913, IDENTITY_MATRIX, flags="3"
        )
        self.stock_log.write_text(stock, encoding="utf-8")
        self.staged_log.write_text(staged, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_matched_draws")

    def test_matching_texture_transforms_normalize_process_local_ids(self) -> None:
        stock = add_texture_transform(
            self.stock_log.read_text(encoding="utf-8"), 13, IDENTITY_MATRIX
        )
        staged = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"), 913, IDENTITY_MATRIX
        )
        self.stock_log.write_text(stock, encoding="utf-8")
        self.staged_log.write_text(staged, encoding="utf-8")
        self.write_sidecars()
        self.assertTrue(self.analyze()["ok"])

    def test_texture_flags_without_matrix_reject_the_run(self) -> None:
        text = append_draw_fields(
            self.staged_log.read_text(encoding="utf-8"), " tmflags=2"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_texture_matrix_missing")

    def test_texture_matrix_without_flags_rejects_the_run(self) -> None:
        text = append_draw_fields(
            self.staged_log.read_text(encoding="utf-8"), " tm0=913"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_texture_flags_missing")

    def test_unknown_texture_matrix_rejects_the_run(self) -> None:
        text = append_draw_fields(
            self.staged_log.read_text(encoding="utf-8"), " tm0=? tmflags=2"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_unknown_matrix")

    def test_missing_texture_matrix_record_rejects_the_run(self) -> None:
        text = append_draw_fields(
            self.staged_log.read_text(encoding="utf-8"), " tm0=999 tmflags=2"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_missing_matrix")

    def test_derived_texture_matrix_rejects_the_run(self) -> None:
        text = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"),
            913,
            IDENTITY_MATRIX,
            derived=True,
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_derived_matrix")

    def test_wrong_slot_texture_matrix_rejects_the_run(self) -> None:
        text = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"),
            913,
            IDENTITY_MATRIX,
            slot="world0",
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_texture_matrix_slot_mismatch")

    def test_invalid_texture_transform_flags_reject_the_run(self) -> None:
        text = add_texture_transform(
            self.staged_log.read_text(encoding="utf-8"),
            913,
            IDENTITY_MATRIX,
            flags="?",
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_texture_flags_invalid")

    def test_camera_must_hold_for_consecutive_frames(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8")
        text = text.replace(
            "M 911 proj m=",
            "M 999 proj m=2.000000,0.000000,0.000000,0.000000,0.000000,1.333333,0.000000,0.000000,0.000000,0.000000,1.000100,1.000000,0.000000,0.000000,-0.100010,0.000000\nM 911 proj m=",
        )
        marker = "D 211 0 DIP"
        before, after = text.split(marker, 1)
        after = after.replace(" p=911", " p=999", 1)
        self.staged_log.write_text(before + marker + after, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_common_stable_camera")

    def test_missing_index_digest_excludes_draw_and_fails_closed(self) -> None:
        lines = [line for line in self.staged_log.read_text(encoding="utf-8").splitlines()
                 if not line.startswith("G ") or " ib " not in line]
        self.staged_log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_attributable_staged_draws")

    def test_provisional_geometry_is_never_attributed(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(" stride=36 xyz", " stride=36 PROVISIONAL xyz")
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_attributable_staged_draws")

    def test_duplicate_draw_anchor_is_ambiguous_not_order_matched(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8")
        for frame in (210, 211, 212):
            block = []
            for line in text.splitlines():
                if line.startswith(f"D {frame} 0 ") or line.startswith(f"G {frame} 0 "):
                    block.append(line.replace(f"{frame} 0", f"{frame} 1", 1))
            insert = "\n".join(block) + "\n"
            text = text.replace(f"P {frame} draws=1", insert + f"P {frame} draws=2")
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_ambiguous_draw_identity")

    def test_bound_texture_without_content_hash_is_not_an_identity(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(":#93:h=1111111111111111", ":#93")
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_attributable_staged_draws")

    def test_viewport_is_part_of_the_draw_anchor(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            "vp=(0,0,640x480)", "vp=(0,0,320x240)"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_matched_draws")

    def test_texture_factor_is_part_of_the_draw_anchor(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            "tfactor=0xFFFFFFFF~", "tfactor=0x00000000"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_matched_draws")

    def test_missing_texture_factor_rejects_the_run(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            " tfactor=0xFFFFFFFF~", ""
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_tfactor_missing")

    def test_unknown_texture_factor_rejects_the_run(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            "tfactor=0xFFFFFFFF~", "tfactor=?"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_tfactor_invalid")

    def test_unidentified_shader_draw_is_never_attributed(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            "vs=0x00000000", "vs=0x12345678"
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_attributable_staged_draws")

    def test_unknown_material_state_is_never_a_matching_value(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace("cull=3", "cull=?")
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "no_attributable_staged_draws")

    def test_duplicate_geometry_record_rejects_instead_of_overwriting(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8")
        line = next(line for line in text.splitlines() if line.startswith("G 210 0 vb "))
        text = text.replace(line, line + "\n" + line, 1)
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_duplicate_geometry_record")

    def test_refusal_summary_is_required(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8").replace(
            "# refusals total=0 warnings=0\n", ""
        )
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_refusal_summary_missing")

    def test_detach_must_be_the_final_nonempty_log_line(self) -> None:
        text = self.staged_log.read_text(encoding="utf-8") + "AFTER DETACH\n"
        self.staged_log.write_text(text, encoding="utf-8")
        self.write_sidecars()
        self.assert_error(self.analyze(), "staged_log_not_terminal_detach")

    def test_failed_cli_still_writes_machine_readable_receipt(self) -> None:
        staged = sidecar("staged", self.staged_log)
        staged["guard"]["collision"] = True
        self.write_sidecars(staged=staged)
        output = self.root / "receipt.json"
        rc = subject.main([
            "--stock-log", str(self.stock_log),
            "--stock-run", str(self.stock_run),
            "--staged-log", str(self.staged_log),
            "--staged-run", str(self.staged_run),
            "--row-va", "0x00631E8C",
            "--min-stable-frames", "3",
            "--min-matched-draws", "1",
            "--output", str(output),
        ])
        self.assertEqual(rc, 1)
        written = json.loads(output.read_text(encoding="utf-8"))
        self.assertFalse(written["ok"])
        self.assertIn("staged_process_collision", written["error_codes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
