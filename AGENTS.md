# Onslaught Toolkit

> Status: active public-primary contributor guide
> Current truth: this is the normal collaboration repository for the Battle Engine Aquila preservation, tooling, and reconstruction project.

## Direction

- `OnslaughtCareerEditor.WinUI/` is the primary user-facing Windows app.
- `OnslaughtCareerEditor.AppCore/` owns shared save, options, patch-planning, media, catalog, and safe-copy correctness.
- `OnslaughtCareerEditor.Cli/` is the supported C# helper CLI.
- `tools/` contains Python RE, validation, asset, and lab tooling; it is not a product GUI lane.
- `rebuild/` is the GPL-licensed, RE-informed original-code reconstruction lane.
- Retired Electron, WPF, and Python app implementations live only in Git history; they are not source lanes.

## Hard Boundaries

- Read `README.MD` and only the files directly related to the change.
- Do not add game binaries, extracted assets, copied executables, arbitrary save payloads, raw debugger logs, full Ghidra projects/backups, credentials, `.env*`, or bulky runtime captures. The tracked regression fixture `tests_shared/fixtures/gold_career_save.bin` is the narrow exception.
- Never patch or mutate an installed Battle Engine Aquila directory or original `BEA.exe`; operate on copied targets only.
- Do not synthesize `.bes` saves from scratch. Start from a real baseline and preserve unknown bytes.
- Keep public claims bounded to demonstrated source, static evidence, controlled copied-runtime evidence, or focused tests. Separate proven behavior from plans and reconstruction aspirations.
- Do not add hosted CI, release automation, or workflow scaffolding. Validation is local.
- Preserve public/private, license, attribution, and provenance boundaries.
- The GPL-licensed `rebuild/` lane is RE-informed, not strict clean-room work. Keep proprietary assets, binaries, copied source text, and generated retail payloads outside it.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation, filesystem, clock, process, network, and GPU APIs; clients and renderers adapt Core state rather than own simulation truth.

## Evidence

- `reverse-engineering/RE-INDEX.md` is the RE front door.
- Static evidence supports only the identities and structures it demonstrates.
- Controlled copied-runtime evidence establishes observed causality, behavior, and measured values.
- Stuart's source and the legacy AYA extractor are references, not proof of Steam behavior or complete format support.
- Use ignored local overlays for proprietary payloads and large lab artifacts; never promote them into Git.

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
