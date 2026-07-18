# CLIParams__ParseCommandLine

> Address: 0x00423bc0 | Source: `references/Onslaught/CLIParams.cpp` (`CCLIParams::GetParams(char *text)` parser shape)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __thiscall CLIParams__ParseCommandLine(void * this, char * commandLine)`)
- **Verified vs Source:** Partially (retail parser shape matches the source text-parser overload; the exact retail flag set differs from Stuart's internal source)

## Purpose

Parses command-line arguments passed to BEA.exe. The retail PC port has a different set of parameters than Stuart's internal source code shows.

A direct literal/xref scan of the canonical unpatched Steam executable
(`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`)
was repeated on 2026-07-18. The retail parser has no literal or parser branch for
`-configuration`, `-norumble`, `-nostaticshadows`, `-hidetail`, or
`-textureramlimit`; those belong to Stuart's different in-house PC parser.

## Signature
```c
void __thiscall CLIParams__ParseCommandLine(void *this, char *commandLine);
```

Wave 320 saved this Ghidra signature and a bounded public-safe comment on 2026-05-10. The function is reached from `CLTShell__WinMain`, takes the command-line string as its lone stack argument, tokenizes it into local `0x100`-byte slots, and scans the observed retail flag set.

## Parameter Parsing Logic

The retail body tokenizes the command-line string into fixed-size local token slots, then iterates through those tokens with case-insensitive string comparisons:

```c
// Pseudocode
for (int i = 0; i < token_count; i++) {
    if (stricmp(tokens[i], "-level") == 0) {
        parse_int(tokens[++i], &level);
    }
    else if (stricmp(tokens[i], "-skipfmv") == 0) {
        g_skipFMV = 1;
    }
    else if (stricmp(tokens[i], "-forcewindowed") == 0) {
        if (DAT_00662f3e != 0) {  // GUARDED!
            g_forceWindowed = 1;
        }
    }
    // ... more parameters
}
```

## -forcewindowed Guard Flag

The windowed mode parameter is guarded by a global flag:

| Address | Symbol | File Offset | Value |
|---------|--------|-------------|-------|
| 0x00662f3e | DAT_00662f3e | 0x262F3E | Canonical Steam hash `74154bfa...` = **0x01** (historical variants with `0x00` reported) |

```c
// Guard check
if (DAT_00662f3e != 0) {
    g_forceWindowed = 1;
}
```

`-forcewindowed` parsing is guard-gated by this byte. In the canonical Steam hash used in this repo (`74154bfa...`), the byte is `0x01`; historical variants with `0x00` explain reports where parser gating blocked the parameter.

### How to Enable

If a variant has `0x262F3E = 0x00`, patch to `0x01` to allow parser processing of `-forcewindowed`.

See [windowed-mode-analysis.md](../../windowed-mode-analysis.md) for the full investigation into windowed mode.

## Parser-Visible Parameters

| Parameter | Type | Effect |
|-----------|------|--------|
| `-level N` | int | Skip to level N |
| `-skipfmv` | flag | Skip startup and level-intro FMV playback; click-to-start remains |
| `-nomusic` | flag | Silence music |
| `-nosound` | flag | Silence all audio |
| `-res W H` | int int | Set resolution |
| `-showdebugtrace` | flag | Debug output |
| `-traceconsole` | flag | Console logging |

## Additional Parser Branches (Discovered Dec 2025)

| Parameter | Type | Effect |
|-----------|------|--------|
| `-e3` | flag | E3 demo mode (trade show build) |
| `-cardid` | flag | Force card identification mode |
| `-backbuffer2` | flag | Double backbuffer for rendering |
| `-timeout N` | int | Set timeout value |
| `-soundbuffers N` | int | Set number of sound buffers |
| `-autoconfigtest [path]` | string (optional) | Run auto-config test |
| `-testeur` | flag | Test mode (European QA flag?) |

See the [retained function index](../_index.md) for related command-line notes.

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Retail binary has fewer parameters than source code suggests, and not every parser-visible flag has current runtime proof.
- Wave 320 saved the Ghidra signature/comment and refreshed the static queue from `5876` functions, `705` commented, `5171` commentless, and `2023` undefined signatures to `715` commented, `5161` commentless, and `2013` undefined signatures after the CLI/FlexArray correction.
- No `-GOD` parameter exists - god mode relies on save-name checks (B4K42 in source/internal; `Maladim` in the PC port, later confirmed to expose a visible toggle and real combat-damage effect)
- The `-forcewindowed` parser path is guard-gated; baseline value depends on binary variant (`74154bfa...` uses `0x01`)
- This static pass does not prove runtime behavior, concrete `CCLIParams` layout, local variable names, tags, or rebuild parity.
