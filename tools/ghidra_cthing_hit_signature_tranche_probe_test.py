#!/usr/bin/env python3
"""Tests for the CThing hit signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cthing_hit_signature_tranche_probe as probe


TARGET_ROWS = {
    "0x00403ba0": {
        "name": "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
        "signature": "void __thiscall CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(void * this, void * otherThing, void * collisionReport)",
        "comment": "Hit override/helper: incoming otherThing type bits 0x10 or 0x02100000 trigger cleanup. Source parity supports the CThing::Hit(CThing*, CCollisionReport*) shape; exact retail class owner/type names remain inferred.",
        "decompile": "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000 otherThing collisionReport CThing__CreateHitRefEvaluateImpulseAndDispatchHit 0x2100000",
    },
    "0x00403bf0": {
        "name": "CThing__Hit_TriggerDieOnTypeMask00100000",
        "signature": "void __thiscall CThing__Hit_TriggerDieOnTypeMask00100000(void * this, void * otherThing, void * collisionReport)",
        "comment": "Hit override/helper variant: incoming otherThing type bit 0x00100000 triggers cleanup. Source parity supports the CThing::Hit(CThing*, CCollisionReport*) shape; exact retail type-bit label remains unresolved.",
        "decompile": "CThing__Hit_TriggerDieOnTypeMask00100000 otherThing collisionReport CThing__CreateHitRefEvaluateImpulseAndDispatchHit 0x100000",
    },
    "0x004fcc30": {
        "name": "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
        "signature": "void __thiscall CThing__CreateHitRefEvaluateImpulseAndDispatchHit(void * this, void * otherThing, void * collisionReport)",
        "comment": "Shared hit dispatcher: marks this+0x248 for unit-type hits, evaluates collisionReport impulse thresholds for type bit 0x00100000, then dispatches CComplexThing::Hit. Not a full CCollisionReport layout proof.",
        "decompile": "CThing__CreateHitRefEvaluateImpulseAndDispatchHit otherThing collisionReport CThing__CreateThingRefWithSquad CComplexThing__Hit",
    },
    "0x004e6640": {
        "name": "CThing__CreateThingRefWithSquad",
        "signature": "void __thiscall CThing__CreateThingRefWithSquad(void * this, void * ownerThing, void * otherThing)",
        "comment": "Helper reached from hit dispatch: takes ownerThing and otherThing as two stack arguments. It does not prove the full referred-object layout.",
        "decompile": "CThing__CreateThingRefWithSquad ownerThing otherThing",
    },
}


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    rename_dry.write_text("--- SUMMARY ---\napplied=0 skipped=2 missing=0 bad=0\n", encoding="utf-8")
    rename_apply.write_text("--- SUMMARY ---\napplied=2 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=4 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=4 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = {address: dict(row) for address, row in TARGET_ROWS.items()}
    if stale:
        rows["0x00403ba0"]["name"] = "CThing__Hit_TriggerDieOnDamageMaskA"
        rows["0x004fcc30"]["signature"] = (
            "void __thiscall CThing__CreateHitRefEvaluateImpulseAndDispatchHit"
            "(void * this, void * param_1, int param_2, void * param_3)"
        )
    if overclaim:
        rows["0x004e6640"]["comment"] += " Full referred-object layout proof."

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{row['name']}\t{row['signature']}\t{row['comment']}\tOK\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{row['name']}\t{row['signature']}\tOK\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    for address, row in rows.items():
        text = f"{row['signature']} {row['decompile']}"
        if stale and address == "0x004fcc30":
            text += " unaff_EDI param_3 DamageMask"
        (decompile / f"{address[2:]}_{row['name']}.c").write_text(text, encoding="utf-8")
    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "".join(f"{address[2:]}\t{row['name']}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(
            f"{address}\t{address}\tAFTER\t1\t{address}\t{address}\t{row['name']}\tRET\t0x8\t\tTERMINATOR\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class CThingHitSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_cthing_hit_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["renamedTargets"], 2)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 4)
        self.assertEqual(report["summary"]["staleTokenHits"], 0)

    def test_fails_for_stale_name_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("stale token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
