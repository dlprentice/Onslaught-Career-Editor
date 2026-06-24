# Repo Hardening Goal

## Mission

Run a long-horizon repository hardening campaign.

Make this repository materially cleaner, safer, more correct, better documented, and easier to maintain. Iterate deeply. Do not do a superficial pass. Search for real issues, fix them, validate them, record progress, then repeat.

The desired end state is not "perfect code" or "zero bugs." The desired end state is a repo where all high-confidence issues discovered during this campaign have either been fixed, validated, or clearly documented as unsafe/out-of-scope follow-ups.

## Parallel Work Constraint

A separate agent may be working on a WinUI/WPF-inspired Electron UI/UX redesign.

Treat that redesign as out of scope.

Do not:
- redesign screens
- restyle components
- restructure visual hierarchy
- rewrite layout systems
- make speculative UX changes
- compete with the other agent's visual direction

You may touch UI-facing code only when needed for:
- correctness
- build health
- type/lint/test failures
- obvious broken behavior
- stale documentation
- accessibility defects that are clear and low-risk
- safe cleanup that does not alter design direction

## Non-Negotiable Guardrails

- Inspect git status before making changes.
- Preserve unrelated uncommitted work.
- Do not clobber another agent's changes.
- Do not commit unless explicitly instructed.
- Keep changes reviewable.
- Prefer small, safe patches.
- Avoid speculative rewrites.
- Avoid broad architecture changes unless required to fix a concrete defect.
- Do not introduce new dependencies unless strongly justified.
- Do not remove code merely because it appears unused. Verify references, exports, routes, configs, build paths, and runtime usage first.
- Keep public APIs, persisted data formats, IPC contracts, file formats, and user-facing behavior stable unless fixing a demonstrated bug.
- Do not claim the repository has no bugs.
- Do not stop after the first easy improvement.
- If validation fails, investigate before moving to unrelated cleanup.
- If a fix is risky, document it as a follow-up instead of forcing it.

## Progress Ledger

Maintain this file throughout the run:

```text
.codex/state/repo-hardening-progress.md
```

If the file does not exist, create it.

The ledger must track:

- current phase
- files inspected
- findings
- fixes completed
- validation commands run
- validation failures
- remaining risks
- deferred follow-ups
- next planned inspection target

Update the ledger after every meaningful work batch.

Do not rewrite this goal file except to correct obvious typos. Treat this file as the operating contract.

## Evidence Report

Maintain this file before claiming completion:

```text
.codex/state/repo-hardening-evidence.md
```

The evidence report must be treated as the source of truth for whether a run actually satisfied this goal. Do not mark this goal complete merely because no obvious issues remain from the areas inspected.

The evidence report must include:

- Exact git diff summary:
  - `git status --short`
  - `git diff --stat`
  - `git diff --name-only`
  - categorized summary of every changed file
- Validation table for every command run:
  - exact command
  - pass/fail/warn
  - important output
  - whether it ran before or after changes
  - whether it validates build, tests, docs, release policy, Electron runtime, C# parity, or hygiene
- Inspection coverage matrix for required repo areas:
  - root docs
  - release docs
  - package scripts
  - CI config
  - Electron main
  - Electron preload
  - Electron renderer
  - IPC surfaces
  - CLI
  - runtime scripts
  - test suites
  - C# release lane
  - docsync/release tooling
  - public allowlist/release manifest
  - build/package scripts
  - generated artifacts
  - stale TODO/FIXME inventory
- Search evidence for relevant repo-wide scans, including when available:
  - stale product names
  - stale WinUI/WPF wording
  - `TODO`, `FIXME`, `HACK`, and `XXX`
  - deprecated APIs
  - dead references to removed files
  - broken command references
  - old package manager references
  - unsafe Electron patterns
  - unchecked `shell.openExternal` usage
  - `nodeIntegration` and `contextIsolation` assumptions
  - preload API exposure
  - missing docs for scripts
- Deferred issue ledger:
  - exact file or area
  - reason deferred
  - risk level
  - suggested next validation or fix
- Runtime proof status:
  - development build
  - production build
  - renderer smoke
  - CLI smoke
  - Electron bundle policy
  - Electron bundle smoke
  - packaged portable runtime
  - installer/signed release
  - C# parity tests
- Stop justification using only the allowed stop reasons in this file.

## Ralph-Style Loop

Repeat this loop until completion criteria are satisfied.

### 1. Discover

Inspect the repo for real issues.

Areas to inspect:

- README
- setup instructions
- developer docs
- architecture docs
- package scripts
- build config
- lint config
- typecheck config
- test config
- CI config
- Electron main process
- Electron preload code
- Electron renderer code
- IPC boundaries
- security assumptions
- file/path handling
- async flows
- state management
- tests
- fixtures
- generated artifacts
- stale TODO/FIXME comments
- obsolete feature references
- renamed files or commands
- unused imports/exports after verification
- inconsistent naming
- duplicated logic
- fragile error handling
- accessibility issues that are obvious and low-risk

Look specifically for:

- build failures
- test failures
- lint failures
- type errors
- broken imports
- broken paths
- incorrect assumptions
- stale docs
- misleading comments
- dead code
- duplicate code
- brittle helpers
- missing error handling
- bad null/undefined handling
- race conditions
- unsafe IPC patterns
- security footguns
- dependency/config drift
- docs that describe old behavior
- comments that contradict code

### 2. Prioritize

Fix issues in this order:

1. Build, test, lint, and typecheck failures.
2. Runtime bugs and broken user flows.
3. Crash, corruption, data loss, or security risks.
4. Incorrect setup, build, or troubleshooting docs.
5. Stale or misleading comments.
6. Dead code and duplicate code after verification.
7. Small maintainability improvements.
8. Low-risk accessibility improvements.
9. Cosmetic cleanup only when already touching the same area.

Do not prioritize subjective UI redesign work.

### 3. Patch

Make focused changes.

Rules:

- Keep each patch logically related.
- Prefer root-cause fixes.
- Avoid drive-by rewrites.
- Preserve naming conventions unless they are actively misleading.
- Preserve formatting conventions.
- Add or update tests when practical.
- Update docs when behavior, commands, setup, or architecture descriptions change.
- Remove misleading comments.
- Add comments only where they explain non-obvious behavior.
- Do not add comments that merely restate the code.

### 4. Validate

Use the repo's own commands.

Discover commands from:

- package.json
- pnpm/npm/yarn scripts
- Makefile
- justfile
- task runner config
- CI config
- README
- docs

Run the strongest practical validation set available, such as:

- install/dependency checks if needed
- tests
- targeted tests
- lint
- typecheck
- build
- format check
- Electron/package validation
- app-specific smoke checks where available

If validation fails:

- inspect the failure
- fix it if safe
- rerun the relevant command
- record the result in the progress ledger

If a validation command is missing, broken, or impossible in the environment:

- record the exact command attempted
- record the failure reason
- infer the safest narrower validation
- continue only after documenting the limitation

### 5. Review

After each work batch:

- Re-check git status.
- Review the diff.
- Ensure the diff is coherent.
- Ensure no unrelated UI redesign work was introduced.
- Ensure no unrelated files were modified.
- Ensure docs and comments match the final code.
- Ensure validation results are recorded.
- Update the progress ledger.

### 6. Continue

After review, choose the next highest-value inspection target and repeat.

Do not stop merely because one issue was fixed.

Continue until one allowed stop reason is reached and recorded in `.codex/state/repo-hardening-evidence.md`.

Allowed stop reasons:

- At least three full hardening cycles have been completed with evidence, and no high-confidence safe fixes remain from the inspected areas.
- The first cycle proves that no safe issue remains, with clear evidence across the required coverage matrix.
- Remaining work requires product/design judgment.
- Remaining work requires external environment, hardware, native runtime access, private game assets, or packaged-runtime proof unavailable to the current Codex run.
- Further changes would risk clobbering unrelated uncommitted work from another agent.
- The available budget is exhausted.

A hardening cycle means:

1. inspect a new area,
2. find or verify issues,
3. patch or explicitly defer,
4. validate,
5. update both the progress ledger and evidence report.

## Documentation Requirements

Docs must describe the current repo, not planned behavior.

Ensure accuracy for:

- setup
- installation
- development
- testing
- building
- packaging
- troubleshooting
- architecture
- Electron process boundaries
- configuration
- known limitations
- feature behavior
- command examples

Remove or correct:

- stale commands
- obsolete screenshots/references
- old dependency names
- renamed files
- removed features
- misleading TODOs
- vague claims
- future-tense features presented as current behavior

Do not invent roadmap items.

If something is planned but not implemented, label it clearly as planned or deferred.

## Electron-Specific Checks

When applicable, inspect:

- main/preload/renderer separation
- contextIsolation assumptions
- nodeIntegration assumptions
- IPC channel names
- IPC payload validation
- filesystem access
- path traversal risks
- window lifecycle handling
- error handling around app startup
- preload API surface
- renderer assumptions about unavailable APIs
- packaging/build config
- platform-specific paths
- dev/prod behavior differences

Fix only high-confidence issues.

## Test Expectations

When fixing a bug:

- add or update a test if practical
- prefer targeted tests
- avoid large test rewrites
- do not weaken tests to make them pass
- do not delete failing tests unless they are demonstrably obsolete and docs/code are updated accordingly

## Dependency Rules

Do not add dependencies by default.

Before adding a dependency, verify:

- it solves a real problem
- the problem cannot be solved simply with existing code
- it does not increase security or maintenance risk unnecessarily
- it fits the repo's package manager and lockfile conventions

If a dependency is stale or vulnerable:

- prefer safe upgrades only when compatibility is clear
- validate after upgrade
- avoid cascading dependency churn unless necessary

## Cleanup Rules

Safe cleanup includes:

- removing verified unused imports
- removing verified dead code
- simplifying obviously redundant logic
- consolidating duplicated helpers
- correcting names that are clearly misleading
- tightening types
- improving error messages
- replacing misleading comments with accurate ones
- deleting obsolete docs only when clearly superseded

Unsafe cleanup includes:

- deleting exports without reference checks
- changing public APIs
- changing persisted formats
- broad refactors
- speculative architecture changes
- visual redesign
- replacing libraries without need
- changing behavior without a demonstrated defect

## Completion Criteria

This goal is complete only when:

1. Git status has been inspected.
2. The repo has been inspected across code, docs, configs, scripts, and tests.
3. High-confidence bugs found during the campaign have been fixed.
4. Stale docs and misleading comments found during the campaign have been corrected or removed.
5. Relevant validation commands have been run.
6. Validation failures have been fixed or documented with exact reasons.
7. The progress ledger is updated.
8. The final diff is coherent and reviewable.
9. No unrelated UI/UX redesign work was introduced.
10. Remaining risks and follow-ups are clearly listed.
11. `.codex/state/repo-hardening-evidence.md` contains all required evidence sections.
12. The stop reason is one of the allowed stop reasons above and is supported by the evidence report.

## Final Response Required

When stopping, provide:

- Summary of what was inspected.
- Summary of changes made.
- Bugs fixed.
- Docs/comments updated.
- Validation commands run and results.
- Files changed.
- Remaining risks.
- Deferred follow-ups.
- Reason the loop stopped.
- Path to `.codex/state/repo-hardening-evidence.md` and a short explanation of how it supports the stop reason.

Do not say the repo has no bugs. Say what was inspected, what was fixed, and what confidence was gained through validation.
