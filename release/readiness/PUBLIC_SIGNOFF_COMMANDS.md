# Public Sign-Off Commands

Status: active source/release validation guide
Last updated: 2026-06-24

Use this guide for the public working repo and app-release signoff. It excludes
live copied-game launch, raw CDB/debugger, full Ghidra database, second-host, and
large runtime-capture commands from ordinary PR gates because those require
local payload overlays. For PR-style handoffs and reviewer expectations, use
`COLLABORATION.md` in the repo root.

A passing source tree is not automatically a GitHub Release. Portable ZIP
publication, source pushes, signing, installer release, and announcement are
separate maintainer actions.

## Start

Prerequisites: Windows 10/11, .NET 10 SDK, Node.js 24.x, npm 11.12.x, and
Python 3 available through the Windows `py` launcher.

```powershell
cd <repo-root>
git submodule update --init --recursive
node --version # must be v24.x
npm --version  # must be 11.12.x
```

For a fresh checkout, install dependencies after checking the hard-payload
boundary if the change touches repo shape or release payload rules:

```powershell
npm run test:hard-payload-safety
npm install
```

## App Release Candidate Gate

Run this before publishing a downloadable WinUI ZIP release:

```powershell
npm run test:winui-zip-release-candidate-probe
```

This builds the exact portable ZIP candidate, verifies the friendly top-level
layout, rejects raw-root DLL/EXE layouts and hard payloads, checks bundled
`lore-book/BOOK.md`, extracts the ZIP, runs launch smoke, runs Home navigation
smoke, runs extracted-package Lore reader smoke, and runs representative Media
smoke when a local game install is available. A green source tree is not enough
for app release publication without this package gate.

## Product Source Gates

<!-- public-package-commands:start -->
```powershell
npm run build:winui
npm run build:cli
npm run build:host
npm run test:appcore
npm run test:winui
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
dotnet run --project .\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj -- --help
```
<!-- public-package-commands:end -->

## Docs And Release-Safety Gates

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

`npm run test:md-links` writes ignored reports under `subagents/md-link-check`.
Those reports are validation artifacts, not app release payload.

`npm run test:hard-payload-safety` is the tracked-source cleanliness gate. It is
expected to reject actual game/runtime binaries, local game payload roots, build
outputs, `.env` files, and credential-like key material. It is not supposed to
hide normal RE notes, state batons, agent reports, or proof summaries.

`npm run test:public-allowlist` runs the hard-payload gate, the submodule
payload scan, and the public-primary migration/hash inventory. Keep
`npm run test:public-submodule-payload-safety` available as a focused diagnostic
when a submodule boundary changes.

## Not Public Gates

The following families are local runtime/debug evidence and are not required for
ordinary PRs:

- `npm run test:winui-safe-copy-runtime`
- live copied-game launch/CDB/input/capture checks
- second-host command-source or runtime-causality checks that require local
  proof roots
- Ghidra mutation, read-back, backup, or local runtime proof commands

Reviewed helper scripts for docs, validation, or self-tests may be present in
the source tree. Their presence does not make live CDB, Ghidra, copied-game
launch, second-host, or local proof-root workflows ordinary PR gates unless a
root `package.json` script explicitly calls a bounded self-test.

## Packaging And Installer Status

Reviewed helper scripts may be present for optional local diagnostics or
self-tests, but ZIP/MSIX signing, trusted install, uninstall-after-install,
binary packaging, and installer-grade release are separate release gates. Do not
claim a binary or installer release from source validation alone.

## Accounting Gates

`tools\release_profile_snapshot.py`, `tools\release_curated_manifest.py`, and
`tools\release_package.sh --dry-run` remain accounting/packaging tools. Run them
when release-profile inputs change or when preparing an app/source release; they
are not required for every narrow PR.
