# PC `.text` missing-function Ghidra scratch admission

Status: **sealed repaired scratch candidate; independent integration review pending**
Date: 2026-08-13
Verdict: **SCRATCH ADMISSION READY; LIVE NOT AUTHORIZED**
Evidence: MEASURED — exact db.18611 PRE identity, two persistent disposable
replicas, dry/apply/separate-process readback, two forced-failure controls, two
external-path refusals, exact equality for every field of all 8,170 existing
function rows, and a sealed read-only replay; UNKNOWN — original linker names
and signatures, runtime reachability, and rebuild parity.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Scratch base: repository commit
`fa07f0a8c970b3040bab98708badb01685fe1546`, exact tracked canonical
db.18611, 68,288,512 bytes, SHA-256
`6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce`.

## Result

The 31 rows prepared in
[`text-gap-missing-function-boundary-preparation-2026-08-13.md`](text-gap-missing-function-boundary-preparation-2026-08-13.md)
survive the repository's disposable scratch gate. Two independent project
copies admit the same 31 exact body sets and reopen to byte-identical full
function and program inventories. This raises only the disposable-project
structural count from 8,170 to 8,201. Live Ghidra, the tracked canonical
project, Generation 23, names, signatures, and rebuild state remain unchanged.
The separate reviewed
[`text-gap-library-function-classification-2026-08-13.md`](text-gap-library-function-classification-2026-08-13.md)
at `fa07f0a8` owns provider-qualified semantic classifications for all 31 rows;
this ceremony neither re-proves nor mutates that semantic owner.

The immutable input manifest is 14,930 bytes, SHA-256
`afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586`.
Its 31 exact bodies contain 14,049 bytes and 3,895 instructions. Of those
instructions, 2,785 were already defined before admission; the bounded
disassembly defines the remaining 1,110 and creates 180 derived references.
The mutator requires every new instruction and every new reference source to
lie inside an authorized body set.

| Measurement | PRE | Scratch POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,170 | 8,201 | +31 |
| Instructions | 549,872 | 550,982 | +1,110 |
| References | 234,357 | 234,537 | +180 |
| Defined-data items | 48,585 | 48,585 | 0 |
| Undefined-data items | 3,912,345 | 3,908,592 | -3,753 |
| User-defined symbols | 6,104 | 6,104 | 0 |
| Analysis symbols | 18,006 | 18,006 | 0 |
| Imported symbols | 907 | 907 | 0 |
| Default other symbols | 61,594 | 61,686 | +92 |
| Comments | 9,199 | 9,199 | 0 |
| Relocations | 0 | 0 | 0 |

The undefined-data reduction is the exact consequence of defining the 1,110
instructions. The 92 default symbols comprise the 31 default function symbols
and 61 derived dynamic labels. The separately hashed stored non-function-symbol
inventory is unchanged. Memory bytes, defined-data count and digest, stored
non-function symbols, comments, relocations, and all 8,170 PRE function rows
are unchanged. The authority additionally requires each of those 8,170 rows to
be exactly equal across every exported TSV field in both POST inventories. The
full inventory diff records exactly 31 created default `FUN_*` rows and zero
destroyed, renamed, re-bounded, retyped, re-signatured, or thunk/no-return
changes.

## Replica and adverse-control evidence

Both disposable replicas ran a read-only dry pass, a persistent apply, and a
fresh-process readback. Their readbacks are byte-identical:

- boundary readback: 12,317 bytes, SHA-256
  `15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597`;
- full function inventory: 7,109,943 bytes, SHA-256
  `2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314`;
- program inventory: 1,267 bytes, SHA-256
  `be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636`.

The dry boundary export is 7,095 bytes, SHA-256
`a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe`;
the apply export is 12,286 bytes, SHA-256
`2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf`.

One adverse project forces failure after the first target. A second performs
the complete inner mutation, explicitly removes the 31 functions and clears
only the newly introduced instructions and reference sources, then forces a
post-compensation outer failure. Separate processes reopen both projects to
the exact PRE exports: function inventory 7,089,535 bytes, SHA-256
`ee3090360bd4f4b68d1ac52c59ab397e7ac37d81c76029d492e2a9d046902f1d`;
program inventory 1,267 bytes, SHA-256
`2360923e0fa95648a708ee44297006dee222036662d7b34108d10a1fa405dc02`.

The exact 19-file base is retained with all disposable copies. It contains
186,813,317 bytes. Its independent restore/open receipt is 6,079 bytes,
SHA-256
`518c2a9fa1421730ba4f2c99e8ad296d02efe787d9195e4a26abb14a64963915`.
The verified restore copy is itself retained and carries an exact copy
manifest.

Two read-only preflights supplied the output TSV and READY JSON outside the
repository in turn. Both refused before publishing either path with
`receipts must stay inside this repository's local-lab tree`.

One setup attempt accidentally omitted `-noanalysis`; the resulting transient
analysis tree was quarantined intact as
`9cde4a1c-ghidra-text-gap-boundary-scratch-20260813-v3`. The formal v3 campaign
then restarted from fresh exact db.18611 copies. Two superseded restore-receipt
files were likewise staged rather than deleted before the retained-copy check.

## Sealed replay and containment

The machine-local evidence root is
`local-lab/ghidra-text-gap-boundary-scratch-20260813-v3/`. Its sealed
179-file, 1,157,131,748-byte artifact tree has SHA-256
`ba67d8f7b31acc1467d30995ace1ecce8fc564644f8b022b23dfc990b4dcf465`.
The final authority receipt is 5,242 bytes, SHA-256
`e3d14106830b2b3645ffaf80c1b4cdbb73a5c0235b0afd2a4f3156702a46d2c4`.
It pins the manifest, mutator, inventory, diff, backup/open-probe owners, PRE
database, all replay exports, and artifact-tree seal. Its verifier opens no
Ghidra project and authorizes neither live nor tracked mutation.

[`GhidraApplyTextGapBoundaries.java`](../../tools/GhidraApplyTextGapBoundaries.java)
is the narrow mutation owner. It can disassemble only the preregistered body
sets, create only the 31 default functions, and publish only create-new outputs
under this repository's ignored `local-lab/` tree. It launches no helper
process, writes no external output, and rejects a pre-existing output path.
Its v2 READY schema records tool, manifest, and output locations only as
repository-relative POSIX paths.
[`ghidra_text_gap_boundary_scratch_authority.py`](../../tools/ghidra_text_gap_boundary_scratch_authority.py)
reproduces the sealed decision without opening Ghidra:

```powershell
python -I -B tools/ghidra_text_gap_boundary_scratch_authority.py verify
```

The receipt is deliberately machine-local and unsigned. It is evidence for a
trusted quiescent host, not hostile-actor-resistant or portable archival proof.
The verifier and full evidence tree were also copied to a different repository
root and reproduced there; two consecutive isolated and two consecutive default
Python invocations in each root left file counts, byte counts, receipt hashes,
and an empty cache set unchanged.

## Boundary

Scratch admission proves structural ownership only. It does not prove original
linker names, exact types, arguments, returns, side effects, runtime
reachability, or rebuild parity; the linked semantic classification remains its
own evidence owner. A live promotion would require a later separately
authorized ceremony against the then-current exact live PRE, with fresh backup,
two current scratch replicas, readback, refutation, POST backup, and
tracked-snapshot synchronization. This report stops before that gate.
