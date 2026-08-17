# CInfluenceNode function map

Status: active static function map
Last updated: 2026-08-17
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
| `0x0048c3b0` | `CInfluenceNode__CalculateInfluence` | `d9 819c000000 d8 81a4000000 33d2 d8 156c855d00 dfe0 f6c441 755a …` | Computes `float(this+0x9C) + float(this+0xA4)`, compares the sum against the float constant at `0x005d856c`, and branches on the `C0|C3` mask (`test ah,0x41`). MEDIUM: it proves an additive influence law over two fields; which arm is the active influence and the constant's value need a focused parity test or a second witness. |

## Open questions (cheapest falsifier first)

- `0x005d856c` constant value and the branch semantics of `CalculateInfluence`
  — read the float and instrument a focused rebuild parity test with the two
  arms.
- `this+0x94` (radius), `+0x9C`/`+0xA4` (influence summands), `+0x2C` bit 1,
  and the neighbor-link fields at `+0x7C`/`+0x84` — a retained-trace field-write
  probe can name them.
- The destructor at `0x0048c300`-ish called by the scalar deleting destructor.
