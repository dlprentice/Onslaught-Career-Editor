# BattleEngine Jet Energy/Stall Candidate Bridge - 2026-05-07

Status: public-safe partial retail candidate evidence, not exact source-method identity proof

## Objective

Advance BattleEngine rebuild coverage for jet movement by moving two source-only anchors to partial retail candidate status when supported by fresh read-only Ghidra decompile and constant evidence:

- `jet_energy_cost`
- `jet_stall_forces_morph_to_walker`

No Ghidra rename-map mutation, runtime launch, executable patching, installed-game mutation, or private asset publication occurred in this pass.

## What Changed

Added:

- `tools/battleengine_jet_stall_candidate_probe.py`
- `npm run test:battleengine-jet-stall-candidate`

The probe validates ignored evidence under `subagents/battleengine-jet-stall-candidate/current/`:

- a fresh read-only Ghidra decompile export for `CMonitor__Process` at `0x004081c0`,
- a read-only constant scan for selected `.rdata` float labels used by that decompile,
- source tokens in `references/Onslaught/BattleEngineJetPart.cpp`.

## Commands

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-jet-stall-candidate/current/addresses.txt subagents/battleengine-jet-stall-candidate/current/decompile 90"
py -3 -m py_compile tools\battleengine_jet_stall_candidate_probe.py tools\battleengine_source_binary_gap_probe.py tools\battleengine_remaining_source_only_name_scan_probe.py
cmd.exe /c npm run test:battleengine-jet-stall-candidate
```

## Result

- Headless Ghidra export passed with targets `1`, dumped `1`, missing `0`, failed `0`.
- The export printed the known GhydraMCP extension manifest warnings and `REPORT: Save succeeded`; this is treated as tool-environment/project-save noise for a read-only export script, not as an intentional Ghidra mutation.
- Python compile check passed.
- Jet energy/stall candidate probe passed source tokens `7/7` and decompile tokens `8/8`.

## Candidate Evidence

The source jet movement anchor still contains:

- min/max air-energy cost tokens,
- energy subtraction,
- low-speed stall entry,
- stall timer,
- Morph fallback.

The fresh `CMonitor__Process` decompile contains:

- a call to `CMonitor__UpdateFlightWalkerTransitionState`,
- an energy-like subtract from offset `0x280` gated by `_DAT_005d8c30` and `_DAT_005d8c2c`,
- a velocity-threshold path that resets or increments offset `0x310`,
- a vfunc call through offset `0x110` after the counter exceeds `5`.

The read-only constant scan maps selected labels to:

| Label | VA | Float |
| --- | --- | ---: |
| `_DAT_005d8c2c` | `0x005d8c2c` | `0.015` |
| `_DAT_005d8c30` | `0x005d8c30` | `-0.03` |
| `_DAT_005d8570` | `0x005d8570` | about `0.0001` |

## What This Proves

- `jet_energy_cost` now has partial retail candidate evidence through the `CMonitor__Process` energy-offset subtract and `.rdata` constant read-back.
- `jet_stall_forces_morph_to_walker` now has partial retail candidate evidence through the `CMonitor__Process` velocity-threshold/counter/vfunc path.
- The source-to-binary gap accounting can move those two anchors out of the source-only bucket without claiming exact identity.

## What This Does Not Prove

- This does not prove exact source-to-retail identity for `BattleEngineJetPart` movement methods.
- This does not prove whether retail `CMonitor__Process` inlined, reorganized, or only partially overlaps the source jet-energy/stall methods.
- This does not prove walker recharge.
- This does not prove runtime flight, stall, or forced walker transition behavior.
- This does not apply a Ghidra rename map.
- This does not mutate `BEA.exe`.
- This does not launch `BEA.exe`.
- This does not make the repository rebuildable from scratch.

## Privacy / Release Safety

The committed evidence is public-safe. It records only repo-relative paths, public source-token names, function names, public VAs, constants, and proof boundaries.

The raw decompile export, constant JSON, and verifier JSON remain ignored under `subagents/`.

## Recommended Next Step

Keep `walker_recharge`, `transform_reject_special_moves`, `cloak_energy_gate_burn_and_render`, and `weapon_fire_breaks_stealth` in source-only status until a bounded decompile/control-flow pass finds comparable candidate evidence. `walker_recharge` is the closest next target because the source anchor is small and tied to energy/shield coupling.
