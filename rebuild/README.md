# Godot rebuild: moved to onslaught-godot

Status: pointer — this folder held a frozen copy of the Godot rebuild; it was removed on 2026-11-11
Last updated: 2026-11-11 (the frozen copy was cut from this repository)
Summary: the rebuild is developed, licensed and documented in onslaught-godot; the last tree of this repository that
held the frozen copy is at the tag `archive/20261111-rebuild-frozen-copy`.

This folder held a frozen copy of the Godot C# rebuild of *Battle Engine Aquila*: the simulation and host projects,
their tests, the rebuild's own tools and its `PARITY.md`, `PROVENANCE.md` and `LICENSE`. It was removed on 2026-11-11. Rebuild
development, issues and pull requests are at [onslaught-godot](https://github.com/dlprentice/onslaught-godot), and the
GPL-3.0-only licence text and the per-unit provenance record, including the credit for the code adapted from Stuart
Gillam's published Onslaught source, are
[`rebuild/LICENSE`](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/LICENSE) and
[`rebuild/PROVENANCE.md`](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PROVENANCE.md) there. The removed
tree stays readable at the tag
[`archive/20261111-rebuild-frozen-copy`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/archive/20261111-rebuild-frozen-copy/rebuild),
and a single file comes back with `git checkout archive/20261111-rebuild-frozen-copy -- <path>`.

The tag holds 853 of this folder's 863 tracked files: ten tool files (the CMSH parser, its tests, and the region and plan JSON
files) moved to [`tools/`](../tools/README.md) before the cut and are in `tools/` both at the tag and here. Each of the 863 was
present at the same path in onslaught-godot at its commit `3d7d1d06cf42bd49c3cfd54ffadfbb3e8cb92593`, by comparing the two file
lists; 544 of them had different content there by then, so the live copy is the one to read.
