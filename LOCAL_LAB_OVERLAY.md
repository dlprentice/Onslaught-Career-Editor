# Local lab overlay

Status: active — the ignored-directory boundary
Last updated: 2026-10-15 (Ghidra and the RE campaign retired as authorities; their tracked records moved to the private RE archive).
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
- `.artifacts/` — legacy validation, screenshots, publish output, reports,
  and extracted release candidates; inspect before retirement because some is unique evidence;
- `local-data/` (Git-ignored, inside this checkout; `~/ProjectData` no longer exists) —
  grouped `recovered/` packages, retained `_recovered-worktrees/` and Windows-profile inputs, retail
  profiles, media, VM media, and the gen32 host attestations that are not part of
  `local-lab/`; its own `AGENTS.md` describes the recovered packages;
- `local-lab/ghidra-projects/BEA/` — the retired working PC Ghidra project (12.1.3), kept untouched; the
  former tracked checkpoint (now in the private RE archive) and the sealed off-volume package are preservation
  copies, never writable inputs.

The canonical lab was moved inside the checkout by atomic rename on 2026-08-30.
On 2026-09-05 the complete checkout moved to `/srv/archive-b/Onslaught-Career-Editor`
on encrypted ext4. The familiar Projects path bind/automount reaches those same files;
the lab itself remains a normal writable child directory. The verified Samsung original
was retired. The old ProjectData path is absent, not a compatibility link.
Fresh clones and Git child worktrees do not receive ignored content. A worktree
must set `BEA_LOCAL_LAB` to the canonical absolute path or pass that path through
the owning tool's explicit lab option; do not create a per-worktree copy.

The rebuild materializer detects a linked worktree and verifies the canonical
materialized files against its current source pins, then creates individual
file links in the worktree's ignored `Assets/` paths. The explicit equivalent is
`python rebuild/tools/materialize_retail_assets.py --reuse-canonical-assets`.
It refuses stale inputs, conflicting destinations and directory links; it never
regenerates the canonical files. This leaves adjacent `.import` files and the
project's `.godot/` cache local to the worktree. Rebuild launchers place each
invocation's output/profile under that checkout's `local-data/first-flight/`
and only read the canonical startup-media cache. Generated production scenes
and resources must remain checkout-local, private and ignored as well.

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

The machine-local RE campaign generations and READY bundles are history: the campaign ended on 2026-10-15 and
its selector, `developer_state.json`, is in the private RE archive. On this workstation open `local-lab/INDEX.md`
for the retained corpus. The retained
`local-lab/hermes-kanban-campaign-2026-08-18/` material is dated operational
history, not a liveness oracle. The DeepSeek drop remains at
`local-lab/ds-deep-review/` and `local-lab/ds-deep-review-extended/`; the
3,211-line historical catalog is `local-lab/INDEX-CATALOG-2026-08-17.md`.

OpenJDK 21.0.12.1 and the verified Ghidra 12.1.3 distribution remain installed (activation receipt under
`local-lab/ghidra-linux-12.1.3-activation-20260830-v1/receipts/`). No Ghidra work is planned; the working project
and the independent cold recovery on Archive A stay as preservation copies.
