# IScript__SetLightningDensity

> Address: `0x005383a0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetLightningDensity` and the `atm_lightningdensity`
console variable are absent from `references/Onslaught/` (checked
2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 45, registered as `SetLightningDensity`: one
float expression through element `vtable[+0x34]`, stored into the
global lightning-density cell `0x00660188`. That cell is the
`atm_lightningdensity` console variable ("Lightning density (0-1)"),
zeroed per level by `Atmospherics__Init`. No shipped mission calls it
(`DORMANT_CANDIDATE` 0/0).
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly, raw byte reads (body hash; image-wide imm32 census;
descriptor walk), rel32 xref scan, and consumer-side windows. No
`FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

`mission-native-corpus-coverage-2026-08-15.tsv` row 45 is
`SetLightningDensity` / `0x005383A0` / `IScript__SetLightningDensity`
in the corpus's name column / 0 authored sites / 0 levels /
`DORMANT_CANDIDATE`. The **current** saved table row for `0x005383a0`
is empty (unnamed handler); this note does not rename anything and
records the discrepancy. Registration:

- Handler immediate: `mov edi, 0x005383a0` (`bf a0 83 53 00`) at VA
  `0x00530ee2` — exactly **one** image-wide imm32 of `0x005383a0`.
- Handler cell store: `mov [0x64d990], edi` at VA `0x00530eed`.
- Name-pointer store: `mov dword ptr [0x64d960], 0x64f7e4` at VA
  `0x00530f84`; `.rdata 0x64f7e4` is `"SetLightningDensity\0"`.
- Descriptor: name cell `0x64d960`, handler cell +0x30 at
  `0x64d990`.

## Contract (byte-exact)

Body `0x005383a0`–`0x005383b1` inclusive through the complete
`ret 0xc`, **18 bytes**, SHA-256
`d96c561015d344bc59677521a4234ed44340ba544d00307e945ddd05cc999806`.
Zero `E8`, zero decoded `E9`. Incoming `ecx` unused.

```
005383a0  8b 44 24 04        mov eax, [esp+4]           ; args object
005383a4  8b 08              mov ecx, [eax]             ; element 1
005383a6  8b 11              mov edx, [ecx]
005383a8  ff 52 34           call [edx+0x34]            ; float eval
005383ab  d9 1d 88 01 66 00  fstp [0x660188]            ; lightning density cell
005383b1  c2 0c 00           ret 0xc
```

Tail context: `ret 0xc` at `0x005383b1` is immediately followed by
native 5 (`PostEvent`) territory at `0x005383c0` — no pad bytes; the
quartet's last member ends flush against the next reservation.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[args+0]` | one script element via `vtable[+0x34]` (float) | `0x005383a8` |
| `0x00660188` | global lightning-density float | `0x005383ab` |
| `0x64d960` / `0x64d990` | registration descriptor name/handler cells | `0x00530f84`, `0x00530eed` |

## Consumers of `0x00660188`

- `Atmospherics__Init`: zeroed (`mov [0x660188], 0` at `0x00404a57`)
  in the seven-cell weather clear.
- `Atmospherics__ResetAndUpdate`: bound as `atm_lightningdensity`
  ("Lightning density (0-1)", `.rdata 0x00622dd8/f0`, type 4) via
  `CConsole__RegisterVariable` at `0x00404b58`.
- One additional code reference at `0x00404b59` (the CVar push
  itself). Unlike snow, no render-side reader was pinned this wake —
  honest unknown: which system consumes the lightning value.

## Callers

Zero rel32 inbound; dispatch-table-only. Corpus 0 authored sites /
0 levels.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core atmospherics owner yet. When one lands: lightning density is
a single global float, default 0 per level, retail range 0–1, shared
between the console variable and Mission native 45. Focused test
deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005383a0`–`0x005383b1` is not
  `d96c5610…99806`, or the body does not end
  `d9 1d 88 01 66 00 c2 0c 00`.
- Any direct `E8` appears, or the store target is anything but
  `0x00660188`.
- A second image-wide imm32 of `0x005383a0` exists.
- `.rdata 0x64f7e4` stops being `"SetLightningDensity\0"`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 body disassembly,
  raw byte reads (body hash; imm32 census: exactly one site at
  `0x00530ee3`; descriptor walk), whole-`.text` rel32 xref scan,
  Atmospherics windows (`local-lab/famB_reg.py`,
  `local-lab/famB_consumers.py`).
- Cross-reference (same wake):
  [`IScript__SetWindVector.md`](IScript__SetWindVector.md),
  [`IScript__SetRainDensity.md`](IScript__SetRainDensity.md),
  [`IScript__SetSnowDensity.md`](IScript__SetSnowDensity.md).
