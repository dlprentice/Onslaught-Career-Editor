#!/usr/bin/env python3
"""Tests for ghidra_particle_manager_list_wave478_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_particle_manager_list_wave478_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ParticleManagerListWave478ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=2 created=0 would_create=0 renamed=0 "
                "would_rename=1 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_SUMMARIES["apply_particle_manager_list_wave478_dry.log"])

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
                base / "apply_particle_manager_list_wave478_apply.log",
                "REPORT: Save succeeded\n"
                "Read-back signature mismatch\n"
                "updated=0 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=2\n",
            )

            link = probe.EXPECTED[probe.LINK_ADDR]
            unlink = probe.EXPECTED[probe.UNLINK_ADDR]
            link_comment = " ".join(link["comment_tokens"])
            unlink_comment = " ".join(unlink["comment_tokens"])
            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.CALLER_ADDR}\tCParticleManager__UnlinkNodeFromActiveList\tvoid __thiscall CParticleManager__UnlinkNodeFromActiveList(void * this, void * node, void * unused_context)\tWave468 comment\tOK\n"
                f"{probe.LINK_ADDR}\t{link['name']}\t{link['signature']}\t{link_comment}\tOK\n"
                f"{probe.UNLINK_ADDR}\t{unlink['name']}\t{unlink['signature']}\t{unlink_comment}\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\tstatus\n"
                f"{probe.LINK_ADDR}\t{link['name']}\t{';'.join(sorted(link['tags']))}\tOK\n"
                f"{probe.UNLINK_ADDR}\t{unlink['name']}\t{';'.join(sorted(unlink['tags']))}\tOK\n",
            )
            xref_lines = [
                f"{target[2:]}\ttarget\t{from_addr[2:]}\t<none>\t{from_function}\tUNCONDITIONAL_CALL"
                for target, from_addr, from_function in sorted(probe.EXPECTED_XREFS)
            ]
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                + "\n".join(xref_lines)
                + "\n",
            )
            write(
                base / "post-decomp" / f"{probe.LINK_ADDR[2:]}_{link['name']}.c",
                "/* Wave478 comment */\n"
                "void __thiscall CParticleManager__LinkNodeByOffset3C40(void *this,void *node) {\n"
                "  *(void **)((int)this + 8) = node;\n"
                "  *(void **)((int)this + 4) = node;\n"
                "  *(undefined4 *)((int)node + 0x3c) = 0;\n"
                "  *(undefined4 *)((int)node + 0x40) = 0;\n"
                "}\n",
            )
            write(
                base / "post-decomp" / f"{probe.UNLINK_ADDR[2:]}_{unlink['name']}.c",
                "/* Wave478 comment can mention prior param_1/param_2 shape */\n"
                "void __thiscall CParticleManager__UnlinkNodeByOffset3C40(void *this,void *node) {\n"
                "  *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)node + 0x40);\n"
                "  *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)node + 0x3c);\n"
                "  *(undefined4 *)((int)node + 0x3c) = 0;\n"
                "  *(undefined4 *)((int)node + 0x40) = 0;\n"
                "}\n",
            )
            write(
                base / "link_unlink_pair_post.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                + "\n".join(f"{addr[2:]}\t\t{mnemonic}\t{operands}" for addr, (mnemonic, operands) in probe.EXPECTED_PAIR_ROWS.items())
                + "\n",
            )
            write(
                base / "active_list_callsite_post.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                + "\n".join(f"{addr[2:]}\t\t{mnemonic}\t{operands}" for addr, (mnemonic, operands) in probe.EXPECTED_CALLSITE_ROWS.items())
                + "\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
