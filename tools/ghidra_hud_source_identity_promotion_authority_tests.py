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
OWNER_PATH = ROOT / "tools/ghidra_hud_source_identity_promotion_authority.py"
SPEC = importlib.util.spec_from_file_location("hud_identity_authority", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


class HudIdentityPromotionAuthorityTests(unittest.TestCase):
    def test_inventory_allows_only_exact_three_metadata_rows(self) -> None:
        base = rows("address\tname\tbodyMin\tcommentLen\n0x00482050\ta\t0x1\t1\n"
                    "0x00487bc0\tb\t0x2\t1\n0x00488090\tc\t0x3\t1\n")
        post = copy.deepcopy(base)
        for row in post:
            row["name"] = owner.POST[row["address"]]["name"]
            row["signature"] = owner.POST[row["address"]]["signature"]
            row["commentLen"] = owner.POST[row["address"]]["commentLen"]
            row["commentSha256"] = owner.POST[row["address"]]["commentSha256"]
            row["tags"] = owner.POST[row["address"]]["tags"]
        base_by = {row["address"]: row for row in base}
        post_by = {row["address"]: row for row in post}
        changed = {address: [key for key in base_by[address]
                             if base_by[address].get(key) != post_by[address].get(key)]
                   for address in base_by}
        self.assertEqual(set(changed), owner.TARGETS)
        self.assertTrue(all(set(fields) <= owner.ALLOWED_FUNCTION_FIELDS for fields in changed.values()))

    def test_fourth_changed_address_is_rejected_by_contract(self) -> None:
        self.assertEqual(owner.TARGETS,
                         {"0x00482050", "0x00487bc0", "0x00488090"})
        self.assertNotIn("0x0053ecc0", owner.TARGETS)

    def test_structural_fields_are_never_authorized(self) -> None:
        for field in ("bodyBytes", "bodyMin", "bodyMax", "bodyRanges", "bodyDigest",
                      "instrCount", "paramCount", "callingConv", "returnType",
                      "frameSize", "localSize", "paramSize"):
            self.assertNotIn(field, owner.ALLOWED_FUNCTION_FIELDS)

    def test_program_gate_allows_only_comment_digest(self) -> None:
        pre = [{"metric": "functions", "value": "8136"},
               {"metric": "instructions", "value": "549872"},
               {"metric": "commentsSha256", "value": "a"}]
        post = copy.deepcopy(pre)
        post[-1]["value"] = "b"
        with patch.object(owner, "read_tsv", side_effect=[pre, post]):
            result = owner.compare_programs(Path("pre"), Path("post"), "test")
        self.assertEqual(result["changedMetrics"], ["commentsSha256"])
        post[0]["value"] = "8137"
        with patch.object(owner, "read_tsv", side_effect=[pre, post]):
            with self.assertRaisesRegex(owner.AuthorityError, "program metric changes differ"):
                owner.compare_programs(Path("pre"), Path("post"), "test")


if __name__ == "__main__":
    unittest.main()
