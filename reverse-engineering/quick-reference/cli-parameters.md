Status: active quick reference
Last updated: 2026-09-30 (what every retail option does, read through the byte-matched decompilation)
Source: pristine retail command-line parser, each option's readers, and the separately dated copied-runtime observations.
Summary: the Steam launch surface Onslaught Toolkit uses, and what each of the retail parser's 25 options does in the game.
Evidence: MEASURED — fresh parser/initializer guard instructions and, on 2026-09-30, every retail instruction that reads
an option's field or global; readers are cited by the bea-decomp function that compiles to their retail bytes, or by
retail address where that function does not match yet. Runtime claims are dated records, not rerun here.
Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

# Steam Launch Contract

The first table is the small launch surface current Steam workflows use. The
[second](#what-every-retail-option-does) says what every option the retail parser
accepts does in the game. Stuart's in-house PC source has a broader parser; those
switches are not Steam contracts unless the canonical retail parser independently
contains them.

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

## What every retail option does

Steam passes launch options as typed in the game's **Properties → General → Launch Options** box, separated by
spaces, with each value straight after its option (`-skipfmv -level 856`); with a Proton `%command%` line, put them
after `%command%`. Options apply only to that launch.

Each row names the reader of the option's field, found by searching the retail code for every access to it (`match`:
the bea-decomp function compiles to its retail bytes; `near miss`: read from retail's instructions). Only `-level`,
`-skipfmv`, `-res`, `-nomusic`, `-nosound` and `-testeur -forcewindowed` have runtime records (above); every other
row is a static reading, and nothing was launched for it.

| Option | What it does | Limits |
| --- | --- | --- |
| `-level N` | Skips the front end and runs world `N` (`CSystem::Run` 004f0330, match). A co-operative or versus world starts two players in split screen; player two uses the other controller port (`CGame::LoadLevel` 0046cdf0, match). | Only the 66 worlds with an archive load ([level inventory](../game-assets/level-inventory.md)). When the level ends the game exits to the desktop. |
| `-skipfmv` | Skips the startup films and splash (`CSystem::Init` 004efb10, match) and the level intro films (`CGame::GetIntroFMV` 0046d810, match). | Also stops the menus' video backgrounds from opening (`CDXFrontEndVideo` 00541140 and 00541430, match). |
| `-res W H` | Sets the screen size the display mode is chosen with (read at 005291aa, 0052a3e4 and 0052afe3, near miss). | Either value below 640×480 resets both to 640×480. |
| `-nomusic` | The front end and the Goodies page start no music (`CFrontEnd::Init` 004662a0, `CFEPMain` 00462640, `CFEPGoodies::Process` 0045d7e0, all match). | |
| `-nosound` | Starts neither the sound system nor music (`CSystem::Init` 004efb10, match): the game is silent. | |
| `-testeur` | Allows `-forcewindowed` (below). In a level, **B** saves the screen to `grabs\scrNNNN.tga` in the game folder (`CGame::DrawGameStuff` 004714c0, match). | Must come before `-forcewindowed` on the line. With every cheat on, **B** asks for a screen dump instead (as `-autoconfigtest`). |
| `-forcewindowed` | Runs in a window when the display mode allows one (device list, 0052a644, near miss). | Needs `-testeur` earlier on the line (guard at 00424150). Other windowed problems are in [windowed-mode-analysis.md](../binary-analysis/windowed-mode-analysis.md). |
| `-e3` | The one runtime switch left from the E3 show build. After the startup films it asks for a `vectorlosttoyssplash.tga` splash instead of `splash.tga` (`CSystem::Init` 004efb10, match), and it locks one multiplayer cell, 859 (0051d28c..0051d2a2). It also lets `-timeout` work (below). | Not the E3 build: that build's compiled-in differences are absent. The E3 splash is not in the install. Its built-in two-minute timeout never takes effect, because the constructor that sets it (004239f0, match) runs before the command line is read. |
| `-timeout N` | After `N` milliseconds without input the game drops back to its intro films, from the menus or from a level (`CController::InactivityMeansQuitGame` 0042d810, match). | Only with `-e3` or `-playabledemo`; otherwise ignored. |
| `-playabledemo` | Turns the front end into the 2003 demo's: a demo main menu whose first choice plays level 201, no story cutscenes, and the controls screen during loading (`CFEPDemoMain::DoAction` 00457ee0 and about 30 other reads, most match). | Static reading; not run on the full install. |
| `-autoconfigtest [DIR]` | An unattended configuration test: it clicks through the menus and a level by itself, takes screen dumps on fixed frames, changes a setting in the pause menu and restarts (`CGame` 0046e921 and the front-end pages). It writes the dumps and `setuphistory.txt` to `DIR`, default `C:\beaautoconfigtest\`, creating the folder. While it runs every cheat counts as on, the mouse is ignored and the music is track 8. After 20,100 frames it switches itself off and turns on every cheat for the rest of the session (0046e921). | `C:\` is the Wine prefix's drive under Proton. With every cheat on the game does not autosave after a level (`CFrontEnd::Init` 004662a0). |
| `-cardid` | Reads the graphics-card list from `C:\cardid.txt` instead of the game folder's `cardid.txt` (0052af2a, near miss). | Without a copy there, the list is not found. No player benefit. |
| `-backbuffer2` | Two back buffers (triple buffering) instead of one (0052b05e, near miss). | Untested. |
| `-32bittextures` | Asks for uncompressed copies of the compressible textures in `data\resources\textures` (`CDXTexture` 00557300, near miss). | Only 8 of the 800 compressed textures have such a copy; for the rest the loader falls back to the compressed file after a failed open. Little or no visible gain. |
| `-dxtntextures` | Compressed textures, which is already the default. | Only undoes an earlier `-32bittextures`. |
| `-landscape0`, `-landscape1`, `-landscape2` | Forces terrain rendering method 0, 1 or 2 (`CRenderMethod::Set` 00527d00, match). The default is method 3, the richest, and the game steps down by itself when the card rejects one. | A forced method is marked accepted, so that check is skipped. Lower numbers give plainer terrain. |
| `-soundbuffers N` | Uses `N` sound voices instead of the card's count (`CPCSoundManager::DeviceInit` 005169b0, match). | The card's count is capped at 64, a given `N` is not: above 64 the free-voice search (`FindFreeChannel` 00517cb0) hands out voices past the 64-entry table. Keep `N` at 64 or below. |
| `-defaultoptionsname NAME` | Loads the startup settings and key bindings from `NAME` instead of `defaultoptions.bea` (`WinMain` 00512130, match). | The options screen still saves to `defaultoptions.bea`. No spaces in `NAME`. |
| `-getversion` | Prints `Version 1.00.00` (from the executable's version resource) and quits with exit code 10000 before starting. | A Windows program has no visible console, so only the exit code shows. |
| `-findgoodwater` | A developer trap: when the device accepts the water setup, the water pass sleeps in a loop and the game freezes (0055c33c..0055c36a, `Sleep(100)`). | Freezes on working hardware as soon as water is drawn. Do not use. |
| `-findbadwater` | A developer trap: the water method is re-checked every frame (0055c1ad), and while the device rejects the water setup the water pass sleeps in a loop (0055c36c..0055c398). | On hardware that accepts the water it only re-checks; where the check fails, the game freezes. |
| `-traceconsole` | Stored, never read (no retail instruction touches the field). | No effect. |
| `-showdebugtrace` | Stored, never read (no retail instruction touches the field). | No effect. |

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
