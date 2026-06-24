# Public Sign-Off Commands

Status: active public-candidate validation guide
Last updated: 2026-06-23

Use this guide for sanitized public-source candidates. It intentionally excludes
private runtime proof, Ghidra backup, local second-host, copied-game launch, and
maintainer-only evidence commands from the private maintainer sign-off runbook.
For PR-style handoffs and reviewer expectations, use
`COLLABORATION.md` in the public candidate root.

A passing public candidate is not automatically a GitHub Release. Portable ZIP
publication, public repo push, signing, installer release, and announcement are
separate maintainer actions.

## Start

Prerequisites: Windows 10/11, .NET 10 SDK, Node/npm, and Python 3 available
through the Windows `py` launcher.

```powershell
cd <repo-root>
```

For a freshly materialized public candidate payload, run the inventory check
before install/build/test commands create generated local outputs. Also verify
that `EXPORT_PROVENANCE.json` exists in the candidate root:

```powershell
npm run test:public-candidate-inventory
npm install
```

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
Those reports are validation artifacts, not release payload. In public-source
candidates this command checks the full exported markdown graph, including the
curated public RE, lore, and roadmap entrypoints.

`npm run test:public-candidate-inventory` is a payload cleanliness gate for a
fresh export. It is expected to fail after local build/test runs create generated
`bin/`, `obj/`, `subagents/`, `node_modules/`, or package-lock artifacts; clean
or regenerate the candidate before packaging or publishing. A final shareable
source candidate should be a fresh export with `EXPORT_PROVENANCE.json` present
and `npm run test:public-candidate-inventory` passing after all product/docs
validation has already been run in a disposable validation copy.

## Not Public Gates

The following families are private maintainer/runtime evidence and are not
required for public-source PRs:

- `npm run test:winui-safe-copy-runtime`
- live copied-game launch/CDB/input/capture checks
- second-host command-source or runtime-causality candidate checks that require
  private proof roots
- Ghidra mutation, read-back, backup, or local runtime proof commands

Reviewed helper scripts for docs, validation, or public-safe self-tests may be
present in the source candidate. Their presence does not make live CDB, Ghidra,
copied-game launch, second-host, or private proof-root workflows public gates
unless a public `package.json` script explicitly calls a bounded self-test.

Public candidates may describe these workstreams only with bounded
public-safe summaries and non-claims.

## Packaging And Installer Status

Reviewed public-safe helper scripts may be present in the source candidate for
optional local diagnostics or self-tests, but ZIP/MSIX signing, trusted install,
uninstall-after-install, binary packaging, and installer-grade release are not
public sign-off gates. Do not claim a binary or installer release from source
candidate validation alone.

When maintainers publish a downloadable app release, the current supported shape
is an unsigned portable Windows x64 ZIP plus SHA-256 checksum sidecar attached
to GitHub Releases. It is not an installer, signed MSIX, Store package, or
SmartScreen/reputation claim.

## Maintainer-Only Export Gates

The private source repo owns curated-manifest generation, release profile
accounting, and `tools\release_package.sh --dry-run`. Public-source candidates
do not include the private curated manifest or private inventory artifacts, so
those commands are not public PR gates.
