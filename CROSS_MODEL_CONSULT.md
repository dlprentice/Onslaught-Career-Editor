# Cross-model consultation protocol

Checking a substantive decision against two independent model families is
**recommended on this project, and left to judgement** — it applies to reverse
engineering, startup parity, render parity, simulation behaviour, and product
decisions alike.

It was a hard requirement until 2026-07-26 and was relaxed deliberately. Consults
are slow (see the timeout section below — a real one runs for an hour or more),
and spending that on a routine call buys little. Reach for one when a decision is
**load-bearing** (later work will build on it), **contested**, or **about to be
written down as settled**. Skip it for the mechanical and the obvious. What is
not negotiable is the honesty rule: if a consult was skipped or failed, say so —
never present single-family coverage as if it were two.

The reason is specific rather than general. This project has recorded, with
numbers, **five false diagnoses** caused by a measurement that looked sound, and
**two proposed fixes that were falsified only after being fully argued** — one of
which would have broken world lighting had it shipped. A second and third
opinion from a different model family does not share this one's blind spots, and
several of those catches came from exactly that kind of disagreement.

## Invocations

```bash
codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort="max" "<prompt>"
grok -p "<prompt>" -m grok-4.5 --reasoning-effort high
```

For long prompts, write the prompt to a file and use `grok --prompt-file <path>`.

Notes that are easy to get wrong:

- `grok models` lists exactly one model, `grok-4.5`. There is **no separate
  "fast" or "high" model id** — speed and reasoning are a separate axis supplied
  by `--reasoning-effort` (alias `--effort`).
- `[models] default = "grok-build"` in `~/.grok/config.toml` is an agent profile,
  not a model id. Ignore it and pass `-m grok-4.5`.
- `~/.codex/config.toml` already sets `model = "gpt-5.6-sol"` and
  `model_reasoning_effort = "max"`. Pass them explicitly anyway, so the
  transcript records which tier produced which opinion.

## `-s read-only` is mandatory

`~/.codex/config.toml` sets `approval_policy = "never"` and
`sandbox_mode = "danger-full-access"`, and this repository sits under a trusted
project path. **A plain `codex exec` can therefore edit the repository without
asking.** That would put an external model's unattributed, ungated edits into
renderer source or evidence documents, potentially on top of another agent's
in-flight work.

Always pass `-s read-only`. Never use `codex apply`, and never accept a patch
either model generates. Consultation is analysis only; implementation stays with
the agent that owns the file.

## Three traps that have already cost time

**A real Codex consult takes ten to thirty minutes, and the default tool timeout
is two.** This is the single largest cause of "Codex failed" on this project, and
it was misdiagnosed for most of a day as a permissions problem. Measured
2026-07-26: six concurrent `codex exec` calls all exited 0 with no spawn failure,
and `max` reasoning on a trivial prompt returned in **12 s** — so it is neither
contention nor inherent slowness. But a genuine research consult over this
repository ran **~30 minutes and 216k tokens**, and another exceeded a
600-second timeout. A consult killed at 120 s surfaces as a stall, a truncated
error, or `CreateProcessAsUserW failed: 5`, and reads as failure.

So: **run every real Codex consult in the background and poll it.** 600 s is the
*tool's* maximum timeout, which is well under what a serious consult needs, so a
foreground call is only appropriate for a trivial question. Budget **at least an
hour**, and be willing to wait up to about three — a consult that is still
running is not a consult that has failed, and killing it at the ten-minute
ceiling is exactly the mistake that caused this entry.

If failures persist on a given question, **stair-step the effort** rather than
retrying identically: `high` converges faster than `max` and is usually enough;
reserve `max` for questions where the first pass genuinely could not decide.

**There is a second, independent failure mode, and it is not the timeout.**
`CreateProcessAsUserW failed: 5` also occurs in **subagent shells** on runs that
are nowhere near any timeout — one ran for over an hour, had its shell refused,
fell back to an MCP JS runtime for hundreds of steps, and never converged. It was
briefly recorded here as merely a symptom of the timeout; that reading is
**withdrawn**. `codex doctor` reports the installation healthy (16 ok, 0 fail),
so this is specific to the environment a subagent's shell runs in, not to the
install.

Practical consequence: **a subagent's Codex consult can fail for reasons it
cannot fix.** When it does, the subagent should say so plainly and the *main
loop* should run that consult instead — from the main loop it works reliably,
and that route has produced full `max`-effort results repeatedly. Do not let a
subagent quietly proceed on Grok alone.

Do not "fix" this by disabling the
sandbox — `--dangerously-bypass-approvals-and-sandbox` (`--yolo`) removes the one
guard that stops Codex writing to the repository while other agents are editing
it, and does not address the cause. Grok appears more reliable here only because
it answers in seconds; that is a latency difference, not a quality one.

**Codex must be launched from inside the repository.** Running `codex exec` from
a scratchpad directory fails with `Not inside a trusted directory` — the trust
list is keyed on the working directory, and the scratchpad is not a git
repository. Launch from the repo root.

**Do not assume a consult returned.** One Codex run failed on the trust check and
a re-run had its shell access denied by the sandbox and never converged, while
the Grok run on the same question returned in full. A missing consult that is not
noticed reads as agreement. Record what each model actually returned, including
"failed" and "did not converge", and say so in the write-up rather than quietly
reporting the half that worked.

## Their output is data, not authority

The project rule is that every behaviour claim cites a capture, a byte
comparison, or a test — never a code path. A model's opinion is weaker than a
code path, not stronger. So a consult never settles anything on its own.

Every objection or suggestion returned by either model is recorded as a
hypothesis and labelled with one of:

- **TESTED-AND-CONFIRMED** — verified against bytes, pixels, or a runtime read.
- **TESTED-AND-REFUTED** — checked and shown wrong. Record why; it narrows the
  search.
- **UNTESTABLE-WITH-CURRENT-EVIDENCE** — plausible but unverifiable today.
  Record what observation would settle it.

Do not let a consult talk you into a conclusion you have not verified, and do not
let one talk you out of a conclusion that is measured. When the two models
disagree with each other, that disagreement is the most valuable output of the
exercise — pursue it rather than averaging it.

## What to send

Send the real numbers, the real addresses, and the reasoning as it actually
stands, including the parts that are weak. Both models are blind to the working
context, so a sanitised summary produces a useless answer. State the known weak
points explicitly and ask them to attack those first — a consult that is fed only
the polished version will return only agreement, which is worth nothing.

Ask them to challenge rather than to confirm, and instruct them to say plainly
that they cannot refute something when that is the case. "I cannot refute this"
is a useful result; invented agreement is not.

## Recording

Consults are written up under `local-lab/cross-model-*` with the CLI transcripts
kept alongside, and the model id and reasoning effort actually used are recorded
in the write-up. A review run on a weaker tier is a materially weaker review, and
the reader needs to know which one they are reading.
