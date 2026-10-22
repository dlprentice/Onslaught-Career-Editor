// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Finding careers left in the retired Windows toolkit's copied installs, on a fake copies folder in scratch shaped
/// like <c>%APPDATA%\OnslaughtCareerEditor\GameProfiles</c>, and saving one through the protected copy route.
/// </summary>
internal static class OldSafeCopiesTests
{
    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("old toolkit copies");
        string root = Path.Combine(outputDirectory, "old-copies", "GameProfiles");
        string enhanced = Directory.CreateDirectory(Path.Combine(root, "Enhanced Copy", "savegames")).FullName;
        string windowed = Directory.CreateDirectory(Path.Combine(root, "windowed", "savegames")).FullName;
        Directory.CreateDirectory(Path.Combine(root, "Empty Copy"));
        File.WriteAllBytes(Path.Combine(enhanced, "Pilot.bes"), original);
        File.WriteAllBytes(Path.Combine(enhanced, "ALPHA.BES"), original);
        File.WriteAllBytes(Path.Combine(enhanced, "short.bes"), original[..100]);
        File.WriteAllBytes(Path.Combine(enhanced, "defaultoptions.bea"), original);
        File.WriteAllText(Path.Combine(enhanced, "notes.txt"), "not a career");
        File.WriteAllBytes(Path.Combine(root, "Enhanced Copy", "Root.bes"), original);
        File.WriteAllBytes(Path.Combine(root, "Enhanced Copy", "defaultoptions.bea"), original);
        File.WriteAllBytes(Path.Combine(Directory.CreateDirectory(Path.Combine(root, "Enhanced Copy", "saves")).FullName, "Old.bes"), original);
        File.WriteAllBytes(Path.Combine(Directory.CreateDirectory(Path.Combine(root, "Enhanced Copy", "Save")).FullName, "Third.bes"), original);
        File.WriteAllBytes(Path.Combine(Directory.CreateDirectory(Path.Combine(root, "Enhanced Copy", "other")).FullName, "Elsewhere.bes"), original);
        File.WriteAllBytes(Path.Combine(root, "Loose.bes"), original);
        File.WriteAllBytes(Path.Combine(windowed, "Second.bes"), original);
        bool linked = TryLink(() => Directory.CreateSymbolicLink(Path.Combine(root, "Linked Copy"), Path.Combine(root, "Enhanced Copy")));
        bool fileLinked = TryLink(() => File.CreateSymbolicLink(Path.Combine(windowed, "Pointer.bes"), Path.Combine(enhanced, "Pilot.bes")));
        Dictionary<string, string> before = Snapshot(root);

        IReadOnlyList<OldCopyCareer> found = OldSafeCopies.Find(root);
        // The folders the retired AppCore rescue searched (savegames, saves, Save and the copy's root), every .bes of any length.
        string[] expected = ["Enhanced Copy/savegames/ALPHA", "Enhanced Copy/savegames/Pilot", "Enhanced Copy/savegames/short",
            "Enhanced Copy/saves/Old", "Enhanced Copy/Save/Third", "Enhanced Copy//Root", "windowed/savegames/Second"];
        string[] listed = found.Select(career => $"{career.Copy}/{career.Folder}/{career.Name}").ToArray();
        check.That(listed.SequenceEqual(expected),
            "Every .bes in a copy's savegames, saves and Save folders and at the copy's root is found, by copy, folder and name; " +
            "other files, defaultoptions.bea, other folders, files outside a copy and linked copies or files are not: " + string.Join(", ", listed));
        check.That(found.Where(career => !career.CanCopy).Select(career => career.Name).SequenceEqual(["short"]) &&
            found.Single(career => career.Name == "short").Length == 100,
            "A .bes that is not career-sized is still listed, marked as one that cannot be copied");
        check.That(found.Single(career => career.Name == "Root").Where == "Enhanced Copy (top folder)" &&
            found.Single(career => career.Name == "Pilot").Where == "Enhanced Copy" && found.Single(career => career.Name == "Old").Where == "Enhanced Copy/saves",
            "Each is named by its copy and, outside savegames, the folder it is in");
        check.That(linked && fileLinked, "The fake tree includes a linked copy and a linked career (both skipped above).");
        check.That(OldSafeCopies.Find(Path.Combine(outputDirectory, "old-copies", "missing")).Count == 0 && OldSafeCopies.Find(null).Count == 0 &&
            OldSafeCopies.Find(" ").Count == 0, "A missing or unset copies folder lists nothing.");
        check.That(OperatingSystem.IsWindows() ? OldSafeCopies.DefaultRoot()?.EndsWith(Path.Combine("OnslaughtCareerEditor", "GameProfiles")) == true
            : OldSafeCopies.DefaultRoot() is null, "Only Windows has an old copies folder to look in.");

        // Saving one elsewhere is the ordinary protected copy: a verified read, a new file, a read-back.
        ProtectedSaveFiles files = new();
        string source = found.FirstOrDefault(career => career.Name == "Pilot")?.Path ?? "";
        ProtectedRead read = files.OpenCareer(source);
        string rescued = Path.Combine(outputDirectory, "old-copies", "Pilot (rescued).bes");
        PublicationReceipt copy = read.Ok ? files.PublishCopy(read.Input, read.Identity, read.Sha256, rescued, read.Bytes!.ToArray()) : new(false, read.Message);
        check.That(copy.Ok && File.ReadAllBytes(rescued).AsSpan().SequenceEqual(original), "A career found in an old copy is saved elsewhere byte for byte.");
        ProtectedRead shortRead = files.OpenCareer(found.Single(career => career.Name == "short").Path);
        check.That(!shortRead.Ok, "A listed file that is not career-sized is refused by the protected read: " + shortRead.Message);
        check.That(Snapshot(root).OrderBy(pair => pair.Key).SequenceEqual(before.OrderBy(pair => pair.Key)),
            "Finding and saving careers changes nothing in the old copies.");
    }

    private static Dictionary<string, string> Snapshot(string root) =>
        new DirectoryInfo(root).EnumerateFileSystemInfos("*", new EnumerationOptions { RecurseSubdirectories = true, AttributesToSkip = 0 })
            .ToDictionary(entry => Path.GetRelativePath(root, entry.FullName),
                entry => entry.LinkTarget ?? (entry is FileInfo file ? Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(file.FullName))) : "folder"));

    private static bool TryLink(Action make)
    {
        try
        {
            make();
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return false;
        }
    }
}
