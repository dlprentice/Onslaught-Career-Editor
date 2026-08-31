# Local lab overlay

Status: active — the ignored-directory boundary
Last updated: 2026-08-30.
Summary: which local paths own retail inputs and bulky generated work, and what
may be promoted out of them into tracked evidence.

Use ignored local directories for retail inputs and bulky/generated work. They
are not source and must not be copied wholesale into a release candidate.
The rebuild materializer writes its exact verified retail inputs to ignored
asset paths so normal build and launch commands keep working without making the
payloads repository source.

Current owners:

- canonical
  `~/Projects/game-dev/Onslaught-Career-Editor/local-lab/` — the one real,
  writable, Git-ignored owner for manually supplied game installs, copied
  runtime targets, converted rebuild assets, campaign evidence, and other
  durable workstation-local inputs;
- `.artifacts/` — disposable validation, screenshots, publish output, reports,
  and extracted release candidates;
- `~/ProjectData/Onslaught/` — recovered worktree/conflict packages, preserved
  Windows-profile inputs, retail profiles, media, and VM media that are not part
  of `local-lab/`;
- a separately selected local Ghidra working copy and off-volume verified
  backups — never the tracked checkpoint or either preservation owner.

The canonical lab was moved by same-filesystem atomic rename on 2026-08-30; the
old ProjectData path is absent, and no twin, symlink, bind mount, or read-only
view remains. It is a physical directory inside only the canonical checkout.
Fresh clones and Git child worktrees do not receive ignored content. A worktree
must set `BEA_LOCAL_LAB` to the canonical absolute path or pass that path through
the owning tool's explicit lab option; do not create a per-worktree copy.

Git ignore is a publication boundary, not a backup. Never run root-level
`git clean` with `-x` or `-X`; any deliberate clean needs a dry run, narrow
scope, and `-e local-lab/`. Never bulk-stage the lab.

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
[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md); resolve
the live selector through `developer_state.json` → `current_re_authority`, not a
generation quoted in prose. On this workstation open `local-lab/INDEX.md`, then
[`PROGRAM.md`](PROGRAM.md) and the current authority. The retained
`local-lab/hermes-kanban-campaign-2026-08-18/` material is dated operational
history, not a liveness oracle. The DeepSeek drop remains at
`local-lab/ds-deep-review/` and `local-lab/ds-deep-review-extended/`; the
3,211-line historical catalog is `local-lab/INDEX-CATALOG-2026-08-17.md`.

OpenJDK 21.0.12.1 and the verified Ghidra 12.1.3 distribution are installed.
Prepared activation copies live below
`local-lab/ghidra-linux-12.1.3-activation-20260830-v1/`, but no mutable Linux
project is designated until the read-only-open, PRE/POST recovery, semantic
comparison, and explicitly authorized writable-open gates complete. Ghidra
mutation therefore remains separately authorized (default: not authorized).
