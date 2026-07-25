# Retail capture provenance — what the reference screenshots actually show

Date: 2026-07-25. Method: static byte comparison of both retail binaries plus
direct pixel measurement of the reference captures. No claim here rests on reading
decompiler output or reference source.

Full working notes, including the adversarial pass, are lab-only (gitignored) at
`local-lab/HYPOTHESIS-1-VERDICT-2026-07-25.md`.

## Why this matters

Frontend parity work compares the reconstruction against retail screenshots. Those
screenshots were captured from a **safe copy of the installed `BEA.exe`, not from
pristine retail**. Anything that binary draws differently from pristine is a false
target that will be faithfully reproduced as a defect. One already was — see
"Consequences".

## The two binaries

| | sha256 | role |
| --- | --- | --- |
| `BEA.exe.original.backup` | `74154bfa…e1e7750` | pristine retail; the Ghidra DB was built from this |
| installed `BEA.exe` | `e78818…829c918` | capture source; `extents.json` records this hash |

Both are 2,506,752 bytes. PE i386, ImageBase `0x00400000`.

## Complete difference: 28 bytes in 4 runs

| File offset | Len | VA | Patch key (`BinaryPatchEngine.cs`) |
| --- | ---: | --- | --- |
| `0x06416f` | 3 | `0x0046416f` | `version_overlay_use_patched_format_pointer` |
| `0x129696` | 1 | `0x00529696` | `resolution_gate` (**primary byte only**) |
| `0x12a644` | 4 | `0x0052a644` | `force_windowed` |
| `0x1aa444` | 20 | `0x005aa444` | `version_overlay_patched_format_cave_string` |

**All 27 entries of `s_widescreenAspectRegions` are absent**, as are
`extra_graphics_default_on` and `ignore_cardid_tweak_overrides`. Of the 28 rows in
`widescreen-diff-regions-28.tsv`, exactly one is live: `region_id=3`, the reject
gate at `0x00129696`.

## What the aspect-adjacent byte does, and why it is harmless here

`0x129696` is the first displacement byte of `JNZ 0x00529766` at `0x00529694`,
inside `CD3DApplication__BuildDeviceList`:

```
0x529688  lea edx,[eax*4]        ; height * 4
0x52968f  lea eax,[ebx+ebx*2]    ; width  * 3
0x529692  cmp eax,edx            ; width*3 == height*4  <=>  4:3
0x529694  jnz 0x529766           ; reject non-4:3 mode   <-- patched byte
```

`cc`→`00` retargets the jump to the next instruction, neutering the 4:3 mode
filter. It only *widens* what the enumerator accepts.

It cannot reach the captures, for a structural reason rather than a coincidental
one. In `CD3DApplication__Initialize3DEnvironment` (`0x0052af00`) the present-params
fork at `0x0052b0c8` branches on `m_bWindowed`:

- **fullscreen** (`0x0052b180`): backbuffer W/H/format come from the selected
  enumerated mode.
- **windowed** (`0x0052b0d0`): backbuffer W/H are the window client rect; the mode
  array is never consulted.

`force_windowed` pins `m_bWindowed` to 1, so the backbuffer is the client rect by
construction and no change to the mode list can reach geometry. The aspect consumer
at `0x0052b14b` computes `factor = K * H / W` from the live backbuffer; at 4:3 with
the default `K = 1.3333334` that is exactly `1.0`, identical to pristine.

**Caveat.** `0x00662df0`, the pristine source of `m_bWindowed`, lies above `.data`'s
raw size — BSS, with no absolute writer and exactly one `.text` reference (the read
the patch overwrites). Pristine retail is therefore effectively **fullscreen-only**
and would have taken its resolution from the enumerated mode list. The 640x480 of
these captures is an artifact of `force_windowed`. Aspect *ratios* are unaffected;
**absolute pixel extents are not guaranteed** to be pristine's choice, and
`extents.json` states its settle math in absolute pixels.

**Two further aspect gates exist in stock retail** and should be pinned by any
future capture: global `0x0089c0ac` (tested at `0x00529686`) skips the 4:3 filter
outright, and `g_ScreenShape` at `0x0082b484` selects a stock `1.7777778` constant
at `0x005e4aec`.

## The one visible contamination

| | VA | contents |
| --- | --- | --- |
| pristine | `0x00629454` | `V%1d.%02d` |
| installed | `0x005AA444` | `V%1d.%02d - PATCHED` |

The reference frame renders **`V1.00 - PATCHED`** in its bottom-left corner.
Released retail renders **`V1.00`**.

## Consequences

1. **The captures are sound as a 4:3 layout and colour reference.** Aspect handling
   is byte-identical to pristine in every respect that composes a frame.
2. **The version overlay string is not.** `RetailFrontendFlow` had hardcoded
   `"V1.00 - PATCHED"`, transcribed from the contaminated capture. Corrected. This
   is the clearest instance of a contaminated reference becoming a product defect,
   and `drawlists/COORDINATOR.md` had listed `version` as an unresolved item for
   precisely this reason.
3. **Future captures should stay at 640x480, or use a pristine safe copy.** A
   capture at a non-4:3 resolution on this safe copy would run unpatched 4:3 aspect
   math against a widescreen mode — a state neither pristine nor fully-patched
   retail produces.

## Verification status

Primary and adversarial passes both completed. The adversarial pass independently
recomputed the diff, re-derived the disassembly from call-target anchors rather than
from exported TSVs, and decoded the PNGs itself. It corrected the region-count
claim and contributed the `m_bWindowed` mechanism and caveat above. Where the two
disagreed, the adversarial reading was adopted.
