# CFEPGoodies__ButtonPressed

> Address: `0x0045cde0`
> Source: `references/Onslaught/FEPGoodies.cpp` (`CFEPGoodies::ButtonPressed`)

## Status

- Function boundary recovered in Ghidra: Yes, 2026-05-07
- Named in Ghidra: Yes
- Signature hardened: Yes, 2026-05-07
- Verified vs source: Partially, through instruction/decompile read-back and source structure

## Current Signature Read-Back

Ghidra index metadata now records:

```c
void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)
```

Local variable names and richer field typing are still provisional.

## Behavior

- Handles Goodies wall input while no Goodie is displayed and image zoom is idle.
- Dispatches frontend button codes through a jump table.
- Moves the current Goodies wall coordinate stored at `this + 0x13c` (`mCX`) and `this + 0x140` (`mCY`).
- Calls `get_goodie_number(mCX, mCY)` to skip invalid coordinates during up/down/right navigation.
- On select, checks the selected Goodie state, calls `CFEPGoodies__StartLoadingGoody`, and marks the selected Goodie as viewed (`GS_OLD`, value `3`) when a valid selected id exists.
- Uses the `MALLOY` and `latete`/accented cheat flags to override effective Goodie state in the select path.

## 2026-05-07 Recovery Evidence

Read-only instruction export first showed that the eight previously no-function xrefs to `get_goodie_number` live inside the same input/selection region:

```text
0x0045ce53
0x0045ce87
0x0045cf2a
0x0045cf4c
0x0045d03b
0x0045d070
0x0045d0be
0x0045d0cd
```

Dry-run through `CreateFunctionsFromAddressList.java` reported `would_create=1` for `0x0045cde0`. The apply pass then created and named `CFEPGoodies__ButtonPressed`, and read-back exported 6/6 selected frontend Goodies functions with missing 0 and failed 0.

Follow-up dry/apply through `ApplyGoodiesButtonPressedSignature.java` set the source-aligned signature:

```c
void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)
```

`tools/goodies_ghidra_readback_probe.py --check` now verifies this signature and the selected-coordinate behavior tokens.

The same verifier now also checks the `CFEPGoodies__ButtonPressed`, `CFEPGoodies__Process`, and `CFEPGoodies__LoadingGoodyPoll` decompile exports for direct `0x47`/`0x48`/`0x49` target constants. Current result: `PASS hits=0`. That keeps the current binary-selection model honest: these paths still route through the coordinate mapper rather than a hard-coded direct selector for Goodies 71-73.

After recovery, xrefs to `get_goodie_number` read back under:

- `CFEPGoodies__StartLoadingGoody`
- `CFEPGoodies__LoadingGoodyPoll`
- `CFEPGoodies__ButtonPressed`
- `CFEPGoodies__Process`

This closes the immediate no-function xref ambiguity around the Goodies wall navigation path. It does not prove that Goodies 71-73 are hidden-reachable; normal wall navigation still routes through `get_goodie_number(x, y)`, whose compiled mapping skips 71-73.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)`.
- Saved function comment now records Goodies wall navigation/display controls, `mCX/mCY`-style coordinate updates, `get_goodie_number`, selectable unlocked/cheat-overridden load starts, old-state marking, and back/close cleanup as static/source-parity evidence only.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `goodies-input`, `goodie-grid`, `retail-binary-evidence`, and `comment-hardened`.
- Instruction/decompile read-back includes grid fields at `+0x13c` and `+0x140`, display fields around `+0x194` and `+0x1d4`, multiple `get_goodie_number` calls, `CFEPGoodies__StartLoadingGoody`, and `CFEPGoodies__FreeUpGoodyResources`.
- This does not prove runtime input behavior, hidden Goodies 71-73 reachability, full asset-viewer parity, or rebuild parity.

## Follow-Up

- Improve local naming and field typing after read-back.
- Continue 71-73 hidden/non-grid reachability work separately from this function-boundary recovery.
