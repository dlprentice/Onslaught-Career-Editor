# MissionScript Thing Value / Engine Helper Command-Effect Static Proof Readiness Note

Status: static thing-value/engine-helper command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-thing-value-engine-helper-command-effect-static`

This readiness note records the static proof slice for `missionscript-thing-value-engine-helper-command-effect-static-proof.md` and `missionscript-thing-value-engine-helper-command-effect.v1.json`.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Address | Static evidence |
| --- | --- |
| `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg` | Guard `+0x34 & 0x10`; getter slot `+0x38`; selected thing vfunc slot `+0x198`; descriptor context `DisableWeapon`. |
| `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg` | Guard `+0x34 & 0x10`; getter slot `+0x38`; selected thing vfunc slot `+0x19c`; descriptor context `EnableFlightMode`. |
| `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg` | Guard `+0x34 & 0x10`; getter slot `+0x38`; calls `CEngine__EnableThingByNameFlag`; descriptor context `DisableSpawner`. |
| `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg` | Guard `+0x34 & 0x10`; getter slot `+0x38`; calls `CEngine__DisableThingByNameFlag`; descriptor context `SetName`. |
| `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg` | Guard `+0x34 & 0x10`; float getter slot `+0x34`; selected thing vfunc slot `+0x1c8`; descriptor context `TeleportOrientation`. |
| `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg` | Guard `+0x34 & 0x10`; integer/faction-like getter slot `+0x30`; calls `CUnit__SetFactionForHierarchy`; descriptor context `SetWindVector`. |

Read-back evidence:

- Wave582 post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `534` instruction rows, `6` decompile rows, and `32` vtable rows.
- Wave582 apply logs reported dry `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, apply `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, and final dry `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- A copied loose-MSL non-comment scan found `15` `DisableWeapon`, `1` `EnableFlightMode`, `2` `DisableSpawner`, `4` `SetName`, `5` `TeleportOrientation`, and `0` `SetWindVector` rows.
- Wave582 backup: `G:\GhidraBackups\BEA_20260519-082352_post_wave582_iscript_thing_value_verified`, `19` files, `160598919` bytes, `DiffCount=0`, manifest hash `CF051683F3A5BA8E0E6B7266941DA5C46CE53224EE2AC65FA16F1D4DF8F74CDF`.
- Latest static closeout backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

What this proves:

- Saved retail Ghidra metadata/decompile/xref/instruction evidence supports the six Wave582 handlers.
- The handler bodies expose guard, argument getter, thing vfunc, engine helper, and unit helper dispatch evidence useful for clean-room MissionScript planning.
- Descriptor names and loose-MSL counts are recorded as static planning context without overclaiming runtime command effects.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime `DisableWeapon`, `EnableFlightMode`, `DisableSpawner`, `SetName`, `TeleportOrientation`, or `SetWindVector` behavior.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact command descriptor layout, exact command arity, exact thing vfunc semantics, exact thing layout, or exact unit faction enum.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.
