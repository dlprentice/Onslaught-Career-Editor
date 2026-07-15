#!/usr/bin/env python3
"""Focused tests for shared native WinUI acceptance support."""

from __future__ import annotations

import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import winui_native_acceptance_support as support


class NativeAcceptanceSupportTests(unittest.TestCase):
    METHOD = "ExpectedNativeMethod"

    def write_trx(
        self,
        root: Path,
        *,
        total: int = 1,
        executed: int = 1,
        passed: int = 1,
        not_executed: int = 0,
        outcome: str = "Passed",
        method: str | None = None,
    ) -> Path:
        path = root / "native.trx"
        path.write_text(
            f"""<?xml version="1.0" encoding="utf-8"?>
<TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
  <Results>
    <UnitTestResult testName="{method or self.METHOD}" outcome="{outcome}" />
  </Results>
  <ResultSummary outcome="{outcome}">
    <Counters total="{total}" executed="{executed}" passed="{passed}"
      failed="0" error="0" timeout="0" aborted="0" inconclusive="0"
      notExecuted="{not_executed}" />
  </ResultSummary>
</TestRun>
""",
            encoding="utf-8",
        )
        return path

    def test_validate_exact_trx_accepts_one_named_passing_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = support.validate_exact_trx(
                self.write_trx(Path(temp_dir)),
                self.METHOD,
                "native fixture",
            )

        self.assertEqual(1, summary["total"])
        self.assertEqual(1, summary["passed"])

    def test_validate_exact_trx_rejects_skipped_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trx = self.write_trx(
                Path(temp_dir),
                executed=0,
                passed=0,
                not_executed=1,
                outcome="NotExecuted",
            )
            with self.assertRaisesRegex(
                support.NativeAcceptanceError,
                "exactly one executed passing test",
            ):
                support.validate_exact_trx(trx, self.METHOD, "native fixture")

    def test_png_dimensions_reads_only_valid_png_ihdr(self) -> None:
        signature = bytes((137, 80, 78, 71, 13, 10, 26, 10))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            path.write_bytes(signature + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 760, 820))
            self.assertEqual((760, 820), support.png_dimensions(path))

            path.write_bytes(bytes(24))
            with self.assertRaisesRegex(support.NativeAcceptanceError, "not PNG"):
                support.png_dimensions(path)

    def test_decode_png_rgba_reconstructs_filtered_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            expected = self._write_rgba_png(path, 8, 6, toolkit_frame=False)

            decoded = support.decode_png_rgba(path)

        self.assertEqual((8, 6), (decoded.width, decoded.height))
        self.assertEqual(expected, decoded.pixels)

    def test_decode_png_rgba_reconstructs_all_standard_filter_types(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "filters.png"
            expected = self._write_filtered_rgba_png(path)

            decoded = support.decode_png_rgba(path)

        self.assertEqual((8, 5), (decoded.width, decoded.height))
        self.assertEqual(expected, decoded.pixels)

    def test_decode_png_rgba_rejects_oversized_dimensions_before_inflate(self) -> None:
        def chunk(kind: bytes, payload: bytes) -> bytes:
            return (
                struct.pack(">I", len(payload))
                + kind
                + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "oversized.png"
            path.write_bytes(
                support.PNG_SIGNATURE
                + chunk(b"IHDR", struct.pack(">IIBBBBB", 100_000, 100_000, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b""))
                + chunk(b"IEND", b"")
            )

            with self.assertRaisesRegex(support.NativeAcceptanceError, "safety limits"):
                support.decode_png_rgba(path)

    def test_require_toolkit_visual_evidence_accepts_frame_and_marker_activity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            self._write_rgba_png(path, 760, 820, toolkit_frame=True)

            support.require_toolkit_visual_evidence(
                path,
                [(48, 210, 180, 80), (330, 500, 190, 120)],
                label="native fixture",
            )

    def test_require_toolkit_visual_evidence_rejects_flat_or_inactive_raster(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            self._write_rgba_png(path, 760, 820, toolkit_frame=False, flat=True)

            with self.assertRaisesRegex(support.NativeAcceptanceError, "visual coverage"):
                support.require_toolkit_visual_evidence(
                    path,
                    [(48, 210, 180, 80)],
                    label="native fixture",
                )

    def test_validate_invocation_id_requires_lowercase_32_hex(self) -> None:
        support.validate_invocation_id("0123456789abcdef0123456789abcdef")
        for invalid in ("ABC", "0123456789ABCDEF0123456789ABCDEF", "g" * 32):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(support.NativeAcceptanceError, "invocation ID"):
                    support.validate_invocation_id(invalid)

    def test_append_cleanup_error_preserves_primary_and_cleanup_context(self) -> None:
        error = support.append_cleanup_error(
            ValueError("primary"),
            "final census",
            RuntimeError("cleanup"),
        )

        self.assertIsInstance(error, support.NativeAcceptanceError)
        self.assertIn("primary", str(error))
        self.assertIn("final census failed: cleanup", str(error))

    def test_run_command_timeout_terminates_only_captured_spawn_identity(self) -> None:
        process = mock.Mock()
        process.pid = 4242
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired(["fixture"], 1), 0]
        identity = support.OwnedProcessIdentity(
            process_id=4242,
            start_time_utc_ticks=638881920000000000,
            executable_path=Path(r"C:\Program Files\dotnet\dotnet.exe"),
        )
        with mock.patch.object(support.subprocess, "Popen", return_value=process), mock.patch.object(
            support,
            "capture_owned_process_identity",
            return_value=identity,
        ) as capture, mock.patch.object(
            support,
            "terminate_owned_process_tree",
        ) as terminate:
            with self.assertRaises(subprocess.TimeoutExpired):
                support.run_command(
                    ["fixture"],
                    repo_root=Path.cwd(),
                    timeout=1,
                )

        capture.assert_called_once_with(4242, repo_root=Path.cwd())
        terminate.assert_called_once_with(identity, repo_root=Path.cwd())
        process.kill.assert_not_called()

    def test_tree_termination_binds_start_and_path_before_taskkill(self) -> None:
        identity = support.OwnedProcessIdentity(
            process_id=4242,
            start_time_utc_ticks=638881920000000000,
            executable_path=Path(r"C:\Program Files\dotnet\dotnet.exe"),
        )
        completed = subprocess.CompletedProcess([], 42, "", "")

        with mock.patch.object(support.subprocess, "run", return_value=completed) as run:
            with self.assertRaisesRegex(support.NativeAcceptanceError, "identity"):
                support.terminate_owned_process_tree(identity, repo_root=Path.cwd())

        command = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        script = command[-1]
        self.assertEqual(command[:4], ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"])
        self.assertLess(script.index("StartTime.ToUniversalTime().Ticks"), script.index("taskkill.exe"))
        self.assertLess(script.index("GetFullPath"), script.index("taskkill.exe"))
        self.assertEqual(environment["ONSLAUGHT_NATIVE_CLEANUP_PID"], "4242")
        self.assertEqual(environment["ONSLAUGHT_NATIVE_CLEANUP_PATH"], str(identity.executable_path))
        self.assertEqual(
            environment["ONSLAUGHT_NATIVE_CLEANUP_START_TICKS"],
            str(identity.start_time_utc_ticks),
        )

    def test_recursive_cleanup_rejects_nested_junction_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            owned = root / "owned"
            outside = root / "outside"
            owned.mkdir()
            outside.mkdir()
            canary = outside / "canary.txt"
            canary.write_text("preserve", encoding="utf-8")
            junction = owned / "nested"
            self._create_junction(junction, outside)
            try:
                with self.assertRaisesRegex(support.NativeAcceptanceError, "reparse point"):
                    support.remove_reparse_free_tree(owned, label="owned fixture")
                self.assertEqual(canary.read_text(encoding="utf-8"), "preserve")
                self.assertTrue(owned.is_dir())
            finally:
                junction.rmdir()

    @staticmethod
    def _create_junction(link: Path, target: Path) -> None:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)

    @staticmethod
    def _write_rgba_png(
        path: Path,
        width: int,
        height: int,
        *,
        toolkit_frame: bool,
        flat: bool = False,
    ) -> bytes:
        def pixel(x: int, y: int) -> tuple[int, int, int, int]:
            if flat:
                return (245, 245, 245, 255)
            if toolkit_frame and 40 <= y <= 115:
                return (32, 52, 154, 255)
            shade = ((x // 8) + (y // 8)) % 10
            return (250 - shade * 18, 250 - shade * 16, 250 - shade * 13, 255)

        rows = []
        pixels = bytearray()
        for y in range(height):
            row = bytearray()
            for x in range(width):
                rgba = pixel(x, y)
                row.extend(rgba)
                pixels.extend(rgba)
            rows.append(b"\x00" + bytes(row))

        def chunk(kind: bytes, payload: bytes) -> bytes:
            return (
                struct.pack(">I", len(payload))
                + kind
                + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
            )

        path.write_bytes(
            support.PNG_SIGNATURE
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows)))
            + chunk(b"IEND", b"")
        )
        return bytes(pixels)

    @staticmethod
    def _write_filtered_rgba_png(path: Path) -> bytes:
        width = 8
        height = 5
        bytes_per_pixel = 4
        raw_rows = []
        expected = bytearray()
        for y in range(height):
            row = bytearray()
            for x in range(width):
                rgba = ((x * 31 + y * 17) % 256, (x * 19 + y * 41) % 256, (x * 47 + y * 13) % 256, 255)
                row.extend(rgba)
                expected.extend(rgba)
            raw_rows.append(row)

        def paeth(left: int, above: int, upper_left: int) -> int:
            estimate = left + above - upper_left
            distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
            return (left, above, upper_left)[distances.index(min(distances))]

        filtered_rows = []
        for y, row in enumerate(raw_rows):
            filter_type = y
            prior = raw_rows[y - 1] if y > 0 else bytearray(len(row))
            encoded = bytearray()
            for index, value in enumerate(row):
                left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
                above = prior[index]
                upper_left = prior[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
                predictor = (
                    0
                    if filter_type == 0
                    else left
                    if filter_type == 1
                    else above
                    if filter_type == 2
                    else (left + above) // 2
                    if filter_type == 3
                    else paeth(left, above, upper_left)
                )
                encoded.append((value - predictor) & 0xFF)
            filtered_rows.append(bytes((filter_type,)) + bytes(encoded))

        def chunk(kind: bytes, payload: bytes) -> bytes:
            return (
                struct.pack(">I", len(payload))
                + kind
                + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
            )

        path.write_bytes(
            support.PNG_SIGNATURE
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(filtered_rows)))
            + chunk(b"IEND", b"")
        )
        return bytes(expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
