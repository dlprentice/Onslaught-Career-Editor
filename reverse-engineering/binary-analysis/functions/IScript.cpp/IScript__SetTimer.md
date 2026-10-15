# IScript__SetTimer

> Address: `0x005358e0`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/eventmanager.cpp:143-146` owns the callee
(`CEventManager::AddEvent` time-from-now overload); the wrapper itself is
absent from the pinned source | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 19, registered as `SetTimer`, schedules a real
future event: it float-evaluates its one script expression as a
time-from-now, keeps the incoming dispatcher-context object as the event's
callback receiver, and calls `CEventManager__AddEvent_TimeFromNow`
(`0x0044b2d0`) on the global event-manager singleton `0x00672fc8` with
event number `0x7d2` (2002). It touches neither the CWorld message/timer
store (natives 76/77/81) nor the thing variable store (native 68) — it is
the scheduled-events subsystem, the third distinct system hiding behind
timer-like names.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 above,
verified before reading) with `tools/disasm_va.py` (whole body), raw byte
reads (body hash, imm32 census, string table, registration block), and
`tools/call_xref_scan.py`. Callee identity corroborated by the tracked
name table and [`../CEventManager.cpp.md`](../CEventManager.cpp.md).
No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding (third system behind timer-like names)

`mission-native-corpus-coverage-2026-08-15.tsv` row 19 is `SetTimer` /
handler `0x005358E0` / 0 authored sites / 0 levels /
`DORMANT_CANDIDATE`; the current saved symbol in
`ghidra-function-name-table-2026-08-17.tsv` is
`IScript__SetTimer`, bounded `0x005358e0`–`0x00535910` (the adjacent
`0x005348f0` row belongs to native 68 `SetVar`). Row confirmed
this wake. With this note the family split across the "variable/timer"
name group is three-way:

| Natives | Name says | Bytes do | Store |
| --- | --- | --- | --- |
| 76 InitVariable / 77 SetVariable / 81 GetVariable | variable map | world text-slot push/time/read | CWorld four-slot store |
| 78 ShutdownVariable | variable delete | clear matching text slots | same store |
| 68 SetVar | variable set | forward raw elements to thing virtual `[+0xf8]` | per-thing named store |
| 19 SetTimer | timer | schedule event 2002 on the global event manager | `CEventManager` ring |

## Contract (byte-exact)

One stack argument `IScript* vm` at `[esp+4]`; uses the incoming `ecx`
(the Mission dispatcher context) like native 68, and evaluates exactly one
element through the float vtable slot. Body `0x005358e0`–`0x00535910`
inclusive through the complete `ret 0xc`, **49 bytes**, SHA-256
`5262e1f5a2ae51e2a1da0a01aea4866302d9a16b675fd8228a664002cb8b7b9b`.
Exactly one direct `E8`.

```
005358e0  8b 44 24 04        mov eax, [esp+4]           ; IScript* vm
005358e4  56                 push esi
005358e5  8b f1              mov esi, ecx               ; SAVE incoming dispatcher context
005358e7  8b 08              mov ecx, [eax]             ; element object 1
005358e9  8b 11              mov edx, [ecx]
005358eb  ff 52 34           call dword ptr [edx+0x34]  ; FLOAT evaluation
005358ee  d9 5c 24 08        fstp dword ptr [esp+8]     ; store into the dead vm-arg slot
005358f2  6a 00              push 0                     ; re_use_event = 0
005358f4  6a 00              push 0                     ; data = 0
005358f6  6a 00              push 0                     ; start_or_end = 0 (START_OF_FRAME)
005358f8  56                 push esi                   ; to_call = dispatcher context
005358f9  8d 44 24 18        lea eax, [esp+0x18]        ; &time_from_now (the reused slot)
005358fd  68 d2 07 00 00     push 0x7d2                 ; event_num = 2002
00535902  50                 push eax
00535903  b9 c8 2f 67 00     mov ecx, 0x672fc8          ; global CEventManager
00535908  e8 c3 59 f1 ff     call 0x44b2d0              ; AddEvent_TimeFromNow
0053590d  5e                 pop esi
0053590e  c2 0c 00           ret 0xc
00535911  90 x?              nop pad to 0x00535920 (native 18 GetHealth)
```

1. `eax = [esp+4]` (vm); `esi = ecx` — the incoming dispatcher-context
   object is saved; it becomes the event's callback receiver.
2. Element object 1 is evaluated through `vtable[+0x34]` (**float**, the
   only element dispatch in the body) and stored with `fstp` into
   `[esp+8]` — which, after the `push esi`, is exactly the consumed
   `vm` argument slot. The wrapper reuses its dead argument cell as the
   `time_from_now` storage; the callee copies the float out during the
   call (`0x44b2d0` reads `[esp+4]` as a reference first thing).
3. Six stack arguments are laid out for
   `CEventManager__AddEvent_TimeFromNow(const float& time_from_now,
   int event_num, void* to_call, int start_or_end, void* data,
   int re_use_event)` — measured push order `(&time, 0x7d2, ctx, 0, 0, 0)`
   — with `ecx = 0x672fc8`, the global event-manager singleton
   (identity independently pinned by `CEventManager.cpp.md:51-52`, where
   every direct caller loads the same immediate).
4. Event number **`0x7d2` = 2002**. Sibling evidence shows the same
   subsystem carrying other natives' traffic: `CScriptEventNB.cpp.md:86`
   and `IScript.cpp.md:138` record native-driven scheduling of event 2000
   (`FollowWaypoint`'s self-sustaining next-frame loop) against the same
   singleton.
5. `pop esi; ret 0xc`.

HIGH on the wrapper bytes, the ABI, the callee/global addresses, and the
event number. MEDIUM_STATIC on the parameter-name reading of positions
4–6 (zeros; names taken from the pinned `CScheduledEvent::Set` /
eventmanager source shape) and on what the dispatcher context does when
event 2002 later fires (which of its vtable slots receives it) — not
re-derived this wake.

## Registration (name ↔ handler binding)

- Handler immediate: `bd e0 58 53 00` (`mov ebp, 0x005358e0`) at VA
  `0x005305f6` / file `0x1305f6` (immediate at VA `0x005305f7`).
  Exactly **one** image-wide imm32 of `0x005358e0` exists — this site.
- Name-pointer store: `c7 05 e0 d2 64 00 60 f9 64 00`
  (`mov dword ptr [0x64d2e0], 0x64f960`) at VA `0x00530654` / file
  `0x130654` (global immediate at `0x00530656`, name immediate at
  `0x0053065a`–`0x0053065d`), in the same descriptor-initialization
  block as the handler immediate.
- Name string: `SetTimer\0` at `.rdata` `0x0064f960` (file `0x24f960`),
  continuing the descending-corpus-index run:
  `GetPlayer(21) 0x64f944 · GetDistToObj(20) 0x64f950 · SetTimer(19)
  0x64f960 · GetHealth(18) 0x64f96c · AddMessage(17) 0x64f978 ·
  PrintText(16) 0x64f984 · GetThingRef(14) 0x64f990 …`.

Name↔handler binding is image-internal: the registration ties the
`SetTimer` label to `0x005358e0`.

## Callers

Zero rel32 `E8` inbound to `0x005358e0` (`tools/call_xref_scan.py`,
2026-08-22): reached only through the Mission-native dispatch table via
the registration immediate. Corpus counts 0 authored sites / 0 levels
(`DORMANT_CANDIDATE`) — the native ships registered but no shipped
mission calls it.

## Pinned-source status

The wrapper is absent from `references/Onslaught/`, but its callee is
sourced: `eventmanager.cpp:143-146` is the `AddEvent(const float&
time_from_now, …)` overload, and `CScheduledEvent::Set(int event_num,
const float& time, CMonitor* to_call, CMonitor* data)`
(`scheduledevent.cpp`, mirrored by `CScheduledEvent__Set.md`) fixes the
field meanings the wrapper's zero arguments fill. Agreement, not
divergence: the retail bytes call the sourced scheduler with the sourced
shape. What the bytes add: the native's event number (2002), the
receiver (dispatcher context), the float-only evaluation, and the
argument-slot reuse.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| incoming `ecx` | dispatcher-context object, saved as event receiver | `0x005358e5` |
| element `vtable[+0x34]` | float evaluation (only element dispatch) | `0x005358eb` |
| `[esp+8]` after `push esi` | reused vm-arg slot holding `time_from_now` | `0x005358ee` |
| `0x00672fc8` | global `CEventManager` singleton | `0x00535903` |
| event `0x7d2` (2002) | the timer event number filed against the context | `0x005358fd` |

## Rebuild mapping

Mechanism owner **exists**:
`rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs` models
`CEventManager::AddEvent` including the `AddEventTimeFromNow` entry point
that wraps `0x0044b2d0`, with admission/refusal laws under
`RetailEventSchedulerTests`. Native-binding owner: **none yet** — no Core
type binds Mission-native 19 (or any native handler table) to the
scheduler; Level 100's exact-set command runtime never issues it. When a
mission-script runtime owner lands, native 19 must be bound as
`scheduler.AddEventTimeFromNow(eventNum: 2002, toCall: dispatcherContext,
timeFromNow: evaluatedFloat, startOrEnd: StartOfFrame, data: 0,
reuseHandle: none)`. A focused test pinning the binding is deferred until
that owner exists (same recorded decision as natives 68/76–78/81);
implementing 19 against the CWorld message/timer store or the thing
variable store would be false to the shipped game.

Corpus correction requested (not self-applied): row 19 should
cross-reference this note; its `DORMANT_CANDIDATE` disposition stands
unchanged.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005358e0`–`0x00535910` is not
  `5262e1f5…b9b`, or the body does not end `5e c2 0c 00`.
- Any `call dword ptr [reg+0x30]` scalar evaluation appears in the body
  (there must be none; the single element dispatch is `[+0x34]`).
- The call target is anything but `0x0044b2d0`, the manager immediate
  anything but `0x00672fc8`, or the event immediate anything but
  `0x7d2`.
- A second image-wide imm32 of `0x005358e0` exists, or the registration
  pair (handler immediate at VA `0x005305f6`, name-pointer store at VA
  `0x00530654`) moves apart.
- `.rdata` `0x0064f960` stops being `SetTimer\0`.
- `tools/call_xref_scan.py` returns any rel32 caller of `0x005358e0`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: `tools/disasm_va.py` (full wrapper
  body; neighbor head `0x00535920` native 18 `GetHealth` to confirm the
  boundary), raw byte reads (body hash; registration window
  `0x005305e6`–`0x00530616` decoding the `bd` handler immediate and the
  `c7 05` name-pointer store; `.rdata` string window
  `0x24f940`–`0x24f9b0`; image-wide imm32 census of `0x005358e0`:
  exactly one site at VA `0x005305f7`; image-wide imm32 census of the
  name VA `0x64f960`: exactly one site at VA `0x0053065a`), and
  `tools/call_xref_scan.py` (zero rel32 callers of `0x005358e0`, run
  this wake; the same tool returned zero callers for native-68
  `0x005348f0` in the same session).
- Corroboration (not duplicated): `CEventManager.cpp.md:51-52` pins
  `0x00672fc8` as the global manager every direct caller loads;
  `IScript.cpp.md:138` and `CScriptEventNB.cpp.md:86` show the sibling
  event-2000 scheduling pattern against the same singleton;
  `CScheduledEvent__Set.md` fixes the scheduled-event field meanings;
  `RetailEventScheduler.cs` (Core) already encodes the callee's
  admission laws with tests.
- Cross-reference (same wake): `IScript__SetVar.md` (native 68) and
  `IScript__GetVariable.md` (native 81) establish the other two legs of
  the family split; measurement dossier
  `local-lab/hermes-kanban-campaign-2026-08-22/setvar-68-dossier-run697.md`.
- Coverage corpus cross-reference:
  `mission-native-corpus-coverage-2026-08-15.tsv` row 19 (index/name/
  disposition confirmed unchanged by this note; 0/0 authored counts
  stand).
