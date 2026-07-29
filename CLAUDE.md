# Onslaught Toolkit

Status: active — rules, routing, and state pointers; not the canonical evidence store.
Last updated: 2026-07-29. Delegation and interrupted-work resumption routing
were re-reviewed; other rules retain their prior evidence boundaries.
Summary: the highest-stakes rules that bind every session, and the pointers to
where the current state actually lives.

[`AGENTS.md`](AGENTS.md) is the authoritative contributor guide for this
repository. Read it before making changes; this file only surfaces the
highest-stakes rules early and does not restate or override it.

## Rules that must not be violated

- Never patch or mutate an installed Battle Engine Aquila directory or the
  original `BEA.exe`. Operate on verified copied targets only.
- **The maintainer's own Steam `BEA.exe` is already patched, deliberately, for
  his personal testing — this is not drift and is not to be flagged.** The
  pristine original sits beside it as `BEA.exe.original.backup` (`74154bfa…`),
  and identically at `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`.
  **Read byte evidence from a pristine specimen, never from the live `BEA.exe`,
  and name the specimen file and hash in every byte finding.**
- Never synthesize `.bes` saves from scratch. Start from a real retail baseline
  and preserve file length, reserved fields, and unknown bytes.
- Do not track retail game assets, converted copies, game binaries, arbitrary
  save payloads, raw debugger logs, Ghidra backups, credentials, `.env*`, or
  bulky runtime captures. Retail inputs are materialized to ignored local paths
  from the user's own installation.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation,
  filesystem, clock, process, network, and GPU APIs.
- Keep public claims bounded to demonstrated evidence. Separate proven behavior
  from plans and reconstruction aspirations. "Never a code path" targets
  **decompiler output** — it is not a ban on the pinned GPL source, which is the
  developers' own text and the fastest correct route for structure and intent.
  Port from it by default and cite file and line; override from bytes only where
  a measurement proves divergence. See
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md).
- Do not add hosted CI, release automation, or workflow scaffolding. Validation
  is local.
- Delegate bounded independent work when it materially protects the primary
  task's context. Keep judgement, integration, and commits with one owner; see
  [`AGENTS.md`](AGENTS.md#delegation) for the isolation and review rules.

## The goal

[`GOAL.md`](GOAL.md) holds the maintainer's standing objective verbatim — what
"done" means, the evidence partition, the evidence rule, and the standing
constraints. It is the one document here that is **not** superseded by
measurement, because it states what is wanted rather than what is true.

## Resuming work

**[`developer_state.json`](developer_state.json) is the pick-up-where-we-left-off
file.** After the repository overview and contributor rules above, read it when
resuming an interrupted task or after compaction. It carries current gate status,
work in progress, and pointers to machine-local evidence stores.

Keep current resumable state and exact evidence pointers there. Include a
bounded finding only when it prevents costly re-derivation, and always include
the evidence path that can overturn it. Measurements outrank the file; when
current evidence supersedes an older account, mark or remove that account
instead of preserving parallel truth.

Keep it current as work lands. It is maintained from the main loop, not written
at handoff time.

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
- [`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) — what belongs in the ignored
  local directories and what may be promoted out of them.

## In-flight work is not in this repository

Working notes, measurement write-ups, handoffs, and raw runtime evidence live
under `local-lab/`, which is **gitignored by design** — it holds retail-derived
material that must never be tracked. A fresh clone therefore contains none of
it, and a new session will not discover it by reading source.

**If a `local-lab/` directory exists on this machine, read `local-lab/INDEX.md`
first.** It indexes the current working notes, what each one settles, and what is
still open. Without it, findings that cost hours to establish are invisible and
get re-derived.

Conclusions that survive scrutiny may be promoted out of `local-lab/` into
tracked evidence under
[`RE-INDEX.md`](reverse-engineering/RE-INDEX.md); the raw logs and captures stay
local. Promotion is a judgement about whether a claim has been tested enough to
be relied on, not a backlog to clear — on this project findings are routinely
overturned within hours, and promoting early is how a wrong one acquires
authority.

## Editing this file

This file is loaded into every session, so whatever it says is treated as
settled — agents rarely re-litigate it, which is exactly what makes it dangerous.

Keep it to **rules and pointers**. Durable current state belongs in
`developer_state.json`; detailed findings belong in dated evidence documents
that can be superseded in place. A bounded finding may be retained in the state
file only with the exact evidence pointer that can overturn it.

Before adding a line, ask whether it is still true if the measurement behind it
turns out to be wrong. If the answer is no, it is a finding — link to it instead.

Keep this file short. It competes with the actual task for context, and length
here is paid on every single session.

Commit, push, publication, release, live launch, and mutation remain separately
authorized actions.
