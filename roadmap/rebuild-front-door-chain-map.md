# Rebuild Front Door

Status: active implementation routing map
Last updated: 2026-07-11

The rebuild has an executable implementation lane. Start with
[`rebuild/README.md`](../rebuild/README.md), not the historical recursive
proof-plan chain.

## Current Architecture

| Surface | Role | Authority |
| --- | --- | --- |
| [`rebuild/OnslaughtRebuild.Core`](../rebuild/OnslaughtRebuild.Core/) | Fixed-step deterministic simulation and snapshots | Owns simulation truth |
| [`rebuild/OnslaughtRebuild.Headless`](../rebuild/OnslaughtRebuild.Headless/) | Command-tape replay plus independent trace/final-state golden verification | Acceptance and diagnostics adapter |
| [`rebuild/scenarios`](../rebuild/scenarios/) | Synthetic replay fixtures with reviewed golden hashes | Determinism regression input |
| [`rebuild/PROVENANCE.md`](../rebuild/PROVENANCE.md) | RE-informed and strict clean-room boundaries | Contribution boundary |
| Future Godot .NET client | Input, camera, rendering, and local presentation | View-only adapter over Core |

The WinUI toolkit remains the primary preservation, patching, save, Lore, and
media application. The rebuild is a separate game implementation; WinUI does
not become its renderer or simulation host.

## Run And Verify

From repository root:

```powershell
npm run build:rebuild-core
npm run test:rebuild-core
npm run run:rebuild-headless
```

The final-state hash proves canonical continuation state; the rolling trace
hash proves the complete input/post-step history for one command tape. Built-in
verification compares them with independent headless constants. A native
client screenshot proves only that a bounded frame rendered. None of these is
retail gameplay, visual, timing, content, or parity proof by itself.

## Evidence Inputs

| Question | Entry point | Boundary |
| --- | --- | --- |
| What does the project currently claim? | [`CURRENT_CAPABILITIES.md`](../CURRENT_CAPABILITIES.md) | Product truth and explicit non-claims |
| Where is static RE measured? | [`static-reaudit-measurement-register.md`](../reverse-engineering/binary-analysis/static-reaudit-measurement-register.md) | Static documentation quality, not runtime behavior |
| Where is RE material indexed? | [`RE-INDEX.md`](../reverse-engineering/RE-INDEX.md) | Research navigation, not implementation authority |
| Where are asset formats documented? | [`game-assets/_index.md`](../reverse-engineering/game-assets/_index.md) | Format and tooling evidence; no proprietary payload license |
| What must stay local? | [`LOCAL_LAB_OVERLAY.md`](../LOCAL_LAB_OVERLAY.md) | Game files, extracted assets, captures, Ghidra stores, and secrets |
| What was the former proof queue? | [`static-to-proof-rebuild-transition-backlog.md`](static-to-proof-rebuild-transition-backlog.md) | Historical evidence register only |

## System Crosswalk

| System | Evidence anchors | Implementation rule |
| --- | --- | --- |
| Player movement and vehicle modes | Static/runtime RE docs plus bounded synthetic contracts | Add one observable behavior at a time with Core tests and replay-hash review; do not infer retail constants from source names alone. |
| Combat and targets | Runtime observations, static function maps, and original rebuild design | Keep hit resolution deterministic and renderer-independent; separate prototype mechanics from parity claims. |
| Career and saves | `reverse-engineering/save-file/`, AppCore save tests, and career docs | Preserve unknown retail bytes in toolkit workflows; use an original rebuild persistence format rather than pretending it is a retail save. |
| Mission scripts and events | `reverse-engineering/game-assets/msl-scripting.md` and script/event RE docs | Specify observable behavior before implementing a new command; do not import decompiler or GPL reference-source bodies. |
| AYA resources and media | `reverse-engineering/game-assets/` and asset tooling | Keep proprietary payloads optional/local. The baseline rebuild must use original procedural content and run without the retail game. |
| Rendering | Renderer/static docs and later native client evidence | Godot owns presentation only. Visual similarity requires separate measured evidence and rights review. |
| Online play | Existing protocol/runtime research | No player-ready claim until distinct endpoints, authority, replay/security, and native client behavior are separately proven. |

## Provenance

The active implementation is RE-informed original code and GPL-3.0-or-later.
Current maintainers and agents have seen GPL reference source and detailed RE
material, so this lane cannot honestly be called strict clean-room.

A future strict clean-room effort needs separate exposed specification,
unexposed implementation, and independent acceptance teams. Its implementation
team must not consume this subtree, reference source, decompiler output, or
private proof payloads.

## Historical Chain

The former static-to-proof backlog remains tracked because it records prior
evidence and safety boundaries. It is no longer an active queue and must not be
extended with another readiness/checklist/proof-plan level. New work should
produce executable source and focused tests, or name one concrete dependency
that actually blocks implementation.
