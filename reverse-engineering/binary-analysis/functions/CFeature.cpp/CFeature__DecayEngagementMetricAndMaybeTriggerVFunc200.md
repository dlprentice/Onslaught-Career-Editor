# CFeature__DecayEngagementMetricAndMaybeTriggerVFunc200

Status: active static function note
Last updated: 2026-08-19
Source File: CFeature.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a
research label. It is **not** a decay-metric proof.

> Address: `0x0044cd20`

## Contract

`thiscall`. `ECX`→`ESI`. Four stack dwords (`ret 0x10` at
`0x0044cd7d`). Body `0x0044cd20`–`0x0044cd7f` is 96 bytes,
SHA-256
`9abb211c116197c64b765b88daa16bc77854e1f8324535b1385eb6ff9be3f27a`.
Zero `E8` / `E9`. Zero inbound `.text` `E8`/`E9` — slot 40
(`+0xa0`) of the `CFeature` vtable at `0x005e45e0` (COL
`0x006184c0`; slot 7 returns the shipped literal `CFeature` at
`0x0063da28`).

```
eax = [this+0xe4]
if [eax+0x10] != 0: ret 0x10
fld  [this+0xe0]
fsub [esp+8]
fst  [this+0xe0]
fcomp 0.0f at 0x005d856c
if ST0 < 0 and ([this+0x2c] & 4) == 0:
    call [vtable+0xc8]          ; 0x0044cd80
if [this+0xe0] > [data+0x18]:
    [this+0xe0] = [data+0x18]
```

`CFeature__Init` `0x0044cb36` is `8b 48 18 89 8b e0 00 00 00`:
`[this+0xe0] = [[this+0xe4]+0x18]`. So the subtracted slot is
seeded from the same data record's `+0x18`. Authored names for
`+0xe0` / `+0xe4` / `+0x10` / `+0x18` are **not** claimed.

Slot 50 (`0x0044cd80`) is already pinned on
[`CComplexThing.cpp.md`](../CComplexThing.cpp.md): if `TF_DYING`
already set return 0; else `or` bit 2 of `[this+0x2c]`, optional
`CallEventId5` if `+0x74`, return 1. That is the FillOut store-0
bit.

Cheapest falsifier: file `0x0004cd20` is not
`56 8b f1 8b 86 e4 00 00 00`, **or** `0x0004cd7d` is not
`c2 10 00`, **or** body SHA-256 is not `9abb211c…f27a`, **or**
`tools/call_xref_scan.py` on `0x0044cd20` is not empty, **or**
`0x001e4680` is not `20 cd 44 00`, **or** `0x0004cd29` is not
`8b 48 10`, **or** `0x0004cd36` is not `d8 64 24 08`, **or**
`0x0004cd57` is not `ff 92 c8 00 00 00`, **or** `0x0004cb36` is
not `8b 48 18 89 8b e0 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0044cd20` | `CFeature__DecayEngagementMetricAndMaybeTriggerVFunc200` | `568bf1 8b86e4000000 8b4810 85c9 754c d986e0000000 d8642408 … ff92c8000000 … c21000` | thiscall; ret 0x10; virtual-only slot 40. If `[data+0x10]==0`, subtract `[esp+8]` from `[this+0xe0]` and call slot 50 when the result is `< 0`. HIGH on ABI, those slots, that call. **Not** on authored names or L100 iceberg `[data+0x10]` / `[data+0x18]` values. |
