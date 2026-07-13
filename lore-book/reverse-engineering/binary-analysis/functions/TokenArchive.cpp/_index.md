# TokenArchive.cpp - Function Analysis

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0048de00` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1190 current-risk update: Wave1190 (`wave1190-particle-descriptor-token-archive-current-risk-review`) accounts for `11 particle descriptor token-writer/TokenArchive current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. It updated `CPDSimpleSprite__WriteTokenFields`, `CPDEmitter__WriteTokenFields`, `CPDSelector__WriteTokenFields`, `CPDColourRange__WriteTokenFields`, `CPDShape__WriteTokenFields`, `CPDTrail__WriteTokenFields`, `CPDFunction__WriteTokenFields`, `CPDMesh__WriteTokenFields`, `CPDFoR__WriteTokenFields`, `CPDPMesh__WriteTokenFields`, and `CTokenArchive__BindIndexedFieldPointer`; xrefs include `CParticleDescriptor__Load`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0`, then final dry updated=0 skipped=11. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `819/1179 = 69.47%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `25 xref rows`, `733 instruction rows`, and `11 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact descriptor/TokenArchive layouts, exact source virtual/source-body identity, runtime particle loading/parsing/rendering/linking behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1190; wave1190-particle-descriptor-token-archive-current-risk-review; 819/1179 = 69.47%; 11 particle descriptor token-writer/TokenArchive current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=11 skipped=0; comment_only_updated=11; tags_added=123; final dry updated=0 skipped=11; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__WriteTokenFields; CPDEmitter__WriteTokenFields; CPDSelector__WriteTokenFields; CPDColourRange__WriteTokenFields; CPDShape__WriteTokenFields; CPDTrail__WriteTokenFields; CPDFunction__WriteTokenFields; CPDMesh__WriteTokenFields; CPDFoR__WriteTokenFields; CPDPMesh__WriteTokenFields; CTokenArchive__BindIndexedFieldPointer; CParticleDescriptor__Load; 0 / 0 / 0; 6411/6411 = 100.00%; 25 xref rows; 733 instruction rows; 11 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.


**Source file:** `[maintainer-local-source-export-root]\TokenArchive.cpp`
**Analysis date:** December 2025
**Functions tracked:** 9, including the Wave420 line-reader helper

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

TokenArchive is a serialization system for reading and writing tokenized data archives. In BEA, this is specifically used for **particle system configuration files** (`.ptc` or similar). The system uses a token-based format where each data field is identified by a string token name followed by its value.

The format appears to be: `TokenName Value` pairs, parsed line-by-line or whitespace-separated.

## Wave 420 Static Re-Audit Note (2026-05-14)

Wave420 hardened `CTokenArchive__ReadLine` at `0x0048de00` to:

```text
void __stdcall CTokenArchive__ReadLine(char * line_buffer, int max_len)
```

The helper calls `DXMemBuffer__ReadLine`, then strips one trailing LF byte when present. `CTokenArchive__ReadNextToken` calls it with scratch line buffer `0x0083e288` and max length `999` before scanning the token/value pair. This is static Ghidra read-back evidence only; parser runtime coverage remains unproven.

## Wave 518 Static Re-Audit Note (2026-05-17)

Wave518 hardened 9 TokenArchive parser, reference-fixup, and token writer functions in saved Ghidra:

```text
char * __cdecl CTokenArchive__GetTokenName(int token_id)
int __thiscall CTokenArchive__ReadNextToken(void * this, int * out_token_id, int * out_int_or_ref_index, float * out_float, char * out_string)
void __thiscall CTokenArchive__RegisterReferenceFixup(void * this, int ref_value, int slot_index, void * fixup_record)
void __thiscall CTokenArchive__ResolveReferences(void * this, void * list_head_ptr)
void __stdcall CTokenArchive__WriteInt(int token_id, int value)
void __stdcall CTokenArchive__WriteFloat(int token_id, float value)
void __stdcall CTokenArchive__WriteString(int token_id, char * value)
void __stdcall CTokenArchive__WritePointer(int token_id, void * named_object)
void __stdcall CTokenArchive__WriteFloatPointer(int token_id, void * value_ref_record)
```

Read-back evidence: `9` metadata rows, `9` tag rows, `178` xref rows, `2565` instruction rows, `9` decompile exports, focused probe PASS, queue refresh PASS, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260517-215239_post_wave518_tokenarchive_verified`. This is static Ghidra evidence only; runtime particle parsing, runtime token writing, exact TokenArchive layout, final token enum names, and rebuild parity remain open.

## Token Types

The system supports 124 (0x7C) different token types, primarily for particle system parameters:

| Range | Category | Examples |
|-------|----------|----------|
| 0-5 | File header | `ParticleSystemEd_File`, `File_Version`, `Num_Particle_Descriptors` |
| 6-27 | Basic particle params | `Radius`, `Gravity`, `Bounce`, `Texture`, `Blend_Mode` |
| 28-44 | Velocity/emission | `Initial_Velocity_X/Y/Z`, `Emit_Per_Turn`, `Particle_Descriptor` |
| 45-48 | Probability | `Probability_0` through `Probability_3` |
| 49-57 | Color | `Start_Red/Green/Blue`, `End_Red/Green/Blue`, `Transition_*` |
| 58-67 | Shape/geometry | `Ring_Axis`, `Hemisphere`, `Num_Particles`, `Hollow` |
| 68-81 | Trail/ribbon | `Width`, `Num_Points`, `Wiggle_Factor`, `Disperse_Rate` |
| 82-95 | Animation/function | `Yaw_Function`, `Pitch_Function`, `Param_A/B/C/D` |
| 96-111 | Cylinder params | `Cylinder_NumPtsAxial`, `Cylinder_Radius`, `Cylinder_Length` |
| 112-123 | Sphere params | `Sphere_NumPtsAx`, `Sphere_Latitude_Start/End`, `Sphere_Longitude_*` |

## Functions

### CTokenArchive__GetTokenName
| Property | Value |
|----------|-------|
| Address | `0x004f52b0` |
| Returns | `char*` (token name string) |
| Parameters | `int token_id` |
| Calling Convention | `__cdecl` |
| Saved signature | `char * __cdecl CTokenArchive__GetTokenName(int token_id)` |

Converts a token ID (0-123) to its string name. Returns `"**Unknown Token**"` for invalid IDs.

**Token examples:**
- 0 = `"ParticleSystemEd_File  C 2000 Lo"` (file header)
- 1 = `"File_Version"`
- 6 = `"Radius"`
- 8 = `"Gravity"`
- 0x31 = `"Start_Red"`

---

### CTokenArchive__ReadNextToken
| Property | Value |
|----------|-------|
| Address | `0x004f57b0` |
| Returns | `int` (1 = success, 0 = failure) |
| Parameters | `int* out_token_id, int* out_int_or_ref_index, float* out_float, char* out_string` |
| Calling Convention | `__thiscall` (ECX = this) |
| Saved signature | `int __thiscall CTokenArchive__ReadNextToken(void * this, int * out_token_id, int * out_int_or_ref_index, float * out_float, char * out_string)` |
| Line refs | 0x138 (312), 0x16a (362) |

Main token parsing function. Reads from internal buffer, parses token name and value(s).

**Behavior by token type:**
- **Cases 0, 5**: Header tokens - no value parsing needed
- **Cases 1, 7, 0x13, etc.**: Float tokens - parse single float into `outFloat2`
- **Cases 2, 3, 8, 9, etc.**: Integer tokens - parse into `outFloat`
- **Cases 4, 0xb, 0x65**: String tokens - copy string to `outString`
- **Cases 6, 0x18, 0x1a, etc.**: Float + string reference - allocates memory for string storage
- **Cases 0xc, 0x10, 0x1c, etc.**: String reference - stores in internal pointer array

Uses sscanf with format `"%s %s"` to parse token/value pairs.

Special handling for color values (tokens 0x31-0x39): multiplies by `0.003921569` (1/255) to normalize 0-255 to 0.0-1.0.

---

### CTokenArchive__BindIndexedFieldPointer
| Property | Value |
|----------|-------|
| Address | `0x004f5b70` |
| Returns | `void` |
| Parameters | `int slot_index, void* field_ptr` |
| Calling Convention | `__thiscall` (ECX = this) |
| Saved signature | `void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)` |

Wave1031 (`particle-cpdsimplesprite-runtime-transform-review-wave1031`) corrected this row from the stale `CParticleDescriptor__SetIndexedParam` owner/name to `0x004f5b70 CTokenArchive__BindIndexedFieldPointer`. The body stores `field_ptr` into the TokenArchive slot table at `this+0x0c+(slot_index*4)` and returns with `RET 0x8`. Fresh xref-window exports show `CParticleDescriptor__Load` callsites `0x004c57d4` / `0x004c57e9` plus thirteen adjacent particle descriptor token-load callsites push a descriptor field address, push the parsed slot index, load `ECX` with the TokenArchive receiver, then call this helper. The adjacent `0x004f5b80 CTokenArchive__RegisterReferenceFixup` writes `fixup_record+4` into the same table shape. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified`. Probe token anchor: Wave1031; particle-cpdsimplesprite-runtime-transform-review-wave1031; 0x004f5b70 CTokenArchive__BindIndexedFieldPointer; 0x004c0150 CParticle__ApplyParentTransformOrStoreLink; 0x004c0940 CPDSimpleSprite__SetUVFromTileIndex; 0x004c5280 CPDSimpleSprite__CopyTransformMatrix; 0x004c5410 CParticleDescriptor__Update; 0x004f5b80 CTokenArchive__RegisterReferenceFixup; 626/1408 = 44.46%; 855/1493 = 57.27%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified; one rename/signature/comment correction.

This is static retail Ghidra evidence only. Exact source symbol, concrete token-slot semantics, runtime particle parsing/linking behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

---

### CTokenArchive__RegisterReferenceFixup
| Property | Value |
|----------|-------|
| Address | `0x004f5b80` |
| Returns | `void` |
| Parameters | `int ref_value, int slot_index, void* fixup_record` |
| Calling Convention | `__thiscall` (ECX = this) |
| Saved signature | `void __thiscall CTokenArchive__RegisterReferenceFixup(void * this, int ref_value, int slot_index, void * fixup_record)` |

Records a pending reference fixup. Instruction read-back shows `ret 0x0c`, so the prior fourth stack parameter was stale. The body stores `ref_value` into `fixup_record`, then stores `fixup_record + 4` into the per-slot fixup-target table at `this + 0x0c + slot_index * 4`.

---

### CTokenArchive__ResolveReferences
| Property | Value |
|----------|-------|
| Address | `0x004f5ba0` |
| Returns | `void` |
| Parameters | `void* list_head_ptr` |
| Calling Convention | `__thiscall` (ECX = this) |
| Saved signature | `void __thiscall CTokenArchive__ResolveReferences(void * this, void * list_head_ptr)` |
| Line refs | 0x1c2 (450) |

Post-parsing phase that resolves string references to object pointers.

**Algorithm:**
1. Count items in linked list (follows offset +0x38 for next pointer)
2. Allocate array of pointers
3. For each stored string reference, use bsearch to find matching object
4. Replace string with object pointer (or NULL if not found)
5. Free temporary string allocations
6. Reset reference counter to 0

---

### CTokenArchive__WriteInt
| Property | Value |
|----------|-------|
| Address | `0x004f5c90` |
| Returns | `void` |
| Parameters | `int token_id, int value` |
| Calling Convention | `__stdcall` |
| Saved signature | `void __stdcall CTokenArchive__WriteInt(int token_id, int value)` |

Formats an integer token line using `"%s %d"`. The final archive sink remains unproven from this static tranche.

---

### CTokenArchive__WriteFloat
| Property | Value |
|----------|-------|
| Address | `0x004f5cd0` |
| Returns | `void` |
| Parameters | `int token_id, float value` |
| Calling Convention | `__stdcall` |
| Saved signature | `void __stdcall CTokenArchive__WriteFloat(int token_id, float value)` |

Formats a float token line using `"%s %f"`. The final archive sink remains unproven from this static tranche.

---

### CTokenArchive__WriteString
| Property | Value |
|----------|-------|
| Address | `0x004f5d10` |
| Returns | `void` |
| Parameters | `int token_id, char* value` |
| Calling Convention | `__stdcall` |
| Saved signature | `void __stdcall CTokenArchive__WriteString(int token_id, char * value)` |

Formats a string token line using `"%s %s"`. The final archive sink remains unproven from this static tranche.

---

### CTokenArchive__WritePointer
| Property | Value |
|----------|-------|
| Address | `0x004f5d50` |
| Returns | `void` |
| Parameters | `int token_id, void* named_object` |
| Calling Convention | `__stdcall` |
| Saved signature | `void __stdcall CTokenArchive__WritePointer(int token_id, void * named_object)` |

Formats a pointer reference token. If `named_object` is null, it formats `"%s NONE"`; otherwise it formats `"%s %s"` using the object's name at `named_object + 4`.

---

### CTokenArchive__WriteFloatPointer
| Property | Value |
|----------|-------|
| Address | `0x004f5dc0` |
| Returns | `void` |
| Parameters | `int token_id, void* value_ref_record` |
| Calling Convention | `__stdcall` |
| Saved signature | `void __stdcall CTokenArchive__WriteFloatPointer(int token_id, void * value_ref_record)` |

Formats a float value with an associated pointer reference. `value_ref_record + 0` is the float, and `value_ref_record + 4` is treated as a named-object pointer.
- If pointer is NULL: format `"%s %f NONE"`
- If pointer is valid: format `"%s %f %s"` (with object name)

## CTokenArchive Class Layout (Partial)

Based on decompilation analysis:

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | void* | vtable? | |
| +0x08 | int | mNumStrings | Count of stored string references |
| +0x9C4C | char*[] | mStrings | Array of allocated string pointers (up to ~10000) |

## Related Systems

- **ParticleDescriptor.cpp** - Uses TokenArchive for particle type definitions
- **ParticleSet.cpp** - Uses TokenArchive for particle system configurations
- **ParticleManager.cpp** - Manages loading/saving of particle archives

## Format Strings Used

| Address | Format | Usage |
|---------|--------|-------|
| 0x00625274 | `"%s %s"` | Token/value parsing |
| 0x00633a24 | `"%f"` | Float value scanning |
| 0x00625098 | `"%f"` | Float value scanning (alternate) |
| 0x00633a28 | `"%s %d"` | Integer output |
| 0x00633a30 | `"%s %f"` | Float output |
| 0x00633a38 | `"%s %s"` | String output |
| 0x00633a40 | `"%s NONE"` | Null pointer output |
| 0x00633a4c | `"%s %f NONE"` | Float with null pointer |
| 0x00633a5c | `"%s %f %s"` | Float with pointer reference |

## Memory Allocation

Uses custom allocator `OID__AllocObject` (likely `operator new` or memory pool) with parameters:
- Size in bytes
- Allocation type/tag (0x61, 0x80)
- Source file path
- Line number

Corresponding free function: `OID__FreeObject`
