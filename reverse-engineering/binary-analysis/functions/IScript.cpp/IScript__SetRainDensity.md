# IScript__SetRainDensity

> Address: `0x00538360`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetRainDensity` and the `atm_raindensity` console
variable are absent from `references/Onslaught/` (checked 2026-08-22) |
Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 43, registered as `SetRainDensity`: the
smallest kind of native — one float expression evaluated through
element `vtable[+0x34]`, stored with a single `fstp` into the global
rain-density cell `0x00660190`. That cell is simultaneously the
`atm_raindensity` console variable ("Rain density (0-1)") registered
by `Atmospherics__ResetAndUpdate`, zeroed per level by
`Atmospherics__Init`, and read by the weather render path. No shipped
mission calls it (`DORMANT_CANDIDATE` 0/0).
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly, raw byte reads (body hash; image-wide imm32 census;
descriptor-cell walk), rel32 xref scan, and consumer-side windows. No
`FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

`mission-native-corpus-coverage-2026-08-15.tsv` row 43 is
`SetRainDensity` / `0x00538360` / empty name-table cell / 0 authored
sites / 0 levels / `DORMANT_CANDIDATE`; confirmed this wake. The
handler is unnamed in the current saved table; this note does not
rename anything. Registration:

- Handler immediate: `mov edi, 0x00538360` (`bf 60 83 53 00`) at VA
  `0x00530ea1` — exactly **one** image-wide imm32 of `0x00538360`.
- Handler cell store: `mov [0x64d910], edi` at VA `0x00530eab`.
- Name-pointer store: `mov dword ptr [0x64d8e0], 0x64f808` at VA
  `0x00530ec4`; `.rdata 0x64f808` is `"SetRainDensity\0"`.
- Descriptor: name cell `0x64d8e0`, handler cell +0x30 at
  `0x64d910` — the shared 0x40-stride layout pinned in the quartet.

## Contract (byte-exact)

Body `0x00538360`–`0x00538371` inclusive through the complete
`ret 0xc`, **18 bytes**, SHA-256
`06d4436759f4daab19a1572e47c504fd452f62086973e8c286a3b277ac3e915e`.
Zero `E8`, zero decoded `E9`. Incoming `ecx` unused.

```
00538360  8b 44 24 04        mov eax, [esp+4]           ; args object
00538364  8b 08              mov ecx, [eax]             ; element 1
00538366  8b 11              mov edx, [ecx]
00538368  ff 52 34           call [edx+0x34]            ; float eval
0053836b  d9 1d 90 01 66 00  fstp [0x660190]            ; rain density cell
00538371  c2 0c 00           ret 0xc
```

Boundary: thirteen `nop` (`0x00538372`–`0x00538380`) then native 44
`SetSnowDensity` — the widest inter-native pad in the corpus run,
matching each body's 16-byte-aligned reservation.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[args+0]` | one script element via `vtable[+0x34]` (float) | `0x00538368` |
| `0x00660190` | global rain-density float | `0x0053836b` |
| `0x64d8e0` / `0x64d910` | registration descriptor name/handler cells | `0x00530ec4`, `0x00530eab` |

## Consumers of `0x00660190`

- `Atmospherics__Init`: zeroed (`mov [0x660190], 0` at `0x00404a45`)
  as part of the seven-cell weather clear.
- `Atmospherics__ResetAndUpdate`: bound as the `atm_raindensity`
  console variable ("Rain density (0-1)", `.rdata 0x00622e2c/3c`,
  type 4 = float) via `CConsole__RegisterVariable` at `0x00404b1f`
  — the native and the console write the same cell.
- This wake found **no** reader window decoding it in the sampled
  consumer regions (unlike snow's two `fld` sites); its consumption
  is claimed only through the CVar binding and init clear, not
  through a pinned reader. Honest unknown: which render code loads
  the rain cell.

## Callers

Zero rel32 inbound; dispatch-table-only. Corpus 0 authored sites /
0 levels.

## Pinned-source status

Absent from the pinned source, like its three siblings.

## Rebuild mapping

No Core atmospherics owner yet. When one lands: rain density is a
single global float, default 0 per level, range documented by retail
help text as 0–1, shared between the console variable and Mission
native 43. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00538360`–`0x00538371` is not
  `06d44367…e915e`, or the body does not end
  `d9 1d 90 01 66 00 c2 0c 00`.
- Any direct `E8` appears, or the store target is anything but
  `0x00660190`.
- A second image-wide imm32 of `0x00538360` exists.
- `.rdata 0x64f808` stops being `"SetRainDensity\0"`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 body disassembly,
  raw byte reads (body hash; imm32 census: exactly one site at
  `0x00530ea2`; descriptor walk), whole-`.text` rel32 xref scan,
  Atmospherics/consumer windows (`local-lab/famB_reg.py`,
  `local-lab/famB_consumers.py`).
- Cross-reference (same wake):
  [`IScript__SetWindVector.md`](IScript__SetWindVector.md),
  [`IScript__SetSnowDensity.md`](IScript__SetSnowDensity.md),
  [`IScript__SetLightningDensity.md`](IScript__SetLightningDensity.md).
