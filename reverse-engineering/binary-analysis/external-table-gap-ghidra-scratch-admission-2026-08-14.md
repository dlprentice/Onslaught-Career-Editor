# External-table gap Ghidra scratch admission

Date: 2026-08-14

Status: scratch-validated preparation; live promotion remains forbidden

Verdict: **SCRATCH_READY_LIVE_FORBIDDEN**

Evidence: **MEASURED** — exact specimen bytes, two persistent scratch replicas,
full PRE/POST inventories, rollback readbacks, actual project-tree hashes, and
a bound read-only restore/open log. This authorizes neither live nor tracked
Ghidra mutation and does not itself change the saved 8,201-function census,
Generation 23, semantic grades, or the rebuild.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
PRE project: 19 files / 186,911,621 bytes, canonical
`sha256<TAB>bytes<TAB>path` inventory SHA-256
`91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211`.
PRE database: `db.18612.gbf`, 68,321,280 bytes, SHA-256
`424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b`.

## Result

The reviewed
[79-row preparation ledger](external-table-gap-function-boundaries-2026-08-13.tsv)
passed a fresh, isolated current-state scratch-admission ceremony:

- 79 pairwise-disjoint entries and bodies, totaling 9,234 bytes;
- preparation ranks P0=12, P1=20, and P2=47;
- all 79 pinned retail body hashes reproduced; the reviewed manifest's
  demo-evidence fields joined exactly but were not rederived by this ceremony;
- two independent db.18612 replicas reached the same 8,280-function POST;
- all fields of all 8,201 PRE function rows remained byte-identical in both
  full inventory exports;
- forced failure after the first target and after a complete validated batch
  both reopened to byte-identical PRE function and program inventories;
- two external-output containment probes refused publication; and
- the PRE backup copied, hash-compared, opened read-only, and remained stable.

The PRE and byte-identical POST exports are:

| Export | Bytes | SHA-256 |
| --- | ---: | --- |
| PRE full functions | 7,109,943 | `2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314` |
| PRE program metrics | 1,267 | `be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636` |
| POST full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| POST program metrics | 1,267 | `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| POST boundary readback | 29,097 | `2f4b23ac985f55562a1897dc3d4163bd546b8b752c1c302e7d35f1d6ae365eb9` |

The POST database view contains 550,991 Ghidra instructions and 234,495
references, versus PRE 550,982 and 234,537. These small net deltas do not mean
that only nine instructions were recovered. Most bytes in these function gaps
were already represented by orphan or occasionally misaligned instructions.
The mutator clears and recreates instructions only when their complete byte
range is inside one admitted body, then protects every instruction and
reference source outside the union.

The preparation ledger counts 3,319 external-decoder instructions; Ghidra
materializes 3,318 over the same exact body bytes. The sole row-level difference
is `0x0055E3F4`, where the external decoder counts 13 instructions and Ghidra
folds one `FWAIT` prefix into the following x87 instruction, yielding 12. The
tool pins this exception explicitly; all other 78 row counts agree.

## Identity boundaries

This gate creates default `FUN_` boundaries only. It applies no prepared name,
signature, comment, tag, calling convention, data, or byte change.

- P0/P1 safe-name candidates remain evidence in the preparation ledger, not
  Ghidra mutations.
- P2 rows remain unnamed.
- `0x0058862E` is pinned as
  `D3DX_SHARED_YUV_CODEC_DTOR_LINEAGE` with safe candidate
  `D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor`; the rejected
  `CFile` interpretation is not present.
- `0x005762DD` consumes the existing portable
  [D3DXVec4Cross proof](d3dx-vec4cross-crossbuild-boundary-2026-08-13.md)
  rather than claiming a second recovery.

The structural input owner remains the
[preparation report](external-table-gap-function-boundaries-2026-08-13.md).
This scratch result does not promote its identities or change semantic grades.

## Current package and historical predecessor

The current mutator receipt schema is
`bea.ghidra.external-table-gap-boundaries.v2`; the current authority schema is
`bea.ghidra.external-table-gap-boundary-scratch-authority.v3`. Relative to the
historical db.18611 rehearsal, the tool pins the 8,201 PRE and 8,280 POST
counters, the exact db.18612 project inventory, and the newly measured POST
instruction/reference state. The structural target set and boundary TSV hashes
remain unchanged.

The eight tracked candidate paths were also compatibility-checked against
repository base `b05623e57392c0ee1a66fe36c9b3900857a07ff3`. Only
`reverse-engineering/RE-INDEX.md` had upstream overlap since the ceremony's
`f3a6a172` code base; its small index hunk was integrated onto the current
8,201-state prose. The tool README and test registry had no upstream overlap,
the other five paths are new, and the saved authority verifies unchanged from
that separate b056-based repository root.

The earlier db.18611 -> 8,249 receipt, SHA-256
`1b09b8492963e4cab85871474137ac46fec3822cd5fc3a13590c5148d5ddcca1`,
remains historical evidence only. It is not substituted for this current-base
ceremony and authorizes no promotion.

## Authority repair

The first current-base aggregate receipt, SHA-256
`ab4bdc76df4dafbea2aa7da1613aac5a4673d89100b4f5f2ccff1dc02174072a`,
is preserved as superseded evidence. Its backup receipt recorded a 4,899-byte
detailed probe log, but the shell redirected its 116-byte console summary onto
that same filename afterward. The old receipt, overwritten log, and aggregate
receipt remain byte-preserved; none is used as the repaired openability proof.

The repair reran only backup/restore/read-only open from the exact base copy.
It emitted distinct `base-restore-v2.console.log` and
`base-restore-v2.ready.open-probe.log` files. Authority v3 binds the actual
detailed-log bytes, exact success sentinel, absence of error markers,
`-readOnly` plus `-noanalysis`, absence of `-commit`, and independently hashes
both the actual base and retained restored project trees to the canonical
19-file inventory. The mutator, manifest, two positive replicas, both rollback
readbacks, boundary TSVs, and full PRE/POST inventories remain hash-identical,
so no mutating Ghidra run was repeated.

## Portable authority

The ignored formal lane is
`local-lab/ghidra-external-table-gap-boundary-current-scratch-20260814-v1/`.
Its create-new `scratch-authority-v3.ready.json` receipt is 7,597 bytes,
SHA-256
`a8e196c3dee91c1fb0600ea63fb5096ad7665159066c7ca40f58a124be48a691`.
The sealed tree excluding that self-referential receipt contains 205 files,
1,344,777,896 bytes, SHA-256
`1bd79dd25c07c256c0963dd0bd0444b89565eec4be8a44ad5ae8b90cf1e45893`.

Portable mutator READY paths and aggregate authority evidence/tool stamps are
repository-relative POSIX paths. Retained inner backup/open receipts may keep
absolute execution history and are not independently portable. The aggregate
authority verifies from the original root and a distinct copied repository root
without rewriting receipts, creating Python bytecode, or changing either sealed
tree.

Reproduce the saved evidence only where the ignored lane exists:

```powershell
python -I -B tools/ghidra_external_table_gap_boundary_scratch_authority.py verify
```

The globally registered unit test skips cleanly when that ignored evidence is
absent; an explicit `verify` remains fail-closed. Any canonical promotion still
requires a separately authorized live backup/apply/readback/POST-backup
ceremony. It is deliberately outside this result.
