import os
import re
import subprocess
import sys
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


def _detect_dotnet() -> str | None:
    env_override = os.environ.get("DOTNET_EXE")
    if env_override and Path(env_override).exists():
        return env_override

    for candidate in (
        Path("/mnt/c/Program Files/dotnet/dotnet.exe"),
        Path("/usr/bin/dotnet"),
        Path("/usr/local/bin/dotnet"),
    ):
        if candidate.exists():
            return str(candidate)
    return None


def _to_windows_path(path: Path) -> str:
    s = str(path)
    if s.startswith("/mnt/") and len(s) > 6:
        drive = s[5]
        rest = s[7:] if s[6] == "/" else s[6:]
        rest = rest.replace("/", "\\")
        return f"{drive.upper()}:\\{rest}"
    return s


def _parse_summary(stdout: str) -> tuple[int, int, int, int, int, int]:
    unlocked = re.search(r"Unlocked:\s+(\d+)/233\s+\(NEW\s+(\d+),\s+OLD\s+(\d+)\)", stdout)
    locked = re.search(r"Locked:\s+(\d+)", stdout)
    instructions = re.search(r"Instructions:\s+(\d+)", stdout)
    reserved = re.search(r"Reserved slots:\s+(\d+)", stdout)

    if not unlocked or not locked or not instructions or not reserved:
        raise AssertionError("Missing one or more expected summary lines.")

    return (
        int(unlocked.group(1)),
        int(unlocked.group(2)),
        int(unlocked.group(3)),
        int(locked.group(1)),
        int(instructions.group(1)),
        int(reserved.group(1)),
    )


class CliGoodieListRegressionTests(unittest.TestCase):
    def _run_python_list_goodies(self, show_reserved: bool) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, "patcher.py", "--list-goodies", str(SAVE_FIXTURE)]
        if show_reserved:
            cmd.append("--show-reserved-goodies")
        return _run(cmd)

    def _run_csharp_list_goodies(self, show_reserved: bool) -> subprocess.CompletedProcess[str]:
        dotnet = _detect_dotnet()
        if dotnet is None:
            self.skipTest("dotnet runtime not found for C# CLI parity test.")

        cmd = [
            dotnet,
            "run",
            "--project",
            "Onslaught - Career Editor.csproj",
            "--",
            _to_windows_path(SAVE_FIXTURE),
            "--list-goodies",
        ]
        if show_reserved:
            cmd.append("--show-reserved-goodies")
        return _run(cmd)

    def test_python_list_goodies_default_hides_reserved_rows(self):
        result = self._run_python_list_goodies(show_reserved=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Display mode: displayable slots (0-232)", result.stdout)
        self.assertIn("Reserved rows hidden; use --show-reserved-goodies to include them.", result.stdout)
        self.assertRegex(result.stdout, r"(?m)^\s*232\s+0x22E6\s+", msg="Expected slot 232 row")
        self.assertNotRegex(result.stdout, r"(?m)^\s*233\s+0x22EA\s+", msg="Reserved slot 233 should be hidden")

    def test_python_list_goodies_with_reserved_shows_tail_rows(self):
        result = self._run_python_list_goodies(show_reserved=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Display mode: all 300 slots", result.stdout)
        self.assertRegex(result.stdout, r"(?m)^\s*299\s+0x23F2\s+", msg="Expected slot 299 row")
        self.assertNotIn("Reserved rows hidden; use --show-reserved-goodies to include them.", result.stdout)

    def test_csharp_list_goodies_default_hides_reserved_rows(self):
        result = self._run_csharp_list_goodies(show_reserved=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Display mode: displayable slots (0-232)", result.stdout)
        self.assertRegex(result.stdout, r"(?m)^\s*232\s+0x22E6\s+", msg="Expected slot 232 row")
        self.assertNotRegex(result.stdout, r"(?m)^\s*233\s+0x22EA\s+", msg="Reserved slot 233 should be hidden")

    def test_csharp_list_goodies_with_reserved_shows_tail_rows(self):
        result = self._run_csharp_list_goodies(show_reserved=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Display mode: all 300 slots", result.stdout)
        self.assertRegex(result.stdout, r"(?m)^\s*233\s+0x22EA\s+", msg="Expected slot 233 row when reserved are shown")
        self.assertRegex(result.stdout, r"(?m)^\s*299\s+0x23F2\s+", msg="Expected slot 299 row")

    def test_csharp_python_list_goodies_summary_parity(self):
        for show_reserved in (False, True):
            with self.subTest(show_reserved=show_reserved):
                py = self._run_python_list_goodies(show_reserved=show_reserved)
                cs = self._run_csharp_list_goodies(show_reserved=show_reserved)

                self.assertEqual(py.returncode, 0, msg=py.stderr)
                self.assertEqual(cs.returncode, 0, msg=cs.stderr)
                self.assertEqual(_parse_summary(py.stdout), _parse_summary(cs.stdout))


if __name__ == "__main__":
    unittest.main(verbosity=2)
