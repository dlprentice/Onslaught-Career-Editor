# Lane 10 Audit — Tests, Repo Hygiene, Release-Readiness

Scope: tests, documented test commands, repo hygiene, generated/untracked artifacts, and release-readiness structure.

## Findings

1. **High — The curated public candidate ships test suites but excludes the save fixture they currently require, so the shipped validation path is not self-contained.**
   - Evidence:
     - Curated manifest includes both test trees: `release/readiness/curated_release_manifest.json:29-30`
     - The same manifest excludes `save-attempts/**`: `release/readiness/curated_release_manifest.json:43-47`
     - C# tests hard-require the excluded baseline save: `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs:14-24`, `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:16-25`
     - PyQt tests also hard-require the excluded baseline save: `tests_pyqt/test_smoke.py:56-62`, `tests_pyqt/test_save_editor_defaults_unittest.py:8-9`, `tests_pyqt/test_save_editor_defaults_unittest.py:111-116`
     - Release docs present the test suite as a release gate: `release/readiness/release_readiness_checklist.md:22`, `RELEASE_SCOPE_AND_TEST_COMMANDS.md:179-186`
   - Impact:
     - A public-curated repo built from the current allowlist can ship tests that fail immediately because the referenced fixture is not present.
     - This is a release-readiness gap, not just a developer convenience issue, because the documented signoff path depends on those tests.

2. **Medium — `tools/release_package.sh` maintains a narrower internal denylist than the authoritative Python snapshot/manifest flow, so its classification summary can drift from actual release policy.**
   - Evidence:
     - Shell gate deny-exact list only excludes state files plus a couple specials: `tools/release_package.sh:43-49`
     - Authoritative snapshot classifier also denies `AGENTS.md`, `USER_SANITY_CHECK.md`, and both Ghidra runbook docs: `tools/release_profile_snapshot.py:24-34`
     - Curated manifest excludes the same operational files from the public candidate: `release/readiness/curated_release_manifest.json:62-90`
   - Impact:
     - Maintainers can see conflicting release-classification behavior depending on whether they trust the shell gate summary or the Python snapshot/manifest outputs.
     - That weakens release-gate confidence and makes it easier to misread an internal/ops file as public-candidate-safe.

3. **Medium — The new version-overlay patch docs are referenced from tracked indexes, but the docs themselves are currently untracked, so tracked-only release generation will omit them and leave the feature under-documented.**
   - Evidence:
     - Public release generation is tracked-only: `release/readiness/curated_release_manifest.json:1-4`
     - Tracked indexes link to the patch note: `reverse-engineering/binary-analysis/_index.md:28-31`, `reverse-engineering/RE-INDEX.md:75-77`, `lore-book/reverse-engineering/binary-analysis/_index.md:28-31`
     - The current working tree still has both patch-note files as untracked paths:
       - `reverse-engineering/binary-analysis/version-overlay-patch.md`
       - `lore-book/reverse-engineering/binary-analysis/version-overlay-patch.md`
   - Impact:
     - The shipped repo would contain index entries for the watermark patch while omitting the actual note pages.
     - This is both a docs-integrity issue and a repo-hygiene issue because the feature is implemented and documented elsewhere (`BinaryPatchEngine.cs`, `patches/README.md`), but the canonical RE note is not yet part of tracked release inputs.

## Hygiene Summary

- `git ls-files 'OnslaughtCareerEditor.UiTests/bin/*' 'OnslaughtCareerEditor.UiTests/obj/*' 'tests_pyqt/__pycache__/*' 'bin/*' 'obj/*'` returned **0 tracked build/test artifacts**.
- `git ls-files -o --exclude-standard` currently reports **22 untracked paths**.
  - Most are expected audit outputs under `subagents/full_repo_recheck_2026-03-05/**` and are already excluded from release scope.
  - The two non-subagent untracked files are the version-overlay docs called out in Finding 3.

## No Additional Real Risk Found In This Lane

- `requirements.txt` already includes the Python test dependencies used by the documented `pytest` path: `requirements.txt:17-19`
- The C# test harness does not hard-pin a single host path for `dotnet`; it checks `DOTNET_EXE` and several common locations: `OnslaughtCareerEditor.UiTests/CliReadOnlyAndOptionsSafetyTests.cs:207-228`, `OnslaughtCareerEditor.UiTests/SavePatchRegressionTests.cs:416-437`
- Standard generated directories (`bin/`, `obj/`, `__pycache__/`) are ignored by repo policy: `.gitignore:15-17`, `.gitignore:31-33`
