# Ghidra Early Comment / Signature Tranche - 2026-05-10

## Scope

This note records a saved Ghidra comment/signature hardening tranche for eight early functions. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Saved name | Saved signature boundary |
| --- | --- | --- |
| `0x00401000` | `CGenericActiveReader__SetReader` | `void __thiscall ...(void * this, void * readerCell)` |
| `0x00401040` | `CMonitor__AddDeletionEvent` | `void __thiscall ...(void * this, void * readerCell)` |
| `0x004011b0` | `vector_constructor_iterator_nothrow` | `void __stdcall ...(void * base, int elemSize, int count, void * ctorFn)` |
| `0x004014c0` | `CFrontEndPage__ActiveNotification_NoOp` | `void __thiscall ...(void * this, int fromPage)` |
| `0x00403650` | `CMeshRenderer__CopyBasisAndRefreshTime` | `void __thiscall ...(void * this, void * srcBasis)` |
| `0x00403f40` | `CResourceDescriptor__ctor` | `void __fastcall ...(void * this)` |
| `0x00403f80` | `CResourceDescriptor__dtor` | `void __fastcall ...(void * this)` |
| `0x004048f0` | `CMesh__IsValidProfileIndex_1to10` | `int __cdecl ...(int profileIndex)` |

## Evidence Summary

- Headless dry/apply saved proof-boundary comments and signatures for all `8` targets with dry `updated=0 skipped=8 missing=0 bad=0` and apply `updated=8 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `8/8` targets.
- Final xref export produced `763` xref rows across the targets.
- Final instruction export produced `1052` instruction rows across the targets.
- The focused probe reports `8` return-evidence hits, `8` xref-evidence hits, `0` stale signature hits, and `0` comment overclaims.
- The refreshed whole-database queue reports `5868` functions, `529` commented functions, `5339` commentless functions, `2069` undefined signatures, and `2429` `param_N` signatures.

## Boundary

This tranche corrects two stale saved signature assumptions: `CFrontEndPage__ActiveNotification_NoOp` is modeled as a `thiscall`-style `ret 0x4` no-op with one `fromPage` stack argument, and `CMeshRenderer__CopyBasisAndRefreshTime` is modeled with one `srcBasis` stack argument while `this` is the destination.

The tranche does not prove exact source identities, concrete object layouts, tags, local-variable names, runtime frontend/resource/mesh behavior, BEA launch behavior, game patching, or rebuild parity. It also does not change the open BattleEngine `weapon_fire_breaks_stealth` gap.
