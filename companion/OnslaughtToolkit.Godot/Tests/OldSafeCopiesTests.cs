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
        File.WriteAllBytes(Path.Combine(root, "Loose.bes"), original);
        File.WriteAllBytes(Path.Combine(windowed, "Second.bes"), original);
        bool linked = TryLink(() => Directory.CreateSymbolicLink(Path.Combine(root, "Linked Copy"), Path.Combine(root, "Enhanced Copy")));
        bool fileLinked = TryLink(() => File.CreateSymbolicLink(Path.Combine(windowed, "Pointer.bes"), Path.Combine(enhanced, "Pilot.bes")));
        Dictionary<string, string> before = Snapshot(root);

        IReadOnlyList<OldCopyCareer> found = OldSafeCopies.Find(root);
        check.That(found.Select(career => $"{career.Copy}/{career.Name}").SequenceEqual(["Enhanced Copy/ALPHA", "Enhanced Copy/Pilot", "windowed/Second"]),
            "Every career-sized .bes in a copy's savegames folder is found, by copy then name; other files, short files, " +
            "files outside savegames and linked copies or files are not: " + string.Join(", ", found.Select(career => career.Copy + "/" + career.Name)));
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
