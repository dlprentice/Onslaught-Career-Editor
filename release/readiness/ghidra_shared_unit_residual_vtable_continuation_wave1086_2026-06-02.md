# Ghidra Shared Unit Residual Vtable Continuation Wave1086 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-02
Scope: `shared-unit-residual-vtable-continuation-wave1086`

Wave1086 continued the shared unit-family residual vtable-boundary recovery line from Waves1083 and 1085. It created 24 previously missing Ghidra function boundaries for repeated or high-value `NO_FUNCTION_AT_POINTER` entries in sampled CAirUnit/CRadar/unit-family/CUnitAI/GillMHead-adjacent vtable rows. The pass saved bounded names, `__thiscall` signatures, comments, and tags. It made no executable-byte changes, no installed-game changes, and no runtime claims.

Representative recovered rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x00405dc0` | `SharedUnitVFunc__ReturnFloat005d858c_00405dc0` | Returns float data at `0x005d858c`; sampled DATA vtable refs include slot `102`. |
| `0x00401f70` | `SharedUnitVFunc__TestFieldCcDeltaBelow015_00401f70` | Compares global float `0x00672fd0 - this+0xcc` against `0x005d8588`; sampled slot `97`. |
| `0x004037a0` | `SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0` | Forwards four stack args to `CUnit__ApplyDamage`, calls vtable slot `+0x160` selector `0x19`, and updates candidate vectors/field `+0xac`; `RET 0x10`. |
| `0x00403a90` | `SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90` | Quantizes/clamps float inputs, copies a 16-byte vector argument, and dispatches field `0x208` vtable slot `+0x10`; `RET 0x14`. |
| `0x00403b60` | `SharedUnitVFunc__ReturnFlag2cScaledSlot40Float_00403b60` | Flag-gated float return using this+`0x2c` mask `0x4`, vtable slot `+0x40`, and constants `0x005d8614/0x005d8610/0x005d860c`. |
| `0x00417df0` | `SharedUnitVFunc__HandleType1388Field74Resource_00417df0` | Checks event word `+0x4 == 0x1388`, releases/clears `this+0x74`, otherwise forwards to `0x004f9820`. |
| `0x004284f0` | `CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0` | Returns `-atan2`-style FPATAN result from `this+0x40` and `this+0x50`. |
| `0x004287c0` | `CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0` | Dispatches `this+0x26c` slot `+0x6c` when present, otherwise copies a 16-byte vector from `this+0x7c` to output. |
| `0x00428be0` | `CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0` | Compares current/target vectors under flag mask `0x4` and calls `CUnit__SmoothEulerTowardTargetAndBuildMatrix`. |
| `0x00428c90` | `CUnitAIVFunc__CanDeployWhenField264Null_00428c90` | Returns `0` when `this+0x264` is non-null, otherwise tail-jumps to `CUnit__CanDeployNow`. |
| `0x0047a730` | `CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730` | Forwards arg to `0x00427b80`, then sets GillMHead `idle` animation token `0x0062ca48` through helper `0x004f4560`. |
| `0x0047a9c0` | `CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0` | Forwards non-`4` modes to `CUnit__SetEngagementModeAndMaybeClearTargetReader`. |

Read-back evidence:

- Dry-run: `updated=0 skipped=0 created=0 would_create=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Apply: `updated=24 skipped=0 created=24 would_create=0 renamed=0 would_rename=0 signature_updated=24 comment_only_updated=0 bad=0`
- Final dry-run: `updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Post exports: `24` metadata rows, `24` tag rows, `171` xref rows, `448` function-body instruction rows, `24` decompile rows, and `1600` post vtable-slot rows.
- Vtable sample improved from `1480` OK / `120` `NO_FUNCTION_AT_POINTER` to `1528` OK / `72` `NO_FUNCTION_AT_POINTER`; the selected Wave1086 targets account for `48` sampled slot occurrences now resolving to saved functions.
- Queue after Wave1086: `6355/6355 = 100.00%` static function-quality closure, with `0` commentless functions, `0` exact-`undefined` signatures, `0` `param_N` signatures, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Expanded static re-audit surface: `1472/1560 = 94.36%`. Wave911 focused remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-134022_post_wave1086_shared_unit_residual_vtable_continuation_verified`, `19` files, `175082375` bytes, `DiffCount=0`.

What this proves:

- The 24 target addresses now exist as saved Ghidra function entries.
- The saved names/signatures/comments/tags match the Wave1086 bounded static evidence.
- The sampled vtable rows now resolve those 48 former `NO_FUNCTION_AT_POINTER` slot occurrences to functions.
- The all-function quality queue remains closed at 100%.

What remains unproven:

- Exact source virtual names.
- Concrete owner layout semantics.
- Runtime behavior or gameplay outcomes.
- BEA patching behavior.
- Clean-room rebuild parity.

Probe token anchor: Wave1086; shared-unit-residual-vtable-continuation-wave1086; `0x00405dc0 SharedUnitVFunc__ReturnFloat005d858c_00405dc0`; `0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0`; `0x00403a90 SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90`; `0x00428be0 CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0`; `0x0047a730 CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730`; `1472/1560 = 94.36%`; `812/1408 = 57.67%`; `500/500 = 100.00%`; `6355/6355 = 100.00%`; `G:\GhidraBackups\BEA_20260602-134022_post_wave1086_shared_unit_residual_vtable_continuation_verified`; boundary recovery.
