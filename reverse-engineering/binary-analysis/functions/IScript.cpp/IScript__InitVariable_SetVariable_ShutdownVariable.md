# IScript natives 76–78 — `InitVariable` / `SetVariable` / `ShutdownVariable` drive the CWorld four-slot message store

> Addresses: `0x00536230` (`IScript__InitVariable`),
> `0x00536260` (`IScript__SetVariable`), and
> `0x00536330` (`IScript__ShutdownVariable`)

Status: active static function note
Last updated: 2026-08-22
Source File: none — these natives are absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the three Mission-script natives the coverage corpus labels
`InitVariable`(76) / `SetVariable`(77) / `ShutdownVariable`(78) do **not**
touch any script-variable store. Each wrapper evaluates its script
expressions through the standard element-vtable slots and then calls one
`CWorld` method on the world object at `0x00855090`: push a localized
text into a four-slot store (`0x0050d6a0`), set its two timings
(`0x0050d720`), or clear every slot carrying a text id (`0x0050d7a0`).
The retail names are the game's own string-table labels; their handlers'
behavior is the world-message system. Evidence: MEASURED — independently
read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
verified before reading) with `tools/disasm_va.py` (whole bodies),
raw byte reads (body hashes, imm32 census, string table), and
`tools/call_xref_scan.py`. Callee semantics corroborated by sealed
fullpass plates W008 primary A10/A11 and adversarial B10/B11 plus their
decompiles under `local-lab/ghidra-fullpass-2026-07-23/exports/W008/decompile/`.
No `FUN_*` milled; no Core owner invented.

## Headline finding (name vs. behavior)

`mission-native-corpus-coverage-2026-08-15.tsv` rows 76–78 carry the
names below with `currentGhidraName = FUN_*`; dispositions are
`OBSERVED` for 76 (77 authored sites / 21 levels) and 77 (146 / 18),
`AUTHORED_UNOBSERVED` for 78 (26 / 0). Those rows are confirmed this
wake, plus one correction to their implied reading:

- The **names** are retail-authentic: the strings sit consecutively in
  `.rdata` — `Shutdown(0x64f628) · ShutdownVariable(0x64f634) ·
  SetVariable(0x64f648) · InitVariable(0x64f654) · Surface(0x64f664) ·
  Dive…` around offset `0x24f628`–`0x24f674`, i.e. the run is laid down
  in **descending** corpus-index order (75 `Surface` … 80 `GetEnergy`
  reads upward) but each name's pointer address matches its corpus
  index's neighbor set exactly.
- The **registration block binds each name to these exact handlers**:
  in the same code region that stores handler immediates
  (`mov ebp, 0x00536230` at `0x131ad7`, `mov ebp, 0x00536260` at
  `0x131afb`, `mov ebp, 0x00536330` at `0x131b1a`, and sibling
  `mov ebp, 0x00535d00` = native 79 `Shutdown`), adjacent instruction
  streams store the matching name pointers into neighboring descriptor
  globals, each as a direct immediate store —
  `mov dword ptr [0x64e120], 0x64f654` (instruction at `0x131ac7`,
  VA `0x00531ac7`, bytes `c7 05 20 e1 64 00 54 f6 64 00`, name
  immediate at `0x131acd`; the preceding instruction at `0x131ac1` is
  `mov [0x64e11c], ebp`) just before the 0x536230 immediate;
  `mov dword ptr [0x64e160], 0x64f648` (instruction `0x131b90`,
  immediate `0x131b96`) just after the 0x536260 immediate;
  `mov dword ptr [0x64e1a0], 0x64f634` (instruction `0x131bd1`,
  immediate `0x131bd7`) just after the 0x536330 immediate.
  Name↔handler binding is therefore image-internal, not corpus-invented.
- The **behavior** is not variable storage: all three handlers end in a
  call on the world object `0x00855090` into the `CWorld` text-slot
  methods named by the W008 plates. Whatever "variable" meant to the
  original authors, retail uses these opcodes to drive on-screen world
  messages. Any rebuild that implements 76–78 as an int/float variable
  map would be false to the shipped game.

## Contract (byte-exact)

All three are Mission-native handlers: `__thiscall`-shaped
(`ecx` unused), one stack argument `IScript* vm` at `[esp+4]`, argument
values read from the VM's expression stack as element objects whose
vtable slots evaluate them, bare work performed, then `ret 0xc`
(the dispatcher's 3-dword frame). Zero direct `E8` calls inside the
VM-facing sections; all callee dispatch is vtable or immediate-address.

### Native 76 `InitVariable(textIdExpr, stateExpr)` — `0x00536230`, 38 bytes

Body `0x00536230`–`0x00536255` through the complete `ret 0xc`
(`5e c2 0c 00`), SHA-256
`e4c8a9c6e626c3f33f1976d9b970a61a3920e6449766c765e74144f4291070c7`.

1. `eax = [esp+4]` (vm); `ecx = [vm+4]`, `esi = [vm+0]`.
2. `[ecx] → vtable; call [+0x30]` — scalar evaluation of stack element 2;
   result pushed.
3. `[esi] → vtable; call [+0x30]` — scalar evaluation of stack element 1;
   result pushed.
4. `mov ecx, 0x855090; call 0x50d6a0` —
   `CWorld__PushWorldTextSlot(world, elem1_scalar, elem2_scalar)`
   (`this` in `ecx`, two stack args; plate B10.md:236 records the sole
   inbound CALL from `0x0053624d`).
5. `pop esi; ret 0xc`. Trailing NOP pad to `0x00536260`.

### Native 77 `SetVariable(textIdExpr, floatAExpr, floatBExpr)` — `0x00536260`, 57 bytes

Body `0x00536260`–`0x00536298` through the complete `ret 0xc`
(`5f 5e c2 0c 00`), SHA-256
`8eba20521dcb6055b6ff5adb4b8be13f695a0f18aeae7f541322191a3a6b3f72`.

1. `eax = [esp+4]`; `edi = [vm+0]`, `esi = [vm+4]`, `ecx = [vm+8]`.
2. `[ecx] → call [+0x34]` — **float** evaluation of element 3; stored
   via `fstp dword ptr [esp]` as the third stack argument.
3. `[esi] → call [+0x34]` — float evaluation of element 2; likewise
   parked as the second stack argument (`push ecx` first reserves the
   slot; the `fstp` overwrites it).
4. `[edi] → call [+0x30]` — scalar evaluation of element 1; pushed.
5. `mov ecx, 0x855090; call 0x50d720` —
   `CWorld__UpdateWorldTextSlotTiming(world, id, floatA, floatB)`
   (four stack dwords total: id + two floats).
6. `pop edi; pop esi; ret 0xc`. Trailing NOP pad.

Argument order note: element 1 supplies the id matched against stored
slots; elements 2 and 3 supply the two timing floats, in that order.

### Native 78 `ShutdownVariable(idExpr)` — `0x00536330`, 25 bytes

Body `0x00536330`–`0x00536348` through the complete `ret 0xc`
(`c2 0c 00`), SHA-256
`8528e59270e85931174a2e6a4977dd30bd76b6ead40fecdb5006b4690eb705d4`.

1. `eax = [esp+4]`; `ecx = [vm+0]`; `[ecx] → call [+0x30]` — scalar id.
2. `push eax; mov ecx, 0x855090; call 0x50d7a0` —
   `CWorld__ClearWorldTextSlot(world, id)`.
3. `ret 0xc`. Trailing NOP pad to `0x00536350` where native 25 `IsA`
   (`0x00536350`) begins.

### Expression-evaluation convention

`vtable[+0x30]` returns an integer/scalar, `vtable[+0x34]` returns a
float (caller reserves stack space, `fstp` lands it). This matches the
convention already pinned across the retained VM corpus — e.g.
`CScriptObjectCode.cpp.md:273` (`args[1]->vtable[+0x30]()`) and
`IScript.cpp.md:57` (`args[0]->vtable[+0x38]()` for a path *name*,
`+0x30` for scalars). No string-typed argument appears here; ids are
integers, so localization happens inside `PushWorldTextSlot` via
`CText__GetStringById`.

## The CWorld four-slot message store (callee side)

Per the sealed W008 decompiles (static, plate-bounded):

- Four slots at world offsets `this+0x20c` (state), `+0x21c` (id),
  `+0x22c` (string ptr from `CText__GetStringById(&g_Text, id)`),
  `+0x23c` (primary time), `+0x24c` (secondary time), `+0x25c` (default
  duration seeded from `DAT_00672fd0`).
- `PushWorldTextSlot(id, state)` claims the **first free slot**
  (`state == 0`), storing id/string/state, zeroing both timing fields,
  seeding the default; **silently drops** when all four are busy.
- `UpdateWorldTextSlotTiming(id, a, b)` updates **every** matching-id
  slot's times; if the slot's **state** field at `this+0x20c`
  (`pfVar1[-0xc]`) currently holds the bit-pattern `4.2039e-45`
  (integer 3), the primary time is treated as relative
  (`new = DAT_00672fd0 + a` written to `+0x23c`) and the secondary
  write (`b` → `+0x24c`) is skipped; otherwise both are stored
  absolute.
- `ClearWorldTextSlot(id)` sets `state = 0` for every matching-id slot,
  leaving the other fields in place.

HIGH on the wrapper bytes, ABI, callee addresses, and the
world-singleton address. MEDIUM_STATIC on the slot-layout and timing
semantics above: they come from Ghidra decompiles behind sealed plates,
not yet re-derived instruction-by-instruction this wake. Explicitly
unproven: the slot-state enum's meaning, the sentinel at `+0x23c`,
who drains the slots for display (HUD runtime), and whether any other
subsystem writes these arrays.

## Callers

Zero rel32 `E8` inbound to all three VAs (`tools/call_xref_scan.py`,
2026-08-22): they are reached only through the Mission-native dispatch
table via the registration immediates listed above, consistent with the
corpus treating them as command-index handlers. The corpus's authored
call-site counts (76: 77 sites / 21 levels; 77: 146 / 18; 78: 26 / 0)
are replay-derived numbers and stand unmodified here.

## Pinned-source status

Beyond the pinned GPL source: `grep -r "InitVariable|SetVariable|
ShutdownVariable"` over `references/Onslaught/` returns nothing. There
is no source anchor for these natives; shape authority is the image
plus the W008 plates. No divergence-from-source section applies.

## Field map pinned by these bodies

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `vm+0x00/+0x04/+0x08` | expression-stack elements 1/2/3 | all three prologues |
| element `vtable[+0x30]` | scalar evaluation | `0x0053623c` / `0x00536286` / `0x00536338` |
| element `vtable[+0x34]` | float evaluation | `0x00536270` / `0x0053627b` |
| `0x00855090` | the world object used as `this` for all three callees | `0x00536248` / `0x0053628a` / `0x0053633c` |
| `0x0050d6a0` / `0x0050d720` / `0x0050d7a0` | push / time / clear text slot | calls at `0x0053624d` / `0x0053628f` / `0x00536341` |
| world `+0x20c…+0x25c` | four message slots (state/id/string/time/time/default stride 0x10) | plate decompiles (MEDIUM_STATIC) |

## Rebuild mapping

Nearest reconstruction owner: **none added.** Core has no world-text or
message-slot model (`grep WorldText|TextSlot|MissionMessage` over
`rebuild/OnslaughtRebuild.Core` → nothing), and the Level 100 actor
runtime's command set (`Level100ActorScriptCommandKind`) contains no
member for these natives — Level 100's program never issues them, so
its exact-set dispatcher correctly rejects them today. What a future
owner needs if another level's program is reconstructed: a
four-entry-slot store keyed by integer text id with
first-free-slot-push (drop-on-full), per-id multi-update timing
(relative-arm included), clear-by-id, and a text-id→localized-string
resolver at push time. Implementing 76–78 as variables would be wrong;
implementing them as single-slot prints would also be wrong (multi-slot
occupancy and per-id multiplicity are observable in the contracts
above). Per lane rules no Core file was edited from this RE root; the
focused-test step is deferred until such an owner exists.

Corpus correction requested (not self-applied — the TSV lives outside
this lane's ownership): rows 76–78 should gain a pointer to this note;
their `command` names stay (retail-authentic) while any future
`currentGhidraName` promotion should be the `CWorld__*WorldTextSlot`
triple, not variable-store names.

## Cheapest falsifier

Any one of:

- Body SHA-256 mismatch: `0x00536230`(38 B)
  `e4c8a9c6…91070c7`; `0x00536260`(57 B) `8eba2052…a6b3f72`;
  `0x00536330`(25 B) `8528e592…eb705d4` — or any body ending other than
  `ret 0xc` (`5e c2 0c 00` / `5f 5e c2 0c 00` / `c2 0c 00`).
- `tools/disasm_va.py` shows a different call target than
  `{0x0050d6a0, 0x0050d720, 0x0050d7a0}` from the three wrappers, an
  immediate other than `0x00855090` loaded into `ecx` before them, or
  evaluation vtable offsets other than `+0x30`/`+0x34`.
- The string table loses its consecutive
  `Shutdown · ShutdownVariable · SetVariable · InitVariable · Surface ·
  Dive…` layout at `.rdata` `~0x24f628`–`0x24f674` (name VAs
  `0x64f634`/`0x64f648`/`0x64f654`), or any
  registration immediate/name-pointer pair moves apart.
- `tools/call_xref_scan.py` on the three VAs returns any rel32 caller.
- A W008 plate revision renames or re-bounds the triple.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: `tools/disasm_va.py` (full wrapper
  bodies; neighbor `0x00536350` head to confirm boundary), raw byte
  reads (three body hashes; `.rdata` string-table window
  `0x24f534`–`0x24f674`; registration-region windows `0x131ab0`–`0x131b40`
  and `0x131b40`–`0x131c10` decoding the `bf` handler immediates and
  the direct `c7 05` name-pointer stores;
  imm32 census: exactly one site per handler VA), and
  `tools/call_xref_scan.py` (zero rel32 callers ×3).
- Corroboration (not duplicated): sealed fullpass plates
  `ghidra-fullpass-findings/W008/adversarial/B10.md:236-240`
  (`CWorld__PushWorldTextSlot`, sole inbound CALL from `0x0053624d`),
  `W008/adversarial/B11.md:24-47` (timing + clear entries),
  `W008/primary/A10.md:328-338` (boundary chain around `0x0050d6a0`);
  decompiles
  `local-lab/ghidra-fullpass-2026-07-23/exports/W008/decompile/
  0050d6a0_CWorld__PushWorldTextSlot.c`,
  `0050d720_CWorld__UpdateWorldTextSlotTiming.c`,
  `0050d7a0_CWorld__ClearWorldTextSlot.c` (slot layout, drop-on-full,
  relative-arm, clear-by-id semantics quoted above).
- Coverage corpus cross-reference:
  `reverse-engineering/binary-analysis/mission-native-corpus-coverage-2026-08-15.tsv`
  rows 76–78 (indices/names/authored counts confirmed; behavior labels
  corrected by this note).
- 2026-08-22 (review pass) — independent reviewer spot-check re-measured
  every claim from the same pristine specimen: full-body hashes through
  the complete `ret 0xc` (38/57/25 B, values above), exactly one
  image-wide imm32 per handler VA, callee targets
  `{0x0050d6a0, 0x0050d720, 0x0050d7a0}`, `.rdata` name run at
  `0x24f628`–`0x24f674` (laid down in descending corpus-index order),
  registration `c7 05` stores at `0x131ac7`/`0x131b90`/`0x131bd1`.
  Defects found and corrected in place: the original body hashes
  truncated each wrapper's `ret 0xc` tail by 2 bytes (lengths 36/55/23
  were wrong); the name run was described in ascending corpus order;
  the InitVariable registration-store instruction address is
  `0x131ac7` / VA `0x00531ac7` (immediate `0x131acd`), not
  `0x131ac1`/`0x131ac7`.
- 2026-08-22 (operator round-1 receipt) — corpus dispositions corrected:
  rows 76/77 are `OBSERVED`, only row 78 is `AUTHORED_UNOBSERVED`
  (re-read from the TSV this pass). Timing-arm sentinel re-attributed
  to the slot **state** field at `this+0x20c` per the cited decompile.
  Header-gate status for this note is unchanged (names-check
  zero-assertion PASS); the repo-level `doc_header_check` exit is
  currently owned by the ResetConfiguration backlog row, which this
  lane must not edit — integration drops that line on land.
