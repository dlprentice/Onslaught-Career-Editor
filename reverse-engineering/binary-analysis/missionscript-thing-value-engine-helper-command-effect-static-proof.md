# MissionScript Thing Value / Engine Helper Command-Effect Static Proof

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00535560` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: static thing-value/engine-helper command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-thing-value-engine-helper-command-effect-static`
Artifact: `missionscript-thing-value-engine-helper-command-effect-static-proof.md`; schema: `missionscript-thing-value-engine-helper-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave582, the completed MissionScript descriptor schema, and a copied loose-MSL command-name scan into a machine-checkable thing-value/engine-helper bridge. It is the next narrow MissionScript command-effect child lane after the completed slot, objective/outcome, message/audio, Goodie-state, selected `SpawnThing`, selected `GetThingRef`, cutscene pan-camera/position, and vector/range static proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Vfunc value handlers | Wave582 saved `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg` and `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg` as three-stack-argument script-context handlers. Both gate on `+0x34 & 0x10`, read the first argument through datatype getter slot `+0x38`, and dispatch selected thing vfunc slots `+0x198` and `+0x19c`. |
| Engine helper handlers | Wave582 saved `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg` and `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`. Both gate on `+0x34 & 0x10`, read a name/value through getter slot `+0x38`, and call `CEngine__EnableThingByNameFlag` or `CEngine__DisableThingByNameFlag` with `context+0x10`. |
| Float and unit helper handlers | Wave582 saved `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg` and `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg`. The first reads a float through getter slot `+0x34` and dispatches thing vfunc `+0x1c8`; the second reads an integer/faction-like state through getter slot `+0x30` and calls `CUnit__SetFactionForHierarchy`. |
| Descriptor context | The descriptor schema preserves raw command rows `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, and `SetWindVector` with raw entry values that resolve to the Wave582 handler addresses after Ghidra naming. This proof records those names as static descriptor context only; exact descriptor field layout, exact command arity, exact thing vfunc semantics, exact unit faction enum, and runtime command effects remain unproven. |
| Loose corpus scan | A copied loose-MSL non-comment token scan found `15` `DisableWeapon`, `1` `EnableFlightMode`, `2` `DisableSpawner`, `4` `SetName`, `5` `TeleportOrientation`, and `0` `SetWindVector` rows. These are static corpus context rows, not live loose-MSL loading or runtime effect proof. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave582 metadata/tag/xref/decompile rows | `6` / `6` / `6` / `6` |
| Wave582 instruction rows and vtable rows | `534` / `32` |

Backups already verified by their original waves:

- Wave582: `[maintainer-local-ghidra-backup-root]\BEA_20260519-082352_post_wave582_iscript_thing_value_verified`
- Latest static closeout backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`

## Why This Matters

This gives clean-room MissionScript planning a bounded bridge from command-name context to thing/engine helper dispatch shape:

- Guard bit: `+0x34 & 0x10`.
- Argument getter slots: `+0x38`, `+0x34`, and `+0x30`.
- Thing vfunc slots: `+0x198`, `+0x19c`, and `+0x1c8`.
- Engine helpers: `CEngine__EnableThingByNameFlag` and `CEngine__DisableThingByNameFlag`.
- Unit helper: `CUnit__SetFactionForHierarchy`.

The proof intentionally does not claim that `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, or `SetWindVector` runtime behavior has been proven. It preserves their descriptor/corpus context so a later copied/app-owned proof can select one visible command path without guessing from the binary.

## Claim Boundary

This proves static thing-value/engine-helper command-effect accounting from saved retail Ghidra metadata, xrefs, instruction/decompile rows, descriptor context, and copied loose-MSL command-name counts. It does not prove runtime MissionScript execution, runtime command effects, runtime `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, or `SetWindVector` behavior, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact command arity, exact thing vfunc semantics, exact thing layout, exact unit faction enum, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
