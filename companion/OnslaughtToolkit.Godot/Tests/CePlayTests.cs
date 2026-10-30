// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Options;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// "Play this level with the mod": the temporary CE user folder (exclusive creation, marker, removal by path, the stale sweep), the changed copy of ce.ini, the
/// launcher's start (arguments, environment, the variables that switch mods off) and what the player's own CE folder and the game folder look like afterwards (the
/// same, byte for byte), then the Level editor's button on an authored level. No launcher or game runs: the start is a stand-in that looks at the folder CE would see.
/// </summary>
internal static partial class CePlayTests
{
    private const string RealIni = "# mine\ngamedir=/somewhere/else\nmods=other-mod\nrecord_sessions=1\nupdate_check=1\nwide_mode_w=1920\n";
    private const string FakeLog = "onslaught-ce: mods: 1 active, 1 game files replaced (experimental)\n" +
        "onslaught-ce: mods: active 1: play-level-100 \"Test play of level 100\" version 1, 1 files\n" +
        "onslaught-ce: mods: play-level-100 adds data/worlds/world100.wrd (4 bytes, sha256 9f64a747...)\n" +
        "onslaught-ce: session pid=1 t_ms=5 P=0 game: level=100\n" +
        "onslaught-ce: mods: play-level-100 serves data/worlds/world100.wrd to the game\n";

    [DllImport("libc", SetLastError = true)]
    private static extern int mkfifo([MarshalAs(UnmanagedType.LPUTF8Str)] string path, uint mode);

    [GeneratedRegex(@"\Aplay-20261030-050000-[0-9a-f]{8}\z")]
    private static partial Regex PlayName();

    private static UnixFileMode Mode(string path) => OperatingSystem.IsLinux() ? File.GetUnixFileMode(path) : default;

    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    internal static void Run(string output, Checks check)
    {
        check.Suite("test play: settings, versions and the temporary folder");
        string root = Path.Combine(output, "ce-play-unit");
        Directory.CreateDirectory(root);
        Settings(check);
        Versions(check);
        if (OperatingSystem.IsLinux()) Folders(Path.Combine(root, "folders"), check);
    }

    // ---- the changed copy of ce.ini ------------------------------------------------------------------------------------------------
    private static void Settings(Checks check)
    {
        static CeSettings Parse(string text) => CeSettings.Parse("/x/ce.ini", true, Encoding.UTF8.GetBytes(text)).Value!;
        static string Prepared(string text, params (string, string)[] changes) => Encoding.UTF8.GetString(Parse(text).PrepareValues(changes).Value!);
        (string, string)[] play = [("mods", "play-level-100"), ("record_sessions", "0"), ("update_check", "0")];

        check.That(Prepared("# mine\r\ngamedir=/a\r\nmods=old,older\r\nupdate_check=1\r\nrecord_sessions=1\r\nunknown=keep\r\n", play) ==
                   "# mine\r\ngamedir=/a\r\nmods=play-level-100\r\nupdate_check=0\r\nrecord_sessions=0\r\nunknown=keep\r\n",
            "the temporary ce.ini changes the three keys in place, keeps every other line (comments, unknown keys, CRLF) as it was, and has mods= name only the mod being tried");
        check.That(Prepared("mods=a\nmods=b\nrecord_sessions=1\nrecord_sessions=1\n", play) == "mods=play-level-100\nrecord_sessions=0\nupdate_check=0\n",
            "copies of a key collapse to one, so CE never reads an ambiguous mods= line");
        check.That(Prepared("gamedir=/a", play) == "gamedir=/a\nmods=play-level-100\nrecord_sessions=0\nupdate_check=0\n",
            "keys that are not there are appended after a last line without a newline");
        check.That(Prepared("mods_extra=1\nxmods=2\n# mods=3\n", play) == "mods_extra=1\nxmods=2\n# mods=3\nmods=play-level-100\nrecord_sessions=0\nupdate_check=0\n",
            "only the exact key is a key: longer names, prefixes and comments are kept");
        check.That(Encoding.UTF8.GetString(CeSettings.Parse("/x/ce.ini", false, []).Value!.PrepareValues(play).Value!) == "mods=play-level-100\nrecord_sessions=0\nupdate_check=0\n",
            "with no ce.ini of the player's, CE's defaults stand in and the file is the three lines");
        check.That(Encoding.UTF8.GetString(Parse("update_check=1\n").Prepare(false, true).Value!) == "update_check=0\nrecord_sessions=1\n",
            "the settings writer's own two-key preparation is unchanged by the general one");
    }

    private static void Versions(Checks check)
    {
        check.That(CeInstallation.IsAtLeast("0.1.12", "0.1.11") && CeInstallation.IsAtLeast("0.1.11", "0.1.11") && CeInstallation.IsAtLeast("0.2", "0.1.11") &&
                   CeInstallation.IsAtLeast("1.0.0.0", "0.1.11") && !CeInstallation.IsAtLeast("0.1.9", "0.1.11") && !CeInstallation.IsAtLeast("0.1.10.5", "0.1.11") &&
                   !CeInstallation.IsAtLeast("dev", "0.1.11") && !CeInstallation.IsAtLeast("0.1.12", "x") && !CeInstallation.IsAtLeast("", "0.1.11"),
            "versions compare as numbers (0.1.10 is before 0.1.11, 0.2 after), and what is not a number is never enough");
        check.That(CeInstallation.IsAtLeast("0.2.0-rc0", "0.1.11") && CeInstallation.IsAtLeast("v0.1.12", "0.1.11") && CeInstallation.IsAtLeast("V0.1.12", "0.1.11") && CeInstallation.IsAtLeast("0.1.12+build5", "0.1.11") &&
                   CeInstallation.IsAtLeast("0.1.11-rc1", "0.1.11") && !CeInstallation.IsAtLeast("0.1.10-rc9", "0.1.11") && !CeInstallation.IsAtLeast("v", "0.1.11") && !CeInstallation.IsAtLeast("-rc1", "0.1.11") &&
                   !CeInstallation.IsAtLeast("0.1.x-rc1", "0.1.11"), "a version with a label is compared by its numeric core, a leading v and a label after a hyphen or a plus set aside, so a release candidate of a later version is not refused");
    }

    // ---- the temporary folder -----------------------------------------------------------------------------------------------------
    private static string Listing(string root) => string.Join("|", Directory.EnumerateFileSystemEntries(root, "*", new EnumerationOptions { RecurseSubdirectories = true, AttributesToSkip = 0 })
        .Select(path => Path.GetRelativePath(root, path)).Order(StringComparer.Ordinal));

    [SupportedOSPlatform("linux")]
    private static void Folders(string root, Checks check)
    {
        Directory.CreateDirectory(root);
        string parent = Path.Combine(root, "play");
        DateTime now = new(2026, 10, 30, 5, 0, 0, DateTimeKind.Utc);
        var first = CePlayFolder.Create(parent, 100, "play-level-100", 4242, now);
        CePlayFolder folder = first.Value!;
        check.That(first.Ok && PlayName().IsMatch(Path.GetFileName(folder.Root)) && Path.GetDirectoryName(folder.Root) == parent && Directory.Exists(folder.Root),
            $"a folder is made in the play folder, named by time and a random word: {folder.Root}");
        check.That(Mode(parent) == (UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute) &&
                   Mode(folder.Root) == (UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute),
            "the play folder and the temporary folder are private to the player (mode 0700)");
        CePlayMarker? marker = CePlayFolder.ReadMarker(folder.Root);
        check.That(marker is { Format: CePlayFolder.MarkerFormat, CompanionPid: 4242, LauncherPid: 0, Level: 100, Mod: "play-level-100" } && marker.Folder == Path.GetFileName(folder.Root) &&
                   folder.Written.Count == 1 && Path.GetFileName(folder.Written[0]) == CePlayFolder.MarkerName,
            "the marker names the folder, the companion's process, the level and the mod, and is the only thing written so far");
        check.That(CePlayFolder.Create(parent, 100, "play-level-100", 4242, now).Value!.Root != folder.Root, "a second folder is a different one");

        // The name is taken exclusively: a name that exists is never reused, and what is in it is not touched.
        string taken = Path.Combine(parent, "play-20261030-050000-aaaaaaaa");
        Directory.CreateDirectory(taken);
        File.WriteAllText(Path.Combine(taken, "canary.txt"), "mine");
        int calls = 0;
        var other = CePlayFolder.Create(parent, 100, "play-level-100", 1, now, () => ++calls <= 2 ? "aaaaaaaa" : "bbbbbbbb");
        check.That(other.Ok && other.Value!.Root.EndsWith("bbbbbbbb", StringComparison.Ordinal) && File.ReadAllText(Path.Combine(taken, "canary.txt")) == "mine" &&
                   Listing(taken) == "canary.txt", "a folder name that already exists is skipped, and the folder that has it is left as it was");
        var never = CePlayFolder.Create(parent, 100, "play-level-100", 1, now, () => "aaaaaaaa");
        check.That(!never.Ok && Listing(taken) == "canary.txt", $"with no free name nothing is made and nothing existing is touched: \"{never.Message}\"");

        // Refusals: nothing is made.
        string link = Path.Combine(root, "link"), realPlace = Path.Combine(root, "real-place");
        Directory.CreateDirectory(realPlace);
        Directory.CreateSymbolicLink(link, realPlace);
        File.WriteAllText(Path.Combine(root, "a-file"), "x");
        Directory.CreateDirectory(Path.Combine(realPlace, "sub"));
        check.That(!CePlayFolder.Create("relative/play", 100, "m", 1, now).Ok && !CePlayFolder.Create(Path.Combine(root, "a-file"), 100, "m", 1, now).Ok &&
                   !CePlayFolder.Create(link, 100, "m", 1, now).Ok && !CePlayFolder.Create(Path.Combine(link, "play"), 100, "m", 1, now).Ok &&
                   !CePlayFolder.Create(Path.Combine(link, "sub", "play"), 100, "m", 1, now).Ok && Listing(realPlace) == "sub",
            "a play folder that is not a full path, is a file, is a link or lies behind one (however deep) is refused, and nothing is written through the link");

        // A refusal names what is wrong: the link on the way, the file in the way; the settings folder the companion owns is made when it is missing.
        Directory.CreateDirectory(Path.Combine(realPlace, "named"));
        var behindLink = CePlayFolder.Create(Path.Combine(link, "named", "play"), 100, "m", 1, now);
        var behindFile = CePlayFolder.Create(Path.Combine(root, "a-file", "inner", "play"), 100, "m", 1, now);
        check.That(!behindLink.Ok && behindLink.Message.Contains(link, StringComparison.Ordinal) && behindLink.Message.Contains("is a link", StringComparison.Ordinal) &&
                   !behindFile.Ok && behindFile.Message.Contains("a-file", StringComparison.Ordinal) && Listing(realPlace) == "named|sub",
            $"a refusal names the link on the way and the file in the way, and nothing is written behind them: \"{behindLink.Message}\" / \"{behindFile.Message}\"");
        var madeDeep = CePlayFolder.Create(Path.Combine(root, "new-data", "settings", "play"), 100, "m", 1, now);
        check.That(madeDeep.Ok && Directory.Exists(Path.Combine(root, "new-data", "settings", "play")) &&
                   Mode(Path.Combine(root, "new-data", "settings")) == (UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute),
            "a play folder whose settings folder is not there yet is made with the missing folders above it, private");
        // The play folder must be the player's own and not writable by others: it holds copies of their settings.
        string openPlay = Path.Combine(root, "open-play");
        Directory.CreateDirectory(openPlay);
        File.SetUnixFileMode(openPlay, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute | UnixFileMode.GroupWrite | UnixFileMode.OtherWrite);
        var writable = CePlayFolder.Create(openPlay, 100, "m", 1, now);
        string afterRefusal = Listing(openPlay);
        File.SetUnixFileMode(openPlay, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute | UnixFileMode.GroupRead | UnixFileMode.GroupExecute | UnixFileMode.OtherRead | UnixFileMode.OtherExecute);
        var readable = CePlayFolder.Create(openPlay, 100, "m", 1, now);
        check.That(!writable.Ok && writable.Message.Contains("can be written by other people", StringComparison.Ordinal) && afterRefusal == "" && readable.Ok,
            $"a play folder that others can write is refused before anything is made, and one they can only read is fine: \"{writable.Message}\"");

        // Files go in new, once, inside the folder.
        folder.WriteFile("ce.ini", Encoding.UTF8.GetBytes("mods=x\n"));
        folder.WriteFile("mods/m/data/worlds/world100.wrd", [1, 2, 3, 4]);
        bool again = false, outside = false, rooted = false;
        try { folder.WriteFile("ce.ini", [0]); } catch (IOException) { again = true; }
        try { folder.WriteFile("../escape.txt", [0]); } catch (ArgumentException) { outside = true; }
        try { folder.WriteFile("/tmp/escape.txt", [0]); } catch (ArgumentException) { rooted = true; }
        check.That(again && outside && rooted && File.ReadAllText(Path.Combine(folder.Root, "ce.ini")) == "mods=x\n" && !File.Exists(Path.Combine(root, "escape.txt")) &&
                   Mode(Path.Combine(folder.Root, "ce.ini")) == (UnixFileMode.UserRead | UnixFileMode.UserWrite) &&
                   folder.Written.Count == 3 && folder.Made.Count == 5, "a file is written once, privately, inside the folder; a file that exists, a path that leaves the folder and a rooted path are refused");

        // Copies of the player's files: a regular file, never a link, never one that is too large.
        string source = Path.Combine(root, "source"), canary = Path.Combine(root, "canary.bin");
        Directory.CreateDirectory(source);
        File.WriteAllBytes(Path.Combine(source, "options.bea"), [9, 9, 9]);
        File.WriteAllBytes(canary, [7]);
        Directory.CreateSymbolicLink(Path.Combine(source, "linked.bea"), canary);
        File.WriteAllBytes(Path.Combine(source, "big.bea"), new byte[64]);
        check.That(folder.CopyRegular(Path.Combine(source, "options.bea"), "options.bea", 1024) is null && File.ReadAllBytes(Path.Combine(folder.Root, "options.bea")).SequenceEqual(new byte[] { 9, 9, 9 }) &&
                   folder.CopyRegular(Path.Combine(source, "absent.bea"), "absent.bea", 1024) is null && !File.Exists(Path.Combine(folder.Root, "absent.bea")) &&
                   folder.CopyRegular(Path.Combine(source, "linked.bea"), "linked.bea", 1024) is string notPlain && notPlain.Contains("not a plain file", StringComparison.Ordinal) && !File.Exists(Path.Combine(folder.Root, "linked.bea")) &&
                   folder.CopyRegular(Path.Combine(source, "big.bea"), "big.bea", 16) is string tooBig && tooBig.Contains("larger", StringComparison.Ordinal) && !File.Exists(Path.Combine(folder.Root, "big.bea")),
            "a plain file is copied, a missing one is nothing to say, a link and a file over the limit are not copied and the player is told");

        // The marker rewrite that records the launcher: atomic, and the file is still the folder's own.
        folder.RecordLauncher(31337);
        check.That(CePlayFolder.ReadMarker(folder.Root) is { LauncherPid: 31337, CompanionPid: 4242 } && !File.Exists(Path.Combine(folder.Root, CePlayFolder.MarkerName + ".new")),
            "recording the launcher's process id rewrites the marker whole and leaves no temporary file");

        // What CE writes into its user folder (a log, screenshots, a dot file) is removed with the rest; the player's own files are somewhere else.
        File.WriteAllText(Path.Combine(folder.Root, "onslaught-ce.log"), "log");
        Directory.CreateDirectory(Path.Combine(folder.Root, "screenshots"));
        File.WriteAllBytes(Path.Combine(folder.Root, "screenshots", "a.png"), [1]);
        File.WriteAllText(Path.Combine(folder.Root, ".hidden"), "dot");
        string untouched = Listing(taken);
        CePlayRemoval gone = folder.Remove();
        check.That(gone.Removed && gone.Left.Count == 0 && !Directory.Exists(folder.Root) && Directory.Exists(parent) && Listing(taken) == untouched && File.Exists(canary) && File.Exists(Path.Combine(source, "options.bea")),
            "removing a play folder removes it whole, dot files included, and nothing beside it");

        // A link or a special file inside is never followed or deleted: it stays, with the folders above it, and is reported.
        var risky = CePlayFolder.Create(parent, 100, "play-level-100", 4242, now).Value!;
        risky.WriteFile("ce.ini", [49]);
        Directory.CreateDirectory(Path.Combine(risky.Root, "inner"));
        File.WriteAllText(Path.Combine(risky.Root, "inner", "plain.txt"), "p");
        File.CreateSymbolicLink(Path.Combine(risky.Root, "inner", "escape"), source);
        check.That(mkfifo(Path.Combine(risky.Root, "pipe"), 0x1A4) == 0, "a named pipe could be made for the test");
        CePlayRemoval stuck = risky.Remove();
        check.That(!stuck.Removed && stuck.Left.Count == 2 && stuck.Left.Any(path => path.EndsWith("escape", StringComparison.Ordinal)) && stuck.Left.Any(path => path.EndsWith("pipe", StringComparison.Ordinal)) &&
                   File.Exists(Path.Combine(source, "options.bea")) && Directory.Exists(Path.Combine(risky.Root, "inner")) && !File.Exists(Path.Combine(risky.Root, "inner", "plain.txt")) &&
                   !File.Exists(Path.Combine(risky.Root, "ce.ini")) && stuck.Message.Contains("left in place", StringComparison.Ordinal),
            $"a link and a pipe inside stay, the target of the link is untouched, the plain files are gone and the player is told: \"{stuck.Message}\"");

        // The removal works by name in open folders, so a folder swapped for a link at the worst moment (after its kind was read, before it is opened) is not followed, and a file
        // swapped for a link loses the link only.
        string raceTarget = Path.Combine(root, "race-target"), precious = Path.Combine(raceTarget, "precious.txt");
        Directory.CreateDirectory(raceTarget);
        File.WriteAllText(precious, "precious");
        CePlayFolder racy = CePlayFolder.Create(parent, 100, "play-level-100", 4242, now).Value!;
        Directory.CreateDirectory(Path.Combine(racy.Root, "inner"));
        File.WriteAllText(Path.Combine(racy.Root, "inner", "x.txt"), "x");
        File.WriteAllText(Path.Combine(racy.Root, "a.txt"), "a");
        CePlayFolder.AfterKind = shown =>
        {
            if (shown.EndsWith("inner", StringComparison.Ordinal))
            {
                Directory.Delete(Path.Combine(racy.Root, "inner"), recursive: true);
                File.CreateSymbolicLink(Path.Combine(racy.Root, "inner"), raceTarget);
            }
            else if (shown.EndsWith("a.txt", StringComparison.Ordinal))
            {
                File.Delete(Path.Combine(racy.Root, "a.txt"));
                File.CreateSymbolicLink(Path.Combine(racy.Root, "a.txt"), precious);
            }
        };
        CePlayRemoval raced;
        try { raced = racy.Remove(); } finally { CePlayFolder.AfterKind = null; }
        check.That(!raced.Removed && raced.Left.Count == 1 && raced.Left[0].EndsWith("inner", StringComparison.Ordinal) && File.ReadAllText(precious) == "precious" && Listing(raceTarget) == "precious.txt" &&
                   File.GetAttributes(Path.Combine(racy.Root, "inner")).HasFlag(FileAttributes.ReparsePoint) && !File.Exists(Path.Combine(racy.Root, "a.txt")) && File.Exists(Path.Combine(racy.Root, CePlayFolder.MarkerName)),
            $"a folder swapped for a link after its kind was read is not followed (the link stays, the target's file is untouched), a file swapped for a link loses the link only, and the marker stays with the folder: {raced.Message}");

        RemovalHolderSwapped(Path.Combine(root, "removal-holder"), check);
        RemovalPlayFolderLink(Path.Combine(root, "removal-play-link"), check);
        RemovalPlayFolderSwappedLate(Path.Combine(root, "removal-play-late"), check);
        RemovalTemporaryFolderLink(Path.Combine(root, "removal-temporary-link"), check);

        // A blocker deep inside keeps the marker too, so the folder is still known as ours; and a folder whose marker was taken away or replaced (by another folder's) is refused whole.
        CePlayFolder deep = CePlayFolder.Create(parent, 100, "play-level-100", 4242, now).Value!;
        Directory.CreateDirectory(Path.Combine(deep.Root, "inner"));
        File.CreateSymbolicLink(Path.Combine(deep.Root, "inner", "escape"), source);
        File.WriteAllText(Path.Combine(deep.Root, "plain.txt"), "p");
        CePlayRemoval deepStuck = deep.Remove();
        check.That(!deepStuck.Removed && deepStuck.Left.Count == 1 && deepStuck.Left[0].EndsWith("escape", StringComparison.Ordinal) && File.Exists(Path.Combine(deep.Root, CePlayFolder.MarkerName)) &&
                   !File.Exists(Path.Combine(deep.Root, "plain.txt")) && CePlayFolder.ReadMarker(deep.Root) is not null,
            $"a link deep inside keeps the marker (the folder is still ours for the next sweep) and is the only thing left: {deepStuck.Message}");
        CePlayFolder tampered = CePlayFolder.Create(parent, 100, "play-level-100", 4242, now).Value!;
        tampered.WriteFile("keep.txt", [1]);
        string tamperedMarker = Path.Combine(tampered.Root, CePlayFolder.MarkerName);
        byte[] ownMarker = File.ReadAllBytes(tamperedMarker);
        File.Delete(tamperedMarker);
        CePlayRemoval noMarker = tampered.Remove();
        File.WriteAllBytes(tamperedMarker, File.ReadAllBytes(Path.Combine(deep.Root, CePlayFolder.MarkerName)));
        CePlayRemoval otherMarker = tampered.Remove();
        File.WriteAllBytes(tamperedMarker, ownMarker);
        check.That(!noMarker.Removed && !otherMarker.Removed && noMarker.Message.Contains("marker", StringComparison.Ordinal) && otherMarker.Message.Contains("marker", StringComparison.Ordinal) &&
                   File.Exists(Path.Combine(tampered.Root, "keep.txt")), "a folder whose marker is gone, or names another folder, is not removed, and what is in it stays");

        // A folder that is not ours is refused whole: no marker, a marker for another name, a link in its place, not a child of the play folder.
        string bare = Path.Combine(parent, "play-bare");
        Directory.CreateDirectory(bare);
        File.WriteAllText(Path.Combine(bare, "keep.txt"), "k");
        string wrongName = Path.Combine(parent, "play-wrong-name");
        Directory.CreateDirectory(wrongName);
        File.WriteAllBytes(Path.Combine(wrongName, CePlayFolder.MarkerName), File.ReadAllBytes(Path.Combine(risky.Root, CePlayFolder.MarkerName)));
        string oddMarker = Path.Combine(parent, "play-odd-marker");
        Directory.CreateDirectory(oddMarker);
        File.WriteAllText(Path.Combine(oddMarker, CePlayFolder.MarkerName), "{\"Format\":\"something-else\",\"Folder\":\"play-odd-marker\"}");
        string bigMarker = Path.Combine(parent, "play-big-marker");
        Directory.CreateDirectory(bigMarker);
        File.WriteAllText(Path.Combine(bigMarker, CePlayFolder.MarkerName), "{\"Format\":\"" + CePlayFolder.MarkerFormat + "\",\"Folder\":\"play-big-marker\",\"CompanionPid\":1}" + new string(' ', 8192));
        check.That(CePlayFolder.ReadMarker(bare) is null && CePlayFolder.ReadMarker(wrongName) is null && CePlayFolder.ReadMarker(oddMarker) is null && CePlayFolder.ReadMarker(bigMarker) is null,
            "a folder without a marker, with a marker for another folder, of another format or too large has no marker of ours");

        // The stale sweep: only real folders with a marker naming themselves, whose companion and CE are not running, and not the one in use.
        string sweepParent = Path.Combine(root, "sweep");
        CePlayFolder Stale(int companion, int launcher, string? name = null)
        {
            CePlayFolder made = CePlayFolder.Create(sweepParent, 100, "play-level-100", companion, now, name is null ? null : () => name).Value!;
            made.WriteFile("ce.ini", [1]);
            if (launcher != 0) made.RecordLauncher(launcher);
            File.WriteAllText(Path.Combine(made.Root, "onslaught-ce.log"), "log");
            return made;
        }
        CePlayFolder dead = Stale(1001, 0, "00000001"), companionAlive = Stale(2002, 0, "00000002"), ceAlive = Stale(1003, 3003, "00000003"), mine = Stale(555, 0, "00000004"), current = Stale(1005, 0, "00000005");
        CePlayFolder deadWithLauncher = Stale(1006, 3006, "00000006");
        Directory.CreateDirectory(Path.Combine(sweepParent, "play-no-marker"));
        File.WriteAllText(Path.Combine(sweepParent, "play-no-marker", "x.txt"), "x");
        File.WriteAllText(Path.Combine(sweepParent, "notes.txt"), "n");
        Directory.CreateDirectory(Path.Combine(sweepParent, "other-folder"));
        File.WriteAllText(Path.Combine(sweepParent, "last-session.log"), "log");
        Directory.CreateSymbolicLink(Path.Combine(sweepParent, "play-link"), companionAlive.Root);
        string deadRoot = dead.Root, deadLauncherRoot = deadWithLauncher.Root;
        CePlaySweep swept = CePlayFolder.SweepStale(sweepParent, 555, current.Root, pid => pid is 2002 or 3003);
        check.That(swept.Removed.Count == 2 && !Directory.Exists(deadRoot) && !Directory.Exists(deadLauncherRoot) && Directory.Exists(companionAlive.Root) && Directory.Exists(ceAlive.Root) &&
                   Directory.Exists(mine.Root) && Directory.Exists(current.Root) && Directory.Exists(Path.Combine(sweepParent, "play-no-marker")) && File.Exists(Path.Combine(sweepParent, "play-no-marker", "x.txt")) &&
                   File.Exists(Path.Combine(sweepParent, "notes.txt")) && Directory.Exists(Path.Combine(sweepParent, "other-folder")) && File.Exists(Path.Combine(sweepParent, "last-session.log")) &&
                   Directory.Exists(companionAlive.Root) && File.Exists(Path.Combine(companionAlive.Root, "ce.ini")),
            $"the sweep removes the folders whose companion and CE have gone and leaves the live, the current, its own, the markerless, the link, and everything else in the play folder: removed {string.Join(", ", swept.Removed)}; kept {string.Join("; ", swept.Kept)}");
        check.That(swept.Kept.Any(line => line.Contains("its companion is still running", StringComparison.Ordinal)) && swept.Kept.Any(line => line.Contains("CE is still running", StringComparison.Ordinal)) &&
                   swept.Kept.Any(line => line.Contains("no marker of ours", StringComparison.Ordinal)) && swept.Kept.Any(line => line.Contains("made by this companion", StringComparison.Ordinal)) &&
                   swept.Kept.Any(line => line.Contains("in use by this companion", StringComparison.Ordinal)), "the sweep says why it kept each one");
        check.That(CePlayFolder.SweepStale(Path.Combine(root, "absent"), 1, null, _ => false) is { Removed.Count: 0, Kept.Count: 0 } &&
                   CePlayFolder.SweepStale("relative", 1, null, _ => false) is { Removed.Count: 0 }, "a play folder that is not there, or not a full path, is nothing to sweep");

        // An empty play folder with no marker (its marker went before a failing last removal) is removed once it is not new; one that holds anything, a dot file included, or is new, stays.
        string emptyParent = Path.Combine(root, "sweep-empty");
        Directory.CreateDirectory(emptyParent);
        File.SetUnixFileMode(emptyParent, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
        string emptyOne = Path.Combine(emptyParent, "play-empty"), holdsDot = Path.Combine(emptyParent, "play-holds-dot"), holdsFolder = Path.Combine(emptyParent, "play-holds-folder");
        Directory.CreateDirectory(emptyOne);
        Directory.CreateDirectory(holdsDot);
        File.WriteAllText(Path.Combine(holdsDot, ".hidden"), "x");
        Directory.CreateDirectory(Path.Combine(holdsFolder, "inner"));
        CePlaySweep fresh = CePlayFolder.SweepStale(emptyParent, 1, null, _ => false);
        bool freshStays = fresh.Removed.Count == 0 && Directory.Exists(emptyOne) && Directory.Exists(holdsDot) && Directory.Exists(holdsFolder);
        CePlaySweep aged = CePlayFolder.SweepStale(emptyParent, 1, null, _ => false, TimeSpan.Zero);
        check.That(freshStays && aged.Removed.SequenceEqual(["play-empty (empty, no marker)"]) && !Directory.Exists(emptyOne) &&
                   File.Exists(Path.Combine(holdsDot, ".hidden")) && Directory.Exists(Path.Combine(holdsFolder, "inner")) && aged.Kept.Count == 2,
            $"an empty marker-less play folder that is not new is removed, a new one and any that holds something stay (fresh sweep kept all: {freshStays}): removed {string.Join(", ", aged.Removed)}; kept {string.Join(", ", aged.Kept)}");

        // A folder that is a link to a real play folder is neither followed nor removed.
        string target = Path.Combine(root, "elsewhere");
        Directory.CreateDirectory(target);
        CePlayFolder inElsewhere = CePlayFolder.Create(target, 100, "play-level-100", 9, now).Value!;
        string linkParent = Path.Combine(root, "link-parent");
        Directory.CreateDirectory(linkParent);
        string linked = Path.Combine(linkParent, Path.GetFileName(inElsewhere.Root));
        Directory.CreateSymbolicLink(linked, inElsewhere.Root);
        CePlaySweep viaLink = CePlayFolder.SweepStale(linkParent, 1, null, _ => false);
        check.That(viaLink.Removed.Count == 0 && Directory.Exists(inElsewhere.Root) && File.Exists(Path.Combine(inElsewhere.Root, CePlayFolder.MarkerName)),
            "a link that is named like a play folder is not followed, and the folder it points at is not removed");
    }

    // ---- the service -----------------------------------------------------------------------------------------------------------------
    private sealed record Seen(List<string> Arguments, Dictionary<string, string?> Environment, string Listing, string Ini, string? OptionsHash, string FileName, string WorkingDirectory, byte[]? World, CePlayMarker? Marker);

    private sealed class Rig
    {
        internal required FakeInstall Install { get; init; }
        internal required string User { get; init; }
        internal required string Package { get; init; }
        internal required string Parent { get; init; }
        internal required GameLibrary Game { get; init; }
        internal required CePlay Play { get; init; }
        internal Seen? Seen { get; set; }
        internal int Runs { get; set; }
        internal int ExitCode { get; set; }
        internal string? LogText { get; set; } = FakeLog;
        internal Action<ProcessStartInfo>? Mischief { get; set; }
        internal int Changes { get; set; }
        internal Func<ProcessStartInfo, Task>? Wait { get; set; }
        internal List<string> Started { get; } = [];
        internal int VersionAsked { get; set; }
    }

    private static async Task<Rig> MakeRigAsync(string root, byte[] career, string packageVersion = "0.1.12", string answer = "Onslaught CE V0.1.12, build abcdef123456", string ini = RealIni,
        Func<bool>? windows = null, bool withPackage = true, string? parentUnder = null, bool executableLauncher = false, IReadOnlyDictionary<string, string?>? environment = null)
    {
        Directory.CreateDirectory(root);
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "install"), career);
        string user = Path.Combine(root, "ce-user");
        Directory.CreateDirectory(Path.Combine(user, "savegames"));
        Directory.CreateDirectory(Path.Combine(user, "tapes"));
        File.WriteAllBytes(Path.Combine(user, "savegames", "CE Pilot.bes"), career);
        File.WriteAllText(Path.Combine(user, "ce.ini"), ini);
        File.WriteAllBytes(Path.Combine(user, "defaultoptions.bea"), career);
        File.WriteAllText(Path.Combine(user, "tapes", "old.tape"), "tape");
        string package = Path.Combine(root, "package");
        Directory.CreateDirectory(package);
        File.WriteAllText(Path.Combine(package, "onslaught-ce"), executableLauncher ? $"#!/bin/sh\necho \"{answer}\"\n" : "test-only launcher marker; never run");   // the one that runs answers --version, nothing more
        if (executableLauncher && OperatingSystem.IsLinux()) File.SetUnixFileMode(Path.Combine(package, "onslaught-ce"), UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
        File.WriteAllText(Path.Combine(package, OnslaughtCe.LinuxLauncher), "test-only launcher marker; never run");
        File.WriteAllText(Path.Combine(package, "bea"), "test-only game marker");
        File.WriteAllText(Path.Combine(package, "README.txt"), $"Onslaught CE V{packageVersion}\n\nQuick start\n");
        SettingsStore store = new(Path.Combine(root, "settings.json"));
        store.Save(new CompanionSettings { GameFolder = install.Game, Target = GameTarget.Original, AutoBackup = false });
        GameLibrary game = new([install.SteamRoot], store, user, name => name == "PATH" && withPackage ? package : null);
        await game.DetectAsync();
        string parent = Path.Combine(parentUnder ?? root, "play");
        Rig? rig = null;
        CePlayHooks hooks = new(Parent: parent, ReadVersion: (_, _) => { rig!.VersionAsked++; return Task.FromResult(answer); }, Environment: environment, OnWindows: windows, Now: () => new DateTime(2026, 10, 30, 5, 0, 0, DateTimeKind.Utc),
            OnStart: start => rig!.Started.Add(string.Join(" ", start.ArgumentList)),
            Run: async start =>
            {
                Rig self = rig!;
                self.Runs++;
                string folder = start.Environment["BEA_USER_DIR"]!;
                string world = Path.Combine(folder, "mods", "play-level-100", "data", "worlds", "world100.wrd");
                self.Seen = new Seen([.. start.ArgumentList], start.Environment.ToDictionary(pair => pair.Key, pair => pair.Value), Listing(folder),
                    File.Exists(Path.Combine(folder, "ce.ini")) ? File.ReadAllText(Path.Combine(folder, "ce.ini")) : "",
                    File.Exists(Path.Combine(folder, "defaultoptions.bea")) ? Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(Path.Combine(folder, "defaultoptions.bea")))) : null,
                    start.FileName, start.WorkingDirectory, File.Exists(world) ? File.ReadAllBytes(world) : null, CePlayFolder.ReadMarker(folder));
                if (self.LogText is { } text) File.WriteAllText(Path.Combine(folder, "onslaught-ce.log"), text);
                Directory.CreateDirectory(Path.Combine(folder, "screenshots"));
                File.WriteAllBytes(Path.Combine(folder, "screenshots", "a.png"), [1]);
                File.WriteAllText(Path.Combine(folder, "setuphistory.txt"), "s");
                self.Mischief?.Invoke(start);
                if (self.Wait is { } wait) await wait(start);
                return self.ExitCode;
            });
        CePlay play = new(game, Path.Combine(root, "unused-default"), hooks);
        rig = new Rig { Install = install, User = user, Package = package, Parent = parent, Game = game, Play = play };
        return rig;
    }

    private static SaveOutcome Stage(string parent, ModInfo info)
    {
        try
        {
            return new SaveOutcome(ModStager.Stage(parent, info, new Dictionary<int, byte[]> { [100] = [1, 2, 3, 4] }, []), "ok");
        }
        catch (ModStageException error)
        {
            return new SaveOutcome(null, error.Message);
        }
    }

    /// <summary>Port knobs the fence list does not name (and no port reads today): a test play scrubs them all the same.</summary>
    private static readonly string[] LeakedKnobs = ["BEA_PORT_UNLISTED_KNOB", "BEA_NET_UNLISTED_KNOB", "BEA_PORT_QUIT"];

    private static string[] PlayFolders(string parent) => Directory.Exists(parent) ? [.. Directory.GetDirectories(parent, "play-*").Order(StringComparer.Ordinal)] : [];

    internal static async Task RunAsync(SceneTree tree, byte[] original, string output, Checks check)
    {
        check.Suite("test play of a level");
        if (!OperatingSystem.IsLinux()) return;
        string root = Path.Combine(output, "ce-play-service");
        Directory.CreateDirectory(root);

        // ---- the whole play, from a player's CE folder that holds a career, options, tapes and a ce.ini with other ideas ---------------------------------
        foreach (string name in CePlay.FenceVariables.Concat(LeakedKnobs)) System.Environment.SetEnvironmentVariable(name, "leaked");
        System.Environment.SetEnvironmentVariable("BEA_REPORT_NO_OPEN", "1");
        System.Environment.SetEnvironmentVariable("BEA_USER_DIR", "/should/not/be/used");
        System.Environment.SetEnvironmentVariable("BEA_GAME_DIR", "/should/not/be/used/either");
        try
        {
            Rig rig = await MakeRigAsync(Path.Combine(root, "main"), original, environment: new Dictionary<string, string?> { ["BEA_PORT_QUIT"] = "9" });
            string[] userBefore = LevelEditorPageTests.Snapshot(rig.User), gameBefore = LevelEditorPageTests.Snapshot(rig.Install.Game), packageBefore = LevelEditorPageTests.Snapshot(rig.Package);
            string userTreeBefore = Listing(rig.User);
            int changes = 0;
            rig.Play.Changed += () => changes++;
            check.That(rig.Game.Ce is not null && rig.Game.Folder is not null && rig.Play.Unavailable() is null && !rig.Play.Running, "with a CE launcher, a game folder and a user folder, a test play is available");
            CePlayReport report = await rig.Play.PlayAsync(100, Stage);
            Seen seen = rig.Seen!;
            check.That(rig.Runs == 1 && report.Started && report.ExitCode == 0 && report.ModServed && report.Left.Count == 0, $"the play ran once, CE exited cleanly and its log says it served the mod: {report.Message}");
            check.That(seen.Arguments.SequenceEqual(["--no-update-check", "-level", "100", "-skipfmv", "-forcewindowed"]) && seen.FileName == Path.Combine(rig.Package, "onslaught-ce") &&
                       seen.WorkingDirectory == rig.Package, $"the launcher is started from its package folder with CE's own switch first and the level after: {string.Join(" ", seen.Arguments)}");
            string playFolder = seen.Environment["BEA_USER_DIR"]!;
            check.That(Path.GetDirectoryName(playFolder) == rig.Parent && Path.GetFileName(playFolder).StartsWith("play-", StringComparison.Ordinal) && playFolder != rig.User &&
                       seen.Environment["BEA_GAME_DIR"] == rig.Install.Game && CePlay.FenceVariables.All(name => !seen.Environment.ContainsKey(name)),
                $"CE is told a temporary folder of its own, never the player's, and the game folder the editor read; none of the variables that switch mods off reaches it: {playFolder}");
            check.That(LeakedKnobs.Except(["BEA_PORT_QUIT"]).All(name => !seen.Environment.ContainsKey(name)) && seen.Environment.Keys.Where(name => name.StartsWith("BEA_PORT_", StringComparison.Ordinal) || name.StartsWith("BEA_NET_", StringComparison.Ordinal)).SequenceEqual(["BEA_PORT_QUIT"]) &&
                       seen.Environment["BEA_PORT_QUIT"] == "9" && seen.Environment["BEA_REPORT_NO_OPEN"] == "1",
                "every other BEA_PORT_* and BEA_NET_* is scrubbed too, whether or not the list names it; what the play hooks add after that reaches CE, and other BEA_ variables stay");
            check.That(seen.Ini == "# mine\ngamedir=/somewhere/else\nmods=play-level-100\nrecord_sessions=0\nupdate_check=0\nwide_mode_w=1920\n",
                $"CE's ce.ini there is the player's with mods= naming the mod alone, recording off and no update check: \"{seen.Ini.Replace("\n", "|")}\"");
            check.That(seen.OptionsHash == Convert.ToHexStringLower(SHA256.HashData(original)) &&
                       seen.Listing == ".onslaught-toolkit-ce-play|ce.ini|defaultoptions.bea|mods|mods/play-level-100|mods/play-level-100/data|mods/play-level-100/data/worlds|mods/play-level-100/data/worlds/world100.wrd|mods/play-level-100/mod.json",
                $"the folder holds the marker, the ce.ini, the options and the mod, and no career or tape: {seen.Listing}");
            check.That(seen.World is { Length: 4 } && seen.Marker is { Level: 100, Mod: "play-level-100", CompanionPid: > 0 }, "the mod is the edit as staged, and the marker names the level, the mod and the companion's process");
            check.That(PlayFolders(rig.Parent).Length == 0 && report.LogCopy == rig.Play.LastLog && File.ReadAllText(rig.Play.LastLog) == FakeLog &&
                       report.ModLines.Count == 4 && report.ModLines[0].Contains("1 active", StringComparison.Ordinal),
                "when CE closed, the temporary folder was removed, CE's log was kept beside it and the lines about mods were read from it");
            check.That(LevelEditorPageTests.Snapshot(rig.User).SequenceEqual(userBefore) && Listing(rig.User) == userTreeBefore && LevelEditorPageTests.Snapshot(rig.Install.Game).SequenceEqual(gameBefore) &&
                       LevelEditorPageTests.Snapshot(rig.Package).SequenceEqual(packageBefore) && File.ReadAllText(Path.Combine(rig.User, "ce.ini")) == RealIni,
                "the player's CE folder (ce.ini, options, careers, tapes), the game folder and the CE package are byte for byte as they were");
            check.That(changes == 2 && !rig.Play.Running && report.Message.StartsWith("Onslaught CE ran level 100 and closed. Its log says it loaded the mod's world file.", StringComparison.Ordinal) && !report.Message.Contains("with your changes", StringComparison.Ordinal),
                $"the page is told when a play starts and ends: {report.Message}");
            check.That(ReferenceEquals(rig.Play.Last, report) && rig.Started.Count == 1 && rig.Started[0] == "--no-update-check -level 100 -skipfmv -forcewindowed",
                "the service keeps the report of the latest play, and a start hook sees the arguments just before the launcher runs");

            // A second call while one runs is refused and starts nothing.
            TaskCompletionSource release = new();
            rig.Wait = _ => release.Task;
            Task<CePlayReport> running = rig.Play.PlayAsync(100, Stage);
            check.That(rig.Play.Running && rig.Play.Unavailable() is string busy && busy.Contains("already", StringComparison.Ordinal), "while CE runs, a test play says another is running");
            CePlayReport second = await rig.Play.PlayAsync(100, Stage);
            check.That(!second.Started && rig.Runs == 2 && PlayFolders(rig.Parent).Length == 1, "a second play while one runs starts nothing and makes no folder");
            release.SetResult();
            CePlayReport finished = await running;
            rig.Wait = null;
            check.That(finished.Started && PlayFolders(rig.Parent).Length == 0 && !rig.Play.Running, "the first one finishes and cleans up");

            // CE's own non-zero exit and a log without the mod's line are reported, not hidden.
            rig.ExitCode = 3;
            rig.LogText = "onslaught-ce: mods: 1 active, 1 game files replaced (experimental)\nonslaught-ce: mods: play-level-100 adds data/worlds/world100.wrd (4 bytes)\n";
            CePlayReport odd = await rig.Play.PlayAsync(100, Stage);
            check.That(odd.Started && odd.ExitCode == 3 && !odd.ModServed && odd.Message.Contains("exit code 3", StringComparison.Ordinal) && odd.Message.Contains("does not say it loaded", StringComparison.Ordinal) &&
                       PlayFolders(rig.Parent).Length == 0, $"a non-zero exit and a log that never says the mod was served are said plainly: {odd.Message}");
            rig.ExitCode = 0;
            rig.LogText = null;
            CePlayReport silent = await rig.Play.PlayAsync(100, Stage);
            check.That(silent.Started && !silent.ModServed && silent.LogCopy is null && silent.Message.Contains("wrote no log", StringComparison.Ordinal), $"a CE that wrote no log is said to have written none: {silent.Message}");
            rig.LogText = "onslaught-ce: nothing about mods here\n";
            CePlayReport quiet = await rig.Play.PlayAsync(100, Stage);
            check.That(quiet.Started && quiet.ExitCode == 0 && !quiet.ModServed && quiet.Message.StartsWith("Onslaught CE ran level 100 and closed. Its log does not say it loaded the mod's world file", StringComparison.Ordinal) &&
                       !quiet.Message.Contains("with your changes", StringComparison.Ordinal) && !silent.Message.Contains("with your changes", StringComparison.Ordinal),
                $"a clean exit never claims the changes were played unless the log says the mod was served: {quiet.Message}");
            rig.LogText = FakeLog;

            // The kept log is made as a new file and then renamed over the old one: a link planted at the working name is never written through (not a dangling one, not one to a file), and a stale file there is replaced.
            string outsideLog = Path.Combine(root, "main", "outside-log.txt"), createdThrough = Path.Combine(root, "main", "created-through-link.txt");
            File.WriteAllText(outsideLog, "outside");
            string working = rig.Play.LastLog + ".new";
            File.CreateSymbolicLink(working, createdThrough);
            CePlayReport danglingPlanted = await rig.Play.PlayAsync(100, Stage);
            check.That(danglingPlanted.LogCopy == rig.Play.LastLog && !File.Exists(createdThrough) && File.ReadAllText(rig.Play.LastLog) == FakeLog && !File.Exists(working) && new FileInfo(working).LinkTarget is null,
                "a dangling link planted at the log's working name is not written through, and the log is kept");
            File.CreateSymbolicLink(working, outsideLog);
            CePlayReport filePlanted = await rig.Play.PlayAsync(100, Stage);
            check.That(filePlanted.LogCopy == rig.Play.LastLog && File.ReadAllText(outsideLog) == "outside" && File.ReadAllText(rig.Play.LastLog) == FakeLog && !File.Exists(working) &&
                       Mode(rig.Play.LastLog) == (UnixFileMode.UserRead | UnixFileMode.UserWrite), "a link to a file planted at the working name leaves that file as it was, and the kept log is private to the player");
            File.WriteAllText(working, "stale");
            CePlayReport stale = await rig.Play.PlayAsync(100, Stage);
            check.That(stale.LogCopy == rig.Play.LastLog && File.ReadAllText(rig.Play.LastLog) == FakeLog && !File.Exists(working), "a stale file at the working name is replaced and the log is kept");

            // Something CE (or anything) leaves that is not a plain file or folder is left alone, reported, and the next sweep does not touch it either.
            string canaryFolder = Path.Combine(root, "main", "canary");
            Directory.CreateDirectory(canaryFolder);
            File.WriteAllText(Path.Combine(canaryFolder, "x.txt"), "x");
            rig.Mischief = start => File.CreateSymbolicLink(Path.Combine(start.Environment["BEA_USER_DIR"]!, "escape"), canaryFolder);
            CePlayReport stuck = await rig.Play.PlayAsync(100, Stage);
            rig.Mischief = null;
            check.That(stuck.Started && stuck.Left.Count == 1 && stuck.Left[0].EndsWith("escape", StringComparison.Ordinal) && stuck.Message.Contains("left in place", StringComparison.Ordinal) &&
                       File.ReadAllText(Path.Combine(canaryFolder, "x.txt")) == "x" && PlayFolders(rig.Parent).Length == 1, $"a link left in the folder is reported, not followed and not removed: {stuck.Message}");
            CePlaySweep again = rig.Play.SweepStale();
            check.That(again.Removed.Count == 0 && PlayFolders(rig.Parent).Length == 1 && File.ReadAllText(Path.Combine(canaryFolder, "x.txt")) == "x", "a sweep in the same companion leaves it (it is this companion's)");
            CePlaySweep later = CePlayFolder.SweepStale(rig.Parent, 999999, null, _ => false);
            check.That(later.Removed.Count == 0 && File.ReadAllText(Path.Combine(canaryFolder, "x.txt")) == "x" && later.Kept.Any(line => line.Contains("left in place", StringComparison.Ordinal)),
                "a later sweep that finds the same folder still does not follow or remove the link, and says so");
        }
        finally
        {
            foreach (string name in CePlay.FenceVariables.Concat(LeakedKnobs)) System.Environment.SetEnvironmentVariable(name, null);
            System.Environment.SetEnvironmentVariable("BEA_REPORT_NO_OPEN", null);
            System.Environment.SetEnvironmentVariable("BEA_USER_DIR", null);
            System.Environment.SetEnvironmentVariable("BEA_GAME_DIR", null);
        }

        // ---- the player's files that cannot be copied or read: said, and the play goes on ------------------------------------------------------------
        Rig bad = await MakeRigAsync(Path.Combine(root, "unreadable"), original, ini: "gamedir=é\n");
        File.WriteAllBytes(Path.Combine(bad.User, "ce.ini"), [0x67, 0x61, 0xFF, 0xFE, 0x0A]);   // not UTF-8
        File.Delete(Path.Combine(bad.User, "defaultoptions.bea"));
        File.CreateSymbolicLink(Path.Combine(bad.User, "defaultoptions.bea"), Path.Combine(bad.User, "savegames", "CE Pilot.bes"));
        CePlayReport coarse = await bad.Play.PlayAsync(100, Stage);
        check.That(coarse.Started && bad.Seen!.Ini == "mods=play-level-100\nrecord_sessions=0\nupdate_check=0\n" && bad.Seen.OptionsHash is null && coarse.Message.Contains("could not be read safely", StringComparison.Ordinal) &&
                   coarse.Message.Contains("not a plain file", StringComparison.Ordinal) && File.Exists(Path.Combine(bad.User, "savegames", "CE Pilot.bes")),
            $"a ce.ini that is not UTF-8 stands in as CE's defaults and an options file that is a link is not copied, both said: {coarse.Message}");

        // ---- refusals, each before anything is made or started -----------------------------------------------------------------------------------------
        async Task Refuses(string what, Rig rigged, string contains, Func<string, SaveOutcome>? stage = null)
        {
            string[] userSnapshot = LevelEditorPageTests.Snapshot(rigged.User);
            Func<string, ModInfo, SaveOutcome> chosen = stage is null ? Stage : (parent, _) => stage(parent);
            CePlayReport refusal = await rigged.Play.PlayAsync(100, chosen);
            check.That(!refusal.Started && rigged.Runs == 0 && ReferenceEquals(rigged.Play.Last, refusal) && refusal.Message.Contains(contains, StringComparison.Ordinal) && PlayFolders(rigged.Parent).Length == 0 &&
                       LevelEditorPageTests.Snapshot(rigged.User).SequenceEqual(userSnapshot), $"{what}: nothing started, no folder left, the player's folder as it was: \"{refusal.Message}\"");
        }
        await Refuses("on Windows", await MakeRigAsync(Path.Combine(root, "windows"), original, windows: () => true), "Linux only");
        await Refuses("with a CE older than 0.1.11", await MakeRigAsync(Path.Combine(root, "old"), original, packageVersion: "0.1.9", answer: "Onslaught CE V0.1.9, build abcdef123456"), "needs 0.1.11");
        await Refuses("with a launcher that answers with something else", await MakeRigAsync(Path.Combine(root, "garbled"), original, answer: "hello"), "version");
        await Refuses("with a package of an affected launcher", await MakeRigAsync(Path.Combine(root, "affected"), original, packageVersion: "0.1.6", answer: "Onslaught CE V0.1.6, build abcdef123456"), "0.1.6");
        await Refuses("with no CE launcher chosen", await MakeRigAsync(Path.Combine(root, "nolauncher"), original, withPackage: false), "Choose the Onslaught CE launcher");
        await Refuses("when the edit cannot be staged", await MakeRigAsync(Path.Combine(root, "nostage"), original), "cannot stage that", _ => new SaveOutcome(null, "The mod cannot stage that edit."));

        // A version that is already known is not asked again, and a package that turns out to be an affected launcher is refused all the same.
        Rig cached = await MakeRigAsync(Path.Combine(root, "cached"), original, executableLauncher: true);
        await cached.Game.ChooseCeAsync(Path.Combine(cached.Package, "onslaught-ce"));
        check.That(cached.Game.CeVersion is { Version: "0.1.12" }, $"the stand-in launcher's answer to --version was read: {cached.Game.CeVersionMessage}");
        CePlayReport known = await cached.Play.PlayAsync(100, Stage);
        check.That(known.Started && cached.VersionAsked == 0 && cached.Runs == 1, "when the launcher's version is known already, the play does not ask for it again");
        File.WriteAllText(Path.Combine(cached.Package, "README.txt"), "Onslaught CE 0.1.6 (preview)\n\nQuick start\n");
        CePlayReport affectedNow = await cached.Play.PlayAsync(100, Stage);
        check.That(!affectedNow.Started && cached.Runs == 1 && affectedNow.Message.Contains("0.1.6", StringComparison.Ordinal) && PlayFolders(cached.Parent).Length == 0,
            $"a package that has become an affected launcher is refused even though its version was known: {affectedNow.Message}");

        // The play folder may never be, hold or lie inside the player's own CE folder: refused before a thing is made there.
        Rig inside = await MakeRigAsync(Path.Combine(root, "inside"), original);
        CePlay clash = new(inside.Game, Path.Combine(inside.User, "ce-play"), new CePlayHooks(Parent: Path.Combine(inside.User, "ce-play"), ReadVersion: (_, _) => Task.FromResult("Onslaught CE V0.1.12, build abcdef123456")));
        string[] insideBefore = LevelEditorPageTests.Snapshot(inside.User);
        string insideTree = Listing(inside.User);
        CePlayReport clashed = await clash.PlayAsync(100, Stage);
        check.That(!clashed.Started && clashed.Message.Contains("same place or one is inside the other", StringComparison.Ordinal) && Listing(inside.User) == insideTree && LevelEditorPageTests.Snapshot(inside.User).SequenceEqual(insideBefore),
            $"a play folder inside the player's own CE folder is refused and nothing is written there, not even a folder: {clashed.Message}");
        CePlay same = new(inside.Game, inside.User, new CePlayHooks(Parent: inside.User, ReadVersion: (_, _) => Task.FromResult("Onslaught CE V0.1.12, build abcdef123456")));
        CePlayReport sameFolder = await same.PlayAsync(100, Stage);
        CePlay holds = new(inside.Game, Path.GetDirectoryName(inside.User)!, new CePlayHooks(Parent: Path.GetDirectoryName(inside.User)!, ReadVersion: (_, _) => Task.FromResult("Onslaught CE V0.1.12, build abcdef123456")));
        CePlayReport above = await holds.PlayAsync(100, Stage);
        check.That(!sameFolder.Started && !above.Started && Listing(inside.User) == insideTree && LevelEditorPageTests.Snapshot(inside.User).SequenceEqual(insideBefore),
            "the player's own folder as the play folder, or a play folder that holds it, is refused too");

        await PageAsync(tree, original, Path.Combine(root, "page"), check);
    }

    // ---- the Level editor's button -----------------------------------------------------------------------------------------------------------------
    private static void Set(LineEdit field, string text) => field.Text = text;

    private static async Task PageAsync(SceneTree tree, byte[] original, string root, Checks check)
    {
        check.Suite("test play: the Level editor's button");
        Directory.CreateDirectory(root);
        Rig rig = await MakeRigAsync(root, original);
        string resources = Path.Combine(rig.Install.Game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "level-100").File));
        string settingsPath = Path.Combine(root, "app-settings", "settings.json");
        Directory.CreateDirectory(Path.GetDirectoryName(settingsPath)!);
        new SettingsStore(settingsPath).Save(new CompanionSettings { GameFolder = rig.Install.Game, Target = GameTarget.Original, AutoBackup = false, CeLauncher = Path.Combine(rig.Package, "onslaught-ce") });
        Seen? seen = null;
        byte[]? stagedWorld = null;
        int exit = 0;
        string? log = FakeLog;
        TaskCompletionSource<bool>? gate = null;   // while set, CE "runs" until the test lets it close
        CePlayHooks hooks = new(Parent: Path.Combine(root, "app-play"), ReadVersion: (_, _) => Task.FromResult("Onslaught CE V0.1.12, build abcdef123456"),
            Run: async start =>
            {
                string folder = start.Environment["BEA_USER_DIR"]!;
                string world = Path.Combine(folder, "mods", "play-level-100", "data", "worlds", "world100.wrd");
                stagedWorld = File.Exists(world) ? File.ReadAllBytes(world) : null;
                seen = new Seen([.. start.ArgumentList], start.Environment.ToDictionary(pair => pair.Key, pair => pair.Value), Listing(folder), "", null, start.FileName, start.WorkingDirectory, stagedWorld, null);
                if (log is not null) File.WriteAllText(Path.Combine(folder, "onslaught-ce.log"), log);
                if (gate is not null) await gate.Task;
                return exit;
            });
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, new CompanionEnvironment([rig.Install.SteamRoot], settingsPath, GameRunning: () => false, OpenUrl: _ => { },
            DefaultBackupFolder: Path.Combine(root, "app-backups"), CeUserFolder: rig.User, CePlay: hooks));
        tree.Root.AddChild(app);
        try
        {
            for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Frame(tree);
            LevelEditorPage page = app.LevelEditor;
            app.Navigate("levels");
            await Frame(tree);
            check.That(page.Play.Disabled && page.Play.Text == "Play this level with the changes", $"with no change there is nothing to try: \"{page.Play.TooltipText}\"");
            check.That(page.OpenLevel(100) && page.Play.Disabled && page.Play.TooltipText.Contains("Make a change first", StringComparison.Ordinal), $"a level just opened has nothing to play yet: \"{page.Play.TooltipText}\"");

            page.SelectRow(1);
            Set(page.X, "7");
            Set(page.Y, "8");
            Set(page.Z, "9");
            page.X.EmitSignal(LineEdit.SignalName.TextSubmitted, page.X.Text);
            string[] gameBefore = LevelEditorPageTests.Snapshot(rig.Install.Game), userBefore = LevelEditorPageTests.Snapshot(rig.User);
            check.That(page.HasChanges && !page.Play.Disabled && page.Play.TooltipText.Contains("without saving anything", StringComparison.Ordinal), $"a move makes the button work, and it says nothing is saved: \"{page.Play.TooltipText}\"");

            gate = new();
            Task playing = page.PlayAsync();
            check.That(page.Play.Disabled && app.Services.Play.Running && page.Play.TooltipText.Contains("already", StringComparison.Ordinal), $"while CE runs the button is off and says why: \"{page.Play.TooltipText}\"");
            gate.SetResult(true);
            await playing;
            gate = null;
            check.That(seen is not null && seen.Arguments[^4] == "-level" && seen.Arguments[^3] == "100" && stagedWorld is { Length: > 100 }, "pressing it starts CE at level 100 with a mod holding the open level's world");
            check.That(stagedWorld!.SequenceEqual(page.Model!.Session!.ToBytes()) && page.Model.Row(1)!.Position == new System.Numerics.Vector3(7f, 8f, 9f), "the mod CE is given holds the open level with the move as it is now, saved or not");
            check.That(page.HasChanges && page.ChangeCount == 1 && !page.Save.Disabled, "the move still counts as unsaved afterwards: a test play saves nothing");
            check.That(!page.Play.Disabled && PlayFolders(Path.Combine(root, "app-play")).Length == 0 && page.Play.Visible, "afterwards the button is on again and the temporary folder is gone");
            check.That(page.PlayNote.Contains("ran level 100 and closed", StringComparison.Ordinal) && page.PlayNote.Contains("loaded the mod's world file", StringComparison.Ordinal), $"the page's note says how it went: \"{page.PlayNote}\"");
            check.That(app.Status.Label.Text.Contains("Onslaught CE closed after level 100", StringComparison.Ordinal), $"the status line says CE closed: \"{app.Status.Label.Text}\"");
            check.That(LevelEditorPageTests.Snapshot(rig.Install.Game).SequenceEqual(gameBefore) && LevelEditorPageTests.Snapshot(rig.User).SequenceEqual(userBefore), "the game folder and the player's CE folder are untouched by the play");

            // Pressed through the button, with a CE that did not load the mod: the note says so and quotes CE's mods lines.
            log = "onslaught-ce: mods: play-level-100: refused (a file's SHA-256 does not match mod.json)\n";
            exit = 2;
            page.Play.EmitSignal(BaseButton.SignalName.Pressed);
            for (int frame = 0; frame < 120 && app.Services.Play.Running; frame++) await Frame(tree);
            await Frame(tree);
            check.That(!app.Services.Play.Running && app.Status.Label.Text.Contains("does not say it loaded the mod", StringComparison.Ordinal), $"a log without the mod's line is said on the status line too: \"{app.Status.Label.Text}\"");

            // With a CE that is too old the button says why, before anything is started.
            File.WriteAllText(Path.Combine(rig.Package, "README.txt"), "Onslaught CE V0.1.9\n");
            exit = 0;
            log = FakeLog;
            int before = PlayFolders(Path.Combine(root, "app-play")).Length;
            check.That(page.Play.Disabled == false && before == 0, "a package whose version is only read at the play is still offered");
        }
        finally
        {
            app.QueueFree();
            await Frame(tree);
        }
    }
}
