// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using System.Text.Json.Serialization;

namespace OnslaughtRebuild.GodotClient;

public sealed class LocalPresentationConfig
{
    public const string ManifestFileName = "manifest.json";
    public const int MaxManifestBytes = 64 * 1024;
    private const int MaxJsonDepth = 8;

    public required string RootPath { get; init; }
    public required LocalAssetManifest Manifest { get; init; }
    public bool HasPlayerMesh => Manifest.Player is not null;
    public bool HasTerrainMesh => Manifest.Terrain is not null;
    public LocalMeshRef? Player => Manifest.Player;
    public LocalMeshRef? Terrain => Manifest.Terrain;
    public string PlayerMeshPath => ResolveContained(Manifest.Player!.Mesh);
    public string? TerrainMeshPath => Manifest.Terrain is null ? null : ResolveContained(Manifest.Terrain.Mesh);

    public static LocalPresentationConfig? TryResolve(string? explicitRoot, bool smokeMode)
        => TryResolve(explicitRoot, smokeMode, out _);

    public static LocalPresentationConfig? TryResolve(string? explicitRoot, bool smokeMode, out string? error)
    {
        error = null;
        if (smokeMode) { error = "Smoke mode always uses synthetic presentation."; return null; }
        if (string.IsNullOrWhiteSpace(explicitRoot)) { error = "No explicit --local-assets root was supplied."; return null; }

        try
        {
            string root = Path.GetFullPath(explicitRoot.Trim());
            if (!Directory.Exists(root) || HasReparseTraversal(root)) { error = "The explicit local asset root is missing or traverses a reparse point."; return null; }

            string manifestPath = Path.Combine(root, ManifestFileName);
            var info = new FileInfo(manifestPath);
            if (!info.Exists || info.Length is <= 0 or > MaxManifestBytes || info.Attributes.HasFlag(FileAttributes.ReparsePoint) ||
                !LocalFileSafety.IsRegularSingleLink(manifestPath)) { error = "manifest.json must be a bounded regular single-link file."; return null; }

            LocalAssetManifest? manifest;
            using (var stream = new FileStream(manifestPath, FileMode.Open, FileAccess.Read, FileShare.Read))
            {
                byte[] json = new byte[checked((int)stream.Length)];
                stream.ReadExactly(json);
                ReadOnlyMemory<byte> jsonPayload = json.AsMemory();
                if (json.Length >= 3 && json[0] == 0xEF && json[1] == 0xBB && json[2] == 0xBF) jsonPayload = json.AsMemory(3);
                using JsonDocument document = JsonDocument.Parse(jsonPayload, new JsonDocumentOptions { MaxDepth = MaxJsonDepth });
                if (HasDuplicateProperties(document.RootElement)) { error = "manifest.json contains duplicate properties."; return null; }
                manifest = ParseManifest(document.RootElement);
            }

            if (manifest is null ||
                !string.Equals(manifest.SchemaVersion, LocalAssetManifest.CurrentSchema, StringComparison.Ordinal) ||
                !string.Equals(manifest.PresentationMode, "local-retail-preview", StringComparison.Ordinal) ||
                !manifest.NonParityClaim ||
                (manifest.Player is null && manifest.Terrain is null)) { error = "manifest.json schema, mode, non-parity marker, or roles are invalid."; return null; }

            var config = new LocalPresentationConfig { RootPath = root, Manifest = manifest };
            if (!ValidateRole(config, manifest.Player) || !ValidateRole(config, manifest.Terrain)) { error = "A local presentation role has an unsafe path, transform, format, or mesh payload."; return null; }
            return config;
        }
        catch (Exception exception) when (exception is IOException or InvalidDataException or UnauthorizedAccessException or ArgumentException or JsonException or NotSupportedException)
        {
            error = exception.Message;
            return null;
        }
    }

    private static bool ValidateRole(LocalPresentationConfig config, LocalMeshRef? role)
    {
        if (role is null) return true;
        if (!float.IsFinite(role.Scale) || role.Scale is < 0.001f or > 1000f ||
            !float.IsFinite(role.YawDegrees) || Math.Abs(role.YawDegrees) > 36000f ||
            !float.IsFinite(role.YOffsetMeters) || Math.Abs(role.YOffsetMeters) > 10000f) return false;

        string path = config.ResolveContained(role.Mesh);
        return LocalMeshSafety.ValidateFile(path).IsValid;
    }

    private string ResolveContained(string relativePath)
    {
        if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathFullyQualified(relativePath) ||
            relativePath.StartsWith("\\\\", StringComparison.Ordinal) || relativePath.StartsWith("//", StringComparison.Ordinal))
            throw new InvalidDataException("Local mesh path must be relative.");

        string fullPath = Path.GetFullPath(Path.Combine(RootPath, relativePath));
        string prefix = RootPath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        if (!fullPath.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) || HasReparseTraversal(fullPath))
            throw new InvalidDataException("Local mesh path escapes its declared asset root.");
        return fullPath;
    }

    private static bool HasReparseTraversal(string path)
    {
        string? current = Path.GetPathRoot(path);
        if (string.IsNullOrEmpty(current)) return true;
        foreach (string segment in path[current.Length..].Split([Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar], StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, segment);
            if (!File.Exists(current) && !Directory.Exists(current)) continue;
            if (File.GetAttributes(current).HasFlag(FileAttributes.ReparsePoint)) return true;
        }
        return false;
    }

    private static bool HasDuplicateProperties(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (JsonProperty property in element.EnumerateObject())
            {
                if (!names.Add(property.Name) || HasDuplicateProperties(property.Value)) return true;
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
        {
            foreach (JsonElement child in element.EnumerateArray()) if (HasDuplicateProperties(child)) return true;
        }
        return false;
    }

    private static LocalAssetManifest ParseManifest(JsonElement root)
    {
        RequireObjectWithOnly(root, "schemaVersion", "presentationMode", "nonParityClaim", "player", "terrain");
        return new LocalAssetManifest
        {
            SchemaVersion = root.GetProperty("schemaVersion").GetString() ?? string.Empty,
            PresentationMode = root.GetProperty("presentationMode").GetString(),
            NonParityClaim = root.GetProperty("nonParityClaim").GetBoolean(),
            Player = root.TryGetProperty("player", out JsonElement player) ? ParseRole(player) : null,
            Terrain = root.TryGetProperty("terrain", out JsonElement terrain) ? ParseRole(terrain) : null,
        };
    }

    private static LocalMeshRef ParseRole(JsonElement role)
    {
        RequireObjectWithOnly(role, "mesh", "scale", "yawDegrees", "yOffsetMeters");
        return new LocalMeshRef
        {
            Mesh = role.GetProperty("mesh").GetString() ?? string.Empty,
            Scale = role.TryGetProperty("scale", out JsonElement scale) ? scale.GetSingle() : 1f,
            YawDegrees = role.TryGetProperty("yawDegrees", out JsonElement yaw) ? yaw.GetSingle() : 0f,
            YOffsetMeters = role.TryGetProperty("yOffsetMeters", out JsonElement offset) ? offset.GetSingle() : 0f,
        };
    }

    private static void RequireObjectWithOnly(JsonElement element, params string[] allowed)
    {
        if (element.ValueKind != JsonValueKind.Object) throw new JsonException("Manifest object expected.");
        var names = new HashSet<string>(allowed, StringComparer.Ordinal);
        foreach (JsonProperty property in element.EnumerateObject())
            if (!names.Contains(property.Name)) throw new JsonException($"Unknown manifest property '{property.Name}'.");
    }
}

public sealed class LocalAssetManifest
{
    public const string CurrentSchema = "onslaught-rebuild-local-godot-assets-manifest.v1";
    [JsonPropertyName("schemaVersion")] public string SchemaVersion { get; init; } = string.Empty;
    [JsonPropertyName("presentationMode")] public string? PresentationMode { get; init; }
    [JsonPropertyName("nonParityClaim")] public bool NonParityClaim { get; init; }
    [JsonPropertyName("player")] public LocalMeshRef? Player { get; init; }
    [JsonPropertyName("terrain")] public LocalMeshRef? Terrain { get; init; }
}

public sealed class LocalMeshRef
{
    [JsonPropertyName("mesh")] public string Mesh { get; init; } = string.Empty;
    [JsonPropertyName("scale")] public float Scale { get; init; } = 1f;
    [JsonPropertyName("yawDegrees")] public float YawDegrees { get; init; }
    [JsonPropertyName("yOffsetMeters")] public float YOffsetMeters { get; init; }
}
