import json
import tempfile
import unittest
from pathlib import Path

import ghidra_cylinder_damage_signature_tranche_probe as probe


class CylinderDamageSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_expected_saved_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "metadata_final.tsv").write_text(
                "\n".join(
                    [
                        "address\tname\tsignature\tcomment\tstatus",
                        "0x0043fde0\tCCylinder__ctor\tvoid __thiscall CCylinder__ctor(void * this, void * sourceCylinder)\tCCylinder constructor stores radius evidence\tOK",
                        "0x0043fe20\tCCylinder__ResolveCollisionVFunc02\tint __thiscall CCylinder__ResolveCollisionVFunc02(void * this, void * movingStateA, void * movingStateB, void * radiusContext, void * contactOut)\tCCylinder collision resolver writes contact normal\tOK",
                        "0x00440b90\tCDamage__Init\tvoid __fastcall CDamage__Init(void * damage)\tCDamage init loads damage0.tga and clears damage table\tOK",
                        "0x00440c00\tCDamage__FreeOwnedDamageObjects\tvoid __fastcall CDamage__FreeOwnedDamageObjects(void * damage)\tCDamage cleanup frees owned damage texture state\tOK",
                        "0x00440c40\tCDamage__ResetDamageTables\tvoid __fastcall CDamage__ResetDamageTables(void * damage)\tCDamage reset clears damage lookup and flags\tOK",
                        "0x00440c70\tCDamage__LoadDamageTexture\tvoid __thiscall CDamage__LoadDamageTexture(void * this, char * tgaPath)\tCDamage load texture-info mipmap data\tOK",
                        "0x00440eb0\tCDamage__InsertCellEntry\tint __thiscall CDamage__InsertCellEntry(void * this, int cellIndex, int coordX, int coordY, int stampValue)\tCDamage insert per-cell entry with ret 0x10\tOK",
                        "0x00440f80\tCDamage__RemoveCellEntryByCoords\tvoid __thiscall CDamage__RemoveCellEntryByCoords(void * this, int cellIndex, int coordX, int coordY)\tCDamage remove per-cell entry with ret 0xc\tOK",
                        "0x00441000\tCDamage__CreateTextureBuffer\tvoid __thiscall CDamage__CreateTextureBuffer(void * this, void * chunkReader)\tCDamage CChunkReader texture-info buffer load\tOK",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "tags_final.tsv").write_text(
                "\n".join(
                    [
                        "address\tname\ttags\tstatus",
                        "0043fde0\tCCylinder__ctor\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "0043fe20\tCCylinder__ResolveCollisionVFunc02\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440b90\tCDamage__Init\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440c00\tCDamage__FreeOwnedDamageObjects\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440c40\tCDamage__ResetDamageTables\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440c70\tCDamage__LoadDamageTexture\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440eb0\tCDamage__InsertCellEntry\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00440f80\tCDamage__RemoveCellEntryByCoords\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                        "00441000\tCDamage__CreateTextureBuffer\tstatic-reaudit;cylinder-damage-wave346;retail-binary-evidence\tOK",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "xrefs_final.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                + "\n".join(f"{addr}\t{name}\t00400000\t00400000\tCaller\tUNCONDITIONAL_CALL" for addr, name in probe.EXPECTED_NAMES.items())
                + "\n",
                encoding="utf-8",
            )
            (root / "instructions_final.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00440eb0\t0x00440eb0\tBODY\t1\t0x00440f7b\t0x00440eb0\tCDamage__InsertCellEntry\tRET\t0x10\tc2 10 00\tTERMINATOR\n"
                "0x00440f80\t0x00440f80\tBODY\t1\t0x00440ffa\t0x00440f80\tCDamage__RemoveCellEntryByCoords\tRET\t0xc\tc2 0c 00\tTERMINATOR\n",
                encoding="utf-8",
            )

            summary = probe.build_summary(root)

        self.assertEqual(summary["status"], "PASS", json.dumps(summary, indent=2))
        self.assertEqual(summary["failures"], [])
        self.assertEqual(summary["summary"]["targets"], 9)

    def test_fails_for_stale_undefined_or_param_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "metadata_final.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00440b90\tCDamage__Init\tundefined CDamage__Init(void)\t\tOK\n",
                encoding="utf-8",
            )
            (root / "tags_final.tsv").write_text("address\tname\ttags\tstatus\n", encoding="utf-8")
            (root / "xrefs_final.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n",
                encoding="utf-8",
            )
            (root / "instructions_final.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n",
                encoding="utf-8",
            )

            summary = probe.build_summary(root)

        self.assertEqual(summary["status"], "FAIL")
        self.assertTrue(any("missing metadata" in failure or "stale signature" in failure for failure in summary["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
