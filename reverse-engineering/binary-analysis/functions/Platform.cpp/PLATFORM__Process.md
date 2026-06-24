# PLATFORM__Process

> Address: `0x00515880` | Source: `references/Onslaught/PCPlatform.cpp:144` (`CPCPlatform::Process`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int PLATFORM__Process(void)`)
- **Verified vs Source:** Yes (high-confidence wrapper match)

## Purpose
Runs the platform/system message pump and reports quit requests.

## Behavior Summary
- Repeatedly calls system handling helper (`PLATFORM__ProcessSystemMessages`) until no more work is pending.
- Tracks a quit-state return code when host/window quit state is set.
- Returns `0` for no quit; returns non-zero quit code when shutdown is requested.

## Callers
- `CGame__MainLoop` (`0x0046eee0`)
- `CFrontEnd__Process` (`0x00466ba0`)
