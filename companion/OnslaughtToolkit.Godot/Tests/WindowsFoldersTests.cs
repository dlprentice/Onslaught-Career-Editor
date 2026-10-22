// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The Windows folder rules as functions of the folders they are given: the unsynced default backup root and the
/// VirtualStore folder of a game in Program Files. Windows itself has not run them.
/// </summary>
internal static class WindowsFoldersTests
{
    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("windows folders");
        string scratch = Directory.CreateDirectory(Path.Combine(outputDirectory, "windows-folders")).FullName;
        string documents = Directory.CreateDirectory(Path.Combine(scratch, "OneDrive", "Documents")).FullName;
        string local = Directory.CreateDirectory(Path.Combine(scratch, "AppData", "Local")).FullName;
        string userData = Path.Combine(scratch, "user");
        check.That(WindowsFolders.DefaultBackupRoot(true, documents, local, userData) == Path.Combine(local, "Onslaught Companion"),
            "On Windows backups default to the unsynced local application data folder, not Documents (often OneDrive).");
        check.That(WindowsFolders.DefaultBackupRoot(true, documents, Path.Combine(scratch, "missing"), userData) == userData &&
            WindowsFolders.DefaultBackupRoot(true, documents, null, userData) == userData,
            "On Windows without a local application data folder, backups go to the app's own data folder, still not Documents.");
        check.That(WindowsFolders.DefaultBackupRoot(false, documents, local, userData) == documents &&
            WindowsFolders.DefaultBackupRoot(false, Path.Combine(scratch, "missing"), local, userData) == userData,
            "Elsewhere backups stay in Documents, or the app's own data folder without one.");

        string[] programs = [@"C:\Program Files (x86)", @"C:\Program Files"];
        string? store = WindowsFolders.VirtualStoreSaves(@"C:\Program Files (x86)\Lost Toys\Battle Engine Aquila\", local, programs);
        check.That(store == Path.Combine(local, "VirtualStore", "Program Files (x86)", "Lost Toys", "Battle Engine Aquila", "savegames"),
            "A game in Program Files (x86) maps to VirtualStore under the same path without its drive: " + store);
        check.That(WindowsFolders.VirtualStoreSaves(@"c:\program files\BEA", local, programs) ==
            Path.Combine(local, "VirtualStore", "program files", "BEA", "savegames"), "Program Files matches without regard to case.");
        check.That(WindowsFolders.VirtualStoreSaves(@"D:\Games\Battle Engine Aquila", local, programs) is null &&
            WindowsFolders.VirtualStoreSaves(@"C:\Program Files Extra\BEA", local, programs) is null &&
            WindowsFolders.VirtualStoreSaves(@"C:\Program Files", local, programs) is null &&
            WindowsFolders.VirtualStoreSaves(@"C:\Program Files\BEA", null, programs) is null,
            "A game outside Program Files, in a folder that only starts with its name, or with no local data folder has none.");
        check.That(OperatingSystem.IsWindows() || WindowsFolders.VirtualStoreSavesHere(@"C:\Program Files\BEA") is null,
            "Only Windows looks for a VirtualStore folder.");

        string saves = Directory.CreateDirectory(Path.Combine(local, "VirtualStore", "Program Files", "BEA", "savegames")).FullName;
        File.WriteAllBytes(Path.Combine(saves, "Pilot.bes"), original);
        File.WriteAllBytes(Path.Combine(saves, "ALPHA.BES"), original);
        File.WriteAllBytes(Path.Combine(saves, "defaultoptions.bea"), original);
        bool linked = TryLink(() => File.CreateSymbolicLink(Path.Combine(saves, "Pointer.bes"), Path.Combine(saves, "Pilot.bes")));
        IReadOnlyList<string> careers = WindowsFolders.Careers(saves);
        check.That(linked && careers.SequenceEqual(["ALPHA.BES", "Pilot.bes"]),
            "A VirtualStore savegames folder lists its .bes careers by name, not settings or linked files: " + string.Join(", ", careers));
        check.That(WindowsFolders.Careers(Path.Combine(scratch, "missing")).Count == 0 && WindowsFolders.Careers(null).Count == 0,
            "A missing or unset VirtualStore folder lists nothing.");
    }

    private static bool TryLink(Action link)
    {
        try
        {
            link();
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return false;
        }
    }
}
