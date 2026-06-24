import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests_shared.fixture_paths import REPO_ROOT, SAVE_FIXTURE


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CliOptionsFileSafetyTests(unittest.TestCase):
    def test_bea_blocks_career_sections_by_default(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-options-safety-") as td:
            td_path = Path(td)
            input_bea = td_path / "defaultoptions.bea"
            output_bea = td_path / "defaultoptions_patched.bea"
            input_bea.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run([sys.executable, "patcher.py", str(input_bea), str(output_bea), "--rank", "S"])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Career section patching is blocked", result.stderr)
            self.assertFalse(output_bea.exists(), "Output should not be written when safety guard blocks.")

    def test_bea_settings_only_mode_is_allowed(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-options-settings-") as td:
            td_path = Path(td)
            input_bea = td_path / "defaultoptions.bea"
            output_bea = td_path / "defaultoptions_settings_only.bea"
            input_bea.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run(
                [
                    sys.executable,
                    "patcher.py",
                    str(input_bea),
                    str(output_bea),
                    "--no-nodes",
                    "--no-links",
                    "--no-goodies",
                    "--no-kills",
                    "--sound-volume",
                    "0.5",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_bea.exists())

    def test_bea_override_flag_allows_career_sections(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-options-override-") as td:
            td_path = Path(td)
            input_bea = td_path / "defaultoptions.bea"
            output_bea = td_path / "defaultoptions_override.bea"
            input_bea.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run(
                [
                    sys.executable,
                    "patcher.py",
                    str(input_bea),
                    str(output_bea),
                    "--allow-career-sections-on-options-file",
                    "--rank",
                    "S",
                    "--kills",
                    "100",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_bea.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
