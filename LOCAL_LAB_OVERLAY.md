# Local lab overlay

Use ignored local directories for proprietary inputs and bulky/generated work.
They are not part of the public source tree and must never be copied into a
release candidate.

Recommended owners:

- `local-lab/` — manually supplied game installs, copied runtime targets,
  converted rebuild assets, and other durable workstation-local inputs;
- `.artifacts/` — disposable validation, screenshots, publish output, reports,
  and extracted release candidates;
- a separately selected local Ghidra root — full projects and verified backups.

Do not store secrets in these folders merely because they are ignored. Keep
credentials in the owning system's secret store. Do not point mutation tools at
an installed Battle Engine Aquila directory; create and verify a copied target
first.

Before promoting any local result to source, retain only the smallest
public-safe, provenance-bounded fact that materially supports a current
implementation or contract. Retail binaries/assets, real saves, raw debugger
logs, screenshots, captures, and generated catalogs remain local.
