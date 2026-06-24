# Local Lab Overlay

Status: active
Last updated: 2026-06-24

This public repository is the primary day-to-day working checkout. The repo is
allowed to contain raw project history and working material such as RE notes,
wave evidence summaries, state batons, agent reports, readiness docs, and
scratch checkers. Ignored local lab overlays are reserved for hard payloads that
should not live in git: copied game files, full Ghidra databases/backups,
secrets, build output, and bulky generated runtime captures.

Ignored local overlays can live inside your checkout so agents and tools can use
them, but GitHub will not receive them unless someone deliberately bypasses
`.gitignore`.

## Allowed Local-Only Folders

Use these names when possible:

| Folder | Local purpose |
| --- | --- |
| `game/` or `local-game/` | Your own Battle Engine Aquila install mirror or copied executable/runtime files. |
| `media/` or `local-media/` | Private media/input payloads used for local extraction or validation. |
| `save-attempts/` or `local-saves/` | Local saves and options payloads used for testing. |
| `local-ghidra/` or `Ghidra/` | Full local Ghidra projects, databases, exports, and backups. |
| `local-proofs/` | Bulky runtime proof bundles, screenshots, traces, CDB logs, and frame captures. |
| `GameProfiles/` / `PatchBench/` | Copied game profiles and patch-bench runtime output. |

These paths are intentionally ignored by `.gitignore`.

## Tracked Public Material

The public repo should track:

- WinUI/AppCore/CLI source and tests.
- Patch catalog metadata and safe-copy profile metadata.
- Reverse-engineering summaries, contracts, maps, structured facts, wave notes,
  scratch checkers, and proof summaries that do not embed actual game payloads.
- Tooling that can run against user-supplied local game files or local Ghidra
  projects.
- Documentation that explains current claims, limits, and contribution paths.
- Project state batons and agent reports when they are useful for handoff,
  accounting, or audit history.

## Do Not Commit

Do not commit:

- Original or copied `BEA.exe`, DLLs, game archives, manuals, media, extracted
  textures/models/audio/video, or save files.
- Full Ghidra project databases or backups.
- Raw CDB logs, screenshots, frame captures, or large runtime proof bundles
  that contain copied game output rather than compact summaries.
- Secrets, credentials, local config, and agent session caches.

Narrow exception: `tests_shared/fixtures/gold_career_save.bin` is the tracked
immutable 10,004-byte regression baseline. Keep arbitrary `.bes`, `.bea`,
options, and `save-attempts/` payloads local/ignored.

## Practical Workflow

1. Clone the public repo.
2. Put local-only material in the ignored overlay folders above.
3. Run tools from the repo root so they can discover tracked code/docs and local
   ignored inputs.
4. Before committing, run:

```powershell
git status --short
npm run test:repo-hygiene
npm run test:public-allowlist
```

If a hard payload appears in `git status`, stop and fix the ignore rule or move
the payload into an ignored local overlay. Do not use this rule to hide normal
source, docs, state batons, RE summaries, or agent reports.

## Ghidra Note

Agents can work with a local Ghidra project if it exists in an ignored overlay,
but the repo should receive deterministic exports, scripts, markdown, JSON, TSV,
and ledger files instead of binary Ghidra project stores.
