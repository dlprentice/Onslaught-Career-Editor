# PC existing-function body-fragment scratch admission

Status: sealed scratch result; no live or tracked Ghidra mutation
Date: 2026-08-14
Verdict: `STRICT_GO_FOR_LATER_TRACKED_PREPARATION`
Evidence: MEASURED — pristine retail bytes, exact current body ownership,
PC-demo normalized twins, retained runtime coverage, two saved replicas, two
adverse controls, complete inventories, and backup/openability proof
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Policy: `LIVE_FORBIDDEN`

## Scope

The exhaustive current `FUNCTION_FRAGMENT_CANDIDATE` class contains five gaps
inside five already existing PC retail functions. The reviewed
[five-row manifest](pc-function-body-fragment-repairs-2026-08-14.tsv) is 2,878
bytes, SHA-256
`c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0`.
It authorizes only exact body-range addition and bounded disassembly on an
isolated copy: no functions, names, signatures, comments, tags, data, bytes, or
other semantics may be added or changed.

| Existing owner | Exact repair | Bytes | Retained runtime union |
|---|---:|---:|---:|
| `CFEPMain__Process` (`0x00462640`) | `0x0046282B..0x00462B64` | 825 | 431/825 |
| `CGame__HandleEvent` (`0x0046FF10`) | `0x004700DA..0x004700F0` | 22 | 0/22 |
| `CHud__RenderTargetIndicatorOverlay` (`0x00482590`) | `0x00482725..0x00482741` | 28 | 14/28 |
| `CExplosionInitThing__SelectNextPathStepDirection` (`0x004BE420`) | `0x004BE82D..0x004BE93D` | 272 | 272/272 |
| `CDXTexture__CreateMipmaps` (`0x00559410`) | `0x0055954C..0x005595BB` | 111 | 0/111 |

The total admitted body gain is 1,258 bytes / 325 instructions. All five have
one unique normalized PC-demo counterpart within the mapped owner bracket.
The runtime join verified 77 of 86 retained coverage stamps; 9/86 unavailable
stamps are disclosed rather than treated as misses or positive coverage.

The original FEP candidate envelope ended at `0x00462B70`. Pristine bytes prove
that `0x00462B64..0x00462B70` is exactly twelve bytes of NOP alignment after the
terminal return, so those 12 bytes remain excluded from the function body.

## Scratch result

The exact db.18613 PRE state was 8,280 functions, 8,400 body-range components,
1,794,212 owned bytes, 550,991 instructions, and 234,495 references. Two fresh
positive replicas and separate saved readbacks produced the same POST state:
8,280 functions, 8,396 body-range components, 1,795,470 owned bytes, 551,014
instructions, and 234,478 references. Four inserted gaps bridge prior range
components; the FEP insertion only extends its prior single component. This is
why 1,258 owned bytes were gained while the component count fell by four.

All 8,275 non-target function rows were preserved field-for-field. Only the
expected body fields changed in the five owner rows; their metadata and ABI did
not. Memory bytes, defined data, stored non-function symbols, and comments were
identical. Both positive function inventories have SHA-256
`d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d`;
their program inventories have SHA-256
`b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e`.

Two forced-failure controls proved the one-target and all-target adverse paths.
Ghidra's nested script rollback did not undo the enclosing headless save, so
both adverse copies were discarded and restored from the independently
verified PRE backup before readback. External-output and tampered-manifest
containment refusals also passed. The 19-file / 186,960,773-byte backup opened
read-only and retained db.18613 SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

## Sealed authority and limits

The portable authority receipt is
`local-lab/ghidra-function-fragment5-range-scratch-20260814-v1/portable/authority/sealed-primary.ready.json`,
9,348 bytes, SHA-256
`a35f35ac99cd5d7251a86b7cf54c5aac2e2919870efca6566600045138571a04`.
An alternate-root replay produced the same receipt bytes. The frozen prover,
mutator, and authority hashes are respectively
`a9e5f02e8dddfa64f50aca7821e3afed483de6c349e6ad0ada06ba77e59020ed`,
`fe845a9df094eff4a1d9b36c9d4a6b141f049356499016a20a673071d492ec4c`,
and `1eed1350e38c4abbf840b2ae0fc1d444a4a818e154726c3a35ad347057f20678`.
This candidate was prepared against exact Git base
`e7aa7548fe99ff7866f57955624968b097375e20`.

The FEP runtime hit is corroboration from a non-READY wrapper, not a causal
contract. No retained range covers the CGame or texture fragments, whose body
ownership rests on static control flow plus the unique normalized demo twins.
The result assigns no new behavior or source equivalence.

The decision is GO only for this tracked evidence-and-tool candidate. It is a
strict NO-GO for live, shared, canonical, or tracked Ghidra mutation. Any such
promotion requires its own separately authorized backup, replica, apply,
readback, recovery, and exact-delta ceremony; this report grants none.
