# IScript__SetSegmentHealth

> Address: `0x00535480`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SetSegmentHealth`, the segments controller behind
`[thing+0x178]`, and the `DestructableSegmentsController.cpp` debug-path
string (`.rdata 0x006287c6`) have no source body in `references/Onslaught/`
(checked 2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 51, registered as `SetSegmentHealth`: the
by-name segment-health writer. Gate prologue (attached thing is UNIT
class, `[thing+0x178]` controller live), then `element[1]` evaluates a
float through `vtable[+0x34]`, `element[0]` fetches a `char*` through
`vtable[+0x38]`, and the controller call `0x00444450(name, value)`
resolves the segment by name and stores the value into the segment's
health cell `+0xc`. All authored uses are the level530 hive boss.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
verified before reading) with capstone whole-body disassembly, raw byte
reads (body hash; image-wide imm32 census; descriptor-cell walk),
whole-`.text` rel32 xref scan, consumer windows, and authored `.msl`
site counts (`local-lab/famD_measure.py`, `famD_callees.py`,
`famD_reg*.py`, `famD_msl*.py`). Cross-checked against
[`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
and the W003 full-pass notes; corrections recorded below. No `FUN_*`
milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

`mission-native-corpus-coverage-2026-08-15.tsv` row 51 is
`SetSegmentHealth` / `0x00535480` / empty name-table cell / 27 authored
sites. Confirmed this wake; the handler is unnamed in the current saved
table and this note renames nothing. Registration:

- Handler immediate: `mov ebp, 0x00535480` (`bd 80 54 53 00`) at VA
  `0x005310b4` — exactly **one** image-wide imm32 of `0x00535480`
  (byte hit at `0x005310b5`). Zero rel32 inbound (`E8`/`E9`).
- Handler cell store: `mov [0x64db10], ebp` at VA `0x005310c5`.
- Name-pointer store: `mov dword ptr [0x64da20], 0x64f7b4` at VA
  `0x005310dd`; `.rdata 0x64f7b4` is `"SetScript\0"` — native 48's
  descriptor, two strides back, which corroborates the 0x40-stride law:
  name cells 0x64da20 (48) → 0x64dae0 (**51**, `"SetSegmentHealth\0"`
  at `.rdata 0x64f788`) with one descriptor apiece for 49/50 between.
- Descriptor: name cell `0x64dae0`, handler cell +0x30 at `0x64db10`.

## Contract (byte-exact)

Body `0x00535480`–`0x005354ba` inclusive through the complete
`ret 0xc`, **59 bytes**, SHA-256
`2957c3e9133eeb1603c646b9483866f2d20b77a4f6aa1f2a56a21b1c34dba707`.
One `E8`, zero decoded `E9`.

```
00535480  8b 41 10           mov eax, [ecx+0x10]        ; attached thing
00535483  57                 push edi
00535484  f6 40 34 10        test byte [eax+0x34], 0x10 ; UNIT class bit
00535488  74 2d              je 0x5354b7                ; -> bare return
0053548a  8b b8 78 01 00 00  mov edi, [eax+0x178]       ; segments controller
00535490  85 ff              test edi, edi
00535492  74 23              je 0x5354b7
00535494  8b 44 24 08        mov eax, [esp+8]           ; args object
00535498  56                 push esi
00535499  8b 48 04           mov ecx, [eax+4]           ; element 2 (health)
0053549c  8b 30              mov esi, [eax]             ; element 1 (name)
0053549e  8b 01              mov eax, [ecx]
005354a0  ff 50 34           call [eax+0x34]            ; float eval -> st0
005354a3  8b 16              mov edx, [esi]
005354a5  51                 push ecx                   ; value slot
005354a6  8b ce              mov ecx, esi
005354a8  d9 1c 24           fstp dword ptr [esp]       ; store the float
005354ab  ff 52 38           call [edx+0x38]            ; char* name -> eax
005354ae  50                 push eax                   ; arg: name
005354af  8b cf              mov ecx, edi               ; this = controller
005354b1  e8 9a ef f0 ff     call 0x00444450            ; (name, value)
005354b6  5e                 pop esi
005354b7  5f                 pop edi
005354b8  c2 0c 00           ret 0xc
```

Boundary: five `nop` then native 134 `ResetSegmentHealth` at
`0x005354c0` (same prologue); the pair shares the descriptor block with
`SetPos`/`SpawnParticle` ahead and `SetAllSegmentsHealth` behind.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing | `0x00535480` |
| `[thing+0x34]` byte bit `0x10` | UNIT class gate | `0x00535484` |
| `[thing+0x178]` | segments controller | `0x0053548a` |
| `args[0]` via `vtable[+0x38]` | `char*` segment name | `0x005354ab` |
| `args[1]` via `vtable[+0x34]` | float health value | `0x005354a0` |
| `0x64dae0` / `0x64db10` | registration descriptor name/handler cells | `0x005310dd`, `0x005310c5` |

## The gate law and `[thing+0x178]`

All five segment natives (51, 52, 134, 109, 110) open with the identical
gate above. The type bit is the same `mThingType & 0x10` UNIT test the
[`IScript.cpp.md`](../IScript.cpp.md) map records for `CComplexThing__HandleEvent`.
`[thing+0x178]` is the field `CUnit__ApplyDamage`
([`../Unit.cpp/CUnit__ApplyDamage.md`](../Unit.cpp/CUnit__ApplyDamage.md))
forwards segment damage through. Whole-`.text` census this wake: exactly
eight accesses of the field — five are these natives' reads, three are
the sibling getter thunks `0x004f99f2` / `0x004f9a12` / `0x004f9a42`;
**no writer exists** in `.text` in either imm or register store form,
so the controller is installed outside `.text` (or by a form this
census cannot see). Honest unknown: who constructs the controller and
when.

## Controller dispatch — `0x00444450` `(name, value)` (byte-exact)

`thiscall`, `ret 8`; unnamed in the live table (W003 labels it
`CDestructableSegmentsController__SetSegmentField0CByName`; see the
spelling correction below). Gates `[this+0x10]` (an owner link inside
the controller) → `[[that]+0x30]` → its `vtable[+0x24]()` must return
nonzero — the name-list carrier. Then:

```
00444467  mov edi, [esp+0xc]      ; arg1 = char* name
0044446b  mov ecx, eax            ; carrier
0044446d  push edi
0044446e  call 0x004aa8a0         ; lookup-by-name -> entry or 0
00444473  test eax, eax; je ret
00444477  mov eax, [eax+0x88]     ; entry -> segment INDEX
0044447d  mov ecx, [esi+4]        ; controller segment-pointer array
00444480  mov eax, [ecx+eax*4]    ; segment object
00444483  test eax, eax; je ret
00444487  mov edx, [esp+0x10]     ; arg2 = float value
0044448c  mov [eax+0xc], edx      ; SEGMENT HEALTH CELL
```

- `0x004AA8A0` (`ret 4`, arg `char*`): walks `[carrier+0x15c]` entries
  at `[carrier+0x160]`, `stricmp` (`0x00568390`) of `entry+0xdc` vs the
  name; first equal wins, else 0. Six inbound `E8`: the four ByName
  callees of this family plus `0x0049f914`/`0x004a0161` (not walked).
- Segment cell `+0xc` is the same cell
  [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
  calls "current damage/health-scale state"; this native is a pure
  script-driven writer of it.
- Authored ABI witness: `level530/hive.msl`
  `SetSegmentHealth("core2", core_health)` — 27 active sites, that one
  file (recounted this wake from the pristine data tree; matches the
  corpus TSV).

## Consumers (why rebuild cares)

The script-visible health getters consume the same cells this native
writes: native 18 `GetHealth` (`0x00535920`) calls thunk `0x004f99f0`
directly, native 111 `GetRealHealth` (`0x005359d0`) calls `0x004f9a40`;
both thunks test `[thing+0x178]` and forward to controller getters at
`0x00444330`/`0x00444370`/`0x004443b0` (all-segments checks, recursive
sums `0x00442890`/`0x00442900`, cached `[controller+0x18]`). Controller
layout observed: `+4` segment array, `+8` count, `+0xc` root segment,
`+0x10` owner link, `+0x18` cached total.

## Callers

Zero rel32 inbound; dispatch-table-only. 27 authored sites, level530
hive only.

## Pinned-source status

Absent. No `IScript.cpp`, no `DestructableSegmentsController.cpp` body;
only the debug-path string survives in `.rdata`.

## Prior-art corrections recorded by this note

- RTTI spelling: the specimen's TypeDescriptors are
  `.?AVCDestroyableSegment@@` (`0x00628570`),
  `.?AVCDestroyableCoreSegment@@` (`0x006285f0`),
  `.?AVCDestroyableSwapSegment@@` (`0x00628818`). **No**
  `CDestructable…` TypeDescriptor exists; the "Destructable" spelling
  in older prose (and the `.cpp` debug string itself) does not match
  the RTTI. Existing saved names are cited here as-is, not renamed.
- [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
  gains concrete controller fields `+4`/`+8` (array/count) from the
  dispatch read above; its segment `+0xc` row is confirmed as the
  direct store target of this native.

## Rebuild mapping

No Core owner for the segments-controller slice yet
(`Level100Destruction.cs` tracks per-actor health bits — a different
slice). When one lands: name-indexed write of a float into
`segment.health`, gated on UNIT class and controller presence; the
damage-side consumption of that cell is runtime behavior this static
note does not prove. Focused test deferred until the owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535480`–`0x005354ba` is not
  `2957c3e9…dba707`, or the dispatch target is anything but
  `0x00444450`.
- A second image-wide imm32 of `0x00535480` appears, or any rel32
  inbound to the native.
- The handler store leaves `0x64db10`, or `.rdata 0x64f788` stops
  being `"SetSegmentHealth\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads (body hashes; imm32 census: one site at `0x005310b5`;
  descriptor-cell walk; `[reg+0x178]` reader/writer census), whole-
  `.text` rel32 xref scan, authored `.msl` recount
  (`local-lab/famD_measure.py`, `famD_callees.py`, `famD_reg.py`,
  `famD_reg2.py`, `famD_reg3.py`, `famD_msl3.py`).
- Cross-reference (same wake):
  [`IScript__SetAllSegmentsHealth.md`](IScript__SetAllSegmentsHealth.md),
  [`IScript__ResetSegmentHealth.md`](IScript__ResetSegmentHealth.md),
  [`IScript__SetSegmentVulnerable.md`](IScript__SetSegmentVulnerable.md),
  [`IScript__SetAllSegmentsVulnerable.md`](IScript__SetAllSegmentsVulnerable.md).
