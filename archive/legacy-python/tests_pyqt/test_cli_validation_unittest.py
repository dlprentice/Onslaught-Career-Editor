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


class CliValidationRegressionTests(unittest.TestCase):
    def test_invalid_level_rank_entry_is_fatal(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-invalid-rank-") as td:
            td_path = Path(td)
            input_path = td_path / "input.bes"
            output_path = td_path / "output.bes"
            input_path.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run(
                [
                    sys.executable,
                    "patcher.py",
                    str(input_path),
                    str(output_path),
                    "--level-rank",
                    "bad",
                    "--no-links",
                    "--no-goodies",
                    "--no-kills",
                ]
            )

            self.assertNotEqual(result.returncode, 0, msg="CLI should fail for invalid --level-rank entry")
            self.assertIn("Invalid --level-rank entry", result.stderr)
            self.assertFalse(output_path.exists(), msg="Output file should not be written on argument validation failure")

    def test_copy_options_flags_conflict_is_fatal(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-copy-options-conflict-") as td:
            td_path = Path(td)
            input_path = td_path / "input.bes"
            output_path = td_path / "output.bes"
            input_path.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run(
                [
                    sys.executable,
                    "patcher.py",
                    str(input_path),
                    str(output_path),
                    "--copy-options-from",
                    str(input_path),
                    "--no-copy-options-entries",
                    "--no-copy-options-tail",
                ]
            )

            self.assertNotEqual(
                result.returncode, 0, msg="CLI should fail when both no-copy options are set with --copy-options-from"
            )
            self.assertIn("both --no-copy-options-entries and --no-copy-options-tail", result.stderr)
            self.assertFalse(output_path.exists(), msg="Output file should not be written on argument validation failure")


if __name__ == "__main__":
    unittest.main(verbosity=2)
