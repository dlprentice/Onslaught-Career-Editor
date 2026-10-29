# Retail function and behavior contracts

Status: active — what the contract documents are and how to read their grades
Last updated: 2026-10-29 (the decompilation's published score stated as it is; earlier: the decompilation cited as onslaught-decomp; the grading campaign ended; the byte-matching decompilation is the authority; campaign records in the private RE archive)
Summary: what a retail behaviour contract states, what its recorded grade meant, and where the authority now sits.
Evidence: SOURCE — the contract documents under `reverse-engineering/contracts/` and the per-function notes under
`reverse-engineering/binary-analysis/functions/`; grades are those the Ghidra-era campaign recorded.
Specimen: pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

The contract documents under [`reverse-engineering/contracts/`](reverse-engineering/contracts/) and the
per-function notes under [`reverse-engineering/binary-analysis/functions/`](reverse-engineering/binary-analysis/functions/_index.md)
describe what individual retail functions do. They were written during the Ghidra-era campaign, which graded every
function in machine-verified campaign generations. That campaign ended on 2026-10-15: the byte-matching
decompilation (5,482 of 5,482 functions in the maintainer's working tree; its public export,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), reproduces 5,449 of them) is now the authority on what a function does, and the
campaign's ledgers, verifiers and `developer_state.json` are in the private `dlprentice/onslaught-re-archive`.

## What a contract is

A function boundary, plausible name, source resemblance, call count, or one observed invocation is not a complete
contract. A useful retail contract states, as far as the evidence permits:

- the exact specimen-bound entity and body/range;
- receiver and input values, representations, units, and valid conditions;
- return value and other outputs;
- globals, structure fields, resources, and external state read or written;
- ordering, timing, side effects, and calls that matter to behavior;
- failure, rejection, and edge behavior;
- unresolved fields, rival explanations, and the cheapest falsifier.

Unknown fields stay unknown. "No write observed in this trace" is not "this function never writes." A forced
script-level `Damage` call can prove the damage boundary it reaches without proving the natural projectile and
collision chain that ordinarily precedes it.

## Recorded grades

A contract's recorded grade is the campaign's last word on it, not a current measurement:

1. `C0_OPAQUE`: accounted for, behavioural contract unknown.
2. `C1_CANDIDATE_PARTIAL`: static, source or runtime evidence proposed bounded fields while named rivals or missing
   observations remained.
3. `C2_BOUNDED_RUNTIME`: controlled or exact-window replay measured a limited runtime contract under bounded
   conditions.
4. Refuter-survived: predictions, controls, identity, receipts and competing explanations passed a can-fail gate.
5. Terminal or `REBUILD_READY`: enough evidence for the stated use, with remaining uncertainty explicit.

Grades are not percentages, and a name or boundary does not raise a semantic grade.

## Writing or correcting a contract now

- Check the claim against the decompiled function in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) and cite it by name and address; never paste
  decompiler output into this repository.
- Keep static structure, measured runtime behaviour, source architecture and open questions visibly separate, and
  state what the document does not prove.
- Name the specimen for any byte or address finding.
- Do not add per-function tables to this page.
