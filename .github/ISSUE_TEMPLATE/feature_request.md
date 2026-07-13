---
name: Feature request
about: Suggest a payload/secret-safe product, tooling, or documentation improvement
title: "[Feature] "
labels: enhancement
assignees: ""
---

## Area

Choose one:

- [ ] WinUI app
- [ ] AppCore / CLI
- [ ] RE-informed rebuild
- [ ] Patch / mod safety
- [ ] Runtime tooling
- [ ] Docs
- [ ] RE / Lore docs
- [ ] Public/release boundary

## Problem

What user or maintainer problem should this solve?

## Proposed Shape

Describe the smallest useful version.

## Safety Boundary

The installed game folder and original `BEA.exe` remain read-only. A public
feature request must not require mutating either one.

Confirm whether this request needs any of the following:

- proprietary game assets, saves, screenshots, or copied executable bytes
- runtime proof, online/multiplayer proof, or rebuild-parity claims
- public release packaging or signing

If yes, explain the boundary without including private material.

Keep the request public-safe: redact local user paths and machine identifiers.
Do not include or attach game binaries, extracted assets, saves, screenshots,
frame captures, copied executables, raw runtime proof bundles, secrets, or
unredacted private paths.

- [ ] No prohibited payload, proof bundle, secret, or unredacted private path is
      included in this request.

For private-data, proprietary-content, security, or online-session concerns,
follow `SECURITY.md` instead of posting sensitive details.
