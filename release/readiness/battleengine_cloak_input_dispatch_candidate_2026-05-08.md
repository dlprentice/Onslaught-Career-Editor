# BattleEngine Cloak Input Dispatch Candidate - 2026-05-08

Status: public-safe bounded static retail-candidate evidence, not runtime activation proof

## Objective

Narrow the cloak activation blocker found by the copied-profile observer runs. The previous runtime pass proved scoped `RSHIFT` and `TAB` inputs reached the current candidate latch helper but did not produce activation. This pass checks whether the current static retail input-dispatch evidence really connects the decoded `Special function` binding to that helper.

## Inputs

Fresh ignored Ghidra headless exports were written under:

```text
subagents/battleengine-cloak-input-dispatch-candidate/current/
```

The raw exports remain ignored/private. They include:

- xrefs for the candidate latch helper and controls binding functions
- decompiles for `CGeneralVolume__Update4ACLatchFromHeightAndA0`, `Controls__DispatchRemap`, `ControlsUI__RenderBindingsList`, and `OptionsEntries__SetBindingSlot`
- instruction context around the latch-helper call site and controls remap call sites

The probe also reads the local Steam `BEA.exe` as read-only input to decode the small retail jump table around the candidate dispatch path. It does not write to or patch that file.

## Probe

Command:

```powershell
npm run test:battleengine-cloak-input-dispatch-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_cloak_input_dispatch_candidate_probe.py --check
```

Result:

```text
BattleEngine cloak input-dispatch candidate probe
Status: pass
Action 0x3B target: 0x004d32e2
Failures: 0
```

## What This Proves

- Current `Controls__DispatchRemap` decompile maps UI action `0x4C` to persisted entry `0x3B` with binding type `8`.
- Read-only retail jump-table bytes map action `0x3B` to dispatch call site `0x004d32e2`.
- The Ghidra xref export confirms `0x004d32e2` calls `CGeneralVolume__Update4ACLatchFromHeightAndA0` at `0x0040d4d0`.
- The instruction export shows the action-index table at `0x004d345c` and jump table at `0x004d3434` feed that call site.

## What This Means For Runtime Proof

This strengthens the input side of the cloak hypothesis: the decoded `Special function` entry is not merely a menu label, and action `0x3B` statically reaches the same candidate helper that the copied-profile observer hit.

The yellow runtime result is therefore more likely a state/setup/helper-gate question than a wrong-key question. The next runtime wave should instrument or inspect the helper's state inputs before sending weapon-fire input.

## Not Proven

- Exact source-to-retail identity for `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.
- Runtime cloak activation in the tested level/profile state.
- Retail `RF_CLOAKED` render-flag identity.
- Weapon-fired stealth reset identity.
- Runtime fire-while-cloaked behavior.
- Ghidra rename-map mutation or project semantic promotion.
- Rebuildable open-source gameplay implementation.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative artifact paths, sanitized addresses already present in the project, command names, and proof boundaries. It does not include binaries, private absolute paths, raw decompile bodies, screenshots, frame data, copied executables, copied saves, debugger logs, Ghidra mutation logs, or raw runtime proof JSON.
