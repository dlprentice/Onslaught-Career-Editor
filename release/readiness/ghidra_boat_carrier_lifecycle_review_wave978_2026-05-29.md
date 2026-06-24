# Ghidra Wave978 Boat/Carrier lifecycle review (2026-05-29)

Status: read-only static review
Date: 2026-05-29
Branch: `main`
Tag: `boat-carrier-lifecycle-review-wave978`

## Scope

Wave978 re-reviewed the Boat/Carrier lifecycle cluster from the Wave911 focused queue with BoatGuide, BoatAI, CarrierAI, and Carrier destructor context.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00414e50` | `CBoat__Init` | Reviewed; no mutation |
| `0x00415d70` | `CBoatGuide__ctor` | Reviewed; no mutation |
| `0x00421a80` | `CCarrier__Init` | Reviewed; no mutation |
| `0x00421b80` | `CCarrierAI__scalar_deleting_dtor` | Reviewed; no mutation |
| `0x00421ba0` | `CCarrierAI__dtor_base` | Reviewed; no mutation |
| `0x00414fa0` | `CBoatAI__scalar_deleting_dtor` | Reviewed; no mutation |
| `0x00414fc0` | `CBoatAI__dtor_body_00414fc0` | Reviewed; no mutation |
| `0x0050ee50` | `CCarrier__scalar_deleting_dtor` | Reviewed; no mutation |
| `0x0050ef30` | `CCarrier__Destructor` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave978-boat-carrier-lifecycle-review/metadata.tsv
subagents/ghidra-static-reaudit/wave978-boat-carrier-lifecycle-review/tags.tsv
subagents/ghidra-static-reaudit/wave978-boat-carrier-lifecycle-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave978-boat-carrier-lifecycle-review/instructions.tsv
subagents/ghidra-static-reaudit/wave978-boat-carrier-lifecycle-review/decompile/
```

Read-back result:

```text
metadata: 9/9 OK
tags: 9/9 OK
xrefs: 10 rows
instructions: 328 rows
decompile: 9/9 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. `CBoat__Init` and `CCarrier__Init` both preserve their init-object shapes and child helper allocation paths. `CBoatGuide__ctor` remains a thin guide-constructor wrapper. BoatAI and CarrierAI destructor wrappers/bodies remain coherent with scalar-deleting destructor and monitor/pointer-set cleanup evidence. Carrier lifecycle rows remain tied to the Wave557 air-unit lifecycle cleanup.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260529-142528_post_wave978_boat_carrier_lifecycle_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for selected Boat and Carrier lifecycle helpers. It does not prove exact source method names, concrete Boat/Carrier/AI/guide layouts, runtime boat or carrier behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave979 from the next Wave911 focused candidate.
