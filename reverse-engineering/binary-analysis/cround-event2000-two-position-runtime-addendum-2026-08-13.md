# `CRound` event-2000 two-position runtime addendum

Status: active, bounded non-parent addendum
Date: 2026-08-13
Evidence: MEASURED — two exact retained runtime windows, call/entry stack
captures, an independent source-population census, pristine target-body bytes,
and a deliberately failing count-gate control
Verdict: **C2_BOUNDED_RUNTIME** for two exact receiver-matched `CALL_ENTRY`
paths only; allocator return/effect and population behavior remain open
Specimen: safe-copy runtime `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`;
pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Authority parent: Generation 23, `campaign.ready.json` SHA-256
`4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc`.
This is a non-parent addendum: Generation 23 remains unchanged and the next
valid campaign generation remains 24.

The deterministic local reduction owner is
`local-lab/cround-event2000-two-window-c2-addendum-20260813-v3/`:

- reducer: 43,945 bytes, SHA-256
  `3cda431f855d3c75fa15c5f54d3d9e42c2cd7c46886aa6b76d09c2ce6a140b9f`;
- reduction receipt: 8,723 bytes, SHA-256
  `56b73ae026bbcfa27558eff653de339ecbf3bc1edaa91027beb43004f1052bc1`;
- READY: 6,592 bytes, SHA-256
  `513eb42dc7438167cb5f4329a03bbd763dc5038fb0ac5f649177fd8b42a60357`.

## Bounded result

For each exact runtime position key below, the observed route reaches a
receiver-matched `CALL_ENTRY` at address `0x00549220`, currently labeled
`CDXMemoryManager__Free`, from call site `0x004d8365`. Both call and entry stack
captures carry the selected event receiver as the first stack argument:

| Session | Exact position key | Receiver | Allocator call position | Allocator entry position |
| --- | --- | --- | --- | --- |
| level 521 | `45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2:0xA6F4F:0x3B..0xA6F5B:0x28` | `0x07a0a930` | `0xA6F57:0x5D` | `0xA6F57:0x5E` |
| level 512 | `3d3a118fe211ead7b1e41055e4150dcff576b6d0cc64879c52d1163beca94808:0x18C01E:0x1E1..0x18C02A:0x28` | `0x08228a50` | `0x18C026:0x5D` | `0x18C026:0x5E` |

Both allocator observations are graded only `CALL_ENTRY`. Neither has an
associated return, and each crosses an association gap. They do not prove a
completed free, deallocation, or heap effect. Exact source spelling remains
open.

## Selection and population boundary

The retained material contains 167 event-2000 calls and ten receiver-predicate
matches. This addendum selects two positions, leaving the other 165 event-2000
invocations and eight other predicate matches untested:

| Session | Event-2000 calls | Receiver-predicate matches | Selected position |
| --- | ---: | ---: | --- |
| level 521 | 161 | 9 for `0x07a0a930` | arbitrary ordinal 6 of 9 |
| level 512 | 6 | 1 for `0x08228a50` | unique match, ordinal 1 of 1 |
| Total | 167 | 10 | 2 exact instances |

The level-521 choice is non-unique and arbitrary. These two instances are not a
representative sample, and this addendum makes no population-frequency claim.

## Replay counts and gaps

Each exact replay produced 38 events and 13 invocation envelopes in the frozen
target order. Only 3 of 13 envelopes per run are gap-free
`CALL_ENTRY_RETURN`; the other 10 per run are `CALL_ENTRY` only. Each selected
outer source envelope has an entry-to-raw-return association-epoch delta of
six, so no full outer-return claim is made.

The route includes target-3 calls at `0x004d8de4` to target 4
(`0x004cb0b0`) and at `0x004d8e2a` to target 5 (`0x00401000`). Pristine
disassembly establishes that both call instructions are unconditional on the
ordinary target-3 return path. Only their callees' internal effects may be
state-dependent; those effects were not measured here.

## Runtime and pristine identity boundary

The runtime and pristine files differ at exactly four bytes, VA `0x0052a644`
through `0x0052a647` inclusive, outside all ten target ranges. All ten complete
target bodies are byte-identical. That equality supports transfer of the
static route and body facts to the pristine specimen; it does not transfer
runtime causality or effects.

## Count-gate control

The level-512 control changed target 9's expected entry count from four to
five. It observed four, exited 10, produced a `BLOCKED` manifest, and produced
no `READY`. This is only a count-gate control. It is not a semantic, receiver,
allocator-argument, or causal control.

## Still open

- Population frequency or representativeness.
- The eight unselected predicate matches and all other 165 event-2000 calls.
- Internal effects of the side calls, including targets 4 and 5.
- Allocator return, completed freeing, deallocation, or heap effect.
- Rebuild parity.
- Exact source spelling.

No campaign promotion, Ghidra mutation, executable write, new recording, or
rebuild change follows from this addendum.
