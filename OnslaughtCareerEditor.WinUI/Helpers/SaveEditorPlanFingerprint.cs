using System.Security.Cryptography;
using System.Text;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class SaveEditorPlanFingerprint
{
    public static string Build(SavePatchRequest request)
    {
        StringBuilder canonical = new();
        Append(canonical, NormalizePath(request.InputPath));
        Append(canonical, NormalizePath(request.OutputPath));
        Append(canonical, request.Rank ?? string.Empty);
        Append(canonical, request.UseNewGoodiesInstead ? "1" : "0");
        Append(canonical, request.GlobalKillCount.ToString(System.Globalization.CultureInfo.InvariantCulture));
        Append(canonical, request.PatchNodes ? "1" : "0");
        Append(canonical, request.PatchLinks ? "1" : "0");
        Append(canonical, request.PatchGoodies ? "1" : "0");
        Append(canonical, request.PatchKills ? "1" : "0");

        foreach ((int key, string value) in (request.LevelRanks ?? new Dictionary<int, string>()).OrderBy(pair => pair.Key))
        {
            Append(canonical, key.ToString(System.Globalization.CultureInfo.InvariantCulture));
            Append(canonical, value ?? string.Empty);
        }

        Append(canonical, "category-kills");
        foreach ((int key, int value) in (request.PerCategoryKills ?? new Dictionary<int, int>()).OrderBy(pair => pair.Key))
        {
            Append(canonical, key.ToString(System.Globalization.CultureInfo.InvariantCulture));
            Append(canonical, value.ToString(System.Globalization.CultureInfo.InvariantCulture));
        }

        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(canonical.ToString())));
    }

    public static bool IsInsideDirectory(string candidate, string root)
    {
        try
        {
            string normalizedRoot = Path.GetFullPath(root.Trim()).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string normalizedCandidate = Path.GetFullPath(candidate.Trim());
            string prefix = normalizedRoot + Path.DirectorySeparatorChar;
            return normalizedCandidate.StartsWith(prefix, StringComparison.OrdinalIgnoreCase);
        }
        catch
        {
            return false;
        }
    }

    private static string NormalizePath(string? path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return string.Empty;
        }

        try
        {
            return Path.GetFullPath(path.Trim()).ToUpperInvariant();
        }
        catch
        {
            return path.Trim().ToUpperInvariant();
        }
    }

    private static void Append(StringBuilder builder, string value)
    {
        builder.Append(value.Length)
            .Append(':')
            .Append(value);
    }
}
