# Collaboration Guide

Status: active public-safe collaboration guide
Last updated: 2026-06-23

Use this guide when preparing work for another developer or an agent reviewer.
This public repository is now the primary collaboration and day-to-day working
repo. Validation is local; do not add GitHub Actions, hosted CI, release
automation, or workflow scaffolding.

## Start Here

1. Read [README.MD](README.MD), [CONTRIBUTING.md](CONTRIBUTING.md), and
   [SECURITY.md](SECURITY.md).
2. Pick one lane and keep the change scoped to that lane.
3. Run the smallest relevant local gate set before review.
4. Include the exact commands you ran in the handoff.
5. Confirm that no game payloads, copied executables, screenshots/frame dumps,
   raw CDB logs, arbitrary saves, secrets, or bulky generated proof payloads
   are in the change. Text state batons, compact proof summaries, and agent
   reports are allowed when they are useful and non-secret.
6. For meaningful code, docs, runtime proof, release, or repo-boundary changes,
   update the relevant state baton or explain why the work was read-only.

## Lanes

| Lane | Main paths | Normal local gates |
| --- | --- | --- |
| WinUI app | `OnslaughtCareerEditor.WinUI/`, `OnslaughtCareerEditor.UiTests/` | `npm run build:winui`, `npm run test:winui`, `npm run test:winui-primary-lane` |
| AppCore / CLI | `OnslaughtCareerEditor.AppCore/`, `OnslaughtCareerEditor.Cli/`, tests | `npm run test:appcore`, `npm run build:cli` |
| Patch / mod safety | `patches/`, AppCore patch services, WinUI patch surfaces | `npm run test:winui-patch-engine-safety`, `npm run test:winui-safe-copy-preflight` |
| Docs / release safety | `README.MD`, `CONTRIBUTING.md`, `release/readiness/`, `roadmap/`, `reverse-engineering/` | `npm run test:doc-commands`, `npm run test:md-links`, `npm run test:public-allowlist`, `npm run test:repo-hygiene` |
| RE docs / proof summaries | `reverse-engineering/`, `lore/`, `lore-book/`, `release/readiness/`, state batons | docs/release safety gates |

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
```
<!-- public-package-commands:end -->

This public repo's root `package.json` is the command authority for contributors
and their agents. Maintainers may run additional local runtime, Ghidra, or
release-accounting gates when a change touches those areas.

For public-primary boundary work, `npm run test:public-allowlist` runs the
hard-payload, submodule payload, and migration inventory gates. Use
`npm run test:public-primary-migration-inventory` or
`npm run test:hard-payload-safety` as focused diagnostics when one of those
sub-gates needs isolated triage.

## Handoff Template

Use this format in a PR description, review request, or agent handoff. Public
issue/PR templates may use the same fields; those templates are not hosted
validation or release automation.

```text
Lane:
Summary:
Changed paths:
Validation run:
Validation intentionally skipped:
Private/public boundary check:
State baton update:
Installed game / original BEA.exe mutation:
Remaining risks or follow-ups:
```

Required answers:

- `Validation run` names exact commands, not broad statements.
- `Private/public boundary check` says whether the change adds hard payload,
  release manifest entries, copied-game proof summaries, or local evidence.
- `State baton update` names updated state files, or says `read-only/no state
  edit`.
- `Installed game / original BEA.exe mutation` must be `none` unless a private
  maintainer intentionally performed a copied-profile/runtime proof. Public
  contributors should never mutate the installed game or original executable.

## Review Expectations

Reviewers should check:

- The change is narrow and path-scoped.
- The lane-specific gates match the changed files.
- User-facing WinUI copy is plain and does not expose maintainer proof jargon.
- Static RE, runtime proof, patch behavior, online play, and rebuild parity are
  kept as separate claim classes.
- The repo remains free of game assets, screenshots/frame dumps, arbitrary
  saves, copied executables, raw proof bundles, secrets, and credential
  material. State files and text agent reports are allowed when concise,
  useful, and non-secret.

## Issue Or Feature Reports

Public reports should be minimal and non-proprietary:

- Describe the product area, expected behavior, actual behavior, and local
  command or app action.
- Redact local user paths and machine identifiers.
- Do not attach game binaries, extracted assets, arbitrary saves, screenshots,
  frame captures, copied executable bytes, or raw runtime proof bundles.
- For security or private-data concerns, follow [SECURITY.md](SECURITY.md)
  instead of posting public details.

## Public Release Note

Passing local repo gates is not the same as publishing a release. Public
publishing, release branches, binary packages, signed installers, and runtime
multiplayer claims require explicit maintainer authorization and their own
proof.
