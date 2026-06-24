import tempfile
import unittest
from pathlib import Path

from onslaught.core.cardid_preset import (
    BEGIN_MARKER,
    END_MARKER,
    STATE_APPLIED,
    STATE_MALFORMED,
    apply_modern_preset,
    build_backup_path,
    restore_from_backup,
    verify_file,
)


class CardIdPresetTests(unittest.TestCase):
    def test_apply_then_restore_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix="onslaught-cardid-py-") as td:
            cardid = Path(td) / "cardid.txt"
            original = "HeaderLine\n"
            cardid.write_text(original, encoding="utf-8")

            ok, msg = apply_modern_preset(cardid)
            self.assertTrue(ok, msg)
            self.assertIn("preset apply complete", msg)

            ok, msg, state = verify_file(cardid)
            self.assertTrue(ok, msg)
            self.assertEqual(state, STATE_APPLIED)

            backup = build_backup_path(cardid)
            self.assertTrue(backup.exists())
            self.assertEqual(backup.read_text(encoding="utf-8"), original)

            ok, msg = restore_from_backup(cardid)
            self.assertTrue(ok, msg)
            self.assertEqual(cardid.read_text(encoding="utf-8"), original)

    def test_apply_rejects_malformed_markers(self):
        with tempfile.TemporaryDirectory(prefix="onslaught-cardid-malformed-py-") as td:
            cardid = Path(td) / "cardid.txt"
            cardid.write_text(f"{BEGIN_MARKER}\nBROKEN\n", encoding="utf-8")

            ok, msg = apply_modern_preset(cardid)
            self.assertFalse(ok)
            self.assertIn("malformed managed markers", msg)

            ok, msg, state = verify_file(cardid)
            self.assertTrue(ok, msg)
            self.assertEqual(state, STATE_MALFORMED)

            self.assertFalse(build_backup_path(cardid).exists())

    def test_apply_is_idempotent_no_duplicate_markers(self):
        with tempfile.TemporaryDirectory(prefix="onslaught-cardid-idempotent-py-") as td:
            cardid = Path(td) / "cardid.txt"
            cardid.write_text("HeaderLine\n", encoding="utf-8")

            ok, msg = apply_modern_preset(cardid)
            self.assertTrue(ok, msg)

            ok, msg = apply_modern_preset(cardid)
            self.assertTrue(ok, msg)
            self.assertIn("No changes needed", msg)

            text = cardid.read_text(encoding="utf-8")
            self.assertEqual(text.count(BEGIN_MARKER), 1)
            self.assertEqual(text.count(END_MARKER), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
