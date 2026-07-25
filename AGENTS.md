# Onslaught Toolkit

> Status: active public-primary contributor guide
> Current truth: this is the normal collaboration repository for the Battle Engine Aquila preservation, tooling, and reconstruction project.

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

## Validation

Root `package.json` owns commands. Choose the smallest gate that proves the changed contract.

```powershell
npm test
npm run dev
```

- WinUI/AppCore/CLI changes: use the matching focused .NET build/tests.
- Rebuild changes: read `rebuild/PROVENANCE.md` and `rebuild/README.md`; run only the focused Core, Client, or native smoke check matching the change. Use `npm run test:rebuild` only for broad cross-cutting changes.
- Docs changes: use `git diff --check` and only affected link, JSON, command, or mirror checks.
- Release/public-boundary changes: follow `README.RELEASE.md` and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`.

Commit, push, publication, release, live launch, and mutation remain separately authorized actions.
