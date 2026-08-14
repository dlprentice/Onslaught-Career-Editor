# CRT/runtime P0 Ghidra scratch admission

Status: superseded receipt schema — v1 evidence retained; use the corrected v2 admission
Last updated: 2026-08-14
Summary: reproduces the corrected CRT22 run-c P0 cohort against the then-current
8,280-function db.18613 project and proves an exact structural-only
8,303-function result on two disposable replicas without authorizing promotion.

Verdict: **SCRATCH_READY_LIVE_FORBIDDEN**

> Superseded receipt note (2026-08-14): hostile review found that the v1
> boundary TSV inherited JPEG-oriented identity, CFG, normalization, and demo
> columns that its mutator did not mechanically populate. The structural result
> was not refuted, but this receipt shape is not admissible. The
> [corrected v2 admission](crt-runtime-p0-ghidra-scratch-admission-v2-2026-08-14.md)
> removes those fields, semantically validates every retained field, and reruns
> the complete campaign. The sealed v1 evidence remains byte-for-byte retained.

Evidence: **MEASURED** — pristine retail bytes, exact then-current body ownership,
corrected run-c plus two byte-identical fresh reproofs, PC-demo twins, two
persistent Ghidra replicas, full PRE/POST inventories, two rollback readbacks,
two path-containment controls, and a retained read-only backup/restore/open
proof.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Repository base: `1727d94ace29a60430d0982a188548d55aae5d1b`.
PRE project: 19 files / 186,960,773 bytes, canonical
`sha256<TAB>bytes<TAB>path` inventory SHA-256
`ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2`.
PRE database: `db.18613.gbf`, 68,337,664 bytes, SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

## Corrected structural cohort

The [23-row manifest](crt-runtime-p0-function-boundaries-2026-08-14.tsv) joins
exactly to corrected CRT22 `run-c` promotion cohort SHA-256
`bc16df601740afec41bdba306d7e02996171da1cc10d3491da38d6d022bdbf5a`.
The complete run-c output was independently regenerated twice from its frozen
analyzer and inputs; every regenerated artifact is byte-identical to run-c.
Superseded run-a/run-b results are not accepted as authority.

Independent admission checks establish:

- 23 sorted P0 entries in 24 pairwise-disjoint ranges, 1,131 pristine bytes,
  and 312 externally decoded instructions;
- exact pristine body hashes and zero overlap with all 8,400 ranges of the
  then-current 8,280-function state;
- a normalized- and CFG-equal PC-demo twin for every entry, rejoined to the
  exact demo specimen SHA-256
  `d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`;
- `0x00542720`, `0x005D0AD6`, and `0x005D0AEA` remain forbidden as function
  entries, and the P1 canary `0x005B8500` remains excluded; and
- `0x0045AC20` is exactly a five-byte thunk to the existing function at
  `0x0045AC30`.

This is boundary evidence only. It does not promote provider names, original
linker names, ABI, parameters, behavior, runtime causality, or rebuild parity.

## Scratch result

Both fresh db.18613 replicas independently passed dry run, apply, save, close,
and separate loaded readback. Their decisive full-function, program, focused
listing, and boundary exports are byte-identical.

| Export | Bytes | SHA-256 |
| --- | ---: | --- |
| PRE full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| PRE program metrics | 1,267 | `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| POST full functions | 7,177,146 | `2c1e2842fabd8be4cb840c35bc56074559041404e0c474fee50aad6e98cf4dc5` |
| POST program metrics | 1,267 | `7bce8becc7dc4cbbf9f513bec0effc75889e90079882c5623933aba335f59a4b` |
| POST boundary readback | 11,094 | `8d9999a7396378776c9ac8c664b0b5cc330fcd400a37ed0789ff614daa117485` |
| POST focused listing state | 1,033 | `ffedbd49109971f452ce0518cf7defd2ac70cdc8173830b5cccc58f08853d8bf` |

POST has exactly 8,303 internal functions and 8,424 function ranges. All
8,280 PRE rows are field-identical; the only added rows are the 23 manifest
entries. Instructions change from 550,991 to 551,069 and references from
234,495 to 234,506. The mutator proves before commit that every instruction
and reference delta is contained by an authorized body. Memory bytes, defined
data and its digest, user/analysis/imported symbol counts, stored non-function
symbol digest, comments and their digest, relocations, and every pre-existing
function field remain exact.

Ghidra represents the new default thunk at `0x0045AC20` with its existing
target's displayed name, `CFEPGoodies__BuildStaticGoodieDataTable`, and inherited
signature source. This is relational default-thunk presentation, not a promoted
name or signature: the mutator calls no semantic setter, the symbol source is
`DEFAULT`, and full-inventory comparison records zero changed pre-existing
names, signatures, or thunk flags.

No name, signature, calling convention, parameter, return type, comment, tag,
data definition, executable byte, or explicit reference is authorized or
applied. No live project, tracked project, canonical snapshot, pristine
specimen, or rebuild file was opened for mutation.

## Failure, recovery, and physical inventories

- A verified exact PRE backup was restored to a retained copy, opened read-only
  with analysis and commit disabled, and rehashed to the same 19-file tree.
- Forced failure after the first target and after a complete internally
  validated batch each reopen to byte-identical PRE boundary, full-function,
  program, and focused-listing exports.
- Separate external-output and external-READY probes both refuse before
  mutation because receipts must remain under the repository's ignored
  `local-lab/` tree; separate readbacks remain exact PRE.
- Each opened disposable project retains 19 files and is exactly 186,977,157
  bytes, a 16,384-byte physical-history increase. Per-project inventory hashes
  are pinned in the aggregate authority. Ghidra's rolling database filenames
  make these physical hashes replica-specific; their semantic POST exports are
  nevertheless byte-identical.

## Portable authority

The ignored formal lane is
`local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v1/`. Its create-new
`scratch-authority.ready.json` is 6,362 bytes, SHA-256
`4193509ebe7d6d64b9c851bbca1d4a439a75075f471ddd094f8aab519916c59b`.
It binds exact repository-relative POSIX paths, tools, evidence, project
inventories, and the retained tree excluding the self-referential receipt: 366
files / 1,783,236,011 bytes, SHA-256
`6cfef99aef8f8f972f54f04d9413e02337966eb9cd76edf9a51f18fc6da63935`.
Verification is read-only and repeats from a distinct repository root without
cache or tree mutation.

The later main revision `e7aa7548fe99ff7866f57955624968b097375e20` changes
only rebuild sources/tests/docs plus `reverse-engineering/delta.md` relative to
the pinned base. The tracked Ghidra tree, external-boundary map, PC-demo map,
and every load-bearing helper remain exact Git objects and bytes. The delta
file change is rebuild-status prose and is not consumed by this derivation or
admission. A fresh e7aa detached worktree accepted the candidate byte-for-byte,
passed all 11 focused tests (one retained-evidence replay skipped until the
ignored lane was copied), and passed diff/link checks. Compatibility receipt
SHA-256: `44cffda4519c3df174a432af00d35c273c49d3993d38385e5f2153984fc81a37`.

Reproduce the saved decision only where the ignored lane exists:

```powershell
python -I -B tools/ghidra_crt_p0_boundary_scratch_authority.py verify
```

The globally registered authority test skips only its retained-campaign replay
when ignored evidence is absent. Explicit `verify` remains fail-closed. Any
live or tracked admission requires a separate authorized backup/apply/separate-
readback/recovery ceremony and is deliberately outside this result.
