// SPDX-License-Identifier: MIT
using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Game;

public enum ExecutableState { Retail, Different, Missing, Unreadable }

/// <summary>
/// What <c>BEA.exe</c> is, measured read-only. Retail means byte-identical to the Steam release: the
/// pristine specimen <c>BEA.exe.original.backup</c> (SHA-256 below), which the Linux Steam install
/// matched on 2026-09-06 and again on 2026-09-25. A different file is never called an original.
/// </summary>
public sealed record ExecutableIdentity(ExecutableState State, long Size = 0, string? Sha256 = null)
{
    public const string RetailSha256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    public const long RetailSize = 2_506_752;

    public static ExecutableIdentity Classify(long size, string sha256) =>
        new(size == RetailSize && string.Equals(sha256, RetailSha256, StringComparison.OrdinalIgnoreCase)
            ? ExecutableState.Retail : ExecutableState.Different, size, sha256.ToLowerInvariant());

    public static ExecutableIdentity Measure(string path)
    {
        try
        {
            FileInfo info = new(path);
            if (!info.Exists) return new ExecutableIdentity(ExecutableState.Missing);
            if (info.LinkTarget is not null) return new ExecutableIdentity(ExecutableState.Unreadable);
            using FileStream stream = new(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            return Classify(stream.Length, Convert.ToHexString(SHA256.HashData(stream)));
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new ExecutableIdentity(ExecutableState.Unreadable);
        }
    }
}

/// <summary>One career or options file found in the game folder, with whether the companion can open it.</summary>
public sealed record GameFile(string Path, string Name, long Size, DateTime Modified, string? Problem)
{
    public bool Supported => Problem is null;
}

/// <summary>A game installation as the companion sees it. Inspection only reads.</summary>
public sealed record GameFolder(string Root, string Source, ExecutableIdentity Executable, IReadOnlyList<GameFile> Careers,
    GameFile? Options, IReadOnlyList<string> Languages, int MusicTracks, int VoiceLines, int Cutscenes)
{
    public string SavegamesPath => System.IO.Path.Combine(Root, "savegames");
    public string OptionsPath => System.IO.Path.Combine(Root, "defaultoptions.bea");

    /// <summary>A full install has the executable and its data folder, the shape the game itself needs.</summary>
    public static bool LooksLikeGame(string? root) =>
        !string.IsNullOrWhiteSpace(root) && File.Exists(System.IO.Path.Combine(root, "BEA.exe")) &&
        Directory.Exists(System.IO.Path.Combine(root, "data"));

    public static GameFolder Inspect(string root, string source)
    {
        string savegames = System.IO.Path.Combine(root, "savegames");
        List<GameFile> careers = [];
        if (Directory.Exists(savegames))
        {
            foreach (FileInfo file in new DirectoryInfo(savegames).EnumerateFiles("*.bes").OrderBy(file => file.Name, StringComparer.OrdinalIgnoreCase))
                careers.Add(Describe(file));
        }
        FileInfo options = new(System.IO.Path.Combine(root, "defaultoptions.bea"));
        return new GameFolder(root, source, ExecutableIdentity.Measure(System.IO.Path.Combine(root, "BEA.exe")), careers,
            options.Exists || options.LinkTarget is not null ? Describe(options) : null,
            Files(System.IO.Path.Combine(root, "data", "language"), "*.dat").Select(System.IO.Path.GetFileNameWithoutExtension)
                .OfType<string>().ToArray(),
            Files(System.IO.Path.Combine(root, "data", "Music"), "*.ogg").Length,
            Files(System.IO.Path.Combine(root, "data", "sounds", "english", "MessageBox"), "*.ogg").Length,
            Files(System.IO.Path.Combine(root, "data", "video", "cutscenes"), "*.vid").Length);
    }

    /// <summary>Checks the size and version word only; the protected open repeats every check.</summary>
    private static GameFile Describe(FileInfo file)
    {
        string? problem = null;
        try
        {
            if (file.LinkTarget is not null)
            {
                problem = "Linked file; open the real file instead.";
            }
            else if (file.Length != CareerSave.Size)
            {
                problem = $"{file.Length:N0} bytes, not the supported 10,004.";
            }
            else
            {
                Span<byte> version = stackalloc byte[2];
                using FileStream stream = new(file.FullName, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
                if (stream.Read(version) != 2 || (version[0] | (version[1] << 8)) != CareerSave.VersionWord)
                    problem = "Not a supported career version.";
            }
            return new GameFile(file.FullName, file.Name, file.Exists ? file.Length : 0, file.Exists ? file.LastWriteTime : default, problem);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new GameFile(file.FullName, file.Name, 0, default, "Could not be read.");
        }
    }

    private static string[] Files(string folder, string pattern)
    {
        try
        {
            return Directory.Exists(folder) ? Directory.GetFiles(folder, pattern) : [];
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return [];
        }
    }
}

/// <summary>The few choices the companion remembers between runs. Stored as JSON in its own user folder.</summary>
public sealed class CompanionSettings
{
    public string? GameFolder { get; set; }
    public string? BackupFolder { get; set; }
}

public sealed class SettingsStore(string path)
{
    public string FilePath { get; } = path;

    /// <summary>Settings, or defaults when the file is missing or unreadable.</summary>
    public CompanionSettings Load()
    {
        try
        {
            return File.Exists(FilePath) ? JsonSerializer.Deserialize<CompanionSettings>(File.ReadAllText(FilePath)) ?? new() : new();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException)
        {
            return new();
        }
    }

    /// <summary>Writes the whole file through a temporary sibling, so a crash never leaves half a file.</summary>
    public bool Save(CompanionSettings settings)
    {
        try
        {
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(FilePath)!);
            string temporary = FilePath + ".tmp";
            File.WriteAllText(temporary, JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true }));
            File.Move(temporary, FilePath, overwrite: true);
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return false;
        }
    }
}
