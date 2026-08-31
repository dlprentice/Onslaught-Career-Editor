# WinUI release candidate

Status: active — the release-candidate shape and its boundary
Last updated: 2026-08-31 (host routing; candidate shape remains unchanged).
Summary: what a candidate ZIP contains, what it explicitly does not claim, and
which steps remain separately authorized.

The supported downloadable shape is an unsigned, self-contained Windows x64
portable ZIP. It is not an installer, MSIX, Store package, signed artifact, or
SmartScreen/reputation claim.

The candidate contains one `Onslaught-Toolkit/` wrapper folder. Inside that
wrapper:

- `Launch Onslaught Toolkit.cmd`;
- the self-contained WinUI payload under `app/`;
- `LICENSE`, the generated third-party notices and license bundle, and the
  package README;
- `lore-book/BOOK.md` plus a generated short-path `lore-pack/` built from the
  canonical public `lore/` library.

It must not contain retail game files, copied executables, saves, extracted
assets, media payloads, Ghidra data, debugger output, private captures, or
rebuild binaries. Users provide their own retail installation for game-aware
workflows, and mutating workflows operate only on copied files or safe copies.

## Build and verify a local candidate

Run the release gate only inside the activated isolated Windows VM. The WinUI
publish, launch, and UI-probe stages are Windows-only; Omarchy deliberately
refuses this root command before any candidate is produced.

```powershell
npm run release:winui-zip
```

The command self-tests Lore packing, exercises ZIP inspection, publishes to an
ignored scratch root, creates and extracts the friendly ZIP, checks entry-path
and content boundaries, launches the extracted app, visits representative Home
and Lore workflows, completes one generated-synthetic Safe Copy Manager
workflow with stale-input and source/output-alias negative controls, verifies
the source and copied-target tree hashes, optionally exercises Media when local
inputs exist, and confirms owned processes are cleaned up. Output remains under
ignored local scratch space; the synthetic fixture is not a retail executable,
installation, or save.

For source-only release boundary changes, select the affected commands from
[`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
[`release/readiness/THIRD_PARTY_NOTICES.winui.md`](release/readiness/THIRD_PARTY_NOTICES.winui.md)
is generated from restored project dependencies and must agree with
`npm run test:notices`.

## Publication boundary

A passing local candidate does not authorize a commit, push, tag, GitHub
Release, upload, signing request, announcement, or installation. Those are
separate maintainer actions. Historical release notes and superseded package
accounting are available in Git history rather than duplicated in the active
tree.

The exact candidate limits shown to users are owned by
[`release/readiness/WINUI-ZIP-README.txt`](release/readiness/WINUI-ZIP-README.txt).
