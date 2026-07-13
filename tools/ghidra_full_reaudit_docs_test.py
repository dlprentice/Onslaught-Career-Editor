import tempfile
import unittest
import json
from pathlib import Path

import ghidra_full_reaudit_docs as docs


class GhidraFullReauditDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def record(address: str, path: str, old: str = "Old", new: str = "New") -> dict:
        return {
            "address": address,
            "currentName": old,
            "correctedName": new,
            "correctedFields": ["name", "comment"],
            "docFindings": [path],
        }

    def test_current_doc_and_existing_lore_mirror_receive_notice(self) -> None:
        canonical = self.write(
            "reverse-engineering/binary-analysis/functions/Test.md",
            "# Test\n\nExisting truth.\n",
        )
        mirror = self.write(
            "lore-book/reverse-engineering/binary-analysis/functions/Test.md",
            "# Test\n\nExisting truth.\n",
        )
        records = [self.record("0x00401000", canonical.relative_to(self.root).as_posix())]

        result = docs.reconcile_docs(self.root, records, write=True)

        self.assertEqual(result.changed_count, 2)
        for path in (canonical, mirror):
            text = path.read_text(encoding="utf-8")
            self.assertIn(docs.NOTICE_START, text)
            self.assertIn("0x00401000", text)
            self.assertIn("`New` (was `Old`)", text)
            self.assertIn("exact records are in", text)
            self.assertIn("Existing truth.", text)
        self.assertEqual(canonical.read_bytes(), mirror.read_bytes())

    def test_roadmap_and_lore_mirror_render_identical_closeout_link(self) -> None:
        canonical = self.write("roadmap/status.md", "# Status\n\n0x00401000 Old.\n")
        mirror = self.write("lore-book/roadmap/status.md", "# Status\n\n0x00401000 Old.\n")
        record = self.record("0x00401000", canonical.relative_to(self.root).as_posix())

        docs.reconcile_docs(self.root, [record], write=True)

        self.assertEqual(canonical.read_bytes(), mirror.read_bytes())

    def test_discovers_other_re_markdown_that_names_corrected_address(self) -> None:
        routed = self.write(
            "reverse-engineering/binary-analysis/functions/Routed.md",
            "# Routed\n\nPrimary finding.\n",
        )
        discovered = self.write(
            "reverse-engineering/binary-analysis/functions/Discovered.md",
            "# Discovered\n\nHistorical row 0x00401000 used Old.\n",
        )
        records = [self.record("0x00401000", routed.relative_to(self.root).as_posix())]

        result = docs.reconcile_docs(self.root, records, write=True)

        self.assertEqual(result.changed_count, 2)
        self.assertIn(docs.NOTICE_START, discovered.read_text(encoding="utf-8"))

    def test_discovers_exact_old_symbol_without_matching_longer_symbol(self) -> None:
        routed = self.write(
            "reverse-engineering/binary-analysis/functions/Routed.md",
            "# Routed\n\nPrimary finding.\n",
        )
        discovered = self.write(
            "reverse-engineering/binary-analysis/functions/OldName.md",
            "# Old Name\n\nHistorical `CActor__dtor_base` row.\n",
        )
        longer = self.write(
            "reverse-engineering/binary-analysis/functions/Longer.md",
            "# Longer\n\nCurrent `CActor__dtor_base_thunk` row.\n",
        )
        record = self.record(
            "0x00401020",
            routed.relative_to(self.root).as_posix(),
            "CActor__dtor_base",
            "CActor__dtor_base_thunk",
        )

        result = docs.reconcile_docs(self.root, [record], write=True)

        self.assertEqual(result.changed_count, 2)
        self.assertIn(docs.NOTICE_START, discovered.read_text(encoding="utf-8"))
        self.assertNotIn(docs.NOTICE_START, longer.read_text(encoding="utf-8"))

    def test_historical_doc_is_labeled_as_provenance(self) -> None:
        historical = self.write(
            "release/readiness/ghidra_wave.md",
            "# Historical Wave\n\nOriginal result.\n",
        )
        records = [self.record("0x00402000", historical.relative_to(self.root).as_posix())]

        docs.reconcile_docs(self.root, records, write=True)

        text = historical.read_text(encoding="utf-8")
        self.assertIn("Historical record", text)
        self.assertIn("provenance rather than current semantic authority", text)
        self.assertIn("Original result.", text)

    def test_reconciliation_is_idempotent_and_updates_existing_notice(self) -> None:
        target = self.write(
            "reverse-engineering/binary-analysis/functions/Test.md",
            "# Test\n\nBody.\n",
        )
        path = target.relative_to(self.root).as_posix()
        docs.reconcile_docs(self.root, [self.record("0x00403000", path)], write=True)
        first = target.read_text(encoding="utf-8")

        second = docs.reconcile_docs(
            self.root,
            [self.record("0x00403000", path), self.record("0x00403010", path, "A", "B")],
            write=True,
        )
        updated = target.read_text(encoding="utf-8")
        third = docs.reconcile_docs(
            self.root,
            [self.record("0x00403000", path), self.record("0x00403010", path, "A", "B")],
            write=True,
        )

        self.assertNotEqual(first, updated)
        self.assertEqual(second.changed_count, 1)
        self.assertEqual(third.changed_count, 0)
        self.assertEqual(updated.count(docs.NOTICE_START), 1)
        self.assertIn("0x00403010", updated)

    def test_many_corrections_render_compact_count_instead_of_long_label_list(self) -> None:
        target = self.write(
            "reverse-engineering/binary-analysis/functions/Many.md",
            "# Many\n\n" + " ".join(f"0x00405{i:03x}" for i in range(6)) + "\n",
        )
        path = target.relative_to(self.root).as_posix()
        records = [self.record(f"0x00405{i:03x}", path, f"Old{i}", f"New{i}") for i in range(6)]

        docs.reconcile_docs(self.root, records, write=True)

        text = target.read_text(encoding="utf-8")
        self.assertIn("6 correction records referenced in this document", text)
        self.assertNotIn("`New5` (was `Old5`)", text)

    def test_late_heading_does_not_push_notice_below_preamble(self) -> None:
        original = "Current preamble with corrected address.\n\n# Historical Heading\n\nBody.\n"
        notice = "<!-- notice -->\n> Current correction.\n<!-- end -->"

        updated = docs._insert_or_replace_notice(original, notice, "\n")

        self.assertTrue(updated.startswith(notice + "\n\nCurrent preamble"))

    def test_existing_late_notice_is_relocated_and_remains_idempotent(self) -> None:
        original = (
            "Current preamble.\n\n"
            + docs.NOTICE_START
            + "\n> Old notice.\n"
            + docs.NOTICE_END
            + "\n\n# Historical Heading\n\nBody.\n"
        )
        notice = "\n".join((docs.NOTICE_START, "> New notice.", docs.NOTICE_END))

        updated = docs._insert_or_replace_notice(original, notice, "\n")
        repeated = docs._insert_or_replace_notice(updated, notice, "\n")

        self.assertTrue(updated.startswith(notice + "\n\nCurrent preamble"))
        self.assertEqual(updated.count(docs.NOTICE_START), 1)
        self.assertEqual(repeated, updated)

    def test_primary_state_and_reference_source_paths_are_excluded(self) -> None:
        state = self.write(".codex/state/progress.md", "# State\n")
        source = self.write("references/Onslaught/engine.cpp", "// source\n")
        records = [
            self.record("0x00404000", state.relative_to(self.root).as_posix()),
            self.record("0x00404010", source.relative_to(self.root).as_posix()),
        ]

        result = docs.reconcile_docs(self.root, records, write=True)

        self.assertEqual(result.changed_count, 0)
        self.assertEqual(result.excluded_count, 2)
        self.assertEqual(state.read_text(encoding="utf-8"), "# State\n")
        self.assertEqual(source.read_text(encoding="utf-8"), "// source\n")

    def test_parent_traversal_doc_path_is_rejected_without_outside_write(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        record = self.record("0x00404020", "../" + outside.name)

        with self.assertRaisesRegex(ValueError, "repo-relative"):
            docs.reconcile_docs(self.root, [record], write=True)

        self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_absolute_doc_path_is_rejected_without_outside_write(self) -> None:
        outside = self.root.parent / f"{self.root.name}-absolute.md"
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        record = self.record("0x00404030", str(outside.resolve()))

        with self.assertRaisesRegex(ValueError, "repo-relative"):
            docs.reconcile_docs(self.root, [record], write=True)

        self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_check_mode_reports_without_writing(self) -> None:
        target = self.write(
            "reverse-engineering/binary-analysis/functions/Test.md",
            "# Test\n\nBody.\n",
        )
        original = target.read_text(encoding="utf-8")

        result = docs.reconcile_docs(
            self.root,
            [self.record("0x00405000", target.relative_to(self.root).as_posix())],
            write=False,
        )

        self.assertEqual(result.changed_count, 1)
        self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_superseding_duplicate_record_wins_independent_of_manifest_order(self) -> None:
        older = self.record("0x00406000", "reverse-engineering/Old.md", "Old", "First")
        newer = self.record("0x00406000", "reverse-engineering/New.md", "Old", "Final")
        newer["supersedesCursorDeltaRecord"] = True
        first = self.write("first.json", json.dumps({"records": [older]}))
        second = self.write("second.json", json.dumps({"records": [newer]}))

        forward = docs.load_records([first, second])
        reverse = docs.load_records([second, first])

        expected = dict(newer)
        expected["docFindings"] = ["reverse-engineering/New.md", "reverse-engineering/Old.md"]
        self.assertEqual(forward, [expected])
        self.assertEqual(reverse, [expected])

    def test_unmarked_nonidentical_duplicate_record_is_rejected(self) -> None:
        first_record = self.record("0x00406010", "reverse-engineering/A.md", "Old", "A")
        second_record = self.record("0x00406010", "reverse-engineering/B.md", "Old", "B")
        first = self.write("first.json", json.dumps({"records": [first_record]}))
        second = self.write("second.json", json.dumps({"records": [second_record]}))

        with self.assertRaisesRegex(ValueError, "duplicate correction address"):
            docs.load_records([first, second])


if __name__ == "__main__":
    unittest.main()
