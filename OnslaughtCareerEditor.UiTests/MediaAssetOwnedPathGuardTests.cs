using System.Diagnostics;

namespace OnslaughtCareerEditor.UiTests;

public class MediaAssetOwnedPathGuardTests
{
    [Test]
    public void RequireEvidenceRoot_AcceptsOnlyExactRepositoryLocalLabPath()
    {
        string repo = CreateRepoRoot();
        string tempRoot = Path.GetDirectoryName(repo)!;
        try
        {
            string evidence = Path.Combine(repo, "local-lab", "winui-media-asset-native-workflow");
            Directory.CreateDirectory(evidence);

            Assert.Multiple(() =>
            {
                Assert.That(
                    MediaAssetOwnedPathGuard.RequireEvidenceRoot(repo, evidence),
                    Is.EqualTo(Path.GetFullPath(evidence)));
                Assert.That(
                    () => MediaAssetOwnedPathGuard.RequireEvidenceRoot(
                        repo,
                        Path.Combine(repo, "local-lab", "other")),
                    Throws.TypeOf<InvalidOperationException>());
            });
        }
        finally
        {
            Directory.Delete(tempRoot, recursive: true);
        }
    }

    [Test]
    public void RequireReparseFreeTree_RejectsNestedJunction()
    {
        string repo = CreateRepoRoot();
        string tempRoot = Path.GetDirectoryName(repo)!;
        string evidence = Path.Combine(repo, "local-lab", "winui-media-asset-native-workflow");
        string target = Path.Combine(repo, "local-lab", "target");
        string nested = Path.Combine(evidence, "nested");
        Directory.CreateDirectory(evidence);
        Directory.CreateDirectory(target);
        CreateJunction(nested, target);
        try
        {
            Assert.That(
                () => MediaAssetOwnedPathGuard.RequireReparseFreeTree(evidence),
                Throws.TypeOf<InvalidOperationException>().With.Message.Contains("reparse point"));
        }
        finally
        {
            Directory.Delete(nested, recursive: false);
            Directory.Delete(tempRoot, recursive: true);
        }
    }

    private static string CreateRepoRoot()
    {
        string repo = Path.Combine(
            Path.GetTempPath(),
            $"media-asset-owned-root-{Guid.NewGuid():N}",
            "repo");
        Directory.CreateDirectory(Path.Combine(repo, "local-lab"));
        return repo;
    }

    private static void CreateJunction(string link, string target)
    {
        using Process process = Process.Start(new ProcessStartInfo("cmd.exe")
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            ArgumentList = { "/d", "/c", "mklink", "/J", link, target },
        })!;
        string stdout = process.StandardOutput.ReadToEnd();
        string stderr = process.StandardError.ReadToEnd();
        Assert.That(process.WaitForExit(10_000), Is.True, "mklink junction creation timed out.");
        Assert.That(process.ExitCode, Is.Zero, stderr + stdout);
    }
}
