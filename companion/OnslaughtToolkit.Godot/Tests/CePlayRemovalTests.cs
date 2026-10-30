// SPDX-License-Identifier: GPL-3.0-only
// Four deterministic checks that pin "every step of the removal is by name in an open folder", proposed by the reviewer (Peer E, review of the Play button, request R7) and taken as
// he wrote them: with the tests of CePlayTests alone, putting back a path-based unlink of a file, a path-based rmdir of a nested folder, a path-based rmdir of the temporary
// folder, a link-following open of the temporary folder or one of the play folder all passed; with these four each of them fails. They work through the CePlayFolder.AfterKind hook.
using System.Runtime.Versioning;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

internal static partial class CePlayTests
{
    private static DateTime RemovalNow => new(2026, 10, 30, 6, 0, 0, DateTimeKind.Utc);

    [SupportedOSPlatform("linux")]
    private static void ScratchClean(string path)
    {
        if (!Directory.Exists(path) && !File.Exists(path)) return;
        FileSystemInfo info = new DirectoryInfo(path);
        if (info.LinkTarget is not null || File.Exists(path)) { File.Delete(path); return; }
        foreach (string entry in Directory.EnumerateFileSystemEntries(path, "*", new EnumerationOptions { AttributesToSkip = 0 }).ToList()) ScratchClean(entry);
        Directory.Delete(path, false);
    }

    // E9: at the worst moment, the folder that HOLDS the entry being removed is swapped for a link to a tree with a same-named file and a same-named empty folder.
    // A removal that goes by path from there would delete the canary file or folder in the other tree; one that works by name in the open folder removes the real entries.
    [SupportedOSPlatform("linux")]
    private static void RemovalHolderSwapped(string root, Checks check)
    {
        Directory.CreateDirectory(root);
        string canaryTree = Path.Combine(root, "canary-tree");
        Directory.CreateDirectory(Path.Combine(canaryTree, "sub"));
        File.WriteAllText(Path.Combine(canaryTree, "x.txt"), "canary");
        CePlayFolder folder = CePlayFolder.Create(Path.Combine(root, "play"), 100, "m", 1, RemovalNow).Value!;
        string inner = Path.Combine(folder.Root, "inner");
        Directory.CreateDirectory(Path.Combine(inner, "sub"));
        File.WriteAllText(Path.Combine(inner, "x.txt"), "real");
        bool swapped = false;
        CePlayFolder.AfterKind = shown =>
        {
            // the first entry of "inner" that is read (x.txt or sub, whichever comes first): swap inner for a link, once
            if (swapped || !shown.Contains(Path.Combine("inner", ""), StringComparison.Ordinal) || shown.EndsWith("inner", StringComparison.Ordinal)) return;
            swapped = true;
            Directory.Move(inner, inner + ".moved");
            Directory.CreateSymbolicLink(inner, canaryTree);
        };
        CePlayRemoval result;
        try { result = folder.Remove(); } finally { CePlayFolder.AfterKind = null; }
        bool canaryFile = File.Exists(Path.Combine(canaryTree, "x.txt")) && File.ReadAllText(Path.Combine(canaryTree, "x.txt")) == "canary", canaryDir = Directory.Exists(Path.Combine(canaryTree, "sub"));
        check.That(swapped && canaryFile && canaryDir, "E9 an entry is removed by name in the open folder that holds it: swapping that folder for a link leaves the other tree's same-named file and folder alone");
        ScratchClean(root);
    }

    // E10: the play folder itself replaced by a link (after Create) is refused and nothing in the other tree is touched.
    [SupportedOSPlatform("linux")]
    private static void RemovalPlayFolderLink(string root, Checks check)
    {
        Directory.CreateDirectory(root);
        string elsewhere = Path.Combine(root, "elsewhere");
        CePlayFolder folder = CePlayFolder.Create(Path.Combine(root, "play"), 100, "m", 1, RemovalNow).Value!;
        string name = Path.GetFileName(folder.Root);
        Directory.CreateDirectory(Path.Combine(elsewhere, name));
        File.Copy(Path.Combine(folder.Root, CePlayFolder.MarkerName), Path.Combine(elsewhere, name, CePlayFolder.MarkerName));
        File.WriteAllText(Path.Combine(elsewhere, name, "canary.txt"), "x");
        Directory.Move(Path.Combine(root, "play"), Path.Combine(root, "play.moved"));
        Directory.CreateSymbolicLink(Path.Combine(root, "play"), elsewhere);
        CePlayRemoval result = folder.Remove();
        bool intact = File.Exists(Path.Combine(elsewhere, name, "canary.txt")) && File.Exists(Path.Combine(elsewhere, name, CePlayFolder.MarkerName));
        check.That(!result.Removed && intact, "E10 a play folder replaced by a link is refused and the other tree is left as it was");
        ScratchClean(root);
    }

    // E10b: the play folder is swapped for a link to a tree that holds an EMPTY folder of the same name, after the first entry was read: a final removal by path would take that empty folder away.
    [SupportedOSPlatform("linux")]
    private static void RemovalPlayFolderSwappedLate(string root, Checks check)
    {
        Directory.CreateDirectory(root);
        string elsewhere = Path.Combine(root, "elsewhere"), play = Path.Combine(root, "play");
        CePlayFolder folder = CePlayFolder.Create(play, 100, "m", 1, RemovalNow).Value!;
        string name = Path.GetFileName(folder.Root), twin = Path.Combine(elsewhere, name);
        Directory.CreateDirectory(twin);
        File.WriteAllText(Path.Combine(folder.Root, "one.txt"), "1");
        bool swapped = false;
        CePlayFolder.AfterKind = shown =>
        {
            if (swapped || !shown.EndsWith("one.txt", StringComparison.Ordinal)) return;
            swapped = true;
            Directory.Move(play, play + ".moved");
            Directory.CreateSymbolicLink(play, elsewhere);
        };
        CePlayRemoval result;
        try { result = folder.Remove(); } finally { CePlayFolder.AfterKind = null; }
        bool twinStays = Directory.Exists(twin);
        bool realGone = !Directory.Exists(Path.Combine(play + ".moved", name));
        check.That(swapped && twinStays, "E10b the final removal of the folder is by name in the open play folder: a swapped play path takes nothing from the other tree");
        ScratchClean(root);
    }

    // E12b: the temporary folder itself replaced by a link to a folder that carries a copy of its marker.
    [SupportedOSPlatform("linux")]
    private static void RemovalTemporaryFolderLink(string root, Checks check)
    {
        Directory.CreateDirectory(root);
        CePlayFolder folder = CePlayFolder.Create(Path.Combine(root, "play"), 100, "m", 1, RemovalNow).Value!;
        string twin = Path.Combine(root, "twin-parent", "real");
        Directory.CreateDirectory(twin);
        File.Copy(Path.Combine(folder.Root, CePlayFolder.MarkerName), Path.Combine(twin, CePlayFolder.MarkerName));
        File.WriteAllText(Path.Combine(twin, "canary.txt"), "x");
        Directory.Move(folder.Root, folder.Root + ".moved");
        Directory.CreateSymbolicLink(folder.Root, twin);
        CePlayRemoval result = folder.Remove();
        bool intact = File.Exists(Path.Combine(twin, "canary.txt")) && File.Exists(Path.Combine(twin, CePlayFolder.MarkerName));
        check.That(!result.Removed && intact, "E12b a temporary folder replaced by a link is refused and what it points at is left as it was");
        ScratchClean(root);
    }
}
