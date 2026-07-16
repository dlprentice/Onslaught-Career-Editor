#!/usr/bin/env python3
"""Focused tests for repo_text_hygiene_check.py rules."""

from __future__ import annotations

import unittest

import repo_text_hygiene_check as hygiene


class RepoTextHygieneRuleTests(unittest.TestCase):
    def test_scans_evidence_text_suffixes(self) -> None:
        for path in [
            "reverse-engineering/binary-analysis/function_mutation_ledger.jsonl",
            "reverse-engineering/scratch/example.goodies_diff.patch",
            "tools/ApplyExample.java",
            "release/readiness/public_candidate_allowlist.tsv",
            "release/readiness/example.csv",
        ]:
            self.assertTrue(hygiene.is_text_file(path))

    def matching_labels(self, path: str, text: str) -> set[str]:
        labels: set[str] = set()
        for rule in hygiene.RULES:
            if rule.applies_to(path) and rule.pattern.search(text):
                labels.add(rule.label)
        return labels

    def matching_path_labels(self, path: str) -> set[str]:
        labels: set[str] = set()
        for rule in hygiene.PATH_RULES:
            if rule.applies_to(path) and rule.pattern.search(path):
                labels.add(rule.label)
        return labels

    def test_flags_tracked_generated_build_and_test_outputs(self) -> None:
        labels = set()
        for path in [
            "OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx",
            "archive/electron-workbench/packages/ui/dist/index.html",
            "OnslaughtCareerEditor.AppCore/obj/Debug/net10.0/project.assets.json",
            "release/artifacts/OnslaughtToolkit.zip",
            "tools/__pycache__/helper.pyc",
        ]:
            labels.update(self.matching_path_labels(path))

        self.assertIn("tracked-generated-build-or-test-output", labels)

    def test_allows_private_mirror_generated_names(self) -> None:
        labels = self.matching_path_labels("game/INSTALL.LOG")

        self.assertNotIn("tracked-generated-build-or-test-output", labels)

    def test_flags_legacy_winui_bundle_helpers_in_active_release_dir(self) -> None:
        labels = set()
        for path in [
            "release/Build-PortableBundle.ps1",
            "release/BUNDLE-LAUNCHER.cmd",
            "release/BUNDLE-README.MD",
        ]:
            labels.update(self.matching_path_labels(path))

        self.assertIn("legacy-winui-bundle-helper-in-active-release-dir", labels)

    def test_requires_private_directive_superseded_banner(self) -> None:
        errors = hygiene.check_required_markers(
            "onslaught_codex_directive.md",
            "# Onslaught Career Editor\n\nProduct direction: Electron + React UI.\n",
        )

        self.assertTrue(any("private-directive-superseded-banner" in error for error in errors))
        self.assertEqual(
            [],
            hygiene.check_required_markers(
                "onslaught_codex_directive.md",
                "Status: superseded historical directive\n",
            ),
        )

    def test_flags_visible_mojibake_markers(self) -> None:
        labels = self.matching_labels(
            "reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md",
            "Index 5 decoded to lat\u00c3\u00aate in an older note.",
        )
        labels.update(self.matching_labels(".gitignore", "/\uf07c"))

        self.assertIn("visible-mojibake-marker", labels)

    def test_flags_private_repo_root_paths_in_archive_docs(self) -> None:
        private_repo_root = (
            "C:"
            + "\\Users"
            + "\\operator"
            + "\\source"
            + "\\Onslaught-Career-Editor-"
            + "private"
            + "\\"
        )
        labels = self.matching_labels(
            "archive/legacy-python/README.md",
            f"`{private_repo_root}apps\\electron`",
        )

        self.assertIn("archive-doc-private-repo-root-path", labels)

    def test_flags_private_repo_root_paths_in_active_docs_and_state(self) -> None:
        private_repo_root = (
            "C:"
            + "\\Users"
            + "\\operator"
            + "\\source"
            + "\\Onslaught-Career-Editor-"
            + "private"
        )
        labels = self.matching_labels(
            "developer_agent_state.json",
            f"`git status` ran in `{private_repo_root}`.",
        )
        labels.update(
            self.matching_labels(
                "release/readiness/public_primary_full_migration_inventory_2026-06-24.md",
                "py -3 tools\\public_primary_migration_inventory.py --check "
                + "--private-root /mnt/c/Users/operator/source/Onslaught-Career-Editor-"
                + "private --require-private-root",
            )
        )
        labels.update(
            self.matching_labels(
                "reverse-engineering/binary-analysis/retail-specimen-manifest-2026-03-14.json",
                '"repo_root": "C:\\\\Users\\\\operator\\\\source\\\\Onslaught-Career-Editor-'
                + 'private"',
            )
        )

        self.assertIn("tracked-private-repo-root-path", labels)

    def test_allows_private_repo_root_paths_in_private_runtime_evidence(self) -> None:
        labels = self.matching_labels(
            "release/readiness/private_runtime_evidence/2026-04-29-media-proof.md",
            "Local proof root: C:\\Users\\operator\\source\\Onslaught-Career-Editor-"
            + "private\\subagents\\runtime-proof.json",
        )

        self.assertNotIn("tracked-private-repo-root-path", labels)

    def test_flags_maintainer_user_root_paths_in_active_docs(self) -> None:
        labels = self.matching_labels(
            "release/readiness/repo_skills_ghidra_policy_inventory_2026-06-25.md",
            "Ghidra project root: C:\\Users\\operator\\Ghidra\\Projects\\BEA.gpr",
        )
        labels.update(
            self.matching_labels(
                "release/readiness/private_runtime_evidence/2026-04-29-media-proof.md",
                "Artifact root: C:\\Users\\operator\\AppData\\Roaming\\Electron",
            )
        )
        labels.update(
            self.matching_labels(
                "reverse-engineering/binary-analysis/ghydra-mcp-runbook.md",
                "Config path: /home/operator/.codex/config.toml",
            )
        )
        labels.update(
            self.matching_labels(
                "MCP_DEBUGGING_OPTIONS.md",
                "WSL config: /home/operator/.codex/config.wsl.toml",
            )
        )

        self.assertIn("tracked-maintainer-user-root-path", labels)

    def test_flags_maintainer_backup_and_export_roots_in_active_docs(self) -> None:
        labels = self.matching_labels(
            "release/readiness/wave1178_carver_current_risk_consolidation_review_2026-06-06.md",
            "Verified backup: Z:\\GhidraBackups\\BEA_20260606_verified",
        )
        labels.update(
            self.matching_labels(
                "lore-book/reverse-engineering/binary-analysis/functions/Carver.cpp.md",
                "Source export root: Z:/dev/ONSLAUGHT2/source/Carver.cpp",
            )
        )
        labels.update(
            self.matching_labels(
                "reverse-engineering/binary-analysis/documentation-audit-pass-2026-02-12.json",
                '"pattern": "Z:\\\\\\\\GhydraMCP-Complete-v2.2.0-rc.2"',
            )
        )
        labels.update(
            self.matching_labels(
                "developer_agent_state.json",
                "Runtime proof archive: Z:\\OnslaughtRuntimeProofs",
            )
        )

        self.assertIn("tracked-maintainer-local-root-path", labels)

    def test_flags_standalone_backup_drive_references_in_active_docs(self) -> None:
        labels = self.matching_labels(
            "release/readiness/ghidra_example.md",
            "The live project backup was verified on `Z:` before mutation.",
        )
        labels.update(
            self.matching_labels(
                "roadmap/legacy-storage-note.md",
                "External backup drives are detached; use backup root while `Z:` is unavailable.",
            )
        )

        self.assertIn("tracked-maintainer-backup-drive-reference", labels)

    def test_allows_decompiler_warning_labels_near_storage_words(self) -> None:
        labels = self.matching_labels(
            "reverse-engineering/binary-analysis/functions/example.cpp.md",
            "WARNING: storage pointer is unchecked in decompiler output.",
        )

        self.assertNotIn("tracked-maintainer-backup-drive-reference", labels)

    def test_flags_stale_current_consult_stack_requiring_gemini_opus(self) -> None:
        labels = self.matching_labels(
            "roadmap/static-to-proof-rebuild-transition-backlog.md",
            "Use bounded normal/adversarial Codex, Grok Composer, Opus, and Gemini consults.",
        )

        self.assertIn("stale-current-consult-stack-requires-gemini-opus", labels)

    def test_flags_top_level_fixture_parity_shorthand(self) -> None:
        labels = self.matching_labels(
            "CURRENT_CAPABILITIES.md",
            "C# is retained until the TypeScript implementation is fixture-proven.",
        )
        labels.update(self.matching_labels("README.MD", "TypeScript reaches fixture parity."))

        self.assertIn("top-level-fixture-parity-shorthand", labels)

    def test_flags_stale_repo_hygiene_text_only_description(self) -> None:
        labels = self.matching_labels(
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "`npm run test:repo-hygiene` scans tracked text files for stale placeholders.",
        )
        labels.update(
            self.matching_labels(
                "release/readiness/release_readiness_checklist.md",
                "`npm run test:repo-hygiene` passes for tracked stale-placeholder and renderer preview-mode copy regressions",
            )
        )

        self.assertIn("stale-repo-hygiene-text-only-description", labels)

    def test_flags_winui_archived_product_claims_in_active_docs(self) -> None:
        labels = self.matching_labels(
            "roadmap/gui-expansion.md",
            "Current truth:\n- `OnslaughtCareerEditor.WinUI` is archiving / non-expanding.\n",
        )
        labels.update(
            self.matching_labels(
                "CURRENT_CAPABILITIES.md",
                "`OnslaughtCareerEditor.WinUI` is a historical product surface.\n",
            )
        )
        labels.update(
            self.matching_labels(
                "README.RELEASE.md",
                "Archived `OnslaughtCareerEditor.WinUI` code remains for reference only.\n",
            )
        )

        self.assertIn("stale-winui-archived-product-claim", labels)

    def test_flags_browser_fixture_proof_terms_in_public_docs(self) -> None:
        labels = self.matching_labels(
            "release/readiness/release_lane_strategy_2026-05-01.md",
            "Browser " + "fixture success is useful UI proof, but not native proof.",
        )

        self.assertIn("public-doc-browser-fixture-proof-copy", labels)

    def test_flags_plural_browser_fixture_terms_in_public_docs(self) -> None:
        labels = self.matching_labels(
            "AGENTS.md",
            "Keep browser " + "fixtures deterministic and honest.",
        )
        labels.update(
            self.matching_labels(
                "roadmap/electron-workbench-migration.md",
                "Browser Use ran a fixture " + "job and recorded a browser://"
                + "fixture/path result.",
            )
        )
        labels.update(
            self.matching_labels(
                "roadmap/electron-workbench-migration.md",
                "The only warning was a stale Vite HMR " + "entry from before this pass.",
            )
        )
        labels.update(
            self.matching_labels(
                "roadmap/electron-workbench-migration.md",
                "The only warning was a pre-existing Vite HMR "
                + "warning from before this pass.",
            )
        )

        self.assertIn("public-doc-browser-fixture-proof-copy", labels)

    def test_allows_browser_fixture_terms_in_private_runtime_evidence(self) -> None:
        labels = self.matching_labels(
            "release/readiness/private_runtime_evidence/2026-04-29-game-harness-proof.md",
            "The accepted run used desktop boundaries, not the browser "
            + "fixture lane.",
        )

        self.assertNotIn("public-doc-browser-fixture-proof-copy", labels)

    def test_flags_split_evidence_report_commit_lines(self) -> None:
        labels = self.matching_labels(
            "release/readiness/ralph_loop_goal_evidence_2026-05-01.md",
            "Evidence-report commit:\n\n- `1456dc2324ffe263df8fcc7f6f48f5d94d4a5fcc`\n",
        )

        self.assertIn("split-evidence-report-commit-line", labels)

    def test_flags_stale_maladim_no_effect_claims(self) -> None:
        labels = self.matching_labels(
            "roadmap/re-investigation.md",
            "Test Maladim cheat: User reports no god mode effect despite IsCheatActive(3).",
        )

        self.assertIn("stale-maladim-no-effect-claim", labels)

    def test_flags_stale_maladim_unrevalidated_hypothesis(self) -> None:
        labels = self.matching_labels(
            "roadmap/re-investigation.md",
            "Candidate effects (unrevalidated): MALLOY=goodies, TURKEY=levels, "
            + "Maladim=god mode, Aurore=free camera.",
        )

        self.assertIn("stale-maladim-unrevalidated-hypothesis", labels)

    def test_flags_stale_save_god_mode_no_effect_comments(self) -> None:
        labels = self.matching_labels(
            "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
            "God mode patching removed (Dec 2025) - none of the encodings worked",
        )
        labels.update(
            self.matching_labels(
                "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
                "None had any effect. Likely disabled at runtime or stripped from console port.",
            )
        )

        self.assertIn("stale-save-god-mode-no-effect-comment", labels)

    def test_flags_stale_battleengine_transform_method_name(self) -> None:
        labels = self.matching_labels(
            "release/readiness/battleengine_transform_string_xrefs_2026-05-06.md",
            "This does not prove exact source-to-retail identity for CBattleEngine::"
            + "Transform.",
        )

        self.assertIn("stale-battleengine-transform-method-name", labels)

    def test_flags_migration_era_release_status_labels(self) -> None:
        labels = self.matching_labels(
            "README.MD",
            "Status: active Electron migration\n",
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_migration_era_product_metadata(self) -> None:
        labels = self.matching_labels(
            "package.json",
            '"description": "Electron migration workspace for the Onslaught Toolkit.",',
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_migration_era_roadmap_index_labels(self) -> None:
        labels = self.matching_labels(
            "roadmap/ROADMAP-INDEX.md",
            "| `archive/electron-workbench/apps/electron` + `archive/electron-workbench/packages/ui` | Active product migration | Community toolkit |\n",
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_migration_era_repo_instruction_label(self) -> None:
        labels = self.matching_labels(
            "AGENTS.md",
            "Put Electron migration/product architecture in `roadmap/electron-workbench-migration.md`.\n",
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_migration_era_architecture_doc_intro(self) -> None:
        labels = self.matching_labels(
            "roadmap/electron-workbench-migration.md",
            "# Electron workbench migration\n\n"
            "The future application surface is an Electron + TypeScript workbench.\n"
            "The C# and Python applications remain only as parity surfaces during migration.\n",
        )
        labels.update(
            self.matching_labels(
                "roadmap/agent-workflow.md",
                "AI/agent session patterns for the Electron-first Onslaught Toolkit "
                + "migration and Battle Engine Aquila reverse-engineering work.\n",
            )
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_migration_era_bundle_templates(self) -> None:
        labels = self.matching_labels(
            "archive/electron-workbench/release/ELECTRON-BUNDLE-README.MD",
            "Status: active Electron " + "migration bundle\n",
        )
        labels.update(
            self.matching_labels(
                "release/BUNDLE-README.MD",
                "Electron is the active product " + "migration surface.\n",
            )
        )
        labels.update(
            self.matching_labels(
                "archive/README.md",
                "Electron is the active product " + "migration surface.\n",
            )
        )

        self.assertIn("stale-electron-migration-status-label", labels)

    def test_flags_stale_lore_catalog_migration_titles(self) -> None:
        labels = self.matching_labels(
            "archive/electron-workbench/apps/electron/src/content-browser.ts",
            'title: "Electron migration",',
        )

        self.assertIn("stale-lore-catalog-migration-title", labels)

    def test_flags_stale_electron_release_future_model(self) -> None:
        labels = self.matching_labels(
            "README.RELEASE.md",
            "The next public release model should be Electron-first. "
            + "The curated source-tree/bundle split can remain, but release authority must move "
            + "from WinUI/CLI to Electron packaging plus the TypeScript parity gate.\n",
        )
        labels.update(
            self.matching_labels(
                "README.RELEASE.md",
                "Electron release packaging and bundle smoke must become the final authority.\n",
            )
        )

        self.assertIn("stale-electron-release-future-model", labels)

    def test_flags_stale_state_electron_current_authority(self) -> None:
        labels = self.matching_labels(
            "developer_agent_state.json",
            '"Keep release docs in present-tense Electron-first wording; '
            + 'the Electron packaging lane is current release authority."',
        )
        labels.update(
            self.matching_labels(
                "documentation_agent_state.json",
                '"Keep user self-test docs clear that `npm run archive:electron:dev` '
                + 'is the normal desktop dev launch."',
            )
        )
        labels.update(
            self.matching_labels(
                "developer_agent_state.json",
                '"Archive move batch pending review/commit: apps/electron, packages/ui, '
                + 'packages/contracts, packages/cli, and Electron bundle helper scripts now live '
                + 'under archive/electron-workbench/."',
            )
        )
        labels.update(
            self.matching_labels(
                "documentation_agent_state.json",
                '"Asset extraction docs and the export-game-assets summary now say '
                + 'Electron workbench integration instead of future WinUI integration."',
            )
        )

        self.assertIn("stale-state-electron-current-authority", labels)

    def test_flags_stale_open_winui_doc_supersession_debt(self) -> None:
        labels = self.matching_labels(
            "roadmap/technical-debt.md",
            "- [ ] Mark historical WinUI/AppCore/CLI planning docs as superseded instead of active.\n",
        )

        self.assertIn("stale-open-winui-doc-supersession-debt", labels)

    def test_flags_stale_operator_community_app_label(self) -> None:
        labels = self.matching_labels(
            "roadmap/csharp-python-parity.md",
            "Electron is the active operator/community " + "app.\n",
        )
        labels.update(
            self.matching_labels(
                "archive/electron-workbench/apps/electron/src/release-policy.ts",
                "Useful for " + "operators, but some planning notes may mention private workflow details.\n",
            )
        )

        self.assertIn("stale-operator-community-app-label", labels)

    def test_flags_stale_goodie_78_developer_item_claim(self) -> None:
        labels = self.matching_labels(
            "reverse-engineering/quick-reference/save-goodies.md",
            "| 78 | First concept art | 43 |\n",
        )
        labels.update(
            self.matching_labels(
                "lore-book/reverse-engineering/quick-reference/save-goodies.md",
                "Goodie 78 is a developer item that requires 43 S-ranks.\n",
            )
        )

        self.assertIn("stale-goodie-78-developer-item-claim", labels)


if __name__ == "__main__":
    unittest.main(verbosity=2)
