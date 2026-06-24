# Deep Mismatch Scan — 2026-03-03

> Status: superseded/clarified on 2026-03-04. Keep this as an archival scan log; canonical parity conclusions should reference `parity_scan_shell/summary.tsv` plus the normalization note below.

## Scope

- Target: detect subtle C#/Python/save-format drift analogous to the previous slot-232 issue.
- Focus areas:
  - Patch-byte parity between C# CLI and Python CLI.
  - Keybind parser/validator parity.
  - Critical constant/offset parity.
  - UI default/behavior parity where user-facing safety can drift.

## Artifacts

- `parity_scan_shell/summary.tsv`
- `parity_fuzz_rel/fuzz_results_rel.json`
- `parity_corpus/corpus_parity_summary.json`
- `bind_matrix/bind_matrix_summary.json`

## Results

1. Deterministic scenario parity (`parity_scan_shell`)
- 5/5 targeted scenarios: C# and Python produced byte-identical outputs.
- Included career and options-style workflows, keybind overrides, and options-copy flows.
- Note: `goodies:no` in `summary.tsv` is a formatting false-negative caused by header/path text diffs in analyzer output (`File:` line), not a payload mismatch.

2. Randomized fuzz parity (`parity_fuzz_rel`)
- 40 generated mixed `.bes/.bea` cases.
- 33 both-success cases: all byte-identical.
- 7 both-error cases: identical guard rejection (`--copy-options-from` with both copy sections disabled).
- 0 one-side failures.

3. Corpus parity (`parity_corpus`)
- 71 scenarios across local `save-attempts/*.bes` and `.bea` corpus.
- 71/71 both-success.
- 0 one-side failures.
- 0 byte mismatches.

4. Keybind token matrix parity (`bind_matrix`)
- 360 action/token combinations.
- 0 mismatches in accept/reject behavior or output bytes.

5. Constant/offset parity (code-level)
- Critical constants/offsets matched across:
  - `BesFilePatcher.cs`
  - `patcher.py`
  - `onslaught/core/constants.py`
- No drift found in checked fields (file size, section bases, control offsets, goodie counts/display bounds).

## Real mismatch found and fixed

### Python GUI defaults were riskier than C# defaults

Issue:
- `onslaught/gui/tabs/save_editor.py` defaulted patch sections ON and copy-options checkboxes ON, while current C# behavior is safe-first.

Fix:
- Set Python defaults to safe-first:
  - Missions/Links/Goodies/Kills defaults OFF.
  - Copy-options entries/tail defaults OFF with no source selected.
  - First copy-source selection now mode-aware:
    - Save mode: entries/tail remain opt-in (OFF/OFF).
    - Configuration mode: entries ON, tail OFF.

Additional cleanup:
- Corrected stale C# comment in `Views/SaveEditorView.xaml.cs` to match actual first-source defaults.

## Validation after fixes

- `python3 -m py_compile onslaught/gui/tabs/save_editor.py` passed.
- `dotnet build "Onslaught - Career Editor.sln" -v minimal` passed.

## Conclusion

- No additional binary-write drift was found after the slot-232 correction.
- One meaningful UX/safety parity mismatch was found and corrected.
- Current C# and Python patch engines are strongly aligned on tested coverage.
