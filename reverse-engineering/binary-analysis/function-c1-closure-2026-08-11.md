# Full function static-C1 closure

Status: active, bounded static closure
Last updated: 2026-08-11
Evidence: MEASURED — 53 sealed receipt files, exact address/body joins, the
8,136-row final Ghidra inventory, and independently checked row/grade counts;
UNKNOWN — the semantic, runtime, source-equivalence, and rebuild gaps retained
per row.
Verdict: all 8,136 known functions have at least a bounded static C1 envelope;
this settles accounting, not complete semantic or reconstruction parity.
Specimen: pristine PC `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Outcome

Every one of the 8,136 functions in the final reviewed inventory now has a
tracked `C1_CANDIDATE_PARTIAL` static envelope or a stronger
`C2_BOUNDED_RUNTIME` grade. The mechanical owner is
[`function-c1-closure-2026-08-11.tsv`](function-c1-closure-2026-08-11.tsv),
3,288,437 bytes, SHA-256
`cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974`.

| Accounting item | Count |
| --- | ---: |
| Final Ghidra functions | 8,136 |
| Sealed static receipts | 53 |
| Standard `contracts.tsv` receipts / rows | 52 / 7,904 |
| Separately shaped Weapon41 receipt rows | 41 |
| Unique receipt-covered functions | 7,945 |
| Post-Gen19 Mission-native C1 functions | 10 |
| Pre-existing Gen19 C1/C2 functions outside those receipts | 181 |
| Final C1 | 8,129 |
| Final C2 | 7 |
| Final static `OPAQUE` | 0 |

The receipt set was recounted from the files, not inferred from narrative
totals. Its 7,945 rows have 7,945 unique addresses: there are no duplicate
addresses between Weapon41 and the 52 standard receipts.

## Exact join

The 53 receipts cover all 7,825 rows still graded `OPAQUE` in the current
8,126-row tracked Generation-19 projection. They also cover 119 already-C1 rows
and one already-C2 row; those stronger or existing grades were not demoted.
The ten functions added to the reviewed Ghidra inventory after Generation 19
are the registry-identified Mission natives from `IScript__ToggleCockpit` at
`0x00533980` through `IScript__SetLightningDensity` at `0x005383A0`. Their
exact boundaries, body sizes, instruction counts, visible operations, and
remaining unknowns are carried by the separately sealed ten-row Mission-native
contract.

The final inventory source is
`local-lab/ghidra-terminal-residue-17-scratch-20260810-v1/functions.tsv`,
7,282,344 bytes, SHA-256
`3e2d855ee673e32783b3cc53386653d565b5b0092eace4e758f12721bf5a0f38`.
Its paired program inventory is SHA-256
`9733b58a545d3adb41bf585a3abfad046cf8ae9a08ffebab62ed062955b85d80`.
The Weapon41 contract source is `comments.tsv`, SHA-256
`cac2a2012c9fe0ffb229f01a0004e0360110a8612325689f3329492556646dd9`;
the ten-row Mission-native boundary source is SHA-256
`76acc64dee0dda2c25f841d00da126fb5cbe2ab1c6ea7e807ce7950cebb6f082`.

Each crosswalk row retains the exact final body range, body digest, instruction
count, tracked name, disposable-project name, grade before and after, closure
class, receipt path, and receipt SHA-256. The `HYP__` disposable names are kept
as provenance only; they do not replace reviewed tracked names.

## Authority boundary

This projection is the current authority for the narrow question, “does every
known function have at least a bounded static C1 envelope?” It does not rewrite
the immutable Generation-19 campaign replay, which remains the authority for
its admitted runtime observations, residual history, and READY/reducer pins.

Static C1 closure does **not** mean original source recovered, exact symbol or
prototype proven, every path understood, runtime causality observed, source
equivalence established, or rebuild parity reached. Many rows intentionally
retain dark execution state, structural-only identity, hidden-ABI uncertainty,
or a cheapest falsifier. Work after this milestone should deepen coherent
systems toward semantic C1/C2 and reconstruction parity rather than repeat the
function-accounting pass.

Post-closure correction: rows `0x00562C76` and `0x00562C99` retain
`CRT__GetFpuControlWord` and `CRT__ReturnVoid` only as the names present in the
dated inventory. The later
[gapless CRT/FPU closure](pc-demo-retail-gapless-closure-2026-08-11.md)
confirms that both semantic plates are false: the first is a two-argument
masked x87 control-word updater returning the prior word, and the second is a
one-argument flag-driven x87 side-effect helper. That report is the current
static semantic authority for those two entries.
