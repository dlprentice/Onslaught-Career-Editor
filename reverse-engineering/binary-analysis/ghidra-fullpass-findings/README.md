# Ghidra fullpass findings

Read-only quality expedition over the maintainer Ghidra DB copied from
`C:\Users\david\Ghidra\Projects` into this worktree's disposable
`local-lab/ghidra-fullpass-2026-07-23/project-ro`.

## Authority (do not confuse with the correction lab)

| This tree | Correction expedition lab |
| --- | --- |
| **Discovery notes** — primary/adversarial wave reviews (W001–W018) | **`local-lab/ghidra-fullpass-2026-07-23/`** (gitignored) — queues, plans, dual QC, apply logs, ops |
| Answers: “what did agents conclude in the wave?” | Answers: “what was dual-CLEARED and written to the live DB?” |

Full map: `local-lab/ghidra-fullpass-2026-07-23/corrections/apply/_AUTHORITY_LAB_VS_RE.md`  
Live working DB: `C:\Users\david\Ghidra\Projects\BEA`  
Tracked Ghidra snapshot (may lag live): `../ghidra/README.md`  
RE front door: `../../RE-INDEX.md`

A path like `W001/primary/A01.md` is **not** proof the live database was mutated.
Mutation evidence lives under the lab’s `corrections/apply/` and apply logs.

## Layout

- `WNNN/primary/AXX.md` — primary review for one shard
- `WNNN/adversarial/BXX.md` — adversarial check of the matching primary shard
- `WNNN/wave-closeout.md` — wave rollup after adversarial

## Rules

- Documentation only unless a later correction pass is separately authorized.
- Bound claims to static evidence from headless exports (`analyzeHeadless`).
- Prefer propose-only corrections; never invent runtime proof.
- Host Ghidra paths and headless posture: `../ghidra/README.md`.
- If a prior finding file exists, append a dated revision section rather than
  silently overwriting unless the coordinator marks a relaunch replace.
