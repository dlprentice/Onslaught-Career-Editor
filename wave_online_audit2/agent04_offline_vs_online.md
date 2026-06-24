# Offline vs Online Audit Contradictions (Commit 4240f34 vs Online Report)

## Sources Reviewed

- Offline artifacts from commit `4240f34`:
  - `reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md`
  - `reverse-engineering/binary-analysis/semantic-audit-pass-2026-02-12.json`
- Online audit report (current repo):
  - `reverse-engineering/binary-analysis/semantic-audit-online-2026-02-12.md`
  - `reverse-engineering/binary-analysis/semantic-audit-online-pass-2026-02-12.json`

## High-Level Contradictions

1. **Offline reports “clean” semantics, while online shows concrete name/function mismatches.**
   - Offline summary claims no “Verified vs Source: Yes” docs missing `references/Onslaught` citations and indicates headers are normalized.
   - Online audit finds **124 name mismatches** and **124 missing functions** across 66 files.
   - These are different checks, but the doc phrasing implies semantic integrity that online checks invalidate (binary naming vs doc expectations).

2. **Offline markdown vs offline JSON counts disagree.**
   - Offline markdown claims **171** function docs with a `Source:` header, **155** referencing `references/Onslaught/`, **16** missing.
   - Offline JSON reports **117** function docs with header source line, **112** referencing `references/Onslaught/`, **30** snapshot gaps.
   - This is a direct contradiction inside the offline artifacts and undermines “clean” framing.

3. **Offline “normalized Source” naming pushes `CCareer::` style, online expects binary symbols (`__`).**
   - Offline normalization favors Stuart-style `CCareer::...` in headers.
   - Online mismatches show expected `CCareer::...` vs actual `CCareer__...` names in Ghidra.
   - Example paths where this appears in both repo and lore-book mirrors:
     - `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
     - `reverse-engineering/binary-analysis/executable-analysis.md`
     - `lore-book/reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
     - `lore-book/reverse-engineering/binary-analysis/executable-analysis.md`

## Representative Offline-Clean vs Online-Fail Examples

These show documents “clean” under offline semantic checks but failing against online symbol verification:

- **Name mismatches (expected Stuart-style or generic names, actual Ghidra symbols differ):**
  - `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
    - 0x004213c0 expected `CCareer::SaveToFile`, actual `CCareer__SaveWithFlag`.
  - `reverse-engineering/binary-analysis/executable-analysis.md`
    - 0x00421350 expected `CCareer::Save`, actual `CCareer__Save`.
  - `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
    - 0x0044b060 expected `FUN_0044b060`, actual `CEventManager__Init`.
  - `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
    - 0x00404960 expected `CAtmospheric__Unlink`, actual `FUN_00404960`.
  - `reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md`
    - 0x00541220 expected `CDXFrontEndVideo::~CDXFrontEndVideo`, actual `CDXFrontEndVideo__dtor`.

- **Missing functions (doc expects a function object at address, online says `None`):**
  - `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
    - 0x0043f510 expected `CCutscene__InitAnimations`, actual `None`.
  - `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`
    - 0x0046cfe2 expected `CGame__LoadLevel`, actual `None`.
  - `reverse-engineering/binary-analysis/functions/DataType.cpp.md`
    - 0x005e4af8 expected `CDataType__ScalarDeletingDestructor`, actual `None`.
  - `reverse-engineering/binary-analysis/README.md`
    - 0x004f7a80 expected `CScriptObjectCode__Run`, actual `None`.

These failures appear both in primary docs and their `lore-book/` mirrors.

## Likely Root Causes

- **Scope mismatch:** Offline audit checks only source citation integrity, not live binary naming.
- **Naming convention collision:** Offline normalization pushes Stuart `CCareer::` names; online expects actual Ghidra symbol names (often `CCareer__`, or still `FUN_` if not renamed).
- **Missing function objects:** Addresses are documented, but Ghidra currently lacks function objects at those addresses (or they are not created), producing `missing_function`.
- **Mirror drift:** Failures duplicate into `lore-book/` copies, which are not separately validated in offline checks.

## Recommended Doc/State Updates to Reconcile

### Documentation updates

1. **Clarify scope in offline audit summary.**
   - Update `reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md` to state explicitly:
     - “Offline audit validates source citation integrity only; it does not validate Ghidra symbol names or function existence.”
     - Link the online report and mention current online fail counts.

2. **Resolve internal offline count contradiction.**
   - Recompute or annotate the mismatch between the markdown summary and JSON counts.
   - Add a note if counts reflect different parsing or filtering modes.

3. **Introduce a naming-policy note for docs.**
   - In `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` (and mirror):
     - Document that `Source:` entries may use Stuart-style `CCareer::` while binary expectations use `CCareer__`.
     - Optionally define a mapping rule for audits: `::` -> `__` for binary comparison.

4. **Flag missing-function expectations as “orphan/expected-missing” where appropriate.**
   - For addresses known to lack function objects, add explicit “expected missing function” tags or update tables to match audit rules.

5. **Mirror hygiene:**
   - Apply any updates to both primary docs and `lore-book/` mirrors to prevent duplicated online failures.

### State updates

1. **Update `documentation_agent_state.json`**
   - Record that offline semantic audit is “clean” for citation integrity but conflicts with online audit results (name/missing function mismatches).
   - Track the naming-convention mismatch and count discrepancy as open questions.

2. **Update `re_orchestrator_state.json`**
   - Add a task for aligning doc naming conventions with online audit expectations (or updating audit tooling to accept aliasing).
   - Add a task for addressing missing function objects in Ghidra (if and when MCP/Ghidra is allowed again).

## Suggested Next Steps (No MCP/Ghidra)

- Decide whether to:
  - **Normalize docs to binary names** (easiest for online audit), or
  - **Extend online audit to accept alias mapping** (`CCareer::` → `CCareer__`).
- After decision, update both primary docs and `lore-book/` mirrors.
- Re-run offline and online audits to confirm clean status alignment.
