# Lane 08 - Authority Model Validation

## Authority Model Under Test

Retail Steam behavior is authoritative:
- `BEA.exe` runtime/load/save behavior + real save observations are controlling.
- Stuart internal source is supportive/reference-only, not controlling when conflict exists.

## Scope Reviewed

- `AGENTS.md`
- `reverse-engineering/save-file/*.md` (canonical)
- `lore-book/reverse-engineering/save-file/*.md` (lore-curated mirror)
- `lore-book/BOOK.md` authority note
- `roadmap/*` and `lore-book/roadmap/*`

## Verdict

**Overall: PASS**

No scoped document set was found to invert the authority model. Canonical and lore-curated documentation preserve the same rule, with minor wording hardening recommended.

## Pass/Fail Matrix

| Area | Verdict | Evidence | Assessment |
|------|---------|----------|------------|
| AGENTS baseline | PASS | `AGENTS.md:149`, `AGENTS.md:337`, `AGENTS.md:754` | Explicitly states internal source differs from retail and requires BEA/save verification. |
| Save-file canonical docs | PASS | `reverse-engineering/save-file/save-format.md:8`, `:90`, `:98`; `grade-system.md:52`; `kill-tracking.md:64`; `_index.md:7` | Repeatedly marks true retail/BEA behavior as authoritative and source as supportive. |
| Save-file lore-curated docs | PASS | Byte-identical to canonical set (`reverse-engineering/save-file/*.md` vs `lore-book/reverse-engineering/save-file/*.md`) | No authority drift between canonical and curated copies. |
| Lore-book top-level authority note | PASS | `lore-book/BOOK.md:4` | Direct, explicit statement: retail/Steam BEA + real saves authoritative on conflict. |
| Roadmap canonical docs | PASS | `roadmap/agent-workflow.md:10`, `:62`; `roadmap/executable-modding.md:88`; `roadmap/modification-features.md:43`; `roadmap/status-current.md:60` | Planning docs consistently treat source as reference and retail behavior as final gate. |
| Roadmap lore-curated docs | PASS | `lore-book/roadmap/ROADMAP-INDEX.md:29`; `lore-book/roadmap/agent-workflow.md:10`, `:62` | Curated roadmap keeps canonical roadmap as content source-of-truth and preserves same authority posture. |

## Alternatives Check (Canonical vs Lore-Curated)

- Save-file docs: **PASS** (mirrors are content-identical, so authority semantics are preserved exactly).
- Roadmap docs: **PASS** (only ordering/navigation deltas in lore-book; no authority model regression).

## Non-Blocking Wording Risks (Advisory)

1. `AGENTS.md:249` labels `BesFilePatcher.cs` as “authoritative.”
- Risk: could be read as behavior authority rather than implementation authority.
- Recommended tweak: qualify as “authoritative implementation in this repo; retail BEA.exe behavior remains behavioral authority.”

2. `reverse-engineering/save-file/kill-tracking.md:176` cites a combined unlock threshold from `source/internal` with “retail behavior appears consistent so far.”
- Risk: acceptable but lightly provisional wording could be misread as fully confirmed.
- Recommended tweak: add explicit verification-status tag (`Observed/Provisional/Verified`) for that line item.

## Recommendation

Ship the authority model as **accepted (PASS)** for this lane. Apply only small wording hardening where noted to reduce future misreads; no structural rewrite is needed.
