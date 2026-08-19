# Local lab overlay

Status: active — the ignored-directory boundary
Last updated: 2026-08-18.
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
first**; Generation 31 **v2** is the campaign parent; historical Gen10 and
candidate Gen73 are demoted). On this workstation start at
`local-lab/INDEX.md` — a short map to
`local-lab/hermes-kanban-campaign-2026-08-18/` (operating brief
`CAMPAIGN-V2.md`, grounding `HANDOFF-CURRENT.md`) and the 2026-08-17
drive inventories. The DeepSeek drop lives at `local-lab/ds-deep-review/`
and `local-lab/ds-deep-review-extended/` (relocated off `F:\DS DEEP *`;
those F: paths no longer exist). The 3,211-line historical catalog is
`local-lab/INDEX-CATALOG-2026-08-17.md`. Keep `developer_state.json` as a
routing aid; each ignored bundle's frozen verifier and measured bytes
remain the authority when a summary goes stale. Ghidra live project
mutation remains separately authorized (default: not authorized).
