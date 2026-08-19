using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to call the safe copy an app-owned folder.
/// Name the copy folder.
/// </summary>
public class PatchBenchSafeCopyFolderHonestyTests
{
    [Test]
    public void WhatGetsTouchedNamesTheCopyFolderNotAnAppOwnedFolder()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));

        Assert.That(page, Does.Not.Contain("Safe game copy: app-owned folder."));
        Assert.That(page, Does.Contain("Safe game copy: this copy folder. This is what Play runs."));
        Assert.That(page, Does.Contain("copy folder"));
    }
}
