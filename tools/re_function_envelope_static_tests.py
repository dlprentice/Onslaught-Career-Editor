#!/usr/bin/env python3
"""Tests for re_function_envelope_static.py."""

from __future__ import annotations

import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "re_function_envelope_static.py"
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
GEN10 = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
    / "campaign-functions.tsv"
)

sys.path.insert(0, str(ROOT / "tools"))
import re_function_envelope_static as fes  # noqa: E402


class SyntheticEnvelopeTests(unittest.TestCase):
    def test_grade_proved_needs_external_call(self) -> None:
        env = {"ok": True, "bytes": 40, "reason": "single_ret"}
        g, _ = fes.grade_candidate(
            0x401000, True, [0x402000], [], [], [], env, None
        )
        self.assertEqual(g, "ENVELOPE_PROVED_STATIC")
        g2, _ = fes.grade_candidate(
            0x401000, True, [], [], [], [], env, 0x401000
        )
        self.assertEqual(g2, "ENTRY_SHAPE_NO_CALL_XREF")

    def test_no_prologue(self) -> None:
        env = {"ok": True, "bytes": 40, "reason": "single_ret"}
        g, _ = fes.grade_candidate(0x401000, False, [1], [], [], [], env, None)
        self.assertEqual(g, "NO_PROLOGUE")


@unittest.skipUnless(SPECIMEN.is_file() and GEN10.is_file(), "local evidence missing")
class LiveEnvelopeTests(unittest.TestCase):
    def test_fastsin_and_block_coeff_islands(self) -> None:
        spans = {
            "spans": [
                {
                    "startVa": "0x005b8e9e",
                    "endVa": "0x005bb9b0",
                    "prevFunc": "CFastVB__FastSinApprox_Scalar_005b8da0",
                    "nextFunc": "CDXTexture__InverseDct8x8_DequantAndStore_Scalar",
                    "candidates": [
                        "0x005b8e9e",
                        "0x005b8fb1",
                        "0x005b916c",
                        "0x005b99aa",
                        "0x005ba61c",
                        "0x005bad4c",
                        "0x005bb4b7",
                    ],
                },
                {
                    "startVa": "0x005ad820",
                    "endVa": "0x005ae190",
                    "prevFunc": "FUN_005ad600",
                    "nextFunc": "CDXTexture__InitBlockCoefficientHistory",
                    "candidates": [
                        "0x005ad820",
                        "0x005ad869",
                        "0x005ad9f2",
                        "0x005ada60",
                        "0x005adb60",
                        "0x005adbc6",
                        "0x005ade44",
                        "0x005adf50",
                    ],
                },
                {
                    "startVa": "0x005b4eb0",
                    "endVa": "0x005b5b80",
                    "prevFunc": "FUN_005b4b20",
                    "nextFunc": "CDXTexture__InitJpegDctQuantPipeline",
                    "candidates": ["0x005b4ed0", "0x005b5370"],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            spans_path = pathlib.Path(td) / "spans.json"
            out = pathlib.Path(td) / "out.json"
            spans_path.write_text(json.dumps(spans), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--specimen",
                    str(SPECIMEN),
                    "--spans-json",
                    str(spans_path),
                    "--gen10-functions-tsv",
                    str(GEN10),
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
            self.assertIn("FUNCTION_ENVELOPE_STATIC_OK", completed.stdout)
            payload = json.loads(
                completed.stdout.split("FUNCTION_ENVELOPE_STATIC_OK")[0].strip()
            )
            self.assertEqual(
                "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                payload["specimen_sha256"],
            )
            self.assertEqual(3, payload["n_spans"])
            # Primary claim under test: these islands do NOT get external E8 proof
            self.assertEqual(0, payload["n_spans_with_proved_envelope"])
            by_start = {s["startVa"]: s for s in payload["spanSummaries"]}
            # FastSin gap: prev body ends at span start; no external calls into span
            fs = by_start["0x005b8e9e"]
            self.assertTrue(fs["prevBodyEndsAtSpanStart"])
            self.assertEqual(0, fs["externalCallEdgesIntoSpan"])
            # Block-coeff gap: classic prologue at start after nop pad from prev
            bc = by_start["0x005ad820"]
            self.assertEqual(0, bc["externalCallEdgesIntoSpan"])
            # At least one candidate has single-ret shape without call xref
            shape = [
                c
                for s in payload["spanSummaries"]
                for c in s.get("bestCandidates") or []
                if c["grade"] == "ENTRY_SHAPE_NO_CALL_XREF"
            ]
            self.assertGreater(len(shape), 0)


if __name__ == "__main__":
    unittest.main()
