using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class TestFixturePathsTests
{
    [Test]
    public void ResolveRepoRoot_FindsMarkersAboveRidSpecificOutput()
    {
        string root = Path.Combine(Path.GetTempPath(), $"repo-root-{Guid.NewGuid():N}");
        string ridOutput = Path.Combine(
            root,
            "OnslaughtCareerEditor.UiTests",
            "bin",
            "Debug",
            "net10.0-windows",
            "win-x64");
        Directory.CreateDirectory(ridOutput);
        File.WriteAllText(Path.Combine(root, "package.json"), "{}");
        Directory.CreateDirectory(Path.Combine(root, "OnslaughtCareerEditor.WinUI"));
        Directory.CreateDirectory(Path.Combine(root, "OnslaughtCareerEditor.UiTests"));

        try
        {
            Assert.That(
                TestFixturePaths.ResolveRepoRoot(ridOutput),
                Is.EqualTo(Path.GetFullPath(root)));
        }
        finally
        {
            Directory.Delete(root, recursive: true);
        }
    }

    [Test]
    public void ResolveRepoRoot_RejectsTreeWithoutRepositoryMarkers()
    {
        string root = Path.Combine(Path.GetTempPath(), $"repo-root-missing-{Guid.NewGuid():N}");
        Directory.CreateDirectory(root);

        try
        {
            Assert.Throws<DirectoryNotFoundException>(() =>
                TestFixturePaths.ResolveRepoRoot(root));
        }
        finally
        {
            Directory.Delete(root, recursive: true);
        }
    }
}
