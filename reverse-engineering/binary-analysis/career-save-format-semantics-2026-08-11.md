# `CCareer` released PC save-format semantics

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — complete pristine retail bodies and instruction streams,
the supported 10,004-byte save specimen, retained `CCareer` source, typed
frontend callers, and eight normalized-identical PC demo twins; UNKNOWN —
fault-injected load/write behavior, other-platform layouts, arbitrary option
table configurations, and rebuild-wide persistence parity.
Verdict: the released PC serializer is recovered. It is not the retained
source's simple version-plus-`CCareer` dump: PC appends active control records
and a fixed hardware/options tail, and `Load` has separate career and default-
options modes.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
The source anchors are `references/Onslaught/Career.cpp` (SHA-256
`8bcb11203dce213ddc89b108756dd23ce9ac08641e7286b40eb94a7b396eb87d`)
and `references/Onslaught/Career.h` (SHA-256
`a17ac88e6569ad0eca8a87b72c709f43b2d60220655e23c84883d2485e4469e9`).

## Result

The eight-function unit covers 2,339 retail bytes and 711 decoded
instructions. Every body has an independently mapped PC demo twin with zero
normalized instruction differences; 232 raw bytes differ only in encoded
addresses or displacements. The machine-readable result is
[`career-save-format-semantics-2026-08-11.tsv`](career-save-format-semantics-2026-08-11.tsv).
It is 2,870 bytes with SHA-256
`847ba38e10b0e6df703355a2ab62de70493a0c6a9f8044ca353e1b54de8959ef`.

This cross-build match covers the complete serializers, loader, size
calculator, options-tail reader/writer, and the two display-profile helpers.
The file law is therefore independently present in two PC executables rather
than inferred from one decompiler rendering.

## Exact released layout and size law

`CCareer::Save` writes:

| File offset | Size | Released operation |
| ---: | ---: | --- |
| `0x0000` | 2 | Version stamp; `0x4BD1` in the supported specimen. |
| `0x0002` | `0x24BC` | Raw fixed `CCareer` block (`0x92F` dwords). |
| `0x24BE` | `0x20 * N` | One raw 32-byte record for each active current option-table entry. |
| `0x24BE + 0x20*N` | `0x56` | PC graphics, controls, language, display-profile, and audio tail. |

`CCareer::GetSaveSize` computes the same layout rather than returning a fixed
literal:

```text
save_size = 0x2514 + 0x20 * active_option_count
```

The released supported table has 16 active records, so the file is exactly
`0x2714` (10,004) bytes and the tail begins at `0x26BE`. The active-record walk
uses the current 0x20-stride option table and its linked/sentinel field; it does
not serialize disabled rows. This formula describes the executable. It does
not authorize AppCore to resize or synthesize saves for an unobserved table
configuration.

There are two serializer entry points. `CCareer::Save` leaves the in-memory
progress flag alone. `CCareer::SaveWithFlag` first writes `1` to
`CCareer+0x2488`—file offset `0x248A`—then emits the identical bytes. The
frontend save transaction uses the latter. The retained source has only one
`Save(char*)` and always marks the career in progress, so the split is a real
released-PC divergence.

## `Load` has two modes

Both modes first require the exact version word and return false without
copying on mismatch. A valid file copies the fixed `0x24BC`-byte career block.
It then validates the metadata byte of the first two packed kill counters at
`CCareer+0x23F4/+0x23F8`: a byte within `0x40..0xC0` is retained, otherwise it
is reset to `0x80`; the lower 24 counter bits are preserved.

The low byte of the third argument selects the remaining policy:

| Flag | Released behavior |
| ---: | --- |
| `0` | Apply the loaded music and sound volumes; copy each serialized active 0x20-byte option record into the live option table; call `OptionsTail_Read`. This is the default-options mode. |
| nonzero | Select the latest unlocked world; restore the pre-load sound and music values; skip the serialized option records and tail. `CFEPLoadGame::DoLoad` passes `1` for a normal career load. |

The fixed career copy happens in both cases, so a career file's embedded option
bytes remain part of its on-disk representation even when the normal load path
does not apply them. A later save writes the then-current live options back to
the file. The retained source always applies sound/music and uses its boolean
only to select the latest level; it has no PC option extension. Retail owns the
PC behavior where they disagree.

## The 0x56-byte options tail

`OptionsTail_Write` serializes the following exact slots. Names below describe
the released globals or their established product role; they are not a claim
that a matching source struct existed.

| Tail offset | Size | Value |
| ---: | ---: | --- |
| `+0x00` | 4 | options/default float 0 |
| `+0x04` | 4 | mouse sensitivity |
| `+0x08` | 2 | control-scheme index |
| `+0x0A` | 2 | language index |
| `+0x0C..+0x18` | 16 | four mesh-quality/LOD values |
| `+0x1C` | 4 | landscape LOD-height/low-resolution flag |
| `+0x20` | 4 | screen shape |
| `+0x24` | 4 | disallow-mipmapping flag |
| `+0x28` | 4 | packed D3D device/mode key |
| `+0x2C` | 4 | lockable-backbuffer flag |
| `+0x30` | 4 | landscape LOD quality |
| `+0x34` | 4 | texture downscale shift |
| `+0x38` | 4 | texture-compression mode |
| `+0x3C` | 4 | current adapter/profile field |
| `+0x40` | 4 | invert-X flag |
| `+0x44..+0x50` | 16 | sound enabled, sample-rate index, device index, and 3D method |
| `+0x54..+0x55` | 2 | two boolean landscape-detail levels |

`OptionsTail_Read` restores the scalar values, applies the control preset and
language, and routes graphics integers through the current console-variable
owners. It detects changes to the display-sensitive fields. If the persisted
device key is not in the current adapter's mode list, it chooses mode zero,
updates the packed key, and marks display reset pending; a changed display
configuration sets the released reset state to `2` when Direct3D is active.

Audio is handled as one four-field transaction. A change in enabled state,
sample rate, device, or 3D method stores all four and calls the sound
reinitialization path with music restoration. With no such change, it reloads
the language sample bank instead. Both landscape-detail bytes are normalized
to booleans.

## Persisted display key

The two small helpers make the `+0x28` field reproducible. Adapter records use
a `0x516C` stride; index `-1` selects the active adapter stored at table
`+0x32E40`. Given the selected mode record, the packed key contains:

- record dword 0 in bits 0–15;
- record dword 1 masked with `0x7FFF` in bits 16–30;
- bit 31 set when the record's format dword is `0x14`, `0x15`, or `0x16`.

This is enough to parse and preserve the released field and to understand the
fallback comparison. It does not establish the complete Direct3D profile-table
type or guarantee that a saved mode is valid on another machine.

## Boundary

This closes the static PC serializer, loader, and size calculation for the
supported specimen. It does not authorize in-place writes, file synthesis,
real-career fault tests, or assumptions about Xbox/PS2 padding. Product writes
must still start from a real baseline, preserve unselected bytes and file
length, write to a safe copy, and re-read the result. The lower filename-backed
adapter is documented separately in the
[`CPCMemoryCard` crosswalk](cpcmemorycard-pc-save-backend-semantics-2026-08-11.md),
and the frontend transaction is documented in the
[save/load crosswalk](frontend-save-load-semantics-2026-08-11.md).
