Status: active quick reference
Last updated: 2026-09-26 (windowed guard corrected; other runtime observations remain inherited)
Source: pristine retail command-line parser and the separately dated copied-runtime observations.
Summary: Narrow Steam launch contract used by Onslaught Toolkit.
Evidence: MEASURED — fresh parser/initializer guard instructions; other runtime claims below are dated records, not rerun here.
Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

# Steam Launch Contract

This is intentionally not an exhaustive engine-switch catalog. It records the
small launch surface used by current Steam workflows. Stuart's in-house PC
source has a broader parser; those switches are not Steam contracts unless the
canonical retail parser independently contains them.

## Supported launch surface

| Parameter | Evidence-bounded behavior |
|-----------|---------------------------|
| `-res W H` | The retail parser accepts width and height. The safe-copy workflow has exercised `1600 900`. |
| `-skipfmv` | Controlled retail launches skip startup and level-intro FMV playback; click-to-start remains. |
| `-level N` | The retail parser accepts a numeric level id. Controlled safe-copy workflows use this for bounded level probes. |
| `-forcewindowed` | The pristine startup initializer clears its guard. On the canonical receiver, preceding it with `-testeur` enables this parser branch; reversing the order does not. Actual window behavior and compatibility patches are separate evidence. |
| `-nomusic` | Controlled retail use disables background music. |
| `-nosound` | Controlled retail use disables game audio. |
| `-showdebugtrace` | The retail parser accepts the flag. Toolkit exposes it only as a copied-profile diagnostic; visible output is not promised. |

Controller configuration, sensitivity, inversion, and bindings are not launch
arguments in the supported Steam workflow. Toolkit writes requested controller
settings only to the safe copy's `defaultoptions.bea`.

## Supported examples

```text
BEA.exe -res 1600 900 -skipfmv
BEA.exe -skipfmv -level 850
BEA.exe -testeur -forcewindowed -res 1600 900
```

## Source/retail boundary

The former claim that the pristine guard was already enabled was wrong.
`0x00662f3e` is uninitialized PE data, and `0x00423ad6` explicitly clears the
matching startup-object field. Parser `0x00423c7d` sets that field for
`-testeur`; `0x00424150` reads the absolute guard before `-forcewindowed`.
The [parser contract](../binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md#windowed-guard-and-logger-boundaries)
separates fresh static findings, September 19 isolated execution and inherited
retail captures. The other workflow descriptions above were not revalidated by
this naming/guard pass.

The canonical unpatched Steam executable with SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
does not contain parser literals for `-configuration`, `-norumble`,
`-nostaticshadows`, `-hidetail`, or `-textureramlimit`. Those names occur in
Stuart's different in-house PC source and are not accepted by AppCore or shown
by WinUI.

See
[`CCLIParams__GetParams`](../binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md)
for the static parser analysis and its evidence limits.
