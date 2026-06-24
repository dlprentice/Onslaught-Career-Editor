#!/usr/bin/env python3
"""Self-tests for the Wave406 CGame::IsMultiplayer probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_cgame_is_multiplayer_wave406_probe as probe


class CGameIsMultiplayerWave406ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "range-check-wave406" / "current"
            decomp = base / "decompile_after"
            decomp.mkdir(parents=True)

            (base / "metadata_before.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004725d0\tCExplosionInitThing__CheckValueRange_852_899\t"
                "int __fastcall CExplosionInitThing__CheckValueRange_852_899(int param_1)\t\tOK\n",
                encoding="utf-8",
            )
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004725d0\tCGame__IsMultiplayer\tint __thiscall CGame__IsMultiplayer(void * this)\t"
                "Name/signature correction: source-parity CGame::IsMultiplayer predicate. Retail body reads the current-level "
                "field at CGame+0x2a0 and returns true for 850..899 via the exact 849 < level < 900 gate. Cross-cutting callers "
                "pass the CGame singleton &DAT_008a9a98 from sound, career, render, BattleEngine, HUD/compass/battleline, "
                "landscape, particle, monitor, and pause-menu contexts. Static retail/source-alignment evidence only; exact "
                "CGame field layout, world-type semantics, runtime multiplayer behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "004725d0\tCGame__IsMultiplayer\tcgame-is-multiplayer-wave406;comment-hardened;cross-cutting-helper;"
                "game;multiplayer;name-corrected;retail-binary-evidence;signature-hardened;source-parity;static-reaudit\tOK\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "004725d0\tCGame__IsMultiplayer\t0041bb29\t0041bb20\tCCareer__DoesBaseThingExist\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t0053e47b\t0053e2e0\tCDXEngine__Render\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t00484c7a\t00484c50\tCExplosionInitThing__RenderTacticalRadarContacts\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t0042727e\t00427210\tCDXCompass__Render\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t00405131\t00404dd0\tCBattleEngine__Init\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t004d106c\t004d0ff0\tCPauseMenu__InitPauseSession\tUNCONDITIONAL_CALL\n"
                "004725d0\tCGame__IsMultiplayer\t004e1422\t004e1360\tCSoundManager__UpdateSoundPosition\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (decomp / "004725d0_CGame__IsMultiplayer.c").write_text(
                "int __thiscall CGame__IsMultiplayer(void *this) {\n"
                "  if ((0x351 < *(int *)((int)this + 0x2a0)) && (*(int *)((int)this + 0x2a0) < 900)) return 1;\n"
                "  return 0;\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "apply_cgame_is_multiplayer_wave406_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            (base / "apply_cgame_is_multiplayer_wave406_apply.log").write_text(
                "SUMMARY updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            queue = root / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
            queue.mkdir(parents=True)
            (queue / "static-reaudit-queue.json").write_text(
                json.dumps(
                    {
                        "totalFunctions": 6028,
                        "qualitySignals": {
                            "commentlessFunctionCount": 4469,
                            "undefinedSignatureCount": 1909,
                            "paramSignatureCount": 1857,
                        },
                        "priorityQueues": {"commentlessHighSignal": [{"address": "0x00472820"}]},
                    }
                ),
                encoding="utf-8",
            )
            source = root / "references" / "Onslaught"
            source.mkdir(parents=True)
            (source / "game.cpp").write_text(
                "BOOL CGame::IsMultiplayer()\n"
                "{\n"
                " if (mCurrentlyRunningLevel >849 && mCurrentlyRunningLevel < 900)return TRUE;\n"
                " return FALSE;\n"
                "}\n",
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_cgame_is_multiplayer_wave406_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x004725d0 CExplosionInitThing__CheckValueRange_852_899 CGame__IsMultiplayer "
                "int __thiscall CGame__IsMultiplayer(void * this) Stuart source CGame::IsMultiplayer "
                "mCurrentlyRunningLevel >849 mCurrentlyRunningLevel < 900 850..899 CGame+0x2a0 "
                "CCareer__DoesBaseThingExist CDXEngine__Render CDXCompass__Render "
                "does not prove exact CGame field layout does not prove runtime multiplayer behavior "
                "does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_stale_function_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "range-check-wave406" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004725d0\tCExplosionInitThing__CheckValueRange_852_899\t"
                "int __fastcall CExplosionInitThing__CheckValueRange_852_899(int param_1)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("CGame__IsMultiplayer" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "range-check-wave406" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_cgame_is_multiplayer_wave406_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime multiplayer behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
