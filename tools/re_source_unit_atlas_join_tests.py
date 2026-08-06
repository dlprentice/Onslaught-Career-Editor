#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for tools/re_source_unit_atlas_join.py."""

from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "re_source_unit_atlas_join.py"
SPEC = importlib.util.spec_from_file_location("re_source_unit_atlas_join", TOOL)
assert SPEC is not None and SPEC.loader is not None
atlas = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(atlas)

CENSUS = ROOT / "local-lab" / "source-unit-census-v1-ready"
GEN10 = (
    ROOT
    / "local-lab"
    / "ttd-call-context-level521-impact-generation10-20260804-v1"
    / "generation-10-ttd-call-context-observation-v2"
)
SPECIMEN = ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
PLATE = ROOT / "local-lab" / "source-unit-atlas-join-gen10-20260805-v1"

HAS_LAB = CENSUS.is_dir() and GEN10.is_dir() and SPECIMEN.is_file()


class SyntheticAgreementTests(unittest.TestCase):
    def test_classify_agreement_exact(self) -> None:
        self.assertEqual(atlas.classify_agreement("A", "A"), "AGREE")
        self.assertEqual(atlas.classify_agreement("", "B"), "CENSUS_EMPTY")
        self.assertEqual(atlas.classify_agreement("A", ""), "GEN10_EMPTY")
        self.assertEqual(atlas.classify_agreement("", ""), "BOTH_EMPTY")
        self.assertEqual(atlas.classify_agreement("A", "B"), "DISAGREE")

    def test_classify_entry_range_drift(self) -> None:
        c = "CODE:sha:VA=0x00401040:RANGES=aaaa"
        g = "CODE:sha:VA=0x00401040:RANGES=bbbb"
        self.assertEqual(atlas.classify_agreement(c, g), "AGREE_ENTRY_RANGE_DRIFT")

    def test_lookup_owner_function_and_residual(self) -> None:
        owners = {
            "starts": [0x401000, 0x401100],
            "intervals": [
                {
                    "lo": 0x401000,
                    "hi": 0x401100,
                    "kind": "FUNCTION",
                    "entityKey": "F1",
                    "entryVa": "0x00401000",
                    "name": "n",
                    "campaignState": "OPEN",
                },
                {
                    "lo": 0x401100,
                    "hi": 0x401180,
                    "kind": "RESIDUAL",
                    "entityKey": "R1",
                    "entryVa": "0x00401100",
                    "name": "",
                    "campaignState": "OPEN",
                    "observationState": "DARK",
                },
            ],
        }
        f = atlas.lookup_owner(owners, 0x401050)
        r = atlas.lookup_owner(owners, 0x401120)
        none = atlas.lookup_owner(owners, 0x401200)
        self.assertEqual(f["entityKey"], "F1")
        self.assertEqual(r["entityKey"], "R1")
        self.assertIsNone(none)

    def test_prior_disposition_primary_semantics(self) -> None:
        # direct helper still documents any-site vs empty
        self.assertEqual(atlas.prior_disposition(0, 0), "NO_SITE_EVIDENCE")
        self.assertEqual(atlas.prior_disposition(2, 0), "HEADER_OR_NON_CPP_ONLY")
        self.assertEqual(atlas.prior_disposition(2, 1), "DIRECT_CPP")


@unittest.skipUnless(HAS_LAB, "local-lab census/gen10/specimen unavailable")
class FrozenLabJoinTests(unittest.TestCase):
    def test_build_counts_match_census_gate(self) -> None:
        result = atlas.build_join(
            census_bundle=CENSUS,
            gen10_campaign=GEN10,
            specimen=SPECIMEN,
        )
        c = result["counts"]
        self.assertEqual(c["censusSites"], 1870)
        self.assertEqual(c["censusUnits"], 151)
        self.assertEqual(c["atlasSites"], 1870)
        self.assertEqual(c["atlasUnits"], 151)
        self.assertEqual(c["gen10Functions"], 8124)
        self.assertEqual(c["gen10Residuals"], 6117)
        self.assertEqual(c["pathOwnerAgree"], 1870)
        self.assertEqual(c["pathOwnerDisagree"], 0)
        self.assertEqual(c["pathOwnerGen10Empty"], 0)
        self.assertEqual(c["callOwnerAgree"], 1870)
        self.assertEqual(c["callOwnerDisagree"], 0)
        self.assertEqual(c["functionsWithDirectCpp"], 368)
        self.assertEqual(c["functionsWithAnySite"], 987)
        self.assertEqual(c["gen10PathFunctionSites"], 1845)
        self.assertEqual(c["gen10PathResidualSites"], 25)
        self.assertEqual(c["residualsWithSites"], 20)
        self.assertEqual(c["gen10SamePathAndCallOwnerSites"], 1869)
        self.assertEqual(c["gen10OwnerBoundaryCrossings"], 1)
        self.assertEqual(len(result["functionPriors"]), 8124)

    def test_known_crossing_is_0x437a2c(self) -> None:
        result = atlas.build_join(
            census_bundle=CENSUS,
            gen10_campaign=GEN10,
            specimen=SPECIMEN,
        )
        crossings = [
            s for s in result["atlasSites"] if s["gen10OwnerBoundaryCrossing"] == "True"
        ]
        self.assertEqual(len(crossings), 1)
        self.assertEqual(crossings[0]["siteVa"].lower(), "0x00437a2c")
        self.assertIn("cphysicsscriptstatements", crossings[0]["canonicalRelativePath"])

    def test_write_and_verify_roundtrip(self) -> None:
        result = atlas.build_join(
            census_bundle=CENSUS,
            gen10_campaign=GEN10,
            specimen=SPECIMEN,
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "plate"
            atlas.write_plate(
                result,
                out,
                census_bundle=CENSUS,
                gen10_campaign=GEN10,
                specimen=SPECIMEN,
            )
            for name in (
                "atlas-sites.tsv",
                "atlas-function-priors.tsv",
                "atlas-units.tsv",
                "atlas-residuals.tsv",
                "SUMMARY.json",
                "INTEGRITY.json",
                "README.md",
            ):
                self.assertTrue((out / name).is_file(), name)
            sites = [
                line
                for line in (out / "atlas-sites.tsv").read_text(encoding="utf-8").splitlines()
                if line and not line.startswith("#")
            ]
            rows = list(csv.DictReader(sites, delimiter="\t"))
            self.assertEqual(len(rows), 1870)
            summary = json.loads((out / "SUMMARY.json").read_text(encoding="utf-8"))
            integrity = json.loads((out / "INTEGRITY.json").read_text(encoding="utf-8"))
            self.assertTrue(all(integrity["checks"].values()))
            self.assertEqual(summary["counts"]["functionsWithDirectCpp"], 368)
            # verify command path
            rc = atlas.main(
                [
                    "verify",
                    "--plate",
                    str(out),
                    "--census-bundle",
                    str(CENSUS),
                    "--gen10-campaign",
                    str(GEN10),
                    "--specimen",
                    str(SPECIMEN),
                ]
            )
            self.assertEqual(rc, 0)

    def test_published_plate_if_present(self) -> None:
        if not (PLATE / "SUMMARY.json").is_file():
            self.skipTest("published plate not present")
        summary = json.loads((PLATE / "SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "MEASURED")
        self.assertEqual(summary["counts"]["pathOwnerAgree"], 1870)
        self.assertEqual(summary["counts"]["functionsWithDirectCpp"], 368)
        rc = atlas.main(
            [
                "verify",
                "--plate",
                str(PLATE),
                "--census-bundle",
                str(CENSUS),
                "--gen10-campaign",
                str(GEN10),
                "--specimen",
                str(SPECIMEN),
            ]
        )
        self.assertEqual(rc, 0)

    def test_gen10_ledgers_not_mutated_by_build(self) -> None:
        before_f = (GEN10 / "campaign-functions.tsv").read_bytes()
        before_r = (GEN10 / "campaign-residuals.tsv").read_bytes()
        before_ready = (GEN10 / "campaign.ready.json").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "plate"
            result = atlas.build_join(
                census_bundle=CENSUS,
                gen10_campaign=GEN10,
                specimen=SPECIMEN,
            )
            atlas.write_plate(
                result,
                out,
                census_bundle=CENSUS,
                gen10_campaign=GEN10,
                specimen=SPECIMEN,
            )
        self.assertEqual(before_f, (GEN10 / "campaign-functions.tsv").read_bytes())
        self.assertEqual(before_r, (GEN10 / "campaign-residuals.tsv").read_bytes())
        self.assertEqual(before_ready, (GEN10 / "campaign.ready.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
