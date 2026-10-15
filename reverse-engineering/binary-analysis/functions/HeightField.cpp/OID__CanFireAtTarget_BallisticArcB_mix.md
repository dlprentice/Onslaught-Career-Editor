# OID__CanFireAtTarget_BallisticArcB mix product

Status: active static function note
Last updated: 2026-08-19
Summary: After `0x0047ec60` returns, the 60-byte product at `0x00508f6f`
writes `v' = n1*(n2*B − n1*A) − n0*(n0*A − n2*C) + v` to `[esp+0x14]`.
EAX is untouched. `je 0x00508fab` skips the whole product when
`[this+0x98]==0`. `A≡0` is not claimed here.
Source File: IScript / OID fire twin (not piled onto `IScript.cpp.md`)
| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_46fb9514`. Product `0x00508f6f`–`0x00508faa` SHA-256
`b75807754af7e4f5d8f9c83e5447084616d00edeb0baa00af61daf7f3fd2f3b8`.
No Ghidra. Table name is a label.

> Address: `0x005088b0`

## Contract

Already pinned: `0x0047ec60` writes four dwords at `[esp+0x2c]`;
call site `0x00508f6a`; join `0x00508e71` when `[stmt+0x6c]==0`.
`0x00508e79` is `0f 84 2c 01 00 00` (`je 0x00508fab`) — that skip
never reads the four dwords.

When the product runs, it loads only out+0/+4/+8
(`[esp+0x2c]` / `+0x30` / `+0x34`). No `[esp+0x38]` (out+0xc).

Independently decoded 60 bytes:

```
fld  [esp+0x2c]          ; n0
fmul [esp+0x10]          ; n0*A
fld  [esp+0x34]          ; n2
fmul [esp+0x28]          ; n2*C
fsubp                    ; n0*A − n2*C
fld  [esp+0x34]
fmul [esp+0x1c]          ; n2*B
fld  [esp+0x30]
fmul [esp+0x10]          ; n1*A
fsubp                    ; n2*B − n1*A
fld  [esp+0x30]
fmul st(1)               ; n1*(n2*B − n1*A)
fxch st(2)
fmul [esp+0x2c]          ; n0*(n0*A − n2*C)
fsubp st(2)              ; n1*(…) − n0*(…)
fstp st(0)               ; drop leftover
fadd [esp+0x14]          ; + v
fstp [esp+0x14]
```

`v' = n1*(n2*B − n1*A) − n0*(n0*A − n2*C) + v`. EAX is not written.
Physics identity and the claim that `A` is identically 0 are **not**
claimed. Did not rewrite `IScript.cpp.md`.

Cheapest falsifier: file `0x00108f6f`–`0x00108faa` SHA-256 is not
`b7580775…f3b8`, **or** `0x00108e79` is not `0f 84 2c 01 00 00`,
**or** those 60 bytes contain `24 38`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005088b0` | `OID__CanFireAtTarget_BallisticArcB` | product `d9 44 24 2c d8 4c 24 10 … d8 44 24 14 d9 5c 24 14` | 60-byte mix into `[esp+0x14]`; skip `je 0x00508fab`. HIGH on the bytes and the algebra above. Not on `A≡0` or physics. |
