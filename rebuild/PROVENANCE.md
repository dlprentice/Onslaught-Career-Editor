# Rebuild Provenance

Status: active implementation boundary

`rebuild/` is a GPL-3.0-or-later, source- and reverse-engineering-informed
reconstruction. It is not a clean-room lane. The root MIT license does not
relicense this subtree or the pinned `references/Onslaught` source.

## Permitted evidence and inputs

- Stuart Gillam's pinned GPL source may be read, ported, and adapted with its
  license and attribution preserved.
- The Steam retail executable and Ghidra database establish released static
  identities and deltas from the reference source.
- Controlled copied-runtime observations establish measured behavior.
- Original design work, deterministic tests, public standards, and engine APIs
  may fill gaps that are clearly labelled provisional.
- The project has full permission to use, modify, and distribute the original
  game assets. Selected assets may enter the rebuild when an implemented slice
  consumes them and their provenance, credits, and third-party terms are clear.

Do not import the retail executable, decompiler output, user saves, raw runtime
captures, or separately licensed third-party code/media into this subtree.
Never describe synthetic or source-only behavior as observed Steam behavior.

## Authority

The reference source is implementation evidence, not automatic proof that the
Steam build is byte- or behavior-identical. When sources disagree, use this
order for the released PC game:

1. controlled retail runtime observation;
2. retail binary/static evidence;
3. pinned source implementation and vocabulary;
4. provisional reconstruction design.

Record a source or address only when it makes a current implementation decision
auditable. Generated inventories, human-review gates, and proof-plan chains are
not provenance.

## Current slice

The deterministic Core and command-tape/hash format are reconstruction-owned
infrastructure. The Godot Aquila Handling Lab now consumes static conversions
of the released Federation walker and jet meshes; their exact source/output
hashes live with the assets. Its arena, targets, weapons, resources, material
assignment, articulation, jet/morph presentation, and scale remain provisional
unless a specific retained retail measurement says otherwise.

One clean Level 100 control and two fresh repeated copies establish the walker
translation and body-turn loop: equal forward/strafe acceleration, a 3.0-unit/s
cap, `0.7` per-retail-update coast, yaw-velocity accumulation, and `0.8`
retention. Core maps those 20 Hz responses into its fixed 30 Hz step. The same
control/repeat discipline maps raw states `2 → 1 → 3` to the explicit
16-tick walker-to-jet transition. Jet forward speed and energy drain retain
earlier bounded measurements.

These slices do not make the surrounding vehicle model retail-faithful.
Eight-way movement projection, terrain response, dash behavior, camera,
jet-to-walker, transform presentation, resources, weapons, and flight dynamics
remain provisional.

A passing replay proves repeatability of the encoded state and input history.
A native smoke proves the current client starts, loads both curated Aquila
meshes, renders, advances, and exits. It does not prove material, animation,
mission, scale, timing, or visual parity.
