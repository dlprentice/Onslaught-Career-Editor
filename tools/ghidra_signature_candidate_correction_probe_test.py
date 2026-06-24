#!/usr/bin/env python3
"""Tests for the Ghidra signature-candidate correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_signature_candidate_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"


def write_fixture(root: Path, *, omit_defer_token: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_after.tsv"

    renames = [
        ("0x0040e280", "DXMemBuffer_ReadBytes__Wrapper_0040e280", "CInitThing__LoadFromMemBuffer"),
        ("0x0040f140", "OID_FreeObject__Wrapper_0040f140", "BattleEngineConfigurations__ShutDown"),
        ("0x0040f520", "CSPtrSet_Init__Wrapper_0040f520", "CBattleEngineData__ctor"),
    ]

    rename_dry.write_text(
        "\n".join(["Mode: args (dry)"] + [f"DRY: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=3 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "\n".join(["Mode: args (apply)"] + [f"OK: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=3 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )

    comments_dry.write_text(
        "\n".join(["Mode: dry"] + [f"DRY: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=3 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    comments_apply.write_text(
        "\n".join(["Mode: apply"] + [f"OK: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=3 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )

    signature_note = "signature and parameter names deferred"
    if omit_defer_token:
        signature_note = "signature updated"

    rows = [
        (
            "0x0040e280",
            "CInitThing__LoadFromMemBuffer",
            "void __thiscall CInitThing__LoadFromMemBuffer(void * this, int param_1, int param_2)",
            f"Source-aligned CInitThing::Load(short, CMEMBUFFER&) reader; reads versioned CInitThing fields and caller CSquadInitThing__VFunc_01_0048d8d0 reads squad amount/mode after it; {signature_note}.",
        ),
        (
            "0x0040f140",
            "BattleEngineConfigurations__ShutDown",
            "void BattleEngineConfigurations__ShutDown(void)",
            f"Source-aligned UBattleEngineConfigurations::ShutDown; clears count at 0x00660250 and frees sConfigurationName array at 0x00660200; {signature_note}.",
        ),
        (
            "0x0040f520",
            "CBattleEngineData__ctor",
            "int __fastcall CBattleEngineData__ctor(int param_1)",
            f"Source-aligned CBattleEngineData constructor; initializes SPtrSet members at +0x40/+0x50 and zeroes owned string/store fields before Initialise/Load; {signature_note}.",
        ),
    ]
    metadata.write_text(METADATA_HEADER + "".join("\t".join(row) + "\tOK\n" for row in rows), encoding="utf-8")

    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
    }


class GhidraSignatureCandidateCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_clean_rename_comment_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "signature-candidates-renamed-commented-signatures-deferred")
        self.assertTrue(report["readback"]["allNamesAndCommentsPresent"])

    def test_fails_when_comment_overclaims_signature_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_defer_token=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x0040e280" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
