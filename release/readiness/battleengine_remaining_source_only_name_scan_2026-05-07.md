# BattleEngine Remaining Source-Only Direct-Name Scan - 2026-05-07

Status: public-safe reverse-engineering triage evidence, not retail identity proof

## Objective

Keep the current BattleEngine source-to-binary gap boundary honest by checking the ignored all-functions Ghidra name export for direct name candidates that would require revisiting the remaining source-only anchors.

No Ghidra mutation, runtime launch, executable patching, installed-game mutation, or private asset publication occurred in this pass.

## What Changed

`tools/battleengine_remaining_source_only_name_scan_probe.py` now verifies that the current source-to-binary gap report still leaves exactly this anchor in `SOURCE_ONLY_PENDING_BINARY_IDENTITY` status:

- `weapon_fire_breaks_stealth`

The probe then scans the ignored `functions_all.tsv` export under `subagents/` for a strict direct-name pattern tied to that anchor.

Earlier in this same campaign, `jet_energy_cost`, `jet_stall_forces_morph_to_walker`, `transform_reject_special_moves`, `walker_recharge`, and `cloak_energy_gate_burn_and_render` also had no direct-name matches. They were later moved out of this source-only set by focused candidate notes, which add partial CMonitor/decompile evidence without claiming exact identity.

Follow-up operand-token triage at `release/readiness/battleengine_weapon_stealth_operand_search_2026-05-07.md` scanned suspected stealth-adjacent retail fields and found `0` weapon/fire/projectile object-offset rows. That keeps the anchor source-only; it is not absence proof.

Follow-up source-callsite triage at `release/readiness/battleengine_weapon_fired_source_callsite_2026-05-07.md` found no unexpected direct source callsite outside the expected declarations/definitions and the part-delegation calls inside `CBattleEngine::WeaponFired`. That explains the static identity difficulty; it does not prove retail absence.

## Validation

Commands:

```powershell
py -3 -m py_compile tools\battleengine_remaining_source_only_name_scan_probe.py
cmd.exe /c npm run test:battleengine-remaining-source-only-name-scan
```

Working directory:

```text
repo root
```

Results:

- Python compile: PASS.
- Remaining source-only direct-name scan: PASS.
- Function rows checked: `5862`.
- Strict direct-name matches:
  - `weapon_fire_breaks_stealth`: `0`

## What This Proves

- The current BattleEngine source-to-binary gap report still classifies exactly the tracked anchor above as source-only pending retail-binary identity.
- The current ignored all-functions Ghidra name export contains no strict direct-name matches for that anchor pattern.
- Future agents now have a guard that will fail if the local Ghidra name export gains an obvious direct-name candidate before the public evidence is updated.

## What This Does Not Prove

- This does not prove absence of a retail implementation for the remaining anchor.
- This does not identify candidate decompile/control-flow body for the remaining anchor.
- This does not prove exact Steam retail function identity.
- This does not mutate Ghidra names or apply a rename map.
- This does not prove runtime gameplay behavior for cloak or weapon-fired stealth.
- This does not make the game rebuildable from scratch.

## Privacy / Release Safety

The committed evidence is public-safe. It records only repo-relative filenames, public anchor keys, direct-name patterns, counts, and proof boundaries.

The raw JSON scan output and the Ghidra all-functions export remain ignored under `subagents/`.

## Recommended Next Step

Move from direct-name triage to a bounded read-only decompile/control-flow search for one remaining anchor at a time. Weapon-fired stealth reset is the better next candidate because recent cloak and weapon helper exports already narrowed nearby context without proving the reset path.
