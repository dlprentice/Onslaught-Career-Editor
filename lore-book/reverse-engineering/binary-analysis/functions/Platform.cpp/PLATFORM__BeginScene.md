# PLATFORM__BeginScene

> Address: `0x005158c0` | Source: `references/Onslaught/PCPlatform.cpp:159` (`CPCPlatform::BeginScene`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`bool PLATFORM__BeginScene(void)`)
- **Verified vs Source:** Yes (high-confidence wrapper match)

## Purpose
Starts a render scene through the active PC platform backend.

## Behavior Summary
- Dispatches to `CPCPlatform` vtable slot `+0xA4`.
- Returns `true` on non-negative backend status (scene begin allowed), otherwise `false`.

## Notable Call Sites
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `CDXEngine__Render` (`0x0053e2e0`)
- `CDXEngine__PostRender` (`0x0053ecc0`)
