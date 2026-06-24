# Ghidra Animal Lifecycle Boundary Review Wave946

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `animal-lifecycle-boundary-wave946`

Wave946 re-reviewed the CAnimal lifecycle/vtable cluster and recovered the remaining real CAnimal vtable function boundaries through the 69-slot table span. The pass created 23 function objects, saved names, signatures, comments, and tags, made no executable-byte changes, did not launch BEA, and left the non-vtable data after slot 68 untouched.

Representative saved boundaries:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0044c140 CAnimal__HandleEvent3000Dispatch` | `void __thiscall CAnimal__HandleEvent3000Dispatch(void * this, void * event)` | CAnimal vtable slot 0; event id `0xbb8`/3000 branch dispatches vtable byte offset `+0x108`, otherwise forwards to `CComplexThing__HandleEvent`. |
| `0x00401440 CThing__GetRenderRadiusFromRenderThing` | `float __thiscall CThing__GetRenderRadiusFromRenderThing(void * this)` | CAnimal vtable slot 16; `this+0x30` render object, vtable byte offset `+0x18`, fallback float constant `0x005d856c`; source-parity with `CThing::GetRenderRadius()`. |
| `0x00401460 CThing__MakeVisible` / `0x00401470 CThing__MakeInvisible` | `void __thiscall ...(void * this)` | CAnimal vtable slots 32/33; clear/set `this+0x2c` bit `0x10`, matching `CThing::MakeVisible()` / `CThing::MakeInvisible()`. |
| `0x00401490 CThing__Damage_NoOp` | `void __thiscall CThing__Damage_NoOp(void * this, float amount, void * byThing, int damageShields, int meshPartNo)` | CAnimal vtable slot 40; single `RET 0x10`, matching an empty four-argument `CThing::Damage`-like virtual at ABI level. |
| `0x004014e0 CComplexThing__IsObjectiveFlagSet` | `int __thiscall CComplexThing__IsObjectiveFlagSet(void * this)` | CAnimal vtable slot 26; masks `this+0x2c` bit `0x20`, source-parity with `CComplexThing::IsObjective()`. |
| `0x00404120 CAnimal__CopyVector7CToOut` / `0x00404150 CAnimal__SetVector7CFromInput` / `0x00404170 CAnimal__AddVectorTo7C` | vector getter/setter/accumulator signatures | CAnimal vtable slots 27/67/68; read, write, and add the vector-like field at `this+0x7c`. |
| `0x004041d0 CAnimal__CopyMatrix9CToOut` | `void __thiscall CAnimal__CopyMatrix9CToOut(void * this, void * outMatrix)` | CAnimal vtable slot 31; copies `0x30` bytes from `this+0x9c` to the caller output buffer. |
| `0x004045d0 CAnimal__RenderViaCThingRender` | `void __thiscall CAnimal__RenderViaCThingRender(void * this, int renderFlags)` | CAnimal vtable slot 36; forwards one render-flags argument to `CThing__Render` and returns with `RET 0x4`. |
| `0x004f3d30 CThing__DrawDebugStuff3d` | `void __thiscall CThing__DrawDebugStuff3d(void * this)` | CAnimal vtable slot 52; copies identity/position data, calls through vtable byte offset `+0x40` for a radius-like float, then calls `CThing__RenderDebugVolumeOverlay`; source-parity with `CThing::DrawDebugStuff3d()`. |

Read-back evidence:

- Composer 2.5 consult lane was attempted twice for Wave946 but produced no output in the headless environment; Codex root proceeded from local Ghidra/source evidence only.
- `ApplyAnimalLifecycleBoundaryWave946.java` initial dry/apply/final dry created the first 7 CAnimal-table boundaries, then an expanded dry/apply/final dry created 16 additional boundaries after the 128-slot vtable scan revealed the remaining real table entries.
- Expanded dry: `updated=0 skipped=7 created=0 would_create=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Expanded apply: `updated=16 skipped=7 created=16 would_create=0 renamed=0 would_rename=0 signature_updated=16 comment_only_updated=0 missing=0 bad=0`.
- Expanded final dry: `updated=0 skipped=23 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 26 metadata rows, 26 tag rows, 1005 xref rows, 389 instruction rows, 26 decompile rows, and 69 post CAnimal vtable rows.
- Queue after Wave946: `6139` total functions, `6139` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`; export-contract function-quality closure remains `6139/6139 = 100.00%`.
- Wave911 focused re-audit progress after Wave946: `232/1408 = 16.48%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-062816_post_wave946_animal_lifecycle_boundary_review_verified`, 19 files, 173476743 bytes, `DiffCount=0`.

What this proves:

- The 23 recovered function objects exist in the saved Ghidra project at the intended entries.
- The saved names, signatures, comments, and tags were read back after apply.
- The real CAnimal vtable span through slot 68 has no `NO_FUNCTION_AT_POINTER` rows after read-back.

What remains unproven:

- Exact source virtual names for every recovered slot.
- Exact CAnimal/CThing/CComplexThing field names and layouts.
- Runtime animal, render, objective, physics, or debug-render behavior.
- BEA patching behavior.
- Rebuild parity.
