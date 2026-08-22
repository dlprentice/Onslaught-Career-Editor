# IScript__SetWindVector

> Address: `0x00538300`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetWindVector` and the `atm_windvector` console variable are absent from `references/Onslaught/` (checked 2026-08-22) | | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 42, registered as `SetWindVector`, writes the
global wind vector — a **four-float** record, not three. It float-
evaluates three script expressions through element `vtable[+0x34]`
(in reverse order) and stores them to the global cells
`0x00660198/0x66_019c/0x66_01a0` in natural element order; the fourth
cell `0x006601a4` is written from the wrapper's saved-`esi` slot, so a
mission calling this native sets the fourth wind component to the
Mission dispatcher's caller-context `esi` — an unscripted value. The
four cells are read together by the wind-speed consumers (norm-shaped
math over all four), are bound to the `atm_windvector` console
variable registered by `Atmospherics__ResetAndUpdate` (which binds at
cell 1), and three of them are zeroed per level by
`Atmospherics__Init`. No shipped mission calls it (`DORMANT_CANDIDATE`
0/0).
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famB_weather.py` output), raw byte reads (body
hash; image-wide imm32 census; descriptor-cell walk), rel32 xref scan,
and consumer-side disassembly (`local-lab/famB_consumers.py`). No
`FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

`mission-native-corpus-coverage-2026-08-15.tsv` row 42 is
`SetWindVector` / `0x00538300` / empty name-table cell / 0 authored
sites / 0 levels / `DORMANT_CANDIDATE`; confirmed this wake. The
current saved symbol for the handler in
`ghidra-function-name-table-2026-08-17.tsv` is empty (unnamed); this
note does not rename anything. Registration is confirmed image-internally:

- Handler immediate: `mov edi, 0x00538300` (`bf 00 83 53 00`) at VA
  `0x00530d58` — exactly **one** image-wide imm32 of `0x00538300`.
- Handler cell store: `mov [0x64d8d0], edi` at VA `0x00530d62`.
- Name-pointer store: `mov dword ptr [0x64d8a0], 0x64f818` at VA
  `0x00530e53`; `.rdata 0x64f818` is `"SetWindVector\0"`.
- Descriptor stride: name cells sit 0x40 bytes apart across the
  weather run (`0x64d860 SetAllegiance(41)` → `0x64d8a0` → `0x64d8e0`
  → `0x64d920` → `0x64d960`), with each handler cell exactly +0x30
  from its name cell.

## Contract (byte-exact)

Body `0x00538300`–`0x0053835d` inclusive through the complete
`ret 0xc`, **94 bytes**, SHA-256
`3cf457a3c28998b322680312e63604cc261ff3a47c3983040c3e95ca59540c0d`.
Zero `E8`, zero decoded `E9` — the wrapper makes **no calls**: every
dispatch is a computed virtual `call [reg+0x34]`. Incoming `ecx` is
unused. One stack argument: the vm/args object at `[esp+4]`, whose
`[+0]`,`[+4]`,`[+8]` are three script-expression elements.

```
00538300  83 ec 14           sub esp, 0x14
00538303  56                 push esi
00538304  8b 74 24 1c        mov esi, [esp+0x1c]        ; args object
00538308  8b 4e 08           mov ecx, [esi+8]           ; element 3
0053830b  8b 01              mov eax, [ecx]
0053830d  ff 50 34           call [eax+0x34]            ; float eval
00538310  8b 4e 04           mov ecx, [esi+4]           ; element 2
00538313  d9 5c 24 04        fstp [esp+4]
00538317  8b 11              mov edx, [ecx]
00538319  ff 52 34           call [edx+0x34]            ; float eval
0053831c  8b 0e              mov ecx, [esi]             ; element 1
0053831e  d9 5c 24 1c        fstp [esp+0x1c]
00538322  8b 01              mov eax, [ecx]
00538324  ff 50 34           call [eax+0x34]            ; float eval
00538327  8b 4c 24 1c        mov ecx, [esp+0x1c]        ; e1 value
0053832b  8b 54 24 04        mov edx, [esp+4]           ; e2 value
0053832f  d9 5c 24 08        fstp [esp+8]               ; e3 value
00538333  8b 44 24 08        mov eax, [esp+8]
00538337  89 4c 24 0c        mov [esp+0xc], ecx
0053833b  a3 98 01 66 00     mov [0x660198], eax        ; cell1 = e3
00538340  8b 44 24 14        mov eax, [esp+0x14]
00538344  89 54 24 10        mov [esp+0x10], edx
00538348  89 0d 9c 01 66 00  mov [0x66019c], ecx        ; cell2 = e1
0053834e  89 15 a0 01 66 00  mov [0x6601a0], edx        ; cell3 = e2
00538354  a3 a4 01 66 00     mov [0x6601a4], eax        ; cell4 = stale slot!
00538359  5e                 pop esi
0053835a  83 c4 14           add esp, 0x14
0053835d  c2 0c 00           ret 0xc
```

Store mapping (traced slot by slot): evaluation runs in **reverse**
order (elements 3, 2, 1), staged through `[esp+4]`, then the arg slot
itself, then `[esp+8]`; the final loads reorder them back, so the
stores land in **natural** order — element 1 → `0x00660198`, element
2 → `0x0066019c`, element 3 → `0x006601a0`. The fourth store reads
`[esp+0x14]`, which is this wrapper's **own saved-`esi` slot** (the
`push esi` at `0x00538303` writes it; nothing overwrites it before
`0x00538340`) — so cell 4 receives the **caller-context `esi`**: the
Mission dispatcher's preserved register at dispatch time. It is not a
script-supplied value and not a zero; a mission calling this native
therefore sets the fourth wind component to whatever the interpreter
happens to hold in `esi`. HIGH on the four store sites and the
esi-spill mechanism; MEDIUM_STATIC on how downstream readers interpret
a nonzero cell 4 (all four cells participate in the consumer norm
math below).

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[args+0/+4/+8]` | three script elements, evaluated reverse order via `vtable[+0x34]` | `0x00538308`–`0x00538324` |
| `0x00660198 / 0x66_019c / 0x66_01a0` | wind-vector globals (cells 1–3) = elements 1/2/3 | `0x0053833b`, `0x00538348`, `0x0053834e` |
| `0x006601a4` | wind-cell 4 — written from the wrapper's saved-`esi` slot (caller-context value, never zeroed here) | `0x00538340`, `0x00538354` |
| `0x64d8a0` / `0x64d8d0` | registration descriptor: name pointer / handler cell (+0x30) | `0x00530e53`, `0x00530d62` |

## Readers of the same globals (consumer evidence)

- `Atmospherics__Init` zeroes six weather cells
  (`0x00660188`–`0x006601a0`, six `c7 05 …, 0` stores at
  `0x00404a25`–`0x00404a57`) — note `0x006601a4` is **not** in that
  clear list either.
- `Atmospherics__ResetAndUpdate` registers `atm_windvector`
  ("The prevailing wind vector", `.rdata 0x00622e50/60`) bound
  directly to cell `0x00660198` (`CConsole__RegisterVariable` at
  `0x00404afc`) — console edits and this native write the same
  memory.
- A physics/render consumer at `0x005031a0` loads cells 2/1 then
  3/4 and computes `sqrt((c2·c2+c1·c1)+(c3·c3+c4·c4))`-shaped sums —
  all four cells participate.
- A second consumer at `0x00555799` copies all four cells into a
  local structure followed by `0x41700000` (15.0f).

## Callers

Zero rel32 inbound (`E8`/`E9`, whole `.text` scan): reached only
through the Mission-native dispatch table via the handler-cell
immediate. Corpus counts 0 authored sites / 0 levels — registered but
never called by any shipped mission.

## Pinned-source status

Absent from the pinned source. The `atm_windvector` CVar string and
its help text are retail strings; nothing in `references/Onslaught/`
documents the native or the cells.

## Rebuild mapping

No Core owner models atmospherics yet (`Level100Terrain` owns terrain
only). When one lands: the wind vector must be a **4-component** float
record whose cells default to 0 (three explicitly cleared per level
init; the fourth only ever written by this native's saved-`esi` spill
or console edits), with `atm_windvector` binding to cell 1.
Implementing a 3-component vector, or a deterministic fourth
component, would diverge from the shipped bytes. Focused test
deferred until that owner exists (same recorded decision as natives
68/76–78/81/19).

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00538300`–`0x0053835d` is not
  `3cf457a3…40c0d`, or the body does not end `5e 83 c4 14 c2 0c 00`.
- Any direct `E8` appears in the body (there must be none).
- The three store immediates are anything but the recorded cells, or
  the cell-4 store stops sourcing `[esp+0x14]` (the saved-`esi`
  slot).
- A second image-wide imm32 of `0x00538300` exists.
- `.rdata 0x64f818` stops being `"SetWindVector\0"`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 body disassembly,
  raw byte reads (body hash; image-wide imm32 census of
  `0x00538300`: exactly one site at `0x00530d59`; name-string census;
  descriptor walk showing the 0x40 stride and +0x30 handler offset),
  whole-`.text` rel32 xref scan (zero callers),
  consumer-window disassembly (`local-lab/famB_consumers.py`),
  Atmospherics windows (`local-lab/famB_reg.py`).
- Cross-reference (same wake):
  [`IScript__SetRainDensity.md`](IScript__SetRainDensity.md),
  [`IScript__SetSnowDensity.md`](IScript__SetSnowDensity.md),
  [`IScript__SetLightningDensity.md`](IScript__SetLightningDensity.md)
  share the registration block and the Atmospherics cell block;
  [`../../cgame-level-lifecycle-semantics-2026-08-11.md`](../../cgame-level-lifecycle-semantics-2026-08-11.md)
  is unrelated but shares the specimen.
