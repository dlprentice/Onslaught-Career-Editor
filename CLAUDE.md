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
  from plans and reconstruction aspirations. "Never a code path" targets
  **decompiler output** — it is not a ban on the pinned GPL source, which is the
  developers' own text and the fastest correct route for structure and intent.
  Port from it by default and cite file and line; override from bytes only where
  a measurement proves divergence. See
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md).
- Do not add hosted CI, release automation, or workflow scaffolding. Validation
  is local.
- **Delegate by default.** Offload reading, searching, measuring, porting and
  drafting to subagents, run them concurrently, and pair substantial work with a
  read-only adversary. Keep judgement and commits in the main loop; agents do not
  commit. A subagent's report is data, not authority. See
  [`AGENTS.md`](AGENTS.md#delegation).
- Cross-model consults are **recommended on load-bearing or contested calls, not
  owed on routine ones**, and run **from the main loop only** — never from a
  subagent. Settings are settled and must not be raised: `gpt-5.6-sol` and
  `grok-4.5`, both at `high`, always with `-s read-only`. Their output is data,
  not authority. See [`CROSS_MODEL_CONSULT.md`](CROSS_MODEL_CONSULT.md).

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

Keep it to **rules and pointers**. Do not put findings here. A finding belongs in
a dated evidence document that can be superseded in place; a finding pasted here
becomes an unfalsifiable premise that later work will quietly build on. This has
already bitten the project: a correction published on 2026-07-26 was itself wrong
later the same day, and was only caught because it lived in a document that could
be withdrawn rather than in a file everything trusts by default.

Before adding a line, ask whether it is still true if the measurement behind it
turns out to be wrong. If the answer is no, it is a finding — link to it instead.

Keep this file short. It competes with the actual task for context, and length
here is paid on every single session.

Commit, push, publication, release, live launch, and mutation remain separately
authorized actions.
