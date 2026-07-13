// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using System.Text.Json.Serialization;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Optional local-only retail mesh preview configuration.
/// Missing assets fall back to procedural synthetics. Smoke mode never uses this.
/// </summary>
public sealed class LocalPresentationConfig
{
    public const string EnvVarName = "ONSLAUGHT_REBUILD_GODOT_ASSETS";
    public const string ManifestFileName = "manifest.json";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    public required string RootPath { get; init; }

    public required LocalAssetManifest Manifest { get; init; }

    public bool HasPlayerMesh => !string.IsNullOrWhiteSpace(Manifest.Player?.Mesh);

    public bool HasTerrainMesh => !string.IsNullOrWhiteSpace(Manifest.Terrain?.Mesh);

    public LocalMeshRef? Player => Manifest.Player;

    public LocalMeshRef? Terrain => Manifest.Terrain;

    public string PlayerMeshPath => ResolveRelative(Manifest.Player!.Mesh!);

    public string? TerrainMeshPath =>
        HasTerrainMesh ? ResolveRelative(Manifest.Terrain!.Mesh!) : null;

    public static LocalPresentationConfig? TryResolve(string? explicitRoot, bool smokeMode)
    {
        if (smokeMode)
        {
            return null;
        }

        string? root = FirstNonEmpty(
            explicitRoot,
            Environment.GetEnvironmentVariable(EnvVarName));

        if (string.IsNullOrWhiteSpace(root))
        {
            string? repoGuess = GuessRepoRoot();
            if (!string.IsNullOrWhiteSpace(repoGuess))
            {
                root = Path.Combine(repoGuess, "local-lab", "rebuild-godot");
            }
        }

        if (string.IsNullOrWhiteSpace(root) || !Directory.Exists(root))
        {
            return null;
        }

        string manifestPath = Path.Combine(root, ManifestFileName);
        if (!File.Exists(manifestPath))
        {
            return null;
        }

        string json = File.ReadAllText(manifestPath);
        LocalAssetManifest? manifest = JsonSerializer.Deserialize<LocalAssetManifest>(json, JsonOptions);
        if (manifest is null ||
            !string.Equals(
                manifest.SchemaVersion,
                "onslaught-rebuild-local-godot-assets-manifest.v1",
                StringComparison.Ordinal))
        {
            return null;
        }

        var config = new LocalPresentationConfig
        {
            RootPath = Path.GetFullPath(root),
            Manifest = manifest,
        };

        if (config.HasPlayerMesh && !File.Exists(config.PlayerMeshPath))
        {
            return null;
        }

        if (config.HasTerrainMesh && !File.Exists(config.TerrainMeshPath!))
        {
            return null;
        }

        if (!config.HasPlayerMesh && !config.HasTerrainMesh)
        {
            return null;
        }

        return config;
    }

    private string ResolveRelative(string relativePath)
    {
        string combined = Path.IsPathRooted(relativePath)
            ? relativePath
            : Path.Combine(RootPath, relativePath);
        return Path.GetFullPath(combined);
    }

    private static string? FirstNonEmpty(params string?[] values)
    {
        foreach (string? value in values)
        {
            if (!string.IsNullOrWhiteSpace(value))
            {
                return value.Trim();
            }
        }

        return null;
    }

    private static string? GuessRepoRoot()
    {
        string? dir = Path.GetDirectoryName(Path.GetFullPath(Godot.OS.GetExecutablePath()));
        for (int i = 0; i < 8 && !string.IsNullOrWhiteSpace(dir); i++)
        {
            if (File.Exists(Path.Combine(dir, "package.json")) &&
                Directory.Exists(Path.Combine(dir, "rebuild")))
            {
                return dir;
            }

            dir = Path.GetDirectoryName(dir);
        }

        string cwd = Directory.GetCurrentDirectory();
        if (File.Exists(Path.Combine(cwd, "package.json")) &&
            Directory.Exists(Path.Combine(cwd, "rebuild")))
        {
            return cwd;
        }

        return null;
    }
}

public sealed class LocalAssetManifest
{
    [JsonPropertyName("schemaVersion")]
    public string SchemaVersion { get; init; } = string.Empty;

    [JsonPropertyName("presentationMode")]
    public string? PresentationMode { get; init; }

    [JsonPropertyName("nonParityClaim")]
    public bool NonParityClaim { get; init; } = true;

    [JsonPropertyName("player")]
    public LocalMeshRef? Player { get; init; }

    [JsonPropertyName("terrain")]
    public LocalMeshRef? Terrain { get; init; }
}

public sealed class LocalMeshRef
{
    [JsonPropertyName("mesh")]
    public string? Mesh { get; init; }

    [JsonPropertyName("scale")]
    public float Scale { get; init; } = 1f;

    [JsonPropertyName("yawDegrees")]
    public float YawDegrees { get; init; }

    [JsonPropertyName("yOffsetMeters")]
    public float YOffsetMeters { get; init; }
}
