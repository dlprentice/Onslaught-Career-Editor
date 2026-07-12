# Product And Implementation Strategy

Status: active
Last updated: 2026-07-11

The filename is retained for existing links. The former three-lane framing is
superseded: the project now has two deliverables, one research/tooling support
surface, and archived application history.

## Deliverables

| Surface | User outcome | Direction |
| --- | --- | --- |
| WinUI 3 toolkit | Preserve, inspect, edit, patch, and launch safe copies of a user-owned game | Primary Windows toolkit; AppCore owns shared correctness |
| GPL rebuild | Play an original-code game implementation without the retail executable or proprietary payloads | Deterministic Core plus a Godot .NET visual client |
| RE, Lore, and tools | Make the game understandable, documented, testable, and moddable | Evidence-backed support for both deliverables |
| Archived Electron, WPF, and Python apps | Preserve project history and potentially useful ideas | Reference only; no parity obligation or default setup cost |

These surfaces do not compete for the same responsibility. WinUI is not the
game renderer. Godot does not own saves, patching, Lore, or copied-retail-game
management. Archived apps do not define current UX or architecture.

## WinUI Toolkit

WinUI is the normal application for players and preservation users. It owns:

- first-run game-folder setup and truthful unavailable-path states;
- Save Lab and options workflows backed by AppCore;
- copied-game profiles, byte-verified patches, and guarded launch/process
  control;
- Media, Asset Library, and offline Lore access; and
- accessible native Windows navigation, status, focus, and error behavior.

Patch and write operations remain copy-first because the installed game and
original `BEA.exe` are user-owned source material, not app scratch space. That
boundary is a safety property, not a reason to make ordinary read-only browsing
or first-run setup cumbersome.

## Rebuild

`rebuild/` is an active GPL-3.0-or-later, RE-informed original-code game
implementation. It is not strict clean-room and does not claim retail parity.

Architecture:

1. `OnslaughtRebuild.Core` owns deterministic fixed-step simulation.
2. Command tapes, canonical final-state hashes, and rolling input/post-step
   trace hashes provide repeatable headless regression evidence.
3. The Godot .NET client owns input sampling, camera, rendering, audio, and
   presentation only; it advances and reads Core rather than duplicating game
   rules.
4. Synthetic scenarios and original procedural assets keep the baseline build
   independent of proprietary game files.

Current commands:

```powershell
npm run build:rebuild-core
npm run test:rebuild-core
npm run run:rebuild-headless
```

Read `rebuild/PROVENANCE.md` before implementation. A future strict clean-room
lane requires separately staffed specification, unexposed implementation, and
independent acceptance teams; it cannot be created by renaming the current
exposed code.

## Research, Lore, And Tooling

Canonical RE material lives under `reverse-engineering/`; canonical narrative
and research-facing Lore lives under `lore/`; active scripts live under
`tools/`. Python is appropriate for validation, extraction, static/runtime
research, and lab automation. It is not a fourth product GUI.

Evidence classes stay distinct:

- static names/comments/types do not prove runtime behavior;
- source architecture does not prove retail implementation identity;
- copied-runtime observation does not authorize installed-game mutation;
- a deterministic Core hash does not prove visual or gameplay parity; and
- a screenshot does not prove deterministic simulation.

Historical proof plans can explain what was measured or deliberately excluded.
They are not authority to generate another readiness/checklist/proof-plan layer
before writing executable code. Use a focused test or name one concrete blocked
dependency instead.

## Archived Apps

`archive/electron-workbench/`, `archive/legacy-wpf/`, and
`archive/legacy-python/` are retained for provenance and selective idea mining.
They are excluded from the normal setup, test, release, and parity contract.
New user-facing work goes to WinUI, AppCore, or the rebuild according to
ownership above.

## Delivery Sequence

1. Keep the WinUI toolkit safe, understandable, accessible, and releaseable as
   an unsigned portable ZIP while signing remains intentionally deferred.
2. Land deterministic rebuild mechanics in small reviewed Core slices, then
   expose them through one pinned Godot client.
3. Expand patches and mods only with copied-target byte and runtime evidence
   appropriate to the claim.
4. Deep-review RE and Lore for semantics, provenance, navigation, duplication,
   and stale claims; do not treat file count as quality.
5. Add online behavior only behind distinct-endpoint, authority, security, and
   source-bound runtime evidence. Do not expose Host/Join as player-ready early.

## Decision Rule

Prefer the path that produces a safer, clearer user workflow or executable,
testable behavior with the fewest competing owners. Add a new framework or lane
only when the current architecture cannot meet a concrete requirement and the
migration cost is justified by evidence.
