# Collaboration Guide

Use this checklist when handing a change to another contributor or reviewer.

## Start

1. Read `AGENTS.md`, `CONTRIBUTING.md`, and the directly relevant implementation or runbook.
2. Keep the change scoped to one product or evidence contract.
3. Run the smallest local gate that proves the change.
4. Confirm the diff contains no proprietary game payload, copied executable, arbitrary save, raw debugger/runtime capture, secret, or bulky generated artifact.

## Main Lanes

| Lane | Main paths | Typical gate |
| --- | --- | --- |
| WinUI | `OnslaughtCareerEditor.WinUI/`, `OnslaughtCareerEditor.UiTests/` | focused WinUI build/test |
| AppCore / CLI | `OnslaughtCareerEditor.AppCore/`, `OnslaughtCareerEditor.Cli/` | focused AppCore/CLI test |
| Rebuild | `rebuild/` | `npm run test:rebuild` |
| Patch / mod safety | `patches/`, AppCore patch services | patch-engine and safe-copy checks |
| Runtime tooling | `tools/`, copied-runtime helpers | owning focused checker |
| Docs | current front doors and subsystem docs | affected link/command checks plus `git diff --check` |
| Release boundary | `release/`, manifests, package inputs | affected public inventory and allowlist gates |

## Handoff

```text
Summary:
Changed paths:
Validation run:
Validation intentionally skipped:
Public/private boundary check:
Installed game or original BEA.exe mutation: none
Remaining risks:
```

Passing local checks does not publish anything. Commit, push, export, release, announcement, signing, and runtime mutation require their own authorization.
