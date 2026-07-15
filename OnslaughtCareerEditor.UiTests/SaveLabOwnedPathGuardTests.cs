using System.Diagnostics;

namespace OnslaughtCareerEditor.UiTests;

public class SaveLabOwnedPathGuardTests
{
    [Test]
    public void RequireEvidenceRoot_AcceptsExactNonReparseRepositoryPath()
    {
        string repo = CreateRepoRoot();
        string tempRoot = Path.GetDirectoryName(repo)!;
        try
        {
            string evidence = Path.Combine(repo, "local-lab", "winui-save-lab-native-workflow");
            Directory.CreateDirectory(evidence);

            Assert.That(SaveLabOwnedPathGuard.RequireEvidenceRoot(repo, evidence), Is.EqualTo(Path.GetFullPath(evidence)));
        }
        finally
        {
            Directory.Delete(tempRoot, recursive: true);
        }
    }

    [Test]
    public void RequireEvidenceRoot_RejectsJunctionEvenWhenTargetRemainsInsideLocalLab()
    {
        string repo = CreateRepoRoot();
        string tempRoot = Path.GetDirectoryName(repo)!;
        string localLab = Path.Combine(repo, "local-lab");
        string target = Path.Combine(localLab, "another-owned-root");
        string evidence = Path.Combine(localLab, "winui-save-lab-native-workflow");
        Directory.CreateDirectory(target);
        CreateJunction(evidence, target);
        try
        {
            Assert.That(
                () => SaveLabOwnedPathGuard.RequireEvidenceRoot(repo, evidence),
                Throws.TypeOf<InvalidOperationException>().With.Message.Contains("reparse point"));
        }
        finally
        {
            Directory.Delete(evidence, recursive: false);
            Directory.Delete(tempRoot, recursive: true);
        }
    }

    private static string CreateRepoRoot()
    {
        string repo = Path.Combine(Path.GetTempPath(), $"save-lab-owned-root-{Guid.NewGuid():N}", "repo");
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
