#!/usr/bin/env python3
"""Tests for the first Ghidra name-confidence comment-pass probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_comment_pass_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"


def write_fixture(root: Path, *, omit_boundary_token: bool = False) -> dict[str, Path]:
    dry_log = root / "comments_dry.log"
    apply_log = root / "comments_apply.log"
    metadata = root / "metadata_after.tsv"

    targets = [
        ("0x00402dd0", "CHeightField_Unk_0047eb80__Wrapper_00402dd0"),
        ("0x00403ff0", "CFastVB_Unk_0055db0a__Wrapper_00403ff0"),
        ("0x0040dcc0", "CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0"),
        ("0x0040dda0", "CUnitAI_Unk_0044c720__Wrapper_0040dda0"),
        ("0x00410670", "CGeneralVolume_Unk_00409e60__Wrapper_00410670"),
        ("0x00411b90", "CEngine_Unk_00506010__Wrapper_00411b90"),
    ]

    dry_log.write_text(
        "\n".join(["Mode: dry"] + [f"DRY: {addr} {name}" for addr, name in targets] + [
            "--- SUMMARY ---",
            "applied=0 skipped=6 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        "\n".join(["Mode: apply"] + [f"OK: {addr} {name}" for addr, name in targets] + [
            "--- SUMMARY ---",
            "applied=6 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )

    boundary = "owner and signature remain provisional"
    if omit_boundary_token:
        boundary = "static evidence only"

    rows = [
        (
            "0x00402dd0",
            "CHeightField_Unk_0047eb80__Wrapper_00402dd0",
            "int __fastcall CHeightField_Unk_0047eb80__Wrapper_00402dd0(void * param_1)",
            f"Shadow/heightfield corner test using CStaticShadows__SampleShadowHeightBilinear; {boundary}.",
        ),
        (
            "0x00403ff0",
            "CFastVB_Unk_0055db0a__Wrapper_00403ff0",
            "void __fastcall CFastVB_Unk_0055db0a__Wrapper_00403ff0(int param_1)",
            "Array-destroy wrapper forwarding to CDXLandscape__DestroyArrayWithCallback and CResourceDescriptor__dtor; owner remains suspect.",
        ),
        (
            "0x0040dcc0",
            "CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0",
            "void __fastcall CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0(void * param_1)",
            "Transition-state wrapper clears +0x58c and calls CMonitor__UpdateFlightWalkerTransitionState when +0x260 == 3.",
        ),
        (
            "0x0040dda0",
            "CUnitAI_Unk_0044c720__Wrapper_0040dda0",
            "void __fastcall CUnitAI_Unk_0044c720__Wrapper_0040dda0(void * param_1)",
            "CUnitAI grid cooldown wrapper checks CSquadNormal__GetCellValueAtWorldXY and refreshes this+0x2e8.",
        ),
        (
            "0x00410670",
            "CGeneralVolume_Unk_00409e60__Wrapper_00410670",
            "void __fastcall CGeneralVolume_Unk_00409e60__Wrapper_00410670(int param_1)",
            "General-volume linked-object drain wrapper uses CGeneralVolume__ToDoubleIdentity, +0x280, +0x588, and +0x520.",
        ),
        (
            "0x00411b90",
            "CEngine_Unk_00506010__Wrapper_00411b90",
            "void __fastcall CEngine_Unk_00506010__Wrapper_00411b90(void * param_1)",
            "Burst-dispatch list wrapper clears +0x588, walks selected index +0x10, calls CGeneralVolume__SpawnBurstFromPresetWithFallback; not CWeapon::Fire proof.",
        ),
    ]
    metadata.write_text(METADATA_HEADER + "".join("\t".join(row) + "\tOK\n" for row in rows), encoding="utf-8")
    return {"dry_log": dry_log, "apply_log": apply_log, "metadata": metadata}


class GhidraNameConfidenceCommentPassProbeTests(unittest.TestCase):
    def test_passes_for_clean_logs_and_comment_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "name-confidence-comment-candidates-commented")
        self.assertTrue(report["readback"]["allCommentsPresent"])

    def test_fails_when_heightfield_comment_loses_proof_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_boundary_token=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00402dd0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
