using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchLaunchTextTests
{
    private static readonly string[] ReflectedLaunchTextSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextResult.cs",
    ];

    [Test]
    public void LaunchConfirmationNamesTheCopyNotThePath()
    {
        string working = Path.Combine(
            "C:" + Path.DirectorySeparatorChar + "Users",
            "player",
            "AppData",
            "GameProfiles",
            "windowed-copy");
        Type helper = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchLaunchText",
            ReflectedLaunchTextSourcePaths);
        string question = (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            helper,
            "BuildLaunchConfirmation",
            working,
            "Launch modifiers: none.");

        Assert.That(question, Does.Contain("windowed-copy"));
        Assert.That(question, Does.Contain("Launch modifiers: none."));
        Assert.That(question, Does.Contain("Steam/game install stays unchanged"));
        Assert.That(question, Does.Not.Contain(working));
        Assert.That(question, Does.Not.Contain(":\\"));
        Assert.That(question, Does.Not.Contain("Users"));
        Assert.That(question, Does.Not.Contain("GameProfiles"));
    }

    [Test]
    public void MissingLaunchPlanNamesTheNextStep()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchLaunchText.cs"));

        Assert.That(source, Does.Contain("Create a new safe copy before Play."));
        Assert.That(source, Does.Not.Contain("Launch plan is not ready."));
        Assert.That(source, Does.Not.Contain("Safe copy launch option needs review."));
    }
}
