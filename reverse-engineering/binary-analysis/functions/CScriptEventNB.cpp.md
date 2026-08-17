# CScriptEventNB function map

Status: active static function map
Last updated: 2026-08-17
Source File: `C:\dev\ONSLAUGHT2\MissionScript\ScriptEventNB.cpp` (SEH
`__FILE__` pointer `0x0064fe98` read out of `RegisterEventListener`) | Binary:
BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — bytes re-read from the pristine specimen at file offset
VA − 0x400000; names are the live Ghidra name table, byte contracts are
independent of the names.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538960` | `CScriptEventNB__RegisterEventListener` | `6aff 6874c35d00 64a100000000 50 64892500000000 … 8b4908 … 8b01 ff5038 … 8b17 8bcf ff5238 … 3a16 751c … 6a68 6898fe6400 6a76 6a18 b9f03d9c00 … 8d6e04 8bcd e8… … e8…` | `ret 8`, two stack args. SEH frame; walks the listener list at `[this+8]`, comparing names through two `call [vtable+0x38]` sites (`0x005389a7`, `0x005389b1`) with an inline byte-wise string loop (`3a 16 / 75 1c` at `0x005389b5`). Allocates via `CDXMemoryManager__Alloc` (manager `0x009c3df0`): a **0x68**-byte listener entry (`ScriptEventNB.cpp` line `0x76` = 118) with `CSPtrSet__Init` on its `+4` field (`0x00538a42` → `0x004e5840`), a 4-byte name cell (line 118), and — on the second arm — a **0x19**-byte node plus a lazily built **0x18**-byte `CSPtrSet` at `[arg+4]` under the `Monitor.h` line 94 pattern (`__FILE__` `0x0064fa6c` = `MissionScript\..\monitor.h`), then `CSPtrSet__AddToTail` calls. Calls `CMonitor__AddDeletionEvent` at `0x00538a85`. MEDIUM-HIGH on the measured calls and sizes; the two arms' register-new-vs-register-existing intent remains open. |

## Family roster (named in live Ghidra, not yet byte-mapped here)

`CScriptEventNB__Init` (`0x00538760`),
`CScriptEventNB__ScalarDeletingDestructor2` (`0x00538780`),
`CScriptEventNB__ClearListenerEntry` (`0x005387b0`),
`CScriptEventNB__CreateListenerSet` (`0x00538860`),
`CScriptEventNB__DestroyAllEvents` (`0x005388d0`),
`CScriptEventNB__BaseDestructor` (`0x00538950`),
`CScriptEventNB__PostEvent` (`0x00538b70`),
`CScriptEventNB__HandleEventMessage` (`0x00538c70`),
`CScriptEventNB__UpdateWaypointFollowing` (`0x00538470`),
`CWorld__LoadScriptEvents` (`0x0050ac70`).

`CScriptEventNB` is a `CMonitor` subclass: `RegisterEventListener` creates the
listener argument's `+4` deletion-event set (`mov [esi+4],ebp` at
`0x00538b20`) with the same `Monitor.h:94` allocation a plain `CMonitor`
uses, and `ClearListenerEntry` calls
`CMonitor__DeleteDeletionEvent` (`0x0053880b`, mapped in
[`CMonitor.cpp.md`](CMonitor.cpp.md)).

## Open questions (cheapest falsifier first)

- The `ret 8` argument pair: which is the name key and which is the listener
  object — a two-argument call-site census of `RegisterEventListener` would
  separate them (search `tools\call_xref_scan.py 0x00538960`).
- The two post-lookup arms (`0x00538a05` found vs `0x00538a12` not found) and
  what the 0x19-byte node's first dword stores.
- `CScriptEventNB__PostEvent` → `HandleEventMessage` dispatch order and how
  `AddToTail` ordering becomes event delivery order.
