#!/usr/bin/env python3
"""Tests for ghidra_particle_effect_link_wave477_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_particle_effect_link_wave477_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ParticleEffectLinkWave477ProbeTests(unittest.TestCase):
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
            summaries = {
                "dry.log": "updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1",
                "apply.log": "updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0",
                "verify_dry.log": "updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0",
                "comment_refresh_dry.log": "updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0",
                "comment_refresh_apply.log": "updated=3 skipped=0 created=0 would_create=0 renamed=0 would_rename=0",
                "comment_refresh_verify_dry.log": "updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0",
            }
            for name, summary in summaries.items():
                write(base / name, f"REPORT: Save succeeded\n{summary} missing=0 bad=0\n")

            target_comment = (
                "Wave477 owner/signature correction RET 0x4 one stack argument prior extra param_2 "
                "this +0x4 handle +0xb4 set_state_one old CUnit owner is too narrow "
                "raw caller boundaries runtime particle/effect behavior rebuild parity remain unproven"
            )
            refresh_comment = f"Wave477 comment refresh calls {probe.EXPECTED_NAME} and remains bounded."
            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                f"{probe.TARGET}\t{probe.EXPECTED_NAME}\t{probe.EXPECTED_SIGNATURE}\t{target_comment}\tOK\n"
                "0x0047cea0\tCGroundUnit__ClearLinkedThingFlagsAndResetCounter\tvoid __fastcall x(void * this)"
                f"\t{refresh_comment}\tOK\n"
                "0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\tvoid __fastcall x(void * this)"
                f"\t{refresh_comment}\tOK\n"
                "0x004f84e0\tCUnit__dtor_base\tvoid __fastcall x(void * this)"
                f"\t{refresh_comment}\tOK\n",
            )
            target_tags = ";".join(sorted(probe.EXPECTED_TAGS))
            refresh_tags = "comment-hardened;particle-effect-link-wave477;retail-binary-evidence"
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\tstatus\n"
                f"{probe.TARGET}\t{probe.EXPECTED_NAME}\t{target_tags}\tOK\n"
                f"0x0047cea0\tCGroundUnit__ClearLinkedThingFlagsAndResetCounter\t{refresh_tags}\tOK\n"
                f"0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\t{refresh_tags}\tOK\n"
                f"0x004f84e0\tCUnit__dtor_base\t{refresh_tags}\tOK\n",
            )
            xref_lines = [
                f"{target[2:]}\t{probe.EXPECTED_NAME}\t{from_addr[2:]}\t<none>\t{from_function}\tUNCONDITIONAL_CALL"
                for target, from_addr, from_function in sorted(probe.EXPECTED_XREFS)
            ]
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                + "\n".join(xref_lines)
                + "\n",
            )
            write(
                base / "post-decomp" / f"{probe.TARGET[2:]}_{probe.EXPECTED_NAME}.c",
                "/* old comment can mention prior extra param_2 */\n"
                "void __thiscall ParticleEffectLink__SetHandleStateAndClear(void *this,int set_state_one) {\n"
                "  *(undefined2 *)(iVar1 + 0xb4) = 2;\n"
                "  *(undefined2 *)(iVar1 + 0xb4) = 1;\n"
                "  *(undefined4 *)((int)this + 4) = 0;\n"
                "}\n",
            )
            write(
                base / "post_004cb080_004cb0df_range.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004cb0b0\t\tMOV\tEAX, dword ptr [ECX + 0x4]\n"
                "004cb0c2\t\tMOV\tword ptr [EAX + 0xb4], 0x2\n"
                "004cb0ce\t\tRET\t0x4\n"
                "004cb0d1\t\tMOV\tword ptr [EAX + 0xb4], 0x1\n"
                "004cb0dd\t\tRET\t0x4\n",
            )
            write(
                base / "post_004c5700_004c572d_rawcaller.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004c570f\t\tPUSH\t0x1\n"
                "004c5713\t\tCALL\t0x004cb0b0\n"
                "004c571a\t\tCALL\t0x004cb050\n"
                "004c5725\t\tCALL\t0x00549220\n",
            )
            write(
                base / "post_callsite_instructions.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "00400000\t\tPUSH\t0x0\n"
                "00400001\t\tPUSH\t0x1\n",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
