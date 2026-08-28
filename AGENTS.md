# Onslaught Toolkit

Status: active — authoritative contributor contract for this repository.
Last updated: 2026-08-12 (execution shape and reviewer use are situational,
optional, and harness-agnostic; one primary integration owner coordinates).
Summary: the mission, evidence boundaries, safety rules, and smallest set of
routes every contributor needs before working on Battle Engine Aquila.

## Mission

This is a full-scope *Battle Engine Aquila* preservation and engineering project
with three coequal, mutually reinforcing outcomes:

1. Fully reverse the retail game—functions, contracts, data, systems, patch
   points, and dormant capabilities—so it can be understood, preserved, patched,
   and modded.
2. Rebuild it in Godot at 1:1 behavioral and experiential parity so the released
   experience runs faithfully and feels like the original game.
3. Ship a polished WinUI 3 preservation toolkit for careers, saves, safe copies,
   patching, media, and the other user-facing capabilities the project proves.

Retail RE feeds reconstruction, and reconstruction exposes the next retail
questions; RE and shared tooling also make safe app features possible. None of
the three outcomes is a side lane or a lower priority. The current user goal
selects where limited attention goes now; it does not redefine the repository's
standing priorities.

Discovering a name or one observed call is not the finish line: recover what
enters, what leaves, what changes, and under which conditions. Carry relevant
contracts into `rebuild/` with focused parity evidence, while retaining findings
that matter independently for patching, modding, and the WinUI app. Honest
unknowns and exact falsifiers are progress; invented semantics are not.
[`GOAL.md`](GOAL.md) defines the standing acceptance targets.

The repository lanes are:

- `reverse-engineering/` — promoted, specimen-bound evidence; start at
  [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md).
- `local-lab/` — ignored working evidence, retail-derived material, scratch
  binaries, captures, and campaign artifacts; read `local-lab/INDEX.md` when it
  exists.
- `tools/` — RE, validation, asset, and controlled-lab instruments.
- `rebuild/` — the GPL-licensed, RE-informed Godot reconstruction. Read
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) and
  [`rebuild/README.md`](rebuild/README.md) before changing it.
- `OnslaughtCareerEditor.WinUI/` — the primary user-facing preservation and
  save/career tool.
- `OnslaughtCareerEditor.AppCore/` — shared save, options, patch-planning,
  media, catalog, and safe-copy correctness.
- `OnslaughtCareerEditor.Cli/` — an unshipped maintainer adapter over AppCore;
  [`CLI.md`](CLI.md) is its headless front door, not a second product lane.

Retired Electron, WPF, and Python app implementations live only in Git history.

## Start from current truth

- Read [`README.MD`](README.MD), this file, and the directly relevant owners.
  Read widely enough to be right: narrow reading has repeatedly produced
  locally correct changes that were wrong against the game.
- [`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership, application flow,
  and dependency direction. Use it to find the implementation owner; use the
  lane's evidence documents to decide what the implementation must do.
- [`GOAL.md`](GOAL.md) states what is wanted. `developer_state.json` carries
  resumable state and evidence pointers, not unquestionable truth. Current user
  intent, code, runtime behavior, and primary evidence outrank stale prose.
- When `local-lab/` exists, its index is essential: a fresh clone cannot see the
  workstation-local evidence corpus. Promote only the smallest reviewed fact a
  source or rebuild path needs; raw and retail-derived material stays local.

## Hard boundaries

Three principles govern writes to a user's files:

1. Nothing irreversible without an explicit informed choice and a verified
   backup made before the write. Make that backup a precondition the caller
   cannot skip—`BinaryPatchEngine.AuthorizeInstalledGameWrite` is the model.
   Never manufacture an "original" from an already modified file.
2. The user's saves are theirs. Never destroy career data as a side effect;
   detect it, name it, and offer to preserve it.
3. The pristine specimen is absolute: `74154bfa…` is the byte-measurement
   baseline. Read it, never write to it.

Also:

- The maintainer's installed `BEA.exe` is deliberately patched for personal
  testing; that is not drift. Read every byte finding from a named pristine
  specimen and include its hash.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve
  length, reserved fields, and unknown bytes.
- Do not track or redistribute retail binaries or assets, converted retail
  material, arbitrary saves, raw debugger logs, bulky captures, Ghidra backups
  or alternate projects, credentials, or `.env*`. The narrow tracked save
  fixture is `tests_shared/fixtures/gold_career_save.bin`.
- Screenshots are captures, not extracted assets. A small deliberate set may be
  tracked for this project's own surfaces only when registered—and only while
  the set stays too small to substitute for owning the game—in
  [`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md);
  bulk frames and asset-viewer substitutes stay local.
- The canonical distributable Ghidra snapshot lives only under
  `reverse-engineering/ghidra/`; live projects and verified backups stay in
  their machine-local owners.
- The GPL rebuild may adapt the pinned GPL source and consume locally
  materialized retail data. Keep retail executables, decompiler output, and
  separately licensed material out of it; preserve file-level provenance and
  terms.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation,
  filesystem, clock, process, network, and GPU APIs. Clients and renderers adapt
  Core state; they do not own simulation truth.
- Do not add hosted CI, release automation, or workflow scaffolding. Validation
  and release gates are local.

## Evidence and reconstruction

- Use the cheapest sufficient authority: pinned GPL source for architecture and
  intent where it exists; retail `data/` for authored content; pristine bytes
  and controlled copied-runtime observations for released behavior. Override
  available source only when retail evidence proves a divergence, and record it.
- Anything the developers shipped may be evidence: RTTI, strings, `FILE` paths,
  registries, assertions, dormant loggers, resource names, traces, data tables,
  and source. Grade and reproduce it; a plausible label is not proof.
- Every behavior claim cites a capture, byte comparison, focused test, or pinned
  source file and line. Decompiler output alone and a model's opinion prove
  nothing. Static evidence establishes only the identities and structures it
  demonstrates; controlled runtime evidence establishes only the causality and
  values it observes.
- Function work should preserve specimen identity, exact body/range identity,
  callers and callees, class ownership, signature, globals and structure fields,
  inputs, outputs, state changes, ordering, failure behavior, confidence,
  unresolved questions, and the cheapest falsifier. Map sufficiently proven
  retail entities to reconstruction owners and tests.
- Account honestly for code, data, padding, library code, ambiguity, and dark
  ranges. "100%" means every item has a defensible terminal state or an explicit
  open question and next instrument—not that every byte executed or received a
  guessed name.
- Prefer a discrete, countable proof gate. `UNSCORED` is not success. Run a
  consequential loop at least twice; when results hit the instrument's noise
  floor, change instruments rather than fit harder.
- Mine existing static evidence, source, level-start traces, and combat traces
  before recording more. Natural traces are broad discovery evidence; authored
  safe-copy scenarios are sparse causal probes for preregistered questions.
- Keep released-behavior evidence, source-informed architecture,
  reconstruction decisions, and remaining hypotheses visibly separate.
- Promote Ghidra changes only after exact program identity, recoverable backup,
  isolated scratch validation, dry-run/apply/readback receipts, and independent
  refutation. Never promote aliased, mismatched, partially applied,
  `UNSCORED`, or refuter-pending claims. The owning procedure is
  [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md).

## Working and delegation

- **Lab evidence is never hard-deleted in one step.** Anything under
  `local-lab/` (and any dated lab output elsewhere) is first **retired** with
  `tools/lab_quarantine.py stage <path> --reason "<why>"`, which moves it to
  `H:\graveyard\lab-quarantine\<date>\` with a tree SHA-256, byte count, and
  manifest row. True deletion happens later, only under space pressure, via
  `lab_quarantine.py purge <id> --reason "<why>"`; the manifest and purge log
  preserve identity for recovery. `restore <id>` brings a staged item back.
  This rule exists because a 2026-08-06 cleanup deleted frozen campaign and
  proof inputs whose identities were hard-pinned in tooling and tests. Later
  rollout replay and surviving twins recovered some bytes exactly, but several
  historical receipts remain genuinely absent; the initial audit checked
  *docs* for references, not *tooling and tests*, and `Remove-Item -Force`
  bypassed the recycle bin.
  Before classifying anything "stale", grep the **tooling and tests** too,
  not only the docs.
- Preserve unrelated and pre-existing work, especially in a dirty tree. Make
  the smallest coherent change that closes the observed contract; do not widen
  into adjacent cleanup or new machinery without evidence that it is needed.
- Choose single-agent or coordinated multi-agent execution situationally from
  the task's scope, consequence, separability, and available independent work.
  Delegation and external consultation are optional; no model, role pair,
  reviewer count, or matrix is a standing requirement. When additional lanes
  are useful, keep them bounded and keep coordination, adjudication, integration,
  commits, mutations, and public claims with one primary owner.
- A subagent report is data, not authority. Reproduce load-bearing conclusions,
  and verify background reviewers actually reached a working state; a spawn
  receipt alone is not a liveness oracle.
- In the Codex harness, spawn lanes with a minimal context fork and a
  self-contained brief that states the lane is a subagent, not the primary,
  forbids commits, and names its single output path. Full-context forks have
  produced lanes that acted as the primary; empty forks have produced lanes
  with no task. Always verify a lane's claimed artifacts on disk before acting
  on them.
- Retirement is never a hard-delete. Every graveyard candidate — anything under
  `local-lab/` and any dated lab output elsewhere — is retired directly with
  `tools/lab_quarantine.py stage <path> --reason "<why>"` into manifested
  `H:\graveyard\lab-quarantine\` (tree SHA-256, byte count, manifest row), and
  the source is removed only after exact-copy verification and manifest
  readback. D: and G: are not staging or backup destinations. H: must be mounted
  and writable; the tool fails closed otherwise. `lab_quarantine.py purge`
  stays an explicit, separately logged space-pressure operation. Extract what a
  retired artifact teaches into the durable owners before moving it.
- External CLI reviewers follow the same rule. Keep their lanes read-only unless
  a writing lane is explicitly isolated; preserve prompts and reports under
  `local-lab/`, confirm real work and clean exit, reproduce consequential claims,
  and budget concurrent heavy processes. Never send a hosted reviewer secrets or
  private/raw retail material beyond the user's explicit scope. The standing
  optional situational model selection and harness-agnostic reviewer rule,
  campaign-review guidance, gauntlet loop, and invocation/resource rules are owned by
  [`reverse-engineering/REVIEW-PROTOCOL.md`](reverse-engineering/REVIEW-PROTOCOL.md)
  — read it before launching external reviews, and change it there rather than
  here.
- Read-only lanes may share the checkout but use distinct output paths. A lane
  that writes uses an isolated worktree, does not commit, and is landed or
  discarded as a unit. Verify its base commit before work begins; the integration
  owner checks the exact staged diff before committing. Let writing lanes reach
  a safe stopping point unless the user redirects them.
- Avoid global synthetic input while the machine may be in use. Prefer
  target-window messages and proxy-owned capture; use global input only when the
  machine is known to be unattended and no bounded alternative exists.

## Validation and authority

Root `package.json` owns commands. Choose the smallest existing check that could
realistically falsify the changed contract; [`VALIDATION.md`](VALIDATION.md) is
the gate-selection table. Documentation changes use `git diff --check` plus the
affected link, JSON, command, mirror, and header checks. Rebuild work uses the
focused Core, client, or native gate named by its owner; broad
`npm run test:rebuild` is for genuinely cross-cutting changes.

Release and public-boundary work follows [`README.RELEASE.md`](README.RELEASE.md)
and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`; the first push of a held
backlog requires that clean public-boundary pass.

Commit, push, publication, and release are standing-authorized by the maintainer
(2026-07-30; recorded in `developer_state.json`). That authority is
action-specific: it does not relax the pristine-specimen rule, user-file backup
and choice, save preservation, evidence gates, or public/private boundaries.
