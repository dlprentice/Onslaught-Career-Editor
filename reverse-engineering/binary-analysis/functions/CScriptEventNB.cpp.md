# CScriptEventNB function map

Status: active static function map
Last updated: 2026-08-17 (event-dispatch slice; register/post/handle and the
world script-event loader byte-mapped; message-0x7d0 fire path closed)
Source File: `C:\dev\ONSLAUGHT2\MissionScript\ScriptEventNB.cpp` (SEH
`__FILE__` pointer `0x0064fe98` read out of `RegisterEventListener`) | Binary:
BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — bytes re-read from the pristine specimen at file offset
VA − 0x400000 with `tools/disasm_va.py`; call sites by the whole-image `E8/E9`
scan `tools/call_xref_scan.py`. Names are the live Ghidra name table
(db.18627 lineage); the byte contracts below are independent of the names.

## Shape

`CScriptEventNB` is a `CMonitor` subclass (see
[`CMonitor.cpp.md`](CMonitor.cpp.md)): its constructor installs the vtable
`0x005e4f44` and its base destructor delegates shutdown to
`CMonitor__Shutdown`. It holds one named-event list at `[this+8]`; each list
element is an event entry whose `+0` is a *name object* (a virtual
`vtable+0x38` name getter and `vtable+0x48` value/clone factory) and whose
`+4` is a `CSPtrSet` of listener nodes. A listener node's first dword is the
listener itself — a `CEventFunction`, dispatched by
`CEventFunction__Execute` — and the same node lives in the listener's own
`CMonitor` deletion-event set, so removing the entry can un-register every
listener symmetrically. The global instance is `0x0089c590`. Its 0x18-byte
`CPostEventData` sibling (vptr `0x005e4f34`, name-object payload at `+8`)
carries a posted event's data between the registry `PostEvent` command and
the fired-event dispatch (see "Message 0x7d0 fire path" below).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538760` | `CScriptEventNB__Init` | `8bc1 33c9 894804 894808 c700 444f5e00 c3` | Zeroes `[this+4]` and `[this+8]`, installs vtable `0x005e4f44`; `ret`. HIGH. |
| `0x00538780` | `CScriptEventNB__ScalarDeletingDestructor2` | `56 8bf1 e8c8010000 f644240801 740b 56 b9f03d9c00 e8860a0100 8bc6 5e c20400` | `BaseDestructor(this)` (`0x00538950`), then if `flags & 1` frees `this` via `CDXMemoryManager__Free` (manager `0x009c3df0`); `ret 4`. HIGH. |
| `0x005387a0` | *(unnamed global-destructor thunk)* | `b990c58900 e9a6010000` | `mov ecx,0x0089c590; jmp 0x00538950` — the exit-time destructor of the singleton. Not a named entry in live Ghidra. HIGH on the bytes. |
| `0x005387b0` | `CScriptEventNB__ClearListenerEntry` | `6aff 681b745d00 64a100000000 50 64892500000000 51 56 8bf1 57 … 8b0e … ff10 … 8d7e04 c70600000000 …` | SEH. Deletes the element's name object via `call [nameObj->vtable][0](nameObj, 1)`; then walks the `[element+4]` set: for each node, `CMonitor__DeleteDeletionEvent(node->[0], node)` (`0x0042d9b0` — removes the node from the listener's own `+4` set) and `CDXMemoryManager__Free(node)`; closes with two `CSPtrSet__Clear` calls on `[element+4]`. HIGH on the delete pair; the doubled Clear's purpose stays open. |
| `0x00538860` | `CScriptEventNB__CreateListenerSet` | `6aff 6846745d00 … 6a42 8bf9 6898fe6400 6a76 6a10 b9f03d9c00 e8… 8bf0 … 8bce e8… 897708` | SEH. Allocates **0x42** bytes (`ScriptEventNB.cpp:118`), runs `CSPtrSet__Init` on it, stores it at `[this+8]`. HIGH on alloc + store. Measured field use: `+0` head node, `+8` walk cursor, `+0xc` count; the exact head/tail identities are MEDIUM. |
| `0x005388d0` | `CScriptEventNB__DestroyAllEvents` | `535657 8bd9 e8d623f8ff 8b7b08 … e8affeffff 56 b9f03d9c00 e8…` | `CMonitor__Shutdown_Core(this)` (`0x004bacb0`), then walks `[this+8]`: `ClearListenerEntry(element)` + `Free(element)` for each. HIGH. |
| `0x00538950` | `CScriptEventNB__BaseDestructor` | `c701 444f5e00 e9e522f8ff` | Installs base vtable `0x005e4f44` and tail-jumps `CMonitor__Shutdown` (`0x004bac40`). HIGH — the IS-A link to `CMonitor`. |
| `0x00538960` | `CScriptEventNB__RegisterEventListener` | `6aff 68c3745d00 64a100000000 50 64892500000000 … 8b4908 … 8b01 ff5038 … 8b17 8bcf 8bf0 ff5238 … 3a16 751c … 6a68 6898fe6400 6a76 6a18 b9f03d9c00 … 8d6e04 8bcd e8f9cdfaff … 6a11 … 6a19 … 8b4e04 57 e84ccffaff … 578d4e04 e8d3cffaff` | `ret 8`, two stack args on the singleton `0x0089c590`. **Arg1 is the name-key node** — `[arg1]` is a virtual name object whose `vtable+0x38` returns the compared name and `vtable+0x48` returns the value stored at `element[0]`. **Arg2 is the listener** (`CEventFunction`), whose `+4` field is the `CMonitor` deletion-event `CSPtrSet`. Walks `[this+8]` comparing `element[0].vtable[0x38]` names byte-wise; on miss it allocates a **0x68**-byte element, `CSPtrSet__Init(element+4)`, stores `element[0] = arg1.vtable[0x48]()`, allocates a **0x11**-byte node, `node[0]=listener`, `CMonitor__AddDeletionEvent(listener,node)` (`0x00401040`) and `CSPtrSet__AddToTail(element+4,node)`; on hit it allocates a **0x19**-byte node, lazily builds `[listener+4]` under the `Monitor.h:94` pattern (`__FILE__` `0x0064fa6c`), then `AddToHead`/`AddToTail`. Returns the element. HIGH on the wiring; the 0x11-vs-0x19 node-size split is measured and open (see below). |
| `0x00538b70` | `CScriptEventNB__PostEvent` | `555657 8bf9 8b4708 8b480c 85c9 7551 … b858c26200 … 3ad3 … 68ccfe6400 6880f56600 e8738bf0ff … 8b4708 8b28 … ff5038 … 3a16 … c6471401 … e86071ffff` | `ret 4`, one string arg, singleton `this`. If `[[this+8]+0xc]` (the listener count) is zero and the name is not `"game playing"` (`0x0062c258`), it prints `CConsole__Printf(0x0066f580, "Warning: No listeners for posted event '%s'", name)` (`0x00441740`, format `0x0064fecc`). Then walks the entries, compares `element[0].vtable[0x38]` names, and on match sets `element[0x14]=1` and calls `CEventFunction__Execute(node->[0])` (`0x0052fda0`) for every node in `element+4`. HIGH. |
| `0x00538c70` | `CScriptEventNB__HandleEventMessage` | `51 8b442408 5357 8bf9 66817804d007 0f851d010000 8b400c … 8b4808 … ff5038 … b858c26200 … 3a1e 751c … 68ccfe6400 6880f56600 … 885f14 … e83370ffff` | `ret 4`; **vtable slot 0** of `CScriptEventNB` (`0x005e4f44`), which is why the `E8/E9` census finds zero direct callers. Arg is the fired `CScheduledEvent`: `word[arg+4]` must be **0x7d0** (2000, `mEventNum`) or it returns, `[arg+0xc]` (`mData`) is a `CPostEventData`, `[mData+8]` is the cloned name object whose `vtable+0x38` supplies the name. Same empty-list `"game playing"` warning and the same entry scan / `CEventFunction__Execute` dispatch as `PostEvent`. HIGH; sender and fire path byte-closed (see below). |
| `0x0050ac70` | `CWorld__LoadScriptEvents` | `6aff 68a25b5d00 64a100000000 50 64892500000000 83ec18 … 8b6c242c … 8d442408 6a04 50 8bcd e8d2d80300 … 81c620010000 … 68c0000000 68acd26300 6a18 6a08 b9f03d9c00 e807e40300 … 55 8bc8 e8a14a0200 … 68c3000000 68acd26300 6a18 6a70 … e89be10200 … 68c5000000 68acd26300 6a18 6a08 … 8938 897004 … 8b4c2414 50 e8c2adfdff … 8d4c241c 6a0a 51 8bcd e804d80300 … c20400` | `ret 4`, one arg — a `CDXMemBuffer` read source (`CDXMemBuffer__Read`, `0x00548570`); `this` is the `CWorld`. Reads a 4-byte count; if `<= 0` returns. Then loops: allocates a **0xc0**-byte `CStringDataType` (`world.cpp:24`, `__FILE__` `0x0063d2ac`) and `CStringDataType__ReadFromBuffer` (`0x0052f790`) for the name, allocates a **0x70**-byte `CMissionScriptObjectCode` (`world.cpp:195`) and constructs it (`0x00538ec0`), allocates an **8**-byte `{name, code}` pair (`world.cpp:197`), `CSPtrSet__AddToTail` (`0x004e5b20`) into `[this+0x120]`, then reads a trailing **0xa**-byte field before the next record. HIGH on the read/construct/append chain; the trailing 0xa field's meaning is MEDIUM. |

## Callers (direct `E8` rel32, whole-image scan)

| Target | Call site | Owner |
| --- | --- | --- |
| `RegisterEventListener` | `0x00533564` | `IScript__CallEvent0AndRegisterNestedListeners` — passes the key node first, the listener second, and stores the returned element at `[keyNode+4]` |
| `PostEvent` | `0x0044e2a0` | `CFenrir__VFunc_0_0044e240` — posts `"fenrir blowing up"` (`0x00628e88`) after a 50-iteration `PickupSpawn_T3_0044e300` loop |
| `PostEvent` | `0x0046fedb` | `CGame__StartPlayingState` — posts `"game playing"` |
| `PostEvent` | `0x0046ff99` | `CGame__HandleEvent` — posts `"game playing"` |
| `PostEvent` | `0x00470041` | `CGame__HandleEvent` — posts `"game playing"` |
| `CreateListenerSet` | `0x0046c5cb` | `CGame__InitRestartLoop` — builds the singleton's `[this+8]` listener container on restart |
| `DestroyAllEvents` | `0x0046ccf2` | `CGame__ShutdownRestartLoop` — clears it on shutdown |

`HandleEventMessage` has no direct caller: its address is stored at `.rdata`
`0x005e4f44`, the first slot of the vtable `Init` installs. It is the
`CMonitor::HandleEvent` override reached through `CEventManager::Flush`'s
listener dispatch — see the fire-path section below.

## Message 0x7d0 fire path — CLOSED (pristine bytes + pinned source)

The sender of message `0x7d0` is `IScript__PostEvent`
(`0x005383c0`; `__FILE__` pointer `0x0064fa40` =
`C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp`). It has zero direct `E8`/`E9`
callers: `ScriptCommandRegistry__InitBuiltins` (`0x0052ff30`) writes its
address into registry slot `0x0064cf90` beside the command-name pointer
`0x0064f9e8` = `"PostEvent"`, so it is the builtin registry command. Byte
path:

1. Clone the name-key node: `mov eax,[arg1]; mov ecx,[eax]; mov edx,[ecx];
   call [edx+0x48]` — the name object's value/clone factory — and store the
   clone at `[esi+8]` of a `CPostEventData` whose vptr is installed as
   `0x005e4f34` (`mov [esi],0x5e4f34`) and whose `+4` is zeroed.
2. Track it: `push esi; mov ecx,0x00855190; call 0x004e5a80`
   (`CSPtrSet__AddToHead`) — the global pending-post set `0x00855190` holds
   the `CPostEventData` alive; its only other reference in the image is the
   destructor body at `0x00538710`.
3. Schedule: `push 0` (re_use), `push esi` (data = the `CPostEventData`),
   `push &-1.0f` (`NEXT_FRAME`, stored `0xbf800000`), `push 0`
   (`START_OF_FRAME`), `push 0x0089c590` (to_call = the singleton),
   `push 0x7d0` (event_num 2000), `mov ecx,0x00672fc8; call 0x0044b370`
   (`CEventManager__AddEvent_AtTime`).

The fire path is `CEventManager::Flush`'s listener dispatch. At `0x0044b68a`
(ring lane) and `0x0044b6f2` (overflow lane) it does
`mov ecx,[node]` (mToCall) → `mov edx,[ecx]` (vtable) → `push node` →
`call [edx]` — **vtable slot 0**, the `CMonitor::HandleEvent` virtual.
`CMonitor`'s base slot 0 is `SharedVFunc__NoOpOneArg` (`0x004014c0`), so a
plain monitor ignores the event; the singleton's slot 0 is `0x00538c70` =
`HandleEventMessage`, which is therefore the `HandleEvent` override (the
Ghidra label `HandleEventMessage` is a research name; the semantic role is
the fire callback). `HandleEventMessage` then reads `word[event+4]==0x7d0`
(mEventNum 2000), `[event+0xc]` (mData = `CPostEventData`), `[mData+8]` (the
cloned name object), `call [nameObj->vtable+0x38]` (the name string), and
runs the same named-listener scan / `CEventFunction__Execute` dispatch as
`PostEvent`. The `CPostEventData` destructor body (`0x005386d0`, entered from
`CPostEventData__ScalarDeletingDestructor` `0x005386b0`) closes the
lifecycle: delete the name object via `call [nameObj->vtable][0](nameObj,1)`,
then `CSPtrSet__Remove(0x00855190,this)` (`0x004e5bd0`), then
`CMonitor__Shutdown` (`0x004bac40`).

The `CScheduledEvent` layout is now byte-settled against the pinned
`Event.h` + `scheduledevent.h` (a `CEvent` base of `mToCall` +
`mEventNum(short)`, then `mBeingReused(short)`, `mData`, and `mTime`):

| Offset | Field | Witness |
| --- | --- | --- |
| `+0x00` | `mToCall` (`CActiveReader<CMonitor>`) | `mov ecx,[eax]` at `0x0044b67d` |
| `+0x04` | `mEventNum` (short) | `cmp word [eax+4],0x7d0` at `0x00538c79`; `mov [esi+4],ax` in `Set` (`0x004de1f0`) |
| `+0x08` | `mBeingReused` (short) | `mov word [eax+8],bp` at `0x0044b67f`; `mov [esi+8],0` in `Set` |
| `+0x0c` | `mData` (`CActiveReader<CMonitor>`) | `mov eax,[eax+0xc]` at `0x00538c85` |
| `+0x10` | `mTime` (float) | `mov [esi+0x10],edx` in `Set`; `fcomp [edx+0x10]` at `0x0044b6d1` |

RTTI class hierarchy (COLOC walk, MSVC `vtable-4` layout — each vptr is
preceded by its Complete Object Locator pointer): `IListener`
(`.?AVIListener@@`, COLOC `0x00619608`) is the root; `CMonitor : IListener`
(`.?AVCMonitor@@`, COLOC `0x0060cbe0` at `0x005d92d0`, vtable `0x005d92d4`);
`CEventFunction`, `IScript`, `CVM`, `CPostEventData`, and `CScriptEventNB`
all derive `: CMonitor`. `CPostEventData`'s COLOC `0x00619658` sits at
`0x005e4f30` (vptr `0x005e4f34`), the singleton's COLOC `0x006196a8` sits at
`0x005e4f40` (vptr `0x005e4f44`) — two adjacent 3-slot vtables. The
singleton's three slots override the three `CMonitor` virtuals —
`HandleEvent` (base no-op `0x004014c0` → `0x00538c70`), scalar dtor
(`0x00538780`), `Shutdown_Core` (`0x005388d0`, which first calls base
`CMonitor__Shutdown_Core` `0x004bacb0`); `CPostEventData` overrides only its
scalar dtor (`0x005386b0`) and keeps the base no-op `HandleEvent`, so a
posted `CPostEventData` never re-enters the dispatch when used as `data`.

## Family roster (named in live Ghidra, not yet byte-mapped here)

`CScriptEventNB__UpdateWaypointFollowing` (`0x00538470`).

`IScript__PostEvent` (`0x005383c0`) and
`CPostEventData__ScalarDeletingDestructor` (`0x005386b0`, body `0x005386d0`)
are now byte-mapped in the fire-path section above.

`CScriptEventNB__UpdateWaypointFollowing` is name-suspect: its body is
position-vector math (`fld [esi+0x14+0x1c]` minus `[target+0x1c]`, distance
squared, `fsqrt`, threshold compare) plus `CScriptObjectCode` calls on the
adjacent singleton `0x0089c5e0` — no listener-set walk — so the
`CScriptEventNB__` prefix is worth a name review, not a body claim.

## Open questions (cheapest falsifier first)

- The name object's class: CLOSED — the RTTI COLOC walk names it
  `CStringDataType` (mangled `.?AVCStringDataType@@`, COLOC `0x006194e8` at
  `vtable-4`, vtable `0x005e4e4c`): slot `+0x38` (14) is
  `SharedVFunc__ReturnField04_0052f540` (the name getter returning the
  string buffer at `[this+4]`) and slot `+0x48` (18) is
  `CStringDataType__Clone` (`0x0052f2c0`, the clone factory used by
  `RegisterEventListener` and `IScript__PostEvent`). The names loaded by
  `CWorld__LoadScriptEvents` are this type, so the event-entry name objects
  are `CStringDataType` instances.
- The `0x11` vs `0x19` node-size split (17 vs 25 bytes) between the
  register-new and register-existing arms: MEASURED, still open — both arms
  write only `node[0] = listener` before the set inserts (the sets wrap each
  item in their own 8-byte `{item,next}` node: `CSPtrSet__AddToHead`
  `0x004e5a80` / `CSPtrSet__AddToTail` `0x004e5b20`); no writer or reader of
  node bytes `+4..+24` was found in `RegisterEventListener`,
  `ClearListenerEntry`, `CMonitor__Shutdown_Core` (`0x004bacb0`, which zeroes
  only `node[0]`), or the dispatch walk. The hit arm's extra 8 bytes have no
  static consumer; next instrument is a runtime watch of a hit-arm node's
  bytes during `RegisterEventListener`.
- The `[this+8]` 0x42-byte container: `+0`/`+8`/`+0xc` are measured as
  head-ish/cursor/count; the exact head-vs-tail node identities.
- Who invokes `CScriptEventNB::HandleEventMessage` (vtable slot 0) with
  message `0x7d0`: CLOSED — `IScript__PostEvent` (`0x005383c0`) schedules
  event 2000 with `to_call = 0x0089c590` and `data = CPostEventData`;
  `CEventManager::Flush` dispatches the fired `CScheduledEvent` to the
  listener's vtable slot 0 at `0x0044b68a` / `0x0044b6f2`. See the fire-path
  section above.
- The doubled `CSPtrSet__Clear` at the tail of `ClearListenerEntry`.
