# Ghidra Wave911 static reaudit risk rank (2026-05-27)

Status: read-only planning evidence
Date: 2026-05-27
Branch: `main`
Tag: `wave911-static-reaudit-risk-rank`

## Scope

Wave911 starts the full post-closure reaudit continuation requested after Wave910. It does **not** claim new Ghidra corrections. It ranks the already-closed `6113/6113` function set for likely follow-up review.

This was read-only:

- no Ghidra mutation
- no saved names/signatures/comments changed
- no function-boundary changes
- no executable-byte changes
- no runtime proof

## Inputs

Fresh Wave910 live export:

```text
subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

Generated Wave911 planning artifacts:

```text
subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-risk-ranked-functions.json
subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-risk-ranked-functions.tsv
subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-focused-correction-candidates.json
subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-focused-correction-candidates.tsv
```

These `subagents/` artifacts are private/R4 evidence and are not public release artifacts.

## Heuristic Signals

The ranking is deliberately conservative. It prioritizes functions whose saved names/comments contain signals such as:

- stale/corrected/wrong/mislabel language
- provisional/candidate/likely/uncertain/unknown language
- exact-layout/source-identity/hidden-ABI deferrals
- generic function-name shapes such as `VFunc`, `Thunk`, `Wrapper`, `ReturnZero`, or `Noop`
- high-use families such as `CUnit`, `CBattleEngine`, `CGame`, `CCareer`, `CDXTexture`, `CFastVB`, `CMesh`, `CWorld`, `CWeapon`, `CScript`, `CDXEngine`, `CEngine`, and related support classes

## Result

Broad risk-rank output:

```text
total functions: 6113
broad candidates: 5803
```

Focused correction-candidate output:

```text
focused candidates: 1408
stale_or_corrected: 1269
provisional_or_candidate: 172
exact_layout_deferred: 1343
generic_name_shape: 117
critical_family: 2196
```

Top focused candidates by heuristic score:

| Score | Address | Name | Signals |
| ---: | --- | --- | --- |
| 28 | `0x00402030` | `CActor__StickToGround` | stale/corrected, provisional/candidate, exact-layout deferred, generic name |
| 28 | `0x00403a50` | `CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear` | stale/corrected, provisional/candidate, exact-layout deferred, generic name |
| 25 | `0x00479020` | `CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | stale/corrected, provisional/candidate, exact-layout deferred, critical family |
| 25 | `0x004aa6b0` | `CMesh__GetNameOrUnknown` | stale/corrected, provisional/candidate, exact-layout deferred, critical family |
| 23 | `0x00403730` | `CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport` | stale/corrected, provisional/candidate, generic name |

## Interpretation

The high candidate count is expected. Prior waves intentionally documented proof boundaries in comments, so many functions mention deferred runtime/exact-layout/source-identity proof. Wave911 does **not** mean the queue regressed.

The useful output is the focused candidate queue: it gives the next static reaudit a prioritized review surface instead of pretending `6113/6113` means no corrections remain.

## Recommended Next Slice

Wave912 should review a small coherent tranche from the focused queue, starting with actor/air-unit generic `VFunc` rows or mesh/collision candidate rows. Keep it read-only unless a proposed correction has at least two independent evidence signals and the operator approves a mutation tranche.
