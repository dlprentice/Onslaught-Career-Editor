# PLATFORM__ClearScreen

> Address: `0x00515910` | Source: `references/Onslaught/PCPlatform.cpp:180` (`CPCPlatform::ClearScreen`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void PLATFORM__ClearScreen(int color)`)
- **Verified vs Source:** Yes (high-confidence wrapper match)

## Purpose
Clears the current render target/depth state before draw passes.

## Behavior Summary
- Dispatches to `CPCPlatform` vtable slot `+0xAC`.
- Forwards the caller-supplied clear color and uses fixed wrapper flags/values for the clear operation.

## Notable Call Sites
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `FUN_00540f70` (`0x00540f70`)
- FMV/render helper cluster around `0x0053f2xx` and `0x0053f5xx`
