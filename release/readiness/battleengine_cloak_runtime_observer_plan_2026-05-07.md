# BattleEngine Cloak Runtime Observer Plan - 2026-05-07

Status: public-safe runtime-observer preparation, followed by inconclusive copied-profile observer probe

## Objective

Prepare a stronger cloak-active detector for the remaining `weapon_fire_breaks_stealth` runtime question.

The first copied-profile `level710` probe proved launch, capture, scoped input, and cleanup, but it did not prove that the player was cloaked before firing. The next runtime attempt should not rely on screenshots alone.

## Prepared Observer

This pass adds a read-only CDB command file:

```text
tools/runtime-probes/cloak-latch-observer.cdb.txt
```

The observer installs breakpoints around the currently named retail helper:

```text
0x0040d4d0 CGeneralVolume__Update4ACLatchFromHeightAndA0
0x0040d4e8 clear-path RET after writing zero to +0x5dc and +0x4ac
0x0040d528 set-or-skip RET after the activation gate either writes +0x4ac/+0x5dc or skips activation
```

That helper is the current bounded retail candidate that sets or clears offsets `0x4ac` and `0x5dc` after energy/config checks. The command file logs the candidate object pointer plus these raw fields on entry and at the two known return paths:

- `+0x4ac`: candidate latch
- `+0x5dc`: candidate target/raw scalar
- `+0xfc`: candidate energy raw float bits
- `+0x2c8` / `+0x2cc`: candidate current/target transition raw float bits
- `+0x4b0`: linked object pointer used by the candidate activation gate
- linked object `+0x2c` and `+0xa0`: gate inputs compared against `this+0xfc` and threshold `0x005d856c`

This is intentionally a latch observer, not a broad per-frame monitor logger. It uses explicit post-write return-path breakpoints instead of debugger step-out commands, because step-out from an event handler can skip later commands in CDB. It should be attached only to a copied-profile, windowed `BEA.exe` process and should be kept under ignored/private runtime evidence.

## Parser

This pass adds a public-safe log parser:

```powershell
npm run test:cloak-runtime-observer-log
```

Equivalent direct command:

```powershell
py -3 tools\cloak_runtime_observer_log_probe.py --self-test
```

For a future private runtime log:

```powershell
py -3 tools\cloak_runtime_observer_log_probe.py --log <private-cdb-log> --out <ignored-json> --require-activation
```

The parser reports `ACTIVATION_OBSERVED` only when a helper enter/exit pair moves from latch `0` to non-zero latch with a non-zero target raw value.

## Next Runtime Use

Use this only after the copied-profile setup is ready:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\cloak-latch-observer.cdb.txt -PrintOnly
```

For a real run, omit `-PrintOnly` only after:

- the game has launched from an ignored copied profile,
- the copied executable is windowed and controllable,
- the scoped input target is the managed copied `BEA.exe` window,
- raw CDB logs, screenshots, frames, copied saves, and copied executables are kept under ignored/private paths,
- the managed process will be stopped and verified absent afterward.

## Acceptance Boundary

If the future private log shows `ACTIVATION_OBSERVED`, the next fire-while-cloaked runtime attempt can use that as the cloak-active baseline before firing.

If the log has no latch events, or only deactivation/no-activation events, the proof must remain blocked or inconclusive. Do not publish a stealth-break or stealth-preserve behavior claim from screenshots alone.

## Runtime Probe Follow-Up

`release/readiness/battleengine_cloak_runtime_observer_probe_2026-05-08.md` records the first copied-profile use of this observer.

The first CDB shape logged one helper entry event but did not log an activation pair and exposed that `gu` inside the breakpoint command can skip later commands in this target. The corrected explicit-return observer then attached cleanly, but the tested `level710` state plus two scoped `tap:TAB` inputs produced `NO_LATCH_EVENTS`. The result is useful yellow evidence for instrumentation and input-state setup, not cloak activation proof.

The next runtime wave should prove the active control prompt/binding before attaching or should use a broader state observer if this helper is not reached from the tested state.

`release/readiness/battleengine_cloak_input_dispatch_candidate_2026-05-08.md` then narrowed the input path: static retail evidence connects the decoded `Special function` binding through action `0x3B` to the same candidate helper call site. `release/readiness/battleengine_cloak_helper_gate_observer_update_2026-05-08.md` updates this observer to log the linked-object gate inputs so the next runtime pass can tell whether the helper was reached but blocked by state/setup gates.

`release/readiness/battleengine_cloak_gate_observer_probe_2026-05-08.md` records that copied-profile follow-up. Scoped `RSHIFT` and `TAB` reached the candidate helper again, but the parser reported `EVENTS_WITHOUT_ACTIVATION`, `eventCount=4`, `pairCount=2`, `activationPairCount=0`, and `gateBlockedPairCount=2`. Both helper pairs passed the energy side of the candidate gate and were blocked because linked object `+0xa0` was not above the threshold constant. The next probe should identify the linked object/state that makes that gate pass before any weapon-fire input is sent.

`release/readiness/battleengine_cloak_gate_state_candidate_2026-05-08.md` records that static/source-to-retail follow-up. Source cloak activation gates on `mConfiguration->mStealth > 0`, and existing read-only retail decompiles show `this+0x4b0` is the current profile/config pointer used for energy, recharge, slot-readiness, active-cloak energy burn, and the candidate helper's profile `+0xa0` threshold. The next runtime pass should identify or select a profile/configuration where profile `+0xa0` is positive before using the latch observer again.

`release/readiness/battleengine_profile_layout_candidate_2026-05-08.md` confirms the source-layout side of that field mapping. The x86 `CBattleEngineData` layout places `mStealth` at `+0xa0` and `mConfigurationName` at `+0xa8`, matching the retail cloak-gate field and the printed profile name offset, so the next runtime setup target should be a positive-`mStealth` profile rather than more input guessing.

`release/readiness/battleengine_profile_data_2026-05-08.md` identifies that setup target from read-only retail data. The local `data/battle engine configurations.dat` parses as six profiles, and `Sniper` is the only positive-stealth profile (`mStealth` / profile `+0xa0` = `80.0`). The next runtime observer should verify or select `Sniper` before testing cloak activation again.

## Validation

Commands:

```powershell
py -3 -m py_compile tools\cloak_runtime_observer_log_probe.py
npm run test:cloak-runtime-observer-log
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\cloak-latch-observer.cdb.txt -PrintOnly
```

Expected result:

- parser self-test passes,
- print-only CDB command generation passes without attaching,
- command file remains public-safe and contains no private paths,
- no game launch, CDB attach, Ghidra mutation, executable patch, or runtime proof is performed in this preparation wave.

## Not Claimed

- The preparation wave alone was not live runtime proof.
- The follow-up copied-profile probe attached CDB and launched a copied `BEA.exe`, but it did not prove cloak activation.
- This does not prove exact Steam retail identity for source `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.
- This does not prove that firing while cloaked breaks or preserves stealth.
- This does not mutate the installed game, original `BEA.exe`, original saves, copied profiles, or Ghidra projects.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative command/script names, public function names/addresses already present in the project, candidate offset names, and proof boundaries. Raw CDB logs and future runtime proof JSON must remain ignored under `subagents/`.
