import tempfile
import unittest
from pathlib import Path


class BinaryPatchesTests(unittest.TestCase):
    def _seed_exe(self, path: Path, include_optional: bool = True) -> bytes:
        from onslaught.core.binary_patches import PATCH_SPECS

        max_end = 0
        for spec in PATCH_SPECS:
            if spec.optional and not include_optional:
                continue
            end = spec.file_offset + len(spec.original)
            if end > max_end:
                max_end = end
        size = max_end + 0x100
        data = bytearray([0x90] * size)
        for spec in PATCH_SPECS:
            if spec.optional and not include_optional:
                continue
            start = spec.file_offset
            end = start + len(spec.original)
            data[start:end] = spec.original
        original = bytes(data)
        path.write_bytes(original)
        return original

    def test_apply_then_restore_roundtrip(self):
        from onslaught.core.binary_patches import (
            PATCH_SPECS,
            apply_patches_to_file,
            build_backup_path,
            restore_from_backup,
        )

        with tempfile.TemporaryDirectory(prefix="onslaught-binary-patches-") as td:
            exe = Path(td) / "BEA.exe"
            original = self._seed_exe(exe, include_optional=False)

            selected = [spec for spec in PATCH_SPECS if not spec.optional]
            ok, msg = apply_patches_to_file(exe, selected)
            self.assertTrue(ok, msg)
            self.assertIn("Patch apply complete.", msg)

            patched = exe.read_bytes()
            for spec in selected:
                self.assertEqual(
                    patched[spec.file_offset : spec.file_offset + len(spec.patched)],
                    spec.patched,
                    f"Patched bytes mismatch for {spec.key}",
                )

            backup = build_backup_path(exe)
            self.assertTrue(backup.exists(), "Backup must be created on first apply.")
            self.assertEqual(backup.read_bytes(), original, "Backup should contain original bytes.")

            ok, msg = restore_from_backup(exe)
            self.assertTrue(ok, msg)
            self.assertEqual(exe.read_bytes(), original, "Restore should return file to original bytes.")

    def test_apply_aborts_on_unexpected_bytes(self):
        from onslaught.core.binary_patches import (
            PATCH_SPECS,
            apply_patches_to_file,
            build_backup_path,
        )

        with tempfile.TemporaryDirectory(prefix="onslaught-binary-patches-mismatch-") as td:
            exe = Path(td) / "BEA.exe"
            self._seed_exe(exe, include_optional=False)

            # Corrupt one selected patch region so verify/apply must abort.
            exe_data = bytearray(exe.read_bytes())
            exe_data[PATCH_SPECS[0].file_offset] = 0x41
            exe.write_bytes(exe_data)

            selected = [spec for spec in PATCH_SPECS if not spec.optional]
            ok, msg = apply_patches_to_file(exe, selected)
            self.assertFalse(ok)
            self.assertIn("Apply aborted", msg)
            self.assertIn("unexpected bytes", msg)
            self.assertFalse(build_backup_path(exe).exists(), "No backup should be created when apply aborts.")

    def test_render_report_includes_track_labels(self):
        from onslaught.core.binary_patches import PATCH_SPECS, render_state_report, verify_patch_specs

        with tempfile.TemporaryDirectory(prefix="onslaught-binary-patches-report-") as td:
            exe = Path(td) / "BEA.exe"
            self._seed_exe(exe, include_optional=True)
            data = exe.read_bytes()
            _, _, rows = verify_patch_specs(data, PATCH_SPECS)
            report = render_state_report(exe, rows, "summary")
            self.assertIn("Stable |", report)
            self.assertIn("Experimental |", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
