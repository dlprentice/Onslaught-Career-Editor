# Local lab overlay

Use ignored local directories for retail inputs and bulky/generated work. They
are not source and must not be copied wholesale into a release candidate.
Curated original assets may move into an owning product/rebuild path under the
project's confirmed permission after provenance, attribution, and third-party
terms are reviewed.

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
