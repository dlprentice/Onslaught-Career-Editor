using System;
using System.IO;
using System.Linq;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods receipt used to say Enhanced Copy applied 16:9
/// gameplay in the app-owned copy. Name the safe copy.
/// </summary>
public class PatchBenchSafeCopyReceiptCopyHonestyTests
{
    [Test]
    public void EnhancedCopyReceiptNamesTheSafeCopyNotAnAppOwnedCopy()
    {
        SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(
            BinaryPatchPlanBuilder.CompatibilityProfileId);
        var result = new GameProfilePrepareResult(
            GameProfilePreflightService.SchemaVersion,
            DateTimeOffset.UnixEpoch,
            Mutation: true,
            SourceGameRoot: "selected-game-root",
            TargetGameRoot: @"X:\Profiles\safe-game-copy-test",
            ExecutablePath: @"X:\Profiles\safe-game-copy-test\BEA.exe",
            Entries:
            [
                new GameProfileCopiedEntry("BEA.exe", @"C:\Source\BEA.exe", @"C:\Target\BEA.exe", Directory: false),
            ],
            PatchResult: new GameProfilePatchResult(
                Requested: true,
                Success: true,
                PatchKeys: BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(preset.Id).ToArray(),
                Message: "Selected patch bytes verified on disk."),
            LaunchPlan: new GameProfileLaunchPlan(
                ExecutablePath: @"C:\Target\BEA.exe",
                WorkingDirectory: @"C:\Target",
                Arguments: [],
                CommandPreview: "\"BEA.exe\""),
            ProfilePresetId: preset.Id,
            ProfilePresetDisplayName: preset.DisplayName,
            ProfilePresetProofStatus: preset.ProofStatus,
            ProfileDefaultControllerConfiguration: preset.DefaultControllerConfiguration,
            ProfileDefaultPersistControllerConfigInOptions: preset.DefaultPersistControllerConfigInOptions,
            ProfileDefaultMouseLookSensitivity: preset.DefaultMouseLookSensitivity,
            ProfileDefaultScreenShape: preset.DefaultScreenShape,
            ProfilePresetModules: preset.Modules,
            MusicSwapResult: null,
            ManifestPath: @"C:\Target\onslaught-profile-manifest.json");

        GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt(
            result,
            copiedSavegames: false,
            controlOptionsResult: null);

        string included = string.Join(Environment.NewLine, receipt.IncludedChanges);
        Assert.That(BinaryPatchPlanBuilder.UsingFallbackSafeCopyProfileCatalog, Is.False, BinaryPatchPlanBuilder.SafeCopyProfileCatalogStatus);
        Assert.That(included, Does.Contain("16:9 gameplay and modern mouse aiming"));
        Assert.That(included, Does.Contain("in the safe copy"));
        Assert.That(included, Does.Not.Contain("app-owned"));
        Assert.That(included, Does.Not.Contain("in the app-owned copy"));
    }

    [Test]
    public void CatalogAndPlanFallbackDropTheAppOwnedCopyClaim()
    {
        string catalog = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "patches",
            "catalog",
            "safe-copy-profiles.v1.json"));
        string plan = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchPlanBuilder.cs"));
        string preflight = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        Assert.That(preflight, Does.Contain("module.ClaimBoundary"));
        Assert.That(page, Does.Contain("receipt.IncludedChanges"));
        Assert.That(catalog, Does.Not.Contain("in the app-owned copy"));
        Assert.That(plan, Does.Not.Contain("in the app-owned copy"));
        Assert.That(catalog, Does.Contain("in the safe copy"));
        Assert.That(plan, Does.Contain("in the safe copy"));
    }
}
