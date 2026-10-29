// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>What a mod says about itself in <c>mod.json</c>. Text is printable ASCII only (CE logs mod text as ASCII).</summary>
/// <param name="Id">1 to 48 lowercase letters, digits, '-' or '_'; also the mod's folder name.</param>
/// <param name="Name">1 to 64 characters.</param>
/// <param name="Version">1 to 32 characters.</param>
/// <param name="Author">Up to 64 characters; left out of <c>mod.json</c> when empty.</param>
/// <param name="Description">Up to 1024 characters; left out of <c>mod.json</c> when empty.</param>
/// <param name="CeMin">The oldest CE version that loads it: one to four numbers of up to five digits joined by dots, or null.</param>
/// <param name="CeMax">The newest CE version that loads it, in the same form, or null.</param>
public sealed record ModInfo(string Id, string Name, string Version = "1", string Author = "", string Description = "", string? CeMin = null, string? CeMax = null);

/// <summary>One file of a staged mod: its path inside the mod's folder, its size and its SHA-256.</summary>
public sealed record StagedFile(string Path, long Size, string Sha256);

/// <summary>A mod that was written: its folder, the SHA-256 of its <c>mod.json</c> and every staged file, in the order written.</summary>
public sealed record StagedMod(string Root, string ManifestSha256, IReadOnlyList<StagedFile> Files);

/// <summary>A mod that cannot be made or saved, in a sentence the player can act on.</summary>
public sealed class ModStageException : Exception
{
    public ModStageException(string message) : base(message)
    {
    }

    public ModStageException(string message, Exception inner) : base(message, inner)
    {
    }
}

/// <summary>
/// Packages edited world bodies as an Onslaught CE mod folder. A port of the Toolkit's <c>tools/world_mod_stage.py</c>,
/// which the tests compare it with byte for byte: supported per-mod loader limits are checked first, but CE still checks the
/// files and other enabled mods present when it runs. The folder it writes is
/// <code>
/// ID/mod.json                   schema 1, the id, name, version, optional author, description, ce_min and ce_max, and every file with its size and SHA-256
/// ID/data/worlds/worldNNN.wrd   the bodies, byte for byte
/// ID/data/MissionScripts/...    optional edited source text for an existing game file
/// </code>
/// A mod is always a new folder (an existing empty one is used), never inside a game folder or a protected folder, with the
/// files written first and <c>mod.json</c> last (a folder without it is inert). Each file goes through the companion's
/// new-file-only publisher. When anything fails, what this call created is removed again.
/// <para>
/// It detects replacement; it does not lock, as the Python helper does not. The folder checks (no link on the way, not inside a
/// game folder or a protected folder, nothing already in the mod folder) run first and the folders are created after them, and
/// the publisher checks each file's destination again as it publishes it, but nothing holds the folders in between: a directory
/// swapped for a link, or moved into a game folder, by another process after the early checks and before the folders are created
/// is not caught by them, and a folder moved by another process during the run is not guaranteed to stay outside the game folder
/// (the limit every writer through the publisher has). The page that calls it says where the mod was written.
/// </para>
/// </summary>
public static class ModStager
{
    public const int MaxFilesPerMod = 4096, MaxWorldBytes = 4 << 20, MaxSourceBytes = 1 << 20, MaxManifestBytes = 256 << 10,
        MaxSourceFiles = 128, MaxSourceTotal = 8 << 20, MaxStageIncludes = 2048, MaxStageIncludeChars = 16 << 20;
    public const long MaxTotalBytes = 1L << 30;

    private static readonly Regex IdPattern = new("\\A[a-z0-9_-]{1,48}\\z", RegexOptions.CultureInvariant);
    private static readonly Regex VersionPattern = new("\\A[0-9]{1,5}(?:\\.[0-9]{1,5}){0,3}\\z", RegexOptions.CultureInvariant);
    private static readonly Regex WorldPathPattern = new("\\Adata/worlds/world[0-9]{3}\\.wrd\\z", RegexOptions.CultureInvariant);
    private static readonly Regex SourcePathPattern = new("\\Adata/MissionScripts/level([0-9]{3})/([^/]+)\\.msl\\z", RegexOptions.CultureInvariant);

    /// <summary>The path CE reads a level's world from inside a mod: <c>data/worlds/worldNNN.wrd</c>.</summary>
    public static string WorldPath(int level)
    {
        if (level is < 0 or > 999) throw new ModStageException($"A world level is a number from 0 to 999, not {level}.");
        return LevelWorlds.WorldFileName(level);
    }

    /// <summary>The level of a supported CE mission-source path, or null when CE's path rules would refuse it.</summary>
    internal static int? SourceLevel(string path)
    {
        if (path.Length > 240) return null;
        Match match = SourcePathPattern.Match(path);
        if (!match.Success) return null;
        string part = path[(path.LastIndexOf('/') + 1)..];
        if (part.Length > 128 || part[0] == ' ' || part[^1] is ' ' or '.' ||
            part.Any(c => c < 32 || c >= 127 || "\\:*?\"<>|".Contains(c))) return null;
        string stem = part.Split('.')[0].TrimEnd(' ').ToUpperInvariant();
        if (stem is "CON" or "PRN" or "AUX" or "NUL" or "CONIN$" or "CONOUT$" ||
            (stem.Length == 4 && (stem.StartsWith("COM", StringComparison.Ordinal) || stem.StartsWith("LPT", StringComparison.Ordinal)) && stem[3] is >= '0' and <= '9')) return null;
        return int.Parse(match.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>The first thing wrong with what a mod says about itself, or null when CE's loader would accept it (and, as the Toolkit stager does, some CE could load it: ce_min is not after ce_max).</summary>
    public static string? Problem(ModInfo info)
    {
        if (!IdPattern.IsMatch(info.Id)) return "A mod id is 1 to 48 lowercase letters, digits, '-' or '_' (it is also the folder's name).";
        foreach ((string label, string value, int low, int high) in new[]
                 {
                     ("name", info.Name, 1, 64), ("version", info.Version, 1, 32), ("author", info.Author, 0, 64), ("description", info.Description, 0, 1024),
                 })
        {
            if (value.Length < low || value.Length > high) return $"The {label} must be {low} to {high} characters.";
            if (value.Any(c => c < 0x20 || c >= 0x7F)) return $"The {label} may hold printable ASCII only (CE logs mod text as ASCII).";
        }
        foreach ((string label, string? value) in new[] { ("ce_min", info.CeMin), ("ce_max", info.CeMax) })
            if (value is not null && !VersionPattern.IsMatch(value))
                return $"The {label} must be one to four numbers of up to five digits joined by dots, such as 0.1.11.";
        if (info.CeMin is not null && info.CeMax is not null && CompareVersions(info.CeMin, info.CeMax) > 0)
            return $"The ce_min {info.CeMin} is after the ce_max {info.CeMax}: no released CE version could load this mod.";
        return null;
    }

    /// <summary>Two versions as CE's loader orders them: four numbers, the missing ones zero (1.2 equals 1.2.0.0; 1.10 is after 1.9).</summary>
    internal static int CompareVersions(string a, string b)
    {
        static int[] Parts(string text)
        {
            int[] numbers = new int[4];
            string[] parts = text.Split('.');
            for (int i = 0; i < parts.Length; i++) numbers[i] = int.Parse(parts[i], System.Globalization.CultureInfo.InvariantCulture);
            return numbers;
        }
        int[] left = Parts(a), right = Parts(b);
        for (int i = 0; i < 4; i++)
            if (left[i] != right[i]) return left[i] < right[i] ? -1 : 1;
        return 0;
    }

    /// <summary><c>mod.json</c> as CE's loader reads it: strict JSON, schema 1, only the keys it knows, every file with size and SHA-256.</summary>
    public static byte[] BuildManifest(ModInfo info, IReadOnlyDictionary<string, byte[]> files)
    {
        if (Problem(info) is { } problem) throw new ModStageException(problem);
        if (files.Count == 0) throw new ModStageException("A mod lists at least one file.");
        if (files.Count > MaxFilesPerMod) throw new ModStageException($"A mod lists at most {MaxFilesPerMod} files.");
        StringBuilder text = new("{\n  \"schema\": 1,\n");
        text.Append("  \"id\": ").Append(Json(info.Id)).Append(",\n");
        text.Append("  \"name\": ").Append(Json(info.Name)).Append(",\n");
        text.Append("  \"version\": ").Append(Json(info.Version)).Append(",\n");
        if (info.Author.Length > 0) text.Append("  \"author\": ").Append(Json(info.Author)).Append(",\n");
        if (info.Description.Length > 0) text.Append("  \"description\": ").Append(Json(info.Description)).Append(",\n");
        if (info.CeMin is not null) text.Append("  \"ce_min\": ").Append(Json(info.CeMin)).Append(",\n");
        if (info.CeMax is not null) text.Append("  \"ce_max\": ").Append(Json(info.CeMax)).Append(",\n");
        text.Append("  \"files\": [\n");
        string[] paths = [.. files.Keys.Order(StringComparer.Ordinal)];
        HashSet<string> seen = new(StringComparer.OrdinalIgnoreCase);
        bool hasWorld = false;
        long total = 0;
        for (int i = 0; i < paths.Length; i++)
        {
            byte[] data = files[paths[i]];
            if (!seen.Add(paths[i])) throw new ModStageException($"{paths[i]}: a file is listed twice, ignoring case.");
            if (WorldPathPattern.IsMatch(paths[i]))
            {
                hasWorld = true;
                if (data.Length is 0 or > MaxWorldBytes) throw new ModStageException($"{paths[i]}: a world file is 1 byte to {MaxWorldBytes} bytes.");
            }
            else if (SourceLevel(paths[i]) is not null)
            {
                if (data.Length > MaxSourceBytes) throw new ModStageException($"{paths[i]}: a mission source is at most {MaxSourceBytes} bytes.");
            }
            else throw new ModStageException($"{paths[i]}: this stager writes world files and mission sources only.");
            total += data.Length;
            if (total > MaxTotalBytes) throw new ModStageException($"A mod's files total at most {MaxTotalBytes} bytes.");
            text.Append("    {\n      \"path\": ").Append(Json(paths[i])).Append(",\n      \"size\": ").Append(data.Length)
                .Append(",\n      \"sha256\": ").Append(Json(Hex(data))).Append("\n    }").Append(i + 1 < paths.Length ? ",\n" : "\n");
        }
        if (!hasWorld) throw new ModStageException("A staged mod needs at least one world file.");
        text.Append("  ]\n}\n");
        if (text.Length > MaxManifestBytes) throw new ModStageException("mod.json would be larger than the loader's 256 KiB.");
        return Encoding.ASCII.GetBytes(text.ToString());
    }

    /// <summary>
    /// Writes <c>PARENT/ID</c>: <c>mod.json</c> and <c>data/worlds/worldNNN.wrd</c> for each level in <paramref name="worlds"/>.
    /// Refuses, with nothing written: what <see cref="BuildManifest"/> refuses, a parent that is not a full path, a mod folder
    /// inside a game folder or any of <paramref name="protectedFolders"/> (compared after resolving links), and a folder that
    /// already holds anything.
    /// </summary>
    /// <exception cref="ModStageException">The mod cannot be made or saved.</exception>
    public static StagedMod Stage(string parent, ModInfo info, IReadOnlyDictionary<int, byte[]> worlds, IEnumerable<string?> protectedFolders) =>
        Stage(parent, info, worlds, protectedFolders, null);

    /// <param name="beforeWrite">Test hook: called with each file's path before it is written.</param>
    /// <param name="beforeCommittedOpen">Test hook: called with each file's path after the publisher moved it into place and before it checks it.</param>
    /// <param name="beforePublish">Test hook: called with each file's path after the publisher began and before it moves the file into place.</param>
    internal static StagedMod Stage(string parent, ModInfo info, IReadOnlyDictionary<int, byte[]> worlds, IEnumerable<string?> protectedFolders,
        Action<string>? beforeWrite, Action<string>? beforeCommittedOpen = null, Action<string>? beforePublish = null)
    {
        Dictionary<string, byte[]> files = [];
        foreach ((int level, byte[] body) in worlds) files[WorldPath(level)] = body;
        return StageFiles(parent, info, files, protectedFolders, beforeWrite, beforeCommittedOpen, beforePublish);
    }

    /// <summary>
    /// Stages a world together with edited source text. Each source must name a world being staged and a source already in the selected game;
    /// this preserves the text, since the game runs the compiled world script. Each source must compile to the exact named script in its
    /// round-tripping world and fit its single-byte encoding; included headers are read from the game and are not copied. Reopening a staged
    /// source is not provided by this API. CE's Windows mod loader remains disabled.
    /// The selected game folder is protected in addition to <paramref name="protectedFolders"/>.
    /// </summary>
    public static StagedMod StageWithSources(string parent, ModInfo info, IReadOnlyDictionary<int, byte[]> worlds,
        IReadOnlyDictionary<string, string> sources, string gameRoot, IEnumerable<string?> protectedFolders) =>
        StageWithSources(parent, info, worlds, sources, gameRoot, protectedFolders, null);

    internal static StagedMod StageWithSources(string parent, ModInfo info, IReadOnlyDictionary<int, byte[]> worlds,
        IReadOnlyDictionary<string, string> sources, string gameRoot, IEnumerable<string?> protectedFolders,
        Action<string>? beforeWrite, Action<string>? beforeCommittedOpen = null, Action<string>? beforePublish = null,
        int maxStageIncludes = MaxStageIncludes, int maxStageIncludeChars = MaxStageIncludeChars)
    {
        if (string.IsNullOrWhiteSpace(gameRoot) || !Path.IsPathFullyQualified(gameRoot)) throw new ModStageException("Choose the game's full folder path first.");
        if (Problem(info) is { } problem) throw new ModStageException(problem);
        if (worlds.Count == 0) throw new ModStageException("A staged mod needs at least one world file.");
        if (sources.Count > MaxSourceFiles) throw new ModStageException($"At most {MaxSourceFiles} mission sources can be staged at once.");
        Dictionary<string, byte[]> files = [];
        long worldTotal = 0;
        foreach ((int level, byte[] body) in worlds)
        {
            if (body is null || body.Length is 0 or > MaxWorldBytes) throw new ModStageException($"A world file is 1 byte to {MaxWorldBytes} bytes.");
            worldTotal += body.Length;
            if (worldTotal > MaxTotalBytes) throw new ModStageException($"A mod's files total at most {MaxTotalBytes} bytes.");
            files[WorldPath(level)] = body.ToArray();
        }
        Dictionary<int, WorldBody> parsedWorlds = [];
        int sourceTotal = 0;
        StageIncludeBudget includes = new(ScriptCompiler.IncludesFrom(gameRoot), maxStageIncludes, maxStageIncludeChars);
        foreach ((string path, string source) in sources)
        {
            if (SourceLevel(path) is not int level || !worlds.ContainsKey(level))
                throw new ModStageException($"{path}: a mission source must name a safe path for a world being staged.");
            if (source is null || source.Length > MaxSourceBytes || source.Any(c => c > 255))
                throw new ModStageException($"{path}: source must be at most {MaxSourceBytes} single-byte characters.");
            sourceTotal += source.Length;
            if (sourceTotal > MaxSourceTotal) throw new ModStageException($"Mission sources total at most {MaxSourceTotal} bytes.");
            if (worldTotal + sourceTotal > MaxTotalBytes) throw new ModStageException($"A mod's files total at most {MaxTotalBytes} bytes.");
            try { _ = ScriptSourceReader.ReadInGame(gameRoot, path); }
            catch (CompileError) { throw new ModStageException($"{path}: the game's original source could not be read safely."); }
            CheckSourceMatchesWorld(path, source, level, files[WorldPath(level)], parsedWorlds, includes.Read);
            files.Add(path, Encoding.Latin1.GetBytes(source));
        }
        return StageFiles(parent, info, files, protectedFolders.Append(gameRoot), beforeWrite, beforeCommittedOpen, beforePublish);
    }

    private static void CheckSourceMatchesWorld(string path, string source, int level, byte[] bytes, Dictionary<int, WorldBody> parsed, Func<string, string> readInclude)
    {
        try
        {
            if (!parsed.TryGetValue(level, out WorldBody? body))
            {
                body = WorldBody.Read(bytes);
                if (!body.Write().AsSpan().SequenceEqual(bytes)) throw new ModStageException($"{path}: the staged world does not round-trip exactly.");
                parsed[level] = body;
            }
            string name = path[(path.LastIndexOf('/') + 1)..^4];
            MissionScript[] found = [.. body.Scripts.Where(script => script.Name == name)];
            if (found.Length != 1) throw new ModStageException($"{path}: the staged world must have exactly one script of this name.");
            MissionScript script = found[0];
            MissionScript compiled = ScriptCompiler.Compile(name, source, readInclude,
                ScriptCompiler.ConstStartOf(script), ScriptCompiler.DoOnceStartOf(script));
            if (!WorldBodyWriter.ScriptBytes(compiled).AsSpan().SequenceEqual(WorldBodyWriter.ScriptBytes(script)))
                throw new ModStageException($"{path}: this source does not compile to the script in the staged world.");
        }
        catch (ModStageException) { throw; }
        catch (CompileError error) { throw new ModStageException($"{path}: {error.Message}", error); }
        catch (Exception error) when (error is IOException || EditSession.IsUnstorable(error))
        {
            throw new ModStageException($"{path}: the source and staged world could not be checked.", error);
        }
    }

    /// <summary>Bounds header reads across every source checked in one stage, not just within each compilation.</summary>
    internal sealed class StageIncludeBudget(Func<string, string> read, int maxFiles, int maxChars)
    {
        private int _files, _chars;
        internal string Read(string path)
        {
            if (_files >= maxFiles) throw new CompileError($"A stage reads at most {maxFiles} included files.");
            _files++;
            string text = read(path);
            if (text.Length > maxChars - _chars) throw new CompileError($"A stage reads at most {maxChars} characters of included text.");
            _chars += text.Length;
            return text;
        }
    }

    private static StagedMod StageFiles(string parent, ModInfo info, Dictionary<string, byte[]> files, IEnumerable<string?> protectedFolders,
        Action<string>? beforeWrite, Action<string>? beforeCommittedOpen, Action<string>? beforePublish)
    {
        byte[] manifest = BuildManifest(info, files);

        string root = CheckDestination(parent, info.Id, protectedFolders);

        List<string> createdFiles = [], createdFolders = [];
        try
        {
            List<StagedFile> written = [];
            foreach (string path in files.Keys.Order(StringComparer.Ordinal))
            {
                string destination = Path.Combine(root, path.Replace('/', Path.DirectorySeparatorChar));
                CreateFolder(Path.GetDirectoryName(destination)!, createdFolders);
                Write(destination, files[path], beforeWrite, beforeCommittedOpen, beforePublish, createdFiles);
                written.Add(new StagedFile(path, files[path].Length, Hex(files[path])));
            }
            Write(Path.Combine(root, "mod.json"), manifest, beforeWrite, beforeCommittedOpen, beforePublish, createdFiles);
            return new StagedMod(root, Hex(manifest), written);
        }
        catch (Exception error)
        {
            // Whatever went wrong, what this call made goes. A problem with the folders or files is reported as a ModStageException; anything
            // else (a cancellation, a bug) is let through as it is, unless something could not be removed, which the player must be told.
            string left = Cleanup(createdFiles, createdFolders);
            if (error is ModStageException) throw Rethrow(error, left);
            if (error is IOException or InvalidOperationException or UnauthorizedAccessException || left.Length > 0)
                throw new ModStageException($"The mod was not saved: {error.Message}{left}", error);
            throw;
        }
    }

    /// <summary>The mod folder's full path, after the checks that need nothing written: nothing is made before they pass.</summary>
    private static string CheckDestination(string parent, string id, IEnumerable<string?> protectedFolders)
    {
        if (!Path.IsPathFullyQualified(parent)) throw new ModStageException("Choose a full folder path to save the mod in.");
        try
        {
            string root = Path.Combine(Path.GetFullPath(parent), id);
            // No link anywhere on the way (the folder, its parents), and not inside a game folder.
            FileMutationSafety.RejectExistingReparseAncestors(root, "Mod folder");
            FileMutationSafety.RejectOutputInGameTree(Path.Combine(root, "mod.json"));
            // A protected folder that does not exist yet (the backups folder before the first backup) still guards its place: RealPath
            // resolves the links in the part that exists and keeps the rest as written.
            foreach (string? guarded in protectedFolders)
                if (!string.IsNullOrEmpty(guarded) && ExportFiles.Inside(root, ExportFiles.RealPath(guarded)))
                    throw new ModStageException("A mod is never saved into your game folder or the companion's backups. Choose another folder.");
            if (File.Exists(root)) throw new ModStageException($"{root} is a file, not a folder: nothing was written.");
            if (Directory.Exists(root))
            {
                string? existing = Directory.EnumerateFileSystemEntries(root).Select(Path.GetFileName).Order(StringComparer.Ordinal).FirstOrDefault();
                if (existing is not null) throw new ModStageException($"{root} already holds \"{existing}\": save the mod in a new folder (nothing was written).");
            }
            return root;
        }
        catch (InvalidOperationException error)
        {
            throw new ModStageException(error.Message, error);
        }
        catch (Exception error) when (error is ArgumentException or NotSupportedException or IOException or UnauthorizedAccessException)
        {
            throw new ModStageException($"That folder cannot be used: {error.Message} Nothing was written.", error);
        }
    }

    private static ModStageException Rethrow(Exception error, string left) =>
        left.Length == 0 ? (ModStageException)error : new ModStageException(error.Message + left, error);

    private static void Write(string path, byte[] bytes, Action<string>? beforeWrite, Action<string>? beforeCommittedOpen, Action<string>? beforePublish, List<string> created)
    {
        beforeWrite?.Invoke(path);
        using GuardedFileMutation guard = FileMutationSafety.BeginGeneratedVacant(path);
        try
        {
            guard.Commit(bytes, beforeCommittedOpen, beforePublish);
        }
        finally
        {
            // A commit that fails after the publisher moved the file into place leaves that file here; it is this call's, so it goes with the rest.
            // (The path is not recorded before the commit: until the file is published, the path may be somebody else's.)
            if (guard.Published) created.Add(path);
        }
    }

    private static void CreateFolder(string path, List<string> created)
    {
        if (Directory.Exists(path)) return;
        string? parent = Path.GetDirectoryName(path);
        if (parent is not null) CreateFolder(parent, created);
        Directory.CreateDirectory(path);
        created.Add(path);
    }

    /// <summary>Removes what one call created, files then folders, newest first; a folder that is not empty is left. Returns a sentence about anything left.</summary>
    private static string Cleanup(List<string> files, List<string> folders)
    {
        List<string> left = [];
        foreach (string file in Enumerable.Reverse(files))
        {
            try
            {
                File.Delete(file);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                left.Add(file);
            }
        }
        foreach (string folder in Enumerable.Reverse(folders))
        {
            try
            {
                Directory.Delete(folder);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                left.Add(folder);
            }
        }
        return left.Count == 0 ? "" : $" These could not be removed and may be deleted: {string.Join(", ", left)}.";
    }

    private static string Hex(byte[] data) => Convert.ToHexStringLower(SHA256.HashData(data));

    /// <summary>A JSON string for printable ASCII (a quotation mark and a backslash are escaped, as Python's json writes them).</summary>
    private static string Json(string text) => "\"" + text.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
}
