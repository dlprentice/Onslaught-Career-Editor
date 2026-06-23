# WinUI Music Audible-Proof Contract

Status: contract guard only
Date: 2026-06-22
Scope: safe-copy music replacement audible-output acceptance boundary

This slice records the next acceptance bar for claiming that a staged safe-copy music replacement is audible in BEA. It does not launch BEA, attach CDB, capture audio, mutate Ghidra, or create new private runtime evidence.

Current audible status: `runtimeAudibleOutputProof=false`.

Current accepted evidence:

| Field | Value |
| --- | --- |
| Safe-copy staging | true |
| Source music unchanged | true |
| Copied target matches replacement | true |
| Restore manifest | true |
| Level-100 selection/decode proofs | 2 |
| Named preset selection/decode proof | `use-bea02-for-bea04` |
| Two-run harness acceptance checker | true |
| runtimeAudibleOutputProof | false |

The minimum future audible-output proof must include source-safety, safe-copy patch/input identity, CDB music selection/decode evidence, same audio endpoint/format, and a bounded loopback or equivalent output-capture artifact. The audio artifact must show a positive non-silent output window, correlate that window with the CDB selection/decode window, and show that the positive staged run differs from a clean same-level baseline.

The future proof must also include ambient/no-BEA and mute-control negative controls plus source-audio correlation. A run using `-nomusic` or `-nosound` cannot satisfy the positive audible-output claim, and RMS-only, peak-only, or non-silent-only evidence is not enough.

Validation:

```powershell
py -3 tools\winui_safe_copy_music_audible_output_contract_check.py --self-test
npm run test:winui-safe-copy-music-audible-output-contract
```

Claim boundary:

- Proves the public-safe audible-output acceptance contract is documented and machine-checked.
- Preserves `runtimeAudibleOutputProof=false`.
- Records `not current audible playback proof`.
- Does not prove current audible playback proof, arbitrary external OGG compatibility, all music cues, loop behavior, volume behavior, mixing or crossfade behavior, gameplay parity, rebuild parity, or no-noticeable-difference parity.
