---
name: Feature request
about: Suggest an improvement to the Modding & Content Toolkit tools, schemas, lore or documentation
title: "[Feature] "
labels: enhancement
assignees: ""
---

## Area

Choose one:

- [ ] Content Catalogue / Content Inventory
- [ ] Format decoders / World / MSL / Mod tools
- [ ] Lore and documentation

Player-facing gameplay, Career/Backups/Mods/Editor UI and launcher requests belong in [Onslaught CE](https://github.com/dlprentice/onslaught-ce/issues); see [Where to contribute](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/CONTRIBUTING.md#where-to-contribute).

## Problem

What modder, preservation or tooling problem should this solve?

## Proposed Shape

Describe the smallest useful change and its authored tests.

## Safety Boundary

Toolkit tools must treat retail installations as read-only, publish outputs outside the game tree via `tools/safe_generated_output.py` (or stdout), and keep retail-derived outputs in ignored `local-data/`.

- [ ] No prohibited payload, generated retail catalogue, secret or unredacted private path is included in this request.

For private-data, proprietary-content or security concerns, follow `SECURITY.md` instead of posting publicly.
