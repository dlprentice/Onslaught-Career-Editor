# Widescreen Regions 8-11 Validation

> Date: 2026-03-01
> Scope: close out behavior uncertainty for diff regions 8-11 in `BEA.exe` vs `BEA_Widescreen.exe`.

## Target Regions

| Region | File Offset | VA | Original | Patched |
|---|---:|---:|---|---|
| 8 | `0x0013E32F..0x0013E333` | `0x0053E32F` | `8B 11 FF 52 10` | `E9 9D 9C 09 00` |
| 9 | `0x0013F3B7..0x0013F3BC` | `0x0053F3B7` | `D9 05 40 8A 88 00` | `E9 99 45 06 00 90` |
| 10 | `0x00141B59..0x00141B5C` | `0x00541B59` | `D9 84 24 C4` | `E9 83 64 09` |
| 11 | `0x00141B5E..0x00141B5F` | `0x00541B5E` | `00 00` | `90 90` |

## Evidence (Disassembly)

### Region 8 hook and cave target

Patched site (`BEA_Widescreen.exe`):

```asm
0053E32F: E9 9D 9C 09 00    jmp 0x005D7FD1
```

Cave payload (`.rdata` raw-disassembled):

```asm
005D7FD1: 8B11               mov edx,[ecx]
005D7FD3: FF5210             call [edx+0x10]
005D7FD6: D80DF44F9D00       fmul dword [0x009D4FF4]
005D7FDC: E95363F6FF         jmp 0x0053E334
```

Conclusion: region 8 is a functional render-path hook that preserves the original virtual call and scales its float result by the widescreen ratio term.

### Region 9 hook and cave target

Patched site (`BEA_Widescreen.exe`):

```asm
0053F3B7: E9 99 45 06 00    jmp 0x005A3955
0053F3BC: 90                nop
```

Cave payload:

```asm
005A3955: D90598B35D00       fld dword [0x005DB398]
005A395B: D835F84F9D00       fdiv dword [0x009D4FF8]
005A3961: E957BAF9FF         jmp 0x0053F3BD
```

Conclusion: region 9 replaces a static FOV constant load with a runtime-adjusted value derived from widescreen globals.

### Regions 10-11 hook and cave target

Patched site (`BEA_Widescreen.exe`):

```asm
00541B59: E9 83 64 09 00    jmp 0x005D7FE1
00541B5E: 90 90             nop nop
```

Cave payload (`.rdata` raw-disassembled):

```asm
005D7FE1: D944E410           fld dword [esp+0x10]
005D7FE5: D9C0               fld st0
005D7FE7: D835F44F9D00       fdiv dword [0x009D4FF4]
005D7FED: D954E410           fst dword [esp+0x10]
005D7FF1: DEE9               fsubp st1
005D7FF3: D80DEC855D00       fmul dword [0x005D85EC]
005D7FF9: E9B7FDFFFF         jmp 0x005D7DB5
```

Follow-on trampoline in `.text`:

```asm
005D7DB5: D884E4C4000000     fadd dword [esp+0xC4]
005D7DBC: EB28               jmp 0x005D7DE6
005D7DE6: E9759DF6FF         jmp 0x00541B60
```

Conclusion: region 10 is functional (FPU transform path rewrite), and region 11 is supportive padding for the 5-byte jump replacement.

## Ownership Context (supporting, from `all_after_wave217.tsv`)

- `0x0053E32F` lies in `CDXEngine__Render` (`0x0053E2E0`)
- `0x0053F3B7` lies in `CDXFMV__VFunc_06_0053F180` (`0x0053F180`)
- `0x00541B59`/`0x00541B5E` lie in `CDXFrontEndVideo__Render` (`0x00541790`)

## Final Classification Update

- Region 8: `known-functional` (high)
- Region 9: `known-functional` (high)
- Region 10: `known-functional` (high)
- Region 11: `known-supporting` (high)

This closes the prior `unknown-needs-re` status for the 8-11 cluster.
