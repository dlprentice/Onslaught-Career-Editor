# PC demo/retail exact-fingerprint frontier closure

Status: complete, bounded cross-build closure
Last updated: 2026-08-11
Evidence: MEASURED — exact specimen hashes, a complete normalized scan of the
demo `.text` section, complete body comparison, changed-operand classification,
mapped caller/code-pointer evidence, and an independent replay; UNKNOWN —
runtime execution, original source identity, complete semantics, and
reconstruction parity.
Verdict: 11 of the former 15 address-unmapped retail functions now have an
exact demo entry. The complete 8,136-function partition is 8,119
normalized-identical bodies, 13 bounded semantic divergences, and four
address-unmapped functions. All 8,132 mapped entries are accounted for.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The tracked machine-readable results are:

- [`pc-demo-retail-exact-fingerprint-closure-2026-08-11.tsv`](pc-demo-retail-exact-fingerprint-closure-2026-08-11.tsv),
  11 rows, 4,828 bytes, SHA-256
  `670fa5b8045119317655c805825a315574e61ebd49e4e388d0a9a10f277e853a`;
  and
- [`pc-demo-retail-address-unmapped-frontier-after-exact-fingerprint-2026-08-11.tsv`](pc-demo-retail-address-unmapped-frontier-after-exact-fingerprint-2026-08-11.tsv),
  four rows, 738 bytes, SHA-256
  `2219e1925b53cb0ea4421accd264242b82992344b03d76bbde6fcfb956127230`.

## Acceptance gate

The prior equal-delta checkpoint left 15 retail entries without a demo
address. This pass decoded each complete retail body, normalized only the
Capstone-reported encoded immediate and displacement spans, and searched every
byte offset in the demo `.text` section for that complete normalized body.
Candidate proximity was not an acceptance rule.

A mapping was accepted only when all applicable checks held:

1. the complete retail and demo bodies decode gaplessly with identical
   instruction boundaries and normalized bytes;
2. the whole-demo scan enumerates every exact candidate rather than stopping
   at the first occurrence;
3. a unique raw or normalized body, mapped caller/code pointer, mapped jump
   target, unique called body, or ordered equal block removes all candidate
   ambiguity;
4. every changed immediate and displacement has a non-conflicting paired
   classification; and
5. no accepted demo entry aliases the existing cross-build map or another new
   pair.

Eleven rows pass. They contain 1,884 body bytes and 545 instructions per build,
with 36 raw-different bytes, zero normalized-different bytes, 31 paired direct
transfers, and 17 changed operand pairs. The operand audit classifies six as
mapped external control targets, two as paired RTTI descriptor anchors, and
nine as paired zero-fill storage references. Nothing is left masked and
unexplained inside this cohort.

| Cross-build state | Before | Added | After |
| --- | ---: | ---: | ---: |
| Normalized-identical bodies | 8,108 | 11 | 8,119 |
| Bounded semantic divergences | 13 | 0 | 13 |
| Address-unmapped bodies | 15 | -11 | 4 |
| Mapped retail functions | 8,121 | 11 | 8,132 |
| Complete retail inventory | 8,136 | 0 | 8,136 |

The arithmetic is exact: `8,119 + 13 + 4 = 8,136`. No address-mapped body is
left in an unresolved comparison state.

## Accepted mappings

| Retail | Demo | Function | Bytes / instructions | Selection evidence |
| --- | --- | --- | ---: | --- |
| `0x00528B20` | `0x00529230` | `CTweakInt_SetNumViewpoints__ctor` | 45 / 11 | sole unclaimed exact body plus a normalized-identical static initializer that calls it |
| `0x00541110` | `0x00541720` | `JmpThunk_00466290` | 10 / 2 | mapped initializer carries the code pointer; selected thunk uniquely jumps to the mapped target |
| `0x00550830` | `0x00550EC0` | `JmpThunk_004530a0_00550830` | 10 / 2 | mapped initializer carries the corresponding thunk and static-object pointers |
| `0x00564FD6` | `0x00564107` | `FirstCall_CRT__FlushAllFileStreamsByMode_00564fd6` | 9 / 4 | sole exact wrapper calling the unique exact flush body and ending at its entry |
| `0x00564FDF` | `0x00564110` | `CRT__FlushAllFileStreamsByMode` | 164 / 66 | unique complete normalized body in demo `.text` |
| `0x005A1889` | `0x005A39A3` | `CFastVB__DispatchOp_NormalizeVec3_005a1889` | 240 / 64 | unique complete raw body in demo `.text` |
| `0x005A1979` | `0x005A3A93` | `CFastVB__DispatchOp_NormalizeVec4_005a1979` | 277 / 74 | unique complete raw body in demo `.text` |
| `0x005A2EE9` | `0x005A1A11` | `CFastVB__DispatchOp_Determinant4x4_005a2ee9` | 267 / 81 | unique complete raw body in demo `.text` |
| `0x005A32D4` | `0x005A1DFC` | `CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4` | 564 / 157 | unique complete raw body in demo `.text` |
| `0x005A38C0` | `0x005A3F80` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` | 149 / 42 | first duplicate in an ordered raw-identical block ending at a mapped upper anchor |
| `0x005A3980` | `0x005A4040` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980` | 149 / 42 | second duplicate in the same ordered block |

## How the ambiguous shapes were resolved

### Constructor and destructor thunks

The 45-byte constructor has two complete normalized candidates. Demo
`0x005291B0` is already paired with retail `0x00528AA0 CVar__Init`; demo
`0x00529230` is the only unclaimed candidate. A separate 32-byte
normalized-identical static initializer, retail `0x00550840` to demo
`0x00550ED0`, directly calls the selected pair. The constructor's two changed
descriptor operands point to paired eight-slot RTTI structures, and its two
changed storage operands point to corresponding unbacked `.data` zero-fill.

Each two-instruction destructor thunk has 96 shape-identical candidates, so the
shape alone proves nothing. For retail `0x00541110`, the mapped initializer
pair `0x005410F0 -> 0x00541700` carries demo code pointer `0x00541720`; that
candidate is also the only exact thunk that jumps to the already mapped demo
target `0x00541730`. For retail `0x00550830`, mapped initializer pair
`0x00550810 -> 0x00550EA0` carries code pointer `0x00550EC0` and the paired
static-object address. Both selected thunk targets are already accepted in the
cross-build function map.

### CRT wrapper and body

`CRT__FlushAllFileStreamsByMode` has exactly one complete normalized occurrence
in demo `.text`, at `0x00564110`. Its four changed calls all target existing
mapped pairs, and its five changed data references resolve to two paired
zero-fill globals. Of 17 shape-identical wrapper candidates, `0x00564107` is
the sole wrapper that calls this unique body and ends exactly where it begins.

### CFastVB bodies

The Vec3, Vec4, determinant, and matrix-multiply bodies are globally unique and
raw-byte-identical. The two transform bodies are deliberately identical to
each other, so each has two candidates. Their containing retail block
`[0x005A38C0,0x005A3A40)` and demo block
`[0x005A3F80,0x005A4100)` are raw-identical across all 384 bytes, SHA-256
`f0b5eb40ca0eb3f01a980cc52970f21f900ff7b9d9d3b1a109a6ce4c8bf39b35`.
The block preserves body order and `0xC0` spacing and ends at the already mapped
pair `0x005A3A40 -> 0x005A4100`; this selects the two addresses without naming
from proximity alone.

## Remaining address frontier

The exact scan deliberately abstains on four rows:

| Retail | Function | Scan result | Next instrument |
| --- | --- | --- | --- |
| `0x004655D0` | `con_fmv_play` | no complete normalized candidate | command registration/string-pointer alignment and edition-specific CFG |
| `0x0046CA70` | `CGame__ShutdownRestartLoop` | no complete normalized candidate | source-guided lifecycle call-sequence alignment |
| `0x0046DC30` | `CGame__RestartLoopRunLevel` | no complete normalized candidate | source-guided lifecycle call-sequence alignment |
| `0x005D2930` | `Unwind@005d2930` | 59 generic exact candidates | MSVC exception metadata and owning-parent funclet alignment |

Absence from the exact cohort is not evidence that the demo lacks an analogous
function. These rows require a different discriminator because three have
edition-specific instruction shape and the unwind body is compiler-generic.

## Reproduction and limits

The ignored analyzer package is
`local-lab/pc-demo-retail-final15-fingerprints-20260811-v1/`. Its resolver is
32,842 bytes, SHA-256
`e97c7e90899b8712bd94cd6b1e2a19d4048ff16822f772131153badd8a5aee31`;
the 17-row operand audit is 2,706 bytes, SHA-256
`1d73fdd37ed5ec4795ba59f397ecd10cc9db7c38b90184468e1c1591185c7e81`;
and the result receipt is 2,878 bytes, SHA-256
`9036743a35e55a2053c0bbd12a6b7c10d80ac995184bfcb938735885c645c51f`.

A separately implemented replay lives under
`local-lab/pc-demo-retail-final15-exact-verify-20260811-v1/`. The verifier is
19,573 bytes, SHA-256
`a0c82b7504d1cb983e613e025adf9686578d4205e221f5366e549cccc84353b3`;
its 2,537-byte receipt has SHA-256
`186a9d0230013572af7c0d7f4fef8efa488cc68af3a1144c7ab93c366cb080ef`
and verdict `PASS`.

This work made no live or tracked Ghidra mutation and no rebuild change. It
proves specimen-specific entry correspondence and complete normalized body
identity for the 11 listed functions. It does not establish that they execute
in a particular scenario, that their masked operands have universal semantics,
that the original source was identical, or that reconstruction parity exists.
