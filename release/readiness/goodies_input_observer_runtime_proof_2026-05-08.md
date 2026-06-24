# Goodies Input Observer Runtime Proof - 2026-05-08

Status: GREEN copied-profile runtime observer proof for normal wall navigation

## Objective

Prove the ordinary Goodies wall navigation path with a focused CDB observer that samples the `CFEPGoodies__ButtonPressed` input handler instead of the hot rendered `get_goodie_number` loop.

## Public-Safe Result

The copied-profile run completed with the focused observer:

```text
observer: tools/runtime-probes/goodies-input-observer.cdb.txt
parser: tools/goodies_selection_observer_log_probe.py
verdict: NORMAL_SEQUENCE_CONFIRMED
coordinateSampleCount: 0
buttonEventCount: 213
navigationEventCount: 16
inputPathObserved: true
debuggerSkippedCommandWarningCount: 0
hiddenReturnIds: []
normal returned ids observed: 66, 67, 68, 69, 70, 74
```

The focused observer also saw neighboring visible ids before and after the race-row skip. The public-safe summary shape confirms that the normal `CFEPGoodies__ButtonPressed` right-navigation path advances through `66, 67, 68, 69, 70` and then reaches `74`, skipping `71`, `72`, and `73` on the ordinary wall path.

## Private Evidence Boundary

Raw CDB logs, screenshots, launch JSON, scoped-input JSON, and captures remain ignored under:

```text
subagents/goodies-input-observer-runtime-2026-05-08/
```

Do not commit raw CDB logs, screenshots, copied executables, copied profile files, or raw proof JSON from that folder.

## What This Proves

- A copied/windowed BEA profile can be launched and driven to the Goodies wall.
- Local exact-PID CDB attach works against the copied profile with the focused input observer.
- The focused observer reaches the `CFEPGoodies__ButtonPressed` input path rather than only render-loop mapper sampling.
- The normal right-navigation path produces the expected race/developer transition sequence `66, 67, 68, 69, 70, 74`.
- The observed normal path did not return hidden ids `71`, `72`, or `73`.
- The updated parser handles CDB logs where multiple observer events are printed on the same physical log line.
- No copied BEA, CDB, Ghidra, or headless Ghidra processes remained after cleanup.

## What This Does Not Prove

- This does not prove Goodies `71`, `72`, or `73` are impossible to reach through every hidden, cheat, developer, or non-wall path.
- This does not prove in-game model-viewer playback.
- This does not prove every Goodies wall coordinate.
- This does not mutate the installed Steam game, the original `BEA.exe`, saves, or Ghidra.

## Next Step

Treat normal Goodies wall navigation as runtime-proven for the `70 -> 74` skip. Continue hidden/non-grid Goodies work as a separate question: search for non-wall selection paths, developer commands, cheat overrides, or direct Goodie selection branches that could select `71`, `72`, or `73`.
