using System.Security.Cryptography;
using System.Text;

namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetNativeApplicationPayload
{
    internal static readonly IReadOnlyList<string> RelativePaths =
    [
        "App.xbf",
        "MainWindow.xbf",
        "OnslaughtCareerEditor.AppCore.dll",
        "OnslaughtCareerEditor.WinUI.deps.json",
        "OnslaughtCareerEditor.WinUI.dll",
        "OnslaughtCareerEditor.WinUI.exe",
        "OnslaughtCareerEditor.WinUI.pri",
        "OnslaughtCareerEditor.WinUI.runtimeconfig.json",
        "Pages/AboutPage.xbf",
        "Pages/AssetLibraryPage.xbf",
        "Pages/BinaryPatchesPage.xbf",
        "Pages/HomePage.xbf",
        "Pages/LorePage.xbf",
        "Pages/MediaPage.xbf",
        "Pages/SavesPage.xbf",
        "Pages/SettingsPage.xbf",
        "patches/catalog/patches.v2.json",
        "patches/catalog/safe-copy-profiles.v1.json",
    ];

    internal static string Compute(string applicationRoot)
    {
        string root = Path.GetFullPath(applicationRoot);
        if (!Directory.Exists(root))
        {
            throw new InvalidOperationException("The native WinUI application payload root is missing.");
        }
        RequireNotReparsePoint(root);

        var receipt = new StringBuilder();
        foreach (string relativePath in RelativePaths)
        {
            string fullPath = ResolvePayloadFile(root, relativePath);
            var info = new FileInfo(fullPath);
            long length = info.Length;
            string hash = HashFile(fullPath);
            info.Refresh();
            if (!info.Exists || info.Length != length)
            {
                throw new InvalidOperationException(
                    $"The native WinUI application payload changed while hashing: {relativePath}");
            }
            receipt.Append(relativePath)
                .Append('\0')
                .Append(length)
                .Append('\0')
                .Append(hash)
                .Append('\n');
        }

        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(receipt.ToString())));
    }

    private static string ResolvePayloadFile(string root, string relativePath)
    {
        if (Path.IsPathRooted(relativePath) ||
            relativePath.Contains('\\') ||
            relativePath.Split('/').Any(segment => segment is "" or "." or ".."))
        {
            throw new InvalidOperationException("Native WinUI payload paths must be normalized relative paths.");
        }

        string current = root;
        foreach (string segment in relativePath.Split('/'))
        {
            current = Path.Combine(current, segment);
            if (!File.Exists(current) && !Directory.Exists(current))
            {
                throw new InvalidOperationException($"The native WinUI application payload is missing: {relativePath}");
            }
            RequireNotReparsePoint(current);
        }

        string resolved = Path.GetFullPath(current);
        string confined = Path.GetRelativePath(root, resolved);
        if (confined == ".." || confined.StartsWith($"..{Path.DirectorySeparatorChar}", StringComparison.Ordinal))
        {
            throw new InvalidOperationException($"The native WinUI application payload escaped its root: {relativePath}");
        }
        if (!File.Exists(resolved))
        {
            throw new InvalidOperationException($"The native WinUI application payload file is missing: {relativePath}");
        }
        return resolved;
    }

    private static void RequireNotReparsePoint(string path)
    {
        if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
        {
            throw new InvalidOperationException($"The native WinUI application payload contains a reparse point: {path}");
        }
    }

    private static string HashFile(string path)
    {
        using FileStream stream = new(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        return Convert.ToHexString(SHA256.HashData(stream));
    }
}
