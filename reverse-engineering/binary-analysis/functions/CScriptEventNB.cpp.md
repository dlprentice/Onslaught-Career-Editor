# CScriptEventNB function map

Status: active static function map
Last updated: 2026-08-17 (event-dispatch slice; register/post/handle and the
world script-event loader byte-mapped)
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
listener symmetrically. The global instance is `0x0089c590`.

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
| `0x00538c70` | `CScriptEventNB__HandleEventMessage` | `51 8b442408 5357 8bf9 66817804d007 0f851d010000 8b400c … ff5038 … b858c26200 … 3a1e 751c … 68ccfe6400 6880f56600 … 885f14 … e83370ffff` | `ret 4`; **vtable slot 0** of `CScriptEventNB` (`0x005e4f44`), which is why the `E8/E9` census finds zero direct callers. Arg is a message struct: `word[arg+4]` must be **0x7d0** (2000) or it returns, and `[arg+0xc]` is the name object whose `vtable+0x38` supplies the name. Same empty-list `"game playing"` warning and the same entry scan / `CEventFunction__Execute` dispatch as `PostEvent`. HIGH on the dispatch; the identity of message 0x7d0's sender stays open. |
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
`0x005e4f44`, the first slot of the vtable `Init` installs.

## Family roster (named in live Ghidra, not yet byte-mapped here)

`CScriptEventNB__UpdateWaypointFollowing` (`0x00538470`).

`CScriptEventNB__UpdateWaypointFollowing` is name-suspect: its body is
position-vector math (`fld [esi+0x14+0x1c]` minus `[target+0x1c]`, distance
squared, `fsqrt`, threshold compare) plus `CScriptObjectCode` calls on the
adjacent singleton `0x0089c5e0` — no listener-set walk — so the
`CScriptEventNB__` prefix is worth a name review, not a body claim.

## Open questions (cheapest falsifier first)

- The name object's class: which RTTI type carries `vtable+0x38` = name getter
  and `vtable+0x48` = value/clone factory — run the COL walk from the vtable
  pointed to by a key node in `IScript__CallEvent0AndRegisterNestedListeners`.
- The `0x11` vs `0x19` node-size split (17 vs 25 bytes) between the
  register-new and register-existing arms — what the found arm's extra 8 bytes
  hold.
- The `[this+8]` 0x42-byte container: `+0`/`+8`/`+0xc` are measured as
  head-ish/cursor/count; the exact head-vs-tail node identities.
- Who invokes `CScriptEventNB::HandleEventMessage` (vtable slot 0) with
  message `0x7d0` and a name object at `[msg+0xc]` — the immediate-`ecx`
  census of `0x0089c590` finds only register/post and the two restart-loop
  lifecycle sites, so the sender loads the singleton through a memory operand
  or a derived pointer; scan for memory-operand reads of `0x0089c590` followed
  by a `call [reg]`.
- The doubled `CSPtrSet__Clear` at the tail of `ClearListenerEntry`.
