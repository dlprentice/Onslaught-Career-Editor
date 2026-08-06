# Local lab overlay

Status: active — the ignored-directory boundary
Last updated: 2026-08-06.
Summary: which local paths own retail inputs and bulky generated work, and what
may be promoted out of them into tracked evidence.

Use ignored local directories for retail inputs and bulky/generated work. They
are not source and must not be copied wholesale into a release candidate.
The rebuild materializer writes its exact verified retail inputs to ignored
asset paths so normal build and launch commands keep working without making the
payloads repository source.

Recommended owners:

- `local-lab/` — manually supplied game installs, copied runtime targets,
  converted rebuild assets, and other durable workstation-local inputs;
- `.artifacts/` — disposable validation, screenshots, publish output, reports,
  and extracted release candidates;
- a separately selected local Ghidra root — full projects and verified backups.

Do not store secrets in these folders merely because they are ignored. Keep
credentials in the owning system's secret store. Prefer a copied target for lab
mutation. An installed target is permitted only when its owner explicitly
chooses it and the write path first creates and verifies a backup; the pristine
specimen is never writable.

Before promoting any local result to source, retain only the smallest
public-safe, provenance-bounded fact that materially supports a current
implementation or contract. Retail binaries/assets, real saves, raw debugger
logs, screenshots, captures, and generated catalogs remain local.

Current machine-local RE campaign and READY pointers are indexed in
[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) (**live tip
first**, historical Gen10 demoted). Complete-RE tip census lives in
`developer_state.json` → `complete_re_tip_20260805`; when present, prefer
`local-lab/OPAQUE-C1-CHECKPOINT-GEN73-20260806-FINAL-3WAY-DELTA.md` over peer
lane synths. Plate/campaign patterns under `local-lab/` include
`c1-opaque-*-batch-*`, `function-c1-*-generationNN-*`, and `checkpoint-*-gen*`;
promote only the smallest public-safe fact. Ghidra live project mutation remains
separately authorized (default: not authorized). Keep that index and
`developer_state.json` as routing aids; each ignored bundle's frozen verifier
and measured bytes remain the authority when a summary goes stale.
