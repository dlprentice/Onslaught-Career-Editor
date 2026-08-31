#!/usr/bin/env python3
"""Focused tests for the Windows-only command guard."""

from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

import require_windows_host


class RequireWindowsHostTests(unittest.TestCase):
    def test_windows_host_passes_without_output(self) -> None:
        error = io.StringIO()
        with (
            mock.patch.object(require_windows_host.os, "name", "nt"),
            contextlib.redirect_stderr(error),
        ):
            self.assertEqual(0, require_windows_host.main())
        self.assertEqual("", error.getvalue())

    def test_non_windows_host_fails_with_vm_route(self) -> None:
        error = io.StringIO()
        with (
            mock.patch.object(require_windows_host.os, "name", "posix"),
            contextlib.redirect_stderr(error),
        ):
            self.assertEqual(2, require_windows_host.main())
        self.assertIn("configured isolated Windows VM", error.getvalue())
        self.assertIn("not native WinUI", error.getvalue())


if __name__ == "__main__":
    unittest.main()
