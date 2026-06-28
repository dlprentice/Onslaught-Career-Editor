using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchOnlineReadinessRoutingGuardTests
{
    private static readonly string[] ReflectedOnlineReadinessSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs",
    ];

    [Test]
    public void BinaryPatchesPage_RoutesOnlineReadinessTextThroughPresentationHelper()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string readinessRender = ExtractCodeSlice(
            code,
            "private void RenderOnlineMultiplayerReadiness()",
            "private void RenderOnlineCompanionSessionReadiness(");
        string companionRender = ExtractCodeSlice(
            code,
            "private void RenderOnlineCompanionSessionReadiness(",
            "private void RenderMaintainerArtifactToolsVisibility()");
        Type readinessStateType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchOnlineReadinessTextState",
            ReflectedOnlineReadinessSourcePaths);
        Type companionStateType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchOnlineCompanionSessionTextState",
            ReflectedOnlineReadinessSourcePaths);

        Dictionary<string, string> readinessControlsByProperty = new(StringComparer.Ordinal)
        {
            ["Headline"] = "PatchBenchOnlineReadinessHeadline",
            ["Slots"] = "PatchBenchOnlineReadinessSlots",
            ["MetadataSlots"] = "PatchBenchOnlineReadinessMetadataSlots",
            ["TargetModel"] = "PatchBenchOnlineTargetModel",
            ["ProofClass"] = "PatchBenchOnlineReadinessProofClass",
            ["NextProof"] = "PatchBenchOnlineReadinessNextProof",
            ["GateDetails"] = "PatchBenchOnlineReadinessGateDetails",
            ["ProofLadder"] = "PatchBenchOnlineProofLadder",
            ["CompanionModelDetails"] = "PatchBenchOnlineCompanionModelDetails",
            ["SecondHostSetupChecklist"] = "PatchBenchOnlineSecondHostSetupChecklist",
            ["BlockedActions"] = "PatchBenchOnlineReadinessBlockedActions",
            ["BlockedReasons"] = "PatchBenchOnlineReadinessBlockedReasons",
            ["LiveAttemptStatus"] = "PatchBenchOnlineLiveAttemptStatus",
            ["LiveAttemptBlockers"] = "PatchBenchOnlineLiveAttemptBlockers",
            ["LiveAttemptCommands"] = "PatchBenchOnlineLiveAttemptCommands",
            ["PromotionLockStatus"] = "PatchBenchOnlinePromotionLockStatus",
            ["SecondHostReadinessArtifactStatus"] = "PatchBenchOnlineReadinessArtifactStatus",
            ["GamepadReadinessArtifactStatus"] = "PatchBenchGamepadReadinessArtifactStatus",
            ["DualSafeCopyTopologyArtifactStatus"] = "PatchBenchDualSafeCopyTopologyArtifactStatus",
            ["DualSafeCopyTopologyBoundary"] = "PatchBenchDualSafeCopyTopologyBoundary",
            ["DualSafeCopyTopologyNextProofs"] = "PatchBenchDualSafeCopyTopologyNextProofs",
        };
        Dictionary<string, string> companionControlsByProperty = new(StringComparer.Ordinal)
        {
            ["PrepActionStatus"] = "PatchBenchOnlinePrepActionStatus",
            ["SessionStatus"] = "PatchBenchOnlineCompanionSessionStatus",
            ["LaunchPlan"] = "PatchBenchOnlineCompanionLaunchPlan",
            ["NextProofs"] = "PatchBenchOnlineCompanionNextProofs",
            ["NonClaims"] = "PatchBenchOnlineCompanionNonClaims",
        };

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(readinessRender, "PatchBenchOnlineReadinessText.Build("), Is.EqualTo(1));
            Assert.That(CountOccurrences(companionRender, "PatchBenchOnlineReadinessText.BuildCompanionSession("), Is.EqualTo(1));
            Assert.That(
                readinessRender.IndexOf("OnlineMultiplayerReadinessService.GetCurrentSummary(", StringComparison.Ordinal),
                Is.LessThan(readinessRender.IndexOf("PatchBenchOnlineReadinessText.Build(", StringComparison.Ordinal)),
                "BinaryPatchesPage should collect service state before handing presentation to the helper.");
            Assert.That(
                companionRender.IndexOf("OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(", StringComparison.Ordinal),
                Is.LessThan(companionRender.IndexOf("PatchBenchOnlineReadinessText.BuildCompanionSession(", StringComparison.Ordinal)),
                "BinaryPatchesPage should collect companion-session state before handing presentation to the helper.");
            Assert.That(
                readinessControlsByProperty.Keys.OrderBy(name => name, StringComparer.Ordinal),
                Is.EqualTo(GetPublicStringPropertyNames(readinessStateType).OrderBy(name => name, StringComparer.Ordinal)));
            Assert.That(
                companionControlsByProperty.Keys.OrderBy(name => name, StringComparer.Ordinal),
                Is.EqualTo(GetPublicStringPropertyNames(companionStateType).OrderBy(name => name, StringComparer.Ordinal)));
        });

        foreach ((string propertyName, string controlName) in readinessControlsByProperty)
        {
            Assert.That(
                readinessRender,
                Does.Contain($"{controlName}.Text = text.{propertyName};"),
                $"{controlName} should be assigned from PatchBenchOnlineReadinessTextState.{propertyName}.");
        }

        foreach ((string propertyName, string controlName) in companionControlsByProperty)
        {
            Assert.That(
                companionRender,
                Does.Contain($"{controlName}.Text = text.{propertyName};"),
                $"{controlName} should be assigned from PatchBenchOnlineCompanionSessionTextState.{propertyName}.");
        }

        AssertNoInlineLiteralTextAssignments(readinessRender, readinessControlsByProperty.Values, "online-readiness render path");
        AssertNoInlineLiteralTextAssignments(companionRender, companionControlsByProperty.Values, "companion-session render path");
    }

    [Test]
    public void BinaryPatchesPage_ButtonLabelsDoNotPromoteOnlineActionsBeforeProofGates()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string[] buttonBlocks = Regex.Matches(xaml, "<Button\\b[\\s\\S]*?(?:/>|>)")
            .Select(match => match.Value)
            .ToArray();
        string[] buttonContentLabels = buttonBlocks
            .Select(block => Regex.Match(block, "\\bContent\\s*=\\s*\"([^\"]*)\"", RegexOptions.IgnoreCase))
            .Where(match => match.Success)
            .Select(match => match.Groups[1].Value)
            .ToArray();
        const string forbiddenOnlineActionLabelPattern =
            "\\b(?:Host|Join|Matchmaking)\\b|Online session|Public matchmaking|\\bonline play\\b|\\bonline-ready\\b|\\bonline action\\b|\\bnetplay\\b";

        string[] blockedButtonContentLabels = buttonContentLabels
            .Where(label => Regex.IsMatch(label, forbiddenOnlineActionLabelPattern, RegexOptions.IgnoreCase))
            .ToArray();
        string[] blockedClickHandlers = Regex.Matches(
                $"{xaml}{Environment.NewLine}{code}",
                "\\b\\w*(?:Host|Join|Matchmaking|Netplay)\\w*Button_Click\\b")
            .Select(match => match.Value)
            .ToArray();
        string[] blockedRuntimeButtonContentStatements = Regex.Matches(
                code,
                "\\bPatchBench\\w*Button\\.Content\\s*=\\s*(?<rhs>[^;]*);",
                RegexOptions.Singleline)
            .Select(match => match.Value)
            .Where(statement => Regex.IsMatch(statement, forbiddenOnlineActionLabelPattern, RegexOptions.IgnoreCase))
            .ToArray();

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("This section is for technical review only. It does not launch online play"));
            Assert.That(xaml, Does.Contain("Not online multiplayer: no BEA launch, listener, invitation, remote input, Host/Join controls, distinct endpoint proof, or player-ready netplay."));
            Assert.That(xaml, Does.Not.Contain("PatchBenchHostOnlineSessionButton"));
            Assert.That(xaml, Does.Not.Contain("PatchBenchJoinOnlineSessionButton"));
            Assert.That(xaml, Does.Not.Contain("PatchBenchPublicMatchmakingButton"));
            Assert.That(blockedButtonContentLabels, Is.Empty, "PatchBench buttons must not expose Host/Join, matchmaking, online-ready, netplay, or online-play action labels before proof gates.");
            Assert.That(blockedClickHandlers, Is.Empty, "PatchBench must not grow Host/Join/Matchmaking/Netplay click handlers before proof gates.");
            Assert.That(blockedRuntimeButtonContentStatements, Is.Empty, "PatchBench code-behind must not set runtime button labels to online action wording before proof gates.");
        });
    }

    private static string[] GetPublicStringPropertyNames(Type type)
    {
        return type.GetProperties(BindingFlags.Instance | BindingFlags.Public)
            .Where(property => property.PropertyType == typeof(string))
            .Select(property => property.Name)
            .ToArray();
    }

    private static void AssertNoInlineLiteralTextAssignments(string source, IEnumerable<string> controlNames, string surfaceName)
    {
        string controlPattern = string.Join("|", controlNames.Select(Regex.Escape));
        MatchCollection inlineAssignments = Regex.Matches(
            source,
            $"\\b(?:{controlPattern})\\.Text\\s*=\\s*\"",
            RegexOptions.Singleline);
        string[] assignmentLocations = inlineAssignments
            .Select(match => $"line {source[..match.Index].Count(c => c == '\n') + 1}")
            .ToArray();
        Assert.That(
            assignmentLocations,
            Is.Empty,
            $"BinaryPatchesPage should not assign inline string literals in the {surfaceName}; route normal online-readiness copy through PatchBenchOnlineReadinessText.");
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

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }

    private static string ExtractCodeSlice(string code, string startToken, string endToken)
    {
        int start = code.IndexOf(startToken, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), $"Missing start token: {startToken}");
        int end = code.IndexOf(endToken, start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), $"Missing end token after {startToken}: {endToken}");
        return code[start..end];
    }
}
