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
| `local-rom-input/` | Large local ROM/input payloads that are useful for extraction or comparison but should not be tracked. |
| `save-attempts/` or `local-saves/` | Local saves and options payloads used for testing. |
| `local-ghidra/`, `ghidra-local/`, or `Ghidra/` | Full local Ghidra projects, databases, exports, and backups. |
| `local-proofs/` | Bulky runtime proof bundles, screenshots, traces, CDB logs, and frame captures. |
| `local-lab/` | Miscellaneous local-only lab material that is too large or payload-like for git. |
| `mcps/` | Local MCP/tooling sandboxes and generated local integration payloads. |
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

`git status --short` is the normal source-change view and intentionally hides
ignored local payloads. When auditing overlay placement, use targeted ignored
checks rather than broad whole-repo ignored scans:

```powershell
git status --short --ignored -- game save-attempts local-rom-input local-proofs local-ghidra ghidra-local local-lab mcps
git check-ignore -v game\BEA.exe local-proofs\OnslaughtRuntimeProofArchive local-ghidra\GhidraBackups
```

Extension ignore rules are a safety net, not an approved placement plan. Put
hard payloads under the approved overlay roots above. If a hard payload appears
as tracked or untracked source, stop and fix the ignore rule or move the payload
into an ignored local overlay. Do not use this rule to hide normal source, docs,
state batons, RE summaries, or agent reports.

Large archives can be exposed through ignored junctions instead of duplicated on
the primary source drive. Keep those junctions under ignored overlay roots such
as `local-proofs/` or `local-ghidra/`.

## Ghidra Note

Agents can work with a local Ghidra project if it exists in an ignored overlay,
but the repo should receive deterministic exports, scripts, markdown, JSON, TSV,
and ledger files instead of binary Ghidra project stores.

Current maintainer-local live project on this workstation:

- Project file: `C:\Users\david\Ghidra\Projects\BEA.gpr`
- Project store: `C:\Users\david\Ghidra\Projects\BEA.rep\`
- Latest verified historical backup pointer: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`

Public clones do not need this database to build or test the app. Use the
tracked Ghidra scripts, exports, ledgers, and RE docs for source work; use the
live Ghidra project only for maintainer-local mutation or read-back proof.
