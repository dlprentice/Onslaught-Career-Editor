# Runtime Notes: defaultoptions / pause persistence wave 1

Date: 2026-03-15
Session type: live runtime probe against a patched-for-windowed installed build
Target executable: `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe`
Baseline note: this was not the clean retail specimen; the installed executable had display/windowed patches applied to make debugger attachment practical.

## What We Were Trying To Prove

1. Whether the load-game frontend path really calls `CCareer__Load(..., flag=1)` at runtime.
2. Whether that same load path really rewrites `defaultoptions.bea` from the loaded save buffer.
3. Whether the pause-menu god-mode gating path (`PauseMenu__Init` / `IsCheatActive(3)`) actually fires the way the current static docs suggest.
4. Whether pause resume/exit also persists `defaultoptions.bea`.

## Confirmed Findings

### 1. Load-game path really hits `CCareer__Load(..., flag=1)`

Confirmed live from the second corrected breakpoint wave:

```text
CFEPLoadGame__DoLoad this=008a1128
CCareer__Load this=00660620 src=03c7ad00 flag=1
```

This is the runtime confirmation we wanted for the core load path. It matches the documented Steam-build behavior where load-game uses `flag=1` rather than the boot/defaultoptions `flag=0` path.

### 2. Load-game path really rewrites `defaultoptions.bea`

Also confirmed live in the same corrected wave:

```text
CFEPOptions__WriteDefaultOptionsFile data=03c7ad00 size=2714
```

This is the strongest runtime confirmation from the session. It means the load-game frontend does explicitly write `defaultoptions.bea` from the loaded save buffer in this patched-live session.

### 3. A second options write happened after gameplay / pause interaction

Observed after the first successful reload:

```text
CFEPOptions__WriteDefaultOptionsFile data=03c6d080 size=2714
CFEPOptions__WriteDefaultOptionsFile data=03c6d080 size=2714
```

This strongly suggests there is also a gameplay/pause/menu persistence path that rewrites `defaultoptions.bea`, but the exact trigger in this session was not pinned down cleanly before the machine locked up.

## Negative / Unresolved Findings

### Pause-menu cheat gating did not confirm cleanly

Breakpoints aimed at:

- `PauseMenu__Init` (`0x004cde60`)
- `CPauseMenu__InitPauseSession` (`0x004d0ff0`)
- direct god-mode label check site (`0x004ce328`)
- `IsCheatActive` (`0x00465490`)

did **not** yield the expected clean hits during pause reopen in this session.

That means at least one of these is true:

- the documented pause-menu entrypoint is not the actual live reopen path we exercised,
- the probe timing was wrong,
- or the current static RE posture overstates how directly this path can be observed from pause reopen alone.

## Probe Corrections Learned During Session

- The first `CCareer__Load` breakpoint recipe was wrong by one stack slot.
- Correct live argument interpretation for the observed call was:
  - `source = poi(@esp+4)`
  - `flag = poi(@esp+8)`
- The earlier printed `size=1 flag=0` line was a breakpoint recipe error, not evidence that the load path used `flag=0`.

## Stability / Risk Note

The workstation eventually locked hard enough that the user had to force reset. That happened after repeated long-lived remote-client breakpoint reconfiguration while the game was running.

Practical lesson for the next wave:

- prefer fewer breakpoints,
- prefer narrower single-question probes,
- avoid piling multiple remote-client reconfiguration passes onto the same long-lived session,
- and document each confirmed result immediately before moving to the next question.

## Later Session Failure: Dock / Display Topology Change

In a later follow-up after the narrower pause-persist probe succeeded, the user connected the machine to a docking station while the game was active and the title raised:

- `Fatal error sorry`
- `Could not reset the 3D system.`

The game window also showed:

- `Changing video options, please wait`

This looks like an old Direct3D device-reset failure caused by live display-topology change while the game was running in patched windowed mode. It should be treated as an environment/display-reset failure, not as a contradiction of the runtime findings above.
