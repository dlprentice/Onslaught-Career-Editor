using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Copying with no export selected used to say only that no file is selected.
/// Name the next step.
/// </summary>
public class AssetExportSelectHonestyTests
{
    [Test]
    public void CopyingWithNoExportNamesTheNextStep()
    {
        string sentence = AssetLibraryPageText.NoExportSelectedStatus;

        Assert.That(sentence, Does.Contain("choose"));
        Assert.That(sentence, Does.Contain("export"));
        Assert.That(sentence, Does.Not.Contain("no file selected"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
    }
}
