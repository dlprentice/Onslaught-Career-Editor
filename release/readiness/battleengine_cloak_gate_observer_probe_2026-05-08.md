# BattleEngine Cloak Gate Observer Probe - 2026-05-08

Status: public-safe copied-profile runtime observer probe, gate-blocked for cloak activation

## Objective

Run the gate-aware cloak observer against the ignored copied profile after static dispatch evidence showed decoded `Special function` inputs reach the candidate latch helper.

The narrow gate was:

```text
When scoped RShift/Tab inputs reach the candidate helper, do the helper's linked-object activation gates pass?
```

## Safety Boundary

- The installed Steam game folder was treated as read-only source material.
- The runtime target was the ignored copied profile under `subagents/`.
- The copied executable had already been prepared for windowed control through the copied-profile patch path.
- Raw CDB logs, launch JSON, window scans, scoped-input logs, parser JSON, and private paths remained ignored under `subagents/`.
- No weapon-fire input was sent.
- The copied `BEA.exe` process and CDB process were stopped after the probe.
- No installed game file, original `BEA.exe`, original save/options file, Ghidra project, or public release artifact was mutated.

## Commands / Evidence Summary

| Step | Result | Public-safe summary |
| --- | --- | --- |
| Copied-profile launch | PASS | Launched the copied profile with `-skipfmv -level 710` from the ignored runtime root. |
| Window scan | PASS | Found one visible managed `BEA.exe` window for the copied process. |
| CDB attach | PASS | Attached x86 CDB with the gate-aware cloak latch observer. |
| Scoped input | SENT/YELLOW | Sent only the decoded cloak bindings, `RSHIFT` then `TAB`, to the exact managed copied window. |
| Parser result | YELLOW | The private summary reported `EVENTS_WITHOUT_ACTIVATION`, `eventCount=4`, `pairCount=2`, `activationPairCount=0`, and `gateBlockedPairCount=2`. |
| Gate classification | YELLOW | Both observed helper pairs passed the energy side of the candidate gate but were blocked because linked object `+0xa0` was not above the threshold constant. |
| Stop/cleanup | PASS | The copied `BEA.exe` process and CDB process were stopped; a final process scan returned no `BEA` or `cdb` rows. |

## Finding

This probe proves the decoded inputs reached the candidate helper again, and the stronger observer now explains the non-activation result for this tested state.

The observed blocker was not wrong-key triage. In both helper pairs:

- the input reached the candidate helper,
- the candidate latch stayed off,
- the energy comparison side of the candidate gate passed,
- the linked-object threshold comparison did not pass,
- no weapon-fire input was sent.

The next runtime question is therefore a state/setup question: what runtime object and state make linked object `+0xa0` exceed the candidate threshold, and does that correspond to the real cloak-capable phase?

## Not Proven

- Runtime cloak activation.
- A cloak-active baseline before firing.
- Whether firing while cloaked breaks or preserves stealth.
- Exact Steam retail identity for source `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.
- Retail `RF_CLOAKED` render-flag identity.
- Rebuild parity for the cloak or weapon-fired stealth system.
- Ghidra project mutation or semantic rename promotion.

## Next Runtime Direction

Do not send weapon-fire input yet.

Good next steps:

- identify the linked object behind helper field `+0x4b0` and its `+0xa0` meaning,
- find a copied-profile start state or setup step where the linked-object threshold gate passes,
- add a narrow read-only observer for the upstream dispatch/state owner if the helper is called before the game reaches a truly cloak-capable state,
- keep raw logs and captures private and continue publishing only sanitized event counts and proof boundaries.

## Validation

Public-safe validation commands for this wave:

```powershell
py -3 tools\cloak_runtime_observer_log_probe.py --log <private-log> --out <private-json>
```

The parser intentionally did not use `--require-activation` as a pass criterion for this wave because the objective was to classify the activation gate blocker, not to claim cloak activation.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative tool names, sanitized statuses, public addresses already used by the project, event counts, and explicit proof boundaries. It does not include private screenshots, copied saves, copied executables, raw captures, full local paths, raw CDB logs, or raw runtime proof JSON.
