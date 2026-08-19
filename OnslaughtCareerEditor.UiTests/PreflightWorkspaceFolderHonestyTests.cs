using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Advanced copy used to require the destination under an app-owned
/// workspace root. Name the folder, not a root.
/// </summary>
public class PreflightWorkspaceFolderHonestyTests
{
    [Test]
    public void AWorkspaceFileOutsideTheFolderNamesTheFolderNotARoot()
    {
        string workspace = Path.Combine(Path.GetTempPath(), $"preflight-ws-{Guid.NewGuid():N}");
        Directory.CreateDirectory(workspace);
        string outside = Path.Combine(Path.GetTempPath(), $"preflight-out-{Guid.NewGuid():N}", "BEA.exe");
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                    outside,
                    workspace,
                    "BEA.exe"));

            Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.WorkspaceFileMustStayInside));
            Assert.That(error.Message, Is.EqualTo("The workspace file must stay inside the app-owned profile folder."));
            Assert.That(error.Message, Does.Contain("profile folder"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(error.Message, Does.Not.Contain(workspace));
            Assert.That(error.Message, Does.Not.Contain(outside));
            Assert.That(error.Message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(workspace, recursive: true);
        }
    }

    [Test]
    public void TheSourceDoesNotKeepTheOldRootSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("WorkspaceFileMustStayInside"));
        Assert.That(source, Does.Not.Contain("Workspace destination must stay under the app-owned workspace root."));
        Assert.That(source, Does.Contain("The workspace file must stay inside the app-owned profile folder."));
    }
}
