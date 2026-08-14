# JPEG/IJG callback Ghidra scratch admission

Status: active — sealed scratch candidate; live and tracked Ghidra mutation forbidden
Last updated: 2026-08-14
Summary: reproduces 24 exact IJG v6b algorithm bodies against the current
8,280-function db.18613 project and proves a structural-only 8,304-function
result on two disposable replicas without authorizing promotion.

Verdict: **SCRATCH_READY_LIVE_FORBIDDEN**

Evidence: **MEASURED** — pristine retail bytes, exact current function-body
ownership, two byte-identical PC-demo reproofs, two persistent Ghidra replicas,
full PRE/POST inventories, two rollback readbacks, two path-containment
controls, and a retained read-only backup/restore/open proof.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Repository base: `d5e238cdc43f3dd03dba120c6236c9f33e791656`.
PRE project: 19 files / 186,960,773 bytes, canonical
`sha256<TAB>bytes<TAB>path` inventory SHA-256
`ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2`.
PRE database: `db.18613.gbf`, 68,337,664 bytes, SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

## Corrected structural cohort

The [24-row manifest](jpeg-ijg-callback-function-boundaries-2026-08-14.tsv)
reproduces twice, byte for byte, from the retained analyzer and exact current
8,280-function body-range export:

- 24 pairwise-disjoint functions in 38 body ranges and 14,817 body bytes;
- 4,497 externally decoded instructions and 4,745 CFG edges;
- 24/24 PC-demo normalized-body and CFG twins, including 14 raw-byte twins;
- zero body-byte overlap with any current 8,280-function body and zero
  pairwise cohort overlap; and
- all 24 bounded as `EXACT_IJG_V6B_SOURCE_ALGORITHM` against their pinned IJG
  v6b source files and algorithms.

These are provider-qualified algorithm identities, not recovered original
linker names, signatures, ABI contracts, runtime contracts, or reconstruction
parity. The scratch mutation therefore creates only default `FUN_` boundaries.

The original 23-target lead omitted one callback and treated `0x005B6900` as a
possible boundary. The corrected body is
`0x005B6800..0x005B6A86`, 646 bytes / 203 instructions, body SHA-256
`dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8`,
with the exact PC-demo twin at `0x005B6ED0`. Its bounded provider identity is
`LIBJPEG6B__h2v2_smooth_downsample`.

`0x005B6900` is neither data nor a function entry. It is the final byte of the
three-byte `0F B6 00` `MOVZX EAX,byte ptr [EAX]` instruction beginning at
`0x005B68FE`. The current PRE listing held a false orphan decode beginning at
`0x005B6900`; both independent POST readbacks place the byte only inside the
instruction at `0x005B68FE` and function `FUN_005b6800`.

The nearby non-function remnants remain outside the cohort: `0x005B4EB0`
contains seven preserved DWORD switch-table entries, while `0x005B4ECC`
contains four preserved NOP alignment bytes. The mutator does not alter or
reclassify either region.

## Scratch result

Both fresh db.18613 replicas independently passed dry run, apply, save, close,
and separate readback. Their boundary, full-function, program, and focused
listing-state exports are byte-identical.

| Export | Bytes | SHA-256 |
| --- | ---: | --- |
| PRE full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| PRE program metrics | 1,267 | `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| POST full functions | 7,177,775 | `dce886c9ee9ddee96a2e27baff616723211b7818c2d9277e19e3202d6a307804` |
| POST program metrics | 1,267 | `b154869020140b266e06dd5ef07d4fd99c71e328a1ffb1223d4d4c6db4b3a5e9` |
| POST boundary readback | 12,769 | `956426b50f1997227828958e38399ba1106bbfdb36f4503c769338a387fffdfb` |
| POST correction-state readback | 955 | `55944e2cc03902c8f99d273aaa51ca98f1bfdedbe129bf18ad4441d21c6e0271` |

The POST replicas contain 8,304 functions, 551,032 instructions, and 234,484
references, versus PRE 8,280, 550,991, and 234,495. The +41 instruction and
-11 reference net changes reflect bounded replacement of existing orphan or
misaligned decoding inside the admitted bodies; the 24 bodies themselves
contain the pinned 4,497 instructions. Undefined data decreases by 120 bytes
and default/other symbols increase by one. Memory bytes, defined-data digest,
stored non-function-symbol digest, comments digest, and every field of every
one of the 8,280 PRE function rows remain exact.

No name, signature, calling convention, parameter, return type, comment, tag,
data definition, executable byte, or explicit reference is authorized or
applied. No live project, tracked project, canonical snapshot, campaign
generation, or rebuild file was opened for mutation.

## Failure and recovery controls

- A verified PRE backup was restored to a retained copy, opened read-only with
  analysis and commit disabled, and rehashed to the exact 19-file project.
- Forced failure after the first target reopened to exact PRE full-function,
  program, boundary, and correction-state exports.
- Forced failure after a complete internally validated batch also reopened to
  those same exact PRE exports, proving exact PRE recovery after a complete
  validated batch, an inner rollback request, and the outer script failure.
- Separate external-output and external-READY probes both refused publication
  before mutation because receipts must remain under the repository's ignored
  `local-lab/` tree.

## Portable authority

The ignored formal lane is
`local-lab/ghidra-jpeg24-boundary-current-scratch-20260814-v1/`. Its final
create-new `scratch-authority.ready.json` receipt is 7,077 bytes, SHA-256
`573c550c7197e15cc098ff0dd09ce55467c7bae95ca2ec4efcf9e045e0954b63`.
The sealed evidence tree excluding that self-referential receipt contains 258
files, 1,013,137,450 bytes, SHA-256
`7c3df3b029b3f175a41bbbf698c1b47dfd5f18c02f7616494794225f3dc2058c`.

The aggregate receipt binds exact relative POSIX paths and stamps for its
manifest, tools, and decisive evidence. It verifies unchanged from the source
worktree and a distinct copied repository root. Retained inner Ghidra and
backup logs preserve their absolute execution history and are not themselves
rewritten for portability.

Reproduce the saved decision only where the ignored lane exists:

```powershell
python -I -B tools/ghidra_jpeg_callback_boundary_scratch_authority.py verify
```

The globally registered authority test skips only the retained-campaign replay
when ignored evidence is absent. Explicit `verify` remains fail-closed. Any
live or tracked admission requires a separate authorized backup/apply/separate-
readback/recovery ceremony and is deliberately outside this result.
