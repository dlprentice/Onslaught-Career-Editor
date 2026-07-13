# Local Lab Overlay

Status: active
Last updated: 2026-07-13

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
| `local-ghidra/`, `ghidra-local/`, or `Ghidra/` | Full local Ghidra projects, databases, local-only exports, and backups. |
| `local-proofs/` | Bulky runtime proof bundles, screenshots, traces, CDB logs, and frame captures. |
| `local-lab/` | Miscellaneous local-only lab material that is too large or payload-like for git. `local-lab/rebuild-godot/` is the only allowed init/bootstrap/export output workspace for optional First Flight user-supplied local mesh presentation. |
| `mcps/` | Local MCP/tooling sandboxes and generated local integration payloads. |
| `GameProfiles/` / `PatchBench/` | Copied game profiles and patch-bench runtime output. |

These paths are intentionally ignored by `.gitignore`.

The local rebuild asset workflow reads a user-supplied trusted canonical retail
mirror but never writes to it. Init, export, conversion staging, role activation,
and manifests stay under `local-lab/rebuild-godot/` or a validated child.
Outputs must not overlap game/source/`BEA.exe` roots, tracked source, junctions,
symlinks, or hardlink aliases. FBX is staging input only; manifests activate
explicit self-contained GLB or bounded OBJ roles. Export uses and holds the
exact `references/AYAResourceExtractor/BoxWithTextures.fbx` template plus the
three mutable trusted-local extractor DLLs before output. After manual FBX
conversion, place only the selected GLB/OBJ candidates under
`local-lab/rebuild-godot/staging/from-export/`; bootstrap never activates FBX or
searches export output directly. Bootstrap verifies both role files under one
content-addressed `versions/` generation before publishing `manifest.json` last,
so a failed generation cannot mix with the active manifest. A path or manifest
does not prove retail origin, redistribution rights, or parity.

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

## Storage Hygiene And Retention

Local campaign worktrees, bulky worker logs, raw tool transcripts, temporary
package probes, and generated build/test output are disposable after final
reports are preserved and accepted findings are folded into tracked docs,
state, tests, or source. Final campaign reports and cleanup manifests normally
stay local; track only sanitized summaries that are useful to future
contributors and do not expose private paths or raw payloads.

Assigned scratch volumes, including removable or drive-letter scratch devices,
can be used for temporary worker scratch when mounted and writable. They must
not become the only durable copy of source, current proof evidence, Ghidra
backups, release assets, or other valuable project material.

The active maintainer-local storage posture is to route new backup-producing
Ghidra work and bulky temporary proof outputs to the configured removable
scratch/backup root when available, or another explicitly selected
local/app-owned ignored root, not to hard-coded legacy archive roots. Historical
legacy drive-root references in old wave evidence are provenance only, not
active configuration. Keep exact volume identity, per-run paths, cleanup
manifests, and deletion decisions in ignored local policy notes or
maintainer-private manifests.
Tracked docs and tools should record only sanitized conclusions, proof IDs,
reproduction steps, ledger entries, and configurable environment-variable
names.

Validation and review workers should avoid creating bulky durable outputs
unless they are necessary evidence. Clean reproducible `bin/`, `obj/`,
`TestResults/`, package-probe extracts, temporary ZIPs, local package caches,
and generated validation reports after acceptance when they are not the
retained proof or final report.

Ghidra backups and proof archives need manifest classification before pruning:
record the family, timestamp or version, size, reason, and retained
replacement or summary. Keep the live Ghidra project, installed game folder,
original `BEA.exe`, latest verified/golden/final backups, and any proof bundle
that is current evidence for a tracked claim. If classification is ambiguous,
leave the material in place and report a retention recommendation instead of
deleting it.

For a Ghidra project, the backup unit is the `.gpr` marker plus the complete
recursive `.rep` store. Use `tools/ghidra_project_backup.py` to copy and verify
the pair through per-file hashes and a disposable read-only program open. A
zero-byte `.gpr` by itself, top-level directory copy, or plausible byte total
without the complete recursive `.rep` store is not a recoverable backup. Keep
verification receipts and exact local paths in an
ignored overlay. The 2026-07-13 full re-audit retention closeout verified both
trusted endpoints and all ten full-sized intermediate backups with this model;
see
[the public-safe closeout](reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md).

For coordinated automation, storage sentinel, Ghidra/headless, consult, and
proof-retention posture, see
[AUTOMATION_STORAGE_GHIDRA_POSTURE.md](coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md).

## Ghidra Note

Agents can work with a local Ghidra project from an ignored overlay or another
maintainer-local path, but the repo should receive deterministic exports,
scripts, markdown, JSON, TSV, and ledger files instead of binary Ghidra project
stores.

Maintainer-local live Ghidra project and backup locations are
private/local-only. Keep exact project and backup paths outside tracked docs in
ignored local overlay notes or maintainer-private manifests. Public clones do
not need a Ghidra database to build or test the app. Use the tracked Ghidra
scripts, exports, ledgers, and RE docs for source work; use a local Ghidra
project for maintainer-local investigation, mutation, or read-back proof.

### Ghidra Distribution Options

| Option | Public repo status | Use |
| --- | --- | --- |
| Deterministic exports, scripts, rename maps, ledgers, hashes, Markdown/JSON/TSV summaries | Track when useful and non-secret | Normal collaboration surface for agents and contributors. |
| Compact proof summaries and readiness notes | Track when they do not embed raw payloads | Durable evidence that avoids requiring the maintainer database. |
| Full `.gpr` / `.rep` project stores and Ghidra backups | Keep local/ignored | Maintainer-local read-back or mutation work only. Do not commit, package, mirror, hardlink, or publish them as source artifacts. |
| Junctions to large local archives | Allowed only under ignored overlay roots such as `local-ghidra/` or `local-proofs/` | Local disk-management convenience. Never use a junction as a public distribution path. |

Hardlinks to game, Ghidra, proof, save, or runtime payloads are not allowed in
the repo tree. They make local payloads look like ordinary source files and can
defeat review expectations. If a future policy intentionally changes full
Ghidra project distribution, that decision needs a separate review and release
boundary update before any file move.
