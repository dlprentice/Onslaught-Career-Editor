#!/usr/bin/env python3
"""Tests for the Wave472 CPlayer AssignBattleEngine probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cplayer_assign_wave472_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
DISASM_HEADER = "address\tbytes\tmnemonic\toperands\n"
CALLER_HEADER = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"


def write_fixture(root: Path, stale: bool = False) -> None:
    (root / "post-decomp").mkdir(parents=True)
    (root / "dry.log").write_text(
        "SUMMARY updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "apply.log").write_text(
        "SUMMARY updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "verify_dry.log").write_text(
        "SUMMARY updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    signature = probe.EXPECTED_SIGNATURE
    comment = " ".join(probe.COMMENT_TOKENS)
    tags = ";".join(probe.EXPECTED_TAGS)
    decompile = "\n".join(probe.DECOMPILE_TOKENS)
    if stale:
        signature = "void __thiscall CPlayer__AssignBattleEngine(void * this, void * param_1, void * param_2)"
        comment += " runtime behavior proven"
        tags = tags.replace("battleengine-reader", "")
        decompile = "param_1 param_2"
    (root / "post_metadata.tsv").write_text(
        METADATA_HEADER + f"{probe.ADDRESS}\t{probe.EXPECTED_NAME}\t{signature}\t{comment}\tOK\n",
        encoding="utf-8",
    )
    (root / "post_tags.tsv").write_text(
        TAGS_HEADER + f"{probe.ADDRESS}\t{probe.EXPECTED_NAME}\t{tags}\tOK\n",
        encoding="utf-8",
    )
    (root / "post-decomp" / f"{probe.ADDRESS[2:]}_{probe.EXPECTED_NAME}.c").write_text(decompile, encoding="utf-8")

    xref_rows = []
    for target, from_addr, from_function in probe.EXPECTED_XREF_EDGES:
        if stale and from_addr == "0x004703cb":
            continue
        xref_rows.append(f"{target}\t{probe.EXPECTED_NAME}\t{from_addr}\t0x00400000\t{from_function}\tUNCONDITIONAL_CALL\n")
    (root / "post_xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")

    disasm_rows = [
        "004d3080\t8B 44 24 04\tMOV\tEAX, dword ptr [ESP + 0x4]\n",
        "004d308e\tE8 6D DF F2 FF\tCALL\t0x00401000\n",
        "004d309c\tE8 5F DF F2 FF\tCALL\t0x00401000\n",
        "004d30ae\tFF 92 E0 00 00 00\tCALL\tdword ptr [EDX + 0xe0]\n",
        "004d30ba\tFF 90 54 01 00 00\tCALL\tdword ptr [EAX + 0x154]\n",
        "004d30c2\tC2 04 00\tRET\t0x4\n",
    ]
    if stale:
        disasm_rows[-1] = "004d30c2\tC3\tRET\t\n"
    (root / "post_disasm_range.tsv").write_text(DISASM_HEADER + "".join(disasm_rows), encoding="utf-8")

    caller_rows = []
    for callsite in sorted(probe.EXPECTED_CALLSITES):
        caller_rows.extend(
            [
                f"{callsite}\t{callsite}\tBEFORE\t-3\t0x00400001\t0x00400000\tcaller\tMOV\tEAX, dword ptr [EAX + 0x7c]\t\tFALL_THROUGH\n",
                f"{callsite}\t{callsite}\tBEFORE\t-2\t0x00400002\t0x00400000\tcaller\tPUSH\tEAX\t50\tFALL_THROUGH\n",
                f"{callsite}\t{callsite}\tBEFORE\t-1\t0x00400003\t0x00400000\tcaller\tMOV\tECX, dword ptr [EDI]\t\tFALL_THROUGH\n",
                f"{callsite}\t{callsite}\tTARGET\t0\t{callsite}\t0x00400000\tcaller\tCALL\t0x004d3080\t\tUNCONDITIONAL_CALL\n",
            ]
        )
    if stale:
        caller_rows = caller_rows[:-4]
    (root / "post_caller_instructions.tsv").write_text(CALLER_HEADER + "".join(caller_rows), encoding="utf-8")


class CPlayerAssignWave472ProbeTests(unittest.TestCase):
    def test_passes_for_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            status, failures = probe.run_checks(root)
        self.assertEqual(status, "PASS", failures)

    def test_fails_for_stale_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, stale=True)
            status, failures = probe.run_checks(root)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("expected signature" in failure for failure in failures))
        self.assertTrue(any("overclaim" in failure for failure in failures))
        self.assertTrue(any("missing tag" in failure for failure in failures))
        self.assertTrue(any("missing xref edge" in failure for failure in failures))
        self.assertTrue(any("RET 0x4" in failure for failure in failures))
        self.assertTrue(any("missing call" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
