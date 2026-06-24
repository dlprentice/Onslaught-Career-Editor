# BattleEngine Weapon-Stealth Runtime Probe - 2026-05-07

Status: public-safe copied-profile runtime probe, inconclusive for stealth-break behavior

## Objective

Run the first bounded copied-profile runtime probe for the remaining `weapon_fire_breaks_stealth` source-only anchor.

The behavior question remains:

```text
In the Steam retail build, when the player is cloaked and fires a weapon, does the live runtime clear or visibly break stealth?
```

## Safety Boundary

- The installed game folder was treated as read-only source material.
- A fresh ignored copied profile was used under `subagents/`.
- The copied executable inherited `force_windowed` as already patched; the patch helper reported `verified: no bytes were written`.
- Raw screenshots, copied executable data, copied profile data, launch JSON, input JSON, and window/capture artifacts remained private under `subagents/`.
- The managed copied process was stopped, and the final scan reported no BEA window/process remaining.

## Commands / Evidence Summary

| Step | Result | Public-safe summary |
| --- | --- | --- |
| Copied profile prep | PASS | `game-profile-prepare.v1`; copied `BEA.exe`, `data`, `defaultoptions.bea`, `savegames`, and required DLLs into an ignored copied-profile root. |
| Windowed patch check on copy | PASS | `force_windowed` was already patched in the copied executable; no bytes were written. |
| Launch | PASS | `game-launch-process.v1`; launched the copied profile with `-skipfmv -level 710`. |
| Window scan | PASS | One visible managed `BEA.exe` window was found, `656 x 539`. |
| Baseline capture | PASS | Private still frame showed live level gameplay with the `Radar sites: 9` objective. |
| Cloak input | SENT | Sent one scoped `tap:TAB` action to the exact managed window; helper reported `keyEventsSent=2`. |
| Fire input | SENT | Sent one scoped center client-coordinate mouse click to the exact managed window; helper reported `mouseEventsSent=2`. |
| After-fire capture | CAPTURED | Private after-fire frame was captured, but it does not conclusively prove a cloak-active baseline. |
| Stop/cleanup | PASS | Managed copied process was stopped; final window scan returned `no-window`, and process scan found no `BEA.exe`. |

## Finding

This run proves the copied-profile harness can:

- prepare an isolated runtime profile
- start Steam retail gameplay directly at `level710`
- capture a bounded still frame from the managed window
- send scoped keyboard and mouse input to the exact managed BEA window
- stop and clean up the copied process

It does **not** prove whether firing while cloaked breaks stealth. The private frames did not provide an unambiguous cloak-active visual baseline after `tap:TAB`, so the fire-after-cloak behavior remains inconclusive.

## Follow-Up Needed

The next proof attempt needs a stronger cloak-active detector before firing. Good candidates:

- capture a visible tutorial/audio/text cue that confirms cloak activation
- use the prepared latch observer at `tools/runtime-probes/cloak-latch-observer.cdb.txt` and require `py -3 tools\cloak_runtime_observer_log_probe.py --log <private-cdb-log> --out <ignored-json> --require-activation`
- add a more controlled input sequence if the current level starts under immediate missile pressure
- verify the exact active binding from runtime options before the input send

Do not publish a stealth-break claim until the before-fire evidence proves the player was actually cloaked.

Follow-up status: `release/readiness/battleengine_cloak_runtime_observer_probe_2026-05-08.md` records the first copied-profile latch-observer attempt. It improved the observer tooling but did not prove cloak activation: one run saw an entry event without activation, and the corrected explicit-return observer produced no latch events under two scoped `tap:TAB` inputs. The fire-while-cloaked behavior therefore remains unproven.

## Not Claimed

- This probe does not prove firing breaks stealth.
- This probe does not prove firing preserves stealth.
- This probe does not prove exact Steam retail function identity for `CBattleEngine::WeaponFired`.
- This probe does not prove behavior across every mission, weapon, or player state.
- This probe does not mutate the installed game, original `BEA.exe`, original saves, or Ghidra projects.

## Privacy / Release Safety

This note is public-safe. It contains sanitized command classes, status, counts, and behavior boundaries only. It does not include private screenshots, copied saves, copied executables, raw captures, local absolute paths, media cache paths, debugger logs, or raw runtime proof JSON.
