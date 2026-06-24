#!/usr/bin/env python3
"""Tests for ghidra_audio_reset_wave480_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_audio_reset_wave480_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class AudioResetWave480ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=2 created=0 would_create=0 renamed=0 "
                "would_rename=1 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_SUMMARIES["apply_audio_reset_wave480_dry.log"])

    def test_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for filename, summary in probe.EXPECTED_SUMMARIES.items():
                write(
                    base / filename,
                    "REPORT: Save succeeded\n"
                    + " ".join(f"{key}={value}" for key, value in summary.items())
                    + "\n",
                )

            metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
            tag_lines = ["address\tname\ttags\tstatus"]
            for address, expected in probe.EXPECTED_METADATA.items():
                metadata_lines.append(
                    f"{address}\t{expected['name']}\t{expected['signature']}\t"
                    f"{' '.join(expected['comment_tokens'])}\tOK"
                )
                tag_lines.append(f"{address}\t{expected['name']}\t{';'.join(sorted(expected['tags']))}\tOK")
                write(
                    base / "post-decomp" / f"{address[2:]}_{expected['name']}.c",
                    "\n".join(expected["decompile_tokens"]) + "\n",
                )
            write(base / "post_metadata.tsv", "\n".join(metadata_lines) + "\n")
            write(base / "post_tags.tsv", "\n".join(tag_lines) + "\n")

            xref_lines = [
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                *[
                    f"{target[2:]}\tname\t{from_addr[2:]}\t<none>\t{from_function}\tUNCONDITIONAL_CALL"
                    for target, from_addr, from_function in sorted(probe.EXPECTED_XREFS)
                ],
            ]
            write(base / "post_xrefs.tsv", "\n".join(xref_lines) + "\n")

            header = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"
            post_rows = [
                f"{addr}\t{addr}\tTARGET\t0\t{addr}\t{addr}\tfn\t{mnemonic}\t{operands}\t\t"
                for addr, (mnemonic, operands) in probe.EXPECTED_POST_INSTRUCTIONS.items()
            ]
            raw_rows = [
                f"{addr}\t{addr}\tTARGET\t0\t{addr}\t<none>\t<no_function>\t{mnemonic}\t{operands}\t\t"
                for addr, (mnemonic, operands) in probe.EXPECTED_RAW_CALLS.items()
            ]
            write(base / "post_instructions.tsv", header + "\n" + "\n".join(post_rows) + "\n")
            write(base / "raw_audio_callsite_ranges.tsv", header + "\n" + "\n".join(raw_rows) + "\n")

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
