#!/usr/bin/env python3
"""Tests for ghidra_pausemenu_render_wave481_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_pausemenu_render_wave481_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PauseMenuRenderWave481ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=2 created=0 would_create=0 renamed=0 "
                "would_rename=1 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_SUMMARIES["apply_pausemenu_render_wave481_dry.log"])

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

            write(
                base / "post_xrefs.tsv",
                "\n".join(
                    [
                        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                        "004d11d0\tCPauseMenu__Render\t0053ee24\t0053ecc0\tCDXEngine__PostRender\tUNCONDITIONAL_CALL",
                        "004d11d0\tCPauseMenu__Render\t0051f71d\t0051f700\tCFEPOptions__Update\tUNCONDITIONAL_CALL",
                        "004a4810\tCMenuItemRange__Render\t004d13f3\t004d11d0\tCPauseMenu__Render\tUNCONDITIONAL_CALL",
                    ]
                )
                + "\n",
            )

            write(
                base / "post_instructions.tsv",
                "\n".join(
                    [
                        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type",
                        "0x004d11d0\t0x004d11d0\tAFTER\t3\t0x004d11d5\t0x004d11d0\tCPauseMenu__Render\tMOV\tESI, ECX\t\t",
                        "0x004d11d0\t0x004d11d0\tAFTER\t273\t0x004d154d\t0x004d11d0\tCPauseMenu__Render\tCALL\t0x004e5c90\t\t",
                        "0x004d11d0\t0x004d11d0\tAFTER\t275\t0x004d1554\t0x004d11d0\tCPauseMenu__Render\tCALL\t0x004a4810\t\t",
                        "0x004d11d0\t0x004d11d0\tAFTER\t303\t0x004d15ad\t0x004d11d0\tCPauseMenu__Render\tCALL\t0x00523a70\t\t",
                    ]
                )
                + "\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
