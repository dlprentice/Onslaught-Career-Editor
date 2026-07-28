# Handoff — Ghidra fullpass + fullbreadth corrections (2026-07-25)

> ## HISTORIC — the branch this handoff directs work on no longer exists
>
> **Superseded 2026-07-27.** This document opened with, and still contains,
> standing instructions for a live branch:
>
> > "For the next agent. **Do not merge to main** unless the user asks.
> > Branch: `ghidra/fullpass-quality-2026-07-23`
> > Worktree: `C:\Users\david\source\Onslaught-Career-Editor-ghidra-fullpass-2026-07-23`"
>
> `ghidra/fullpass-quality-2026-07-23` **was merged into `main` at `af22af95`**
> on 2026-07-25, and the branch ref was deleted on 2026-07-27. Its history is in
> `main`; nothing is lost. The worktree path above **does not exist**.
>
> **Every branch, worktree, and merge instruction below is spent.** That includes
> the "Merge this branch into `main` without explicit user request" non-goal and
> the `Branch:` / `Worktree:` lines in the machine checklist — they describe a
> decision that has already been taken, not one awaiting the next agent. Read
> this file as the **record of that expedition**: its authority map, findings,
> and evidence boundaries remain useful. Do not read it as a live work item.
>
> Ghidra work has moved on since. For the current name-grading residual and the
> flag it requires, see
> [`reverse-engineering/RE-INDEX.md`](../RE-INDEX.md) — "The name-grading
> residual". The live maintainer DB has been mutated since this handoff was
> written; the tracked `ghidra/` snapshot (2026-07-18) has not.

## Authority map (read first)

| Layer | Path | Role |
| --- | --- | --- |
| **Discovery notes** | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` (W001–W018) | Wave primary/adversarial findings (~533 md). **Not** proof of DB mutation. |
| **Expedition lab (gitignored)** | `local-lab/ghidra-fullpass-2026-07-23/` | Queues, plans, dual QC, apply logs, exports, `state/correction-ops.json`. **Ops truth for this campaign.** |
| **Live Ghidra DB** | `C:\Users\david\Ghidra\Projects\BEA` | **Applied** truth (headless writes). |
| **Tracked Ghidra snapshot** | `reverse-engineering/ghidra/` (snapshot **2026-07-18**) | **Lags live** after 2026-07-24/25 corrections. Refresh is separately authorized. |
| **Tools** | `tools/Ghidra*.java`, `CreateFunctionsFromAddressList.java` | Headless apply/export/create-function. |
| **Install** | `D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC` | analyzeHeadless |
| **Backups** | `F:\GhidraBackups\` | pre/post promote copies of live project |

Lab map detail: `local-lab/.../corrections/apply/_AUTHORITY_LAB_VS_RE.md`  
Closeout: `local-lab/.../corrections/FULLBREADTH-CLOSEOUT-2026-07-25.md`  
Residual: `local-lab/.../corrections/apply/_RESIDUAL_FOLLOWON_PLAN.md`  
Ops JSON: `local-lab/.../state/correction-ops.json`

## Hard rules (still in force)

- Dual PRIMARY + ADVERSARIAL QC every gate; fail closed  
- Serial Ghidra apply only (never concurrent mutate on same DB)  
- No Steam install / original `BEA.exe` mutation  
- Hash plans/TSVs as **raw bytes**  
- Forward slashes in path-like comments  
- No invent-add tags; never remove `signature-corrected` casually  
- Comment/tag/rename lanes only unless user authorizes create-function listing recovery  
- `loop.armed=false` unless user re-arms  
- Ask before git commit (this handoff is the authorized push of **tracked** docs/tools only)

## Fullbreadth scoreboard (campaign CLOSED)

| Lane | Count | Outcome |
| --- | ---: | --- |
| needs_signature | 511 | Live dual CLEAR |
| needs_name | 228 | Live comments |
| + renames | 28 | Live `GhidraBatchRename` dual CLEAR |
| needs_tags | 234 | Live 20 scrub / 214 KEEP |
| overclaim | 25 | Live 24 REWRITE + was 1 quarantine (see residual) |
| needs_comment | 52 | Live |
| needs_boundary | 12 | Live dual CLEAR |
| possible_missing_neighbor | 322 | Plan dual CLEAR: 250 Q / 72 KEEP / **0 REWRITE** (no invent-FN) |
| T0 | 3 | Plan dual CLEAR: all QUARANTINE |

**Queue JSONL still lists historical tokens** — that is **not** remaining apply work. Drain = plan-set + dual CLEAR (+ live when REWRITE).

## Residual work status (after fullbreadth)

| ID | Work | Status |
| --- | --- | --- |
| R1 | `0x004062d0` rename → `Mat34__SetFromEulerAngles_004062d0` + comment | **LIVE** dual CLEAR |
| R2 | 28 stale “propose-only” comments → “Rename applied: …” | **LIVE** dual CLEAR |
| R3 | T0×3 re-check | **No mutate** — live plates already instruction-backed |
| R4 | Neighbor listing recovery (create functions) | **STOPPED before live** |

### Why R4 stopped

Dry-run `CreateFunctionsFromAddressList` on `project-rw` for **257** gap-start candidates: **`would_create=257`**, `already_exists=0`, `failed=0`.

Bulk create without per-span dual **code vs pad** filter risks mass false functions on padding/data.  

**Preserved artifacts (lab only):**

- `corrections/apply/_neighbor_create_function_candidates.txt` (257)  
- `corrections/apply/_neighbor_create_function_dry.tsv`  
- dry log on project-rw  

**Safe resume recipe (if user authorizes):**

1. Multi-agent dual classify each gap: **code / pad / data / already-fn**  
2. Keep only dual-CLEAR **code** starts (canary 5–20 first)  
3. Dry-run create on `project-rw` → dual readback  
4. Live create only after canary CLEAR  
5. Optional comment plates only after functions exist  
6. Never invent class names for recovered stubs without evidence  

## Live apply proof (high signal paths)

### Tools used

- `GhidraApplyFunctionCommentsFromTsv.java`  
- `GhidraApplyTagOpsFromTsv.java` (now tracked)  
- `GhidraBatchRename.java`  
- `ExportFunctionMetadataByAddress.java` / `ExportFunctionTagsByAddress.java`  
- `CreateFunctionsFromAddressList.java` (dry only for neighbor)  

### Residual R1+R2

- Live: `C:\Users\david\Ghidra\Projects\BEA`  
- Logs:  
  - `local-lab/.../corrections/apply/t3_residual_004062d0_apply_live.log` — rename=1 comment=1 bad=0  
  - `local-lab/.../corrections/apply/t3_residual_rename_comments_28_apply_live.log` — applied=28 bad=0  
- Backups:  
  - `F:\GhidraBackups\BEA_20260725-033712Z_pre_promote_t3_residual_r1_r2`  
  - `F:\GhidraBackups\BEA_20260725-033736Z_post_promote_t3_residual_r1_r2`  
- Readback: `local-lab/.../corrections/qc-t3-residual-r1-r2-readback/metadata_live.tsv`  
  - name `0x004062d0` = `Mat34__SetFromEulerAngles_004062d0`  
  - 28/28 comments contain `Rename applied:` + exact map name  

## What is in THIS git commit vs lab-only

| In git (this branch) | Lab-only (gitignored `/local-lab/`) |
| --- | --- |
| RE front doors (RE-INDEX, binary-analysis index, ghidra README) | All plans, QC notes, apply logs, exports |
| `ghidra-fullpass-findings/` discovery tree | `state/correction-ops.json` |
| `tools/GhidraApplyTagOpsFromTsv.java` | `project-rw` / `project-ro` clones |
| This handoff markdown | Backups on F:\ |

**Critical:** Finishing residual work **requires the lab tree on this machine**. Cloning only git is not enough for ops history.

## Recommended next work for finishing agent

### Priority A — if user wants listing recovery (large)

1. Read residual plan + taxonomy in lab  
2. Dual-agent code-vs-pad on canary 10–20 of 257 candidates (use `DiagnoseAddressListingState` / disasm dumps)  
3. Create-function canary on `project-rw` only → dual QC  
4. Promote canary to live only after dual CLEAR  
5. Scale in batches of ≤20  

### Priority B — tracked Ghidra snapshot refresh (user-authorized)

1. Copy or headless-export policy from live `Projects\BEA` into `reverse-engineering/ghidra/` per project rules  
2. Update snapshot date/hash in `ghidra/README.md`  
3. Separate commit; do not force-push  

### Priority C — hygiene only

- Ensure RE docs stay aligned if more residual lands  
- Do not re-open fullbreadth lanes; queue tokens are historical  

## Explicit non-goals unless user re-scopes

- Invent functions from comments alone  
- Bulk create 257 functions without filter  
- Mutate Steam install  
- Merge this branch into `main` without explicit user request  
- Re-arm agent loop without user request  

## Machine checklist for next agent

**The `Worktree:` and `Branch:` lines below are spent — see the banner at the top
of this file. The branch was merged at `af22af95` and deleted; the worktree path
does not exist.** The remaining paths were still accurate as of 2026-07-27.

```
Worktree:  C:\Users\david\source\Onslaught-Career-Editor-ghidra-fullpass-2026-07-23
Branch:    ghidra/fullpass-quality-2026-07-23
Lab:       local-lab\ghidra-fullpass-2026-07-23
Live DB:   C:\Users\david\Ghidra\Projects\BEA
Ghidra:    D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC
Backups:   F:\GhidraBackups\
Ops:       local-lab\...\state\correction-ops.json
```

Verify: `loop.armed` is false; residual_r4 status is `STOPPED_before_live`.

## One-sentence summary

**Fullbreadth comment/tag/rename campaign is complete on live; residual rename+hygiene applied; neighbor create-function was prepared then deliberately stopped as too risky unfiltered; lab holds ops truth (gitignored); tracked ghidra snapshot may lag live.**
