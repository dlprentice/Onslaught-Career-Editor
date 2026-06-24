# BattleEngine Weapon-Fired Stealth Runtime Proof Plan - 2026-05-07

Status: public-safe copied-profile proof plan, not runtime proof

## Objective

Design the next safe runtime wave for the remaining `weapon_fire_breaks_stealth` source-only anchor without mutating the installed Steam game, the original `BEA.exe`, original saves, Ghidra projects, or public release scope.

The narrow question is:

```text
In the Steam retail build, when the player is cloaked and fires a weapon, does the live runtime clear or visibly break stealth?
```

## Current Evidence Boundary

Static/source work already proves:

- Stuart source defines `CBattleEngine::WeaponFired(...)` and clears stealth after either jet or walker weapon fire reports success.
- The current source-to-binary gap probe reports source anchors `17/17`, source-only anchors `1`, and partial retail candidates `16`.
- The current all-functions name scan checked `5862` Ghidra rows and found `0` strict direct-name matches for the remaining weapon-fired stealth anchor.
- The current operand-token scan checked `377` stealth-adjacent operand rows, including `64` object-offset rows, and found `0` weapon/fire/projectile object-offset rows.
- The current source-callsite scan found `0` unexpected direct source callsites outside expected declarations/definitions and the part-delegation calls inside `CBattleEngine::WeaponFired`.
- The current source-path probe shows player fire input reaches BattleEngine walker/jet part delegation and then `weapon->Fire()`, but the referenced `Weapon.h` / `Weapon.cpp` implementation is not present in this checkout.

This means more broad static name or operand scanning is unlikely to be the highest-value next step. A copied-profile runtime probe can answer the player-visible behavior even if exact one-to-one retail method identity remains unresolved.

## Non-Negotiable Safety

- Do not patch or mutate the installed/original Steam `BEA.exe`.
- Do not patch or mutate original saves, profiles, or `defaultoptions.bea`.
- Do not synthesize `.bes` or `defaultoptions.bea` buffers from scratch.
- Copy a valid profile/save/options baseline before any proof setup.
- Use an app-owned copied-profile root and app-owned proof root.
- Apply the `force_windowed` patch only to the copied `BEA.exe` if windowed control is required.
- Keep raw screenshots, captures, frame dumps, copied saves, copied executables, debugger logs, process logs with private paths, and proof JSON under ignored/private paths.
- Publish only sanitized status, counts, command names, and behavioral conclusions.
- Stop the managed process and confirm no `BEA.exe` process remains at the end.

## Proposed Runtime Matrix

| Step | Purpose | Expected Private Evidence | Public Claim If Green |
| --- | --- | --- | --- |
| Copied-profile prep | Create an isolated runtime profile from the installed game. | Copied-profile manifest, copied executable hash, proof-root path. | Runtime proof used copied material only. |
| Windowed patch on copy | Keep the game controllable for capture/input. | Byte verification for the copied executable before and after `force_windowed`. | Windowed control used a copied executable only. |
| Baseline launch and stop | Confirm managed copied-profile launch and cleanup before behavior probing. | Launch/capture/stop log and process-list cleanup proof. | The proof harness can start and stop the copied runtime cleanly. |
| Reach a cloak-capable state | Enter a mission/state where the player can cloak and fire at least one weapon. | Private navigation/capture notes and selected state. | The behavior was observed in a cloak-capable runtime state. |
| Cloak baseline capture | Activate cloak and capture the visual/state baseline before firing. | Private frame/capture and, if available, debugger/watch values. | Cloak was active before the firing check. |
| Fire while cloaked | Send one bounded, scoped weapon input to the managed BEA window. | Scoped-input log naming the managed target plus before/after captures. | Weapon input was sent to the managed copied runtime only. |
| After-fire capture | Observe whether stealth visibly clears, persists, or enters an ambiguous transition. | Private after-fire capture and optional debugger/watch values. | Runtime either clears stealth, preserves stealth, or remains inconclusive under the tested state. |
| Stop and cleanup | Stop the managed process and verify no BEA process remains. | Process-list proof. | Runtime proof left no managed BEA process. |

## Suggested Execution Guard

Do not run this proof until the operator can confirm or the test harness can reliably create a cloak-capable starting state. If mission navigation, save setup, or scoped input is not reliable enough, stop at copied-profile launch/cleanup and document the blocker rather than forcing an ambiguous gameplay claim.

`release/readiness/battleengine_weapon_stealth_runtime_setup_target_2026-05-07.md` identifies `level710` as the preferred first setup target because tracked mission evidence shows cloak-specific help and Tatiana character-message keys in `Level710script.msl`. `release/readiness/battleengine_level_configuration_2026-05-08.md` strengthens that target: the local read-only `710_res_PC.aya` world-resource data exposes a structural `BSWD` BattleEngineConfigurations header table containing only `Sniper`, an `RLWD` table containing `Standard` / `Sniper` / `Laser` / `Blaster`, and a `Level710script` reference. Read-only Ghidra export also shows the initial-spawn path resolving config strings through the loaded config table into `CBattleEngineInitThing::mConfigurationId`. If `level710` cannot be reached or controlled reliably, `level611` / `level612` and `level621` / `level622` are weaker fallback clue levels because their mission event indexes mention `Cloaked` or `Stealth`; they still require runtime proof that the player can cloak and fire in the tested state.

`release/readiness/battleengine_level_configuration_index_2026-05-08.md` broadens this setup map across the local numeric level corpus. Base-world `Sniper` appears only in levels `710`, `720`, `731`, and `732`; those are the strongest static fallback targets before using levels where `Sniper` appears only in the runtime-level table.

`release/readiness/battleengine_level_launch_helper_2026-05-07.md` records the small helper hardening that lets `tools/start_game_profile.ps1` accept a numeric-only `-level <id>` argument. Use `-skipfmv -level 710` as the preferred PrintOnly/launch argument pair for the later copied-profile proof, after the copied executable has been prepared and windowed control is safe.

`release/readiness/battleengine_cloak_input_helper_2026-05-07.md` records scoped-input helper hardening, and `release/readiness/battleengine_cloak_input_binding_triage_2026-05-08.md` corrects the next input target. The current decoded `Special function` binding is `P1=RShift` and `P2=Tab`; do not treat backslash as the current default cloak binding for this profile.

`release/readiness/battleengine_weapon_stealth_runtime_probe_2026-05-07.md` records the first copied-profile runtime attempt. It proved direct `-skipfmv -level 710` launch, managed-window capture, scoped `TAB` input, scoped center mouse click, and cleanup. It did not prove the stealth-break behavior because the private captures did not unambiguously prove a cloak-active baseline before firing.

`release/readiness/battleengine_cloak_runtime_observer_plan_2026-05-07.md` prepares the stronger next detector. It adds `tools/runtime-probes/cloak-latch-observer.cdb.txt` and `tools/cloak_runtime_observer_log_probe.py`, so a future copied-profile run can require a candidate latch activation event before firing instead of relying on screenshots alone.

`release/readiness/battleengine_cloak_runtime_observer_probe_2026-05-08.md` records the first copied-profile use of that detector. The result was inconclusive for activation: the first observer shape saw one helper entry event without activation and exposed CDB step-out fragility; the corrected explicit-return observer attached cleanly but produced no latch events under two scoped `tap:TAB` inputs. The next runtime wave should verify the active cloak binding or broaden the observer before sending any weapon-fire input.

`release/readiness/battleengine_cloak_binding_observer_probe_2026-05-08.md` records the follow-up copied-profile observer wave using the corrected decoded bindings. Scoped `RSHIFT` and `TAB` inputs both reached the candidate latch helper, but the fixed parser reported `EVENTS_WITHOUT_ACTIVATION`, `eventCount=4`, `pairCount=2`, and `activationPairCount=0`. The next proof should inspect player-control/input-dispatch state or broaden the observer before any weapon-fire input.

`release/readiness/battleengine_cloak_input_dispatch_candidate_2026-05-08.md` records that static retail dispatch evidence supports the decoded input path: `Controls__DispatchRemap` maps UI action `0x4C` to persisted entry `0x3B` with binding type `8`, read-only retail jump-table bytes map action `0x3B` to call site `0x004d32e2`, and Ghidra xrefs show that call site invokes `CGeneralVolume__Update4ACLatchFromHeightAndA0`. This keeps the next runtime blocker focused on helper state/setup gates, not wrong-key triage.

`release/readiness/battleengine_cloak_helper_gate_observer_update_2026-05-08.md` hardens the observer for that next blocker. It logs the linked object pointer, linked `+0x2c`, linked `+0xa0`, and threshold raw value used by the helper's candidate activation gates, and the parser can now classify gate-blocked pairs before any weapon-fire input is sent.

`release/readiness/battleengine_cloak_gate_observer_probe_2026-05-08.md` records the first copied-profile use of the gate-aware observer. Scoped `RSHIFT` and `TAB` reached the candidate helper again, but the gate-aware parser reported `EVENTS_WITHOUT_ACTIVATION`, `eventCount=4`, `pairCount=2`, `activationPairCount=0`, and `gateBlockedPairCount=2`. Both pairs were blocked by the linked-object threshold side of the candidate activation gate, so the next runtime wave should identify the linked object/state that makes linked `+0xa0` exceed the threshold before sending weapon-fire input.

`release/readiness/battleengine_cloak_gate_state_candidate_2026-05-08.md` narrows that state/setup blocker. Source `CBattleEngine::Cloak()` requires `mConfiguration->mStealth > 0`, and read-only retail decompiles show `this+0x4b0` is the current profile/config pointer reused for energy, recharge, per-slot readiness, active-cloak energy burn, and the candidate helper's profile `+0xa0` threshold. The next runtime wave should identify or select a profile/configuration with positive profile `+0xa0` before any fire-while-cloaked test.

`release/readiness/battleengine_profile_layout_candidate_2026-05-08.md` makes the `+0xa0` side stronger: source x86 layout places `CBattleEngineData::mStealth` at `+0xa0` and `mConfigurationName` at `+0xa8`, and existing retail decompiles use `+0xa8` as the profile name. Treat the next runtime setup target as a positive-`mStealth` profile/configuration.

`release/readiness/battleengine_profile_data_2026-05-08.md` identifies that target from read-only retail profile data: the local install parses six profiles, and `Sniper` is the only positive-stealth profile with `mStealth` / profile `+0xa0` = `80.0`. Do not send weapon-fire input until a copied runtime observer proves cloak activation while the runtime is using or has selected `Sniper`.

## Acceptance Language

If firing while cloaked visibly clears stealth:

```text
Copied-profile runtime proof observed that firing while cloaked breaks stealth in the tested Steam retail state. Raw captures and copied-profile proof remain private; public docs record only the behavior class, safety posture, and sanitized command outcomes.
```

If firing while cloaked visibly preserves stealth:

```text
Copied-profile runtime proof observed that firing while cloaked did not break stealth in the tested Steam retail state. This narrows the source-to-retail gap but does not prove every weapon, mission, or cloak state.
```

If the run is ambiguous:

```text
Copied-profile runtime proof could not conclusively determine whether firing breaks stealth. The blocker was recorded, the copied runtime was stopped, and exact retail behavior remains unproven.
```

## Validation To Run After A Runtime Wave

- `tasklist.exe /FI "IMAGENAME eq BEA.exe"` after stop.
- `py -3 tools\cloak_runtime_observer_log_probe.py --log <private-cdb-log> --out <ignored-json> --require-activation` when the cloak latch observer is used.
- A private proof parser/checker if one is added for scoped-input and capture logs.
- `npm run test:battleengine-source-binary-gap`
- `npm run test:battleengine-logic-coverage`
- `npm run test:md-links`
- `npm run test:doc-commands`
- `py -3 tools\docsync_check.py`
- `py -3 tools\release_profile_snapshot.py --check`
- `py -3 tools\release_curated_manifest.py --check`
- `npm run test:public-allowlist`
- `git diff --check`

## Not Claimed By This Plan

- This plan is not runtime proof.
- This plan does not launch BEA.
- This plan does not prove exact Steam retail function identity for `CBattleEngine::WeaponFired`.
- This plan does not prove source-to-retail rebuild parity.
- This plan does not authorize mutation of the installed game or original save/profile files.
- This plan does not prove behavior for every weapon, mission, or player state.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative evidence names, sanitized counts, proof boundaries, and planned command classes. It does not include binaries, private absolute paths, screenshots, frame data, copied executables, copied saves, debugger logs, Ghidra mutation logs, or raw runtime proof JSON.
