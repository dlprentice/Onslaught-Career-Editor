# CGame__MainLoop

> Address: `0x0046eee0` | Source: `references/Onslaught/game.cpp:2076`

Status: source and bounded pristine-instruction contract
Last updated: 2026-09-12
Summary: gameplay/render ordering and the distinct render stamp consumed by attachment caches.
Source File: game.cpp; Binary: BEA.exe

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0046e910` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__MainLoop(void *this)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CGame::MainLoop`)

## Purpose
Per-frame gameplay loop:
- processes platform quit/input state
- runs gameplay update and audio status updates
- performs render pass and frame timing maintenance
- updates frame-fraction/base-time bookkeeping

## Notes
- Called from `CGame__RestartLoopRunLevel` (`0x0046dc30`) while `mQuit == QT_NONE`.
- Entry call chain now resolves to named helpers:
  - `Input__ResetMouseTransientState` (`0x00523db0`)
  - `PLATFORM__Process` (`0x00515880`)
  - `CController__InactivityMeansQuitGame` (`0x0042d810`)
- Wave567 corrected the older `CProfiler__ResetAll` label at `0x00523db0`; source hints include both `CProfiler::ResetAll` and `CVBufTexture::ResetAll` callsites, but the retail body clears mouse transient state and is now behavior-bounded as input reset.
- Audio/status tail now resolves to:
  - `CSoundManager__UpdateStatus` (`0x004e1b20`)
  - `CMusic__Update` (`0x004e2ea0`)
- Viewpoint maintenance loop now resolves to `CEngine__UpdatePos` (`0x0044a1c0`) per active camera slot.
- Calls `CGame__Update` (`0x0046e910`) before render/audio frame completion.
- Contains the runtime branch that can force quit-state transitions based on platform/process results.
- `Platform__AsyncSaveCareer` call path references this function in the current mapping set.

## Render stamp and gameplay ordering

The September 12 read-only check used
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Body anchors are MainLoop `[0046eee0,0046f2c0)`, SHA-256
`ca07832a37ebaa7c3d49b89bc3d060766c8ce666b8a0564e0e999a5374371574`,
and Render `[0046e460,0046e90c)`, SHA-256
`80fe5f6d32dd004dcc14d069e2666fd3e23ba078c1ea21fc01691801070903e2`.
The following are instruction findings within those bodies and their selected
callers, not an execution of the complete loop:

1. MainLoop computes the model fraction at `0046ef40–0046efd5`, then calls
   Update at `0046efd7`. Update increments **CGame+18** at
   `0046e91a–0046e91e`. Its unpaused path advances the event manager at
   `0046eb5d`, services direct controllers, and flushes events at `0046ebce`.
2. Render is called afterward at `0046f151`. It reads **CGame+14** at
   `0046e578`, increments it at `0046e57e`, and stores it at `0046e599`.
   With the actual CGame base `008a9a98`, this is global **`008a9aac`**.
   Pinned `references/Onslaught/game.h:262–263` distinguishes
   `mRenderFrameNumber` from `mUpdateFrameNumber`; `game.cpp:1704–1707`
   places the former increment in Render.
3. The branch at `0046f17e` returns to `0046f06a`, permitting additional
   renders without another Update. Conversely the pre-run loop calls Update
   at `0046e052` and returns through `0046e05d` without Render. Source
   `game.cpp:2063–2072,2126–2130,2198–2220` preserves these two shapes.

In this loop ordering, callbacks within one event flush share the prior render
stamp, and even multiple gameplay updates can share it during pre-run. A render stamp is not
the event-manager frame, a fixed 20 Hz tick, or a one-to-one update counter.
The [Unit attachment cache](../Unit.cpp/CUnit__UpdateTransform.md#renderer-cache-population-and-render-stamp)
uses this stamp for both normal-cache refresh and direct-cache reuse. The
isolated attachment probes supply it explicitly; their frozen `frame` labels
mean render stamps. They do not measure the cadence of a retail playthrough.

Core integration needs ordered render context alongside gameplay/camera
callbacks. Choosing a synthetic one-render-per-tick cadence would discard
these measured branch distinctions. No Ghidra database was opened or changed
for this readback.
