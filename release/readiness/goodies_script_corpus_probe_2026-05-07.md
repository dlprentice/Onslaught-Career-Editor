# Goodies Script Corpus Probe - 2026-05-07

## Scope

This note records read-only scans of the repo-local mission-script corpus and the user's installed Steam mission-script corpus for `GetGoodieState(...)` and `SetGoodieState(...)` calls. The raw script corpus remains private/release-excluded; this public-safe note records counts only.

It does not launch BEA, mutate `BEA.exe`, patch the installed game, mutate saves, or inspect non-MSL binary paths.

## Commands Run

| Command | Result | Important Output | What It Proves |
| --- | --- | --- | --- |
| `py -3 tools\goodies_script_corpus_probe.py --check --require-root` | PASS | `files=733 calls=32 indices=51,53,68,69,70,71 target72to74=0` | The checked local mission-script corpus has Goodie state calls, but none for the 1-based script indices 72-74 that would correspond to save Goodies 71-73. |
| `py -3 tools\goodies_script_corpus_probe.py --check --require-root --script-root <installed-game>\data\MissionScripts --out <ignored-output>` | PASS | `files=733 calls=32 indices=51,53,68,69,70,71 target72to74=0` | The installed Steam mission-script corpus reports the same public-safe Goodie state call summary. |

## Finding

- Mission scripts use 1-based Goodie indices.
- The checked local and installed Steam corpora use script indices `51`, `53`, and `68-71`.
- Goodies 71-73 would require script indices `72`, `73`, and `74`.
- Both checked corpora have zero calls for script indices `72-74`.

## Not Claimed

- This is not proof that packed/runtime scripts cannot differ from the checked corpus.
- This is not copied-profile runtime proof.
- This does not prove hidden/non-grid Goodies 71-73 reachability is impossible.
