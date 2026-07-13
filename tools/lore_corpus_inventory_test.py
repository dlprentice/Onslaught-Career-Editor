#!/usr/bin/env python3
"""Focused tests for the deterministic Lore corpus inventory."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("lore_corpus_inventory.py")
ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "lore" / "corpus-taxonomy.v1.json"


def load_inventory_module():
    if not MODULE_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("lore_corpus_inventory", MODULE_PATH)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LoreCorpusInventoryTests(unittest.TestCase):
    def test_build_inventory_classifies_path_without_copying_source_text(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "lore-book" / "lore" / "history.md"
            canonical = root / "lore" / "history.md"
            source.parent.mkdir(parents=True)
            canonical.parent.mkdir(parents=True)
            separator = chr(92)
            private_text = separator.join(["C:", "Users", "sample", "private", "raw.txt"])
            long_quote = "> This raw private quotation must never enter generated output."
            content = (
                "# History\n\n"
                "Status: review needed\n"
                "Last updated: 2026-07-13\n\n"
                f"Discord note at {private_text}\n{long_quote}\n"
                "Reference: https://example.org/article\n"
            )
            source.write_text(content, encoding="utf-8")
            canonical.write_text(content, encoding="utf-8")

            policy = {
                "schema": "lore-corpus-taxonomy.v1",
                "inventorySchema": "lore-corpus-inventory.v1",
                "triageBoundary": {
                    "statement": "Deterministic editorial triage signals only.",
                    "notConclusions": ["legal status"],
                },
                "families": [
                    {
                        "id": "narrative-lore",
                        "prefix": "lore-book/lore/",
                        "editorialRole": "reader-facing narrative",
                    }
                ],
                "canonicalMappings": [
                    {
                        "projectionPrefix": "lore-book/lore/",
                        "canonicalPrefix": "lore/",
                    }
                ],
                "sourceRiskSignals": [
                    {"label": "community-testimony", "pattern": "discord"}
                ],
            }

            inventory = module.build_inventory(
                root,
                policy,
                ["lore-book/lore/history.md"],
                {"lore-book/lore/history.md": "2026-07-12"},
            )
            rendered = json.dumps(inventory, sort_keys=True)

            self.assertEqual(inventory["documentCount"], 1)
            self.assertEqual(inventory.get("triageBoundary"), policy["triageBoundary"])
            row = inventory["documents"][0]
            self.assertEqual(row["family"], "narrative-lore")
            self.assertEqual(row["canonicalPath"], "lore/history.md")
            self.assertEqual(row["projectionState"], "equal")
            self.assertEqual(row["triageSignals"]["sourceRiskLabels"], ["community-testimony"])
            self.assertEqual(row["triageSignals"]["quotation"]["blockQuoteLines"], 1)
            self.assertEqual(row["triageSignals"]["externalDomains"], ["example.org"])
            self.assertTrue(row.get("statusMarkerPresent"))
            self.assertNotIn("statusMarkerSha256", row)
            self.assertEqual(row["lastUpdatedMarker"], "2026-07-13")
            self.assertEqual(row["lastCommitDate"], "2026-07-12")
            self.assertNotIn(private_text, rendered)
            self.assertNotIn(long_quote, rendered)
            self.assertNotIn("raw private quotation", rendered)

    def test_render_and_check_detect_drift_without_rewriting_output(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(hasattr(module, "render_inventory"), "render_inventory must exist")
        self.assertTrue(hasattr(module, "check_inventory"), "check_inventory must exist")

        inventory = {
            "schema": "lore-corpus-inventory.v1",
            "documentCount": 0,
            "documents": [],
        }
        expected = json.dumps(inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        self.assertEqual(module.render_inventory(inventory), expected)

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "inventory.json"
            output.write_bytes(expected.encode("utf-8"))
            module.check_inventory(inventory, output)

            crlf_bytes = expected.replace("\n", "\r\n").encode("utf-8")
            output.write_bytes(crlf_bytes)
            with self.assertRaisesRegex(ValueError, "generated inventory is stale"):
                module.check_inventory(inventory, output)
            self.assertEqual(output.read_bytes(), crlf_bytes)

            bom_bytes = b"\xef\xbb\xbf" + expected.encode("utf-8")
            output.write_bytes(bom_bytes)
            with self.assertRaisesRegex(ValueError, "generated inventory is stale"):
                module.check_inventory(inventory, output)
            self.assertEqual(output.read_bytes(), bom_bytes)

            output.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "generated inventory is stale"):
                module.check_inventory(inventory, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "{}\n")

    def test_taxonomy_policy_covers_approved_corpus_families_and_non_conclusions(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(POLICY_PATH.is_file(), "corpus-taxonomy.v1.json must exist")
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

        cases = {
            "lore-book/lore/game-overview.md": "narrative-lore",
            "lore-book/roadmap/status-current.md": "roadmap",
            "lore-book/reverse-engineering/binary-analysis/example.md": "binary-analysis",
            "lore-book/reverse-engineering/game-assets/example.md": "game-assets",
            "lore-book/reverse-engineering/source-code/example.md": "source-code",
            "lore-book/reverse-engineering/quick-reference/example.md": "quick-reference",
            "lore-book/reverse-engineering/save-file/example.md": "save-file",
            "lore-book/reverse-engineering/project-meta/example.md": "project-meta",
            "lore-book/reverse-engineering/game-mechanics/example.md": "game-mechanics",
            "lore-book/BOOK.md": "front-door",
            "lore-book/reverse-engineering/RE-INDEX.md": "top-level-re",
        }
        for path, expected_family in cases.items():
            with self.subTest(path=path):
                family, _ = module.classify_family(path, policy)
                self.assertEqual(family, expected_family)

        boundary = policy["triageBoundary"]
        self.assertIn("triage signals only", boundary["statement"])
        self.assertEqual(
            boundary["notConclusions"],
            ["historical truth", "legal status", "release safety", "rights status"],
        )

    def test_prefix_rules_use_longest_match_and_exact_file_boundaries(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        policy = {
            "families": [
                {
                    "id": "generic-re",
                    "prefix": "lore-book/reverse-engineering/",
                    "editorialRole": "generic",
                },
                {
                    "id": "binary-analysis",
                    "prefix": "lore-book/reverse-engineering/binary-analysis/",
                    "editorialRole": "specific",
                },
                {
                    "id": "front-door",
                    "prefix": "lore-book/BOOK.md",
                    "editorialRole": "exact file",
                },
            ],
            "canonicalMappings": [
                {
                    "projectionPrefix": "lore-book/reverse-engineering/",
                    "canonicalPrefix": "reverse-engineering/",
                },
                {
                    "projectionPrefix": "lore-book/reverse-engineering/binary-analysis/",
                    "canonicalPrefix": "reviewed-binary-analysis/",
                },
                {
                    "projectionPrefix": "lore-book/BOOK.md",
                    "canonicalPrefix": "BOOK.md",
                },
            ],
        }
        path = "lore-book/reverse-engineering/binary-analysis/example.md"
        self.assertEqual(module.classify_family(path, policy), ("binary-analysis", "specific"))
        self.assertEqual(
            module.canonical_path_for(path, policy),
            "reviewed-binary-analysis/example.md",
        )
        near_file = "lore-book/BOOK.md.backup"
        self.assertEqual(
            module.classify_family(near_file, policy),
            ("unclassified", "requires taxonomy review"),
        )
        self.assertIsNone(module.canonical_path_for(near_file, policy))

    def test_policy_rejects_non_allowlisted_signal_labels(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        policy = {
            "schema": "lore-corpus-taxonomy.v1",
            "allowedSourceRiskLabels": ["community-testimony"],
            "sourceRiskSignals": [
                {"label": "legal-status", "pattern": "example"}
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source-risk label is not allowlisted"):
                module.load_policy(policy_path)

    def test_parse_git_log_dates_keeps_newest_date_for_each_tracked_path(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(hasattr(module, "parse_git_log_dates"), "parse_git_log_dates must exist")
        raw_log = (
            "@@DATE:2026-07-13\n\n"
            "lore-book/lore/new.md\n"
            "lore-book/lore/shared.md\n\n"
            "@@DATE:2026-07-01\n\n"
            "lore-book/lore/shared.md\n"
            "lore-book/lore/old.md\n"
        )
        self.assertEqual(
            module.parse_git_log_dates(raw_log),
            {
                "lore-book/lore/new.md": "2026-07-13",
                "lore-book/lore/old.md": "2026-07-01",
                "lore-book/lore/shared.md": "2026-07-13",
            },
        )

    def test_status_metadata_never_serializes_private_or_arbitrary_source_text(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        separator = chr(92)
        drive_path = separator.join(["C:", "Users", "sample", "private", "raw.txt"])
        posix_path = "/" + "/".join(["home", "sample", "private", "raw.txt"])
        sensitive_note = "named person unpublished note"
        content = (
            "# Heading\n"
            f"Status: {drive_path}\n"
            f"Later: {posix_path}\n"
            f"Note: {sensitive_note}\n"
            "Last updated: 2026-07-13\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "lore-book" / "entry.md"
            source.parent.mkdir(parents=True)
            source.write_text(content, encoding="utf-8")
            policy = {
                "schema": "lore-corpus-taxonomy.v1",
                "inventorySchema": "lore-corpus-inventory.v1",
                "families": [],
                "canonicalMappings": [],
                "sourceRiskSignals": [],
            }
            inventory = module.build_inventory(root, policy, ["lore-book/entry.md"], {})
            row = inventory["documents"][0]
            rendered = module.render_inventory(inventory)
            self.assertTrue(row.get("statusMarkerPresent"))
            self.assertNotIn("statusMarkerSha256", row)
            self.assertEqual(row["lastUpdatedMarker"], "2026-07-13")
            self.assertNotIn(drive_path, rendered)
            self.assertNotIn(posix_path, rendered)
            self.assertNotIn(sensitive_note, rendered)

    def test_external_domains_exclude_local_and_private_endpoint_shapes(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        content = (
            "https://example.org/public "
            "http://localhost:8080/private "
            "http://10.0.0.1/private "
            "https://secret.internal/private "
            "https://machine.corp/private "
            "https://[2001:4860:4860::8888]/public "
            "https://[fd00::1]/private "
            "https://[::ffff:127.0.0.1]/mapped-loopback "
            "https://[::ffff:10.0.0.1]/mapped-private "
            "https://[::ffff:8.8.8.8]/mapped-public "
            "https://[not-ipv6/path "
            "https://bad_host/path "
            "https://example.net]/malformed"
        )
        try:
            domains = module.external_domains(content)
        except ValueError as exc:
            self.fail(f"malformed URL crashed domain extraction: {type(exc).__name__}")
        self.assertEqual(
            domains,
            ["2001:4860:4860::8888", "::ffff:8.8.8.8", "example.org"],
        )

    def test_build_repository_inventory_covers_tracked_packable_corpus(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(
            hasattr(module, "build_repository_inventory"),
            "build_repository_inventory must exist",
        )

        inventory = module.build_repository_inventory(ROOT, POLICY_PATH)
        self.assertEqual(inventory["documentCount"], 955)
        self.assertEqual(sum(inventory["countsByFamily"].values()), 955)
        self.assertEqual(inventory["countsByFamily"]["binary-analysis"], 765)
        self.assertEqual(inventory["countsByFamily"]["narrative-lore"], 15)
        self.assertGreaterEqual(inventory["divergentProjectionCount"], 7)
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(inventory["triageBoundary"], policy["triageBoundary"])

        rendered = module.render_inventory(inventory)
        self.assertEqual(
            set(inventory),
            {
                "schema",
                "taxonomySchema",
                "triageBoundary",
                "documentCount",
                "countsByFamily",
                "divergentProjectionCount",
                "documents",
            },
        )
        expected_row_keys = {
            "path",
            "extension",
            "family",
            "editorialRole",
            "canonicalPath",
            "projectionState",
            "sourceSha256",
            "canonicalSha256",
            "statusMarkerPresent",
            "lastUpdatedMarker",
            "lastCommitDate",
            "triageSignals",
        }
        for row in inventory["documents"]:
            self.assertEqual(set(row), expected_row_keys)
            self.assertEqual(
                set(row["triageSignals"]),
                {
                    "quotation",
                    "sourceRiskLabels",
                    "sourceRiskMatchCounts",
                    "externalDomains",
                },
            )
            self.assertEqual(
                set(row["triageSignals"]["quotation"]),
                {"blockQuoteLines", "maxConsecutiveBlockQuoteLines"},
            )
        self.assertNotIn('"content"', rendered)
        self.assertNotIn('"excerpt"', rendered)
        self.assertNotIn('"statusMarker"', rendered)
        self.assertNotRegex(rendered, r"[A-Za-z]:\\")
        self.assertNotRegex(rendered, r"\\\\[^\s\"]+\\")
        self.assertNotRegex(rendered, r"/(?:home|users|private|mnt)/")
        self.assertNotRegex(rendered, r"~[/\\]")
        self.assertTrue(
            all(row["path"].startswith("lore-book/") for row in inventory["documents"])
        )

    def test_write_inventory_creates_exact_deterministic_bytes(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(hasattr(module, "write_inventory"), "write_inventory must exist")
        inventory = {
            "schema": "lore-corpus-inventory.v1",
            "documentCount": 0,
            "documents": [],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "generated" / "inventory.json"
            module.write_inventory(inventory, output)
            self.assertEqual(output.read_text(encoding="utf-8"), module.render_inventory(inventory))

    def test_main_builds_and_checks_a_small_git_corpus(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(hasattr(module, "main"), "main must exist")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "lore-book" / "lore" / "start.md"
            canonical = root / "lore" / "start.md"
            source.parent.mkdir(parents=True)
            canonical.parent.mkdir(parents=True)
            source.write_text("# Start\n", encoding="utf-8")
            canonical.write_text("# Start\n", encoding="utf-8")
            policy_path = root / "lore" / "corpus-taxonomy.v1.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "schema": "lore-corpus-taxonomy.v1",
                        "inventorySchema": "lore-corpus-inventory.v1",
                        "sourceRoot": "lore-book",
                        "packableExtensions": [".md", ".txt"],
                        "families": [
                            {
                                "id": "narrative-lore",
                                "prefix": "lore-book/lore/",
                                "editorialRole": "reader-facing narrative",
                            }
                        ],
                        "canonicalMappings": [
                            {
                                "projectionPrefix": "lore-book/lore/",
                                "canonicalPrefix": "lore/",
                            }
                        ],
                        "allowedSourceRiskLabels": [],
                        "sourceRiskSignals": [],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Lore Test"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "lore-test@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "--quiet", "-m", "fixture"], cwd=root, check=True)

            output = root / "lore" / "generated" / "corpus-inventory.v1.json"
            common = [
                "--root",
                str(root),
                "--policy",
                str(policy_path),
                "--output",
                str(output),
            ]
            self.assertEqual(module.main([*common, "--build"]), 0)
            self.assertEqual(module.main([*common, "--check"]), 0)
            output.write_text("{}\n", encoding="utf-8")
            self.assertEqual(module.main([*common, "--check"]), 1)

    def test_repository_inventory_rejects_tracked_symlink_mode_before_reading(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "lore-book" / "link.md"
            source.parent.mkdir(parents=True)
            source.write_text("../local-input/note.md", encoding="utf-8")
            policy_path = root / "policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "schema": "lore-corpus-taxonomy.v1",
                        "inventorySchema": "lore-corpus-inventory.v1",
                        "sourceRoot": "lore-book",
                        "packableExtensions": [".md", ".txt"],
                        "families": [],
                        "canonicalMappings": [],
                        "allowedSourceRiskLabels": [],
                        "sourceRiskSignals": [],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Lore Test"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "lore-test@example.invalid"],
                cwd=root,
                check=True,
            )
            blob = subprocess.run(
                ["git", "hash-object", "-w", "lore-book/link.md"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout.strip()
            subprocess.run(
                [
                    "git",
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    f"120000,{blob},lore-book/link.md",
                ],
                cwd=root,
                check=True,
            )
            subprocess.run(["git", "add", "policy.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "--quiet", "-m", "fixture"], cwd=root, check=True)

            with self.assertRaisesRegex(ValueError, "non-regular tracked Lore source"):
                module.build_repository_inventory(root, policy_path)

    def test_inventory_rejects_casefold_colliding_tracked_paths(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        self.assertTrue(
            hasattr(module, "reject_casefold_collisions"),
            "reject_casefold_collisions must exist",
        )

        with self.assertRaisesRegex(ValueError, "case-fold collision"):
            module.reject_casefold_collisions(
                [
                    "lore-book/lore/Entry.md",
                    "lore-book/lore/entry.md",
                ]
            )

    def test_inventory_rejects_non_regular_tracked_canonical_before_reading(self) -> None:
        module = load_inventory_module()
        self.assertIsNotNone(module, "lore_corpus_inventory.py must exist")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "lore-book" / "lore" / "entry.md"
            canonical = root / "lore" / "entry.md"
            source.parent.mkdir(parents=True)
            canonical.parent.mkdir(parents=True)
            source.write_text("# Entry\n", encoding="utf-8")
            canonical.write_text("../local-input/note.md", encoding="utf-8")
            policy = {
                "schema": "lore-corpus-taxonomy.v1",
                "inventorySchema": "lore-corpus-inventory.v1",
                "families": [],
                "canonicalMappings": [
                    {
                        "projectionPrefix": "lore-book/lore/",
                        "canonicalPrefix": "lore/",
                    }
                ],
                "sourceRiskSignals": [],
            }
            with self.assertRaisesRegex(ValueError, "non-regular tracked canonical source"):
                module.build_inventory(
                    root,
                    policy,
                    ["lore-book/lore/entry.md"],
                    {},
                    tracked_modes={
                        "lore-book/lore/entry.md": "100644",
                        "lore/entry.md": "120000",
                    },
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
