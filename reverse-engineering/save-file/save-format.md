# BES save file format

Status: supported retail/Steam specimen contract
Last updated: 2026-07-16

Supported career saves are exactly 10,004 bytes (`0x2714`) and begin with the
16-bit version word `0x4BD1`. `CCareer__Load` and `CCareer__Save` copy a fixed
`0x24BC`-byte career block at file offset `0x0002`; therefore the authoritative
dword view begins where `file_offset % 4 == 2`:

```text
file_offset = 0x0002 + career_offset
```

Older aligned-view notes read two bytes early and made ordinary values appear
shifted by 16 bits. Product code and current documentation use the true view.
Stuart's internal-build source is useful for logic and structure names, but the
retail executable and observed retail files own the on-disk contract.

## File layout

| Offset | Size | Content | Write policy |
| ---: | ---: | --- | --- |
| `0x0000` | 2 | version word `0x4BD1` | validate; preserve |
| `0x0002` | 4 | `new_goodie_count` | preserve unless explicitly edited |
| `0x0006` | 6,400 | `CCareerNode[100]` | scoped node edits only |
| `0x1906` | 1,600 | `CCareerNodeLink[200]` | scoped link edits only |
| `0x1F46` | 1,200 | `CGoodie[300]` | indices 0–232 displayable; 233–299 preserve-only |
| `0x23F6` | 20 | five packed kill counters | edit lower 24 bits; preserve every top byte |
| `0x240A` | 128 | `mSlots[32]` | scoped bit edits only |
| `0x248A` | 4 | `mCareerInProgress` | preserve unless explicitly edited |
| `0x248E` | 4 | sound volume float | preserve on career edits |
| `0x2492` | 4 | music volume float | preserve on career edits |
| `0x2496` | 4 | `g_bGodModeEnabled` | scoped edit only |
| `0x249A` | 4 | unused/reserved | preserve |
| `0x249E` | 4 | P1 flight invert Y | scoped options edit only |
| `0x24A2` | 4 | P2 flight invert Y | scoped options edit only |
| `0x24A6` | 4 | P1 walker invert Y | scoped options edit only |
| `0x24AA` | 4 | P2 walker invert Y | scoped options edit only |
| `0x24AE` | 8 | P1/P2 vibration | scoped options edit only |
| `0x24B6` | 8 | P1/P2 controller preset | supported values 1–4 |
| `0x24BE` | 512 | 16 observed options entries | preserve unless editing bindings |
| `0x26BE` | 86 | options/global tail snapshot | preserve unless editing a known field |

The general static size formula is `0x2514 + 0x20 * N`, where `N` is the
enabled options-entry count. The supported retail specimen uses `N = 16` and a
fixed size of `0x2714`; do not resize or synthesize a save for another value.

## Career structures

### `CCareerNode` (64 bytes)

| Relative offset | Field |
| ---: | --- |
| `+0x00` | state/legacy flags; preserve when not targeted |
| `+0x04` | completion dword |
| `+0x08` | lower link index |
| `+0x0C` | higher link index |
| `+0x10` | world number |
| `+0x14` | nine persistence dwords (`mBaseThingsExists`) |
| `+0x38` | attempt count |
| `+0x3C` | ranking float bits |

### `CCareerNodeLink` (8 bytes)

`+0x00` is the link type/state (`0`, `1`, or observed alternate-parent value
`2`); `+0x04` is the destination node index, with `0xFFFFFFFF` unused.

### `CGoodie` (4 bytes)

States are `0` locked, `1` instructions/hint, `2` new, and `3` viewed/old.
MissionScript uses one-based Goodie indices; the save array is zero-based:

```text
save_index = script_index - 1
offset = 0x1F46 + 4 * save_index
```

Only indices 0–232 are supported displayable rows. Reserved rows must remain
unchanged.

## Kill counters and slots

The five kill counters start at true-view offset `0x23F6`. Their lower 24 bits
hold the count; the top byte carries confirmed metadata for the first two rows
and is conservatively preserved for all five. The historical `0x23A4` location
is inside the Goodie array and must never be used for kill edits.

The slot bitset begins at `0x240A`. Retail logic addresses
`mSlots[slot >> 5]` with bit `slot & 31`; observed game logic uses slot IDs
0–255 even though the file reserves 32 dwords. Offset `0x240C` is a legacy
misaligned view inside this bitset, not a god-mode field.

## Options entries

The supported specimen has 16 entries of `0x20` bytes. Each contains an active
flag, entry id, and two binding triples. Packed keys use
`(virtual_key << 16) | scan_code`. The options block is part of both `.bes` and
`defaultoptions.bea`, but retail load behavior differs:

- `CCareer__Load(flag=1)` loads a career while preserving current sound/music
  values and skipping application of the entry/tail globals.
- `CCareer__Load(flag=0)` applies the entry table and calls
  `OptionsTail_Read`; this is the boot path for `defaultoptions.bea`.
- A later career save serializes the current in-memory option table, so an
  existing `.bes` options block can be replaced by the current boot settings.

These semantics are why AppCore treats save and options edits as separate,
byte-preserving operations.

## Tail snapshot

Offsets are relative to `0x26BE` for the supported specimen.

| Offset | Size | Field |
| ---: | ---: | --- |
| `+0x00` | 4 | unknown/default options float |
| `+0x04` | 4 | mouse sensitivity |
| `+0x08` | 2 | control scheme index |
| `+0x0A` | 2 | language index |
| `+0x0C` | 4 | mesh quality distance |
| `+0x10` | 4 | mesh LOD bias |
| `+0x14` | 4 | mesh quality scale |
| `+0x18` | 4 | mesh quality LOD table |
| `+0x1C` | 4 | low-resolution landscape geometry flag |
| `+0x20` | 4 | screen shape |
| `+0x24` | 4 | mipmapping-disallow flag |
| `+0x28` | 4 | D3D device index |
| `+0x2C` | 4 | lockable-backbuffer flag |
| `+0x30` | 4 | landscape maximum levels |
| `+0x34` | 4 | texture resolution-loss shift |
| `+0x38` | 4 | 32-bit texture allowance |
| `+0x3C` | 4 | multisample override |
| `+0x40` | 4 | invert-X flag |
| `+0x44` | 4 | sound enabled |
| `+0x48` | 4 | sample-rate index |
| `+0x4C` | 4 | sound device index |
| `+0x50` | 4 | 3D sound method |
| `+0x54` | 1 | landscape detail level 2 flag |
| `+0x55` | 1 | landscape detail level 1 flag |

## Product rules

1. Accept only a real baseline of the supported size/version.
2. Copy before write when the input is not already an app-owned output.
3. Reject in-place writes where the workflow promises a copy.
4. Preserve file length and every byte outside the selected field ranges.
5. Re-read and validate the written file; keep the original unchanged on
   validation failure.
6. Do not infer runtime behavior or another build's format from this specimen.

Focused implementation protection lives in AppCore tests using the reviewed
`tests_shared/fixtures/gold_career_save.bin` fixture. That fixture is the only
tracked save-payload exception.
