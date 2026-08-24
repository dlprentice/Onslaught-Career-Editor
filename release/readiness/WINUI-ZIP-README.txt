Onslaught Toolkit - WinUI ZIP Package
=====================================

This ZIP package is the non-cert distribution shape for the WinUI 3 app.
It is not an installer, MSIX package, Microsoft Store package, or signed
installer release. Everything lives under one Onslaught-Toolkit\ folder so
Extract Here does not spill app\ into the folder you extracted into.

Onslaught Toolkit is an unofficial community project. It is not affiliated
with or endorsed by the game's publishers or rights holders. This package does
not grant rights in Battle Engine Aquila or its assets.

Quick start
-----------

1. Extract the whole ZIP to a writable folder.
2. Open the Onslaught-Toolkit folder and run Launch Onslaught Toolkit.cmd.
3. If the launcher is blocked by local policy, run
   app\OnslaughtCareerEditor.WinUI.exe from that same folder.
4. Keep the files together; do not move the executable away from the
   app folder and its support files.


Windows will warn you about this app. Here is why, and how to check it.
-----------------------------------------------------------------------

You will probably see a blue "Windows protected your PC" box, or Windows will
say the download is not commonly downloaded and might be dangerous.

That warning is correct and expected. It does not mean anything was detected in
this app. It means the app is not code-signed. A signing certificate costs money
every year and has to be tied to a verified legal identity, and this is a free
community preservation project with neither. SmartScreen also builds
"reputation" from download counts, so a small project sits at zero regardless.

You do not have to take that on faith. Check the file against the hash the
project publishes:

  1. Download the .zip and the matching .zip.sha256 file from the release page.
  2. Open PowerShell in the folder where you saved them and run:

       Get-FileHash .\<the-zip-file>.zip -Algorithm SHA256

  3. Compare the Hash it prints with the value inside the .sha256 file. They
     are the same 64 characters if the download is intact and unmodified.

  A hash match proves the file is exactly what the project published. It is not
  a promise the project is trustworthy - nothing you can compute on your own
  machine is. It rules out the download being corrupted or tampered with in
  transit, which is the part a hash can actually settle.

To run it past the warning:

  - On the blue "Windows protected your PC" box, click "More info", then
    "Run anyway".
  - If the ZIP itself is marked, right-click the .zip BEFORE extracting, choose
    Properties, tick "Unblock" at the bottom, then Apply. Doing this before
    extraction saves unblocking the files one at a time.

If you would rather not do any of that, that is a completely reasonable
decision. The source is on GitHub and it builds with the .NET SDK; the exact
commands the project uses to build and check this package are in the repository.

Licenses
--------

- LICENSE contains the Onslaught Toolkit source license.
- app\THIRD_PARTY_NOTICES.md identifies the restored dependency graph.
- THIRD_PARTY_LICENSES\ contains the corresponding package terms, .NET runtime
  notices, LibVLC source locations, and compatible-library replacement path.

First run
---------

- The Lore reader includes a short lore-book\ entry point plus a generated
  lore-pack\ content pack for offline search and reading of public Markdown/TXT
  Lore documents. Included document links stay in the reader. External links
  open in your browser.
- The packaged Lore library content is stored through short lore-pack\ files
  instead of raw long lore-book\ filenames, so normal Explorer extraction
  remains reliable.
- If Battle Engine Aquila is installed in Steam or a known Steam library,
  the app attempts to find and save that read-only game folder automatically.
- Media and safe copied-game workflows need a local Battle Engine Aquila
  install. If auto-detect does not find it, open Settings and choose the game
  folder manually.
- Asset Library needs a generated local asset catalog. It does not browse raw
  game files directly; choose a folder containing asset_catalog\catalog.json or
  catalog.json after generating/exporting assets locally. Catalog generation is
  a source-repository/lab workflow documented at
  https://github.com/dlprentice/Onslaught-Career-Editor/tree/main/reverse-engineering/game-assets;
  this portable app ZIP only loads an existing generated catalog.
- Lore rendering uses the Microsoft Edge WebView2 Runtime. Current Windows
  systems usually already have it; if the Lore page cannot initialize on a
  fresh machine, install or repair WebView2 and keep the extracted files
  together.

Safety notes
------------

- By default the app works on copies: copied saves, copied options files, and
  copied game executables. Your installed game is only read.
- You can choose to have it patch your installed game instead. When you do, it
  copies your original BEA.exe next to it as BEA.exe.original.backup and checks
  that copy byte for byte BEFORE it writes anything. If the backup cannot be
  made and verified, the patch does not happen. The app can also put the
  original back.
- Nothing deletes your career saves as a side effect. If you remove a game copy
  that has saves inside it, the app finds them, tells you, and offers to keep
  them somewhere first.
- Full game assets, raw saves, private screenshots, raw/private proof JSON,
  generated media caches, and local test outputs are not included in this ZIP
  lane.
- Game-aware workflows require the user's own lawfully obtained retail data.

What this package shape proves
------------------------------

The repository ZIP probe builds disposable WinUI publish output, stages a
friendly portable root under one Onslaught-Toolkit\ wrapper with this README,
LICENSE, THIRD_PARTY_LICENSES\, Launch Onslaught Toolkit.cmd, app\,
lore-book\, and lore-pack\, creates this ZIP, writes a SHA-256 sidecar,
rejects Explorer-unsafe long ZIP entry paths, verifies the generated Lore pack
schema/hashes/content safety, rejects raw deep lore-book mirror leakage,
extracts the ZIP, launches the extracted app from app\, runs native launch
smoke, runs extracted app Home navigation smoke, runs extracted-package Lore
reader smoke, completes one generated-synthetic Safe Copy Manager workflow
with stale-input and source/output-alias negative controls, runs
representative Media smoke when a local game install is available, and
confirms no WinUI process remains. The probe also rejects raw publish layouts
that expose DLLs or executables at the ZIP root.

What this package shape does not prove
--------------------------------------

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Start menu shortcuts, uninstall entries, or installer UX.
- SmartScreen, Microsoft Store, reputation, or malware-scanner posture. The
  section above explains what the warning means and how to check the download;
  it does not make the warning go away, and nothing short of a signing
  certificate would.
- Legal/compliance approval for public binary redistribution.
- Row-by-row media playback coverage.
