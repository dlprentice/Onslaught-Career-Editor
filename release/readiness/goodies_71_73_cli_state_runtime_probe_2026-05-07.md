# Goodies 71-73 CLI-State Runtime Probe - 2026-05-07

Status: YELLOW runtime probe, public-safe summary

## Objective

Use the new C# CLI `--set-goodie-state` helper in a copied-profile runtime replay to test whether forcing Goodies 71, 72, and 73 to `NEW` in a copied save changes normal Goodies wall behavior.

## Safety Posture

- The installed Steam game root was treated as read-only source material.
- A copied profile was created under ignored `subagents/`.
- The copied executable was verified with the `force_windowed` patch state; no bytes were written in this pass because the copied executable was already patched.
- The installed save was not mutated.
- Copied saves and backups stayed under ignored `subagents/`.
- Raw screenshots, JSON, and local paths stayed private.
- `BEA.exe` was stopped at the end of the probe.

## Copied-Save State Setup

The final controlled save used for the second replay had this public-safe Goodie window:

```text
66 OLD
67 OLD
68 OLD
69 OLD
70 OLD
71 NEW
72 NEW
73 NEW
74 OLD
75 OLD
76 OLD
77 OLD
```

The setup used the C# CLI helper, not ad hoc byte editing.

## Runtime Observations

The replay successfully launched a copied profile, loaded the controlled copied save, opened the Goodies wall, and captured private frames.

Visible observations from the private captures:

- The Goodies wall opened with unlocked entries.
- The replay saw nearby unlocked Goodie labels including `Hawk Winter`, `Tatiana Kiralova`, and `Race Challenge 2`.
- The replay did not show `All Configurations`, `Free Camera Mode`, or `God Mode` as visible/selectable wall labels.
- The replay did not reproduce the earlier edge-scroll proof that reached Race Challenge 5 then skipped to Battle Engine Aquila Picture.

## Verdict

YELLOW.

This pass proves the new CLI helper can prepare copied-save runtime inputs and that a copied-profile replay can load the controlled save and open the Goodies wall. It does not prove the hidden/non-grid status of Goodies 71-73, because this run stalled at `Race Challenge 2` and did not reproduce the known 70-to-74 edge-scroll sequence.

## Likely Next Work

The next Goodies runtime wave should improve the replay harness before making reachability claims:

- capture or infer selected Goodie ids directly where possible,
- improve deterministic Goodies-wall navigation past `Race Challenge 2`,
- or attach a read-only runtime probe to `get_goodie_number`, `StartLoadingGoody`, and selection-state updates while navigating.

Follow-up static guard: `GoodieWallGridMappingService_RaceRowSkipsHiddenGoodiesToDeveloperItems` now asserts the expected normal row sequence `66, 67, 68, 69, 70, 74`. Runtime replay should reproduce or explain divergence from that exact invariant.

## Not Claimed

- This is not proof that Goodies 71-73 are unreachable.
- This is not proof that copied-save state forcing changes runtime reachability.
- This did not mutate the installed game or original executable.
- This did not commit private screenshots, copied saves, copied executables, or raw proof JSON.
