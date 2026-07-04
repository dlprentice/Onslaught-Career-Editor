# debris.cpp

> Static retail evidence for `CDebris` helper functions from `BEA.exe`.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x00441370 CDebris__GetClassId as part of the generic/shared vfunc-thunk tail current-risk review. The row remains a bounded class/OID id helper returning 0x1f, with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: [maintainer-local-ghidra-backup-root]\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Exact source enum identity, runtime debris behavior, exact layout, and rebuild parity remain separate proof.


## Source Context

The checked Stuart source snapshot contains `CDebris` callsite hints, including `CDebris::ShuffleDebris(...)` calls and a commented spawn example, but not a full `CDebris` implementation body. Names below are therefore saved Ghidra behavior labels, not exact source-body closure.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004411a0 | CDebris__Init | SAVED | Initializes render-object/resource context, calls base init, registers debris console variables, and links into the global debris list. |
| 0x00441320 | CDebris__dtor_base | SAVED | Corrects the stale constructor-like label; unlinks from the global debris list before base destruction. |
| 0x00441360 | CDebris__GetClassName | SAVED | Recovered class-name boundary returning `CDebris`. |
| 0x00441370 | CDebris__GetClassId | SAVED | Recovered class/OID id boundary returning `0x1f`. |
| 0x00441380 | CDebris__scalar_deleting_dtor | SAVED | Scalar-deleting destructor wrapper that calls `CDebris__dtor_base` and conditionally frees the object. |
| 0x004413a0 | CDebris__Render | SAVED | Recovered render boundary with visibility/render-object checks and distance-fade alpha context. |
| 0x00441420 | CDebris__RenderImposter | SAVED | Recovered imposter-render boundary with distance-fade alpha context. |

## Wave 347 Signature / Boundary Read-Back

Wave 347 saved and read back the current `CDebris` names, signatures, comments, and tags after metadata, decompile, xref, instruction, tag, vtable, and class-string review:

- `CDebris__Init`: `void __thiscall CDebris__Init(void * this, void * init)`
- `CDebris__dtor_base`: `void __fastcall CDebris__dtor_base(void * this)`
- `CDebris__GetClassName`: `char * __cdecl CDebris__GetClassName(void)`
- `CDebris__GetClassId`: `int __cdecl CDebris__GetClassId(void)`
- `CDebris__scalar_deleting_dtor`: `void * __thiscall CDebris__scalar_deleting_dtor(void * this, int flags)`
- `CDebris__Render`: `void __thiscall CDebris__Render(void * this, int renderFlags)`
- `CDebris__RenderImposter`: `void __fastcall CDebris__RenderImposter(void * this)`

The final read-back verified `7` metadata rows, `7` decompile exports, `7` xref rows, `847` instruction rows, `7` tag rows, and `4` vtable evidence hits. Vtable context for `0x005daf10` now includes the scalar-deleting destructor, class-name/class-id helpers, and `CDebris__Init`; other unresolved slots were left untouched.

## Wave1090 Lifecycle/Render Re-Audit

Wave1090 (`cdebris-lifecycle-render-review-wave1090`) re-read the seven saved `CDebris` lifecycle/render rows with no mutation. Fresh primary exports verified `7` metadata rows, `7` tag rows, `7` xref rows, `202` function-body instruction rows, and `7` decompile rows; context exports verified `11` metadata rows, `11` tag rows, `1263` xref rows, `460` instruction rows, and `11` decompile rows. Vtable `0x005daf14` exported `48` slots, all `OK`.

The reviewed evidence preserves the prior names/signatures/comments/tags around `grs_tuft1.MSH`, the global debris list `DAT_0066eb78`, render alpha state `DAT_0063012c`, render-object dispatch, class string `0x006283e0`, and class/OID id `0x1f`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Post-100 re-audit progress after this read-only pass is `1534/1560 = 98.33%`; Wave911 focused progress remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`; function-quality closure remains `6410/6410 = 100.00%`. Probe token anchor: Wave1090; cdebris-lifecycle-render-review-wave1090; 0x004411a0 CDebris__Init; 0x00441320 CDebris__dtor_base; 0x004413a0 CDebris__Render; 0x00441420 CDebris__RenderImposter; 0x005daf14; grs_tuft1.MSH; DAT_0066eb78; DAT_0063012c; no mutation.

## Behavior Summary

### CDebris__Init (0x004411a0)

- Builds a resource descriptor for the checked tuft mesh string context.
- Creates/stores a render object at the instance render-object slot.
- Calls the complex-thing base init path and then a virtual setup hook.
- Registers `cg_debrisarea`, `cg_debrisfadestart`, and `cg_debrisfadeend`.
- Links the object into the global debris list.

### CDebris__dtor_base (0x00441320)

- Installs the checked debris/base vtable context during teardown.
- Walks the global debris list and unlinks the current instance.
- Delegates to the complex-thing base destructor path.

### CDebris__Render / CDebris__RenderImposter

- Check visibility/render-object context before dispatch.
- Compute fade alpha from distance/fade globals.
- Temporarily update render alpha state, call the render-object vfunc, and restore the prior alpha value.

## Claim Boundary

This page records saved static Ghidra evidence only. Runtime debris rendering, exact source identity, concrete `CDebris` layout recovery, local/type recovery, BEA launch, game patching, and rebuild parity remain unproven.
