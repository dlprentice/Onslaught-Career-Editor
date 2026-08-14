# CRT EH parent-range Ghidra scratch admission

Status: sealed scratch result; no live or tracked Ghidra mutation
Last updated: 2026-08-14
Summary: closes one 25-byte exception-filter/handler hole inside the existing
`CRT__LongJmpProbe_NoOp` body on two disposable db.18616 replicas.
Verdict: **STRICT_GO_FOR_LATER_LIVE_PROMOTION_PREPARATION**
Evidence: **MEASURED** — pristine retail and demo bytes, exact scope-table
lineage, corrected static replicas, two saved Ghidra replicas, full PRE/POST
function inventories, forced-failure controls, containment refusals, and
backup/openability proof.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
Policy: `LIVE_FORBIDDEN`

## Structural decision

The existing function at `0x005D0A9F` had two body components:
`0x005D0A9F..0x005D0AD6` and `0x005D0AEF..0x005D0B04`. The intervening
25 bytes are not padding and are not two new functions:

- `0x005D0AD6..0x005D0AEA` is the eight-instruction exception filter. It
  returns whether the exception code is `0xC0000005`.
- `0x005D0AEA..0x005D0AEF` is the two-instruction handler that restores the
  saved stack pointer and clears `EAX`.
- Retail scope table `0x0060C170` names the filter and handler for parent
  `0x005D0A9F`; demo scope table `0x0060D170` names the exact counterparts at
  `0x005D11D6` and `0x005D11EA`.
- Corrected static run-c/run-d reproduce normalized- and CFG-equal demo
  evidence and require `REPAIR_EXISTING_FUNCTION_BODY` while forbidding new
  entries at `0x005D0AD6` and `0x005D0AEA`.

The reviewed [one-row manifest](crt-eh-parent-range-repair-2026-08-14.tsv) is
464 bytes, SHA-256
`272062f47b6ef2c45a29e1bbe07a0f186ac1ae6ad8259bfd4f0a3d33edcf8831`.
It permits only body-range addition and bounded disassembly on an isolated
copy. It authorizes no new function, name, signature, ABI, comment, tag, data
definition, byte change, or manual reference.

## Scratch result

PRE is the exact current 19-file / 187,009,925-byte tracked project with
`db.18616.gbf` at 68,354,048 bytes, SHA-256
`f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc`.
Two fresh copies independently passed dry/apply/save/close/separate readback:

| Metric | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Functions | 8,327 | 8,327 | 0 |
| Body-range components | 8,458 | 8,457 | -1 |
| Owned `.text` bytes | 1,811,418 | 1,811,443 | +25 |
| Program instructions | 551,133 | 551,143 | +10 |
| References | 234,478 | 234,478 | 0 |

The repaired owner becomes one contiguous `0x005D0A9F..0x005D0B04` body.
All 8,326 non-target function rows are field-identical. The target changes only
body bytes/digest, component count, and instruction count: 76 → 101 bytes,
two components → one, and 28 → 38 instructions. Both POST full inventories are
7,192,981 bytes, SHA-256
`08886e03b846668681301f0f2ec2ba9ac1af0463faa1835c57abe9e717ebd866`.
The PRE inventory is 7,192,980 bytes, SHA-256
`8640c35a820b3c5e415b947fa8a13eeb5c7c535868780dc2fe511d020a54c40e`.

Program bytes, defined data and digest, user/analysis/imported symbol counts,
stored non-function-symbol digest, references and digest, comments and digest,
relocations, and every non-target function field remain exact. Undefined-data
count falls by the admitted 25 bytes; the instruction-layout digest changes
with the ten bounded instructions.

## Failure, recovery, and containment

The mutator has distinct failure probes immediately after the repair and after
the complete validated POST. Both nested transactions requested rollback and
both separate-process readbacks returned semantic PRE. Ghidra still advanced
each failed copy's physical database generation, so those copies are retained
as tainted evidence and were not reused. Two independently copied restoration
projects match the original PRE byte-for-byte and separately read back as PRE.

An output path outside the package and a same-length altered manifest both
refused before publication. The exact PRE backup opened read-only with analysis
and commit disabled, then remained byte-identical. No live or tracked project
was opened by the mutator.

## Sealed authority and limits

The retained authority is
`local-lab/crt-eh-parent-repair-db18616-20260814-v1/formal/authority/scratch-authority.ready.json`,
3,877 bytes, SHA-256
`3d472b734d4a3eeb19a896e713e1f2d2cc1dfbac5befcd66ef8c39ad0618eb82`.
It seals 283 files / 1,518,299,333 bytes at tree SHA-256
`bd7545cd76571ec9a6c20f6a981a0f7933e0a9d629ad7867ecdddf8c0c6a8a49`.
Two consecutive verifies at the source root and two at a copied root reproduce
the same authority with no Python cache creation. The frozen mutator is 49,382
bytes, SHA-256
`bc9f18ff6e67d1cb7c41b9c5b5d108732af5598a062425ef36c53f93f2aba1e9`.

Reproduce the saved decision where the ignored package is retained:

```powershell
python -I -B tools/ghidra_crt_eh_parent_range_scratch_authority.py verify
```

This is a structural ownership repair only. It does not settle the parent's
signature debt, give the filter or handler independent function identity,
establish runtime frequency/effect, change the Generation 27 semantic grade,
or authorize live/tracked/canonical Ghidra mutation. A live promotion requires
a new current-root preflight, recoverable backup, two replicas, one bounded
live save, separate readback, tracked refresh/restore, and current-state
projection under its own reviewed authority.
