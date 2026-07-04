# Ghidra HiveBoss Unit Vtable Tail Review Wave1087 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-02
Closeout completed: 2026-06-04
Scope: `hiveboss-unit-vtable-tail-review-wave1087`

Wave1087 recovered and saved ten previously missing Ghidra function boundaries from the CHiveBoss unit-family vtable tail at `0x005e1668`. The pass created bounded names, `__thiscall` signatures, comments, and tags for code pointers that previously exported as `INSTRUCTION_NO_FUNCTION`. It deliberately left the two `.rdata` vtable entries at `0x00617f58` and `0x006178c0` as non-function/data slots. The pass made no executable-byte changes, no installed-game changes, and no runtime claims.

Representative recovered rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x00480000` | `CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000` | Slot `26`, DATA xref `0x005e16d0`; checks fields around `this+0x170/0x29c`, may call helper `0x00441740` with string `0x0062ccb8` (`!!all flash!!`), returns `0x64` on that path, otherwise forwards an argument to `0x004fd5e0`. |
| `0x0050eb10` | `CHiveBossVFunc__GetClassNameString_0050eb10` | Slot `37`, DATA xref `0x005e16fc`; returns string `0x0063d844`, read back as `CHiveBoss`. |
| `0x0050eb20` | `CHiveBossVFunc__ForwardArgWithFlags40100400_0050eb20` | Slot `68`, DATA xref `0x005e1778`; ORs stack value with `0x40100400`, forwards to `0x004fcdc0`, and returns with `RET 0x4`. |
| `0x00480050` | `CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050` | Slot `70`, DATA xref `0x005e1780`; checks `hitContext+0x34` mask `0x01000000` and forwards four stack arguments to `CUnit__ApplyDamage` when clear. |
| `0x0050eb40` | `CHiveBossVFunc__ReturnFloat005d8580_0050eb40` | Slot `75`, DATA xref `0x005e1794`; returns float data at `0x005d8580`. |
| `0x004802f0` | `CHiveBossVFunc__MaybeScheduleEvent1388ForField74_004802f0` | Slot `80`, DATA xref `0x005e17a8`; calls `0x004fd140`, checks `this+0x74`, and may schedule event/type `0x1388` through global context `0x00672fc8`. |
| `0x00480220` | `CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220` | Slot `96`, DATA xref `0x005e17e8`; accumulates motion/offset fields around `this+0x250..0x29c`, then tail-jumps to `0x004fa8d0`. |
| `0x00480690` | `CHiveBossVFunc__ForwardArgToThingHelper4f3ac0_00480690` | Slot `120`, DATA xref `0x005e1848`; compact `RET 0x4` thunk forwarding the stack argument to `0x004f3ac0`. |
| `0x00480340` | `CHiveBossVFunc__BuildField164ContextAndDispatch_00480340` | Slot `125`, DATA xref `0x005e185c`; builds a stack context from `this+0x164`, `this+0x30`/`this+0x1c`, helper `0x0050ff10`, and global list `0x008553f8`, then dispatches through a returned object's slot `+0x24`. |
| `0x00480080` | `CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080` | Slot `140`, DATA xref `0x005e1898`; computes a scaled vector offset using global object `0x008a9d3c+0x1c`, field `this+0x2a0`, and helper `0x0047eb80`, then writes four dwords to the caller output buffer. |

Read-back evidence:

- Dry-run: `updated=0 skipped=0 created=0 would_create=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Apply: `updated=10 skipped=0 created=10 would_create=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 bad=0`
- Final dry-run: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Pre exports: `10` missing metadata rows, `10` missing tag rows, `12` xref rows, `1052` around-instruction rows, `2570` wide-instruction rows, `10` missing decompile rows, and `160` vtable-slot rows.
- Post exports: `10` metadata rows, `10` tag rows, `12` xref rows, `328` function-body instruction rows, `10` decompile rows, and `160` post vtable-slot rows.
- Vtable sample after Wave1087: `158` OK and `2` `NO_FUNCTION_AT_POINTER`. The ten selected code pointers now resolve to saved functions; the two remaining unresolved rows are `.rdata`/non-function entries at slots `29` and `147`.
- Queue after Wave1087: `6365/6365 = 100.00%` static function-quality closure, with `0` commentless functions, `0` exact-`undefined` signatures, `0` `param_N` signatures, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Expanded static re-audit surface: `1482/1560 = 95.00%`. Wave911 focused remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-141730_post_wave1087_hiveboss_unit_vtable_tail_verified`, `19` files, `175082375` bytes, `DiffCount=0`.

What this proves:

- The ten target code addresses now exist as saved Ghidra function entries.
- The saved names/signatures/comments/tags match the bounded Wave1087 static evidence.
- The CHiveBoss vtable tail sample resolves the ten selected former `NO_FUNCTION_AT_POINTER` code entries to functions.
- The all-function quality queue remains closed at 100%.

What remains unproven:

- Exact source virtual names.
- Concrete CHiveBoss/unit-family layout semantics.
- Runtime behavior or gameplay outcomes.
- BEA patching behavior.
- Clean-room rebuild parity.

Probe token anchor: Wave1087; hiveboss-unit-vtable-tail-review-wave1087; `0x00480000 CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000`; `0x0050eb10 CHiveBossVFunc__GetClassNameString_0050eb10`; `0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050`; `0x00480220 CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220`; `0x00480340 CHiveBossVFunc__BuildField164ContextAndDispatch_00480340`; `0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080`; `158` OK / `2` `NO_FUNCTION_AT_POINTER`; `1482/1560 = 95.00%`; `812/1408 = 57.67%`; `500/500 = 100.00%`; `6365/6365 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260602-141730_post_wave1087_hiveboss_unit_vtable_tail_verified`; boundary recovery.
