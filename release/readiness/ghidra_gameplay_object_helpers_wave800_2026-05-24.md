# Ghidra Gameplay Object Helpers Wave800 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `gameplay-object-helpers-wave800`

Wave800 gameplay object helpers saved Ghidra comments/tags/signatures for four raw commentless helper rows and corrected one over-specific helper name after serialized headless dry/apply/read-back. The pass made one rename, three signature corrections, one comment-only hardening, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00445010 CMCBuggy__GetTargetValueOrFallback` | `float __thiscall CMCBuggy__GetTargetValueOrFallback(void * this, int target_id)` | Called by `CDestructableSegmentsMotionController__ApplyRumbleTransform` at `0x00494cfa`; `RET 0x4` proves one explicit stack argument after `ECX`. The body reads a target table at `this+4`, returns candidate field `+0x44`, or falls back to global float `0x005d856c`. |
| `0x00445070 CDiveBomber__SelectTarget` | `void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)` | Called by `CCannon__SelectTarget` at `0x004fd4e1`; caller/decompile evidence shows a stack output pointer, replacing the older no-argument return-pointer signature. |
| `0x00449560 Vec3__AssignFromValuePointersAndReturnThis` | `void * __thiscall Vec3__AssignFromValuePointersAndReturnThis(void * this, float * x_value, float * y_value, float * z_value)` | Renamed from the over-specific `CMine__AssignVec3AndReturnThis`; instruction evidence copies three dereferenced 4-byte values into destination offsets `+0/+4/+8`, returns `this`, and ends with `RET 0xc`. |
| `0x00449d40 OID__FreeObject_Callback` | `void __cdecl OID__FreeObject_Callback(void * ptr)` | Retained existing OID cleanup callback name; `661` wave xrefs include `657` direct xrefs to this row. Instruction evidence forwards the stack pointer argument to `CDXMemoryManager__Free` using memory-manager/context `0x009c3df0`. |

Read-back evidence:

- `ApplyGameplayObjectHelpersWave800.java dry`: `updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=3 comment_only_updated=1 missing=0 bad=0`
- `ApplyGameplayObjectHelpersWave800.java apply`: `updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=3 comment_only_updated=1 missing=0 bad=0`
- `ApplyGameplayObjectHelpersWave800.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `4` metadata rows, `4` tag rows, `661` xref rows, `148` instruction rows, and `4` decompile rows.
- Queue after Wave800: `6098` total functions, `5556` commented, `542` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5556/6098 = 91.11%`, strict clean-signature proxy `5556/6098 = 91.11%`.
- Probe anchors: `0 exact-undefined signatures`; `0 param_N signatures`.
- Next raw commentless row: `0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified`, `19` files, `171314055` bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved names, signatures, comments, and tags match the Wave800 read-back evidence.
- The observed helper behavior is static retail Ghidra evidence tied to xrefs, instruction exports, decompile exports, and queue telemetry.

What remains unproven:

- Exact source-body identity.
- Concrete class/vector/object layouts beyond the stated offsets.
- Runtime targeting, rumble, mine, cleanup, or allocator behavior.
- BEA patching behavior.
- Rebuild parity.
