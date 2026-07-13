# CGame__Update

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0046e910` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x0046e910` | Source: `references/Onslaught/game.cpp:1836`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__Update(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::Update`)

## Purpose
Core gameplay update/tick function:
- processes controller/player update paths
- advances and flushes EventManager timing/events
- handles game-state/fade/pause transitions
- applies camera/control handoff and related per-frame runtime logic

## Notes
- Called from `CGame__MainLoop` once per frame prior to render/audio post-processing.
- Includes dev-mode/easter-egg and state-transition logic that materially affects runtime flow.
