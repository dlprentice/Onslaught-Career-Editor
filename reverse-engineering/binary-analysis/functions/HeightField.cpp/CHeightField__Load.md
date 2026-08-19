# CHeightField__Load

> Address: 0x0047f750 | Source: HeightField.cpp (source file not present in `references/Onslaught/` snapshot)

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x0040c640` | `DebugPrint` | `DebugTrace` | label replaced |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

---

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes, corrected in Wave396
- **Verified vs Source:** No (source not yet provided by Stuart)

## Purpose
Loads heightfield terrain data from a serialized level resource. Validates expected size (0x13dc = 5084 bytes), allocates height buffer, processes color/lighting data, and reads height samples in 9x9 tile blocks.

## Signature
```c
// Thiscall convention (ECX = this)
void __thiscall CHeightField__Load(void * this, void * chunk_reader);
```

## MEASURED 2026-08-19 (overlay writes `+0x102c`)

Independently re-read official specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` =
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(2506752 bytes; pristine-target twin matches). No Ghidra. Table names
are labels. Wave396 / decompiler text below is **not** this proof.

`thiscall`, `ECX`→`EDI`. One stack arg (chunk reader) → `EBP`.
`ret 4` at `0x0047f9af`. Body `0x0047f750`–`0x0047f9b1` is 610 bytes,
SHA-256
`ce5c79bbbcdbec27f0ca2cd082a49b639560cd09bafbc3fdddf4f4963dbb55a1`.
Eleven `E8`, zero `E9`. One inbound `E8`: `0x004910d6` inside
`CHeightField__DeserializeMapAndInitResources`. That body's sole
inbound is `CEngine__Deserialize` `0x0044a72f`:

```
push ebx
mov  ecx, 0x006fadc8
call 0x00491060
```

So Load's `this` is the shared BSS instance.

`CChunkReader__Read` (`0x00423960`) is `thiscall` `ret 0xc`:
`dest, nbytes, count`; copies `nbytes*count` from `[reader+4]` via
`CDXMemBuffer__Read` `0x00548570` and advances `[reader+8]`. Overlay:

```
push 1
push 0x13dc
push edi          ; dest = this
mov  ecx, ebp
call 0x00423960   ; 0x0047f7dc
```

That is the only image `0x13dc`-byte copy onto an object. It writes
`[this+0x102c]` (scale). Image-wide, every instruction-aligned
`disp32 0x102c` is a **load** (`fmul` ×5, `mov eax,[ebx+0x102c]`,
`fld` ×2). No `mov`/`fstp`/`mov dword` store of `+0x102c`. Ctor
`0x0047e870` zeros `+0x20`/`+0x24`/`+0x28..+0x1027`/`+0x1028` and
does not touch `+0x102c`. After the overlay, Load replaces only
`[+0x1028]` with `CDXMemoryManager__Alloc(0xa2000)` at `0x0047f8d2`.
The authored float at overlay `+0x102c` is **not** read here.

Cheapest falsifier: file `0x0007f750` is not `81 ec 14 01 00 00`,
**or** `0x0007f9af` is not `c2 04 00`, **or** body
`0x0007f750`–`0x0007f9b1` SHA-256 is not `ce5c79bb…55a1`, **or**
`0x0007f7d2` is not `6a 01 68 dc 13 00 00 57`, **or**
`tools/call_xref_scan.py` on `0x0047f750` is not exactly `E8` at
`0x004910d6`, **or** `0x0004a72a` is not
`b9 c8 ad 6f 00 e8 2c 69 04 00`, **or** `0x00023989` is not
`c2 0c 00`, **or** any of the eight `2c 10 00 00` sites decodes as a
store to `[reg+0x102c]`.

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047f750` | `CHeightField__Load` | `81ec14010000 53 55 56 57 8bf9 … 6a01 68dc130000 57 … c20400` | thiscall; ret 4; 0x13dc overlay onto `this=0x006fadc8`; that write is the `+0x102c` scale. HIGH on ABI, inbound, overlay, image-wide load-only `+0x102c`. **Not** on the authored float or color/sample loops. |

## Wave396 Read-Back

Wave396 corrected the undefined saved signature to a thiscall shape with one chunk-reader stack argument. Post-apply read-back validates the expected `0x13dc` structure size, calls `CHeightField__InitColorGradient`, allocates the `0xa2000`-byte height buffer, and reads repeated `9x9` tile blocks. This is saved static Ghidra metadata/read-back evidence only; it does not prove runtime terrain behavior or complete concrete field typing.

## Decompiled Analysis

### Memory Allocation
```c
// Frees existing buffers
if (this->pUnknown1 != NULL) {
    CMemoryManager::Free(this->pUnknown1);
    this->pUnknown1 = NULL;
}
if (this->pHeightData != NULL) {
    CMemoryManager::Free(this->pHeightData);
    this->pHeightData = NULL;
}

// Allocate new height buffer
// 0xa2000 = 663,552 bytes = 331,776 height samples (16-bit)
this->pHeightData = CMemoryManager::Alloc(0xa2000, 0x22,
    "[maintainer-local-source-export-root]\\HeightField.cpp", 0x880);
```

### Size Validation
```c
if (*pSizePtr != 0x13dc) {
    sprintf(buffer, "Got size %d, expected %d", *pSizePtr, 0x13dc);
    DebugPrint(buffer);
}
```

### Color Processing
The function processes ARGB color values at offsets 0x107c and 0x108c, extracting RGB channels and normalizing them to prevent overflow past 0xFF.

### Height Data Reading
Height data is read in nested loops:
- Outer: until 0xa2000 bytes read
- 64 iterations (0x40)
- 9x9 = 81 height values per tile
- Each value is 2 bytes (16-bit short)

```c
do {
    for (i = 0x40; i != 0; i--) {
        for (j = 9; j != 0; j--) {
            for (k = 9; k != 0; k--) {
                ReadStream(&heightValue, 2, 1);
                *(short*)(offset + this->pHeightData) = heightValue;
                offset += 2;
            }
        }
    }
} while (offset < 0xa2000);
```

### Color Gradient Post-Processing
After loading, the function doubles color values in the gradient table and clamps to maximum values (RGB565-like encoding).

## Cross-References

### Called By
| Address | Function | Context |
|---------|----------|---------|
| 0x004910d6 | CHeightField__DeserializeMapAndInitResources | Wave426-corrected MAP deserialize/resource-init caller; static context includes "Deserializing map" |

### Calls
| Address | Function | Purpose |
|---------|----------|---------|
| 0x00549220 | CMemoryManager::Free | Free existing buffers |
| 0x005490e0 | CMemoryManager::Alloc | Allocate height buffer |
| 0x00423910 | StreamReader::GetTag | Stream reading |
| 0x00423960 | StreamReader::Read | Read data from stream |
| 0x0047e8e0 | CHeightField__InitColorGradient | Initialize color gradient table |
| 0x0055de9b | sprintf | Format error messages |
| 0x0040c640 | DebugTrace | Debug output |

## Key Values
- **Struct Size:** 0x13dc (5084 bytes)
- **Height Buffer Size:** 0xa2000 (663,552 bytes)
- **Height Samples:** 331,776 (16-bit values)
- **Tiles per Load:** 64 (0x40)
- **Tile Size:** 9x9 = 81 height values
- **Alloc Debug Line:** 0x880 (2176 decimal)

## Notes
- Uses thiscall convention (ECX = this pointer)
- Migrated from debug string xref analysis (Dec 2025)
- The 9x9 tile structure suggests terrain patches for LOD
- Color processing suggests fog/ambient color blending
- Related to CResourceAccumulator level loading system

## Related Functions
- [CHeightField__InitColorGradient](CHeightField__InitColorGradient.md) - Called during load
