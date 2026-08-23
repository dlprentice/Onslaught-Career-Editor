# Rebuild delta — W5 engine, render, platform, and shell

Status: complete — current implementation re-read and ranked source-first slices identified
Date: 2026-08-22
Summary: the rebuild already carries selected retail camera, viewport, frontend-window, and input-edge laws, but it does not contain a general `CEngine`/`PCLTShell` state model or a runtime `CResourceAccumulator`. D3D8/D3D9 device wrappers are intentionally backend-replaced by Godot rather than candidates for literal porting.
Evidence: SOURCE + MEASURED — current rebuild source was re-read against the W5 source contract and tracked retail-static predecessors; proposed slices remain design recommendations, not new parity claims.
Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes; retail addresses are inherited from tracked evidence and no specimen bytes were read or written in this wave.

## Assembly boundary

The live rebuild contract remains:

- deterministic state and fixed-step laws belong to `OnslaughtRebuild.Core`;
- real-time input and frontend lifecycle adaptation belong to
  `OnslaughtRebuild.Client`;
- native rendering, window/device ownership, and host input belong to
  `OnslaughtRebuild.Godot`;
- retail file discovery, verification, and conversion belong to the bounded
  materializer, not Core
  ([`rebuild/README.md:20-30`](../../../../rebuild/README.md#L20-L30)).

That division is consequential for this wave. Source accessors that expose pure
state can inform Core/Client laws. Direct3D, HWND, DirectInput, COM, gamma,
texture, and render-state calls cannot enter Core. The source is port-first
evidence, while released measurements override proved divergences
([`rebuild/PROVENANCE.md:32-53`](../../../../rebuild/PROVENANCE.md#L32-L53)).

## Current code already carrying part of the W5 contract

### Camera and projection

`RetailCameraLaws` already owns the fixed single-player/multiplayer aspect values
and explicitly rejects deriving them from the host window
([`RetailCameraLaws.cs:15-48`](../../../../rebuild/OnslaughtRebuild.Core/RetailCameraLaws.cs#L15-L48)).
The Godot world view already builds the released first-person projection with
near `0.1`, far `700`, the measured vertical tangent, and a current camera
([`FirstFlightWorldView.cs:16-33`](../../../../rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs#L16-L33),
[`FirstFlightWorldView.cs:716-734`](../../../../rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs#L716-L734)).

That means a blanket claim that near/far/projection or viewport-relative camera
work is absent is stale. What remains absent is the source's general two-slot
engine state: per-viewpoint camera/player/viewport ownership, explicit current
viewport copy, current-viewpoint selection, and the pure accessor envelope from
`engine.h:66-154`.

### Window/input laws

The click-to-start owner already carries the retail fact that both mouse-rect
extents come from `PLATFORM__GetWindowWidth`, not height
([`RetailClickToStartInput.cs:31-37`](../../../../rebuild/OnslaughtRebuild.Godot/RetailClickToStartInput.cs#L31-L37),
[`RetailClickToStartInput.cs:64-67`](../../../../rebuild/OnslaughtRebuild.Godot/RetailClickToStartInput.cs#L64-L67)).
The interactive client already queues one-shot simulation edges rather than
turning all inputs into held levels; skip-pan, fire, weapon-cycle, zoom, and
movement/look pulses have explicit pending-edge state
([`InteractiveSession.cs:260-369`](../../../../rebuild/OnslaughtRebuild.Client/InteractiveSession.cs#L260-L369)).
Godot already suppresses key echoes and responds to pressed joypad/button edges
on the pause path
([`FirstFlightGame.cs:455-500`](../../../../rebuild/OnslaughtRebuild.Godot/FirstFlightGame.cs#L455-L500)).

Those owners implement selected product behavior, not a complete source
`PCLTShell` key/joy table. There is no reusable held/one-shot/old-current input
state object that proves source `xKeyOn`, `xKeyOnce`, and the three joystick edge
predicates together. The W5 source rows and W009 retail bodies close enough of
that law to make a focused adapter slice possible without importing DirectInput.

### Assets and resource accumulation

The materializer already reads a user installation, verifies exact archive/data
hashes, and writes only bounded ignored assets
([`materialize_retail_assets.py:1-32`](../../../../rebuild/tools/materialize_retail_assets.py#L1-L32)).
This is intentionally not a port of the source `CResourceAccumulator`: no
runtime post-increment resource-id allocator, target platform/level state,
static resource handles, or page-writer object exists in the rebuild. A claim
that those source accessors are already implemented merely because assets are
materialized would be false.

### Render/device state

Godot replaces the source's HWND, DirectInput, D3D application lifecycle, D3D8
state mirrors, COM texture/shader handles, gamma ramp, and device-object list.
The current renderer carries many measured visual laws, but it does not and
should not expose a literal `PCLTShell::SRS` or D3D8 wrapper API. The retail
D3D9 cache bodies are useful delta evidence for ordering and duplicate-call
suppression; they are not a mandate to reconstruct the obsolete API boundary.

The source screen-capture flags also do not map to the current parity capture
rig. The rig reads the Godot viewport after drawing for test evidence; it is not
a player/runtime implementation of `CDXEngine::TriggerScreenCapture` or its
partial top/bottom bounds.

## Stale or unsafe gap statements found

1. **"The rebuild has no viewport/projection law" is stale.** It has the released
   near/far and projection envelope for the active Level 100 view; only the
   generic multi-viewpoint owner remains absent.
2. **"Input edges are absent" is stale.** Multiple client inputs are already
   represented as edges. The remaining gap is a coherent platform-level
   held/consume/old-current state contract, not edge semantics in general.
3. **"Resource accumulation is implemented by the materializer" is false.** The
   materializer is a safe filesystem boundary; the source accumulator is runtime
   state with different ownership.
4. **"Port the Direct3D wrappers to Core" is unsafe.** It violates Core's
   dependency contract and copies an API that retail itself changed from D3D8 to
   D3D9. Only pure ordering/cache laws may cross into deterministic code.
5. **"PCEngine.h is the active PC engine" is stale for this source selection.**
   `_DIRECTX` selects `CDXEngine`; the old `CPCEngine` rows are alternate-target
   vocabulary, not an implementation backlog.

## Ranked coherent implementation slices

### 1. Platform input edge state — highest readiness

Create one deterministic Client-level state owner for held keys, consume-once
keys, previous/current joy-button bytes, and explicit frame/reset boundaries.
Feed it from Godot events and consume it through the existing session queues;
do not expose DirectInput types. Focused tests should prove held read,
consume-and-clear, rising edge, held button, falling edge, reset, and no-repeat
on an echo.

Why first: source lines are complete (`ltshell.h:78-81, 291-319`), retail
statically agrees on held read and consume-and-clear at `0x00515970` and
`0x00515980`, and the current client already owns edge delivery. Remaining
unknowns—table ownership, repeat policy, and joystick polling cadence—are
explicit falsifiers rather than architecture blockers.

### 2. Two-viewpoint engine state envelope — medium readiness

Add a pure Core value/state owner for exactly two viewport slots, selected slot,
near/far values, and camera/player identifiers. Client/Godot adapters should
translate that state into native cameras/viewports; Core must not reference
Godot geometry or GPU APIs. Preserve the source's by-value current viewport
copy and bounds-check the selected slot rather than copying unchecked C++ array
access.

Why second: the source contract is dense and coherent
(`engine.h:13-16, 66-154`), and current code already proves the active
single-player projection, but the retail ABI/field layout of most inline
accessors is unresolved. Start with source shape and keep the existing measured
far `700` exception rather than reviving the base source default `256`.

### 3. Resource-plan metadata, not a raw accumulator port — lower readiness

Introduce a deterministic manifest-side model for target platform, target
level, monotonic logical resource ids, and named materialized inputs. Keep file
handles/page writers inside the materializer or another filesystem adapter;
never put them in Core. Use it only when a concrete second-world/resource
consumer needs stable identity ordering.

Why third: source accessors and limits are clear
(`ResourceAccumulator.h:62-108`), and the current materializer already owns
verified inputs, but retail identity is unresolved for seven of the eight
omitted accessors. The tracked source defect ledger also warns that fixed arrays
lack capacity checks and that the similarly named retail filename function is a
different path-builder body. This is a planning slice, not permission to copy
unsafe fixed buffers or add retail payloads.

## Deliberately not proposed

- no literal D3D8/D3D9 state-cache recreation in Core;
- no editor D3D application base;
- no legacy `CPCEngine` implementation;
- no raw HWND/DirectInput/COM ownership in deterministic assemblies;
- no source-style fixed resource arrays, unchecked indices, or file handles in
  Core;
- no per-function task fan-out.

The ranked slices are architecture-level implementation candidates. Retail
correspondence and row-level falsifiers remain in
[`RETAIL-DELTA.tsv`](RETAIL-DELTA.tsv).
