#!/usr/bin/env python3
"""Focused fail-closed tests for the retired CRT canary owner."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

try:
    import ghidra_crt_canary_refutation as owner
except ModuleNotFoundError:  # supports ``python -m unittest`` from repository root
    from tools import ghidra_crt_canary_refutation as owner


class CrtCanaryRefutationTests(unittest.TestCase):
    def test_tracked_cli_refuses_retired_historical_topology(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            with redirect_stdout(output):
                result = owner.main(
                    ["--verify-ready", str(Path(temporary) / "proof.ready.json")]
                )
        self.assertEqual(1, result)
        self.assertIn("frozen Windows-era one-shot", output.getvalue())
        self.assertIn("never substitute the active mutable", output.getvalue())

    def test_direct_verifier_is_also_fail_closed(self) -> None:
        with self.assertRaisesRegex(owner.RefutationError, "package catalog"):
            owner.verify_ready(Path("unused.ready.json"), live_readback=False)


if __name__ == "__main__":
    unittest.main()
