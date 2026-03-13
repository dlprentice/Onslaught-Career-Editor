# CFrontEnd__Process

- **Address:** `0x00466ba0`
- **Status:** Renamed / signature + comment applied in Ghidra
- **Source match:** `references/Onslaught/FrontEnd.cpp:595` (`void CFrontEnd::Process()`)

## Purpose

Per-frame frontend update loop body used by `CFrontEnd__Run`.

## Key Behavior

1. Runs platform/system processing and quit-state checks.
2. Calls `EVENT_MANAGER.Update()` (`CEventManager__Update` on global singleton).
3. Updates particles/sound/music/frontend video status.
4. Flushes controller state.
5. Handles transition timing (`mTransitionFrom`, `mTransitionTo`, `mTransitionTime`).
6. Iterates all frontend pages and calls each page's `Process(state)`.
7. Processes frontend message box (`FEMESSBOX.Process()`).

## Notable Calls (Retail)

- `CEventManager__Update` (`0x0044b5c0`)
- `CMusic__Update`
- `CDXFrontEndVideo__Update`
- `CFEPOptions__GetState`

## Notes

- This function was previously left as `FUN_00466ba0` in docs and is now mapped.
- The event-manager call in this function was one of the anchors for the latest `eventmanager.cpp` mapping pass.
