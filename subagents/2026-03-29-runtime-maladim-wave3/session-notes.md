# Runtime Notes: Maladim gameplay-effect wave 3

Date: 2026-03-29
Session type: user-driven manual gameplay test after earlier menu-path confirmation
Target executable: `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe`
Baseline note: no debugger was kept attached for this pass; the result is from direct gameplay observation.

## What This Pass Answered

This pass closed the remaining high-value gameplay question from the earlier `Maladim` work:

- does `God ON` in the Steam build actually change combat damage behavior?

## Reported Gameplay Findings

User-reported live result:

- with `God ON`, normal combat damage no longer depleted shields
- with `God OFF`, normal combat damage resumed
- after taking about 50% shield damage with god mode off, turning it back on instantly restored shields to full
- after taking hull damage with god mode off, turning god mode back on restored shields but did **not** repair the already-lost hull

## Practical Interpretation

This is strong evidence that the Steam-build `Maladim` path is functionally real, not just cosmetic UI:

- the toggle changes actual gameplay damage behavior
- the protection boundary appears shield-centric in the observed scenario
- existing hull loss is not treated as a full heal when the toggle is re-enabled

## Still Not Directly Re-Tested In This Pass

- water / environmental-death coverage

The user suspected water would still kill based on the shield-centric behavior, but that specific hazard was not directly re-tested in this pass and should remain documented as likely rather than proven.
