#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for FUN native name align plate + Gen34 generation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


plate_mod = _load("plate", "tools/re_fun_native_name_align.py")
gen_mod = _load("gen", "tools/re_fun_native_name_align_generation.py")

PARENT = (
    ROOT
    / "local-lab"
    / "residual-terminal-generation33-large-island-resolve-20260805-v1"
    / "generation-33-residual-terminal-large-island-resolve"
)
PLATE = ROOT / "local-lab" / "fun-native-name-align-20260805-v1"
OUT = (
    ROOT
    / "local-lab"
    / "function-native-name-align-generation34-20260805-v1"
    / "generation-34-function-native-name-align"
)
HAS_LAB = PARENT.is_dir()


class UnitSelectTests(unittest.TestCase):
    def test_select_requires_boundary_status(self) -> None:
        rows = [
            {
                "entityKey": "F1",
                "entryVa": "0x005348c0",
                "currentName": "FUN_005348c0",
                "nameClass": "FUN",
                "nativeShippedName": "Damage",
                "nativeRegistryStatus": "WEAK",
                "executionState": "COVERED",
                "bodyBytes": "10",
                "semanticGrade": "OPAQUE",
                "campaignState": "OPEN_EXECUTED",
                "understoodTier": "U2",
            },
            {
                "entityKey": "F2",
                "entryVa": "0x00536a60",
                "currentName": "FUN_00536a60",
                "nameClass": "FUN",
                "nativeShippedName": "TeleportOrientation",
                "nativeRegistryStatus": "FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY",
                "executionState": "COVERED",
                "bodyBytes": "269",
                "semanticGrade": "OPAQUE",
                "campaignState": "OPEN_EXECUTED",
                "understoodTier": "U2",
            },
            {
                "entityKey": "F3",
                "entryVa": "0x00401000",
                "currentName": "FUN_00401000",
                "nameClass": "FUN",
                "nativeShippedName": "None",
                "nativeRegistryStatus": "FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY",
                "executionState": "COVERED",
                "bodyBytes": "16",
                "semanticGrade": "OPAQUE",
                "campaignState": "OPEN_EXECUTED",
                "understoodTier": "U0",
            },
        ]
        proofs, still = plate_mod.select_proofs(rows)
        self.assertEqual(len(proofs), 1)
        self.assertEqual(proofs[0]["newName"], "TeleportOrientation")
        self.assertTrue(any(s.get("lane") == "STATUS_HELD" for s in still))
        # stringified None must not become a rename target
        self.assertFalse(any(p.get("newName") == "None" for p in proofs))
        self.assertTrue(plate_mod.is_real_native_name("Damage"))
        self.assertFalse(plate_mod.is_real_native_name("None"))
        self.assertFalse(plate_mod.is_real_native_name(""))


@unittest.skipUnless(HAS_LAB, "local-lab unavailable")
class LabNativeNameTests(unittest.TestCase):
    def test_build_apply_verify_parent_unmutated(self) -> None:
        pre_fn = hashlib.sha256(
            (PARENT / "campaign-functions.tsv").read_bytes()
        ).hexdigest()
        pre_res = hashlib.sha256(
            (PARENT / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        rc = plate_mod.main(["build", "--campaign", str(PARENT), "--out", str(PLATE)])
        self.assertEqual(rc, 0)
        pack = json.loads((PLATE / "FORMAL-PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(pack["status"], "READY_FOR_GENERATION")
        self.assertEqual(pack["n_proofs"], gen_mod.EXPECTED_PROOFS)
        self.assertEqual(plate_mod.main(["verify", "--plate", str(PLATE)]), 0)
        rc2 = gen_mod.main(
            [
                "apply",
                "--parent",
                str(PARENT),
                "--formal-pack",
                str(PLATE / "FORMAL-PACK.json"),
                "--out",
                str(OUT),
            ]
        )
        self.assertEqual(rc2, 0)
        post_fn = hashlib.sha256(
            (PARENT / "campaign-functions.tsv").read_bytes()
        ).hexdigest()
        post_res = hashlib.sha256(
            (PARENT / "campaign-residuals.tsv").read_bytes()
        ).hexdigest()
        self.assertEqual(pre_fn, post_fn)
        self.assertEqual(pre_res, post_res)
        ready = json.loads((OUT / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(ready["generation"], 34)
        self.assertEqual(ready["counts"]["functionNamesAlignedThisGeneration"], 40)
        self.assertFalse(ready["advance"]["delta"]["ghidraMutated"])
        self.assertEqual(
            gen_mod.main(
                [
                    "verify",
                    "--campaign",
                    str(OUT),
                    "--formal-pack",
                    str(PLATE / "FORMAL-PACK.json"),
                    "--parent",
                    str(PARENT),
                ]
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
