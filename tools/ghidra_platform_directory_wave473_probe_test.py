#!/usr/bin/env python3
"""Tests for ghidra_platform_directory_wave473_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_platform_directory_wave473_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PlatformDirectoryWave473ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "SUMMARY updated=0 skipped=2 created=0 would_create=0 renamed=0 "
                "would_rename=0 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_DRY)

    def test_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, summary in (
                ("dry.log", "updated=0 skipped=2"),
                ("apply.log", "updated=2 skipped=0"),
                ("verify_dry.log", "updated=0 skipped=2"),
            ):
                write(
                    base / name,
                    "REPORT: Save succeeded\n"
                    f"SUMMARY {summary} created=0 would_create=0 renamed=0 "
                    "would_rename=0 missing=0 bad=0\n",
                )

            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004d2600\tPlatform__CreateDirectoryPath\t"
                "void __stdcall Platform__CreateDirectoryPath(char * path, int strip_filename)\t"
                "Wave473 260-byte stack buffer strip_filename _strchr "
                "Platform__CreateDirectoryWithErrno RET 0x8 CLIParams__ParseCommandLine "
                "runtime filesystem behavior\tOK\n"
                "0x0055f347\tPlatform__CreateDirectoryWithErrno\t"
                "int __cdecl Platform__CreateDirectoryWithErrno(char * path)\t"
                "Wave473 CreateDirectoryA GetLastError "
                "CRT__SetErrnoAndDosErrnoFromWinError_00567a35 returns -1 returns 0 "
                "EnumerateSaveFiles_Main runtime filesystem behavior\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\n"
                "0x004d2600\tPlatform__CreateDirectoryPath\t"
                "static-reaudit;platform-directory-wave473;retail-binary-evidence;"
                "signature-corrected;comment-hardened;platform;directory-path;"
                "recursive-directory-create;ret-0x8\n"
                "0x0055f347\tPlatform__CreateDirectoryWithErrno\t"
                "static-reaudit;platform-directory-wave473;retail-binary-evidence;"
                "signature-corrected;comment-hardened;platform;directory-path;"
                "createdirectorya-wrapper;errno-bridge\n",
            )
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "004d2600\tPlatform__CreateDirectoryPath\t00424091\t00423bc0\tCLIParams__ParseCommandLine\tUNCONDITIONAL_CALL\n"
                "0055f347\tPlatform__CreateDirectoryWithErrno\t004d266b\t004d2600\tPlatform__CreateDirectoryPath\tUNCONDITIONAL_CALL\n"
                "0055f347\tPlatform__CreateDirectoryWithErrno\t00514bfd\t00514be0\tEnumerateSaveFiles_Main\tUNCONDITIONAL_CALL\n",
            )
            write(
                base / "post_disasm_004d2600.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004d2611\t\tMOV\tEDI, dword ptr [ESP + 0x110]\n"
                "004d262b\t\tMOV\tEAX, dword ptr [ESP + 0x114]\n"
                "004d2642\t\tCALL\t0x0055f320\n"
                "004d2655\t\tCALL\t0x0055e2d0\n"
                "004d266b\t\tCALL\t0x0055f347\n"
                "004d268d\t\tRET\t0x8\n",
            )
            write(
                base / "post_disasm_0055f347.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "0055f34d\t\tCALL\tdword ptr [0x005d81c8]\n"
                "0055f357\t\tCALL\tdword ptr [0x005d8138]\n"
                "0055f366\t\tCALL\t0x00567a35\n"
                "0055f36c\t\tOR\tEAX, 0xffffffff\n"
                "0055f370\t\tXOR\tEAX, EAX\n",
            )
            write(
                base / "post_caller_instructions_wide.tsv",
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00424091\t0x00424091\tBEFORE\t-1\t0x0042403d\t0x00423bc0\tCLIParams__ParseCommandLine\tPUSH\t0x1\t\t\n"
                "0x00424091\t0x00424091\tBEFORE\t-1\t0x00424045\t0x00423bc0\tCLIParams__ParseCommandLine\tPUSH\t0x662cb0\t\t\n"
                "0x00424091\t0x00424091\tTARGET\t0\t0x00424091\t0x00423bc0\tCLIParams__ParseCommandLine\tCALL\t0x004d2600\t\t\n"
                "0x00514bfd\t0x00514bfd\tBEFORE\t-1\t0x00514bf8\t0x00514be0\tEnumerateSaveFiles_Main\tPUSH\t0x63df94\t\t\n"
                "0x00514bfd\t0x00514bfd\tTARGET\t0\t0x00514bfd\t0x00514be0\tEnumerateSaveFiles_Main\tCALL\t0x0055f347\t\t\n",
            )
            write(
                base / "post-decomp" / "004d2600_Platform__CreateDirectoryPath.c",
                "void __stdcall Platform__CreateDirectoryPath(char * path,int strip_filename) "
                "{ _strrchr(path,0x5c); _strchr(path,0x5c); Platform__CreateDirectoryWithErrno(path); }",
            )
            write(
                base / "post-decomp" / "0055f347_Platform__CreateDirectoryWithErrno.c",
                "int __cdecl Platform__CreateDirectoryWithErrno(char * path) "
                "{ CreateDirectoryA(path,0); GetLastError(); CRT__SetErrnoAndDosErrnoFromWinError_00567a35(1); }",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
