# Lane 06 Release Readiness Audit

Date: 2026-03-05
Scope: release docs, readiness artifacts, packaging scripts, README/README.RELEASE, allowlist/redaction/public-candidate logic
Mode: read-only audit; no tracked repo files modified

## Verdict
Current release guidance is not internally clean. The release lane is not in a trustworthy "ready" state because the curated allowlist artifact is stale, one README is described as public-facing but is not part of the public candidate, and the dry-run gate is documented like validation while still rewriting tracked artifacts.

Targeted release files appear clean in the working tree (`git status --short -- ...` returned no changes), so these findings reflect current repo state rather than local scratch edits.

## Findings

### 1. High: `public_candidate_allowlist.tsv` is stale, so the repo's own "authoritative" release artifact is currently wrong
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md:16` says `release/readiness/public_candidate_allowlist.tsv` is authoritative.
- `tools/release_curated_manifest.py:128-143` defines `--check` as the source-of-truth sync check.
- On 2026-03-05, `python3 tools/release_curated_manifest.py --check` exited `1` with:
  - `Selected files: 1054`
  - `current_allow=1026`
  - `missing=28`
  - `extra=0`
- Sample missing paths from the current allowlist:
  - `BinaryPatchEngine.cs`
  - `CardIdPresetEngine.cs`
  - `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs`
  - `release/readiness/curated_release_manifest.json`
  - `release/readiness/public_candidate_allowlist.tsv`
  - `release/readiness/redaction_notes.md`
  - `release/readiness/release_readiness_checklist.md`
  - `roadmap/release-allowlist-profile.md`
  - `tools/release_curated_manifest.py`
  - `tools/release_package.sh`
- `rg '^release/readiness/' release/readiness/public_candidate_allowlist.tsv` returned no matches, even though `release/readiness/curated_release_manifest.json:37-40` explicitly includes four `release/readiness/*` files.
- Impact: any guidance that treats the current allowlist as the accurate public-candidate snapshot is stale until the file is regenerated and checked back in.

### 2. Medium: `README.RELEASE.md` is documented as the public release README, but the release flow does not ship or consume it
- `README.RELEASE.md:3` says it is "the public-facing README intended for release packaging/public repo publishing."
- The curated manifest selects `README.MD` (`release/readiness/curated_release_manifest.json:9`) and does not select `README.RELEASE.md` at all (`include=False`, `exclude=False` when matched against the manifest).
- The current allowlist includes `README.MD` (`release/readiness/public_candidate_allowlist.tsv:20`).
- Repo search found `README.RELEASE.md` referenced only by itself and `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:101`; no release script copies, renames, or otherwise consumes it.
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:96-101` treats both `README.RELEASE.md` and `RELEASE_SCOPE_AND_TEST_COMMANDS.md` as final pre-publish sanity files, but neither is part of the curated public candidate.
- Impact: maintainers can update the wrong README and still ship `README.MD`; the current documentation describes a release artifact that the packaging logic does not use.

### 3. Medium: `release_package.sh --dry-run` is described like validation, but it rewrites tracked artifacts before exiting
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:7` says the runbook performs validation only.
- `release/readiness/release_readiness_checklist.md:12-16` lists `./tools/release_package.sh --dry-run` as a mandatory gate.
- `tools/release_package.sh:16-23` always runs:
  - `python3 tools/release_profile_snapshot.py`
  - `python3 tools/release_curated_manifest.py`
  - `python3 tools/release_curated_manifest.py --check`
- The dry-run branch does not happen until `tools/release_package.sh:184-186`, after those writers have already run.
- Those commands are not read-only:
  - `tools/release_profile_snapshot.py:204-223` writes classification/profile/private-inventory artifacts.
  - `tools/release_curated_manifest.py:140-141` writes `release/readiness/public_candidate_allowlist.tsv` when not in `--check` mode.
- Impact: the current wording is misleading for audit lanes and cautious operators. `--dry-run` means "no archive/publish action," not "no file mutations."

### 4. Medium: redaction/classification guidance overstates what the private inventory actually proves
- `release/readiness/redaction_notes.md:3-34` labels several items under `Hard Exclusions (R4_DENY)`, including:
  - `tools/run_ghidra_batch_rename_headless.sh`
  - `tools/run_ghidra_headless_postscript.sh`
  - `tools/semantic_audit_online.py`
  - `developer_agent_state.json`
  - `subagents/**`
- But `tools/release_profile_snapshot.py:40-82` does not classify those tool paths as `R4_DENY`; they are manifest-only excludes, not classifier-level R4 rules.
- `tools/release_profile_snapshot.py:105-115` writes `private_only_inventory.tsv` from classifier output only, and `tools/release_profile_snapshot.py:85-95` builds that inventory from `git ls-files` only.
- Observed results:
  - `release/readiness/private_only_inventory.tsv` contains `references/Onslaught`, `references/AYAResourceExtractor`, `wave_online_audit/...`, and `game/...`.
  - It does not contain `tools/run_ghidra_batch_rename_headless.sh`.
  - It does not contain the state files.
  - It cannot contain untracked `subagents/**` outputs.
- This conflicts with `release/readiness/release_readiness_checklist.md:17-20`, which says `private_only_inventory.tsv` should include all `R3_CONDITIONAL` and `R4_DENY` families and separately implies state files / `subagents/**` verification through generated artifacts.
- Impact: the checklist currently overstates the proof value of `private_only_inventory.tsv`; some exclusions live only in the curated manifest, and some deny families are untracked so they never appear in the snapshot inventory.

## Summary
The biggest issue is artifact drift: the manifest and allowlist are out of sync right now. After that, the main doc drift is that `README.RELEASE.md` is described as public-facing even though the current public candidate ships `README.MD`. The release dry-run also needs clearer wording because it mutates tracked artifacts, and the redaction docs should stop equating manifest-only excludes with classifier-backed `R4_DENY` inventory.
