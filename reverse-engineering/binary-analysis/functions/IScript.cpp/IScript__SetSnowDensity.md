# IScript__SetSnowDensity

> Address: `0x00538380`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetSnowDensity` and the `atm_snowdensity` console variable are absent from `references/Onslaught/` (checked 2026-08-22) | | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 44, registered as `SetSnowDensity`: one float
expression through element `vtable[+0x34]`, stored into the global
snow-density cell `0x0066018c`. That cell is the `atm_snowdensity`
console variable ("Snow density (0-1)"), zeroed per level by
`Atmospherics__Init`, and — uniquely in the weather quartet — this
wake pinned **two live readers**: a particle-count law
`(int)(density × 0x5d8c54_float)` clamped at 1000, and a second
consumer window. No shipped mission calls it (`DORMANT_CANDIDATE`
0/0).
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly, raw byte reads (body hash; image-wide imm32 census;
descriptor walk), rel32 xref scan, and reader windows
(`local-lab/famB_consumers.py`). No `FUN_*` milled; no Core owner
invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

`mission-native-corpus-coverage-2026-08-15.tsv` row 44 is
`SetSnowDensity` / `0x00538380` / empty name-table cell / 0 authored
sites / 0 levels / `DORMANT_CANDIDATE`; confirmed this wake. The
handler is unnamed in the current saved table; no rename performed.
Registration:

- Handler immediate: `mov edi, 0x00538380` (`bf 80 83 53 00`) at VA
  `0x00530ebf` — exactly **one** image-wide imm32 of `0x00538380`.
- Handler cell store: `mov [0x64d950], edi` at VA `0x00530ece`.
- Name-pointer store: `mov dword ptr [0x64d920], 0x64f7f8` at VA
  `0x00530f41`; `.rdata 0x64f7f8` is `"SetSnowDensity\0"`.
- Descriptor: name cell `0x64d920`, handler cell +0x30 at
  `0x64d950`.

## Contract (byte-exact)

Body `0x00538380`–`0x00538391` inclusive through the complete
`ret 0xc`, **18 bytes**, SHA-256
`d264ac612ef05855bd1ad422109d5c2446588591b7d9e30a2207872fae09cdef`.
Zero `E8`, zero decoded `E9`. Incoming `ecx` unused.

```
00538380  8b 44 24 04        mov eax, [esp+4]           ; args object
00538384  8b 08              mov ecx, [eax]             ; element 1
00538386  8b 11              mov edx, [ecx]
00538388  ff 52 34           call [edx+0x34]            ; float eval
0053838b  d9 1d 8c 01 66 00  fstp [0x66018c]            ; snow density cell
00538391  c2 0c 00           ret 0xc
```

Boundary: thirteen `nop` (`0x00538392`–`0x005383a0`) then native 45
`SetLightningDensity`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[args+0]` | one script element via `vtable[+0x34]` (float) | `0x00538388` |
| `0x0066018c` | global snow-density float | `0x0053838b` |
| `0x64d920` / `0x64d950` | registration descriptor name/handler cells | `0x00530f41`, `0x00530ece` |

## Readers of `0x0066018c` (consumer evidence, both pinned this wake)

1. Particle-count law at `0x005555ba`: `fld [0x66018c]; fmul
   [0x5d8c54]; fistp qword` → integer count; clamp `cmp eax, 0x3e8;
   jle keep; mov eax, 0x3e8` — density scales a spawned count with a
   hard ceiling of 1000. The multiplier constant at `.rdata
   0x005d8c54` was not re-derived to an exact decimal this wake
   (recorded unknown).
2. Second consumer at `0x00555633`: another `fld [0x66018c]` site in
   the same module (window recorded; full semantics not chased).

Together with `Atmospherics__Init`'s zero store (`0x00404a4f`) and the
`atm_snowdensity` CVar binding (`push 0x66018c` at `0x00404b39`),
this is the most completely witnessed cell of the quartet.

## Callers

Zero rel32 inbound; dispatch-table-only. Corpus 0 authored sites /
0 levels.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core atmospherics owner yet. When one lands: snow density is a
single global float, default 0 per level, retail range 0–1, consumed
as `(int)(density × k)` capped at 1000 for particle spawning. Focused
test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00538380`–`0x00538391` is not
  `d264ac61…9cdef`, or the body does not end
  `d9 1d 8c 01 66 00 c2 0c 00`.
- Any direct `E8` appears, or the store target is anything but
  `0x0066018c`.
- A second image-wide imm32 of `0x00538380` exists.
- The count clamp stops being `0x3e8` (1000) at `0x005555ce`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 body disassembly,
  raw byte reads (body hash; imm32 census: exactly one site at
  `0x00530ec0`; descriptor walk), whole-`.text` rel32 xref scan,
  reader windows `0x0055559c`–`0x005555dc`, `0x00555610`–
  `0x00555650`, Atmospherics windows (`local-lab/famB_reg.py`,
  `local-lab/famB_consumers.py`).
- Cross-reference (same wake):
  [`IScript__SetWindVector.md`](IScript__SetWindVector.md),
  [`IScript__SetRainDensity.md`](IScript__SetRainDensity.md),
  [`IScript__SetLightningDensity.md`](IScript__SetLightningDensity.md).
