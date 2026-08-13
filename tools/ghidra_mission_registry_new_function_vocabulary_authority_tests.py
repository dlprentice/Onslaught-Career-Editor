#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import csv
import hashlib
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "new34_vocabulary_authority",
    HERE / "ghidra_mission_registry_new_function_vocabulary_authority.py",
)
AUTH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUTH)


class NewFunctionVocabularyAuthorityTests(unittest.TestCase):
    def test_all_current_nonlocal_pins_match(self) -> None:
        for path in AUTH.STAMPS:
            if path in (AUTH.SCRIPT, AUTH.PRE_FUNCTIONS, AUTH.PRE_PROGRAM):
                continue
            self.assertEqual((path.stat().st_size, AUTH.sha256_file(path)),
                             AUTH.STAMPS[path], path)

    def test_manifest_is_exact_canonical_34(self) -> None:
        rows = AUTH.load_manifest()
        self.assertEqual(len(rows), 34)
        with AUTH.MANIFEST.open(encoding="utf-8", newline="") as stream:
            ordered = list(csv.DictReader(stream, delimiter="\t"))
        payload = "".join(
            f"{row['index']}\t{row['handlerVa']}\t{row['expectedPreName']}\t"
            f"{row['proposedName']}\n" for row in ordered
        ).encode()
        self.assertEqual(len(payload), 1_684)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), AUTH.CANONICAL_SHA)
        self.assertEqual({row["cohort"] for row in ordered}, {"NEW34_STATIC_C1"})

    def test_manifest_exactly_joins_boundary_and_static_contract_owners(self) -> None:
        manifest = AUTH.load_manifest()
        result = AUTH.validate_static_contract_join(manifest)
        self.assertEqual(result["rows"], 34)
        self.assertTrue(result["exactManifestJoin"])
        self.assertTrue(result["exactRegistryTripleJoin"])
        self.assertTrue(result["registryRowsWerePreBoundaryNonEntries"])
        self.assertTrue(result["exactBoundaryRecordAndDefaultNameJoin"])
        self.assertFalse(result["runtimeBehaviorAuthorized"])
        self.assertFalse(result["reconstructionParityAuthorized"])
        self.assertNotIn("0x0050ff10", manifest)

    def test_current_projection_has_defaults_and_no_name_collisions(self) -> None:
        manifest = AUTH.load_manifest()
        with AUTH.PROJECTION.open(encoding="utf-8", newline="") as stream:
            projection = list(csv.DictReader(
                (line for line in stream if not line.startswith("#")), delimiter="\t"))
        by_address = {row["address"].lower(): row for row in projection}
        names = {row["name"] for row in projection}
        self.assertEqual(len(projection), 8_170)
        for address, row in manifest.items():
            self.assertEqual(by_address[address]["name"], row["expectedPreName"])
            self.assertEqual(row["expectedNameSource"], "DEFAULT")
            self.assertNotIn(row["proposedName"], names)

    def test_pre_metadata_is_exact_empty_state(self) -> None:
        manifest, metadata = AUTH.load_manifest(), AUTH.load_metadata()
        self.assertEqual(manifest.keys(), metadata.keys())
        self.assertTrue(all(row["preCommentPresent"] == "false" and
                            row["preRepeatableCommentPresent"] == "false" and
                            row["preTags"] == "" for row in metadata.values()))
        lines = AUTH.METADATA.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 35)
        self.assertTrue(all(line.endswith("\t<EMPTY>") for line in lines[1:]))

    def test_every_comment_preserves_row_specific_unknowns_and_falsifier(self) -> None:
        comments = [AUTH.post_comment(row) for row in AUTH.load_manifest().values()]
        self.assertEqual(len(set(comments)), 34)
        for comment in comments:
            for text in ("C1_CANDIDATE_PARTIAL", "STATIC_HYPOTHESIS_ONLY",
                         "Remaining unknowns:", "Cheapest falsifier:",
                         "not a recovered C++ symbol", "No runtime reachability",
                         "reconstruction parity is admitted"):
                self.assertIn(text, comment)

    def test_post_tags_add_exactly_two_existing_vocabulary_tags(self) -> None:
        manifest, metadata = AUTH.load_manifest(), AUTH.load_metadata()
        for address, row in manifest.items():
            self.assertEqual(AUTH.post_tags(row, metadata[address]),
                             ["script-command-registry", "tier2-script-facing-name"])

    def test_allowed_inventory_fields_exclude_abi_boundaries_and_repeatable_comments(self) -> None:
        forbidden = {"sigSource", "bodyBytes", "bodyMin", "bodyMax", "bodyRanges",
                     "bodyDigest", "instrCount", "paramCount", "callingConv",
                     "returnType", "varArgs", "customStorage",
                     "repeatableCommentPresent", "repeatableCommentLen",
                     "repeatableCommentSha256"}
        self.assertTrue(AUTH.ALLOWED_TARGET_FIELDS.isdisjoint(forbidden))

    def test_saved_receipt_paths_are_required_to_be_portable_repo_relative(self) -> None:
        expected = AUTH.MANIFEST.relative_to(AUTH.REPO).as_posix()
        self.assertEqual(AUTH.require_repo_path_claim(expected, AUTH.MANIFEST, "manifest"),
                         expected)
        with self.assertRaises(AUTH.AuthorityError):
            AUTH.require_repo_path_claim(str(AUTH.MANIFEST.resolve()), AUTH.MANIFEST,
                                         "manifest")
        with self.assertRaises(AUTH.AuthorityError):
            AUTH.require_repo_path_claim("reverse-engineering/wrong.tsv", AUTH.MANIFEST,
                                         "manifest")

    def test_external_path_controls_are_authority_owned(self) -> None:
        source = AUTH.SCRIPT.read_text(encoding="utf-8")
        for value in ("probe-external-output", "probe-external-ready",
                      "rejectedBeforePreValidation", "rejectedBeforeTransaction",
                      "exactPreInventoryRestored"):
            self.assertIn(value, source)


if __name__ == "__main__":
    unittest.main()
