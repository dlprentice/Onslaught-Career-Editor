# Review protocol

Status: active — the standing reviewer set, pins, and invocation rules
Last updated: 2026-08-07
Evidence: MEASURED — every pin and measurement below was produced on this
host by the named harness (OpenCode concurrency re-measured 2026-08-05; the
Grok/Opus/Codex invocations verified 2026-08-07).
Summary: who reviews load-bearing plates, at what effort, with what
invocation, and what must be preserved. This file owns the reviewer-pin
machinery that used to live in `AGENTS.md`; AGENTS.md keeps only the
invariant and this pointer, so FRAGO churn no longer rewrites the
auto-loaded constitution.

## The invariant (restated nowhere else)

Delegated review is input, not authority. Keep reviewer lanes read-only and
preserve prompts/reports under `local-lab/`. A subagent or CLI report is
data; the integration owner reproduces load-bearing conclusions before they
land. A spawn receipt is not a liveness oracle — verify the reviewer actually
reached a working state.

## Standing reviewer set (maintainer FRAGO 2026-08-05, extended 2026-08-06)

The default reviewer mix is the standing set:

| Lane | Model | Invocation | Effort |
|---|---|---|---|
| Grok | Grok 4.5 (reasoning high) | `grok --single --model grok-4.5 --reasoning-effort high --permission-mode dontAsk --tools Read,Glob,Grep --disable-web-search --no-memory --no-subagents --max-turns 100 --output-format plain --cwd <repo> <prompt>` | high |
| DeepSeek | `deepseek/deepseek-v4-flash` variant `max` | `opencode run --pure -m deepseek/deepseek-v4-flash --variant max --title <t> --dir <repo> <prompt>` | max (only) |
| Claude | `claude-opus-5` | `claude -p <prompt> --model claude-opus-5 --effort medium --output-format text` | medium (only) |
| GPT | `gpt-5.6-luna` | `codex exec -m gpt-5.6-luna --skip-git-repo-check -c model_reasoning_effort=max <prompt>` | max (only) |

Notes:

- The Codex model slug is `gpt-5.6-luna` with `model_reasoning_effort=max`;
  `gpt-5.6-luna-max` is not a valid model id with a ChatGPT account.
- Opus 5 **max** and DeepSeek **pro-max** are **retired for standing RE** —
  one-off use only with explicit maintainer re-authorization.
- Codex remains usable when weekly quota allows; do **not** skip Grok,
  DeepSeek Flash, Opus medium, or GPT 5.6 Luna lanes because a quota
  percentage looks low.

**Standing critic pin:** load-bearing plates require **all eight** cells
(Grok N+A, DeepSeek Flash-max N+A, Opus 5 medium N+A, GPT 5.6 Luna Max N+A).
Incomplete coverage is not a finished review.

## Harness-agnostic reviewer selection (maintainer FRAGO 2026-08-08)

The reviewer set and the invocation table above are **harness-agnostic**:
they describe *what the project needs*, not *which harness must provide it*.
The harness the maintainer is currently running in provides the primary
cells from its **own native subagents**; the other lanes are complementary
and run when available or on request.

- **Running in Codex:** primary N+A = Codex native subagents (`codex exec`
  subagent lanes, e.g. `codex-collaboration-subagent`); do **not** spawn a
  separate `gpt-5.6-luna` lane — you ARE that lane. Complement with Grok,
  Opus 5 medium, and DeepSeek Flash-max via their CLIs when the maintainer
  requests them or quota allows.
- **Running in Claude Code:** primary N+A = Claude Code native subagents
  (`claude -p` with subagent tooling or `/agents`); you ARE the Opus lane.
  Complement with the others on request.
- **Running in Grok:** primary N+A = Grok subagents; you ARE the Grok lane.
- **Running in OpenCode (DeepSeek):** primary N+A = native OpenCode subagent
  tool (explore/general); you ARE the DeepSeek Flash-max lane (variant max).
  This is the FRAGO 2026-08-06 direct-session carve-out, generalized.
- **Always normal AND adversarial.** Whatever the harness, each load-bearing
  review needs both roles with fresh context, inspecting real artifacts —
  never the builder's self-summary.
- **Never self-grade.** A harness's own work is reviewed by OTHER lanes or by
  its own adversarial pass against the builder's report, not by the builder
  grading itself.
- The eight-way pin still describes the *complete* load-bearing review. When
  running in one harness, the maintainer decides (with the pin as default)
  which additional external lanes to invoke; their absence does not block a
  direct-session plate but does mean the review is a subset, and that subset
  must be labeled as such when it lands.

## Direct DeepSeek session carve-out (FRAGO 2026-08-06)

When the maintainer works directly with DeepSeek in an interactive OpenCode
session, the external eight-way lanes are **not mandatory**. The reviewer
pair is the native OpenCode subagent tool run as normal **and** adversarial
roles (explore/general), orchestrated by the session lead. The external CLIs
remain available on request and when available; their absence does not block
a direct-session plate. This is the OpenCode instance of the general
harness-agnostic rule above — the other harnesses follow the same pattern.
The carve-out does **not** relax per-generation police or gauntlet-loop bars
for campaign work launched outside a direct session,
and it does not relax the DeepSeek authority boundaries (DeepSeek is still
not the integration owner and does not authorize names, signatures, types,
memory writes, campaign upgrades, rebuild parity, Ghidra mutation, or new
captures — the maintainer is present and adjudicates).

## DeepSeek direct pin (standing)

- Model: `deepseek/deepseek-v4-flash` only for standing RE
- Variant: **`max` only** (never `high`, `low`, or unset/default)
- Official Flash API id serves **DeepSeek-V4-Flash-0731**; do not use InferX
  `inferx/deepseek-v4-flash` (non-0731) or pay InferX for a 0731 mirror when
  direct is funded; do **not** use `opencode/deepseek-*` (Zen) as a fallback
- `deepseek/deepseek-v4-pro` is not standing-authorized
- Live pin proof: `local-lab/opencode-deepseek-direct-proof/PROOF.md`
  (historical Flash/Pro measurements remain valid evidence of harness
  capability; standing RE uses Flash-max only)

## Opus 5 pin (standing)

Model `claude-opus-5` via Claude Code headless; effort **medium only** for
standing RE. Run both normal and adversarial roles at medium. Preserve
prompt, stdout, model, effort, role, start/finish, exit under `local-lab/`.
Do not delay Opus medium lanes for "low weekly %" foot-dragging.

## Per-generation police

For multi-gen residual/function campaign work, each generation is its own
review lane (Gen9, Gen10, … GenN separately) — not one mega-sweep. Each
load-bearing gen needs the eight-way set. A cross-gen retrospective may
supplement but does not replace per-gen lanes. Scaffold/status:
`local-lab/per-gen-review-*/` + `tools/re_per_gen_review_scaffold.py` /
`tools/re_per_gen_review_scaffold_gen26_33.py`.

## Gauntlet Loop (standing for the complete-RE goal)

Ambitious bar (specimen + honest 100% terminal/OPEN+falsifier + dual
authority + AGENTS evidence gates) — not "pretty good." Lead splits into
smallest pieces; each piece gets a builder and **separate** critics with
fresh context (Grok N+A, DeepSeek Flash-max N+A, Opus 5 medium N+A, GPT 5.6
Luna Max N+A). Critics inspect real artifacts, never the builder's
self-summary. No fixed round count; keep looping until the bar wins or the
maintainer stops. See `local-lab/per-gen-review-*/GAUNTLET.md` and
https://somethingbig.ai/gauntlet-loop. Grok and Claude fan out in parallel;
OpenCode DeepSeek runs use **bounded parallel** on this host (see below). The
goal does **not** authorize skipping critics for throughput.

## Review both claims and instruments

Review **both** campaign/evidence claims **and** the scripts/instruments
that produced them (compose gates, reducers, verify paths, tests). All lanes
are expected to improve code quality as well as catch false terminals — not
only post-apply attack tables.

## Invocation hygiene

- Tools are required for real reviews; always `--title`; never `--auto`; use
  single-line CLI messages (multiline positionals truncate); wait long enough
  for tool loops (10–30+ min is fine); on kill/timeout delete the OpenCode
  session and mark the plate failed.
- Preserve prompt, stdout/stderr, model id, variant, role
  (normal|adversarial), start/finish, exit code under a distinct `local-lab/`
  review directory.
- `low`/`high` variants may exist on direct Flash (measured) but are **not**
  authorized for standing RE reviews; pin **max** only.

## OpenCode concurrency (retain across sessions/compactions)

OpenCode stores sessions in a shared SQLite DB
(`~/.local/share/opencode/opencode.db`). Desktop/TUI multi-session is
supported; concurrent `opencode run` is also **allowed** and was re-measured
OK on this host (2026-08-05): 2–4 short shared-DB runs and 2 concurrent
toolful flash-max runs all exit 0 with no lock error. A historical
`database is locked` / `SQLITE_BUSY` failure still exists under heavy write
contention when `busy_timeout=0` (upstream issue #21215; also seen once in
`local-lab/opencode-deepseek-direct-proof/PROOF.md` under parallel
pro-max-tool). Standing RE path: **bounded parallel** DeepSeek Flash-max only
(prefer 2 concurrent `opencode run` for the two Flash roles, not large
fan-out); on lock/fail **retry** that cell; optional isolation via per-job
`XDG_DATA_HOME` + copied `auth.json` if contention returns. Serial remains
valid but is not required. Grok subagents fan out freely.

## Historical note (unban)

OpenCode was previously avoided because free / Zen / InferX DeepSeek mirrors
were unreliable for load-bearing RE. That ban is **lifted**. Standing work
uses **DeepSeek direct** (maintainer API key via OpenCode). Do not revive the
ban; do not fall back to Zen/InferX for consequential reviews.
