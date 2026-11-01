// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>Reads one explicitly selected world as a bounded, read-only snapshot.</summary>
internal static class SelectedWorldInput
{
    // This preview supports the same upper bound as a world member read from an existing level archive.
    internal const int MaxBytes = LevelArchive.MaxMemberInflatedBytes;

    internal static byte[] Read(string path)
    {
        if (string.IsNullOrWhiteSpace(path) || !string.Equals(Path.GetExtension(path), ".wrd", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Choose an Onslaught CE world file ending in .wrd.");
        FileInfo file = new(path);
        if (file.LinkTarget is not null)
            throw new InvalidDataException("Choose the world file itself, not a link.");
        // Check before opening too: empty files and common special files do not need to be opened at all.
        if (!file.Exists || file.Length is 0 or > MaxBytes || (file.Attributes & (FileAttributes.Directory | FileAttributes.Device)) != 0)
            throw new InvalidDataException("This world is empty, unavailable, or larger than the preview supports.");
        using FileStream stream = new(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (!stream.CanSeek || stream.Length is 0 or > MaxBytes)
            throw new InvalidDataException("This world is empty or larger than the preview supports.");
        byte[] bytes = new byte[(int)stream.Length];
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1)
            throw new InvalidDataException("The selected world changed while it was being read. Choose it again.");
        return bytes;
    }

    internal static string DisplayName(string path)
    {
        string clean = new(Path.GetFileName(path).Where(c => !char.IsControl(c)).Take(80).ToArray());
        return clean.Length > 0 ? clean : "Selected world";
    }
}
