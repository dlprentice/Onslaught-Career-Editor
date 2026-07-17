# Product And Implementation Strategy

The project has two deliverables and one supporting evidence surface.

| Surface | Ownership |
| --- | --- |
| WinUI Toolkit | User-facing save/options, Media, Lore, generated-asset browsing, copied-game profiles, patching, and launch workflows |
| GPL rebuild | Deterministic simulation in `OnslaughtRebuild.Core`; input, camera, rendering, audio, and presentation in clients |
| RE, Lore, and tools | Evidence and bounded utilities that support the two deliverables without becoming another product lane |

## WinUI and AppCore

WinUI is the normal Windows application. AppCore owns shared parsing, save-byte
preservation, patch planning, guarded writes, copied-target enforcement, media
discovery, catalogs, and Lore loading. The CLI exposes supported AppCore-backed
save and analysis workflows; it is not a separate implementation.

Installed retail files are read-only inputs. Mutating workflows write a chosen
copy or an app-owned safe-copy profile and verify expected bytes before and
after executable patches.

## Rebuild

`rebuild/` is GPL-3.0-or-later, RE-informed original code. Core stays
deterministic and independent of filesystem, process, clock, network, and GPU
APIs. The Godot client adapts Core state and does not own simulation truth.
Tracked scenarios and visuals are synthetic or original; optional user-supplied
retail-derived inputs remain ignored and local.

Read [`rebuild/PROVENANCE.md`](../rebuild/PROVENANCE.md) before changing this
lane. The current work is not strict clean-room and does not claim retail
gameplay or visual parity.

## Evidence

Canonical technical research lives under `reverse-engineering/`; narrative
Lore lives under `lore/`; reusable tools live under `tools/`. Static identity,
source architecture, copied-runtime observation, deterministic hashes, and
visual inspection are different evidence classes and must be described as such.

Git history is the archive for completed waves, plans, and readiness state.
Keep a tracked artifact only when it contains unique evidence or drives a live
product, contributor, safety, or release workflow.

## Decision rule

Prefer the smallest change that produces safer or clearer user behavior. Add a
new lane, abstraction, or compatibility path only for a current demonstrated
requirement.
