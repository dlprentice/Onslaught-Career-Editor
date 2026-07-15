# Durable slash goal — Full reconstruction campaign (time-boxed marathon)

Status: **canonical `/goal` text**  
Last updated: 2026-07-15  
Campaign map: [`goal.campaign.md`](../../goal.campaign.md)  
Policy: [`goal.policy.md`](../../goal.policy.md)  
Mutable baton: [`goal.md`](../../goal.md)

## How to invoke

1. Set **STOP_LOCAL** in the verbatim block (your machine local time).
2. Paste the whole block into `/goal`.
3. Re-use the same campaign text every session; only change `STOP_LOCAL` / date.

Example: start at 11pm, set `STOP_LOCAL=10:00` and `STOP_DATE=tomorrow` so work continues overnight until 10:00 local.

---

## Verbatim `/goal` objective

```text
TIME-BOXED MARATHON — Full Reconstruction Campaign (Battle Engine Aquila / Onslaught Toolkit).

=== SESSION CLOCK (edit these two lines per run) ===
STOP_LOCAL=10:00
STOP_DATE=today
# STOP_DATE: today | tomorrow | YYYY-MM-DD (machine local timezone)
# Meaning: keep working until local wall clock is past STOP_LOCAL on STOP_DATE.
# Example overnight: STOP_LOCAL=10:00 and STOP_DATE=tomorrow
=== END CLOCK ===

THIS IS NOT A ONE-SLICE OR FIVE-SLICE GOAL.
- A single ADVANCEMENT / dual-accept / commit is routine progress, NOT completion.
- Meeting any minimum slice count is NOT a stop reason if wall clock has not reached STOP.
- Do NOT call update_goal(completed) or stop because "quota met", "good progress", "next agent can continue", or "context might be large" while wall clock is still before STOP.
- After every slice closeout: commit/push if green → immediately pick next slice → rewrite goal.md → execute → REPEAT.

PRIMARY STOP RULE (hard):
1) At the start of every cycle AND after every closeout, check local time:
   PowerShell: Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
   Compute stop_datetime = STOP_DATE at STOP_LOCAL in local time.
   If now < stop_datetime → CONTINUE (another slice). Do not hand back.
   If now >= stop_datetime → STOP after finishing the current in-flight slice cleanly (gates, baton mutate, commit/push if green), leave resume-ready goal.md.
2) Also stop early only for: human pause; BLOCKED_* that truly needs human authority (Steam write, release/tag, paid spend, exhausted retries with no new evidence path); or OS/tooling completely unusable.
3) Context pressure: if near limit, compact by writing state to goal.md and CONTINUE with the next slice until STOP wall clock — do not end the goal early for "context".

SECONDARY FLOOR (not a ceiling):
- Prefer at least five slice closeouts if the session is long enough before STOP.
- If STOP is hours away, expect many more than five. Keep going.

Authority (every cycle, in order):
1) goal.policy.md
2) goal.campaign.md
3) goal.md  ← MUST mutate every cycle
4) AGENTS.md + nearest nested AGENTS.md
5) Slice-local docs/code only

Resume: trust goal.md + goal.campaign.md over chat. Never restart campaign from zero.
Do not reopen closed walker-forward, jet-thrust, Look/Left yaw, or Movement/Left strafe dual-accepts without overturning evidence.

Mission: continuous RE / rebuild Core-Client-Godot / WinUI 3 / lore / harness slices per goal.campaign.md priority.
Measurement-before-Core: dual-accept → public contract → translation policy → Core. Co-land tests. Lab hygiene: strip profile-app-config + runner bin/obj after live closeout; compact only.

Hard constraints:
- Never mutate Steam / original BEA.exe
- No release/tag/signing/announcement unless newer human text authorizes that family
- No parity-complete / player-ready online; Host/Join disabled
- No thrash AYA MSB4278 without new evidence
- No hosted CI/GitHub Actions
- Commit/push green waves (no force-push; no amend published history)

Slice loop (repeat until STOP wall clock):
1. Check wall clock vs STOP — if past STOP, exit loop under PRIMARY STOP RULE
2. Read policy + campaign + baton; note git tip
3. Execute Current Slice
4. ADVANCEMENT or well-formed BLOCKED_*; update goal.md + campaign milestones
5. Commit/push if green
6. Immediately select next Current Slice and go to step 1 — no human permission needed

Final report when STOP hits: local time, stop_datetime, slices closed this session, tip SHA, baton Current Slice, campaign remains ACTIVE unless exit criteria truly hold.
Do NOT claim campaign complete from a time stop alone.
```

---

## Short alias

```text
/goal Time-boxed marathon: roadmap/goals/full-rebuild-campaign-slash-goal.md with STOP_LOCAL=10:00 STOP_DATE=tomorrow. Work continuously until that local wall clock; do NOT stop after one or five slices. Mutate goal.md every cycle. Start at Current Slice.
```

## Operator notes

| Want | Set |
|------|-----|
| Work until 10:00 **today** | `STOP_LOCAL=10:00` `STOP_DATE=today` |
| Work overnight until 10:00 **tomorrow** | `STOP_LOCAL=10:00` `STOP_DATE=tomorrow` |
| Work until a calendar day | `STOP_LOCAL=10:00` `STOP_DATE=2026-07-16` |

- **Pause early:** `/goal pause` or set `goal.md` Status to `PAUSED`.
- **Why old marathons still died:** “min 5 slices” was treated as a finish line. Clock stop is the finish line; slice count is only a floor.
