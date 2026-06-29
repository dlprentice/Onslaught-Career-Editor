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
    private static readonly string[] ExpectedPatchBenchPresentationFiles =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchChoiceVisualState.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchMenuColorSelectionText.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchPatchGroups.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSelectedProfileText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextResult.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchMenuColorSelectionKind.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedChoiceState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedProfileTextState.cs",
    ];

    private static readonly string[] SafeCopyOutcomeBoundaryFiles =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs",
    ];

    [Test]
    public void PatchBenchPresentationFiles_MustBeExplicitlyClassifiedBeforeAddingReceiptOrSourceHelpers()
    {
        string[] actualFiles = GetPatchBenchPresentationFiles()
            .Select(ToRepoRelativePath)
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToArray();

        Assert.That(
            actualFiles,
            Is.EqualTo(ExpectedPatchBenchPresentationFiles.OrderBy(path => path, StringComparer.Ordinal)),
            "Classify any new PatchBench helper/model file in PatchBenchPrimitiveProjectionBoundaryTests before extracting receipt or source-summary presentation code.");
    }

    [Test]
    public void FutureReceiptAndSourceProjectionSurfaces_UsePrimitiveStateAndNoBehaviorTokens()
    {
        string[] candidateFiles = GetPatchBenchPresentationFiles()
            .Where(IsFutureReceiptOrSourceProjectionCandidate)
            .ToArray();

        foreach (string filePath in candidateFiles)
        {
            string source = File.ReadAllText(filePath);
            string relativePath = ToRepoRelativePath(filePath);
            AssertNoForbiddenBoundaryTokens(source, relativePath, strictOnlineActionScan: true);
            AssertPrimitiveProjectionRecordsOnly(source, relativePath);
        }
    }

    [Test]
    public void PatchBenchSafeCopyOutcomeSurfaces_StayOutsideReceiptAndSourceOwnership()
    {
        foreach (string relativePath in SafeCopyOutcomeBoundaryFiles)
        {
            string source = ReadRepoFile(relativePath);
            AssertNoForbiddenBoundaryTokens(source, relativePath, strictOnlineActionScan: false);
        }

        string outcomeText = ReadRepoFile("OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs");
        Assert.That(
            outcomeText,
            Does.Contain("public const string HostJoinReceiptBoundary = \"No Host/Join or online multiplayer\";"),
            "Accepted Host/Join boundary copy is a non-claim fallback and must not be treated as an online action.");
    }

    [Test]
    public void BinaryPatchesPage_KeepsReceiptAndSourceSummaryOwnershipUntilPrimitiveExtraction()
    {
        string page = ReadRepoFile("OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(page, "GameProfilePreflightService.BuildPrepareReceipt("), Is.EqualTo(1));
            Assert.That(page, Does.Contain("GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt("));
            Assert.That(page, Does.Contain("RenderSafeCopyReceipt(receipt);"));
            Assert.That(page, Does.Contain("private void RenderSafeCopyReceipt(GameProfilePrepareReceipt receipt)"));
            Assert.That(page, Does.Contain("private static string BuildSafeCopyReceiptText(GameProfilePrepareReceipt receipt)"));
            Assert.That(page, Does.Contain("foreach (GameProfileReceiptLine line in receipt.Lines)"));
            Assert.That(page, Does.Contain("receipt.StillNotIncluded.Any(limit => limit.Contains(hostJoinBoundary, StringComparison.OrdinalIgnoreCase))"));
            Assert.That(page, Does.Contain("builder.AppendLine($\"- {hostJoinBoundary}.\");"));
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
    }

    [Test]
    public void PrimitiveProjectionBoundaryGuard_FailsUnsafeSamplesByCategory()
    {
        Dictionary<string, string> unsafeSamples = new(StringComparer.Ordinal)
        {
            ["AppCore receipt DTO"] = "internal static string Build(GameProfilePrepareReceipt receipt) => receipt.Headline;",
            ["direct receipt construction"] = "var receipt = new GameProfilePrepareReceipt(\"ready\", lines, changes, limits);",
            ["file and path API"] = "return File.Exists(path) ? Path.GetFullPath(path) : Directory.GetCurrentDirectory();",
            ["service and catalog behavior"] = "GameProfilePreflightService.BuildPrepareReceipt(result, false, null); BinaryPatchPlanBuilder.GetSafeCopyProfilePresets();",
            ["launch and process behavior"] = "Process.Start(command); GameProfileRuntimeService.LaunchCopiedProfile(plan);",
            ["online action wording"] = "PatchBenchHostOnlineSessionButton.Content = \"Online-ready Host session\";",
            ["raw proof or local path leak"] = "var proof = \"proof-id=runtime-proof-123 C:\\\\Users\\\\tester\\\\AppData\\\\Local\\\\proof-root\";",
        };

        foreach ((string category, string source) in unsafeSamples)
        {
            string[] failures = FindForbiddenBoundaryTokens(source, strictOnlineActionScan: true);
            Assert.That(failures, Is.Not.Empty, $"Unsafe {category} sample should fail the PatchBench receipt/source boundary guard.");
        }
    }

    [Test]
    public void PrimitiveProjectionBoundaryGuard_AllowsPrimitiveBoundarySamples()
    {
        string safeSample = """
namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchSafeCopyReceiptText
    {
        public const string HostJoinReceiptBoundary = "No Host/Join or online multiplayer";

        public static string Build(PatchBenchSafeCopyReceiptTextState state)
        {
            return state.Headline + HostJoinReceiptBoundary;
        }
    }
}

namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSafeCopyReceiptTextState(
        string Headline,
        IReadOnlyList<PatchBenchReceiptLineTextState> Lines,
        IReadOnlyList<string> IncludedChanges,
        IReadOnlyList<string> StillNotIncluded,
        bool CopiedSavegames,
        int FilesCopied);

    internal sealed record PatchBenchReceiptLineTextState(string Label, string Value);
}
""";

        AssertNoForbiddenBoundaryTokens(safeSample, "safe primitive receipt sample", strictOnlineActionScan: true);
        AssertPrimitiveProjectionRecordsOnly(safeSample, "safe primitive receipt sample");
    }

    [Test]
    public void PrimitiveProjectionRecordGuard_RejectsBehaviorTypes()
    {
        string unsafeModelSample = """
namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchUnsafeReceiptTextState(
        GameProfilePrepareReceipt Receipt,
        IReadOnlyList<GameProfileReceiptLine> Lines,
        Func<string> BuildText);
}
""";

        AssertionException? exception = Assert.Throws<AssertionException>(() =>
            AssertPrimitiveProjectionRecordsOnly(unsafeModelSample, "unsafe receipt model sample"));

        Assert.That(exception!.Message, Does.Contain("GameProfilePrepareReceipt"));
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
            .SelectMany(root => Directory.GetFiles(root, "PatchBench*.cs"))
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToArray();
    }

    private static bool IsFutureReceiptOrSourceProjectionCandidate(string filePath)
    {
        string name = Path.GetFileNameWithoutExtension(filePath);
        string[] candidateTerms =
        [
            "Receipt",
            "SourceSummary",
            "ExecutableSummary",
            "WorkingCopySummary",
            "ProfileCatalog",
            "CatalogStatus",
            "Projection",
            "Formatter",
            "Presenter",
        ];

        return candidateTerms.Any(term => name.Contains(term, StringComparison.OrdinalIgnoreCase));
    }

    private static void AssertNoForbiddenBoundaryTokens(string source, string sourceName, bool strictOnlineActionScan)
    {
        string[] failures = FindForbiddenBoundaryTokens(source, strictOnlineActionScan);
        Assert.That(
            failures,
            Is.Empty,
            $"{sourceName} must stay primitive/display-only for PatchBench receipt/source projection. Forbidden tokens: {string.Join(", ", failures)}");
    }

    private static string[] FindForbiddenBoundaryTokens(string source, bool strictOnlineActionScan)
    {
        var patterns = new List<BoundaryPattern>
        {
            new("AppCore receipt DTO", @"\bGameProfile(?:PrepareReceipt|ReceiptLine|PrepareResult|PrepareOptions|ControlOptionsRequest|LaunchPlan)\b"),
            new("direct AppCore receipt construction", @"\bnew\s+GameProfile(?:PrepareReceipt|ReceiptLine)\b|\bBuildPrepareReceipt\s*\("),
            new("AppCore or patch behavior service", @"\b(?:GameProfilePreflightService|GameProfileRuntimeService|GameProfileControlOptionsService|GameProfileMusicReplacementService|BinaryPatchEngine|BinaryPatchPlanBuilder|OnlineMultiplayerReadinessService)\b"),
            new("patch catalog behavior", @"\b(?:SafeCopyProfileCatalog|SafeCopyProfilePreset|PatchSpec|PatchPlan)\b"),
            new("file or path API", @"\b(?:File|Directory|Path)\s*\.|\bSystem\.IO\b|\b(?:FileInfo|DirectoryInfo|DriveInfo)\b"),
            new("process or async behavior", @"\b(?:ProcessStartInfo|Process\.Start|Task|async|await)\b"),
            new("launch/process ownership", @"\b(?:BuildLaunchPlan|BuildSelectedLaunchArguments|TryBuildCopiedProfileLaunchPlan|LaunchCopiedProfile|StopCopiedProfile|CommandPreview|Start-Process)\b"),
            new("raw local or proof path leak", @"[A-Za-z]:\\|\\\\[A-Za-z0-9._$-]+\\|\\Users\\|\\AppData\\|\b(?:runtime-proof|proof-root|proof-id|proof artifact|CDB|Ghidra|frame dump|screenshot)\b"),
            new("release or package claim", @"\b(?:GitHub Release|MSIX|README\.RELEASE|release readiness|package output)\b"),
        };

        if (strictOnlineActionScan)
        {
            patterns.Add(new BoundaryPattern(
                "Host/Join or online action wording",
                @"\b(?:HostOnlineSession|JoinOnlineSession|PatchBenchHostOnlineSessionButton|PatchBenchJoinOnlineSessionButton|PublicMatchmaking|public matchmaking|online-ready|Online session|enable\s+Host|enable\s+Join|netplay)\b"));
        }

        return patterns
            .Where(pattern => Regex.IsMatch(source, pattern.Regex, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant))
            .Select(pattern => pattern.Name)
            .ToArray();
    }

    private static void AssertPrimitiveProjectionRecordsOnly(string source, string sourceName)
    {
        foreach ((string recordName, string parameters) in FindRecordPrimaryConstructors(source))
        {
            foreach (string parameter in SplitParameterList(parameters))
            {
                string typeName = GetParameterType(parameter);
                if (string.IsNullOrWhiteSpace(typeName))
                {
                    continue;
                }

                Assert.That(
                    IsAllowedPrimitiveProjectionType(typeName, source),
                    Is.True,
                    $"{sourceName} record {recordName} parameter '{parameter.Trim()}' uses non-primitive projection type {typeName}.");
            }
        }
    }

    private static IEnumerable<(string Name, string Parameters)> FindRecordPrimaryConstructors(string source)
    {
        MatchCollection matches = Regex.Matches(
            source,
            @"\brecord\s+(?<name>\w+)\s*\((?<parameters>[\s\S]*?)\)\s*;",
            RegexOptions.CultureInvariant);
        foreach (Match match in matches)
        {
            yield return (match.Groups["name"].Value, match.Groups["parameters"].Value);
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
        string clean = Regex.Replace(parameter.Trim(), @"\s+", " ");
        int lastSpace = clean.LastIndexOf(' ');
        return lastSpace <= 0 ? string.Empty : clean[..lastSpace].Trim();
    }

    private static bool IsAllowedPrimitiveProjectionType(string typeName, string source)
    {
        string clean = typeName.Trim();
        clean = clean.EndsWith("?", StringComparison.Ordinal) ? clean[..^1] : clean;
        clean = clean.StartsWith("System.", StringComparison.Ordinal) ? clean["System.".Length..] : clean;

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

        if (Regex.IsMatch(clean, @"^(?:IReadOnlyList|IEnumerable|List|IReadOnlyCollection)<(?<inner>.+)>$", RegexOptions.CultureInvariant))
        {
            string inner = Regex.Match(clean, @"<(?<inner>.+)>", RegexOptions.CultureInvariant).Groups["inner"].Value.Trim();
            return IsAllowedPrimitiveProjectionType(inner, source);
        }

        if (clean.EndsWith("[]", StringComparison.Ordinal))
        {
            return IsAllowedPrimitiveProjectionType(clean[..^2], source);
        }

        if (clean.StartsWith("PatchBench", StringComparison.Ordinal) &&
            Regex.IsMatch(source, $@"\brecord\s+{Regex.Escape(clean)}\b", RegexOptions.CultureInvariant))
        {
            return true;
        }

        return false;
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
        return Path.GetRelativePath(TestFixturePaths.RepoRoot, path).Replace('\\', '/');
    }

    private sealed record BoundaryPattern(string Name, string Regex);
}
