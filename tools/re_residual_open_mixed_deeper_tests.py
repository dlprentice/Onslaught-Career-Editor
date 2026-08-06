#!/usr/bin/env python3
"""Unit tests for re_residual_open_mixed_deeper.py."""

from __future__ import annotations

import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_residual_open_mixed_deeper.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
STILL_OPEN = (
    ROOT
    / "local-lab"
    / "residual-mixed-static-batch-20260804-v1"
    / "still-open.tsv"
)

# Import helpers for synthetic tests
sys.path.insert(0, str(ROOT / "tools"))
import re_residual_open_mixed_deeper as deeper  # noqa: E402


class SyntheticDeeperTests(unittest.TestCase):
    def test_tiny_pad_gap(self) -> None:
        blob = b"\x90\xcc\x00\x90"
        r = deeper.analyze_span(0x401000, blob, "UNRESOLVED_MIXED", "A", "B", None)
        self.assertTrue(r["wholeSpanTerminal"])
        self.assertEqual(r["primary"], "TINY_PAD_GAP")
        self.assertEqual(r["subspans"][0]["kind"], "TINY_PAD_GAP")

    def test_code_address_table_prefix(self) -> None:
        # 12 code pointers into .text then garbage
        ptrs = b"".join(struct.pack("<I", 0x005BE628 + i * 4) for i in range(12))
        # Non-decodable junk tail (0xFF run) so remainder stays open.
        blob = ptrs + b"\xff" * 32
        r = deeper.analyze_span(0x005C9C69, blob, "UNRESOLVED_MIXED", "H", "D", None)
        kinds = [s["kind"] for s in r["subspans"]]
        self.assertIn("CODE_ADDRESS_TABLE_PREFIX", kinds)
        self.assertGreaterEqual(r["terminalBytes"], 48)
        self.assertFalse(r["wholeSpanTerminal"])  # tail remains
        self.assertEqual(r["startVa"], "0x005c9c69")

    def test_float_table_prefix(self) -> None:
        floats = b"".join(struct.pack("<f", 0.1 * (i + 1)) for i in range(16))
        r = deeper.analyze_span(0x500000, floats, "UNRESOLVED_MIXED", "X", "Y", None)
        kinds = [s["kind"] for s in r["subspans"]]
        self.assertIn("FLOAT32_TABLE_PREFIX", kinds)
        self.assertTrue(r["wholeSpanTerminal"])

    def test_denormal_junk_not_float_table(self) -> None:
        # Pattern like post-HResult residual: ascending bytes + high junk
        blob = bytes(range(16)) + b"\xf2\x5b\x00\x1d" * 4
        r = deeper.analyze_span(0x005C9E59, blob, "UNRESOLVED_MIXED", "H", "D", None)
        kinds = [s["kind"] for s in r["subspans"]]
        self.assertNotIn("FLOAT32_TABLE_PREFIX", kinds)


@unittest.skipUnless(SPECIMEN.is_file() and STILL_OPEN.is_file(), "local evidence missing")
class LiveDeeperTests(unittest.TestCase):
    def test_live_open_mixed_deeper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "out.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--still-open-tsv",
                    str(STILL_OPEN),
                    "--json-out",
                    str(out),
                    "--summary-only",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertIn("RESIDUAL_OPEN_MIXED_DEEPER_OK", completed.stdout)
            payload = json.loads(completed.stdout.split("RESIDUAL_OPEN_MIXED_DEEPER_OK")[0].strip())
            self.assertEqual(720, payload["n_open_input"])
            self.assertEqual(
                "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                payload["specimen_sha256"],
            )
            # HResult post-body residual must expose code-address table prefix
            hr = payload.get("hresult_post_body_residual")
            self.assertIsNotNone(hr)
            self.assertEqual(hr["startVa"].lower(), "0x005c9c69")
            self.assertEqual(26743, hr["bytes"])
            kinds = [s["kind"] for s in hr.get("subspans") or []]
            self.assertIn("CODE_ADDRESS_TABLE_PREFIX", kinds)
            prefix = next(
                s for s in hr["subspans"] if s["kind"] == "CODE_ADDRESS_TABLE_PREFIX"
            )
            self.assertGreaterEqual(prefix["bytes"], 496)
            # Deeper pass must account for some terminal bytes without closing all
            self.assertGreater(payload["terminal_bytes_accounted"], 0)
            self.assertGreater(payload["open_bytes_remaining"], 0)
            self.assertLess(payload["n_whole_span_terminal"], payload["n_open_input"])


if __name__ == "__main__":
    unittest.main()
