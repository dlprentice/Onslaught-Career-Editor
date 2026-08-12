#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import csv
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/ghidra_collision_component_identity_promotion_authority.py"
SPEC = importlib.util.spec_from_file_location("collision_identity_authority", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


class CollisionIdentityPromotionAuthorityTests(unittest.TestCase):
    def test_inventory_allows_only_exact_five_metadata_rows(self) -> None:
        base = rows(
            "address\tname\tbodyMin\tcommentLen\n" +
            "\n".join(f"{address}\told\t0x1\t1" for address in sorted(owner.TARGETS)) + "\n")
        post = copy.deepcopy(base)
        for row in post:
            expected = owner.POST[row["address"]]
            row["name"] = expected["name"]
            row["signature"] = expected["signature"]
            row["commentLen"] = expected["commentLen"]
            row["commentSha256"] = expected["commentSha256"]
            row["tags"] = expected["tags"]
        base_by = {row["address"]: row for row in base}
        post_by = {row["address"]: row for row in post}
        changed = {
            address: [key for key in base_by[address]
                      if base_by[address].get(key) != post_by[address].get(key)]
            for address in base_by
        }
        self.assertEqual(set(changed), owner.TARGETS)
        self.assertTrue(all(
            set(fields) <= owner.ALLOWED_FUNCTION_FIELDS for fields in changed.values()))

    def test_sixth_changed_address_is_rejected_by_contract(self) -> None:
        self.assertEqual(len(owner.TARGETS), 5)
        self.assertNotIn("0x00426900", owner.TARGETS)

    def test_structural_fields_are_never_authorized(self) -> None:
        for field in (
            "bodyBytes", "bodyMin", "bodyMax", "bodyRanges", "bodyDigest",
            "instrCount", "paramCount", "callingConv", "returnType",
            "frameSize", "localSize", "paramSize",
        ):
            self.assertNotIn(field, owner.ALLOWED_FUNCTION_FIELDS)

    def test_program_gate_allows_only_comment_digest(self) -> None:
        pre = [
            {"metric": "functions", "value": "8136"},
            {"metric": "instructions", "value": "549872"},
            {"metric": "commentsSha256", "value": "a"},
        ]
        post = copy.deepcopy(pre)
        post[-1]["value"] = "b"
        with patch.object(owner, "read_tsv", side_effect=[pre, post]):
            result = owner.compare_programs(Path("pre"), Path("post"), "test")
        self.assertEqual(result["changedMetrics"], ["commentsSha256"])
        post[0]["value"] = "8137"
        with patch.object(owner, "read_tsv", side_effect=[pre, post]):
            with self.assertRaisesRegex(owner.AuthorityError, "program metric changes differ"):
                owner.compare_programs(Path("pre"), Path("post"), "test")

    def test_folded_alias_and_runtime_claims_remain_outside_authority(self) -> None:
        source = OWNER_PATH.read_text(encoding="utf-8")
        self.assertIn("No folded-alias exclusion", source)
        self.assertIn('"runtimeClaimsAuthorized": False', source)
        self.assertIn('"rebuildReadyAuthorized": False', source)


if __name__ == "__main__":
    unittest.main()
