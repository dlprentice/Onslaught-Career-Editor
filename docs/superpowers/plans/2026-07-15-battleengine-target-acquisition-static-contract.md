# BattleEngine Target-Acquisition Static Contract Implementation Plan

1. Capture focused baseline failures for the stale targeting bridge and
   Unit/BattleEngine contract gate without launching BEA or Ghidra.
2. Add failing unit tests for the new contract validator: canonical anchors,
   evidence tiers, sequence order, false guards, evidence paths, Markdown
   coverage, and rejection of the superseded `0x00406560` name.
3. Implement the smallest parser/checker that makes the unit fixtures pass.
4. Add the v1 JSON and Markdown contract, then correct the three address-bound
   function notes and the current Unit/BattleEngine targeting summary.
5. Repair the two focused legacy compatibility gates against current authority
   and add one package command for the new contract.
6. Run the focused tests, contract gate, compatibility gates, JSON/docs/link/
   payload checks, Python compile, diff check, and zero-process census.
7. Review the integrated diff for concrete claim or safety defects, resolve
   them, commit/push, and advance the campaign baton without claiming goal
   completion. No fixed review envelope or external consult is required.
