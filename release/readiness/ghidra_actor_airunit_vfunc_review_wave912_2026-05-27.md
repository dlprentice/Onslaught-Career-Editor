# Ghidra Wave912 actor/air-unit vfunc review (2026-05-27)

Status: saved Ghidra correction + read-back verified
Date: 2026-05-27
Branch: `main`
Tag: `actor-airunit-vfunc-review-wave912`

## Scope

Wave912 reviewed the top actor/air-unit/animal entries from the Wave911 focused correction queue.

Reviewed targets:

| Address | Saved name before Wave912 | Result |
| --- | --- | --- |
| `0x00402030` | `CActor__VFunc_18_SyncOldVectorAfterBaseCall` | **Renamed to `CActor__StickToGround`** |
| `0x00403a50` | `CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear` | Reviewed; no mutation |
| `0x00403730` | `CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport` | Reviewed; no mutation |
| `0x00403760` | `CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` | Reviewed; no mutation |
| `0x00403d30` | `CAnimal__Init` | Reviewed; no mutation |
| `0x00404010` | `CAnimal__dtor_base` | Reviewed; no mutation |

## Correction

`0x00402030` is source-backed as `CActor::StickToGround()`.

Stuart source:

```text
CActor::StickToGround()
  SUPERTYPE::StickToGround();
  mOldPos=mPos;
```

Retail read-back:

- calls base `CThing__StickToGround`
- copies dwords from `this+0x1c..0x28` into `this+0x8c..0x98`
- preserves `void __thiscall (...)(void * this)` signature shape

Saved state after Wave912:

```text
0x00402030 CActor__StickToGround
void __thiscall CActor__StickToGround(void * this)
```

## Mutation Discipline

Pre-mutation backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-100120_pre_wave912_actor_sticktoground_mutation
files=19
bytes=173247367
```

Post-mutation backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-100357_post_wave912_actor_sticktoground_verified
files=19
bytes=173247367
```

Dry/apply/final-dry:

```text
dry: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=0 comment_only_updated=1 missing=0 bad=0
apply: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0
final dry: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0
```

## Read-back

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/metadata.tsv
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/tags.tsv
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/instructions.tsv
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/decompile/
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/post_metadata.tsv
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/post_tags.tsv
subagents/ghidra-static-reaudit/wave912-actor-airunit-vfunc-review/post_decompile/
```

Post-mutation queue:

```text
npm run test:ghidra-static-reaudit-queue
Status: PASS
Total functions: 6113
Commentless functions: 0
Undefined signatures: 0
Param signatures: 0
```

## Non-claims

This corrects one saved Ghidra name/comment/tag set. It does not prove runtime movement behavior, concrete `CActor`/`FVector` layouts, BEA patch behavior, or rebuild parity.

## Next

Continue Wave913 with another coherent slice from the Wave911 focused queue. Good candidates are remaining actor/air-unit rows or the mesh/collision rows beginning at `0x00479020`.
