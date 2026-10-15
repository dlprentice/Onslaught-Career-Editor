# IScript__SetVar

> Address: `0x005348f0`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/thing.h:294` / `thing.cpp:827-829` (the
callee's virtual; the wrapper itself is absent from the pinned source) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 68, registered as `SetVar`, is the one native in
the 68/76/77/78/81 "variable" name group whose name is **true**: it
forwards its two expression-stack element objects unevaluated to a virtual
at slot `[+0xf8]` on `[incoming-ecx + 0x10]` — the dispatcher-context
object's named-variable-store method (`CComplexThing::SetVar` in the
pinned source), not any world-singleton call. Its siblings 76/77/81 are
the CWorld four-slot message/timer system (see the sibling notes); 68 does
not touch that store.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 above,
verified before reading) with `tools/disasm_va.py` (whole body),
raw byte reads (body hash, imm32 census, string table, registration
block). No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding (name vs. behavior)

`mission-native-corpus-coverage-2026-08-15.tsv` row 68 is
`SetVar` / `0x005348F0` / `FUN_005348f0` / 56 authored sites / 4 levels /
`OBSERVED`; the current saved symbol in
`ghidra-function-name-table-2026-08-17.tsv` is `IScript__SetVar`
(boundary `0x005348f0`–`0x0053490a`). Both confirmed this wake. The
family split first established by the natives 76–78 and 81 notes is here
completed with the opposite sign:

- Natives 76 `InitVariable` / 77 `SetVariable` / 81 `GetVariable` carry
  variable names but drive the CWorld four-slot world-message/timer
  store; their names are retail-authentic labels whose handlers do
  something else.
- Native 68 `SetVar` carries a variable name **and** performs variable
  storage: it forwards `(element1, element2)` raw to
  `receiver->vtable[+0xf8]`, which the pinned source declares as
  `virtual void CComplexThing::SetVar(CStringDataType* name,
  CDataType* data)` (`thing.h:294`). The base implementation's warning —
  `"Warning: Uknown var '%s' in call to SetVar"` (typo in the original) —
  sits embedded at `.rdata` `0x00633210` (file `0x233210`) next to RTTI
  `.?AVCMCThunderHead@@`, matching `thing.cpp:827-829`.

Any rebuild that treats 68 as part of the world-message system would be
false to the shipped game; any rebuild that treated all five "variable"
names as one script-variable map would be false to both halves.

## Contract (byte-exact)

One stack argument `IScript* vm` at `[esp+4]` like its siblings, but this
wrapper alone **uses the incoming `ecx`** (the Mission dispatcher's
`this`) and alone forwards element objects without evaluating them. Body
`0x005348f0`–`0x0053490a` inclusive through the complete `ret 0xc`,
**27 bytes**, SHA-256
`ae1f3cdca13337a2bc41cc9a83e19119e436f8e22a323cc9841e2456d25878cc`
(the sealed C1 row tsv:4822 windows the same body differently — 11
instructions ending at `0x0053490a`, body hash `34fbc2c1…17c12`; both
windows end on the same `ret 0xc`). No direct `E8` inside the wrapper.

```
005348f0  8b 44 24 04        mov eax, [esp+4]           ; IScript* vm
005348f4  8b 49 10           mov ecx, [ecx+0x10]        ; receiver from INCOMING ecx
005348f7  56                 push esi
005348f8  8b 70 04           mov esi, [eax+4]           ; element object 2
005348fb  8b 00              mov eax, [eax]             ; element object 1
005348fd  8b 11              mov edx, [ecx]             ; receiver vtable
005348ff  56                 push esi                   ; arg2 = element object 2, UNEVALUATED
00534900  50                 push eax                   ; arg1 = element object 1, UNEVALUATED
00534901  ff 92 f8 00 00 00  call dword ptr [edx+0xf8]  ; receiver->SetVar(elem1, elem2)
00534907  5e                 pop esi
00534908  c2 0c 00           ret 0xc                    ; dispatcher's 3-dword frame
0053490b  90 x5              nop pad to 0x00534910 (native 66 CreatePosition)
```

1. `eax = [esp+4]` (vm); `ecx = [ecx+0x10]` — receiver taken from the
   incoming dispatcher context, not loaded from an immediate global.
2. Element objects 1 and 2 are read off the VM expression stack
   (`[vm+0]`, `[vm+4]`) and pushed **as pointers, unevaluated** — no
   `vtable[+0x30]` scalar or `[+0x34]` float dispatch appears anywhere in
   the wrapper.
3. Virtual call through receiver vtable displacement `+0xf8` with the two
   element pointers as stack arguments; the callee owns evaluation and
   storage (per the pinned source signature, element 1 supplies the
   variable *name*, element 2 the data).
4. `pop esi; ret 0xc`. Trailing NOP pad to the next native.

## Registration (name ↔ handler binding)

- Handler immediate: `bd f0 48 53 00` (`mov ebp, 0x005348f0`) at VA
  `0x0053179f` / file `0x13179f` (immediate at file `0x1317a0`).
  Exactly **one** image-wide imm32 of `0x005348f0` exists — this site;
  the wrapper has no other image reference.
- Name-pointer store: `c7 05 20 df 64 00 a8 f6 64 00`
  (`mov dword ptr [0x64df20], 0x64f6a8`) at VA `0x00531828` /
  file `0x131828` (name immediate at file `0x13182e`), in the same
  descriptor-initialization block that seeds the neighboring globals.
- Name string: `SetVar\0` at `.rdata` `0x0064f6a8` (file `0x24f6a8`),
  continuing the descending-corpus-index run pinned by the 76–78 note:
  `GameTime(70) 0x64f694 · Damage(69) 0x64f6a0 · SetVar(68) 0x64f6a8 ·
  GetFloatRand(67) 0x64f6b0 · CreatePosition(66) 0x64f6c0 ·
  GetComponent(65) 0x64f6d0`.
- Sibling handler immediates either side of the same block:
  `mov ebp, 0x00538290` (67 GetFloatRand) at file `0x131780`;
  `mov ebp, 0x005348c0` (69 Damage) at file `0x1317be`;
  `mov ebp, 0x00534770` (70 GameTime) at file `0x1317dd`.

Name↔handler binding is therefore image-internal: the game's own
registration ties the `SetVar` label to `0x005348f0`.

## Callers

Zero rel32 `E8` inbound to `0x005348f0` is expected (dispatch is by
registration immediate only); the complete imm32 census above is the
positive evidence, and `tools/call_xref_scan.py <image> 0x005348f0`
returning nothing is the standing falsifier. The corpus counts 56
authored mission call sites over 4 levels (`OBSERVED`).

## Pinned-source status

The wrapper itself is absent from `references/Onslaught/` (no IScript
native table survives there), but its callee is fully sourced:
`thing.h:294` declares the virtual
`void SetVar(CStringDataType* name, CDataType* data)` and
`thing.cpp:827-829` shows the base body logging
`"Warning: Uknown var '%s' in call to SetVar"` for unknown names — the
exact string embedded at `0x00633210` in the specimen. Agreement, not
divergence: the retail bytes implement the source's per-thing named
variable store. What the bytes add beyond the source is the ABI: which
receiver (`[ecx+0x10]`), which vtable slot (`+0xf8`), and that arguments
arrive as unevaluated VM element objects the callee must evaluate.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| incoming `ecx+0x10` | receiver object carrying the variable store (dispatcher context member) | `0x005348f4` |
| `vm+0x00` / `vm+0x04` | expression-stack element objects 1/2 (forwarded raw) | `0x005348fb` / `0x005348f8` |
| receiver `vtable[+0xf8]` | the `SetVar(name, data)` virtual | call `0x00534901` |
| `.rdata 0x00633210` | base-class unknown-variable warning string | file `0x233210` |

## Rebuild mapping

Nearest reconstruction owner: **none added.** Core has no per-thing
named-variable model (`grep SetVar` over `rebuild/` returns nothing), and
Level 100's exact-set command runtime never issues these Mission natives.
What a future owner needs if another level's program is reconstructed: a
name-keyed store living on the thing that receives the script context
(not on any world singleton), populated through the same path the pinned
source shows — set-by-name with a logged miss for unknown names — plus
whatever reader side the getters use. This native must NOT be routed into
the future CWorld message/timer owner that natives 76/77/81 imply, and
vice versa. Per lane rules no Core file was edited from this RE root; the
focused-test step is deferred until such an owner exists.

Corpus correction requested (not self-applied — the TSV lives outside
this lane's ownership): row 68 should cross-reference this note; unlike
rows 76–78, its behavior label needs **no** correction.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005348f0`–`0x0053490a` is not
  `ae1f3cdc…78cc`, or the body does not end `5e c2 0c 00`.
- Any `call dword ptr [reg+0x30]` or `[reg+0x34]` element evaluation
  appears inside the wrapper (it must contain none — elements go through
  unevaluated).
- The dispatch displacement is anything but `[edx+0xf8]`, or the receiver
  load is anything but `mov ecx, [ecx+0x10]` from the incoming `ecx`.
- A second image-wide imm32 of `0x005348f0` exists, or the registration
  pair (`mov ebp` at file `0x13179f`, name-pointer store at file
  `0x131828`) moves apart.
- The string at `.rdata` `0x00633210` is not the
  `Uknown var '%s' in call to SetVar` warning, or `thing.cpp:827` stops
  matching it.
- `tools/call_xref_scan.py` returns any rel32 caller of `0x005348f0`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: `tools/disasm_va.py` (full wrapper
  body; neighbor heads `0x005348c0` Damage and `0x00534910`
  CreatePosition to confirm boundaries), raw byte reads (body hash;
  `.rdata` string window `0x24f660`–`0x24f6e0`; registration block
  disassembly `0x00531795`–`0x00531840`; warning-string read at file
  `0x233210`; image-wide imm32 census of `0x005348f0`: exactly one site
  at VA `0x005317a0`).
- Measurement dossier: run 697 pre-measured every value above before this
  note was written — see
  `local-lab/hermes-kanban-campaign-2026-08-22/setvar-68-dossier-run697.md`
  (untracked lab evidence; the tracked record is this note).
- Cross-reference (same wake, independently consistent): the sibling
  notes `IScript__InitVariable_SetVariable_ShutdownVariable.md`
  (natives 76–78 → CWorld text-slot store) and `IScript__GetVariable.md`
  (native 81 → `CWorld__GetWorldTextSlotTimerValue` via `0x0050d760`)
  establish the family split this note completes; the GetVariable note's
  registration sites (`0x00531c9c`/`0x00531ca1`) were re-derived
  independently by this wake's reads and agree.
- Coverage corpus cross-reference:
  `mission-native-corpus-coverage-2026-08-15.tsv` row 68 (indices/names/
  authored counts/disposition confirmed unchanged by this note).
