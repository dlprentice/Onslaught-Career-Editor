# CGame__Update

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
