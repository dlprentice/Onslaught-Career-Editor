# CGame__ResetRenderStateForWorldRender

> Source File: UNKNOWN — the previous attribution to `references/Onslaught/game.cpp` is withdrawn below, and no replacement is claimed | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x004eb1e0`
> Status: **superseded name — this note is a redirect, not evidence**
> Last updated: 2026-07-28

<!-- ghidra-name-drift-accepted: 0x004eb1e0 D3DStateCache__UseDefaultRenderState (2026-07-28) -->

**The canonical record for `0x004EB1E0` is
[The default render-state block, re-derived from bytes](../../d3d-default-render-state-block-2026-07-27.md).**
Read that, not this. This file exists only so older links to the withdrawn name
still resolve, and so the withdrawal itself is visible rather than silent.

## What this note said until 2026-07-28

Quoted rather than deleted. The document's first four lines read, in full:

```markdown
# CGame__ResetRenderStateForWorldRender

- **Address:** `0x004eb1e0`
- **Source context:** `references/Onslaught/game.cpp` (behavior-level alignment pass)
```

and its body read:

> ## Summary
>
> Reinitializes D3D render-state cache and sampler defaults before world rendering passes.
>
> ## Notes
>
> - Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
> - Signature is still decompiler-derived; parameter naming remains provisional pending deeper callsite pass.

## What changed, and on what evidence

Two of the three claims in that identity line are withdrawn. They are graded
separately, because they are not withdrawn for the same reason and collapsing
them would overstate the second.

| Claim | Verdict | Evidence |
| --- | --- | --- |
| the symbol at `0x004eb1e0` is `CGame__ResetRenderStateForWorldRender` | **WRONG** | MEASURED. `ghidra-function-name-table-2026-07-27.tsv` carries this address as `D3DStateCache__UseDefaultRenderState`, with extent `0x004eb1e0`–`0x004eb99c`. That extent — 1,981 bytes — is independently reproduced from the pristine specimen in [the render-state block document](../../d3d-default-render-state-block-2026-07-27.md), which reads the body byte by byte and states its bound. Two independent fullpass reviews use the same name: `ghidra-fullpass-findings/W007/primary/A09.md:198` and `ghidra-fullpass-findings/W007/adversarial/B09.md:137`. |
| this function is a `CGame` method | **WRONG**, as a consequence of the row above | The current class prefix is `D3DStateCache`. |
| its source file is `references/Onslaught/game.cpp` | **UNSUPPORTED — not disproven** | MEASURED, and deliberately weaker than the rows above. `references/Onslaught/game.cpp` does exist, and `grep -rn -i 'DefaultRenderState\|ResetRenderState\|D3DStateCache' references/Onslaught/` returns **zero hits anywhere in that tree**. That is absence of support, not proof of a different owner. The pinned GPL drop is a partial drop, so a symbol's absence from it is expected for the recovered-from-bytes half of the evidence partition. |

**Owner: UNKNOWN.** What would settle it: a call-graph tie from this address to a
translation unit the pinned drop does contain, or a debug-path string constant
referenced from inside `[0x004eb1e0, 0x004eb99d)` of the kind other notes in this
directory quote. Neither was measured here. Writing "game.cpp was never the
owner" would be a guess dressed as a fact, so it is not written.

## Why this one mattered more than a typical drift

`0x004EB1E0` is load-bearing for the terrain and cockpit lighting lane — the
lighting enable, the two material sources, the stage-0 texture arguments and the
absence of `D3DRS_COLORVERTEX` were all decided against it. A reader chasing that
lane by symbol name reached this file first and met a wrong symbol, a wrong class
and a source attribution nothing supports.

## Boundaries

- This note performs no Ghidra rename and no mutation. It records a withdrawal.
- Nothing from the canonical document is restated here, deliberately, so the two
  cannot drift apart.
