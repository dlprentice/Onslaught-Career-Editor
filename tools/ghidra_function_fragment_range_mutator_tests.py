#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyFunctionFragmentRanges.java"
MANIFEST = ROOT / (
    "reverse-engineering/binary-analysis/"
    "pc-function-body-fragment-repairs-2026-08-14.tsv"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FunctionFragmentRangeMutatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MUTATOR.read_text(encoding="utf-8")
        with MANIFEST.open(encoding="utf-8", newline="") as stream:
            cls.rows = list(csv.DictReader(stream, delimiter="\t"))

    def test_frozen_mutator_and_manifest_identities(self) -> None:
        self.assertEqual(MUTATOR.stat().st_size, 50339)
        self.assertEqual(
            sha256_file(MUTATOR),
            "fe845a9df094eff4a1d9b36c9d4a6b141f049356499016a20a673071d492ec4c",
        )
        self.assertEqual(MANIFEST.stat().st_size, 2878)
        self.assertEqual(
            sha256_file(MANIFEST),
            "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0",
        )

    def test_only_existing_function_bodies_and_bounded_listing_are_mutated(self) -> None:
        for token in (
            "createFunction(",
            "setName(",
            "setComment(",
            "setRepeatableComment(",
            "addTag(",
            "setCallingConvention(",
            "replaceParameters(",
            "setReturnType(",
            "createData(",
            "setBytes(",
            "addMemoryReference(",
            "removeFunction(",
        ):
            self.assertNotIn(token, self.source)
        self.assertEqual(self.source.count("owner.setBody(target.postBody);"), 1)
        self.assertEqual(self.source.count("listing.clearCodeUnits("), 1)
        self.assertIn("target.repair.contains(", self.source)
        self.assertIn("disassembler.disassemble(new AddressSet(seed, seed), target.repair, true)", self.source)
        self.assertIn("instructionCoverage(target.repair).hasSameAddresses", self.source)

    def test_exact_pre_post_counts_and_policy_are_frozen(self) -> None:
        for name, value in (
            ("PRE_FUNCTIONS", 8280),
            ("PRE_BODY_RANGES", 8400),
            ("PRE_OWNED_BYTES", 1794212),
            ("PRE_INSTRUCTIONS", 550991),
            ("PRE_REFERENCES", 234495),
            ("POST_FUNCTIONS", 8280),
            ("POST_BODY_RANGES", 8396),
            ("POST_OWNED_BYTES", 1795470),
            ("POST_INSTRUCTIONS", 551014),
            ("POST_REFERENCES", 234478),
            ("TARGET_COUNT", 5),
            ("REPAIR_BYTES", 1258),
            ("REPAIR_INSTRUCTIONS", 325),
        ):
            self.assertRegex(self.source, rf"{name}\s*=\s*{value}")
        self.assertIn('private static final String POLICY = "LIVE_FORBIDDEN";', self.source)
        self.assertIn('"newFunctionsAuthorized\\": false', self.source)
        self.assertIn('"namesSignaturesCommentsTagsDataAuthorized\\": false', self.source)

    def test_all_non_body_state_has_exact_preservation_guards(self) -> None:
        for marker in (
            'equal("target metadata at "',
            'equal("non-target function at "',
            'equal("instructions outside repair"',
            'equal("references outside repair"',
            'equal("defined data"',
            'equal("stored non-function symbols"',
            'equal("comments"',
            'equal("memory"',
        ):
            self.assertIn(marker, self.source)

    def test_modes_containment_and_restore_requirement_are_explicit(self) -> None:
        for mode in ("dry", "probe-after-one", "probe-after-all", "apply", "readback"):
            self.assertIn(f'"{mode}"', self.source)
        self.assertIn("requireNewOutput(packageRoot, args[1]", self.source)
        self.assertIn("requireNewOutput(packageRoot, args[2]", self.source)
        self.assertIn("StandardOpenOption.CREATE_NEW", self.source)
        self.assertIn("output.toPath().startsWith(packageRoot.toPath())", self.source)
        self.assertIn("RESTORE_VERIFIED_SCRATCH_BASE_REQUIRED", self.source)

    def test_manifest_target_order_and_current_names_are_exact(self) -> None:
        expected = tuple(zip(
            ("0x00462640", "0x0046ff10", "0x00482590", "0x004be420", "0x00559410"),
            (
                "CFEPMain__Process",
                "CGame__HandleEvent",
                "CHud__RenderTargetIndicatorOverlay",
                "CExplosionInitThing__SelectNextPathStepDirection",
                "CDXTexture__CreateMipmaps",
            ),
            strict=True,
        ))
        self.assertEqual(
            tuple((row["entry"], row["current_name"]) for row in self.rows),
            expected,
        )
        for entry, name in expected:
            self.assertIn(f'"{entry}"', self.source)
            self.assertIn(f'"{name}"', self.source)


if __name__ == "__main__":
    unittest.main()
