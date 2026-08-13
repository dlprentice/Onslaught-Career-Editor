#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/ghidra_mission_registry_boundary_authority.py"
SPEC = importlib.util.spec_from_file_location("mission_registry_boundary_authority", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]],
              fields: list[str] | None = None) -> None:
    fields = fields or list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class MissionRegistryBoundaryManifestTests(unittest.TestCase):
    def test_manifest_is_immutable_and_exactly_joins_missing_registry_entries(self) -> None:
        manifest = read_tsv(owner.MANIFEST)
        registry = {row["handlerVa"].lower(): row for row in read_tsv(owner.REGISTRY)}
        self.assertEqual(len(manifest), 34)
        self.assertEqual(owner.sha256_file(owner.MANIFEST), owner.STAMPS[owner.MANIFEST][1])
        self.assertEqual(owner.MANIFEST.stat().st_size, owner.STAMPS[owner.MANIFEST][0])
        self.assertEqual(len({row["entry"] for row in manifest}), 34)
        self.assertEqual([int(row["entry"], 16) for row in manifest],
                         sorted(int(row["entry"], 16) for row in manifest))
        for row in manifest:
            joined = registry[row["entry"].lower()]
            self.assertEqual(row["command"], joined["command"])
            self.assertEqual(row["registryIndex"], joined["index"])
            self.assertEqual(joined["isFunctionEntry"], "False")
            self.assertEqual(int(row["recordVa"], 16),
                             0x0064CE20 + int(row["registryIndex"]) * 0x40)
            self.assertEqual(row["expectedDefaultName"],
                             "FUN_" + row["entry"][2:])

    def test_half_open_ranges_have_exact_counts_digests_and_no_overlap(self) -> None:
        manifest = read_tsv(owner.MANIFEST)
        prior_end = 0
        for row in manifest:
            start, end_exclusive = owner.range_bounds(row["reachableBodyRanges"])
            self.assertEqual(start, int(row["entry"], 16))
            self.assertEqual(end_exclusive - start, int(row["bodyBytes"]))
            self.assertGreaterEqual(start, prior_end)
            prior_end = end_exclusive
            inventory_range = f"{start:08x}:{end_exclusive - 1:08x};".encode("ascii")
            self.assertEqual(hashlib.sha256(inventory_range).hexdigest(),
                             row["bodyRangeSha256"])

    def test_known_endpoint_and_touching_pair_guard_against_plus_one(self) -> None:
        by_command = {row["command"]: row for row in read_tsv(owner.MANIFEST)}
        visible = by_command["SetVisible"]
        self.assertEqual(visible["reachableBodyRanges"], "0x00535ea0-0x00535ecd")
        self.assertEqual(visible["bodyBytes"], "45")
        wind_start, wind_end = owner.range_bounds(
            by_command["SetWindVector"]["reachableBodyRanges"])
        rain_start, _ = owner.range_bounds(
            by_command["SetRainDensity"]["reachableBodyRanges"])
        self.assertEqual(wind_start, 0x00538300)
        self.assertEqual(wind_end, rain_start)


class MissionRegistryBoundaryAuthorityTests(unittest.TestCase):
    def test_restore_gate_keeps_raw_open_and_internal_inventory_counts_distinct(self) -> None:
        project = {"projectName": "BEA", "fileCount": 1, "totalBytes": 1,
                   "structurallyComplete": True, "files": []}
        probe_copy = r"C:\scratch\probe"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "restore.json"
            log = path.with_name("restore.open-probe.log")
            log.write_text("probe\n", encoding="utf-8")
            receipt = {
                "sourceStable": True,
                "copyComparison": {"matches": True},
                "probeCopy": probe_copy,
                "source": project,
                "readonlyOpen": {
                    "opened": True,
                    "contentStable": True,
                    "postOpenComparison": {"matches": True},
                    "observedProgramMd5": owner.PROGRAM_MD5,
                    "observedProgramSha256": owner.PROGRAM_SHA,
                    "observedFunctionCount": owner.PRE_OPEN_FUNCTION_COUNT,
                    "commandArgv": [
                        str(owner.ANALYZE_HEADLESS), probe_copy, "BEA", "-process", "BEA.exe",
                        "-readOnly", "-noanalysis", "-scriptPath", str(owner.REPO / "tools"),
                        "-postScript", owner.OPEN_PROBE.name, "BEA.exe", owner.PROGRAM_MD5,
                        owner.PROGRAM_SHA,
                    ],
                    "probeLog": {
                        "path": log.name,
                        "bytes": log.stat().st_size,
                        "sha256": owner.sha256_file(log),
                    },
                },
            }
            path.write_text(json.dumps(receipt), encoding="utf-8")
            owner.validate_restore(path, project, "PRE restore",
                                   owner.PRE_OPEN_FUNCTION_COUNT)
            with self.assertRaisesRegex(owner.AuthorityError, "program identity"):
                owner.validate_restore(path, project, "PRE restore",
                                       owner.PRE_FUNCTION_COUNT)

    @staticmethod
    def target(address: str, name: str) -> dict[str, str]:
        start = int(address, 16)
        return {
            "entry": address, "expectedDefaultName": name,
            "reachableBodyRanges": f"0x{start:08x}-0x{start + 2:08x}",
            "bodyBytes": "2", "bodyRangeSha256": "range", "instructionCount": "1",
        }

    @staticmethod
    def existing(address: str, name: str) -> dict[str, str]:
        return {"address": address, "name": name, "bodyBytes": "1"}

    @staticmethod
    def added(target: dict[str, str]) -> dict[str, str]:
        address = target["entry"]
        start, end_exclusive = owner.range_bounds(target["reachableBodyRanges"])
        name = target["expectedDefaultName"]
        return {
            "address": address, "name": name, "fqname": name,
            "nameSource": "DEFAULT", "sigSource": "DEFAULT",
            "bodyBytes": target["bodyBytes"], "bodyMin": f"0x{start:08x}",
            "bodyMax": f"0x{end_exclusive - 1:08x}", "bodyRanges": "1",
            "bodyDigest": target["bodyRangeSha256"], "instrCount": "1",
            "paramCount": "0", "callingConv": "unknown", "returnType": "undefined",
            "varArgs": "false", "isThunk": "false", "thunkTarget": "",
            "isExternal": "false", "customStorage": "false", "inline": "false",
            "noReturn": "false", "commentPresent": "false", "commentLen": "0",
            "repeatableCommentPresent": "false", "repeatableCommentLen": "0",
            "tagCount": "0", "tags": "",
        }

    def test_inventory_gate_accepts_only_exact_plus_target_delta(self) -> None:
        targets = {
            "0x00000020": self.target("0x00000020", "FUN_00000020"),
            "0x00000030": self.target("0x00000030", "FUN_00000030"),
        }
        pre = [self.existing("0x00000010", "a"), self.existing("0x00000011", "b")]
        post = [*pre, *(self.added(target) for target in targets.values())]
        with tempfile.TemporaryDirectory() as folder:
            pre_path, post_path = Path(folder) / "pre.tsv", Path(folder) / "post.tsv"
            fields = list(dict.fromkeys(key for row in post for key in row))
            write_tsv(pre_path, pre, fields)
            write_tsv(post_path, post, fields)
            with patch.object(owner, "PRE_FUNCTION_COUNT", 2), \
                 patch.object(owner, "POST_FUNCTION_COUNT", 4), \
                 patch.object(owner, "TARGET_COUNT", 2), \
                 patch.object(owner, "load_targets", return_value=targets):
                result = owner.compare_inventories(pre_path, post_path, "test")
        self.assertEqual(result["preFunctionsUnchanged"], 2)
        self.assertEqual(result["addedAddresses"], sorted(targets))

    def test_inventory_gate_rejects_changed_preexisting_row(self) -> None:
        target = self.target("0x00000020", "FUN_00000020")
        pre = [self.existing("0x00000010", "a")]
        changed = self.existing("0x00000010", "changed")
        post = [changed, self.added(target)]
        with tempfile.TemporaryDirectory() as folder:
            pre_path, post_path = Path(folder) / "pre.tsv", Path(folder) / "post.tsv"
            fields = list(dict.fromkeys(key for row in post for key in row))
            write_tsv(pre_path, pre, fields)
            write_tsv(post_path, post, fields)
            with patch.object(owner, "PRE_FUNCTION_COUNT", 1), \
                 patch.object(owner, "POST_FUNCTION_COUNT", 2), \
                 patch.object(owner, "TARGET_COUNT", 1), \
                 patch.object(owner, "load_targets", return_value={target["entry"]: target}):
                with self.assertRaisesRegex(owner.AuthorityError, "pre-existing"):
                    owner.compare_inventories(pre_path, post_path, "test")

    def test_program_gate_allows_only_exact_function_count_delta(self) -> None:
        pre = [{"metric": "functions", "value": "2"},
               {"metric": "instructions", "value": "9"}]
        post = [{"metric": "functions", "value": "4"},
                {"metric": "instructions", "value": "9"}]
        with tempfile.TemporaryDirectory() as folder:
            pre_path, post_path = Path(folder) / "pre.tsv", Path(folder) / "post.tsv"
            write_tsv(pre_path, pre)
            write_tsv(post_path, post)
            with patch.object(owner, "PRE_FUNCTION_COUNT", 2), \
                 patch.object(owner, "POST_FUNCTION_COUNT", 4), \
                 patch.object(owner, "TARGET_COUNT", 2):
                result = owner.compare_programs(pre_path, post_path, "test")
                post[1]["value"] = "10"
                write_tsv(post_path, post)
                with self.assertRaisesRegex(owner.AuthorityError, "metric changes"):
                    owner.compare_programs(pre_path, post_path, "test")
        self.assertEqual(result["changedMetrics"], ["functions"])


if __name__ == "__main__":
    unittest.main()
