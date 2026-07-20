# WinUI release candidate

The supported downloadable shape is an unsigned, self-contained Windows x64
portable ZIP. It is not an installer, MSIX, Store package, signed artifact, or
SmartScreen/reputation claim.

The candidate contains:

- `Launch Onslaught Toolkit.cmd` at the ZIP root;
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

```powershell
npm run release:winui-zip
```

The command self-tests Lore packing, exercises ZIP inspection, publishes to an
ignored scratch root, creates and extracts the friendly ZIP, checks entry-path
and content boundaries, launches the extracted app, visits representative Home
and Lore workflows, optionally exercises Media when local inputs exist, and
confirms owned processes are cleaned up. Output remains under ignored local
scratch space.

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
