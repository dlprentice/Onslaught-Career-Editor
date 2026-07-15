namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetOwnedPathGuard
{
    private const string EvidenceRootName = "winui-media-asset-native-workflow";

    internal static string RequireEvidenceRoot(string repoRoot, string evidenceRoot)
    {
        string repo = Path.GetFullPath(repoRoot);
        string localLab = Path.Combine(repo, "local-lab");
        string expected = Path.Combine(localLab, EvidenceRootName);
        string actual = Path.GetFullPath(evidenceRoot);
        if (!string.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException(
                "Media/Asset evidence root is not the exact repository-owned local-lab path.");
        }

        RequireNoReparsePoint(localLab, "repository local-lab");
        RequireNoReparsePoint(actual, "Media/Asset evidence root");
        return actual;
    }

    internal static string RequireDirectChild(string ownedRoot, string childPath)
    {
        string root = Path.GetFullPath(ownedRoot);
        string child = Path.GetFullPath(childPath);
        if (!string.Equals(Path.GetDirectoryName(child), root, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException(
                "Media/Asset owned path is not a direct child of its evidence root.");
        }

        RequireNoReparsePoint(root, "Media/Asset evidence root");
        RequireNoReparsePoint(child, "Media/Asset owned child");
        return child;
    }

    internal static void RequireReparseFreeTree(string rootPath)
    {
        string root = Path.GetFullPath(rootPath);
        RequireNoReparsePoint(root, "Media/Asset owned tree root");
        if (!Directory.Exists(root))
        {
            return;
        }

        foreach (string entry in Directory.EnumerateFileSystemEntries(root, "*", SearchOption.AllDirectories))
        {
            RequireNoReparsePoint(entry, "Media/Asset owned tree entry");
        }
    }

    private static void RequireNoReparsePoint(string path, string label)
    {
        if (!Directory.Exists(path) && !File.Exists(path))
        {
            return;
        }

        if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
        {
            throw new InvalidOperationException($"{label} must not be a reparse point: {path}");
        }
    }
}
