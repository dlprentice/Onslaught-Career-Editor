namespace OnslaughtCareerEditor.UiTests;

internal static class SaveLabOwnedPathGuard
{
    private const string EvidenceRootName = "winui-save-lab-native-workflow";

    internal static string RequireEvidenceRoot(string repoRoot, string evidenceRoot)
    {
        string repo = Path.GetFullPath(repoRoot);
        string localLab = Path.Combine(repo, "local-lab");
        string expected = Path.Combine(localLab, EvidenceRootName);
        string actual = Path.GetFullPath(evidenceRoot);
        if (!string.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("Save Lab evidence root is not the exact repository-owned local-lab path.");
        }

        RequireNoReparsePoint(localLab, "repository local-lab");
        RequireNoReparsePoint(actual, "Save Lab evidence root");
        return actual;
    }

    internal static string RequireDirectChild(string ownedRoot, string childPath)
    {
        string root = Path.GetFullPath(ownedRoot);
        string child = Path.GetFullPath(childPath);
        if (!string.Equals(Path.GetDirectoryName(child), root, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("Save Lab owned path is not a direct child of its evidence root.");
        }

        RequireNoReparsePoint(root, "Save Lab evidence root");
        RequireNoReparsePoint(child, "Save Lab owned child");
        return child;
    }

    private static void RequireNoReparsePoint(string path, string label)
    {
        if (!Directory.Exists(path) && !File.Exists(path))
        {
            return;
        }

        FileAttributes attributes = File.GetAttributes(path);
        if ((attributes & FileAttributes.ReparsePoint) != 0)
        {
            throw new InvalidOperationException($"{label} must not be a reparse point: {path}");
        }
    }
}
