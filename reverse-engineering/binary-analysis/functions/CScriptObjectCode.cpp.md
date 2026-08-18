# CScriptObjectCode function map

Status: active static function map
Last updated: 2026-08-18 (CInstructionOP_RETURN vtable[+8]/[+0] pin;
CMissionScriptObjectCode trailer fields +0x5c/+0x60/+0x6c)
Source File: `C:\dev\ONSLAUGHT2\MissionScript\ScriptObjectCode.cpp` (the
VM's `__FILE__` chain is established by the adjacent
[`ScriptObjectCode.cpp.md`](ScriptObjectCode.cpp.md) wave receipts) | Binary:
BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000 with `tools/disasm_va.py`; embedded strings read
from the same image. Function names are the live Ghidra name table
(db.18627 lineage); the byte contracts below are independent of the names.

## Shape

`CScriptObjectCode` is the mission-script stack-VM instance; the shipped
global singleton is `0x0089c5e0` (every teardown arm in
[`IScript.cpp.md`](IScript.cpp.md) loads it). Measured field map from the
bodies below:

| Offset | Field | Witness |
| --- | --- | --- |
| `+0x08` | current `CMissionScriptObjectCode*` | `mov [esi+8],edi` in `CallEvent`/`CallEventDirect`; constructed at `0x00538ec0` |
| `+0x0c` | operand stack head | `lea ecx,[esi+0xc]` fed to `Push`/`RestoreStack`/`ClearStack` |
| `+0x20c` | stack depth | compared against `+0x21c` at exit; zeroed on the stop path |
| `+0x210` | running flag | `Run`'s re-entry guard sets 1, clears 0 at every exit |
| `+0x214` | instruction pointer (PC) | written by `GotoInstruction`/`CallEvent`/`Run` |
| `+0x218` | flags (printed by the trace) | trace format `"-> %4d stack size = %d flags = %d"` |
| `+0x21c` | saved stack base | snapshot before `Run`; the exit check compares `+0x20c` to it |
| `+0x220` | stop flag | set to 1 by the 10,000-step guard; `Run` exits when nonzero |
| `+0x224` | return-depth guard | `Run` zeroes it on entry; exits when a `0x17` instruction is fetched and this field is `<= 0` |

### Event object (`CMissionScriptObjectCode`, 0x70 bytes)

`CallEvent`'s `eventObj` is the 0x70-byte record `CWorld__LoadScriptEvents`
allocates (`world.cpp:195`) and constructs via
`CMissionScriptObjectCode__ctor` (`0x00538ec0`; only direct `E8` is
`0x0050ad20`). The ctor installs vptr `0x005e4f54` and the `__FILE__`
pointer used for its allocations is `0x00650040` =
`C:\dev\ONSLAUGHT2\MissionScript\ScriptObjectCode.cpp`.

| Offset | Field | Witness |
| --- | --- | --- |
| `+0x00` | vptr `0x005e4f54` | `mov [esi],0x5e4f54` at `0x00538f14` |
| `+0x04` | code-array (flex) head | `lea ebx,[esi+4]; call 0x004241a0`; `Run` fetches `code = [obj+4]` |
| `+0x14` | 13-dword event-id → PC table | ctor reads 13 dwords through `CDXMemBuffer__Read` (`0x00548570`); `CallEvent` indexes `[obj+0x14+eventId*4]` |
| `+0x48` | `CSPtrSet` of `CEventFunction` | ctor `call 0x004e5840` then `CSPtrSet__AddToTail` (`0x004e5b20`) |
| `+0x58` | symbol table | ctor stores the `0x00539770` reader result (`mov [esi+0x58],eax` at `0x00538fab`) |
| `+0x5c` | preamble-present dword (serialized) | ctor `lea eax,[esi+0x5c]; push 4; push eax; call 0x00548570` at `0x00539011`; `CallEvent` runs PC=0 iff this is nonzero and `+0x6c == 0` |
| `+0x60` | per-step trace dword (serialized) | ctor `lea edx,[esi+0x60]; push 4; push edx; call 0x00548570` at `0x00539004`; `Run` does `cmp dword [obj+0x60],1` at `0x00539ba4` |
| `+0x64` | instruction-count copy | ctor `mov ecx,[esi+0xc]; mov [esi+0x64],ecx` at `0x0053901e` |
| `+0x6c` | preamble-already-run flag | ctor zeroes it (`mov [esi+0x6c],ebp` with `ebp=0` at `0x00538f1a`); `CallEvent`/`CallEventDirect` write `1` after the PC=0 preamble |

`CScriptObjectCode__Clone` copies the four trailer dwords on the success
path (`mov [esi+0x6c],[ebx+0x6c]` / `+0x60` / `+0x5c` / `+0x64` at
`0x00539165..0x0053917f`) and zeroes `+0x5c` only on the allocation-failure
arm at `0x00539265`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538ec0` | `CMissionScriptObjectCode__ctor` | `6aff 6812755d00 … c706544f5e00 896e6c e84ef60000 … 8d5660 6a04 52 8bcf e85ff50000 8d465c 6a04 50 8bcf e852f50000 8b4e0c 89 4e64 … c20400` | `ret 4`; arg = `CDXMemBuffer*`. Inits flex array at `+4` and `CSPtrSet` at `+0x48`, installs vptr `0x005e4f54`, zeroes `+0x6c`, reads the instruction stream through `CAsmInstruction__SpawnFromOpcode` (`0x0052d3d0`), reads 13 event PCs into `+0x14`, stores the symbol table at `+0x58`, appends each `CEventFunction` (`0x0052fa70`) onto `+0x48`, then reads the two serialized trailer dwords into `+0x60` then `+0x5c` and copies the flex count to `+0x64`. HIGH on the layout and the two trailer reads. |
| `0x0052da00` | `FUN_0052da00` | `b817000000 c3` at file offset `0x0012da00` | Zero-arg `ret`. `mov eax,0x17; ret` — a 32-bit EAX constant 23. This is `CInstructionOP_RETURN` vtable `0x005e4bd0[+8]`, the getter `Run` calls via `call [edx+8]` at `0x00539b5e` and then `cmp eax,0x17`. The same address is also stored at `.rdata` `0x005dab54` (a second, non-RETURN vtable), so the thunk is not class-exclusive; the current name `FUN_0052da00` is the honest label. HIGH on the RETURN-slot contract and the return width (32-bit EAX, not a byte). |
| `0x0052e0f0` | `CInstructionOP_RETURN__ExecutePop` | `578b7c2408 8b8724020000 85c0 7e72 … 898724020000 e85db30000 … ff5030 898714020000 … c7 00 f84a5e00 c7400401000000 e8c1b20000 … c20c00` | `ret 0xc`; `CInstructionOP_RETURN` vtable `0x005e4bd0[+0]`, the executor `Run` calls via `call [edx]` at `0x00539b9f` with `(vm, &stack, symbols)`. If `[vm+0x224] <= 0` it returns immediately. Else it decrements `+0x224`, `Pop`s (`0x00539470`), reads a scalar through the element's `vtable[+0x30]`, writes that value to `vm+0x214` (PC), deletes the element, and pushes an 8-byte `CInt` (`vptr 0x005e4af8`, value 1). HIGH on the bytes. This arm is reachable only after something has incremented `+0x224`; `Run` itself zeroes that field on entry, so a top-level `0x17` exits the loop *without* calling this function. |
| `0x00539910` | `CScriptObjectCode__CopyState` | `8b7c240c 8bf1 8b4708 8d570c 894608 8b8f14020000 898e14020000 52 8d4e0c e81afaffff … 8b8718020000 898618020000 … c7861002000000000000 8bc6 … c20400` | `ret 4`, one arg = source. Copies `[src+8]`, `[src+0x214]` (PC), calls `CScriptObjectCode__RestoreStack` (`0x00539350`) with `(dst+0xc, src+0xc)`, then copies `+0x218`, `+0x220`, `+0x21c`, `+0x224`, and zeroes the running flag `+0x210`. Returns `this`. HIGH. |
| `0x00539980` | `CScriptObjectCode__Reset` | `83c10c e958faffff` | Zero-arg tail: `add ecx,0xc; jmp 0x005393e0` = `CScriptObjectCode__ClearStack(this+0xc)`. HIGH. |
| `0x00539990` | `CScriptObjectCode__CallEvent` | `8b860c020000 85c0 7412 6860016500 6880f56600 e8937df0ff … 8b7c240c 897e08 8b476c 85c0 752b 8b475c 85c0 7424 c7861402000000000000 … e81e010000 c7476c01000000 … 8b449114 83f8ff 898614020000 7525 …` | `ret 0x10`, four args `(eventObj, eventId, args[], argCount)`. If the operand stack is not empty (`[this+0x20c] != 0`) prints `"FATAL ERROR: stack not empty on call"` (`0x00650160`). Stores `[this+8] = eventObj`; if `eventObj->[+0x6c] == 0` and `eventObj->[+0x5c] != 0` runs the preamble (`PC = 0`, `Run`, then `eventObj->[+0x6c] = 1`). Resolves the entry `eventObj->[+0x14 + eventId*4]`; `-1` means no handler, in which case it deletes each arg element via `call [elem->vtable][0](elem, 1)` and returns. Otherwise sets `PC = entry`, pushes each arg with `CScriptObjectCode__Push` (`0x00539420`), and calls `Run`. HIGH on the dispatch; `+0x5c`/`+0x6c` are now owned (see the event-object table) and the preamble-present *meaning* of a nonzero `+0x5c` stays MEDIUM. |
| `0x00539420` | `CScriptObjectCode__Push` | `8b4c2408 8b8600020000 890c86 8b8e00020000 41 898600020000 3d80000000 7e1f 6878006500 6880f56600 e8eb82f0ff … 48 898600020000 … c20400` | `ret 4`; `this` = the stack head (`this+0xc` of the VM). `sp = [head+0x200]; [head + sp*4] = arg; sp++`; if `sp > 0x80` (128) it prints `"FATAL ERROR: Stack out of memory"` (`0x00650078`) and decrements the depth back (the overflowing push is rejected). HIGH — the 128-slot stack ceiling the schema records is byte-verified here. |
| `0x005393e0` | `CScriptObjectCode__ClearStack` | `8b8600020000 85c0 7423 … 8b4c86fc 85c9 7406 8b11 6a01 ff12 … 48 898600020000 75dd` | Zero-arg; walks the stack top-down, `call [elem->vtable][0](elem, 1)` for each non-null element, and zeroes the depth `+0x200`. HIGH. |
| `0x00539350` | `CScriptObjectCode__RestoreStack` | `8b8600020000 85c0 7423 … 8b7c240c 33c9 8b8700020000 898600020000 7e2c … 8b2c02 8928 … c7870002000000000000 … c20400` | `ret 4`; `this` = destination head, arg = source head. First clears the destination (the same delete loop as `ClearStack`), then copies the source's depth and each element dword `[src + i*4] → [dst + i*4]` (a **shallow move** of the pointer array), and zeroes the source depth. HIGH. |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` | `8b7c2410 8bf1 897e08 8b476c 85c0 7529 8b475c 85c0 7422 c7861402000000000000 8b860c020000 89861c020000 e86b000000 c7476c01000000 … 8b5c241c 8b8e0c020000 85db 898e1c020000 7e19 … e85ef9ffff … 8b442414 8bce 898614020000 e826000000 …` | `ret 0x10`, four args `(eventObj, entryPC, args[], argCount)`. Same preamble as `CallEvent` (PC = 0 + `Run` + `eventObj->[+0x6c] = 1` when `+0x6c == 0` and `+0x5c != 0`); snapshots the stack base (`+0x21c = +0x20c`); pushes each arg; sets `PC = entryPC` (taken directly, not looked up); calls `Run`. This is the entry `CEventFunction__Execute` uses for named callbacks. HIGH. |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` | `8b442404 898114020000 e811000000 c20400` | `ret 4`: `PC = arg; Run()`. HIGH — the jump-into-script primitive behind `IScript`'s 2001 teardown. |
| `0x00539b00` | `CScriptObjectCode__Run` | `b801000000 398610020000 7516 6808026500 6880f56600 e87f7df0ff … 8b8e14020000 898610020000 8b4608 … 8b5004 8b4058 8b3c8a … 8b17 8bcf ff5208 83f817 750e 8b8624020000 85c0 0f8e94000000 … 8b9e14020000 8d4e0c 8d4301 898614020000 … 50 51 56 8bcf ff12 …` | The interpreter loop. Re-entry guard: if `[this+0x210] == 1` prints `"ERROR: VM tryin to run VM whilst it was already running."` (`0x00650208`) and returns; else sets the flag. Each step: `instr = code[PC]` with `code = [obj+4]`, `symbols = [obj+0x58]`; `opcode = instr->vtable[+8]()` (32-bit EAX); if `opcode == 0x17` and `[this+0x224] <= 0` → exit **without** calling the executor; if the stop flag `[this+0x220] != 0` → exit; otherwise `PC++` and `instr->vtable[+0](this, &stack[this+0xc], symbols)`. A `0x2710` (10,000) instruction guard prints `"FATAL ERROR :Infinite loop in script!"` (`0x006501bc`) and sets the stop flag. If `[obj+0x60] == 1` it traces `"-> %4d stack size = %d flags = %d"` (`0x006501e4`) per step. On exit: stop path zeroes `+0x20c`; normal path compares stack depth `+0x20c` against the saved base `+0x21c` and prints `"FATAL ERROR:  stack was different size when exiting"` (`0x00650188`) on mismatch. HIGH. |

## Wiring with the rest of the script system

- `IScript`'s message arms call the singleton: 2001 →
  `CopyState`/`Reset`/`GotoInstruction`; 2002 → `Reset`/`CallEvent`
  ([`IScript.cpp.md`](IScript.cpp.md)).
- `CEventFunction__Execute` (`0x0052fda0`) stages its parameter wrappers and
  calls `CallEventDirect` ([`EventFunction.cpp.md`](EventFunction.cpp.md)).
- `CMissionScriptObjectCode__ctor` (`0x00538ec0`) is the derived loader
  (`CWorld__LoadScriptEvents` constructs it per script file; see
  [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md)).

## Instruction factory — `CAsmInstruction__SpawnFromOpcode` (`0x0052d3d0`)

The 27-opcode dispatch is byte-settled against the
[VM schema](../missionscript-vm-datatype-opcode-schema.v1.json):

1. `mov ecx,[esp+8]` takes the bytecode reader; `lea eax,[esp+0xc]` reuses the
   argument slot as a 4-byte buffer and `call 0x00548570`
   (`CDXMemBuffer__Read`) reads the instruction **attribute** (the "second
   dword" the schema names).
2. `mov eax,[esp+8]; cmp eax,0x1a; ja 0x52d8cb` bounds-checks the **opcode
   argument** (arg0, already decoded by the caller) against 26; out of range
   prints `"FATAL ERROR: uknown instruction in spawn"` (`0x0064cab8`, the
   shipped typo) and returns null.
3. `jmp dword [eax*4 + 0x0052d8e4]` dispatches through the 27-entry jump table
   (entries `0x0052d3f7` … `0x0052d89b`, one case body per opcode).
4. Each case allocates **0xc** bytes (`AsmInstruction.cpp` `__FILE__`
   `0x0064c5c4`, per-case `__LINE__` `0x57`/`0x58`/… rising), stores the
   attribute at `instr+0x04`, and installs the per-opcode vtable at `instr+0`
   with the exact law **`vtable = 0x005e4d40 − 0x10 × opcode`** — verified for
   all 27 opcodes against the schema's vtable column (`NOOP_0` `0x005e4d40`
   down to `PUSHPC` `0x005e4ba0`).

So an instruction object is a 12-byte `{vtable, attribute}` pair, and
`Run`'s two virtual calls are `vtable[+8]` (opcode getter) and `vtable[+0]`
(executor) over that pair. The `0x10` stride is three method pointers plus
the adjacent class's Complete Object Locator: `vtable[-4]` of RETURN is
`0x00618f80`, and `vtable[+0xc]` is POINTER's COL `0x00618e90`, not a fourth
RETURN virtual.

## Instruction class pin — `CInstructionOP_RETURN` (opcode `0x17`)

RTTI name `.?AVCInstructionOP_RETURN@@` at `0x0064c8a0`. Vtable
`0x005e4bd0` (file offset `0x001e4bd0`), three slots, zero direct `E8`/`E9`
callers (virtual only):

| Slot | Address | Current name | Body |
| --- | --- | --- | --- |
| `+0` | `0x0052e0f0` | `CInstructionOP_RETURN__ExecutePop` | nested-return executor (`ret 0xc`) |
| `+4` | `0x0052d9d0` | `CInstructionOP_RETURN__VFunc_1_0052d9d0` | clone: alloc `0xc` (`asminstruction.h:114`), install the same vptr `0x005e4bd0`, copy `[this+4]` |
| `+8` | `0x0052da00` | `FUN_0052da00` | `mov eax,0x17; ret` — 32-bit opcode getter |

The NOOP class (`vtable 0x005e4d40`) uses the same three-slot shape with
`SharedVFunc__ReturnZero_00405930` (`xor eax,eax; ret`) at `[+8]`, which is
the opcode-0 instance of the same getter-width law. Cheapest falsifier: a
`CInstructionOP_RETURN` instance whose `vtable[+8]` is not `0x0052da00`, or
`FUN_0052da00` returning anything other than `0x17` in EAX.

The getter width is therefore a 32-bit integer in EAX. `Run`'s
`cmp eax,0x17` is a full-dword compare, not a byte test.

A prior copied-runtime proof that serialized `+0x60 == 1` (and not `0` or
`2`) enables the per-step trace on a disposable Level 100 copy lives at
`local-lab/vm-trace-pilot-2026-08-02/vm-trace.ready.json` (SHA-256
`ad373947273ad083c9c37a53aba876e28399cba26821ae067df59d207e4ced09`,
re-hashed this slice). Its static-anchor bytes
`8d56606a04528bcfe85ff50000` / `8d465c6a04508bcfe852f50000` /
`837a60017521` match the ctor/`Run` reread above. The 136-line runtime
count was **not** re-executed here.

## Stack discipline (settled this slice)

The operand stack is an **inline 128-dword array**: head at `+0xc` of the VM
object, depth at `[head+0x200]` (the `+0x20c` field `Run` and `CallEvent`
already read). `Push` stores at `[head + depth*4]` and rejects past 128 with
`"FATAL ERROR: Stack out of memory"`; `ClearStack` and `RestoreStack` delete
each resident element through its `vtable[0](elem, 1)` (the shared
value-delete convention), and `RestoreStack` then shallow-moves the source's
pointer array into the destination.

## Open questions (cheapest falsifier first)

- Who increments `vm+0x224` so `CInstructionOP_RETURN__ExecutePop` is
  reachable? `Run` zeroes the field on every entry. Cheapest: byte-map
  `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40` (`0x0052ec40`) and any sibling
  that writes `[reg+0x224]`.
- `+0x5c` is a serialized dword that gates the one-time PC=0 preamble. Its
  authored name and any meaning beyond "nonzero ⇒ run preamble" are still
  open. Cheapest: read the two trailer dwords out of one shipped
  `MissionScripts/level***` record and watch `CallEvent` skip or take the
  preamble.
- The 13 event-id slots at `eventObj+0x14`. IScript's 2002 arm already
  calls `CallEvent(..., 2, &0x0089c528, 0)` — slot 2 is one named user;
  the other twelve are not.
- The second `.rdata` holder of `FUN_0052da00` at `0x005dab54` is not a
  RETURN vtable. Class identity of that table is unclaimed.
