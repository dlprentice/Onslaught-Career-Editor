#!/usr/bin/env python3
"""Tests for ghidra_controller_target_wave479_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_controller_target_wave479_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ControllerTargetWave479ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=1 created=0 would_create=0 renamed=0 "
                "would_rename=1 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_SUMMARIES["apply_controller_target_wave479_dry.log"])

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

            comment = " ".join(probe.COMMENT_TOKENS)
            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.TARGET_ADDR}\t{probe.NEW_NAME}\t{probe.EXPECTED_SIGNATURE}\t{comment}\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\tstatus\n"
                f"{probe.TARGET_ADDR}\t{probe.NEW_NAME}\t{';'.join(sorted(probe.EXPECTED_TAGS))}\tOK\n",
            )
            xref_lines = [
                f"{target[2:]}\t{probe.NEW_NAME}\t{from_addr[2:]}\t<none>\t{from_function}\tUNCONDITIONAL_CALL"
                for target, from_addr, from_function in sorted(probe.EXPECTED_XREFS)
            ]
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                + "\n".join(xref_lines)
                + "\n",
            )
            write(
                base / "post-decomp" / f"{probe.TARGET_ADDR[2:]}_{probe.NEW_NAME}.c",
                "void __fastcall GameControllers__RelinquishControlForTarget(void *controlled_target) {\n"
                "  void *pvVar1; int number; number = 0;\n"
                "  pvVar1 = CGame__GetController(&DAT_008a9a98,number);\n"
                "  pvVar1 = CController__GetToControl(pvVar1);\n"
                "  if (pvVar1 == controlled_target) CController__RelinquishControl(pvVar1);\n"
                "  while (number < 2) {}\n"
                "}\n",
            )
            write(
                base / "controller_target_post_range.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                + "\n".join(f"{addr[2:]}\t\t{mnemonic}\t{operands}" for addr, (mnemonic, operands) in probe.EXPECTED_INSTRUCTION_ROWS.items())
                + "\n",
            )
            write(
                base / "raw_callsite_0048ff80_00490010.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                + "\n".join(f"{addr[2:]}\t\t{mnemonic}\t{operands}" for addr, (mnemonic, operands) in probe.EXPECTED_RAW_CALLSITE_ROWS.items())
                + "\n",
            )
            write(
                base / "controller_context_instructions.tsv",
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                + "\n".join(
                    f"{addr}\t{addr}\tTARGET\t0\t{addr}\t{addr}\tfn\t{mnemonic}\t{operands}\t\t"
                    for addr, (mnemonic, operands) in probe.EXPECTED_CONTEXT_ROWS.items()
                )
                + "\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
