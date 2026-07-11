# Repository Authority Map

Status: active contributor authority map
Last updated: 2026-07-11
Doc version: 4.0

Use this map when two files appear to describe the same behavior, when deciding
where new work belongs, or before moving or deleting a large surface. It
separates current sources from projections, generated artifacts, history, and
maintainer-local payloads.

## Conflict Rules

1. Current implementation and focused tests outrank prose summaries.
2. Canonical source outranks a derived mirror or generated projection.
3. Root contributor docs and root `package.json` outrank materialized release
   templates and historical wave notes.
4. A newer release note does not promote an unproven runtime, gameplay, online,
   visual, RE-semantic, or rebuild claim.
5. When authority is unclear, stop and classify the surface before editing it.

## Current Front Doors

| Question | Start here | Authority |
| --- | --- | --- |
| What does the shipped app do? | `CURRENT_CAPABILITIES.md` | Current bounded capability summary |
| How do I build or contribute? | `CONTRIBUTING.md` | Current human contributor workflow |
| What may an agent change? | `AGENTS.md`, `goal.policy.md`, `goal.md` | Current execution and campaign boundaries |
| Which commands should I run? | Root `package.json` | Current command definitions |
| What is release signoff? | `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` | Current source/package signoff guide |
| What is current RE truth? | `re_orchestrator_state.json`, `reverse-engineering/RE-INDEX.md` | Current baton plus canonical RE index |
| What is current Lore truth? | `documentation_agent_state.json`, `lore/LORE-INDEX.md` | Current baton plus canonical narrative index |

Do not browse all 1,400-plus package scripts to begin work. Use `npm test` for
the active-product quick check, then choose a focused command from
`CONTRIBUTING.md`. The exhaustive public/release gates are intentionally
separate.

## Canonical Active Sources

| Surface | Role | Edit posture |
| --- | --- | --- |
| `OnslaughtCareerEditor.WinUI/` | Primary WinUI 3 application | Normal product source |
| `OnslaughtCareerEditor.AppCore/` | Shared save/options/patch/media/Lore/asset correctness | Prefer behavior here when it is not UI-specific |
| `OnslaughtCareerEditor.Cli/` | Supported C# analysis/patch support CLI | Active support source |
| `OnslaughtCareerEditor.AppCore.Tests/`, `OnslaughtCareerEditor.UiTests/` | Active regression and UI-contract tests | Update with affected behavior |
| `patches/catalog/patches.v2.json` | Patch catalog | Byte-verified copied-target entries only |
| `lore/` | Canonical narrative and research-facing Lore source | Edit here, then refresh protected projections |
| `reverse-engineering/` | Canonical RE specifications, evidence summaries, and research | Keep proof classes explicit |
| `roadmap/` | Current strategy, plans, and bounded proof queues | Plans are not implementation proof |
| `tools/` | Active and historical validation/RE/lab scripts | Start at `tools/README.md`; do not assume every wave script is a current gate |
| `developer_agent_state.json`, `documentation_agent_state.json`, `re_orchestrator_state.json` | Concise current batons | Current truth, not campaign changelogs |

`OnslaughtCareerEditor.WinUI.slnx` is the normal product solution.
`OnslaughtCareerEditor.Release.slnx`, AppCore.Host, and the CLI remain support
surfaces, not a second GUI product.

## Derived And Protected Projections

These files are tracked because readers, release packaging, or checkers use
them. They do not become independent sources of truth.

| Surface | Derived from / purpose | Rule |
| --- | --- | --- |
| `lore-book/lore/` | Projection of canonical `lore/` | Change canonical source and run docsync |
| `lore-book/roadmap/` | Projection of selected `roadmap/` content | Change canonical source and run docsync |
| `lore-book/reverse-engineering/` | Broad technical archive projection | Not a reader-curation claim; change canonical RE source first |
| `lore-book/CURRENT_CAPABILITIES.md` | Protected capability mirror | Keep byte/content parity through docsync |
| `release/readiness/public_package.json` | Materialized public-package command template | Root `package.json` remains contributor command authority |
| `release/readiness/public_AGENTS.md`, `public_gitignore.txt` | Materialized candidate templates | Root files remain current working authority |
| Generated indexes, ledgers, reports, and snapshots | Checker or packaging inputs | Regenerate from declared inputs; do not hand-edit unless the owning tool says so |

The v1.0.9 offline pack contains 949 tracked Markdown/TXT documents from Lore,
roadmap, and technical RE material. That number measures packaging breadth, not
editorial curation, completeness, freshness, rights review, or public-safety
approval.

## Historical And Archived Sources

| Surface | Classification | Normal contributor posture |
| --- | --- | --- |
| `archive/electron-workbench/` | Archived Electron/React/TypeScript product detour | Do not install or test by default |
| `archive/legacy-wpf/` | Archived WPF app | Retained because some UI tests inspect historical resources |
| `archive/legacy-python/` | Archived Python GUI/CLI attempt | Reference only; active Python tooling lives in `tools/` |
| `archive/historical-docs/` | Superseded guidance | Never use as current product direction |
| `wave_online_audit/`, `wave_online_audit2/` | Historical audit records | Evidence/history, not default work queues |
| Dated `release/readiness/*release*` notes | Release snapshots | Historical after a newer published release |
| Numbered Ghidra/wave scripts and reports | Campaign evidence and reproducibility material | Not ordinary contributor commands unless a current front door names them |

Historical files may remain useful and tracked. Their presence does not make
them current, release-required, or a reason to install archived dependencies.

## Maintainer-Local And Generated Payloads

Keep these out of Git and out of public app ZIPs unless a narrow exception is
explicitly reviewed:

- `game/`, `media/`, `save-attempts/`, `local-ghidra/`, `local-proofs/`, and
  `local-rom-input/`;
- copied executables, DLLs, game archives, extracted audio/video/model/texture
  payloads, arbitrary saves/options, screenshots, frame captures, and raw CDB
  logs;
- full Ghidra project databases/backups, secrets, `.env*`, credentials, local
  configuration, build output, and generated package output;
- generated `subagents/` snapshots or raw proof payloads. Compact non-secret
  text reviews may be tracked when they remain useful.

The only tracked save-shaped exception is
`tests_shared/fixtures/gold_career_save.bin`, the immutable regression fixture.
Do not generalize that exception.

## Release Boundary

The public source repository and a portable app ZIP have different boundaries.
Source may contain useful tools, RE notes, plans, compact proof summaries, and
history. A release ZIP contains the WinUI payload, launcher/readme/license, and
deliberately selected offline content. Source validation does not publish a
release, sign a binary, create an installer, or prove gameplay/runtime parity.

Use `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` for signoff and a dated
readiness note for one exact package. Do not infer current release truth from an
older materialized template.

## Safe Cleanup Order

1. Identify the canonical owner and all generated/protected consumers.
2. Prove active build, test, docs, and package references.
3. Preserve unique history before deleting branches or files.
4. Move or delete one classified surface at a time.
5. Run docsync, focused product tests, and the appropriate public-boundary gate.
6. Update current batons; archive long campaign detail instead of growing them.

Do not casually move the primary solutions, archived WPF resources referenced
by tests, protected Lore projections, release manifests, or large RE/tool trees.
Create a generated front door or ownership index before restructuring a large
directory.
