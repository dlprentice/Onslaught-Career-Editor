# Lane 10 Repo Structure Audit

Date: 2026-03-05
Scope: root repo structure, AGENTS/README/index docs, private-vs-public sensitivity, dead files, submodule references, and release/collaboration confusion.
Method: read-only inspection; no state files edited.

## Summary

The indexed doc trees are in better shape than the repo root. The main collaboration/release risks are:
- included docs that link to files the curated release manifest excludes,
- two competing README surfaces with no single public-release handoff,
- tracked machine-local/scratch artifacts that inflate repo noise,
- release-governance artifacts that disagree unless the maintainer already knows which one is authoritative.

## Findings

### 1. High: curated public docs contain links to files the curated manifest excludes

Why this matters:
- A curated public snapshot can ship with dead links and operator-only references.
- Future collaborators can follow the shipped docs into files that are intentionally absent from the release candidate.

Evidence:
- `release/readiness/curated_release_manifest.json:33-40` includes `reverse-engineering/**`, `lore-book/**`, `roadmap/**`, and `README.MD`.
- The same manifest excludes `AGENTS.md` at `release/readiness/curated_release_manifest.json:68`.
- The same manifest excludes both Ghydra runbook copies at `release/readiness/curated_release_manifest.json:72-73`.
- Included docs linking to excluded `AGENTS.md` include:
  - `README.MD:274`
  - `lore-book/Start-Here.md:10`
  - `lore-book/roadmap/ROADMAP-INDEX.md:69`
  - `roadmap/ROADMAP-INDEX.md:53`
  - `reverse-engineering/save-file/_index.md:60`
  - `reverse-engineering/game-mechanics/_index.md:58`
  - `reverse-engineering/game-assets/_index.md:56`
  - `reverse-engineering/project-meta/_index.md:36`
  - mirrored lore-book copies of those RE indexes
- Included docs linking to excluded Ghydra runbook include:
  - `lore-book/BOOK.md:49`
  - `reverse-engineering/RE-INDEX.md:77`
  - `reverse-engineering/binary-analysis/_index.md:32`
  - `lore-book/reverse-engineering/RE-INDEX.md:77`
  - `lore-book/reverse-engineering/binary-analysis/_index.md:32`

Assessment:
- This is the clearest release-confusion bug in the repo today.

### 2. High: the repo has two README roles, but only one is on the curated release path

Why this matters:
- A maintainer can update the wrong README and think the public release surface is covered.
- The declared public README can silently drift because it is not the README that actually ships.

Evidence:
- `README.RELEASE.md:1-3` says it is the "public-facing README intended for release packaging/public repo publishing."
- `release/readiness/curated_release_manifest.json:5-10` includes `README.MD` but not `README.RELEASE.md`.
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md:21-42` lists `README.MD` in the current root release composition and does not list `README.RELEASE.md`.
- `README.MD:274` also links to `AGENTS.md`, which is excluded from the curated release manifest.

Assessment:
- Right now, `README.RELEASE.md` reads like the intended public entry point, but the release machinery says otherwise.

### 3. Medium: release-governance artifacts disagree in ways that require insider knowledge to interpret correctly

Why this matters:
- The repo has good release tooling, but the supporting artifacts are not self-consistent.
- A future maintainer can consult a generated classification file and reach the wrong conclusion about what ships.

Evidence:
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md:9-17` says the curated allowlist is authoritative.
- `roadmap/release-allowlist-classification.tsv:7` marks `AGENTS.md` as `R0_ALLOW`.
- `roadmap/release-allowlist-classification.tsv:32` marks `USER_SANITY_CHECK.md` as `R0_ALLOW`.
- `roadmap/release-allowlist-classification.tsv:5952` and `:6494` mark both Ghydra runbook paths as `R0_ALLOW`.
- But `release/readiness/curated_release_manifest.json:65-73` excludes `USER_SANITY_CHECK.md`, `AGENTS.md`, and both Ghydra runbooks.

Assessment:
- The repo documents which artifact is authoritative, but the non-authoritative artifacts still look authoritative enough to mislead.

### 4. Medium: tracked machine-local, scratch, and generated artifacts still pollute the root or tracked tree

Why this matters:
- These files are mostly excluded from release, but they still make the working repo look less intentional than the policy docs imply.
- They increase onboarding noise and make it harder to tell what is canonical versus incidental.

Evidence:
- `setuphistory.txt:1-80` is machine-local graphics/adapter capability output, not durable project documentation.
- The curated manifest explicitly excludes `setuphistory.txt` and the zero-byte file `|` at `release/readiness/curated_release_manifest.json:66-67`.
- Tracked scratch/generated artifacts observed during the pass include:
  - `.tmp_cs_tUnyKr/base.bes`
  - `.tmp_cs_tUnyKr/input.bes`
  - `.tmp_cs_tUnyKr/ovr.bes`
  - `OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx`
  - `wave_online_audit/**`
  - `wave_online_audit2/**`
  - root file `|`
- Root binaries `BEA_Widescreen.exe` and `BEA.exe.gzf` are documented as non-targets in `patches/README.md:228-233`, but their root placement still reads like active product surface rather than archival/supporting artifacts.

Assessment:
- None of these are catastrophic alone, but together they create avoidable repo-structure ambiguity.

### 5. Medium: submodule provenance is fork-pinned without an explicit public-collaboration explanation

Why this matters:
- The submodule URLs decide provenance and expected maintenance path.
- Future collaborators may not know whether these are intentionally pinned mirrors, temporary forks, or canonical upstreams.

Evidence:
- `.gitmodules:1-6` points both submodules at `https://github.com/dlprentice/...` fork URLs.
- The curated manifest excludes `references/**` at `release/readiness/curated_release_manifest.json:52`, so these are already treated as a non-public/conditional lane.

Assessment:
- The current setup is workable for the private branch, but it is not self-explanatory for release prep or outside collaboration.

### 6. Low: the root doc surface is broader than the canonical index model and has overlapping intent

Why this matters:
- New collaborators have to infer which root docs are canonical, private, historical, or just convenience notes.

Evidence:
- `CURRENT_CAPABILITIES.md:1-3` and `WHAT_WE_CAN_DO_NOW.md:1-3` are both "current capability / what can we do now" summaries.
- `WHAT_WE_CAN_DO_NOW.md:7-10` already points back to `CURRENT_CAPABILITIES.md`, which suggests overlap rather than clear separation.
- Additional root operational docs such as `USER_SANITY_CHECK.md`, `STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md`, `MCP_DEBUGGING_OPTIONS.md`, `MCP_LIMITATIONS.md`, and `RELEASE_SCOPE_AND_TEST_COMMANDS.md` are useful, but there is no single root-level canonical index that classifies them.

Assessment:
- This is manageable today, but it will keep growing into avoidable orientation debt.

## Healthy Areas

- `reverse-engineering/` and `lore-book/reverse-engineering/` appear structurally mirrored as expected on this pass.
- The release tooling is allowlist-first, not denylist-only, which is the right default for this repo.
- The private/public split is documented clearly enough at policy level; the bigger problem is artifact drift, not missing policy.

## Suggested Cleanup Order

1. Fix shipped dead links by reconciling `AGENTS.md` and Ghydra runbook references with the curated manifest.
2. Decide whether `README.MD` or `README.RELEASE.md` is the actual public entry point, then collapse to one authoritative release README path.
3. Move or untrack machine-local/scratch/generated artifacts that are no longer part of active workflows.
4. Add one short doc note explaining why `references/*` submodules point at fork URLs, or retarget them to canonical upstreams if that is the real intent.
5. Reduce root-doc overlap by naming one root operational index and demoting convenience notes beneath it.
