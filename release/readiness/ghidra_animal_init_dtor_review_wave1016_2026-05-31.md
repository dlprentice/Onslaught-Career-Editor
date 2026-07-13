# Ghidra Animal Init Dtor Review Wave1016

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: PASS read-only static read-back evidence
Date: 2026-05-31
Scope: `animal-init-dtor-review-wave1016`

Wave1016 re-read the CAnimal init/destructor rows after Wave1015. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x00403d30 CAnimal__Init` | DATA/vtable slot 9 xref `0x005d86bc`; copies init transform/vector state, constructs a stack `CResourceDescriptor`, reads init type at `init+0x3bc`, uses `bird.msh` for type 1, creates a render object through `PCRTID__CreateObject`, delegates to `CComplexThing__Init`, links `DAT_00660130`/`DAT_00660134`, and schedules event `3000` through `CEventManager__AddEvent_AtTime` when active. |
| `0x00404010 CAnimal__dtor_base` | Called by `CAnimal__scalar_deleting_dtor`; resets CAnimal vtables, walks/clears animal-list references through `DAT_00660130`/`DAT_00660134`, unlinks this node when present, then jumps to `CComplexThing__dtor_base`. |
| `0x004041f0 CAnimal__scalar_deleting_dtor` | DATA/vtable slot 1 xref `0x005d869c`; calls `CAnimal__dtor_base`, frees through `CDXMemoryManager__Free` when `flags&1`, returns `this`, and `RET 0x4` confirms the one stack `flags` argument. |

Read-back evidence:

- Target exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `195` body-instruction rows, and `3` decompile rows.
- Context exports verified `32` metadata rows, `637` xref rows, `1292` body-instruction rows, and `32` decompile rows.
- CAnimal vtable export verified `69` slots from `0x005d8698`; slot 1 points to `0x004041f0 CAnimal__scalar_deleting_dtor`, slot 7 to `0x004040f0 CAnimal__GetClassNameString`, slot 8 to `0x00404100 CAnimal__GetTypeId1D`, slot 9 to `0x00403d30 CAnimal__Init`, slot 27 to `0x00404120 CAnimal__CopyVector7CToOut`, slot 30 to `0x004041a0 CAnimal__CopyVector8CToOut`, slot 31 to `0x004041d0 CAnimal__CopyMatrix9CToOut`, slot 36 to `0x004045d0 CAnimal__RenderViaCThingRender`, slot 38 to `0x00404110 CAnimal__SetThingTypeMask80000001`, slot 67 to `0x00404150 CAnimal__SetVector7CFromInput`, and slot 68 to `0x00404170 CAnimal__AddVectorTo7C`.
- Data/string evidence verified `14` xref rows, `3` scalar-reference rows, and direct strings `0x00622d48 = bird.msh`, `0x00622d1c = Warning! Unknown animal type %d generated!\x0a`, and `0x00622d70 = CAnimal`.
- Context rows covered CThing/CComplexThing lifecycle, `CAnimal__HandleEvent3000Dispatch`, CAnimal vector/matrix/render helpers, `CResourceDescriptor__ctor`, `CResourceDescriptor__dtor`, `CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk`, `CActor__Init`, `CActor__dtor_base`, `CEventManager__AddEvent_AtTime`, `PCRTID__CreateObject`, and `CConsole__AddString`.
- Export-contract function-quality closure remains `6238/6238 = 100.00%`.
- Wave911 focused re-audit progress advances to `513/1408 = 36.43%`.
- Expanded static surface progress advances to `739/1493 = 49.50%`.
- Wave911 top-500 risk-ranked coverage advances to `439/500 = 87.80%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1016; animal-init-dtor-review-wave1016; 0x00403d30 CAnimal__Init; 0x00404010 CAnimal__dtor_base; 0x004041f0 CAnimal__scalar_deleting_dtor; 0x005d8698; 0x00622d48 bird.msh; 0x00622d1c Warning! Unknown animal type; 0x00622d70 CAnimal; 513/1408 = 36.43%; 739/1493 = 49.50%; 439/500 = 87.80%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified; no mutation.

Boundary note: this proves static read-back coherence for the selected CAnimal init/destructor rows and immediate vtable/data/context evidence only. Exact source virtual names, concrete `CAnimal`/`CAnimalInitThing`/resource-descriptor/list layouts, runtime animal behavior, runtime event scheduling, BEA patching, and rebuild parity remain separate proof.
