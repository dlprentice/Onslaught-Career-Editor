# PLATFORM__EndScene

> Address: `0x005158e0` | Source: `references/Onslaught/PCPlatform.cpp:165` (`CPCPlatform::EndScene`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void PLATFORM__EndScene(void)`)
- **Verified vs Source:** Yes (high-confidence wrapper match)

## Purpose
Ends the active render scene through the platform backend.

## Behavior Summary
- Dispatches to `CPCPlatform` vtable slot `+0xA8`.
- Used as the scene-finalization counterpart to `PLATFORM__BeginScene`.

## Notable Call Sites
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `CDXEngine__Render` (`0x0053e2e0`)
- `CDXEngine__PostRender` (`0x0053ecc0`)
