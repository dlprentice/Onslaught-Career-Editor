# CInfluenceNode function map

Status: active static function map
Last updated: 2026-08-23
Source File: `C:\dev\ONSLAUGHT2\InfluenceMap.cpp` (named by the shipped image at `0x0062d61c`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` at the
stated file offsets (VA − 0x400000 for .text). Class identity: RTTI
`.?AVCInfluenceNode@@` at `0x0062d5e0`, string `"CInfluenceNode"` at
`0x0062d658`; the runtime receiver of `CalculateInfluence` is `CInfluenceNode`
(`0x005dc050`) at all three observed call sites.
Summary: the class is a small RTTI-backed influence node. Its accessors are
byte-proven constants and field loads; the scalar deleting destructor frees
through the `0x009c3df0` pool shared with the `0x004e2b30` node family. Exact
influence semantics beyond the measured field arithmetic remain open.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048b5f0` | `CInfluenceNode__GetTypeName_0048b5f0` | `b8 58d66200 c3` | Returns the constant pointer `0x0062d658`, the shipped string `"CInfluenceNode"` — i.e. `const char* GetTypeName()`. HIGH. |
| `0x0048b600` | `CInfluenceNode__GetTypeId_0048b600` | `b8 1e000000 c3` | Returns the constant `0x1E` (30) — `int GetTypeId()`. HIGH. |
| `0x0048b610` | `CInfluenceNode__GetInfluenceRadius_0048b610` | `d9 81 94000000 c3` | Returns the float field at `this+0x94` via `fld [ecx+0x94]`. HIGH that it is a stored-radius getter; the field's meaning/units remain open. |
| `0x0048c2e0` | `CInfluenceNode__scalar_deleting_dtor` | `56 8bf1 e8 18000000 … f6 442408 01 74 0b 56 b9 f03d9c00 e8 …` | Standard MSVC scalar deleting destructor: calls the real destructor (`+0x18`), and when flags bit 0 is set frees `this` through pool `0x009c3df0`. HIGH on the shape; the destructor body itself is unexamined. |
| `0x0048c350` | `CInfluenceNode__DetachNeighborLinks_0048c350` | `53 8bd9 56 57 8d7b7c 8b07 85c0 894708 741b 8b30 …` | Walks the neighbor-link list head at `this+0x7C`, re-links the successor into `this+0x84` (`mov [edi+8], eax`), and detaches the removed node. MEDIUM: field roles are inferred from the relink shape, not yet double-witnessed. |
| `0x0048c390` | `CInfluenceNode__InitFromComplexThingInit_0048c390` | `8b442404 50 c74070 ffffffff 80612c fd e8 …` | Takes one stack argument; stores `-1` into `arg+0x70`, clears bit 1 of `this+0x2C` (`and byte [ecx+0x2c], 0xFD`), then calls an init helper. MEDIUM: the helper and the meaning of the flag remain open. |
| `0x0048c3b0` | `CInfluenceNode__CalculateInfluence` | `d9 819c000000 d8 81a4000000 33d2 d8 156c855d00 dfe0 f6c441 755a …` | Computes `float(this+0x9C) + float(this+0xA4)` and branches on the `C0|C3` mask (`test ah,0x41`) against the float constant at pristine VA `0x005d856c`, which reads `00 00 00 00` = **`0.0f`** (`.rdata`, file offset `0x1D856C`; specimen `74154bfa…`). Byte-proven branch law (105 instr, `0x0048c3b0..0x0048c54e`, `RET 0x4`; full 417-byte span SHA-256 `46e53f60d87e68446d717ccbc91730cc1735f3634bbe90e21fcecddf0771b19e`, re-read from the specimen and byte-identical to the W005 export encodings): for finite ordered self fields, sum ≤ 0.0 → neutral arm and sum > 0.0 → active arm; an unordered initial comparison also routes to the neutral arm. The neutral arm discards the tested self sum at `0x0048c425`, writes `this+0xB8 = 0.0f`, seeds two zero accumulators, and sums neighbor `+0x9C` separately from neighbor `+0xA4`. For finite ordered neighbor values it sets `+0xBC = 1` iff **Σneighbor(`+0x9C`) < Σneighbor(`+0xA4`)**, otherwise `+0xBC = 2` (including equal totals and an empty list); an unordered final compare sets x87 `C0`, so `test ah,0x01` routes to class 1. The active arm writes `+0xB8 = (+0x9C − +0xA4) / sum`, then, for finite ordered values, classifies stored `+0xB4`: `< 0.0` → `+0xBC = 1`, `== 0.0` → `+0xBC = 0`, `> 0.0` → `+0xBC = 2` (unordered `+0xB4` also routes to class 1 via `C0`). Epilogue: for ordered values, if the target/raw ratio at `+0xB8 == 0.0f` exactly, it is replaced by `-1.0f` (`0xBF800000`) when `+0xBC == 1` or `+1.0f` (`0x3F800000`) when `+0xBC == 2`; unordered `+0xB8` also follows that `C3`-set branch. Finally `smooth == 0` copies `+0xB8` into `+0xB4`; otherwise the current/smoothed value `+0xB4` moves toward target `+0xB8` by at most the step constant `0.05f` at `0x005d8578`. HIGH on every write/branch above (two channels: fresh specimen decode + W005 export). Field *roles* (`+0xBC` classification/state, `+0xB8` target/raw ratio, `+0xB4` current/smoothed value) and the “neutral”/“active” arm labels are inferred semantics, not byte-proven names. |

## Open questions (cheapest falsifier first)

- RESOLVED 2026-08-23 — the `0x005d856c` constant reads `00 00 00 00` = `0.0f`
  (pristine specimen `.rdata`, file offset `0x1D856C`; adverse controls: adjacent
  floats at `0x5D8560/64/68/70/74/7C` all nonzero), and both compare arms are
  enumerated with their writes in the `0x0048c3b0` contract row above. The same
  threshold serves the decay pass at `0x0048bf70` (subtract the `0.2f` constant
  at `0x005d8604` per step, re-test against `0.0f`). See
  `CInfluenceMap.cpp.md`. Remaining open: which semantic label
  ("active influence" versus "neutral") the game's consumers
  attach to each arm is an inference from field roles, not yet byte-proven; a
  focused runtime observation of one receiver (`+0x9C/+0xA4/+0xB4/+0xBC`, branch
  PC at `0x0048c3c9`/`0x0048c4a6`) under positive and negative controls remains
  the cheapest falsifier if that labeling ever matters.
- `this+0x94` (radius), `+0x9C`/`+0xA4` (influence summands), `+0x2C` bit 1,
  and the neighbor-link fields at `+0x7C`/`+0x84` — a retained-trace field-write
  probe can name them.
- The destructor at `0x0048c300`-ish called by the scalar deleting destructor.
