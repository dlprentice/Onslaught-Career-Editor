# CHeightField__TraceLineAgainstHeightfield

Status: active static function note
Last updated: 2026-08-18
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-18 from the pristine
specimen at file offset VA − 0x400000 with `tools/disasm_va.py` /
`tools/call_xref_scan.py`. The Ghidra database was not opened. Table name
is a research label, not an authored identity.

> Address: `0x00490a40`

## Contract

`thiscall`. Prologue saves `ECX` in `EBX` (`mov ebx, ecx` at
`0x00490a59`). Three stack args; one `ret 0xc` at `0x00490e00`
(`c2 0c 00`). Body `0x00490a40`–`0x00490e02` inclusive is 963 bytes,
SHA-256 `b2bb51add08610fe2e8a37c1472b4ebfd8e2100b2506bd91799d967617aded35`.
Specimen SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(2,506,752 bytes).

EAX reaching the epilogue is **0 or 1**:

| EAX | writer | path |
| --- | --- | --- |
| 1 | `mov eax, 1` at `0x00490ce6` | hit declared and the step is small (`fcomp [0x005d8574]`; `test ah, 0x41`); 16 bytes written to arg1 |
| 1 | `mov eax, 1` at `0x00490ddb` | self-call returned 0; FALSE warning printed; coarse 16 bytes still written |
| 1 | self-call EAX at `0x00490d8f` | `test eax, eax` / `jne 0x00490de8` — this body only ever returns 0/1, so the passthrough is 1 |
| 0 | `xor eax, eax` at `0x00490de6` | walk exhausted (`jg 0x00490de2`) or step count `< 0` |

No other `mov eax, imm32` exists on a path to `0x00490de8`.

Arg1 write on EAX=1 (`edx = [esp+0x9c]` at `0x00490cc8`, or `edi` on
the warning path): four dwords at `out+0/+4/+8/+0xc`. The warning path
is EAX=1 after an inner EAX=0.

Self-call (`0x00490d8f`): `mov ecx, ebx` at `0x00490d82`, then
`mov [esp+0x9c], 0`, then `E8` back into this body. Same this. Arg2 is
the original `[esp+0xa0]`.

## Inbound this

Fifteen `.text` `E8`s, zero `E9`. Fourteen external sites load
`ECX = 0x006fadc8` before the call. The class-1 consumer
`0x0050b0cc` places that immediate at `0x0050b094`; no instruction
between `0x0050b094` and `0x0050b0cc` writes ECX (only stack stores).
The fifteenth site is the self-call.

Already-pinned `0x0050b030` (not re-derived): `xor ebp, ebp` at
`0x0050b064`, `cmp eax, ebp` at `0x0050b0d1`, `je 0x0050b124` leaves
class 0, else `mov [edi+8], 1` at `0x0050b102`. This callee never
returns 2 or 3, so the class-1 store is exactly "this body returned 1".

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00490a40` | `CHeightField__TraceLineAgainstHeightfield` | `6aff 6888315d00 … 8bd9 … b801000000 … e8acfcffff 85c0 75 … b801000000 eb06 33c0 … c20c00` | thiscall; ECX→EBX; `ret 0xc`; EAX∈{0,1}; this imm `0x006fadc8` on every external inbound. HIGH on ABI, inbound set, ret, EAX polarity, and the `0x0050b030` zero/nonzero class-1 store. **Not** on authored enumerator names, CLine field names, or `this+0x13dc` / `+0x13e0`. |

Retail names EAX=0 as FALSE: the only string this body prints is
`0x0062d964`
`"Warning: LOS return FALSE in lower step l = %2.8f, step = %2.8f checks = %d on check = %d"`
via `0x00441740`, and only after the self-call returned 0.

Cheapest falsifier: file `0x00090a40` is not `6a ff 68 88 31 5d 00`,
**or** `0x00090a59` is not `8b d9`, **or** `0x00090ce6` / `0x00090ddb`
are not `b8 01 00 00 00`, **or** `0x00090d82` is not `8b cb`, **or**
`0x00090de6` is not `33 c0`, **or** `0x00090e00` is not `c2 0c 00`,
**or** `tools/call_xref_scan.py` on `0x00490a40` is not exactly the
fifteen `E8`s
`0x0044827e` / `0x00490d8f` / `0x004d8966` / `0x004d9c49` /
`0x004d9e9e` / `0x004ec857` / `0x004eca9b` / `0x004ecccb` /
`0x004ecef7` / `0x004ed11f` / `0x004ed36b` / `0x004ed5b2` /
`0x004ed7fb` / `0x004f6cc5` / `0x0050b0cc`, **or**
`0x0010b094` is not `b9 c8 ad 6f 00`, **or** `0x0010b0d1` is not
`3b c5`, **or** `0x0010b102` is not `c7 47 08 01 00 00 00`.

## Open

- What `0x006fadc8` is beyond the already-shared BSS this of
  `0x0047eb80`.
- Authored names for `this+0x1034` / `+0x102c` / `+0x13dc` / `+0x13e0`
  and for `line+0x20`.
- The four hit-declare predicates that jump to `0x00490cb3` (walked by
  child `t_34939b24`; not re-derived here).
- Callee `0x0047eb00` (`CHeightField__SampleInterpolatedHeight`) body.
