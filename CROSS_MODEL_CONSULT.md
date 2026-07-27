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
codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort="high" "<prompt>"
grok -p "<prompt>" -m grok-4.5 --reasoning-effort high
```

**`high` is the default on both. This is settled — do not re-litigate it.**

`xhigh` was tried as the default on 2026-07-26 and dropped the same day, **on
cost rather than quality**. It does work: on the identical prompt it reached the
same correct verdict and did open the callee. But it took **1202 s against
`high`'s ~600 s** — twice the wall clock for the same answer. The owner's
instruction is explicit: *"I can't handle the timeouts."* A consult that doubles
the wait without improving the result is not worth it, and at 20 minutes it also
exceeds the tool's 600 s ceiling, so it cannot be run in the foreground at all.

**Do not use `xhigh`, `max`, `ultra`, `minimal`, `low`, or `none`.**

- `max` did not return at all on a real question: 35+ minutes producing nothing
  past the stdin preamble, from the main loop, on a prompt `high` finished in ten.
  It answers a trivial prompt in 12 s, so it is reachable — it just does not
  converge on work. OpenAI's model guidance describes a **pro reasoning mode**
  for GPT-5.6 that "can tolerate higher latency"; if `max` routes there, this is
  structural slowness rather than a defect, and no amount of waiting fixes the
  economics.
- `ultra` is **undocumented for this model** and unverified. It is accepted on a
  trivial prompt (7 s), but an unrecognised value can be silently ignored or
  coerced, and its full-prompt run stalled exactly like `max`. An earlier
  revision of this file called it "reachable" on the strength of the trivial
  probe; that was over-claiming from a weak test.
- `minimal` is rejected outright with `invalid_request_error` in 11 s.
- `low` is the dangerous one. It **returns fast and answers wrongly**: on a test
  question with a known answer it concluded from *call order* that one function
  "draws over" another, without opening the callee where every draw is guarded.
  That is reasoning from a code path, which this project's evidence rule forbids.
  A cheap consult that ratifies a false claim is worse than no consult, because
  it launders it.

Note we authenticate through the **ChatGPT subscription** (`codex doctor` reports
`auth mode: chatgpt`), not the API, so OpenAI's published API enum is indicative
for this route rather than authoritative. Where the docs and a probe disagree,
the probe wins — that is how `minimal` and `ultra` were settled.

For long prompts, write the prompt to a file and use `grok --prompt-file <path>`.

## Hygiene, and why a returned consult can still be worthless

A 16-agent consult round on 2026-07-26 found a failure mode **worse than any
timeout**: *a consult that returns fluent, on-format, correct-looking output
answering **somebody else's question**.* At least 7 of 16 hit it. It reads as
agreement, so it is strictly worse than silent failure. Four causes, all
reproduced:

- **Codex inherits stdin and answers whatever prompt is on it.** Always append
  `< /dev/null` to every `codex exec`.
- **Filename collisions.** Concurrent agents wrote the same `codex_out.txt` /
  `grok_out.txt` and clobbered each other. Give every consult a unique output
  path in its own subdirectory.
- **Grok multiplexes concurrent sessions** through `~/.grok/leader.sock`. Use
  `--prompt-file`, a fresh `--session-id`, and a private `--leader-socket`.
- **Context compaction silently substitutes the question.** The model keeps
  reasoning — on whatever it was *reading*. This is the one that produces a
  completely wrong consult with no visible symptom.

Two defences follow, and neither is optional for a load-bearing consult:

1. **Require an identity sentinel.** Put a unique token in the prompt and require
   it echoed in the answer. If it is missing, discard the result — do not read it.
2. **Inline the evidence rather than pointing at paths.** Every drifted run was
   one told to go read files under `local-lab/`. A prompt that carries its own
   evidence cannot be answered about something else.

Notes that are easy to get wrong:

- `grok models` lists exactly one model, `grok-4.5`. There is **no separate
  "fast" or "high" model id** — speed and reasoning are a separate axis supplied
  by `--reasoning-effort` (alias `--effort`).
- `[models] default = "grok-build"` in `~/.grok/config.toml` is an agent profile,
  not a model id. Ignore it and pass `-m grok-4.5`.
- `~/.codex/config.toml` already sets `model = "gpt-5.6-sol"` and
  `model_reasoning_effort = "max"`. Pass them explicitly anyway, so the
  transcript records which tier produced which opinion.

**The effort ladders, measured 2026-07-26 by feeding each CLI a bogus value and
reading the enum it rejected with — not by reading the desktop UI, which differs
from what the command line can reach.**

- Codex accepts `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` **and
  `ultra`**. The app's `Light` is `low` and `Extra High` is `xhigh`.

  **Do not trust the CLI's own error message here.** Feeding it a bogus value
  makes it reject with "Supported values are: 'none', 'minimal', 'low', 'medium',
  'high', 'xhigh', and 'max'" — that list is **incomplete**. `ultra` is accepted
  and answers a trivial prompt in 7 s (`xhigh`: 13 s). An earlier revision of
  this file asserted `ultra` was unreachable on the strength of that error
  message; that was wrong, and it is a good reminder that a tool's own
  documentation of itself is evidence, not proof.
- Grok accepts exactly: `low`, `medium`, `high`. `high` is the CLI ceiling.

**Neither speed axis is exposed to the CLI.** The desktop apps offer a
fast/standard toggle; `grok --help` has no such flag and `~/.grok/config.toml`
has no speed key (only `[cli]`, `[ui]`, `[models]`, `[marketplace]`). So a
consult cannot opt *into* grok-fast, and cannot accidentally opt into the
expensive fast tier on Codex either. The invocations above are already the
correct tier on both; there is nothing to tune here.

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

If a question does not resolve, **do not escalate the tier** — the tiers above
`high` are the ones measured not to return, so escalating trades an answer for
silence. Escalate the *prompt* instead: narrow it, name the specific artefact to
open, and say what evidence would settle it. That is what produced the sharpest
results here. A consult nobody waits for is a consult that did not happen.

## Measured tier behaviour, 2026-07-26

One prompt (a real HUD audit whose correct answers were already known), run at every
reachable tier. The discriminator was whether the model opened
`CDXBattleLine__Render` rather than reasoning from call order in its caller.

| tier | main loop | verdict quality |
| --- | --- | --- |
| `low` | 221 s | **WRONG.** Concluded from call order that the battleline "draws over" the portrait. It never opened the callee, where every draw is guarded. |
| `medium` | 676 s | correct |
| `high` | ~600 s | correct, and went furthest — decoded the shipped asset and traced composed constants |
| `xhigh` | **1202 s** | **correct** — reached the same REFUTED verdict and did open the callee. Rejected purely on cost: twice `high`'s wall clock for the same answer |
| `max` | **no output after 35 min** | — |
| `ultra` | hung on a trivial prompt | — |

Three conclusions, all of which cost real time to establish:

- **`low` is unsafe here.** It answered fast and confidently and was wrong, by
  reasoning from a code path — the exact thing this project's evidence rule
  forbids. A cheap consult that ratifies a false claim is worse than none,
  because it launders it.
- **`medium` costs the same as `high` and returns less.** There is no saving.
- **`max` does not return on real questions.** It answers a trivial prompt in 12 s
  but produced nothing in 35 minutes on a substantive one, from the main loop.
  It is not slow; it is non-returning. Do not reach for it.

`high` is therefore not a cost compromise. It is the **only tier with a completed
measurement showing it both finishes and investigates properly** — `medium` also
finishes and is correct but shallower, and `xhigh` never returned inside a usable
window. That is the whole reason `high` is the default.

## From a subagent, background-and-poll is mandatory

**The Windows sandbox refuses codex's shell in subagent shells unconditionally,
at every effort level.** Measured: at `high` from a subagent, both `pwsh` spawn
attempts failed with `CreateProcessAsUserW failed: 5` within ten seconds — the
same error seen at `max`. The difference is not the tier, it is **recovery**:
codex announced a switch to the read-only JS runtime and completed the whole
audit through 73 `node_repl/js` calls, one file operation at a time, reaching the
same correct verdict as the main loop.

The cost of that fallback is time: **1008 s versus ~600 s for the identical
prompt from the main loop.** That exceeds the tool's 600 s ceiling, so **a
foreground call from a subagent cannot complete a real consult regardless of the
timeout requested.** Background and poll, or hand the consult to the main loop.

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
