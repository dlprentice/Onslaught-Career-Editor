# MissionScript 34-handler semantic refinement

Status: candidate additive static-semantic correction; deterministic replay passed
Date: 2026-08-13
Evidence: MEASURED — exact pristine instruction bodies for each corrected branch,
the pinned 34-row semantic replay, and the frozen boundary/static-contract joins;
UNKNOWN — original C++ handler symbols and exact receiver type, runtime behavior,
authored edge-case reachability, and rebuild parity
Verdict: the 34-row ledger corrects eight handler descriptions and the common
receiver-type boundary while admitting zero functions, grades, runtime claims,
or Ghidra changes. The frozen admission remains unchanged.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Authority split

The existing static-contract addendum and its TSV remain the immutable admission
and grade record. This additive owner supersedes only the richer semantic wording
from the ignored pre-fix replay. Its mechanical row owner is
[`mission-script-registry-new-function-semantic-refinement-2026-08-13.tsv`](mission-script-registry-new-function-semantic-refinement-2026-08-13.tsv),
49,679 bytes, SHA-256 `c4aa9b00613b269d4cb194e35e2ddd10e304d1a022720c7a340a837242a8fcdd`.

The local reduction receipt is
`local-lab/mission-registry-new34-semantic-recovery-20260813-v1/corrected-v2-replay-a/refinement-receipt.json`,
5,842 bytes, SHA-256 `d24700ec00ec6b8126f78cbeb6ed085aed0ecb7ccbc3fcef387e08745cefcfc6`. Two clean output directories
reproduce the ledger, receipt, report, and READY byte-for-byte before integration.

| Property | Result |
| --- | ---: |
| Rows retained | 34 |
| Row-specific wording corrections | 8 |
| Common receiver-type corrections | 34 |
| New function boundaries | 0 |
| Grade changes | 0 |
| Runtime claims | 0 |
| Ghidra mutations | 0 |
| Rebuild/parity claims | 0 |

## Corrected findings

- `InJetMode`: the direct callee tests x87 C0 only, so unordered follows the
  less-than path; for state 2 the callee is true and the negating wrapper is
  false. The old claim that NaN made the wrapper true is withdrawn.
- `SpawnEscapePod`: each returned-position comparison tests x87 C3 only.
  Unordered is treated like equality for x, y, or z, and target-position
  fallback occurs when all three components are zero or unordered.
- Common ABI wording: the receiver is `void *` with an IScript-shaped layout;
  `IScriptContext*` was an invented concrete type and is not retained.
- `PlayAnimationWait`: allocation failure proves only that the wrapper calls
  `AddToTail` with null. It does not prove that the helper appends a null item.
- `Normalise`: the vector getter writes a caller-provided local buffer and its
  return value is ignored. The unguarded edge is the argument/getter dispatch,
  not a returned-pointer dereference.
- `GetFloatRand`: `Random__NextLCGAbs` sign-normalizes before return; ordinary
  wrapper output is the nonnegative remainder fraction in `[0,1)`.
- `SetSegmentHealth`, `ResetSegmentHealth`, and `SetSegmentVulnerable`: their
  callees read mesh-part `+0x88` and index controller `+0x04` directly, without
  a local comparison against controller count `+0x08`.

## Preserved boundaries

All other semantic cells are byte-for-byte carried from the pinned replay.
Every row remains `C1_CANDIDATE_PARTIAL` / `STATIC_BEHAVIOR`, every Tier-2 name
remains registry-derived vocabulary, and every original C++ identity remains
open. The package creates no new function, Generation, runtime causality,
reconstruction mapping, or parity result, and it does not mutate live or tracked
Ghidra.
