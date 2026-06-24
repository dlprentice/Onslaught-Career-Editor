# Ghidra Object Lifecycle Destructor Review Wave1022

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `object-lifecycle-dtor-review-wave1022`

Wave1022 re-read an adjacent object-lifecycle destructor strip from `0x004bfe10 CRocket__dtor_base` through `0x004c0000 CEscapePod__dtor_base` and saved a narrow owner-prefix normalization for the SpawnerThng destructor pair.

Saved Ghidra mutation:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004bfd80 CSpawnerThng__scalar_deleting_dtor` | Renamed from stale `CSpawnerThing__scalar_deleting_dtor`; saved comment/tags; signature remains `void * __thiscall ...(void * this, byte flags)`. | DATA xref `0x005dd170` is slot 1 of vtable `0x005dd16c`; slots 2 and 9 in the same table are `CSpawnerThng__Shutdown` and `CSpawnerThng__Init`. Body calls `CSpawnerThng__dtor_base`, conditionally frees `this` when `flags&1`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfed0 CSpawnerThng__dtor_base` | Renamed from stale `CSpawnerThing__dtor_base`; saved comment/tags; signature remains `void __fastcall ...(void * this)`. | Called by the scalar-deleting wrapper at `0x004bfd83`. Body removes the `+0x7c` owner/list link through `CSPtrSet__Remove` when present, then delegates to `CComplexThing__dtor_base`. |

Read-only destructor rows re-confirmed:

| Address | Saved name |
| --- | --- |
| `0x004bfe10` | `CRocket__dtor_base` |
| `0x004bfe70` | `CWaypoint__dtor_base` |
| `0x004bff30` | `CComplexThing__dtor_base_Thunk_004bff30` |
| `0x004bff40` | `CSphereTrigger__dtor_base` |
| `0x004bffa0` | `CWingmanStart__dtor_base` |
| `0x004c0000` | `CEscapePod__dtor_base` |

Read-back evidence:

- `ApplyObjectLifecycleDtorWave1022.java dry`: `updated=0 skipped=2 renamed=0 would_rename=2 comment_only_updated=0 tags_added=9 missing=0 bad=0`
- `ApplyObjectLifecycleDtorWave1022.java apply`: `updated=2 skipped=0 renamed=2 would_rename=0 comment_only_updated=0 tags_added=9 missing=0 bad=0`
- `ApplyObjectLifecycleDtorWave1022.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Pre/post primary exports verified `7` metadata rows, `7` tag rows, `11` xref rows, `152` body-instruction rows, and `7` decompile rows.
- Wrapper exports verified `7` metadata rows, `7` tag rows, `10` xref rows, `77` body-instruction rows, and `7` decompile rows.
- Context exports verified `16` metadata rows, `76` xref rows, `809` body-instruction rows, and `16` decompile rows.
- Vtable exports verified `160` rows across `0x005dd458`, `0x005dd2f0`, `0x005dd16c`, `0x005dce64`, `0x005dcb58`, `0x005dc830`, `0x005dcfe8`, `0x005dccdc`, `0x005dc9c8`, and `0x005def1c`.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress advances to `539/1408 = 38.28%`; expanded static surface progress advances to `768/1493 = 51.44%`; Wave911 top-500 risk-ranked coverage advances to `467/500 = 93.40%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The two saved SpawnerThng destructor rows now use the same owner prefix as the rest of the vtable-backed SpawnerThng family.
- The selected adjacent destructor strip still reads back as static object-lifecycle destructor/wrapper evidence in the saved Ghidra database.
- The live static function-quality queue remains closed at `6238/6238 = 100.00%`.

What remains unproven:

- Runtime spawner, rocket, waypoint, trigger, wingman-start, or escape-pod cleanup behavior.
- Exact source-body identity.
- Concrete object layouts beyond observed offsets and vtable/call evidence.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bfd80 CSpawnerThng__scalar_deleting_dtor; 0x004bfed0 CSpawnerThng__dtor_base; 0x004bfe10 CRocket__dtor_base; 0x004bfe70 CWaypoint__dtor_base; 0x004bff40 CSphereTrigger__dtor_base; 0x004c0000 CEscapePod__dtor_base; 539/1408 = 38.28%; 768/1493 = 51.44%; 467/500 = 93.40%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified; renamed=2.
