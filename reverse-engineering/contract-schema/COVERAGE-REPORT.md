# Contract coverage

Status: generated contract-status dashboard; do not hand-edit
Last updated: 2026-08-23
Summary: mechanical status distribution over the campaign's pinned function
denominator, generated from the evidence register, notes, manifests, and
validated factory contracts.
Evidence: MEASURED — `tools/contract_coverage.py`; exact row-level inputs and
classification flags are retained in `coverage.json`.

> **Generated file.** Re-run `py -3 tools/contract_coverage.py`. Do not copy
> these moving counts into another living document.

## Denominator

- Campaign generation: `32`
- Functions: **8,329**
- Contracts: **14,365**
- Lineage: `incident-20260806-recovery-v1`
- READY SHA-256: `08ed89644ed25feb9e85fefb5b31ab2bdecbbd91b8aca720e20c53a7fbc5e73f`

## Status distribution

| Status | Count | Share |
| --- | ---: | ---: |
| STALE | 1 | 0.0% |
| DISPUTED | 44 | 0.5% |
| BLOCKED | 58 | 0.7% |
| VERIFIED | 591 | 7.1% |
| REVIEW_READY | 7,532 | 90.4% |
| PROVISIONAL | 17 | 0.2% |
| SKELETON | 86 | 1.0% |

## Input census

| Input | Count |
| --- | ---: |
| Evidence-register rows | 8,329 |
| Function-note files | 802 |
| Manifest files with named witnesses | 36 |
| Manifest witness keys | 144 |
| Factory contract files | 275 |
| Factory contract rows joined | 275 |

## Reading contract

- This dashboard measures evidence held, not complete semantic understanding.
- A factory contract joins one canonical VA but does not promote `VERIFIED`
  without the required independent witness or promotion receipt.
- `REVIEW_READY` includes bounded static/runtime candidates; it is not parity.
- `SKELETON` means the overlay found no stronger current marker.
- The row-level `coverage.json` is canonical for auditing an individual status.
