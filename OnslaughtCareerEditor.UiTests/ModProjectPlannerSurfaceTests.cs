using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class ModProjectPlannerSurfaceTests
{
    private static string ReadWinUiFile(params string[] parts)
    {
        string path = Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            Path.Combine(parts));
        return File.ReadAllText(path);
    }

    [Test]
    public void PlannerSurfaceNamesAPlanReceiptAndItsMetadataBoundary()
    {
        string xaml = ReadWinUiFile("Pages", "AssetLibraryPage.xaml");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("Mod project manifest planner"));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetModProjectSummary\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetModProjectProvenance\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetModProjectItemsList\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetAddCurrentToModProjectButton\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetModProjectOutputFileTextBox\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetExportModProjectPlanButton\""));
            Assert.That(xaml, Does.Contain("not an asset pack"));
            Assert.That(xaml, Does.Contain("not an installer"));
            Assert.That(xaml, Does.Contain("not a compatibility guarantee"));
        });
    }

    [Test]
    public void PlannerUsesBoundedAppCorePlanningAndGuardedExport()
    {
        string code = ReadWinUiFile("Pages", "AssetLibraryPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("ModProjectPlannerService.MaxSelectedAssets"));
            Assert.That(code, Does.Contain("ModProjectPlannerService.BuildPlan"));
            Assert.That(code, Does.Contain("ModProjectPlannerService.Export"));
            Assert.That(code, Does.Contain("new ModProjectSelectionEntry(\"texture\""));
            Assert.That(code, Does.Contain("new ModProjectSelectionEntry(\"mesh\""));
            Assert.That(code, Does.Contain("new ModProjectSelectionEntry(\"embedded-mesh\""));
            Assert.That(code, Does.Contain("new ModProjectSelectionEntry(\"goodie\""));
        });
    }

    [Test]
    public void PlannerOffersAnExactJsonSavePathAndOptionalTsv()
    {
        string xaml = ReadWinUiFile("Pages", "AssetLibraryPage.xaml");
        string picker = ReadWinUiFile("Helpers", "PickerInterop.cs");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetModProjectIncludeTsvCheckBox\""));
            Assert.That(xaml, Does.Contain("Optional TSV beside the JSON receipt"));
            Assert.That(picker, Does.Contain("FileSavePicker"));
            Assert.That(picker, Does.Contain("PickSaveFileAsync"));
        });
    }
}
