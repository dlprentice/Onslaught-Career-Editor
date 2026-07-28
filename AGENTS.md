# Onslaught Toolkit

> Status: active public-primary contributor guide
> Current truth: this is the normal collaboration repository for the Battle Engine Aquila preservation, tooling, and reconstruction project.
> Last updated: 2026-07-28 (body). Header fields added the same day under
> [`DOCUMENTATION.md`](DOCUMENTATION.md); no guidance below was re-reviewed by
> that pass.
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
- Never patch or mutate an installed Battle Engine Aquila directory or original `BEA.exe`; operate on copied targets only.
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

**Default to subagents. The main loop's context is the scarce resource on this
project, and it is the only lane that can hold the whole argument.** Spend it on
judgement — deciding what is true, what to do next, what to reject — not on
reading files a subagent could have read for you.

- Offload **reading, searching, measuring, porting, and drafting**. Keep
  **deciding, adjudicating, and committing**. Agents do not commit.
- Pair substantial work with an **adversary**: a second, read-only agent briefed
  to refute the first. Brief the adversary to attack the *refutations* too — a
  wrong refutation makes you discard good work, and that has happened here.
- Run agents **concurrently** when their work is independent. One message, many
  tool calls.
- A subagent's report is **data, not authority**. Hand-verify anything
  load-bearing before it becomes a claim or a commit. Findings have been reported
  here that did not survive checking.
- **Concurrent agents contaminate each other unless isolated.** Sixteen running at
  once once produced answers to *other agents'* questions, through inherited
  stdin, shared output paths and a shared client socket. Give every agent its own
  output path, and treat a result that does not name its own question as suspect.
- **A stated file lane is advisory. Only a worktree is enforcement.** Telling an
  agent which files it owns does not stop it writing elsewhere, and it should not:
  an agent that needs a one-line `case` in a shared file to make its own work run
  is right to take it. What that costs is the tree — on 2026-07-28 four writing
  lanes interleaved edits into `SimulationTypes.cs`, `FirstFlightGame.cs` and
  `materialize_retail_assets.py`, and no gate could be run until all of them
  finished, because a failure could not be attributed to a lane.
  So: **any lane that writes gets `isolation: "worktree"`. Read-only lanes run
  free and unlimited.** Land worktrees one at a time, gating between each. The
  cost is a few hundred ms of setup per agent; the thing it buys is the ability to
  measure at all while work is in flight.
- **Never stop a writing lane mid-flight to "pause work".** Killing thirteen
  writing agents at once on 2026-07-28 left half-finished edits from every one of
  them in a single shared tree, with no record of which agent wrote what — the
  work was not paused, it was made unattributable. Let a writing lane reach its
  own stopping point, or discard its worktree whole.
- **Do not send global synthetic input by default** — `SendInput`, `keybd_event`,
  `mouse_event`, `SetCursorPos`, and above all PrtScn. The maintainer usually sits
  at this machine while agents run, and global input lands in whatever window has
  focus: a `PrtScn` sent by an agent on 2026-07-27 froze his screen mid-session.
  It is also why retail captures were blocked for days as "needs the user away
  from the keyboard".
  **This is an engineering default, not a prohibition the maintainer imposed** —
  he has said explicitly that nothing is banned. Global input is permissible when
  the machine is known to be unattended and no message-based route exists; say so
  when you use it. Prefer the alternatives regardless, because they work
  unattended, repeat deterministically, and cannot race the user: post messages to
  the target `HWND` (`tools/send_game_window_input.ps1` has a background mode),
  and grab frames from inside the d3d9 proxy at `Present` rather than screenshotting
  the desktop — `PrintWindow` is measured not to work on this game anyway.

## Evidence

- **A behavior or parity claim must cite a capture, a byte comparison, or a test —
  never a code path.** "The code does X" is not evidence that the product does X.
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
- New or edited tracked `.md`: [`DOCUMENTATION.md`](DOCUMENTATION.md) is the
  header contract — Status, Date, Verdict/Summary on everything, plus Evidence
  and Specimen on a finding. `npm run test:doc-headers` gates it, and a document
  is gated from the moment it exists rather than when it is committed.
- Release/public-boundary changes: follow `README.RELEASE.md` and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`.

Commit, push, publication, release, live launch, and mutation remain separately authorized actions.
