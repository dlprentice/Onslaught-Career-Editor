# Ghidra CUnit VFunc08 Boundary Wave1075 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `cunit-vfunc08-boundary-wave1075`

Wave1075 recovered and saved one previously missing Ghidra function boundary at `0x004dfa40 CUnit__VFunc08_InitAndAddToWorld`. The pass created the function object, saved the bounded `void __thiscall CUnit__VFunc08_InitAndAddToWorld(void * this, void * init)` signature, saved comments/tags, and made no executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Evidence summary:

| Address | Evidence |
| --- | --- |
| `0x004dfa40 CUnit__VFunc08_InitAndAddToWorld` | CUnit-family vtable table `0x005dfd40` slot 8 at `0x005dfd60` DATA-xrefs the previously missing function start. |
| `0x004dfa47` | Fresh pre-state listed this as `INSTRUCTION_NO_FUNCTION`, but it has no direct xref and sits inside the recovered `0x004dfa40` body. |
| `0x004dfa40` body | Body consumes ECX as `this` and the stack `init` pointer, sets observed init fields, clears `this+0x250`, calls `CUnit__Init`, dispatches vtable offset `+0x48`, clears `this+0x13c`, and calls `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`. |
| `0x004dfa9a` / `0x004dfaa0` boundary | Post read-back keeps a tight body through `0x004dfa9a RET 0x4` and does not absorb the next existing function at `0x004dfaa0`. |

Read-back evidence:

- Pre exports: `1` diagnose row, `1` missing metadata row, `1` DATA xref row, `161` instruction-window rows, and `1` missing decompile row.
- Context exports: `6` diagnose rows, `6` metadata rows, `24` xref rows, `438` instruction rows, and `6` decompile index rows, plus two 64-row pointer-table windows at `0x005dfd40` and `0x00622680`.
- Apply dry: `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: `1` metadata row, `1` tag row, `1` xref row, `23` function-body instruction rows, `1` decompile row, and `64` post vtable-slot rows.
- Queue closure is now `6248/6248 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1359/1560 = 87.12%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The loaded Ghidra project now has a saved function object at `0x004dfa40`.
- The saved name, signature, comment, and tags read back for `CUnit__VFunc08_InitAndAddToWorld`.
- The function is tied to CUnit-family vtable table `0x005dfd40` slot 8 through DATA xref `0x005dfd60`.
- The recovered function body is bounded around CUnit init/add-to-world static evidence and does not absorb the next function at `0x004dfaa0`.

What remains separate proof:

- Exact source virtual name.
- Concrete CUnit/init/world-layout semantics.
- Runtime init/add-to-world/static-shadow behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with read-only review first from the remaining expanded static re-audit surface.

Probe token anchor: Wave1075; cunit-vfunc08-boundary-wave1075; 0x004dfa40 CUnit__VFunc08_InitAndAddToWorld; 0x005dfd40; 0x005dfd60; 0x004dfa47; 0x004dfa9a; 0x004dfaa0; CUnit__Init; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; 812/1408 = 57.67%; 1359/1560 = 87.12%; 500/500 = 100.00%; 6248/6248 = 100.00%; G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified; boundary recovery.
