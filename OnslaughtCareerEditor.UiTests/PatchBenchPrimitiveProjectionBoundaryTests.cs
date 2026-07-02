using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchPrimitiveProjectionBoundaryTests
{
    private static readonly BoundaryFileEntry[] PatchBenchBoundaryFiles =
    [
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchChoiceVisualState.cs", BoundaryProfile.ChoiceVisualBinding),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs", BoundaryProfile.LaunchReadiness),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs", BoundaryProfile.LaunchReadiness),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchMenuColorSelectionText.cs", BoundaryProfile.MenuColorSelection),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs", BoundaryProfile.OnlineReadiness),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchPatchGroups.cs", BoundaryProfile.PatchGroups),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs", BoundaryProfile.ReceiptSourceProjection),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs", BoundaryProfile.SafeCopyOutcome),
        new("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSelectedProfileText.cs", BoundaryProfile.SelectedProfile),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextResult.cs", BoundaryProfile.LaunchReadiness),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextState.cs", BoundaryProfile.LaunchReadiness),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchMenuColorSelectionKind.cs", BoundaryProfile.MenuColorSelection),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs", BoundaryProfile.OnlineReadiness),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs", BoundaryProfile.OnlineReadiness),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs", BoundaryProfile.SafeCopyOutcome),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs", BoundaryProfile.SafeCopyOutcome),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs", BoundaryProfile.SafeCopyOutcome),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyReceiptTextState.cs", BoundaryProfile.ReceiptSourceProjection),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedChoiceState.cs", BoundaryProfile.ChoiceVisualBinding),
        new("OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedProfileTextState.cs", BoundaryProfile.SelectedProfile),
    ];

    [Test]
    public void PatchBenchPresentationFiles_MustBeExplicitlyProfiledBeforeAddingReceiptOrSourceHelpers()
    {
        string[] actualFiles = GetPatchBenchPresentationFiles()
            .Select(ToRepoRelativePath)
            .ToArray();

        AssertDiscoveredFilesAreProfiled(actualFiles, BuildBoundaryProfileMap());
    }

    [Test]
    public void PatchBenchPresentationFiles_FollowTheirBoundaryProfiles()
    {
        IReadOnlyDictionary<string, BoundaryProfile> profiles = BuildBoundaryProfileMap();
        Dictionary<string, string> sourcesByPath = profiles.ToDictionary(
            pair => pair.Key,
            pair => ReadRepoFile(pair.Key),
            StringComparer.OrdinalIgnoreCase);
        ISet<string> receiptProjectionTypes = BuildProjectionTypeSet(
            sourcesByPath
                .Where(pair => profiles[pair.Key] == BoundaryProfile.ReceiptSourceProjection)
                .Select(pair => pair.Value));

        foreach ((string relativePath, BoundaryProfile profile) in profiles.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            ISet<string> allowedProjectionTypes = profile == BoundaryProfile.ReceiptSourceProjection
                ? receiptProjectionTypes
                : BuildProjectionTypeSet([sourcesByPath[relativePath]]);
            AssertNoBoundaryViolations(sourcesByPath[relativePath], relativePath, profile, allowedProjectionTypes);
        }
    }

    [Test]
    public void PatchBenchProfileRegistry_FailsUnclassifiedNestedOrNeutralPatchBenchFiles()
    {
        var profiles = new Dictionary<string, BoundaryProfile>(StringComparer.OrdinalIgnoreCase)
        {
            ["OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs"] = BoundaryProfile.LaunchReadiness,
        };
        string[] discovered =
        [
            "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs",
            "OnslaughtCareerEditor.WinUI/Models/Receipt/PatchBenchSafeCopyPreparedLinesText.cs",
        ];

        AssertionException? exception = Assert.Throws<AssertionException>(() =>
            AssertDiscoveredFilesAreProfiled(discovered, profiles));

        Assert.That(exception!.Message, Does.Contain("Classify every PatchBench helper/model file"));
    }

    [Test]
    public void ReceiptSourceBoundaryProfile_FailsAcceptedHostileSamples()
    {
        Dictionary<string, (BoundaryProfile Profile, string Source, string Expected)> unsafeSamples = new(StringComparer.Ordinal)
        {
            ["neutral helper with receipt DTO"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal static class PatchBenchPreparedLinesText { public static string Build(GameProfilePrepareReceipt receipt) => receipt.Headline; }",
                "GameProfile"),
            ["file and path API"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "return File.Exists(path) ? Path.GetFullPath(path) : Directory.GetCurrentDirectory();",
                "file or path"),
            ["receipt construction service"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "GameProfilePreflightService.BuildPrepareReceipt(result, false, null);",
                "receipt construction"),
            ["process and async behavior"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "async Task<string> Build() { Process.Start(command); return await Task.FromResult(\"x\"); }",
                "process"),
            ["sensitive primitive names"] = (
                BoundaryProfile.ReceiptSourceProjection,
                """
                internal sealed record PatchBenchUnsafeReceiptTextState(
                    string SourcePath,
                    string ManifestPath,
                    string ProofId,
                    string CommandPreview,
                    string TargetGameRoot,
                    string TargetExecutablePath);
                """,
                "sensitive"),
            ["record body"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(string Headline) { public string SourcePath { get; init; } = string.Empty; }",
                "parameter-only"),
            ["class state"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed class PatchBenchUnsafeReceiptTextState { public string Headline { get; init; } = string.Empty; }",
                "class or struct"),
            ["property with AppCore DTO"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(string Headline) { public GameProfileControlOptionsResult? ControlOptions { get; init; } }",
                "GameProfile"),
            ["field with delegate"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(string Headline); internal static class PatchBenchUnsafeReceiptText { private static readonly Func<string> Build = () => string.Empty; }",
                "non-primitive"),
            ["method parameter with result DTO"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal static class PatchBenchUnsafeReceiptText { public static string Build(GameProfileMusicReplacementResult result) => string.Empty; }",
                "GameProfile"),
            ["missed GameProfileCopiedEntry"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(GameProfileCopiedEntry Entry);",
                "GameProfile"),
            ["missed GameProfilePatchResult"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(GameProfilePatchResult PatchResult);",
                "GameProfile"),
            ["future GameProfile result"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(GameProfileFutureReceiptResult Result);",
                "GameProfile"),
            ["non-GameProfile online DTO"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal static class PatchBenchUnsafeReceiptText { public static string Build(OnlineMultiplayerReadinessSummary summary) => string.Empty; }",
                "non-receipt"),
            ["non-GameProfile catalog DTO"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "internal sealed record PatchBenchUnsafeReceiptTextState(SafeCopyProfilePreset Preset);",
                "non-receipt"),
            ["using alias evasion"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "using Receipt = GameProfilePrepareReceipt; internal static class PatchBenchUnsafeReceiptText { public static string Build(Receipt receipt) => string.Empty; }",
                "GameProfile"),
            ["safe-copy outcome receipt DTO"] = (
                BoundaryProfile.SafeCopyOutcome,
                "internal static class PatchBenchSafeCopyOutcomeText { public static string BuildSafeCopyReceipt(GameProfilePrepareReceipt receipt) => receipt.Headline; }",
                "GameProfile"),
            ["selected profile service call"] = (
                BoundaryProfile.SelectedProfile,
                "var presets = BinaryPatchPlanBuilder.GetSafeCopyProfilePresets();",
                "catalog service"),
            ["online action enablement"] = (
                BoundaryProfile.OnlineReadiness,
                "PatchBenchHostOnlineSessionButton.IsEnabled = true; Enable Host and Join now;",
                "online action"),
            ["attribute leak"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "[Display(Name = \"ManifestPath\")] internal sealed record PatchBenchUnsafeReceiptTextState(string Headline);",
                "literal"),
            ["reflection bypass"] = (
                BoundaryProfile.ReceiptSourceProjection,
                "object value = Activator.CreateInstance(typeof(GameProfilePrepareReceipt))!;",
                "reflection"),
        };

        foreach ((string category, (BoundaryProfile profile, string source, string expected)) in unsafeSamples)
        {
            string[] failures = FindBoundaryViolations(source, profile, BuildProjectionTypeSet([source]));
            Assert.That(
                failures,
                Has.Some.Contains(expected).IgnoreCase,
                $"Unsafe {category} sample should fail the PatchBench receipt/source boundary guard. Failures: {string.Join(", ", failures)}");
        }
    }

    [Test]
    public void BoundaryProfiles_KeepScopedCurrentSurfaceAllowances()
    {
        Dictionary<string, (BoundaryProfile Profile, string Source)> safeSamples = new(StringComparer.Ordinal)
        {
            ["launch command preview"] = (
                BoundaryProfile.LaunchReadiness,
                "internal sealed record PatchBenchLaunchReadinessTextState(bool HasLaunchPlan, string? CommandPreview);"),
            ["online non-claim proof copy"] = (
                BoundaryProfile.OnlineReadiness,
                """
                internal sealed record PatchBenchOnlineReadinessTextState(
                    string ProofClass,
                    string NextProof,
                    string ProofLadder,
                    string LiveAttemptCommands);
                internal static class PatchBenchOnlineReadinessText
                {
                    public static string Build(OnlineMultiplayerReadinessSummary summary)
                    {
                        return "Host/Join remain unavailable; proof status only, not online-ready.";
                    }
                }
                """),
            ["selected profile catalog constants"] = (
                BoundaryProfile.SelectedProfile,
                """
                internal static class PatchBenchSelectedProfileText
                {
                    public static string Build(PatchBenchSelectedProfileTextState state)
                    {
                        return BinaryPatchPlanBuilder.CompatibilityProfileId + state.MatchedPreset?.DisplayName;
                    }
                }
                internal sealed record PatchBenchSelectedProfileTextState(int SelectedVisibleRowCount, SafeCopyProfilePreset? MatchedPreset, bool IsModernGraphicsOnly);
                """),
            ["safe copy display names"] = (
                BoundaryProfile.SafeCopyOutcome,
                "internal sealed record PatchBenchSafeCopyOutcomeTextState(string SafeCopyFolderName, string BackupRelativePath, string TargetMusicFileName);"),
            ["choice visual binding"] = (
                BoundaryProfile.ChoiceVisualBinding,
                "internal sealed record PatchBenchChoiceButtonBinding(Button Button, PatchBenchSelectedChoiceState State); internal static void Apply(ResourceDictionary resources, Style selectedStyle) { }"),
            ["menu color enum"] = (
                BoundaryProfile.MenuColorSelection,
                "internal enum PatchBenchMenuColorSelectionKind { Original, Teal, Purple }"),
        };

        foreach ((string category, (BoundaryProfile profile, string source)) in safeSamples)
        {
            AssertNoBoundaryViolations(source, category, profile);
        }
    }

    [Test]
    public void ReceiptSourceProjectionProfile_AllowsCrossFilePrimitiveRecordsAndEnums()
    {
        Dictionary<string, string> projectionSources = new(StringComparer.Ordinal)
        {
            ["OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs"] = """
                internal static class PatchBenchSafeCopyReceiptText
                {
                    public static string Build(PatchBenchSafeCopyReceiptTextState state) => state.Headline;
                }
                """,
            ["OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyReceiptTextState.cs"] = """
                internal sealed record PatchBenchSafeCopyReceiptTextState(
                    string Headline,
                    IReadOnlyList<PatchBenchReceiptLineTextState> Lines,
                    IReadOnlyList<string> IncludedChanges,
                    IReadOnlyList<string> StillNotIncluded);
                """,
            ["OnslaughtCareerEditor.WinUI/Models/PatchBenchReceiptLineTextState.cs"] = """
                internal sealed record PatchBenchReceiptLineTextState(string Label, string Value);
                """,
        };

        AssertProjectionSourcesFollowReceiptBoundary(projectionSources);
    }

    [Test]
    public void ReceiptSourceProjectionProfile_RejectsCrossProfilePatchBenchTypes()
    {
        Dictionary<string, string> projectionSources = new(StringComparer.Ordinal)
        {
            ["OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyReceiptTextState.cs"] = """
                internal sealed record PatchBenchSafeCopyReceiptTextState(PatchBenchOnlineReadinessTextState OnlineState);
                """,
        };

        AssertionException? exception = Assert.Throws<AssertionException>(() =>
            AssertProjectionSourcesFollowReceiptBoundary(projectionSources));

        Assert.That(exception!.Message, Does.Contain("PatchBenchOnlineReadinessTextState"));
    }

    [Test]
    public void OutputLeakSentinelGuard_FailsHostileDisplayStrings()
    {
        string[] unsafeOutputs =
        [
            @"Source: C:\Users\tester\AppData\Local\Onslaught\BEA.exe",
            @"Manifest: C:\safe-copy\onslaught-profile-manifest.json",
            "proof-id=runtime-proof-12345",
            "proof-root is private",
            @"CommandPreview=Start-Process C:\games\BEA.exe -ArgumentList -windowed",
        ];

        foreach (string output in unsafeOutputs)
        {
            Assert.That(
                FindForbiddenOutputLeakTokens(output),
                Is.Not.Empty,
                $"Unsafe output leak sample should fail: {output}");
        }

        Assert.That(
            FindForbiddenOutputLeakTokens("Safe copy folder: BEA-safe-copy. Host/Join remain unavailable."),
            Is.Empty);
    }

    [Test]
    public void BoundaryScanner_IgnoresCommentsWhenCheckingIdentifiers()
    {
        string source = """
            // SourcePath should stay page-owned and must not be introduced as a member.
            internal sealed record PatchBenchSafeCopyReceiptTextState(string Headline);
            """;

        AssertNoBoundaryViolations(source, "comment-only sensitive identifier sample", BoundaryProfile.ReceiptSourceProjection);
    }

    [Test]
    public void BinaryPatchesPage_KeepsReceiptAndSourceSummaryOwnershipAtPrimitiveMapperBoundary()
    {
        string page = ReadRepoFile("OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(page, "GameProfilePreflightService.BuildPrepareReceipt("), Is.EqualTo(1));
            Assert.That(page, Does.Contain("GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt("));
            Assert.That(page, Does.Contain("RenderSafeCopyReceipt(receipt);"));
            Assert.That(page, Does.Contain("private void RenderSafeCopyReceipt(GameProfilePrepareReceipt receipt)"));
            Assert.That(page, Does.Contain("private static string BuildSafeCopyReceiptText(GameProfilePrepareReceipt receipt)"));
            Assert.That(page, Does.Contain("PatchBenchSafeCopyReceiptText.Build(BuildSafeCopyReceiptTextState(receipt))"));
            Assert.That(page, Does.Contain("private static PatchBenchSafeCopyReceiptTextState BuildSafeCopyReceiptTextState(GameProfilePrepareReceipt receipt)"));
            Assert.That(page, Does.Contain("new PatchBenchReceiptLineTextState(line.Label, line.Value)"));
            Assert.That(page, Does.Contain("BuildStillNotIncludedLimits(receipt.StillNotIncluded)"));
            Assert.That(page, Does.Contain("PatchBenchSafeCopyOutcomeText.HostJoinReceiptBoundary"));
            Assert.That(page, Does.Not.Contain("builder.AppendLine($\"- {hostJoinBoundary}.\""));
            Assert.That(page, Does.Contain("private static string BuildSourceExecutableSummary(string path)"));
            Assert.That(page, Does.Contain("private static string BuildSafeCopySourceStatus(string path)"));
            Assert.That(page, Does.Contain("private static string BuildSafeCopyProfileCatalogStatus()"));
            Assert.That(page, Does.Contain("private static string BuildWorkingCopySummary(string path)"));
            Assert.That(page, Does.Contain("File.Exists(path)"));
            Assert.That(page, Does.Contain("Path.GetFileName(Path.GetDirectoryName(path))"));
            Assert.That(page, Does.Contain("BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion"));
            Assert.That(page, Does.Contain("BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256"));
            Assert.That(page, Does.Contain("BinaryPatchPlanBuilder.UsingFallbackSafeCopyProfileCatalog"));
        });

        string prepareSlice = ExtractCodeSlice(
            page,
            "GameProfilePrepareResult result = await Task.Run(() =>",
            "RefreshMusicTrackChoices();");
        AssertTokenAppearsOnceBefore(
            prepareSlice,
            "GameProfilePreflightService.BuildPrepareReceipt(",
            "RenderSafeCopyReceipt(receipt);",
            "AppCore receipt construction must stay page-owned before receipt text rendering.");

        string mapperSlice = ExtractCodeSlice(
            page,
            "private static PatchBenchSafeCopyReceiptTextState BuildSafeCopyReceiptTextState(GameProfilePrepareReceipt receipt)",
            "private static string[] BuildStillNotIncludedLimits");
        Assert.Multiple(() =>
        {
            Assert.That(mapperSlice, Does.Not.Contain("File."));
            Assert.That(mapperSlice, Does.Not.Contain("Path."));
            Assert.That(mapperSlice, Does.Not.Contain("Directory."));
            Assert.That(mapperSlice, Does.Not.Contain("Process"));
            Assert.That(mapperSlice, Does.Not.Contain("Task"));
            Assert.That(mapperSlice, Does.Not.Contain("LaunchPlan"));
            Assert.That(mapperSlice, Does.Not.Contain("CommandPreview"));
            Assert.That(mapperSlice, Does.Not.Contain("OnlineMultiplayerReadinessService"));
            Assert.That(mapperSlice, Does.Not.Contain("HostOnlineSession"));
            Assert.That(mapperSlice, Does.Not.Contain("JoinOnlineSession"));
        });
    }

    [Test]
    public void BoundaryRoutingGuard_FailsWhenTokensAreMissingOrReversed()
    {
        Assert.Multiple(() =>
        {
            AssertionException? missingEarlier = Assert.Throws<AssertionException>(() =>
                AssertTokenAppearsOnceBefore("RenderSafeCopyReceipt(receipt);", "BuildPrepareReceipt(", "RenderSafeCopyReceipt(receipt);", "sample"));
            AssertionException? missingLater = Assert.Throws<AssertionException>(() =>
                AssertTokenAppearsOnceBefore("BuildPrepareReceipt(", "BuildPrepareReceipt(", "RenderSafeCopyReceipt(receipt);", "sample"));
            AssertionException? reversed = Assert.Throws<AssertionException>(() =>
                AssertTokenAppearsOnceBefore("RenderSafeCopyReceipt(receipt); BuildPrepareReceipt(", "BuildPrepareReceipt(", "RenderSafeCopyReceipt(receipt);", "sample"));

            Assert.That(missingEarlier!.Message, Does.Contain("Expected exactly one earlier routing token"));
            Assert.That(missingLater!.Message, Does.Contain("Expected exactly one later routing token"));
            Assert.That(reversed!.Message, Does.Contain("sample"));
        });
    }

    private static IReadOnlyDictionary<string, BoundaryProfile> BuildBoundaryProfileMap()
    {
        var profiles = new Dictionary<string, BoundaryProfile>(StringComparer.OrdinalIgnoreCase);
        foreach (BoundaryFileEntry entry in PatchBenchBoundaryFiles)
        {
            string normalizedPath = NormalizeRepoRelativePath(entry.RelativePath);
            Assert.That(
                profiles.ContainsKey(normalizedPath),
                Is.False,
                $"Duplicate PatchBench boundary profile entry for {normalizedPath}.");
            profiles.Add(normalizedPath, entry.Profile);
        }

        return profiles;
    }

    private static void AssertDiscoveredFilesAreProfiled(
        IEnumerable<string> discoveredPaths,
        IReadOnlyDictionary<string, BoundaryProfile> profileMap)
    {
        string[] actualFiles = discoveredPaths
            .Select(NormalizeRepoRelativePath)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();
        string[] expectedFiles = profileMap.Keys
            .Select(NormalizeRepoRelativePath)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        Assert.That(
            actualFiles,
            Is.EqualTo(expectedFiles),
            "Classify every PatchBench helper/model file with an explicit boundary profile before extracting receipt or source-summary presentation code.");
    }

    private static string[] GetPatchBenchPresentationFiles()
    {
        string winUiRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI");
        string[] roots =
        [
            Path.Combine(winUiRoot, "Helpers"),
            Path.Combine(winUiRoot, "Models"),
        ];

        return roots
            .Where(Directory.Exists)
            .SelectMany(root => Directory.GetFiles(root, "PatchBench*.cs", SearchOption.AllDirectories))
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();
    }

    private static void AssertNoBoundaryViolations(string source, string sourceName, BoundaryProfile profile)
    {
        AssertNoBoundaryViolations(source, sourceName, profile, BuildProjectionTypeSet([source]));
    }

    private static void AssertNoBoundaryViolations(
        string source,
        string sourceName,
        BoundaryProfile profile,
        ISet<string> allowedProjectionTypes)
    {
        string[] failures = FindBoundaryViolations(source, profile, allowedProjectionTypes);
        Assert.That(
            failures,
            Is.Empty,
            $"{sourceName} must stay within the {profile} PatchBench boundary profile. Violations: {string.Join(", ", failures)}");
    }

    private static void AssertProjectionSourcesFollowReceiptBoundary(IReadOnlyDictionary<string, string> sourcesByPath)
    {
        ISet<string> projectionTypes = BuildProjectionTypeSet(sourcesByPath.Values);
        foreach ((string path, string source) in sourcesByPath)
        {
            string[] failures = FindBoundaryViolations(source, BoundaryProfile.ReceiptSourceProjection, projectionTypes);
            Assert.That(
                failures,
                Is.Empty,
                $"{path} must stay within the primitive receipt/source projection boundary. Violations: {string.Join(", ", failures)}");
        }
    }

    private static string[] FindBoundaryViolations(
        string source,
        BoundaryProfile profile,
        ISet<string> allowedProjectionTypes)
    {
        string code = StripCommentsAndStrings(source);
        var failures = new List<string>();

        AddPatternFailure(failures, code, "AppCore GameProfile DTO/result", @"\bGameProfile[A-Z]\w*\b");
        AddPatternFailure(failures, code, "direct AppCore receipt construction", @"\bnew\s+GameProfile(?:PrepareReceipt|ReceiptLine)\b|\bBuildPrepareReceipt\s*\(");
        AddPatternFailure(failures, code, "file or path API", @"\b(?:File|Directory|Path)\s*\.|\bSystem\.IO\b|\b(?:FileInfo|DirectoryInfo|DriveInfo)\b|\busing\s+\w+\s*=\s*System\.IO\b");
        AddPatternFailure(failures, code, "process, async, or reflection behavior", @"\b(?:ProcessStartInfo|Process\.Start|Task|async|await|Activator|dynamic|System\.Reflection|Unsafe)\b");
        AddPatternFailure(failures, code, "AppCore behavior service", @"\b(?:GameProfilePreflightService|GameProfileRuntimeService|GameProfileControlOptionsService|GameProfileMusicReplacementService|OnlineMultiplayerReadinessService)\b");

        foreach (string leak in FindForbiddenOutputLeakTokens(StripComments(source)))
        {
            failures.Add($"literal/output leak: {leak}");
        }

        foreach (string sensitiveName in FindSensitiveIdentifierNames(code))
        {
            if (!IsSensitiveIdentifierAllowed(profile, sensitiveName))
            {
                failures.Add($"sensitive member/parameter identifier: {sensitiveName}");
            }
        }

        if (profile != BoundaryProfile.SelectedProfile)
        {
            AddPatternFailure(failures, code, "selected-profile catalog DTO", @"\b(?:SafeCopyProfilePreset|SafeCopyProfileModule)\b");
            AddPatternFailure(failures, code, "selected-profile catalog constants", @"\bBinaryPatchPlanBuilder\b");
        }
        else
        {
            AddPatternFailure(failures, code, "catalog service call", @"\bBinaryPatchPlanBuilder\s*\.\s*(?:GetSafeCopyProfilePresets|GetRequiredCompatibilityPatches|Build|Create)\s*\(");
        }

        if (profile != BoundaryProfile.PatchGroups)
        {
            AddPatternFailure(failures, code, "patch group model DTO", @"\b(?:BinaryPatchItemModel|BinaryPatchGroupModel)\b");
        }

        if (profile != BoundaryProfile.OnlineReadiness)
        {
            AddPatternFailure(failures, code, "non-receipt online readiness DTO", @"\bOnline[A-Z]\w+\b");
            AddPatternFailure(failures, code, "Host/Join or online action wording", OnlineActionRegex);
        }
        else
        {
            AddPatternFailure(failures, code, "Host/Join or online action enablement", @"\b(?:HostOnlineSession|JoinOnlineSession|PatchBenchHostOnlineSessionButton|PatchBenchJoinOnlineSessionButton|PublicMatchmaking|public matchmaking|HostOnline|JoinOnline)\b");
        }

        if (profile == BoundaryProfile.SafeCopyOutcome)
        {
            AddPatternFailure(failures, code, "receipt DTO parameter in safe-copy outcome", @"\bBuild\w*Receipt\w*\s*\([^)]*\bGameProfile[A-Z]\w*");
        }

        if (profile == BoundaryProfile.ReceiptSourceProjection)
        {
            failures.AddRange(FindReceiptSourceProjectionViolations(code, allowedProjectionTypes));
            AddPatternFailure(failures, code, "non-receipt catalog or online DTO in receipt/source projection", @"\b(?:Online[A-Z]\w+|SafeCopyProfilePreset|SafeCopyProfileModule|BinaryPatchItemModel|BinaryPatchGroupModel|BinaryPatchPlanBuilder)\b");
            AddPatternFailure(failures, code, "Host/Join or online action wording", OnlineActionRegex);
        }

        return failures.Distinct(StringComparer.Ordinal).ToArray();
    }

    private static IEnumerable<string> FindReceiptSourceProjectionViolations(
        string code,
        ISet<string> allowedProjectionTypes)
    {
        var failures = new List<string>();

        foreach (Match match in Regex.Matches(code, @"\brecord\s+(?<name>PatchBench\w+)\s*\((?<parameters>[\s\S]*?)\)\s*(?<terminator>[{;])", RegexOptions.CultureInvariant))
        {
            string recordName = match.Groups["name"].Value;
            if (match.Groups["terminator"].Value == "{")
            {
                failures.Add($"{recordName} must be a parameter-only record ending with ';'");
            }

            foreach (string parameter in SplitParameterList(match.Groups["parameters"].Value))
            {
                string typeName = GetParameterType(parameter);
                if (!string.IsNullOrWhiteSpace(typeName) &&
                    !IsAllowedPrimitiveProjectionType(typeName, allowedProjectionTypes))
                {
                    failures.Add($"{recordName} parameter '{parameter.Trim()}' uses non-primitive projection type {typeName}");
                }
            }
        }

        AddPatternFailure(failures, code, "record body or non-primary record projection", @"\brecord\s+PatchBench\w+\s*(?:[{;]|:\s*)");
        AddPatternFailure(failures, code, "class or struct projection state", @"\b(?:class|struct)\s+PatchBench\w*(?:TextState|Projection|ReceiptState|SourceState)\w*\b");

        foreach ((string owner, string typeName) in FindDeclaredMemberTypes(code))
        {
            if (!IsAllowedPrimitiveProjectionType(typeName, allowedProjectionTypes))
            {
                failures.Add($"{owner} uses non-primitive projection type {typeName}");
            }
        }

        return failures;
    }

    private static IEnumerable<(string Owner, string TypeName)> FindDeclaredMemberTypes(string code)
    {
        foreach (Match match in Regex.Matches(
            code,
            @"\b(?:public|internal|private|protected)\s+(?:static\s+|readonly\s+|const\s+)*?(?<type>[A-Za-z_][\w.<>,?\[\]\s]*?)\s+(?<name>@?[A-Za-z_]\w*)\s*(?:[{=;])",
            RegexOptions.CultureInvariant))
        {
            string typeName = NormalizeTypeWhitespace(match.Groups["type"].Value);
            if (!IsTypeDeclarationPrefix(typeName))
            {
                yield return ($"member {match.Groups["name"].Value}", typeName);
            }
        }

        foreach (Match match in Regex.Matches(
            code,
            @"\b(?:public|internal|private|protected)\s+(?:static\s+)?(?<return>[A-Za-z_][\w.<>,?\[\]\s]*?)\s+(?<name>@?[A-Za-z_]\w*)\s*\((?<parameters>[^)]*)\)",
            RegexOptions.CultureInvariant))
        {
            string returnType = NormalizeTypeWhitespace(match.Groups["return"].Value);
            if (!IsTypeDeclarationPrefix(returnType) &&
                !string.Equals(returnType, "void", StringComparison.Ordinal))
            {
                yield return ($"method {match.Groups["name"].Value} return", returnType);
            }

            foreach (string parameter in SplitParameterList(match.Groups["parameters"].Value))
            {
                string typeName = GetParameterType(parameter);
                if (!string.IsNullOrWhiteSpace(typeName))
                {
                    yield return ($"method {match.Groups["name"].Value} parameter '{parameter.Trim()}'", typeName);
                }
            }
        }
    }

    private static ISet<string> BuildProjectionTypeSet(IEnumerable<string> sources)
    {
        var types = new HashSet<string>(StringComparer.Ordinal);
        foreach (string source in sources)
        {
            string code = StripCommentsAndStrings(source);
            foreach (Match match in Regex.Matches(code, @"\b(?:record|enum)\s+(?<name>PatchBench\w+)\b", RegexOptions.CultureInvariant))
            {
                types.Add(match.Groups["name"].Value);
            }
        }

        return types;
    }

    private static bool IsAllowedPrimitiveProjectionType(string typeName, ISet<string> allowedProjectionTypes)
    {
        string clean = NormalizeTypeWhitespace(typeName);
        clean = clean.EndsWith("?", StringComparison.Ordinal) ? clean[..^1] : clean;
        clean = clean.StartsWith("System.", StringComparison.Ordinal) ? clean["System.".Length..] : clean;
        clean = clean.StartsWith("global::", StringComparison.Ordinal) ? clean["global::".Length..] : clean;

        string[] primitiveTypes =
        [
            "string",
            "bool",
            "byte",
            "sbyte",
            "short",
            "ushort",
            "int",
            "uint",
            "long",
            "ulong",
            "float",
            "double",
            "decimal",
            "char",
        ];
        if (primitiveTypes.Contains(clean, StringComparer.Ordinal))
        {
            return true;
        }

        Match genericMatch = Regex.Match(clean, @"^(?:IReadOnlyList|IEnumerable|List|IReadOnlyCollection)<(?<inner>.+)>$", RegexOptions.CultureInvariant);
        if (genericMatch.Success)
        {
            return IsAllowedPrimitiveProjectionType(genericMatch.Groups["inner"].Value.Trim(), allowedProjectionTypes);
        }

        if (clean.EndsWith("[]", StringComparison.Ordinal))
        {
            return IsAllowedPrimitiveProjectionType(clean[..^2], allowedProjectionTypes);
        }

        return clean.StartsWith("PatchBench", StringComparison.Ordinal) &&
            allowedProjectionTypes.Contains(clean);
    }

    private static IEnumerable<string> FindSensitiveIdentifierNames(string code)
    {
        string[] sensitiveNames =
        [
            "SourcePath",
            "TargetPath",
            "SourceExecutablePath",
            "TargetExecutablePath",
            "ExecutablePath",
            "ManifestPath",
            "ProfileRoot",
            "TargetGameRoot",
            "ProofId",
            "ProofStatus",
            "CommandPreview",
            "LaunchPlanPreview",
            "SafeCopyFolderName",
            "BackupRelativePath",
            "TargetMusicFileName",
        ];

        foreach (string name in sensitiveNames)
        {
            if (Regex.IsMatch(code, $@"\b@?{Regex.Escape(name)}\b", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant))
            {
                yield return name;
            }
        }
    }

    private static bool IsSensitiveIdentifierAllowed(BoundaryProfile profile, string sensitiveName)
    {
        return profile switch
        {
            BoundaryProfile.LaunchReadiness => string.Equals(sensitiveName, "CommandPreview", StringComparison.OrdinalIgnoreCase),
            BoundaryProfile.OnlineReadiness => string.Equals(sensitiveName, "LaunchPlanPreview", StringComparison.OrdinalIgnoreCase),
            BoundaryProfile.SafeCopyOutcome => sensitiveName.Equals("SafeCopyFolderName", StringComparison.OrdinalIgnoreCase) ||
                sensitiveName.Equals("BackupRelativePath", StringComparison.OrdinalIgnoreCase) ||
                sensitiveName.Equals("TargetMusicFileName", StringComparison.OrdinalIgnoreCase),
            BoundaryProfile.ReceiptSourceProjection => sensitiveName.Equals("SafeCopyFolderName", StringComparison.OrdinalIgnoreCase),
            _ => false,
        };
    }

    private static string[] FindForbiddenOutputLeakTokens(string output)
    {
        var patterns = new List<BoundaryPattern>
        {
            new("drive root", @"[A-Za-z]:\\"),
            new("user profile path", @"\\Users\\|\\AppData\\"),
            new("manifest file path", @"\bonslaught-profile-manifest\.json\b"),
            new("proof id", @"\bproof-id\s*=|\bruntime-proof-[A-Za-z0-9._-]+\b"),
            new("proof root", @"\bproof-root\b"),
            new("raw command preview", @"\bStart-Process\b|\bCommandPreview\s*="),
            new("sensitive literal identifier", @"\b(?:SourcePath|ManifestPath|ProofId|TargetGameRoot|TargetExecutablePath)\b"),
        };

        return patterns
            .Where(pattern => Regex.IsMatch(output, pattern.Regex, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant))
            .Select(pattern => pattern.Name)
            .ToArray();
    }

    private static void AddPatternFailure(List<string> failures, string source, string name, string regex)
    {
        if (Regex.IsMatch(source, regex, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant))
        {
            failures.Add(name);
        }
    }

    private static IEnumerable<string> SplitParameterList(string parameters)
    {
        var current = new StringBuilder();
        int genericDepth = 0;
        foreach (char c in parameters)
        {
            if (c == '<')
            {
                genericDepth++;
            }
            else if (c == '>')
            {
                genericDepth--;
            }

            if (c == ',' && genericDepth == 0)
            {
                yield return current.ToString();
                current.Clear();
                continue;
            }

            current.Append(c);
        }

        if (current.Length > 0)
        {
            yield return current.ToString();
        }
    }

    private static string GetParameterType(string parameter)
    {
        string clean = NormalizeTypeWhitespace(parameter);
        int lastSpace = clean.LastIndexOf(' ');
        return lastSpace <= 0 ? string.Empty : clean[..lastSpace].Trim();
    }

    private static string NormalizeTypeWhitespace(string typeName)
    {
        string clean = Regex.Replace(typeName.Trim(), @"\s+", " ");
        string[] modifiers = ["static ", "readonly ", "const ", "sealed ", "partial ", "params "];
        bool removed;
        do
        {
            removed = false;
            foreach (string modifier in modifiers)
            {
                if (clean.StartsWith(modifier, StringComparison.Ordinal))
                {
                    clean = clean[modifier.Length..];
                    removed = true;
                }
            }
        }
        while (removed);

        return clean;
    }

    private static bool IsTypeDeclarationPrefix(string typeName)
    {
        return typeName.Contains(" record", StringComparison.Ordinal) ||
            typeName.Contains(" class", StringComparison.Ordinal) ||
            typeName.Contains(" struct", StringComparison.Ordinal) ||
            typeName.Contains(" enum", StringComparison.Ordinal) ||
            typeName.Equals("record", StringComparison.Ordinal) ||
            typeName.Equals("class", StringComparison.Ordinal) ||
            typeName.Equals("struct", StringComparison.Ordinal) ||
            typeName.Equals("enum", StringComparison.Ordinal);
    }

    private static string StripCommentsAndStrings(string source)
    {
        var builder = new StringBuilder(source.Length);
        for (int i = 0; i < source.Length; i++)
        {
            char current = source[i];
            char next = i + 1 < source.Length ? source[i + 1] : '\0';

            if (current == '/' && next == '/')
            {
                while (i < source.Length && source[i] != '\n')
                {
                    i++;
                }

                builder.Append('\n');
                continue;
            }

            if (current == '/' && next == '*')
            {
                i += 2;
                while (i + 1 < source.Length && !(source[i] == '*' && source[i + 1] == '/'))
                {
                    builder.Append(source[i] == '\n' ? '\n' : ' ');
                    i++;
                }

                i++;
                continue;
            }

            if (current == '@' && next == '"')
            {
                builder.Append(' ');
                i += 2;
                while (i < source.Length)
                {
                    if (source[i] == '"' && i + 1 < source.Length && source[i + 1] == '"')
                    {
                        i += 2;
                        continue;
                    }

                    if (source[i] == '"')
                    {
                        break;
                    }

                    builder.Append(source[i] == '\n' ? '\n' : ' ');
                    i++;
                }

                continue;
            }

            if (current == '"')
            {
                builder.Append(' ');
                i++;
                while (i < source.Length)
                {
                    if (source[i] == '\\')
                    {
                        i += 2;
                        continue;
                    }

                    if (source[i] == '"')
                    {
                        break;
                    }

                    builder.Append(source[i] == '\n' ? '\n' : ' ');
                    i++;
                }

                continue;
            }

            builder.Append(current);
        }

        return builder.ToString();
    }

    private static string StripComments(string source)
    {
        var builder = new StringBuilder(source.Length);
        for (int i = 0; i < source.Length; i++)
        {
            char current = source[i];
            char next = i + 1 < source.Length ? source[i + 1] : '\0';

            if (current == '/' && next == '/')
            {
                while (i < source.Length && source[i] != '\n')
                {
                    i++;
                }

                builder.Append('\n');
                continue;
            }

            if (current == '/' && next == '*')
            {
                i += 2;
                while (i + 1 < source.Length && !(source[i] == '*' && source[i + 1] == '/'))
                {
                    builder.Append(source[i] == '\n' ? '\n' : ' ');
                    i++;
                }

                i++;
                continue;
            }

            builder.Append(current);
        }

        return builder.ToString();
    }

    private static void AssertTokenAppearsOnceBefore(string source, string earlierToken, string laterToken, string message)
    {
        int earlierCount = CountOccurrences(source, earlierToken);
        int laterCount = CountOccurrences(source, laterToken);
        Assert.That(earlierCount, Is.EqualTo(1), $"Expected exactly one earlier routing token: {earlierToken}");
        Assert.That(laterCount, Is.EqualTo(1), $"Expected exactly one later routing token: {laterToken}");

        int earlierIndex = source.IndexOf(earlierToken, StringComparison.Ordinal);
        int laterIndex = source.IndexOf(laterToken, StringComparison.Ordinal);
        Assert.That(earlierIndex, Is.LessThan(laterIndex), message);
    }

    private static int CountOccurrences(string source, string token)
    {
        int count = 0;
        int index = 0;
        while ((index = source.IndexOf(token, index, StringComparison.Ordinal)) >= 0)
        {
            count++;
            index += token.Length;
        }

        return count;
    }

    private static string ExtractCodeSlice(string code, string startToken, string endToken)
    {
        int start = code.IndexOf(startToken, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), $"Missing start token: {startToken}");
        int end = code.IndexOf(endToken, start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), $"Missing end token after {startToken}: {endToken}");
        return code[start..end];
    }

    private static string ReadRepoFile(string relativePath)
    {
        string path = ResolveRepoPath(relativePath);
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {relativePath}");
        return File.ReadAllText(path);
    }

    private static string ResolveRepoPath(string relativePath)
    {
        string[] parts = relativePath.Split(['/', '\\'], StringSplitOptions.RemoveEmptyEntries);
        return Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
    }

    private static string ToRepoRelativePath(string path)
    {
        return NormalizeRepoRelativePath(Path.GetRelativePath(TestFixturePaths.RepoRoot, path));
    }

    private static string NormalizeRepoRelativePath(string path)
    {
        return path.Replace('\\', '/').TrimStart('/');
    }

    private const string OnlineActionRegex =
        @"\b(?:HostOnlineSession|JoinOnlineSession|PatchBenchHostOnlineSessionButton|PatchBenchJoinOnlineSessionButton|PublicMatchmaking|public matchmaking|online-ready|Online session|enable\s+Host|enable\s+Join|netplay)\b";

    private sealed record BoundaryFileEntry(string RelativePath, BoundaryProfile Profile);

    private sealed record BoundaryPattern(string Name, string Regex);

    private enum BoundaryProfile
    {
        ReceiptSourceProjection,
        SafeCopyOutcome,
        LaunchReadiness,
        OnlineReadiness,
        SelectedProfile,
        PatchGroups,
        ChoiceVisualBinding,
        MenuColorSelection,
    }
}
