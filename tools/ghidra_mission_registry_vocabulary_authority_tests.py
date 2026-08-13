#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import csv
import hashlib
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "vocabulary_authority", HERE / "ghidra_mission_registry_vocabulary_authority.py")
AUTH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUTH)


class VocabularyAuthorityTests(unittest.TestCase):
    def test_all_nonlocal_pins_match(self):
        for path in AUTH.STAMPS:
            if path in (AUTH.PRE_FUNCTIONS, AUTH.PRE_PROGRAM):
                continue
            self.assertEqual(
                (path.stat().st_size, AUTH.sha256_file(path)), AUTH.STAMPS[path], path)

    def test_manifest_is_exact_canonical_75(self):
        rows = AUTH.load_manifest()
        self.assertEqual(len(rows), 75)
        with AUTH.MANIFEST.open(encoding="utf-8", newline="") as stream:
            ordered = list(csv.DictReader(stream, delimiter="\t"))
        payload = "".join(
            f"{row['index']}\t{row['handlerVa']}\t{row['expectedPreName']}\t"
            f"{row['proposedName']}\n" for row in ordered).encode()
        self.assertEqual(len(payload), 4_035)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), AUTH.CANONICAL_SHA)

    def test_manifest_partition_and_exclusions(self):
        rows = AUTH.load_manifest()
        counts = {}
        for row in rows.values():
            counts[row["cohort"]] = counts.get(row["cohort"], 0) + 1
        self.assertEqual(counts, {"DEFAULT54": 54, "MSG5": 5, "CLASS3_16": 16})
        self.assertNotIn("0x0050ff10", rows)
        boundary_rows = AUTH.read_tsv(
            AUTH.REPO / "reverse-engineering/binary-analysis/"
            "mission-script-registry-missing-function-boundaries-2026-08-13.tsv")
        self.assertTrue(set(rows).isdisjoint(
            row["entry"].lower() for row in boundary_rows))
        exclusion = AUTH.validate_static_contract_exclusion(rows)
        self.assertEqual(exclusion, {
            "rows": 34, "overlapWithNormalization": 0,
            "grade": "C1_CANDIDATE_PARTIAL",
            "evidenceClass": "STATIC_HYPOTHESIS_ONLY",
            "metadataMutationAuthorized": False,
        })

    def test_current_projection_join_has_no_drift_or_collision(self):
        rows = AUTH.load_manifest()
        with AUTH.PROJECTION.open(encoding="utf-8", newline="") as stream:
            projection = list(csv.DictReader(
                (line for line in stream if not line.startswith("#")), delimiter="\t"))
        by_address = {row["address"].lower(): row for row in projection}
        current_names = {row["name"] for row in projection}
        self.assertEqual(len(projection), 8_170)
        for address, row in rows.items():
            self.assertEqual(by_address[address]["name"], row["expectedPreName"])
            self.assertNotIn(row["proposedName"], current_names)

    def test_metadata_is_exact_and_complete(self):
        manifest = AUTH.load_manifest()
        metadata = AUTH.load_metadata()
        self.assertEqual(manifest.keys(), metadata.keys())
        self.assertEqual(sum(row["preCommentPresent"] == "false"
                             for row in metadata.values()), 54)
        self.assertEqual(sum("script-command-registry" in row["preTags"].split(",")
                             for row in metadata.values()), 20)
        self.assertTrue(all("tier2-script-facing-name" not in row["preTags"].split(",")
                            for row in metadata.values()))

    def test_metadata_empty_tags_use_lossless_nonwhitespace_sentinel(self):
        lines = AUTH.METADATA.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 76)
        self.assertTrue(all(line.rstrip() == line for line in lines))
        self.assertEqual(sum(line.endswith("\t" + AUTH.EMPTY_TAGS_SENTINEL)
                             for line in lines[1:]), 54)
        self.assertFalse(any(line.endswith("\t") for line in lines))
        decoded = AUTH.load_metadata()
        self.assertEqual(sum(row["preTags"] == "" for row in decoded.values()), 54)

    def test_comment_caveats_remain_cohort_specific(self):
        rows = list(AUTH.load_manifest().values())
        samples = {row["cohort"]: row for row in rows}
        self.assertIn("no behavior claim is added", AUTH.suffix(samples["DEFAULT54"]))
        self.assertIn("neither refutes", AUTH.suffix(samples["CLASS3_16"]))
        messages = {row["index"]: AUTH.message_comment(row)
                    for row in rows if row["cohort"] == "MSG5"}
        self.assertEqual(set(messages), {"17", "28", "36", "90", "91"})
        self.assertTrue(all("queued advancement can reach" in text
                            for text in messages.values()))
        self.assertIn("fixed global `0x0089C328`", messages["17"])
        self.assertIn("registers no callback", messages["28"])
        self.assertIn("not fade", messages["36"])
        self.assertIn("priority remains a plausible", messages["90"])
        self.assertIn("fade claim and tag are withdrawn", messages["91"])
        self.assertEqual(len(set(messages.values())), 5)

    def test_msg5_post_tags_remove_only_refuted_claims(self):
        manifest = AUTH.load_manifest()
        metadata = AUTH.load_metadata()
        by_index = {row["index"]: (row, metadata[address])
                    for address, row in manifest.items() if row["cohort"] == "MSG5"}
        tags = {index: AUTH.post_tags(*values) for index, values in by_index.items()}
        self.assertNotIn("callback-message", tags["28"])
        self.assertNotIn("fade-event", tags["36"])
        self.assertNotIn("fade-event", tags["91"])
        self.assertIn("scheduled-event-7d1", tags["36"])
        self.assertIn("scheduled-event-7d1", tags["91"])
        self.assertIn("priority-message", tags["90"])
        self.assertIn("priority-message", tags["91"])
        for index in by_index:
            self.assertIn("script-command-registry", tags[index])
            self.assertIn("tier2-script-facing-name", tags[index])

    def test_allowed_inventory_fields_exclude_abi_and_boundaries(self):
        forbidden = {"sigSource", "bodyBytes", "bodyMin", "bodyMax", "bodyRanges",
                     "bodyDigest", "instrCount", "paramCount", "callingConv",
                     "returnType", "varArgs", "customStorage", "repeatableCommentSha256"}
        self.assertTrue(AUTH.ALLOWED_TARGET_FIELDS.isdisjoint(forbidden))


if __name__ == "__main__":
    unittest.main()
