# Review protocol

Status: active — situational, harness-agnostic reviewer guidance
Last updated: 2026-08-12
Summary: how to obtain useful independent review without turning a model matrix
into authority or a mandatory ceremony.
Evidence: MEASURED — maintainer direction and observed reviewer-harness behavior
own the operating policy; model output remains untrusted until reproduced by
the named mechanical evidence gate.

## Invariant

Delegated review is input, not authority. Keep reviewer lanes read-only unless a
separate writing worktree was explicitly authorized. Preserve prompts, reports,
model/effort/role, timing, and exit status under `local-lab/`. The integration
owner reproduces every load-bearing conclusion and admits it only through the
repository's mechanical evidence gates. A spawn receipt is not a liveness
oracle; verify that the reviewer reached real work and exited cleanly.

No fixed reviewer mix, model count, or normal/adversarial matrix is mandatory.
Review depth follows consequence, uncertainty, novelty, and the quality of the
available mechanical refuters. A model report never compensates for a missing
receipt, failed control, stale reducer, identity mismatch, or unproved claim.

## Harness-agnostic selection

The primary integration owner chooses single-agent or coordinated multi-agent
execution situationally from the task's scope, consequence, separability, and
available independent work. Delegation and external consultation are optional;
no reviewer is automatically required. When reviewer use is useful, the active
harness owns integration and ordinarily uses its own native subagents before
adding an external copy merely to recreate the model already doing the work.
Codex uses Codex subagents, Claude Code uses Claude subagents, Grok uses Grok
subagents, and OpenCode uses its native agents. Every additional lane reports to
the primary integration owner; no reviewer becomes the project lead or final
authority.

Fresh normal and adversarial contexts may be useful when their different jobs
materially reduce risk, but neither role is compulsory for a generation or
ordinary change. One strong independent critic can be enough when exact tests
and receipts already dominate the decision; additional models are optional and
selected only when the problem is broad, ambiguous, or vulnerable to a shared
blind spot.

The builder does not self-grade. A native adversarial subagent is independent
review data only when it receives the real artifacts and a fresh brief rather
than the builder's desired conclusion. External lanes are selected because they
add perspective, not because a historical scaffold has empty boxes.

## Reviewer toolbox

These are available choices, not a required ranking or invocation checklist:

| Reviewer | Best use | Standing effort |
|---|---|---|
| Native subagents | Fast repository-grounded measurement, normal and adversarial checks, parallel bounded reading | Use the active harness's strongest suitable setting |
| Claude Opus 5 | Long-form architecture, recovery, cross-system synthesis, difficult adversarial review | `max` for highest-impact work; `medium` for faster secondary review |
| DeepSeek V4 Flash | Substantial independent architecture/refutation and bounded high-volume analysis | `max` |
| Grok 4.6 | Independent RE synthesis, adversarial review, public-source research, and focused checks | `xhigh` |

Opus 5 Max is the preferred external long-form reviewer when the question is
important enough to justify its latency. Opus 5 Medium is useful when turnaround
matters. Grok 4.6 XHigh is a strong independent view, not intrinsically more
authoritative than the active agent or its native subagents. DeepSeek V4 Flash
Max can provide a substantial independent review, but its report is still only
a hypothesis until reproduced.

## DeepSeek through OpenCode

Use OpenCode as the DeepSeek harness. Select the provider in this order:

1. the maintainer's OpenCode Go DeepSeek V4 Flash offering;
2. the OpenCode Zen free DeepSeek V4 Flash model as a fallback;
3. the direct DeepSeek V4 Flash provider using the maintainer's API credential
   only when the first two routes are unavailable or unsuitable.

Use variant `max`. Provider model IDs can change, so run `opencode models` and
record the exact selected ID rather than copying a stale slug. Never expose an
API key in a prompt, command log, receipt, state file, or report. Free-provider
data handling may differ; do not send secrets or material outside the user's
authorized scope.

Typical shape:

`opencode run --pure -m <verified-model-id> --variant max --dir <repo> <prompt>`

Prefer serial DeepSeek sessions by default because the shared OpenCode SQLite
store has previously experienced contention. Bounded parallel runs are allowed
only when the integration owner has checked memory, distinct outputs, and real
session progress. A lock or failed process invalidates that lane; retry it
cleanly rather than treating a spawn as a report.

## Opus and Grok

Opus runs through Claude Code headless. For the highest-impact pass:

`claude -p <prompt> --model claude-opus-5 --effort max --permission-mode plan --output-format text`

Use `--effort medium` for the faster lane. Background runs must have a trusted
project, preserved stdin/prompt and stdout/stderr, and enough time for real tool
work. Plan permission is appropriate for read-only reviews.

Grok uses model `grok-4.6` with `--reasoning-effort xhigh` and `--no-plan`.
Run one primary Grok review session at a time unless resource evidence supports
a different bound. Grok-native subagents and public web research are optional
capabilities when they materially strengthen the review; Grok remains a
coordinated reviewer beneath the primary integration owner. Keep every local
lane read-only unless one explicit scratch/report output is authorized. Preserve
the exact prompt, complete direct output, model/effort, timing, exit status,
session ID, and any cited public sources under `local-lab/`. Never disclose
credentials, raw retail payloads, decompiler bodies, or material beyond the
approved scope. Treat Grok and all of its subagents as review input, not
authority.

Current headless shape (verify with `grok models` and `grok --help` before use):

`grok --cwd <repo> --model grok-4.6 --reasoning-effort xhigh --no-plan --permission-mode dontAsk --tools Read,Glob,Grep,WebSearch,WebFetch,Task,TaskOutput --max-turns 100 --output-format plain --session-id <uuid> --prompt-file <prompt>`

Remove `WebSearch,WebFetch` or `Task,TaskOutput` when the review does not need
web research or Grok-native subagents. Keep write/edit/shell tools absent for a
read-only review. Give the outer process up to 3,600 seconds (one hour) because
Grok 4.6 XHigh may spend substantial time reasoning and coordinating its native
subagents. Poll often enough to distinguish live work from authentication,
permission, transport, or process failure; the one-hour allowance does not make
a stalled session valid evidence.

## Campaign and gauntlet work

Each campaign generation still needs its own mechanical parent, delta, receipt,
reducer, replay, and adverse-control gates. A cross-generation review cannot
replace those. Reviewer choice is situational: use separate critics where a
generation introduces a consequential new claim or instrument, and do not force
an eight-way model sweep over a generation whose exact reducer and focused
counterexamples already settle the question.

The gauntlet remains an outcome, not a model quota: split the ambitious goal
into falsifiable pieces; inspect the real artifacts; attack both the claim and
the instrument; loop until the evidence bar wins or the maintainer redirects.
No model may authorize a function name, signature, type, runtime contract,
campaign promotion, rebuild parity claim, Ghidra mutation, capture, or memory
write. Those decisions belong to the owning evidence gate and integration
owner.

Historical per-generation scaffolds may record the reviewer set used at that
time. Active scaffolds must accept an explicitly selected reviewer subset and
must not silently launch retired or unrequested models. Label the actual subset
that ran; do not describe absent cells as failed authority.

## Invocation hygiene

- Give reviewers the real files and a falsifiable question, not only a summary
  engineered for agreement.
- Preserve prompt, stdout/stderr, model/provider, effort/variant, role, start and
  finish time, exit code, and any session ID under a distinct `local-lab/` root.
- Verify process state and resource use. Do not mistake an auth/trust dialog,
  empty output, timeout, or partial stream for completed reasoning.
- Keep CLI reviewers read-only. A writing reviewer uses an isolated worktree and
  is integrated or discarded as one reviewed unit.
- Review instruments as well as findings: reducers, parsers, exact-delta gates,
  negative controls, exporters, and publication ordering are frequent sources
  of false authority.
- Stop adding reviewers when their marginal result is lower than running the
  cheapest mechanical falsifier.
