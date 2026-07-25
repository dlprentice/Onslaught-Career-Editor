# Onslaught Toolkit

[`AGENTS.md`](AGENTS.md) is the authoritative contributor guide for this
repository. Read it before making changes; this file only surfaces the
highest-stakes rules early and does not restate or override it.

## Rules that must not be violated

- Never patch or mutate an installed Battle Engine Aquila directory or the
  original `BEA.exe`. Operate on verified copied targets only.
- Never synthesize `.bes` saves from scratch. Start from a real retail baseline
  and preserve file length, reserved fields, and unknown bytes.
- Do not track retail game assets, converted copies, game binaries, arbitrary
  save payloads, raw debugger logs, Ghidra backups, credentials, `.env*`, or
  bulky runtime captures. Retail inputs are materialized to ignored local paths
  from the user's own installation.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation,
  filesystem, clock, process, network, and GPU APIs.
- Keep public claims bounded to demonstrated evidence. Separate proven behavior
  from plans and reconstruction aspirations.
- Do not add hosted CI, release automation, or workflow scaffolding. Validation
  is local.

## Orientation

- [`README.MD`](README.MD) — product and lane overview.
- [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) — what is proven today
  and what remains unproven.
- [`VALIDATION.md`](VALIDATION.md) — choosing the smallest gate that proves the
  changed contract. Root [`package.json`](package.json) owns the commands.
- [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) — RE
  evidence front door.
- [`rebuild/README.md`](rebuild/README.md) and
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) — the GPL reconstruction lane
  boundary.

Commit, push, publication, release, live launch, and mutation remain separately
authorized actions.
