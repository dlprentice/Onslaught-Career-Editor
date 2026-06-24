# Ghidra Unit-Family Residual Vtable Final Review Wave1089 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `unit-family-residual-vtable-final-review-wave1089`

Wave1089 recovered and saved thirty-five previously missing function boundaries from the final ten-vtable unit-family residual sample. The wave covered code pointers from CInfantryUnit, CPod, CSentinel, CSimpleBuilding, CSubmarine, CGroundUnit, CAirUnit, and CGillMHead vtable neighborhoods. The pass made no executable-byte changes, no installed-game changes, and no runtime claims.

Representative recovered rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x00489ed0` | `CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0` | CInfantryUnit vtable `0x005e26b4` slot 23 / DATA xref `0x005e2710`; tests `this+0x24` mask `0x4` and returns one of two float constants. |
| `0x004d35d0` | `CPodVFunc__FlagArg70AndSeedMotion250_004d35d0` | CPod vtable `0x005dff14` slot 39 / DATA xref `0x005dffb0`; sets mask `0x02000010` in `arg+0x70`, seeds `this+0x250/0x254`, calls `0x004f86d0`, and copies an arg block into `this+0x258`. |
| `0x004deec0` | `CSentinelVFunc__BuildField164ContextAndDispatch_004deec0` | CSentinel vtable `0x005e0868` slot 125 / DATA xref `0x005e0a5c`; gates on `this+0x164`, builds a stack context, walks global list head `0x008553f8`, and dispatches through a returned object's slot `+0x24`. |
| `0x004dfc60` | `CSimpleBuildingVFunc__ResetVectorAndDispatchSlot70_004dfc60` | CSimpleBuilding vtable `0x005dfcc4` slot 98 / DATA xref `0x005dfe4c`; calls timestamp helper `0x00402000`, optionally runs cleanup when `this+0x2c` mask `0x4` is set, and dispatches slot `+0x70` with a zeroed stack vector. |
| `0x004eee80` | `CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80` | CSubmarine vtable `0x005e1418` slot 96 / DATA xref `0x005e1598`; dispatches slots `+0x130` and `+0x120`, accumulates/scales `this+0x14c..0x154` into `this+0x7c..0x84`, normalizes, and calls `0x004fa8d0`. |
| `0x0050e870` | `CAirUnitVFunc__ForwardArgWithFlags40000400_0050e870` | CAirUnit vtable `0x005e3700` slot 68 / DATA xref `0x005e3810`; ORs the stack value with `0x40000400`, forwards to `0x004fcdc0`, and returns with `RET 0x4`. |
| `0x0050e9d0` | `CInfantryUnitVFunc__GetClassNameString_0050e9d0` | CInfantryUnit vtable `0x005e26b4` slot 37 / DATA xref `0x005e2748`; returns string `0x0063d804`, read back as `CInfantryUnit`. |
| `0x0050eb50` | `CSubmarineVFunc__GetClassNameString_0050eb50` | CSubmarine vtable `0x005e1418` slot 37 / DATA xref `0x005e14ac`; returns string `0x0063d850`, read back as `CSubmarine`. |
| `0x0050ec60` | `CSentinelVFunc__GetClassNameString_0050ec60` | CSentinel vtable `0x005e0868` slot 37 / DATA xref `0x005e08fc`; returns string `0x0063d888`, read back as `CSentinel`. |
| `0x0050fd10` | `CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10` | CGillMHead vtable `0x005e4180` slot 68 / DATA xref `0x005e4290`; ORs the stack value with `0x40082000`, forwards to `0x004fcdc0`, and returns with `RET 0x4`. |

Read-back evidence:

- Pre exports: `35` code diagnoses, `20` data diagnoses, `70` code xref rows, `1715` around-instruction rows, `6335` wide-instruction rows, and `1600` pre vtable-slot rows.
- Dry-run: `updated=0 skipped=0 created=0 would_create=35 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`.
- Apply: `updated=35 skipped=0 created=35 would_create=0 renamed=0 would_rename=0 signature_updated=35 comment_only_updated=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry-run: `updated=0 skipped=35 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`.
- Post exports: `35` metadata rows, `35` tag rows, `70` xref rows, `468` function-body instruction rows, `35` decompile rows, and `1600` post vtable-slot rows.
- Vtable sample after Wave1089: `1580` OK and `20` `NO_FUNCTION_AT_POINTER`; the remaining entries are deliberate non-function/data table cells in the sampled vtables.
- Queue after Wave1089: `6410/6410 = 100.00%` static function-quality closure, with `0` commentless functions, `0` exact-`undefined` signatures, `0` `param_N` signatures, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Expanded static re-audit surface: `1527/1560 = 97.88%`. Wave911 focused remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The thirty-five selected code addresses now exist as saved Ghidra function entries.
- The saved names/signatures/comments/tags match bounded static vtable/xref/instruction/string evidence.
- The final ten-vtable residual sample now resolves all sampled code-pointer entries; only non-function/data entries remain unresolved in that sample.
- The live loaded Ghidra database remains at static function-quality closure with zero comment/signature debt.

What remains unproven:

- Exact source virtual names.
- Concrete unit-family owner layouts and field semantics.
- Runtime unit, targeting, motion, dispatch, or class-name behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Clean-room rebuild parity.

Probe token anchor: Wave1089; unit-family-residual-vtable-final-review-wave1089; `0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0`; `0x004d35d0 CPodVFunc__FlagArg70AndSeedMotion250_004d35d0`; `0x004deec0 CSentinelVFunc__BuildField164ContextAndDispatch_004deec0`; `0x004eee80 CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80`; `0x0050e9d0 CInfantryUnitVFunc__GetClassNameString_0050e9d0`; `0x0050fd10 CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10`; `1580` OK / `20` `NO_FUNCTION_AT_POINTER`; `1527/1560 = 97.88%`; `812/1408 = 57.67%`; `500/500 = 100.00%`; `6410/6410 = 100.00%`; `G:\GhidraBackups\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified`; boundary recovery.
