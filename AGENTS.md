# Onslaught Toolkit

> Status: active public-primary contributor guide
> Current truth: this is the normal collaboration repository for the Battle Engine Aquila preservation, tooling, and reconstruction project.
> Last updated: 2026-08-01. The blanket "never touch an installed game" rule was
> replaced by three principles about backups, saves, and the pristine specimen;
> other sections retain their prior evidence boundaries.
> Summary: how to work in this repository — the hard boundaries, the delegation
> rules, the evidence bar, and which gate a given change has to run.

## Direction

- `OnslaughtCareerEditor.WinUI/` is the primary user-facing Windows app.
- `OnslaughtCareerEditor.AppCore/` owns shared save, options, patch-planning, media, catalog, and safe-copy correctness.
- `OnslaughtCareerEditor.Cli/` is an unshipped maintainer adapter over AppCore,
  not a second product lane.
- `tools/` contains Python RE, validation, asset, and lab tooling; it is not a product GUI lane.
- `rebuild/` is the GPL-licensed, RE-informed original-code reconstruction lane.
- Retired Electron, WPF, and Python app implementations live only in Git history; they are not source lanes.

## Hard Boundaries

- Read `README.MD`, then read widely enough to be right. Prefer the smallest
  *change*, not the smallest amount of reading: this project's recurring failure
  has been locally-correct code that was wrong against the game, and narrow reading
  is how that happens.
- Do not add game binaries, copied executables, arbitrary save payloads, raw
  debugger logs, Ghidra backups or alternate projects, credentials, `.env*`,
  or bulky runtime captures. The canonical distributable Ghidra project lives
  only under `reverse-engineering/ghidra/`. The tracked regression fixture
  `tests_shared/fixtures/gold_career_save.bin` is the narrow save exception.
- **Three principles govern anything that writes to a user's files.** They
  replaced a blanket "never touch an installed game" prohibition on 2026-08-01,
  because a rule that forbids the thing people want produces workarounds rather
  than safety. Permissive where it costs nothing; strict where data can be lost.
  1. **Nothing irreversible without an explicit informed choice AND a verified
     backup made before the write.** The backup has no opt-out. Express it as a
     precondition the calling code cannot skip rather than a step it must
     remember — see `BinaryPatchEngine.AuthorizeInstalledGameWrite`, which
     cannot return permission until a verified original exists beside the target.
     Refuse rather than manufacture: a backup taken from an already-modified file
     and named "original" destroys the only route back.
  2. **The user's saves are theirs.** Nothing may destroy save data as a side
     effect of doing something else. A delete that happens to remove careers is
     the failure this principle exists for; detect them, name them, and offer to
     keep them before proceeding.
  3. **The pristine specimen stays untouchable.** `74154bfa…` is the measurement
     baseline for every byte finding in the RE lane. Read from it, never write to
     it. This one is absolute and is not a safety blanket for anything else.
- The maintainer's own installed `BEA.exe` is deliberately patched for personal
  testing. That is not drift and is not to be flagged. Read byte evidence from a
  pristine specimen and name the specimen file and hash in every byte finding.
- Do not synthesize `.bes` saves from scratch. Start from a real baseline and preserve unknown bytes.
- Keep public claims bounded to demonstrated source, static evidence, controlled copied-runtime evidence, or focused tests. Separate proven behavior from plans and reconstruction aspirations.
- Do not add hosted CI, release automation, or workflow scaffolding. Validation is local.
- Preserve public/private, license, attribution, and provenance boundaries.
- Do not track or redistribute retail game assets or derived conversions.
  Rebuild assets are materialized to ignored paths from a user-provided retail
  installation, with exact hashes, provenance, credits, and third-party terms
  preserved. File extensions are not provenance: project-authored or
  specifically developer-provided assets may be tracked outside those reserved
  local owners when their file-level provenance and terms are clear.
- The GPL-licensed `rebuild/` lane may adapt the pinned GPL reference source and
  consume locally materialized retail data. Keep retail executables, decompiler
  output, and separately licensed third-party material outside it; retain any
  developer-provided material only under its own file-level provenance and terms.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation, filesystem, clock, process, network, and GPU APIs; clients and renderers adapt Core state rather than own simulation truth.

## Delegation

Delegate bounded reading, searching, measuring, porting, and drafting when doing
so materially protects the primary task's context or shortens independent work.
Keep final adjudication, integration, commits, and public claims with one owner.

- A subagent report is data, not authority. Hand-check load-bearing conclusions.
- Pair consequential evidence or architecture work with a read-only adversary;
  routine edits do not need a ceremonial second lane.
- Read-only lanes may share the checkout, but must use distinct output paths.
  Any lane that writes uses an isolated worktree, does not commit, and is landed
  or discarded as a unit. Remove its worktree afterward.
- Let a writing lane reach a safe stopping point unless the user explicitly
  redirects the work. Do not treat killing a shared-tree process as a pause.
- Avoid global synthetic input while the machine may be in use. Prefer
  target-window messages and proxy-owned frame capture; use global input only
  when the machine is known to be unattended and no bounded alternative exists.

## Evidence

- **A released-behavior or parity claim must cite a capture, byte comparison, or
  focused test.** The pinned GPL source is valid architecture, algorithm, and
  intent evidence where that source exists, but a source or decompiler code path
  alone does not prove Steam runtime behavior or final rendered output.
  Reviewing code has repeatedly certified defects here: a half-intensity colour
  transform, a video drawn where retail draws flat colour, and a patched-build
  version string copied into the product all passed code review and green gates.
  Each was found in minutes once output was compared to the game.
- Findings state evidence and a verdict. Hedge boilerplate, restated verdicts, and
  confirmation prose are not deliverables; a measured number and its method are.
- `reverse-engineering/RE-INDEX.md` is the RE front door.
- Local Ghidra install / maintainer project paths and headless posture:
  `reverse-engineering/ghidra/README.md` (machine-local; keep expedition
  overlays in ignored `local-lab/`).
- Static evidence supports only the identities and structures it demonstrates.
- Controlled copied-runtime evidence establishes observed causality, behavior, and measured values.
- Stuart's source is architecture and implementation evidence; the Steam binary
  and controlled runtime observation decide released-behavior deltas. The legacy
  AYA extractor does not establish complete format support.
- Use ignored local overlays for large intermediate and lab artifacts. Promote
  only the smallest reviewed inputs that a live product or rebuild path consumes.

### Iterating toward a bar

Assessed 2026-07-28 against an external method that proposes looping a builder
against a critic until the gap closes. Both a constructive and an adversarial
review are in `local-lab/GAUNTLET-LOOP-ASSESSMENT-*-2026-07-28.md`. The rules
below are what survived both.

- **Iterate only where the bar is DISCRETE and countable. Never against a
  continuous score.** A draw-call table is discrete: 74 draws, each matching
  retail's rectangle, colour and blend state or not, and termination is 74/74.
  A pixel score is continuous, and iterating it here is measurably a fitting
  procedure — the beat-9 and look-axis sweeps produced a 3-kill point whose
  immediate neighbours score 0 and 2, and a null perturbation that changed
  nothing threw the run outright. The objective is chaotic below the
  simulation's own input quantisation.
- **A continuous score can be loud about a defect that does not exist and blind
  to the one that does.** After the arc shell's real hue error was corrected
  (`#7F7F7F` → `#AE8E6E`), mean error over its 1,054 ink texels moved
  31.53 → 31.47. The same estimator had reported a 49 % energy surplus that was
  an artefact.
- **A critic that cannot return UNSCORED is not a gate.** `score_frontend_capture.py`
  returns UNSCORED precisely because "no evidence" must never render as "no
  problem" — and a language model cannot make that distinction about its own
  looking. "I found no gap" and "I was unable to look" are the same sentence.
  Pair any model critic with a mechanical check that can abstain.
- **Run the loop at least twice.** This project builds strong bars and runs them
  roughly once, and that is where its error rate lives: one extra pass over an
  existing sweep found six real errors with no new measurement, two of six
  in-level divergences certified with exact retail numbers did not survive being
  applied, and the measured error rate is about 1-in-6 unadjudicated against 0
  on adjudicated groups.
- **When marginal gain reaches the per-region cross-run noise floor, change
  instrument rather than iterating.** That floor is not one number: it ranges
  from 0.02 % to 36.79 % depending on frame class.
- **Brief an agent with existence claims, not value comparisons from one
  sample.** Wrong existence claims ("this file holds that table", "this sound
  plays") die in one cheap step. A wrong value comparison drawn from a single
  sample of a periodic signal cost a full re-derivation, and a wrong mechanism
  premise cost 32+ parameter dead ends before anyone ran the cheap check.

## Validation

Root `package.json` owns commands. Choose the smallest gate that proves the changed contract.

```powershell
npm test
npm run dev
```

- WinUI/AppCore/CLI changes: use the matching focused .NET build/tests.
- Rebuild changes: read `rebuild/PROVENANCE.md` and `rebuild/README.md`; run only the focused Core, Client, or native smoke check matching the change. Use `npm run test:rebuild` only for broad cross-cutting changes.
- Docs changes: use `git diff --check` and only affected link, JSON, command, or mirror checks.
- New tracked `.md`, and existing documents outside the recorded legacy backlog:
  [`DOCUMENTATION.md`](DOCUMENTATION.md) is the header contract. Run
  `npm run test:doc-headers`; an existing backlog entry may be edited without
  retrofitting unrelated historical metadata, but the backlog may only shrink.
- Release/public-boundary changes: follow `README.RELEASE.md` and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`.

Commit, push, publication, and release are standing-authorized by the maintainer (2026-07-30; recorded in `developer_state.json` under `_AUTHORIZATION_2026_07_30`). The first push of a held backlog follows a clean public-boundary pass per `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`; after that, pushing is routine. The pristine specimen remains untouchable, and anything that writes to a user's files still owes them the backup and the choice, per the principles above.
