#!/usr/bin/env python3
"""Focused contract tests for the active patch and safe-copy profile catalogs."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import winui_patch_catalog_accounting_check as checker


ROOT = Path(__file__).resolve().parents[1]


class PatchCatalogAccountingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = json.loads(checker.CATALOG.read_text(encoding="utf-8"))
        self.profiles = json.loads(checker.PROFILE_CATALOG.read_text(encoding="utf-8"))

    def validate(self, catalog: dict | None = None, profiles: dict | None = None) -> dict:
        return checker.validate_catalog_and_profiles(
            catalog or copy.deepcopy(self.catalog),
            profiles or copy.deepcopy(self.profiles),
            root=ROOT,
        )

    def row(self, catalog: dict, row_id: str) -> dict:
        return next(row for row in catalog["patches"] if row["id"] == row_id)

    def profile(self, profiles: dict, profile_id: str) -> dict:
        return next(profile for profile in profiles["profiles"] if profile["id"] == profile_id)

    def test_live_catalog_and_profiles_follow_contract(self) -> None:
        summary = self.validate()

        self.assertEqual(29, summary["total"])
        self.assertEqual(20, summary["visible"])
        self.assertEqual(9, summary["hidden"])
        self.assertEqual(17, summary["dependencyEdges"])
        self.assertEqual(118, summary["conflictEdges"])

    def test_appcore_and_python_helper_pin_the_live_catalog_hash(self) -> None:
        digest = checker.assert_catalog_hash_pins()

        self.assertEqual(64, len(digest))
        self.assertTrue(all(character in "0123456789abcdef" for character in digest))

    def test_legacy_references_alias_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["references"] = ["patches/README.md"]

        with self.assertRaisesRegex(checker.AccountingError, "legacy references alias"):
            self.validate(catalog=catalog)

    def test_invalid_or_unequal_byte_spans_are_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["patched_bytes"] = "0"

        with self.assertRaisesRegex(checker.AccountingError, "patched_bytes"):
            self.validate(catalog=catalog)

        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "force_windowed")["patched_bytes"] = "90"

        with self.assertRaisesRegex(checker.AccountingError, "equal byte lengths"):
            self.validate(catalog=catalog)

        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["file_offset"] = f"0x{checker.TARGET_SIZE:X}"

        with self.assertRaisesRegex(checker.AccountingError, "exceeds the target binary"):
            self.validate(catalog=catalog)

    def test_no_op_patch_bytes_are_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        row = self.row(catalog, "resolution_gate")
        row["patched_bytes"] = row["expected_original_bytes"]

        with self.assertRaisesRegex(checker.AccountingError, "no-op mutation"):
            self.validate(catalog=catalog)

    def test_patch_ids_are_unique_case_insensitively(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        duplicate = copy.deepcopy(self.row(catalog, "resolution_gate"))
        duplicate["id"] = "RESOLUTION_GATE"
        catalog["patches"].append(duplicate)

        with self.assertRaisesRegex(checker.AccountingError, "case-insensitive duplicate ids"):
            self.validate(catalog=catalog)

    def test_row_lists_reject_case_insensitive_duplicates(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["preset_eligibility"].append("CUSTOM")

        with self.assertRaisesRegex(checker.AccountingError, "duplicate values"):
            self.validate(catalog=catalog)

    def test_unknown_dependency_and_dependency_cycle_are_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["dependencies"] = ["missing-row"]

        with self.assertRaisesRegex(checker.AccountingError, "unknown dependency"):
            self.validate(catalog=catalog)

        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["dependencies"] = ["force_windowed"]
        self.row(catalog, "force_windowed")["dependencies"] = ["resolution_gate"]

        with self.assertRaisesRegex(checker.AccountingError, "dependency cycle"):
            self.validate(catalog=catalog)

    def test_conflicts_must_be_known_and_symmetric(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["conflicts"] = ["missing-row"]

        with self.assertRaisesRegex(checker.AccountingError, "unknown conflict"):
            self.validate(catalog=catalog)

        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["conflicts"] = ["force_windowed"]

        with self.assertRaisesRegex(checker.AccountingError, "asymmetric conflict"):
            self.validate(catalog=catalog)

    def test_different_overlapping_mutations_require_exclusion(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        left = self.row(catalog, "resolution_gate")
        right = self.row(catalog, "force_windowed")
        right["file_offset"] = left["file_offset"]
        right["expected_original_bytes"] = "CC"
        right["patched_bytes"] = "01"
        right["conflicts"] = []
        right["exclusive_group"] = ""

        with self.assertRaisesRegex(checker.AccountingError, "overlapping mutation"):
            self.validate(catalog=catalog)

    def test_compatible_partial_overlap_still_requires_exclusion(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        left = self.row(catalog, "resolution_gate")
        right = self.row(catalog, "force_windowed")
        right["file_offset"] = left["file_offset"]
        right["expected_original_bytes"] = "CC 11 22 33 44"
        right["patched_bytes"] = "00 55 66 77 88"
        right["conflicts"] = []
        right["exclusive_group"] = ""

        with self.assertRaisesRegex(checker.AccountingError, "overlapping mutation"):
            self.validate(catalog=catalog)

    def test_exclusive_group_peers_must_also_conflict(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        red = self.row(catalog, "frontend_clear_screen_dark_red")
        green = self.row(catalog, "frontend_clear_screen_dark_green")
        red["conflicts"].remove(green["id"])
        green["conflicts"].remove(red["id"])

        with self.assertRaisesRegex(checker.AccountingError, "exclusive group peers must conflict"):
            self.validate(catalog=catalog)

    def test_whitespace_only_exclusive_group_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["exclusive_group"] = " "

        with self.assertRaisesRegex(checker.AccountingError, "exclusive_group cannot be whitespace"):
            self.validate(catalog=catalog)

    def test_each_visible_row_has_a_conflict_free_effective_closure(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pause = self.row(catalog, "pause_o_scan_initializer_experiment")
        pause["dependencies"] = [
            "frontend_clear_screen_dark_red",
            "frontend_clear_screen_dark_green",
        ]

        with self.assertRaisesRegex(checker.AccountingError, "visible row closure contains conflicting rows"):
            self.validate(catalog=catalog)

    def test_visible_closure_injects_pair_required_by_transitive_dependency(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pause = self.row(catalog, "pause_o_scan_initializer_experiment")
        cave = self.row(catalog, "version_overlay_patched_format_cave_string")
        resolution = self.row(catalog, "resolution_gate")
        pause["requires_windowed_pair"] = False
        pause["dependencies"] = [cave["id"]]
        pause["conflicts"] = [resolution["id"]]
        resolution["conflicts"].append(pause["id"])
        cave["requires_windowed_pair"] = True

        with self.assertRaisesRegex(checker.AccountingError, "visible row closure contains conflicting rows"):
            self.validate(catalog=catalog)

    def test_hidden_companions_must_be_dependency_reachable(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pointer = self.row(catalog, "version_overlay_use_patched_format_pointer")
        pointer["dependencies"] = []

        with self.assertRaisesRegex(checker.AccountingError, "orphaned hidden companion"):
            self.validate(catalog=catalog)

    def test_profiles_cannot_select_hidden_or_ineligible_rows(self) -> None:
        profiles = copy.deepcopy(self.profiles)
        compatibility = self.profile(profiles, "compatibility-copy")
        compatibility["patch_keys"].append("version_overlay_patched_format_cave_string")

        with self.assertRaisesRegex(checker.AccountingError, "hidden companion"):
            self.validate(profiles=profiles)

        profiles = copy.deepcopy(self.profiles)
        compatibility = self.profile(profiles, "compatibility-copy")
        compatibility["patch_keys"].append("pause_o_scan_initializer_experiment")

        with self.assertRaisesRegex(checker.AccountingError, "not eligible"):
            self.validate(profiles=profiles)

    def test_patch_rows_cannot_name_unknown_profile_eligibility(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["preset_eligibility"].append("missing-profile")

        with self.assertRaisesRegex(checker.AccountingError, "unknown preset eligibility"):
            self.validate(catalog=catalog)

    def test_profile_eligibility_membership_is_case_insensitive(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        resolution = self.row(catalog, "resolution_gate")
        index = resolution["preset_eligibility"].index("compatibility-copy")
        resolution["preset_eligibility"][index] = "Compatibility-Copy"

        summary = self.validate(catalog=catalog)

        self.assertEqual(29, summary["total"])

    def test_graph_and_profile_patch_references_are_case_insensitive(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        profiles = copy.deepcopy(self.profiles)
        pointer = self.row(catalog, "version_overlay_use_patched_format_pointer")
        pointer["dependencies"][0] = pointer["dependencies"][0].upper()
        compatibility = self.profile(profiles, "compatibility-copy")
        compatibility["patch_keys"][0] = compatibility["patch_keys"][0].upper()
        compatibility["modules"][0]["patch_keys"][0] = (
            compatibility["modules"][0]["patch_keys"][0].upper()
        )

        summary = self.validate(catalog=catalog, profiles=profiles)

        self.assertEqual(29, summary["total"])

    def test_profile_expansion_requires_windowed_pair_and_rejects_conflicts(self) -> None:
        profiles = copy.deepcopy(self.profiles)
        debug = self.profile(profiles, "debug-camera-preview")
        debug["patch_keys"] = [
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_forward_q_hook",
        ]

        with self.assertRaisesRegex(checker.AccountingError, "omits the required windowed pair"):
            self.validate(profiles=profiles)

        catalog = copy.deepcopy(self.catalog)
        profiles = copy.deepcopy(self.profiles)
        compatibility = self.profile(profiles, "compatibility-copy")
        compatibility["patch_keys"].extend(
            ["frontend_clear_screen_dark_red", "frontend_clear_screen_dark_green"]
        )
        for row_id in ("frontend_clear_screen_dark_red", "frontend_clear_screen_dark_green"):
            self.row(catalog, row_id)["preset_eligibility"].append("compatibility-copy")

        with self.assertRaisesRegex(checker.AccountingError, "expands to conflicting rows"):
            self.validate(catalog=catalog, profiles=profiles)

    def test_noncustom_profiles_are_nonempty_and_modules_own_each_row_once(self) -> None:
        profiles = copy.deepcopy(self.profiles)
        compatibility = self.profile(profiles, "compatibility-copy")
        compatibility["patch_keys"] = []

        with self.assertRaisesRegex(checker.AccountingError, "non-custom profile must select a patch row"):
            self.validate(profiles=profiles)

        profiles = copy.deepcopy(self.profiles)
        recommended = self.profile(profiles, "recommended-safe-copy")
        recommended["modules"][0]["patch_keys"].append("extra_graphics_default_on")

        with self.assertRaisesRegex(checker.AccountingError, "module patch ownership is ambiguous"):
            self.validate(profiles=profiles)

    def test_proof_class_and_direct_runtime_evidence_are_row_specific(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "resolution_gate")["proof_level"] = "goodies_wall_runtime_visual_smoke"

        with self.assertRaisesRegex(checker.AccountingError, "proof_level drifted"):
            self.validate(catalog=catalog)

        catalog = copy.deepcopy(self.catalog)
        resolution = self.row(catalog, "resolution_gate")
        resolution["evidence_refs"].remove(
            "release/readiness/winui_safe_copy_live_runtime_smoke_2026-06-17.md"
        )

        with self.assertRaisesRegex(checker.AccountingError, "missing required evidence"):
            self.validate(catalog=catalog)

    def test_rollback_requires_the_verified_full_file_snapshot(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        self.row(catalog, "free_camera_keyboard_backward_q_cave")["rollback_strategy"] = (
            "Rewrite this row's original bytes."
        )

        with self.assertRaisesRegex(checker.AccountingError, "full-file backup"):
            self.validate(catalog=catalog)

    def test_rejected_diagnostics_cannot_be_accepted_evidence(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pause = self.row(catalog, "pause_o_scan_initializer_experiment")
        pause["diagnostic_refs"].remove(
            "release/readiness/winui_free_camera_pause_context_diagnostic_2026-06-18.md"
        )
        pause["evidence_refs"].append(
            "release/readiness/winui_free_camera_pause_context_diagnostic_2026-06-18.md"
        )

        with self.assertRaisesRegex(checker.AccountingError, "diagnostic evidence"):
            self.validate(catalog=catalog)

    def test_diagnostic_status_cannot_be_accepted_evidence(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pause = self.row(catalog, "pause_o_scan_initializer_experiment")
        diagnostic = "release/readiness/winui_controller_mapping_table_diagnostic_2026-06-18.md"
        pause["diagnostic_refs"].remove(diagnostic)
        pause["evidence_refs"].append(diagnostic)

        with self.assertRaisesRegex(checker.AccountingError, "diagnostic evidence"):
            self.validate(catalog=catalog)

    def test_evidence_and_diagnostic_roles_cannot_overlap_by_case(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pause = self.row(catalog, "pause_o_scan_initializer_experiment")
        pause["evidence_refs"].append(pause["diagnostic_refs"][0].upper())

        with self.assertRaisesRegex(checker.AccountingError, "mixes accepted and diagnostic references"):
            self.validate(catalog=catalog)

    def test_diagnostic_refs_must_point_to_classified_diagnostics(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        resolution = self.row(catalog, "resolution_gate")
        resolution["evidence_refs"].remove("patches/README.md")
        resolution["diagnostic_refs"] = ["patches/README.md"]

        with self.assertRaisesRegex(checker.AccountingError, "not classified as diagnostic"):
            self.validate(catalog=catalog)

    def test_hash_pin_extraction_ignores_commented_assignments(self) -> None:
        good = "a" * 64
        stale = "b" * 64
        source = (
            f'// EXPECTED_CATALOG_SHA256 = "{good}"\n'
            f'EXPECTED_CATALOG_SHA256 = "{stale}"\n'
        )

        self.assertEqual(stale, checker.extract_hash_pin(source, "EXPECTED_CATALOG_SHA256"))

    def test_only_orchestrator_state_owns_patch_counters(self) -> None:
        summary = self.validate()
        expected_visible, expected_catalog = checker.expected_state_counters(summary)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            developer = root / "developer_agent_state.json"
            documentation = root / "documentation_agent_state.json"
            orchestrator = root / "re_orchestrator_state.json"
            developer.write_text(json.dumps({"current_focus": "patches"}), encoding="utf-8")
            documentation.write_text(json.dumps({"current_focus": "patch docs"}), encoding="utf-8")
            orchestrator.write_text(
                json.dumps(
                    {
                        "currentCounters": {
                            "visiblePatchRows": expected_visible,
                            "catalogRows": expected_catalog,
                        }
                    }
                ),
                encoding="utf-8",
            )

            checker.assert_state(
                summary,
                state_files=(developer, documentation, orchestrator),
                counter_owner=orchestrator,
            )

            orchestrator.write_text(json.dumps({"currentCounters": {}}), encoding="utf-8")
            with self.assertRaisesRegex(checker.AccountingError, "visiblePatchRows is stale"):
                checker.assert_state(
                    summary,
                    state_files=(developer, documentation, orchestrator),
                    counter_owner=orchestrator,
                )


if __name__ == "__main__":
    unittest.main()
