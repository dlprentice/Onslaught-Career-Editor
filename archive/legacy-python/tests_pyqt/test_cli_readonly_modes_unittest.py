import re
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


class CliReadOnlyModesTests(unittest.TestCase):
    def test_version_flag(self):
        result = _run([sys.executable, "patcher.py", "--version"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertRegex(result.stdout.strip(), r"^2\.0\.0(?:\+[0-9a-f]{40})?$")

    def test_analyze_read_only_mode(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")
        result = _run([sys.executable, "patcher.py", str(SAVE_FIXTURE), "--analyze"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("SAVE FILE ANALYSIS", result.stdout)
        self.assertIn("OPTIONS (bindings + tail snapshot)", result.stdout)

    def test_compare_read_only_mode(self):
        self.assertTrue(SAVE_FIXTURE.exists(), f"Missing fixture: {SAVE_FIXTURE}")

        with tempfile.TemporaryDirectory(prefix="onslaught-cli-compare-") as td:
            td_path = Path(td)
            left = td_path / "left.bes"
            right = td_path / "right.bes"
            left.write_bytes(SAVE_FIXTURE.read_bytes())
            right.write_bytes(SAVE_FIXTURE.read_bytes())

            result = _run([sys.executable, "patcher.py", str(left), "--compare", str(right)])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("COMPARISON", result.stdout)
            self.assertIn("Files are identical!", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
