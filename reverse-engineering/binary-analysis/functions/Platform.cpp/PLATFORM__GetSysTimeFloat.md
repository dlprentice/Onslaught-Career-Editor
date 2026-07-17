# PLATFORM__GetSysTimeFloat

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0046e910` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x005159e0` | Source: `references/Onslaught/PCPlatform.cpp:241` (`CPCPlatform::GetSysTimeFloat`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`float PLATFORM__GetSysTimeFloat(void)`)
- **Verified vs Source:** Yes (high-confidence timing helper match)

## Purpose
Returns wall-clock elapsed time in seconds for game/frontend timing systems.

## Behavior Summary
- Uses `QueryPerformanceCounter` delta when frequency data is initialized.
- Falls back to `timeGetTime()/1000.0f` when high-resolution timing is unavailable.
- Widely used by frame timing, fade logic, inactivity timeout checks, and UI animations.

## Notable Call Sites
- `CGame__MainLoop` (`0x0046eee0`)
- `CGame__Update` (`0x0046e910`)
- `CController__InactivityMeansQuitGame` (`0x0042d810`)
