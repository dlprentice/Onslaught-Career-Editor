# CHeightField__RecomputeGridExtentsAndHeightRange

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Wave396 / A15 text is **not** this proof.

> Address: `0x0047ef20`

## Contract

`thiscall`. Zero stack args. `ECX` is this for the whole body. Two
bare `ret` (`c3`) sites: `0x0047efe7` (walked) and `0x0047efea`
(early-out). EAX is `ECX` on both (`mov eax, ecx`). Body
`0x0047ef20`–`0x0047efea` is 203 bytes, SHA-256
`57cf35b2956ce1f1d2374be41dc5898a07188fc307ff4ebae26a36f612968854`.
Zero `E8`, zero `E9`.

Two inbound `.text` `E8`s, zero `E9`. Both load the already-pinned
BSS this first:

```
mov  ecx, 0x006fadc8
call 0x0047ef20
```

| site | owner (table label) | file bytes |
| --- | --- | --- |
| `0x0053a3ab` | `CDXBattleLine__UpdateHeightmap` | `b9 c8 ad 6f 00 e8 70 4b f4 ff` |
| `0x0053a602` | `CDXBattleLine__BuildMesh` | `b9 c8 ad 6f 00 e8 19 49 f4 ff` |

`BuildMesh` parks EAX in `EDI` and `fild`s `[edi]`, `[edi+4]`,
`[edi+8]`, `[edi+0xc]` (the integer slots this body writes). Mesh
algebra is **not** claimed.

First instruction:

```
cmp  dword ptr [ecx+0x10], 0xcaa24af0
jne  0x0047efe8
```

`0xcaa24af0` is −5318008.0f if read as a float. The immediate exists
**once** in the image, at this `cmp`. Who first plants that dword at
`[+0x10]` is **not** claimed.

If the compare fails, EAX=`this` and the body writes nothing.

If it matches, the body seeds then optionally walks:

| slot | seed | later role |
| --- | --- | --- |
| `[this+0]` | `0x000186a0` (100000) | min of column index `edx` |
| `[this+4]` | `0x000186a0` (100000) | min of row index `edi` |
| `[this+8]` | `0xfffe7960` (−100000) | max of column index `edx` |
| `[this+0xc]` | `0xfffe7960` (−100000) | max of row index `edi` |
| `[this+0x18]` | `0xc7c35000` (−100000.0f) | max of `[esi]` |
| `[this+0x1c]` | `0x47c35000` (+100000.0f) | min of `[esi]` |

Walk bounds: `ebp = [this+0x10c0]` (row count, signed `jle` skip if
`<=0`), `ebx = [this+0x10bc]` (column count, same). Sample cursor
`esi = [this+0x20]`, stride `add esi, 0x18`. Authored names for those
three slots, and who writes `[+0x20]`, are **not** claimed.

Per cell:

1. `fld [esi]` / `fcomp [this+0x1034]` / `test ah,1` / `je` skip
   extent. Extent updates **only** when the sample is strictly `<`
   `[this+0x1034]`. Then `edx` vs `[+0]`/`[+8]`, `edi` vs `[+4]`/`[+0xc]`.
2. Always (even when the extent test fails): `[+0x1c]` becomes min of
   `[esi]` (`test ah,1`); `[+0x18]` becomes max of `[esi]`
   (`test ah,0x41` / `jne` skip, so store when sample `>` current).

After the walk (or when a count was `<=0` and seeds stand):

```
[this+0x14] = [this+0x20]
[this+0x10] = [this+0x1034]
eax = this
```

So a second call early-outs unless something rewrites `[+0x10]` back
to `0xcaa24af0` (or any other value that is not the current
`[+0x1034]` bits).

A 2026-07-26 terrain note called this a battle-line object because of
the `0x18` stride. Both inbound sites `mov ecx, 0x006fadc8` before
the call. That identity is the already-pinned heightfield BSS. The
stride does not move `this`.

Cheapest falsifier: file `0x0007ef20` is not `81 79 10 f0 4a a2 ca`,
**or** `0x0007ef27` is not `0f 85 bb 00 00 00`, **or** `0x0007efe7`
is not `c3`, **or** `0x0007efe8` is not `8b c1 c3`, **or** body
SHA-256 is not `57cf35b2…8854`, **or** `tools/call_xref_scan.py` on
`0x0047ef20` is not exactly `E8` at `0x0053a3ab` and `0x0053a602`,
**or** `0x00053a3a6` is not `b9 c8 ad 6f 00 e8 70 4b f4 ff`, **or**
`0x00053a5fd` is not `b9 c8 ad 6f 00 e8 19 49 f4 ff`, **or**
`0x0007ef40` is not `c7 01 a0 86 01 00`, **or** `0x0007efe1` is not
`89 51 10`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047ef20` | `CHeightField__RecomputeGridExtentsAndHeightRange` | `817910f04aa2ca 0f85bb000000 … c701a0860100 … 8bc15d c3 8bc1 c3` | thiscall; bare ret ×2; EAX=this; this imm `0x006fadc8` on both `E8`; dirty `[+0x10]==0xcaa24af0`; integer min/max at `+0/+4/+8/+0xc`; float max/min at `+0x18/+0x1c`; walk `[+0x10c0]`×`[+0x10bc]` at `[+0x20]` stride `0x18`. HIGH on ABI, inbound set, sentinel, seeds, both polarities, tail copies. **Not** on authored names, `[+0x20]` producer, or mesh meaning. |
