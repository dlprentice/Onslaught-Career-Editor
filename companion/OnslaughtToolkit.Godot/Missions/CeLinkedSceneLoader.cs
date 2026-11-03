// SPDX-License-Identifier: GPL-3.0-only
using System.Collections.ObjectModel;
using System.Numerics;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>One object as the selected map installs it. Base-world objects are displayed but are never placement targets.</summary>
public sealed record CeLinkedSceneObject(string Id, string SourceObject, string Definition, string? ModelKey,
    Vector3 Position, Vector3 Orientation, bool FromBaseWorld);

/// <summary>An independently owned, static frame-zero model. Its bytes are local preview data, never project content.</summary>
public sealed class CeLinkedSceneModel
{
    private readonly byte[] _glb;
    public string Key { get; }
    public ReadOnlyMemory<byte> Glb => _glb;

    public CeLinkedSceneModel(string key, ReadOnlyMemory<byte> glb)
    {
        if (string.IsNullOrWhiteSpace(key) || glb.Length is < 12 or > (32 << 20))
            throw new InvalidDataException("The linked model exceeds the preview bounds.");
        Key = key;
        _glb = glb.ToArray();
    }

    public static CeLinkedSceneModel FromMesh(string key, CmshMesh mesh)
    {
        // A map editor needs the installed rest pose, not every animation sample.
        CmshMesh rest = new() { Name = mesh.Name, Textures = mesh.Textures, Parts = mesh.Parts, Modes = [] };
        return new(key, GltfExport.Write(rest, _ => null, _ => throw new InvalidOperationException()));
    }
}

public sealed record CeLinkedSceneInstance(CeLinkedSceneObject Source, Vector3 Position, int? PlacementIndex);

/// <summary>Read-only terrain and installed object/model identities. Position edits do not reload or alter this snapshot.</summary>
public sealed class CeLinkedSceneSnapshot
{
    public int Level { get; }
    public TerrainSurface Terrain { get; }
    public ReadOnlyCollection<CeLinkedSceneObject> Objects { get; }
    public ReadOnlyCollection<CeLinkedSceneModel> Models { get; }
    public ReadOnlyCollection<string> Notes { get; }

    public CeLinkedSceneSnapshot(int level, TerrainSurface terrain, IEnumerable<CeLinkedSceneObject>? objects = null,
        IEnumerable<CeLinkedSceneModel>? models = null, IEnumerable<string>? notes = null)
    {
        if (level is < 1 or > 9999) throw new ArgumentOutOfRangeException(nameof(level));
        ArgumentNullException.ThrowIfNull(terrain);
        CeLinkedSceneObject[] rows = (objects ?? []).Take(2001).ToArray();
        CeLinkedSceneModel[] meshes = (models ?? []).Take(513).ToArray();
        if (rows.Any(row => row is null) || meshes.Any(mesh => mesh is null))
            throw new InvalidDataException("A linked scene has an empty object or model.");
        if (rows.Length > 2000 || meshes.Length > 512 ||
            rows.Select(row => row.Id).Distinct(StringComparer.Ordinal).Count() != rows.Length ||
            meshes.Select(mesh => mesh.Key).Distinct(StringComparer.OrdinalIgnoreCase).Count() != meshes.Length ||
            meshes.Sum(mesh => (long)mesh.Glb.Length) > 128L << 20)
            throw new InvalidDataException("The linked scene exceeds the preview bounds.");
        foreach (CeLinkedSceneObject row in rows)
            if (!Finite(row.Position) || !Finite(row.Orientation))
                throw new InvalidDataException("A linked object has non-finite coordinates.");
        Level = level;
        Terrain = terrain;
        Objects = Array.AsReadOnly(rows);
        Models = Array.AsReadOnly(meshes);
        string[] warnings = (notes ?? []).Take(513).ToArray();
        if (warnings.Length > 512 || warnings.Any(note => note is null || note.Length > 1024))
            throw new InvalidDataException("The linked preview has too many notes.");
        Notes = Array.AsReadOnly(warnings);
    }

    /// <summary>
    /// Where each object appears for this project, by the rule CE applies as the map loads: a placement moves the one selected-level
    /// object its definition is bound to, the base world is left alone, and a binding no placement uses is not read. Drafts CE would refuse
    /// stay previewable: a placement without a binding moves nothing, and a definition placed twice keeps its object where it was.
    /// </summary>
    public IReadOnlyList<CeLinkedSceneInstance> Instances(CeMissionProject project)
    {
        if (project.Map is not { } map || map.Level != Level)
            throw new InvalidDataException("The preview belongs to a different linked map.");
        const int PlacedTwice = -1;
        Dictionary<string, int> rows = new(StringComparer.Ordinal);
        for (int i = 0; i < project.Placements.Count; i++)
            rows[project.Placements[i].Definition] = rows.ContainsKey(project.Placements[i].Definition) ? PlacedTwice : i;
        Dictionary<string, int> named = new(StringComparer.Ordinal);
        foreach (CeLinkedSceneObject item in Objects)
            if (!item.FromBaseWorld) named[item.SourceObject] = named.GetValueOrDefault(item.SourceObject) + 1;
        Dictionary<string, int> targets = new(StringComparer.Ordinal);
        foreach (CeMissionObjectBinding binding in map.Bindings)
        {
            if (!rows.TryGetValue(binding.Definition, out int row)) continue;
            if (named.GetValueOrDefault(binding.SourceObject) != 1)
                throw new InvalidDataException("A placement's map object must be exactly one object of the selected level; base-world objects are not moved.");
            if (row != PlacedTwice) targets.Add(binding.SourceObject, row);
        }
        return Objects.Select(item => !item.FromBaseWorld && targets.TryGetValue(item.SourceObject, out int row)
            ? new CeLinkedSceneInstance(item, project.Placements[row].Position, row)
            : new CeLinkedSceneInstance(item, item.Position, null)).ToArray();
    }

    private static bool Finite(Vector3 v) => float.IsFinite(v.X) && float.IsFinite(v.Y) && float.IsFinite(v.Z);
}

/// <summary>Loads only the selected map and its referenced models. No Godot calls, writes, catalogue or staging operations.</summary>
public static class CeLinkedSceneLoader
{
    internal const int MaxWorldBytes = 16 << 20, MaxMeshBytes = 32 << 20;
    private const int MaxEntries = 8192;

    public static CeLinkedSceneSnapshot Load(string gameRoot, CeMissionProject project)
    {
        ArgumentNullException.ThrowIfNull(project);
        CeMissionMapLink map = project.Map ?? throw new InvalidDataException("Link an installed map before loading its preview.");
        DirectoryInfo root = new(Path.GetFullPath(gameRoot));
        DirectoryInfo data = Directory(root, "data"), resources = Directory(data, "resources");
        FileInfo archive = File(resources, $"{map.Level:D3}_res_pc.aya");
        LevelWorlds worlds = LevelArchive.Read(Read(archive, LevelArchive.MaxFileBytes));
        TerrainSurface surface = TerrainSurface.Build(Heightfield.Read(worlds.Terrain ??
            throw new InvalidDataException("The selected map has no terrain.")));
        List<(bool FromBaseWorld, WorldBody Body)> bodies = [];
        if (worlds.BaseBody is not null && worlds.BaseLevel >= 0) bodies.Add((true, WorldBody.Read(worlds.BaseBody)));
        else if (worlds.BaseLevel >= 0 && worlds.BaseLevel != map.Level)
            bodies.Add((true, ReadLoose(data, worlds.BaseLevel)));
        bodies.Add((false, worlds.RealLevel == map.Level && worlds.RealBody is not null
            ? WorldBody.Read(worlds.RealBody) : ReadLoose(data, map.Level)));

        List<CeLinkedSceneObject> objects = [];
        HashSet<string> needed = new(StringComparer.OrdinalIgnoreCase);
        foreach ((bool fromBaseWorld, WorldBody body) in bodies)
        {
            if (body.Things.Count > WorldBody.MaxThings) throw new InvalidDataException("The map has too many objects to preview.");
            for (int i = 0; i < body.Things.Count; i++)
            {
                PlacedObject thing = body.Things[i];
                int number = thing.Init.MeshNumber;
                string? model = number >= 0 && number < body.NamedMeshes.Count ? MeshKey(body.NamedMeshes[number]) : null;
                if (model is not null) needed.Add(model);
                objects.Add(new((fromBaseWorld ? "base:" : "level:") + i, thing.Init.Name, thing.Definition ?? "", model,
                    thing.Init.Position, thing.Init.Orientation, fromBaseWorld));
            }
        }
        if (needed.Count > 512) throw new InvalidDataException("The map references too many preview models.");
        List<CeLinkedSceneModel> models = [];
        List<string> notes = [];
        int withoutModel = objects.Count(row => row.ModelKey is null);
        if (withoutModel > 0) notes.Add($"{withoutModel} map object(s) have no stored model reference; their geometry is omitted.");
        if (bodies.Any(body => body.Body.TreeGroups.Count > 0)) notes.Add("Tree-group geometry is not included in this preview.");
        if (needed.Count > 0)
        {
            DirectoryInfo meshes = Directory(resources, "meshes");
            Dictionary<string, FileInfo> files = new(StringComparer.OrdinalIgnoreCase);
            foreach (FileInfo file in Entries(meshes).OfType<FileInfo>().Where(file => file.Name.EndsWith(".aya", StringComparison.OrdinalIgnoreCase)))
                if (!files.TryAdd(MeshKey(file.Name), file)) throw new InvalidDataException("Model filenames are ambiguous.");
            long vertices = 0, bytes = 0, instancedParts = 0;
            foreach (string name in needed.Order(StringComparer.OrdinalIgnoreCase))
            {
                if (!files.TryGetValue(name, out FileInfo? file)) { notes.Add("A referenced model is unavailable: " + name); continue; }
                CmshMesh mesh = CmshReader.Read(AyaContainer.Inflate(Read(file, MaxMeshBytes), 64 << 20))[0];
                vertices += mesh.Parts.Sum(part => (long)part.Positions.Length);
                instancedParts += mesh.Parts.Count * (long)objects.Count(row => string.Equals(row.ModelKey, name, StringComparison.OrdinalIgnoreCase));
                if (mesh.Parts.Count > 4096 || vertices > 2_000_000 || instancedParts > 50_000)
                    throw new InvalidDataException("Model geometry exceeds the linked-preview limit.");
                CeLinkedSceneModel model = CeLinkedSceneModel.FromMesh(name, mesh);
                bytes += model.Glb.Length;
                if (bytes > 128L << 20) throw new InvalidDataException("Model geometry exceeds the linked-preview byte limit.");
                models.Add(model);
            }
        }
        CeLinkedSceneSnapshot snapshot = new(map.Level, surface, objects, models, notes);
        _ = snapshot.Instances(project); // Admit names against the same immutable object list the view will use.
        return snapshot;
    }

    private static WorldBody ReadLoose(DirectoryInfo data, int level) =>
        WorldBody.Read(Read(File(Directory(data, "worlds"), $"world{level:D3}.wrd"), MaxWorldBytes));

    private static string MeshKey(string name)
    {
        string key = name.Replace('\\', '%').Replace('/', '%');
        if (key.EndsWith(".aya", StringComparison.OrdinalIgnoreCase)) key = key[..^4];
        if (key.EndsWith(".msh", StringComparison.OrdinalIgnoreCase)) key = key[..^4];
        if (key.StartsWith("m_", StringComparison.OrdinalIgnoreCase)) key = key[2..];
        if (string.IsNullOrWhiteSpace(key) || key.Length > 512 || key.Any(c => char.IsControl(c)))
            throw new InvalidDataException("A map model reference cannot be previewed.");
        return key;
    }

    private static FileSystemInfo[] Entries(DirectoryInfo folder)
    {
        if (!folder.Exists || folder.LinkTarget is not null) throw new InvalidDataException("A preview folder is missing or is a link.");
        FileSystemInfo[] entries = folder.EnumerateFileSystemInfos().Take(MaxEntries + 1).ToArray();
        if (entries.Length > MaxEntries) throw new InvalidDataException("A preview folder exceeds the entry limit.");
        return entries;
    }

    private static DirectoryInfo Directory(DirectoryInfo parent, string name)
    {
        DirectoryInfo[] matches = Entries(parent).OfType<DirectoryInfo>()
            .Where(p => p.Name.Equals(name, StringComparison.OrdinalIgnoreCase)).Take(2).ToArray();
        if (matches.Length > 1) throw new InvalidDataException("Map-data folder names are ambiguous.");
        return matches.SingleOrDefault() ?? throw new DirectoryNotFoundException("A required map-data folder is missing.");
    }

    private static FileInfo File(DirectoryInfo parent, string name)
    {
        FileInfo[] matches = Entries(parent).OfType<FileInfo>()
            .Where(p => p.Name.Equals(name, StringComparison.OrdinalIgnoreCase)).Take(2).ToArray();
        if (matches.Length > 1) throw new InvalidDataException("Map-data filenames are ambiguous.");
        return matches.SingleOrDefault() ?? throw new FileNotFoundException("A required map-data file is missing.");
    }

    private static byte[] Read(FileInfo file, int maximum)
    {
        if (file.LinkTarget is not null) throw new InvalidDataException("A preview input may not be a link.");
        using FileStream stream = OpenRegular(file.FullName);
        long size = stream.Length;
        if (size <= 0 || size > maximum) throw new InvalidDataException("A preview input exceeds its byte limit.");
        byte[] bytes = new byte[checked((int)size)];
        stream.ReadExactly(bytes);
        if (stream.Length != size) throw new InvalidDataException("A preview input changed while it was read.");
        return bytes;
    }

    /// <summary>
    /// Decides the file's kind on an open handle, before any byte is read. An ordinary open of a named pipe waits for a writer and
    /// cannot be cancelled, so the Linux open does not block; neither open follows a final link.
    /// </summary>
    private static FileStream OpenRegular(string path)
    {
        SafeFileHandle handle = OperatingSystem.IsLinux()
            ? LinuxSaveNative.OpenAt(LinuxSaveNative.AtCurrentDirectory, path, LinuxSaveNative.ReadFile, 0)
            : OperatingSystem.IsWindows() ? FileMutationSafety.OpenNoFollowReadHandle(path, "Map preview input")
            : throw new PlatformNotSupportedException("Protected map reads support Linux and Windows.");
        try
        {
            bool regular = OperatingSystem.IsLinux()
                ? (LinuxSaveNative.Inspect(handle).Mode & 0xF000) == 0x8000
                : !FileMutationSafety.GetWindowsIdentity(handle, "Map preview input").IsReparsePoint && ScriptSourceReader.IsDiskFile(handle);
            if (!regular) throw new InvalidDataException("A preview input must be a regular file.");
            return new FileStream(handle, FileAccess.Read);
        }
        catch { handle.Dispose(); throw; }
    }
}
