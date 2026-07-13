using System.Text.Json;
using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[TestFixture]
public sealed class PatchBenchPlayerLabCurationTests
{
    private static readonly XNamespace Xaml = "http://schemas.microsoft.com/winfx/2006/xaml";

    [Test]
    public void NormalPlayerSurface_StatesExactCompatibilityAndOptInModBoundariesBeforeLab()
    {
        string xamlText = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        XDocument document = XDocument.Parse(xamlText);
        XElement lab = FindNamedElement(document, "PatchBenchLabExpander");
        string normalText = xamlText[..xamlText.IndexOf("PatchBenchLabExpander", StringComparison.Ordinal)];
        XElement markerButton = FindAutomationElement(document, "PatchBenchAddVersionMarkerButton");
        XElement playerModsGrid = markerButton.Parent!;

        Assert.Multiple(() =>
        {
            Assert.That(lab.Name.LocalName, Is.EqualTo("Expander"));
            Assert.That((string?)lab.Attribute("IsExpanded"), Is.EqualTo("False"));
            Assert.That(xamlText, Does.Contain("Every safe game copy includes two required compatibility changes: allow non-4:3 display-mode candidates and prefer windowed startup."));
            Assert.That(xamlText, Does.Contain("This does not prove widescreen field-of-view parity or guarantee windowed behavior on every PC."));
            Assert.That(xamlText, Does.Contain("Both player mods start off and change only the copied executable."));
            Assert.That(xamlText, Does.Contain("does not edit your save, award Goodies, or make an unlock persistent"));
            Assert.That(xamlText, Does.Contain("does not prove every Goodies entry or model/FMV playback"));
            Assert.That(xamlText, Does.Contain("Select legacy graphics-default Lab recipe; visible improvement is unproven"));
            Assert.That(xamlText, Does.Contain("Select retained legacy Enhanced Profile Preview Lab recipe"));
            Assert.That(xamlText, Does.Contain("Select experimental Debug Camera Preview Lab research recipe"));
            Assert.That(xamlText, Does.Contain("PatchBenchPlayerModsSelectionStatus"));
            Assert.That(normalText, Does.Not.Contain("recover by restoring the app-owned backup"));
            Assert.That(
                xamlText.IndexOf("PatchBenchAddVersionMarkerButton", StringComparison.Ordinal),
                Is.LessThan(xamlText.IndexOf("PatchBenchLabExpander", StringComparison.Ordinal)));
            Assert.That(
                xamlText.IndexOf("PatchBenchAddGoodiesPreviewButton", StringComparison.Ordinal),
                Is.LessThan(xamlText.IndexOf("PatchBenchLabExpander", StringComparison.Ordinal)));
            Assert.That(
                xamlText.IndexOf("PatchBenchProfileCatalogStatus", StringComparison.Ordinal),
                Is.GreaterThan(xamlText.IndexOf("PatchBenchLabExpander", StringComparison.Ordinal)));
            Assert.That(
                xamlText.IndexOf("PatchBenchSelectedProfileDetailsExpander", StringComparison.Ordinal),
                Is.GreaterThan(xamlText.IndexOf("PatchBenchLabExpander", StringComparison.Ordinal)));
            Assert.That(
                playerModsGrid.Elements().Single(element => element.Name.LocalName == "Grid.RowDefinitions").Elements().Count(),
                Is.EqualTo(2));
            AssertAutomationGridCell(document, "PatchBenchAddVersionMarkerButton", "0", "0");
            AssertAutomationGridCell(document, "PatchBenchClearVersionMarkerButton", "0", "1");
            AssertAutomationGridCell(document, "PatchBenchAddGoodiesPreviewButton", "1", "0");
            AssertAutomationGridCell(document, "PatchBenchClearGoodiesPreviewButton", "1", "1");
        });
    }

    [Test]
    public void PlayerModStatus_ReportsEachExactOptInCombination()
    {
        string helper = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Helpers", "PatchBenchSelectedProfileText.cs");
        Assert.Multiple(() =>
        {
            Assert.That(helper, Does.Contain("BuildPlayerModsStatus(bool hasPatchedMarker, bool hasGoodiesPreview)"));
            Assert.That(helper, Does.Contain("Player mods selected: none."));
            Assert.That(helper, Does.Contain("Player mods selected: PATCHED identity marker."));
            Assert.That(helper, Does.Contain("Player mods selected: Goodies wall preview."));
            Assert.That(helper, Does.Contain("Player mods selected: PATCHED identity marker and Goodies wall preview."));
        });
    }

    [Test]
    public void Lab_IsStructuredAndRetainsLegacyRecipesAndDetailedPatchRows()
    {
        XDocument document = XDocument.Parse(
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));
        XElement lab = FindNamedElement(document, "PatchBenchLabExpander");
        string labText = string.Join(
            "\n",
            lab.Descendants().Select(element => (string?)element.Attribute("Text")).Where(text => text is not null));

        Assert.Multiple(() =>
        {
            Assert.That(labText, Does.Contain("Legacy and research recipes"));
            Assert.That(labText, Does.Contain("Visual and executable experiments"));
            Assert.That(
                (string?)FindNamedElement(lab, "PatchBenchLabLaunchControlExpander").Attribute("Header"),
                Is.EqualTo("Launch and control diagnostics"));
            Assert.That(
                (string?)FindNamedElement(lab, "PatchBenchLabOnlineResearchExpander").Attribute("Header"),
                Is.EqualTo("Online research"));
            Assert.That(
                (string?)FindNamedElement(lab, "PatchBenchLabMusicExperimentsExpander").Attribute("Header"),
                Is.EqualTo("Music experiments"));
            Assert.That(
                (string?)FindNamedElement(lab, "PatchBenchLabBeaDiagnosticsExpander").Attribute("Header"),
                Is.EqualTo("BEA.exe-only diagnostics"));
            Assert.That(FindNamedElement(lab, "PatchBenchStableDefaultsButton"), Is.Not.Null);
            Assert.That(FindNamedElement(lab, "PatchBenchEnhancedPreviewProfileButton"), Is.Not.Null);
            Assert.That(FindNamedElement(lab, "PatchBenchDebugCameraPreviewProfileButton"), Is.Not.Null);
            Assert.That(FindNamedElement(lab, "PatchBenchPatchRows"), Is.Not.Null);
            AssertGridCell(lab, "PatchBenchStableDefaultsButton", "0", "0");
            AssertGridCell(lab, "PatchBenchEnhancedPreviewProfileButton", "0", "1");
            AssertGridCell(lab, "PatchBenchModernGraphicsPresetButton", "1", "0");
            AssertGridCell(lab, "PatchBenchDebugCameraPreviewProfileButton", "1", "1");
            Assert.That(
                labText.IndexOf("Visual and executable experiments", StringComparison.Ordinal),
                Is.LessThan(labText.IndexOf("Frontend margin color", StringComparison.Ordinal)));
            foreach (string heading in new[]
                     {
                         "Legacy and research recipes",
                         "Visual and executable experiments",
                     })
            {
                XElement headingElement = lab.Descendants().Single(element => (string?)element.Attribute("Text") == heading);
                Assert.That((string?)headingElement.Attribute("AutomationProperties.HeadingLevel"), Is.EqualTo("Level2"));
            }
        });
    }

    [Test]
    public void ProfileCatalog_RetainsAllLegacyIdsAndExactCompatibilityBase()
    {
        using JsonDocument catalog = JsonDocument.Parse(
            ReadRepoFile("patches", "catalog", "safe-copy-profiles.v1.json"));
        Dictionary<string, JsonElement> profiles = catalog.RootElement
            .GetProperty("profiles")
            .EnumerateArray()
            .ToDictionary(profile => profile.GetProperty("id").GetString()!, StringComparer.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(profiles.Keys, Is.SupersetOf(new[]
            {
                "compatibility-copy",
                "recommended-safe-copy",
                "enhanced-edition-preview",
                "debug-camera-preview",
                "custom",
            }));
            Assert.That(
                profiles["compatibility-copy"].GetProperty("patch_keys").EnumerateArray().Select(value => value.GetString()),
                Is.EqualTo(new[] { "resolution_gate", "force_windowed" }));
            Assert.That(
                profiles["compatibility-copy"].GetProperty("patch_keys").EnumerateArray().Select(value => value.GetString()),
                Does.Not.Contain("version_overlay_use_patched_format_pointer"));
            Assert.That(
                profiles["compatibility-copy"].GetProperty("patch_keys").EnumerateArray().Select(value => value.GetString()),
                Does.Not.Contain("goodies_gallery_display_unlock"));
        });
    }

    private static XElement FindNamedElement(XContainer container, string name)
    {
        return container.Descendants()
            .Single(element => string.Equals((string?)element.Attribute(Xaml + "Name"), name, StringComparison.Ordinal));
    }

    private static XElement FindAutomationElement(XContainer container, string automationId)
    {
        return container.Descendants().Single(
            element => string.Equals(
                (string?)element.Attribute("AutomationProperties.AutomationId"),
                automationId,
                StringComparison.Ordinal));
    }

    private static void AssertGridCell(XContainer container, string name, string row, string column)
    {
        XElement element = FindNamedElement(container, name);
        Assert.That((string?)element.Attribute("Grid.Row"), Is.EqualTo(row), $"{name} row");
        Assert.That((string?)element.Attribute("Grid.Column"), Is.EqualTo(column), $"{name} column");
    }

    private static void AssertAutomationGridCell(XContainer container, string automationId, string row, string column)
    {
        XElement element = FindAutomationElement(container, automationId);
        Assert.That((string?)element.Attribute("Grid.Row"), Is.EqualTo(row), $"{automationId} row");
        Assert.That((string?)element.Attribute("Grid.Column"), Is.EqualTo(column), $"{automationId} column");
    }

    private static string ReadRepoFile(params string[] parts)
    {
        string root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
        return File.ReadAllText(Path.Combine(new[] { root }.Concat(parts).ToArray()));
    }
}
