#!/usr/bin/env python3
"""Tests for ghidra_particle_parent_transform_wave476_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_particle_parent_transform_wave476_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ParticleParentTransformWave476ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=1 created=0 would_create=0 renamed=0 "
                "would_rename=1 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_DRY)

    def test_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, summary in (
                ("dry.log", "updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1"),
                ("apply.log", "updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0"),
                ("verify_dry.log", "updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0"),
            ):
                write(base / name, f"REPORT: Save succeeded\n{summary} missing=0 bad=0\n")

            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.TARGET}\t{probe.EXPECTED_NAME}\t{probe.EXPECTED_SIGNATURE}\t"
                "Wave476 owner/signature correction raw caller 0x004c524f particle pointer "
                "parent-particle pointer link-parent-only flag no current CUnitAI evidence "
                "particle +0x58 +0xa0 +0x38/+0x3c/+0x40 runtime particle behavior "
                "rebuild parity remain unproven\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\tstatus\n"
                f"{probe.TARGET}\t{probe.EXPECTED_NAME}\t"
                f"{';'.join(sorted(probe.EXPECTED_TAGS))}\tOK\n",
            )
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                f"{probe.TARGET[2:]}\t{probe.EXPECTED_NAME}\t004c524f\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
            )
            write(
                base / "post-decomp" / f"{probe.TARGET[2:]}_{probe.EXPECTED_NAME}.c",
                "particle parent_particle link_parent_only particle + 0x58 + 0xa0 "
                "Vec3__SetXYZ Mat34__SetRows Mat34__TransformVec3ByBasisToOut",
            )
            write(
                base / "post_004c51e0_004c5290_caller_range.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004c521f\t\tCALL\t0x004cb5c0\n"
                "004c524a\t\tPUSH\tECX\n"
                "004c524b\t\tPUSH\tEDX\n"
                "004c524c\t\tPUSH\tESI\n"
                "004c524f\t\tCALL\t0x004c0150\n",
            )
            write(
                base / "post_004c0000_004c036f_range.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004c016b\t\tRET\t0xc\n"
                "004c035f\t\tRET\t0xc\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
