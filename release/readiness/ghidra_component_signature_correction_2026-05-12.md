# Ghidra Component Signature Correction - 2026-05-12

Status: public-safe static reverse-engineering evidence.

## Scope

Wave 324 revisited the Component-family cluster after fresh metadata, decompile, xref, instruction, vtable RTTI, and tag read-back. This wave saved ten Ghidra signatures/comments/tags and corrected four stale destructor-owner labels. It did not create new function boundaries.

A fresh out-of-repo backup of the live Ghidra project was made before this accounting pass. Backup verification reported `19` files, `151489415` bytes, and `DiffCount=0`.

## Saved Corrections

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x00427b80` | `void __thiscall CComponent__VFunc_09_00427b80(void * this, void * init)` | Kept the conservative virtual-slot name and removed the stale phantom integer parameter. |
| `0x00427cd0` | `void __fastcall CComponent__CreateSubComponent1(void * this)` | Creates the small `this+0x70` component context. |
| `0x00427d50` | `void __fastcall CComponent__CreateSubComponent2(void * this)` | Creates the `this+0x208` component context and uses the `CComponentGuide` vtable. |
| `0x00427dd0` | `void __thiscall CComponent__CreateWeaponComponent(void * this, void * initOrContext)` | Factory over Fenrir bomb launcher, Fenrir main gun, Carrier health pad, and fallback paths. |
| `0x00427f90` | `void * __thiscall CComponentBomberAI__scalar_deleting_dtor(void * this, byte flags)` | Corrects stale generic vfunc label to scalar-deleting destructor wrapper. |
| `0x00427fb0` | `void __fastcall CComponentBomberAI__dtor_base(void * this)` | Corrects stale constructor-like label to destructor-base cleanup. |
| `0x00428050` | `void * __thiscall CFenrirMainGunAI__scalar_deleting_dtor(void * this, byte flags)` | Corrects stale generic vfunc label to scalar-deleting destructor wrapper. |
| `0x00428070` | `void __fastcall CFenrirMainGunAI__dtor_base(void * this)` | Corrects stale constructor-like label to destructor-base cleanup. |
| `0x00428110` | `void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)` | Activation/pickup helper context remains static evidence only. |
| `0x00428500` | `void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)` | Cached component transform helper context remains static evidence only. |

All ten targets now carry saved Ghidra function tags: `component-system`, `component-wave324`, `signature-hardened`, and `static-reaudit`. The four owner-corrected destructor targets also carry `destructor` and `owner-corrected`.

## Vtable RTTI Context

| Vtable address | Read-back type name |
| --- | --- |
| `0x005d96b4` | `CComponentBomberAI` |
| `0x005d9680` | `CFenrirMainGunAI` |
| `0x005d8e08` | `CRepairPadAI` |
| `0x005d9654` | `CComponentGuide` |
| `0x005d8d1c` | `CUnitAI` |

## Validation

| Check | Result |
| --- | --- |
| `ApplyComponentSignatureCorrection.java dry` | `updated=0 skipped=10 renamed=0 missing=0 bad=0`; `REPORT: Save succeeded` |
| `ApplyComponentSignatureCorrection.java apply` | `updated=10 skipped=0 renamed=4 missing=0 bad=0`; `REPORT: Save succeeded` |
| Metadata read-back | `10/10` targets |
| Decompile read-back | `10/10` targets |
| Xref read-back | `18` rows |
| Instruction read-back | `810` rows, `0` missing targets |
| Tag read-back | `10/10` targets |
| Vtable RTTI read-back | Confirms `CComponentBomberAI`, `CFenrirMainGunAI`, `CRepairPadAI`, `CComponentGuide`, and `CUnitAI` context |
| Quality queue | `5884` total functions, `761` commented, `5123` commentless, `1994` undefined signatures, `2299` `param_N` signatures |
| Focused probe | `PASS`, schema `ghidra-component-signature-correction.v1` |

## What This Proves

- The saved Ghidra project now has hardened signatures/comments/tags for ten Component-family targets.
- Four stale lifecycle labels were corrected to `CComponentBomberAI` and `CFenrirMainGunAI` destructor wrappers/base destructors.
- The current Component weapon factory vtable evidence distinguishes `CComponentBomberAI`, `CFenrirMainGunAI`, `CRepairPadAI`, and fallback paths more precisely than the older three-function note.

## What This Does Not Prove

- Runtime Component, AI activation, pickup, weapon, or transform behavior.
- Exact `Component.cpp` source-body identity, because matching source bodies are not present in the available Stuart source snapshot.
- Concrete object layouts, local variable names, structure types, exhaustive tags, or rebuild parity.
- Any mutation or execution of `BEA.exe`.

## Public/Private Boundary

This note includes only repo-relative paths, public addresses, saved names/signatures/tags, aggregate counts, and public-safe summaries. Raw decompile exports, instruction dumps, private project backups, and generated probe JSON remain outside public release scope.
