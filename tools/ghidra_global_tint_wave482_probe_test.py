#!/usr/bin/env python3
"""Tests for ghidra_global_tint_wave482_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_global_tint_wave482_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class GlobalTintWave482ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=1 created=0 would_create=0 renamed=0 "
                "would_rename=0 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_SUMMARIES["apply_global_tint_wave482_dry.log"])

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

            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.TARGET}\t{probe.TARGET_NAME}\t{probe.EXPECTED_SIGNATURE}\t"
                f"{' '.join(probe.COMMENT_TOKENS)}\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\tstatus\n"
                f"{probe.TARGET}\t{probe.TARGET_NAME}\t{';'.join(sorted(probe.EXPECTED_TAGS))}\tOK\n",
            )
            write(
                base / "post-decomp" / f"{probe.TARGET[2:]}_{probe.TARGET_NAME}.c",
                "\n".join(probe.DECOMPILE_TOKENS) + "\n",
            )

            xrefs = ["target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type"]
            for from_addr, from_function in sorted(probe.EXPECTED_XREFS):
                xrefs.append(f"{probe.TARGET}\t{probe.TARGET_NAME}\t{from_addr}\t0x00400000\t{from_function}\tUNCONDITIONAL_CALL")
            write(base / "post_xrefs.tsv", "\n".join(xrefs) + "\n")

            instruction_rows = [
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type",
                f"{probe.TARGET}\t{probe.TARGET}\tTARGET\t0\t0x004d1710\t{probe.TARGET}\t{probe.TARGET_NAME}\tMOV\tEAX, dword ptr [ESP + 0x4]\t\t",
                f"{probe.TARGET}\t{probe.TARGET}\tAFTER\t1\t0x004d1714\t{probe.TARGET}\t{probe.TARGET_NAME}\tMOV\tdword ptr [0x0082b4ec], 0xff\t\t",
                f"{probe.TARGET}\t{probe.TARGET}\tAFTER\t2\t0x004d171e\t{probe.TARGET}\t{probe.TARGET_NAME}\tMOV\t[0x0082b494], EAX\t\t",
                f"{probe.TARGET}\t{probe.TARGET}\tAFTER\t3\t0x004d1723\t{probe.TARGET}\t{probe.TARGET_NAME}\tRET\t\t\t",
            ]
            write(base / "post_instructions.tsv", "\n".join(instruction_rows) + "\n")

            callsite_rows = ["target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type"]
            for call_addr, pushed_value in probe.EXPECTED_CALLSITE_PUSHES.items():
                callsite_rows.append(f"{call_addr}\t{call_addr}\tBEFORE\t-1\t0x00000001\t0x00400000\tcaller\tPUSH\t{pushed_value}\t\t")
                callsite_rows.append(f"{call_addr}\t{call_addr}\tTARGET\t0\t{call_addr}\t0x00400000\tcaller\tCALL\t{probe.TARGET}\t\t")
            write(base / "callsite_instructions.tsv", "\n".join(callsite_rows) + "\n")

            write(
                base / "global_operand_refs.tsv",
                "token\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                f"0x0082b4ec\t0x004d1714\t{probe.TARGET}\t{probe.TARGET_NAME}\tMOV\tdword ptr [0x0082b4ec], 0xff\t\t\n"
                f"0x0082b494\t0x004d171e\t{probe.TARGET}\t{probe.TARGET_NAME}\tMOV\t[0x0082b494], EAX\t\t\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
