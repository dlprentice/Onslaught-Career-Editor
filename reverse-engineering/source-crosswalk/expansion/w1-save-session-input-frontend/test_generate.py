from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generate


ROOT = Path(__file__).resolve().parent
REPOSITORY = generate.repo_root()
SOURCE_ROOT = generate.find_source_root(REPOSITORY)


class GenerateWaveReceiptTests(unittest.TestCase):
    def test_find_local_lab_root_resolves_ordinary_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "Onslaught-Career-Editor"
            local_lab = repository / "local-lab"
            local_lab.mkdir(parents=True)

            self.assertEqual(local_lab, generate.find_local_lab_root(repository))

    def test_find_local_lab_root_resolves_linked_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            primary_repository = Path(temporary) / "Onslaught-Career-Editor"
            local_lab = primary_repository / "local-lab"
            repository = primary_repository / ".worktrees" / "task-id"
            local_lab.mkdir(parents=True)
            repository.mkdir(parents=True)

            self.assertEqual(local_lab, generate.find_local_lab_root(repository))

    def test_generated_receipt_bytes_match_tracked_lf_bytes(self) -> None:
        tracked = (ROOT / "RECEIPT.json").read_bytes()
        self.assertTrue(tracked.endswith(b"\n"))
        self.assertNotIn(b"\r\n", tracked)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            generate.generate(ROOT / "selection.tsv", REPOSITORY, SOURCE_ROOT, output)
            generated = (output / "RECEIPT.json").read_bytes()

        self.assertNotIn(b"\r\n", generated)
        self.assertEqual(tracked, generated)

    def test_readiness_projects_to_conservative_crosswalk_class(self) -> None:
        self.assertEqual(
            "SOURCE_EXACT",
            generate.classification_for_readiness("EXISTING_EXACT_RETAIL_NOTE_VA"),
        )
        self.assertEqual(
            "SOURCE_ANALOG",
            generate.classification_for_readiness("NAMED_RETAIL_ANALOG_PRECISE_TARGET"),
        )
        for readiness in (
            "SOURCE_ONLY_BOUNDED_NO_MATCH",
            "AMBIGUOUS_OVERLOAD_MACRO_NONFUNCTION",
            "EXTERNAL_PROOF_REQUIRED",
        ):
            self.assertEqual("NO_MATCH_FOUND", generate.classification_for_readiness(readiness))

    def test_pc_else_branch_is_not_collapsed_with_non_pc_definition(self) -> None:
        branch = generate.source_target_branch(SOURCE_ROOT / "Career.h", 129, 129)
        self.assertIn("TARGET == PC", branch)
        self.assertNotIn("TARGET != PC", branch)

    def test_inline_operator_body_is_extracted_from_exact_anchor(self) -> None:
        definition = generate.extract_source_definition(SOURCE_ROOT / "Career.h", 35)
        self.assertEqual(35, definition.start_line)
        self.assertIn("grade == 'S'", definition.body)
        self.assertIn("right.grade == 'S'", definition.body)

    def test_multiline_constructor_body_and_initializer_are_preserved(self) -> None:
        definition = generate.extract_source_definition(SOURCE_ROOT / "Player.cpp", 24)
        self.assertEqual(24, definition.start_line)
        self.assertGreaterEqual(definition.end_line, 34)
        self.assertIn("mNumber(number)", definition.text)
        self.assertIn("WipeStats", definition.body)

    def test_source_analysis_separates_fields_constants_and_side_effects(self) -> None:
        definition = generate.extract_source_definition(SOURCE_ROOT / "scheduledevent.h", 16)
        analysis = generate.analyze_source(definition)
        self.assertIn("mData", analysis.fields)
        self.assertIn("NULL", analysis.constants)
        self.assertIn("mNumCreated", analysis.side_effects)
        self.assertTrue(analysis.algorithm)

    def test_initializer_list_is_an_algorithm_and_side_effect(self) -> None:
        definition = generate.extract_source_definition(SOURCE_ROOT / "Career.h", 32)
        analysis = generate.analyze_source(definition)
        self.assertIn("grade", analysis.algorithm)
        self.assertIn("grade", analysis.side_effects)

    def test_return_expression_preserves_cast_and_nested_call_parentheses(self) -> None:
        cast_return = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "activereader.h", 40)
        )
        call_return = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "PCController.h", 21)
        )
        self.assertIn("(T*)mToRead", cast_return.algorithm)
        self.assertIn("LT.JoyButtonOnce(pad_number, button)", call_return.algorithm)
        self.assertNotIn("LT", call_return.fields)

    def test_parenthesized_return_without_whitespace_is_recognized(self) -> None:
        analysis = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "PCMemoryCard.h", 15)
        )
        self.assertEqual("Returns (FALSE).", analysis.algorithm)

    def test_unresolved_evidence_expands_generic_plan_labels_to_named_paths(self) -> None:
        evidence = generate.expanded_evidence(
            {
                "source_file": "eventmanager.h",
                "source_line": "58",
                "readiness": "SOURCE_ONLY_BOUNDED_NO_MATCH",
                "authority": "pinned source;promoted semantic tables;bounded owner aliases",
            }
        )
        self.assertNotIn("promoted semantic tables", evidence)
        self.assertNotIn("bounded owner aliases", evidence)
        self.assertIn("event-manager-scheduler-semantics-2026-08-11.tsv", evidence)
        self.assertIn("reverse-engineering/EVIDENCE-REGISTER.tsv", evidence)

    def test_source_constants_do_not_misclassify_return_types(self) -> None:
        grade = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "Career.h", 35)
        )
        no_op = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "PCMemoryCard.h", 97)
        )
        cast = generate.analyze_source(
            generate.extract_source_definition(SOURCE_ROOT / "scheduledevent.h", 24)
        )
        self.assertNotIn("BOOL", grade.constants)
        self.assertNotIn("BOOL", cast.constants)
        self.assertIn("'S'", grade.constants)
        self.assertIn("false", no_op.constants)

    def test_reviewed_selection_and_source_commit_are_pinned(self) -> None:
        self.assertEqual(generate.EXPECTED_SELECTION_SHA256, generate.sha256(ROOT / "selection.tsv"))
        self.assertEqual(generate.SOURCE_COMMIT, generate.git_head(SOURCE_ROOT))

    def test_rebuild_projection_recognizes_existing_event_scheduler(self) -> None:
        manager = generate._rebuild_projection({"source_file": "eventmanager.h", "source_line": "58"})
        scheduled = generate._rebuild_projection({"source_file": "scheduledevent.h", "source_line": "16"})
        active = generate._rebuild_projection({"source_file": "activereader.h", "source_line": "19"})
        self.assertEqual("PORTED_SOURCE_SHAPE", manager[0])
        self.assertEqual("PARTIAL_OWNER_PRESENT", scheduled[0])
        self.assertEqual("PARTIAL_OWNER_PRESENT", active[0])
        self.assertIn("RetailEventScheduler.cs", manager[1])


if __name__ == "__main__":
    unittest.main()
