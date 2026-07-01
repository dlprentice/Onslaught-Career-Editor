using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchSafeCopyReceiptTextTests
{
    private static readonly Lazy<string> HostJoinBoundaryValue = new(GetHostJoinBoundaryFromOutcomeHelper);
    private static string HostJoinBoundary => HostJoinBoundaryValue.Value;

    private static readonly string[] ReflectedReceiptTextSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyReceiptTextState.cs",
    ];

    private static readonly string[] ReflectedPageFormatterSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs",
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
    ];

    [Test]
    public void Build_FormatsPrimitiveReceiptLayoutAndNormalizesWhitespace()
    {
        object state = CreateState(
            "  Safe copy ready \r\n",
            [
                (" Profile ", " Enhanced Profile Preview\t"),
                ("Launch modifiers", "  -skipfmv   -level 850  "),
            ],
            [
                " Windowed mode ready ",
                " Savegames copied into this safe copy only; source savegames remain read-only. ",
            ],
            [
                $"{HostJoinBoundary}.",
                "No installed-game mutation.",
                "Original BEA.exe remains read-only.",
            ]);

        string output = InvokeBuild(state);

        string expected = string.Join(
            Environment.NewLine,
            "Safe copy ready",
            "Profile: Enhanced Profile Preview",
            "Launch modifiers: -skipfmv -level 850",
            string.Empty,
            "Included changes",
            "- Windowed mode ready",
            "- Savegames copied into this safe copy only; source savegames remain read-only.",
            string.Empty,
            "Still not included",
            $"- {HostJoinBoundary}.",
            "- No installed-game mutation.",
            "- Original BEA.exe remains read-only.");
        Assert.That(output, Is.EqualTo(expected));
        Assert.That(output.EndsWith(Environment.NewLine, StringComparison.Ordinal), Is.False);
    }

    [Test]
    public void Build_FailsClosedWhenPrimitiveStateContainsHostileDisplayValues()
    {
        string[] hostileValues =
        [
            @"Source: C:\Users\tester\AppData\Local\Onslaught\BEA.exe",
            @"Copy: \\server\share\BEA.exe",
            "proof-id=runtime-proof-12345",
            "runtime-proof-12345",
            "proof_root=private",
            "CommandPreview=Start-Process -FilePath BEA.exe",
            "Start-Process -FilePath BEA.exe",
            "SourcePath",
            "ManifestPath",
            "TargetGameRoot",
            "TargetExecutablePath",
            "source path",
            "manifest path",
            "target game root",
            "target executable path",
        ];

        foreach (string hostileValue in hostileValues)
        {
            foreach ((string field, object state) in CreateStatesWithHostileValue(hostileValue))
            {
                Exception? exception = CaptureBuildException(state);
                Assert.That(
                    exception,
                    Is.TypeOf<ArgumentException>(),
                    $"{field} should reject hostile receipt display text: {hostileValue}");
            }
        }
    }

    [Test]
    public void Build_RejectsRuntimeAssembledForbiddenSentinelsAcrossAllFields()
    {
        string proof = "proof";
        string command = "command";
        string preview = "preview";
        string source = "source";
        string manifest = "manifest";
        string target = "target";
        string online = "online";
        string host = "Host";
        string join = "Join";
        string[] hostileValues =
        [
            string.Concat(proof, " ", "id"),
            $"{proof}{"-"}root",
            string.Concat("runtime", " ", proof),
            $"{command} {preview}",
            string.Concat("Start", " ", "Process"),
            $"{source} {"path"}",
            string.Concat(manifest, " ", "path"),
            $"{target} {"game"} {"root"}",
            $"{target} {"executable"} {"path"}",
            string.Concat(online, " ", "ready"),
            $"{host} {" / "} {join} enabled",
            $"{host}{"-"}{join} available",
        ];

        foreach (string hostileValue in hostileValues)
        {
            foreach ((string field, object state) in CreateStatesWithHostileValue(hostileValue))
            {
                Exception? exception = CaptureBuildException(state);
                Assert.That(
                    exception,
                    Is.TypeOf<ArgumentException>(),
                    $"{field} should reject runtime-assembled hostile receipt text: {hostileValue}");
            }
        }
    }

    [Test]
    public void Build_EnforcesManifestFilenameDisplayPolicy()
    {
        string[] unsafeManifestFilenameValues =
        [
            "onslaught-profile-manifest.json",
            "Profile manifest: onslaught-profile-manifest.json",
            "Manifest file onslaught-profile-manifest.json",
        ];

        foreach (string unsafeManifestFilenameValue in unsafeManifestFilenameValues)
        {
            foreach ((string field, object state) in CreateStatesWithHostileValue(unsafeManifestFilenameValue))
            {
                Exception? exception = CaptureBuildException(state);
                Assert.That(
                    exception,
                    Is.TypeOf<ArgumentException>(),
                    $"{field} should reject raw manifest filename display text: {unsafeManifestFilenameValue}");
            }
        }

        string output = InvokeBuild(CreateState(
            "Safe copy ready",
            [("Profile manifest", "written for the safe copy")],
            ["Safe-copy profile manifest was written."],
            [$"{HostJoinBoundary}."]));

        Assert.That(output, Does.Contain("Profile manifest: written for the safe copy"));
    }

    [Test]
    public void Build_RejectsOnlineReadyPromotionWordingButPreservesBoundaryLimits()
    {
        string[] unsafeOnlineValues =
        [
            "online-ready",
            "online ready",
            "OnlineReady",
            "online_ready",
            "online play ready",
            "online play available",
            "Online session is ready",
            "online session ready",
            "enable Host now",
            "enable Join now",
            "Enable: Host now",
            "Enable: Join now",
            "Public matchmaking available",
            "public-matchmaking available",
            "PublicMatchmaking ready",
            "netplay ready",
            "net play ready",
            "Host/Join available",
            "Host/Join enabled",
            "HOST/JOIN AVAILABLE",
            "Host / Join enabled",
            "Host-Join ready",
            "Host and Join available",
        ];

        foreach (string unsafeOnlineValue in unsafeOnlineValues)
        {
            Exception? exception = CaptureBuildException(CreateState(
                "Safe copy ready",
                [("Profile", "Enhanced Profile Preview")],
                ["Windowed mode ready"],
                [unsafeOnlineValue]));
            Assert.That(exception, Is.TypeOf<ArgumentException>(), unsafeOnlineValue);
        }

        string output = InvokeBuild(CreateState(
            "Safe copy ready",
            [("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            [
                $"{HostJoinBoundary}.",
                "No installed-game mutation.",
                "Original BEA.exe remains read-only.",
            ]));

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(output, HostJoinBoundary), Is.EqualTo(1));
            Assert.That(output, Does.Contain("No installed-game mutation."));
            Assert.That(output, Does.Contain("Original BEA.exe remains read-only."));
        });
    }

    [Test]
    public void Build_RejectsProofAndCommandPreviewVariants()
    {
        string[] unsafeValues =
        [
            "proof-id",
            "PROOF-ID",
            "proof_id",
            "proof id",
            "ProofId",
            "proof-root",
            "proof root",
            "ProofRoot",
            "runtime-proof",
            "runtime proof",
            "CommandPreview",
            "commandpreview",
            "command-preview",
            "command preview",
            "Command Preview: launch preview",
            "Start-Process",
            "Start Process",
        ];

        foreach (string unsafeValue in unsafeValues)
        {
            foreach ((string field, object state) in CreateStatesWithHostileValue(unsafeValue))
            {
                Exception? exception = CaptureBuildException(state);
                Assert.That(
                    exception,
                    Is.TypeOf<ArgumentException>(),
                    $"{field} should reject proof/command sentinel variant: {unsafeValue}");
            }
        }
    }

    [Test]
    public void Build_AllowsBenignHostJoinPartialWordsAndNegativeBoundaryCopy()
    {
        string output = InvokeBuild(CreateState(
            "Safe copy ready",
            [("Profile", "Enhanced Profile Preview")],
            [
                "Windowed mode ready",
                "ghost marker removed from the safe-copy note",
                "joinery wording is unrelated to online actions.",
            ],
            [
                $"{HostJoinBoundary}.",
                "Host/Join remain unavailable.",
                "No installed-game mutation.",
            ]));

        Assert.Multiple(() =>
        {
            Assert.That(output, Does.Contain("ghost marker"));
            Assert.That(output, Does.Contain("joinery wording"));
            Assert.That(output, Does.Contain($"{HostJoinBoundary}."));
            Assert.That(output, Does.Contain("Host/Join remain unavailable."));
        });
    }

    [Test]
    public void PageFormatter_MatchesHelperForNormalizedReceiptWhenBoundaryPresent()
    {
        var receipt = new GameProfilePrepareReceipt(
            "Safe copy ready",
            [
                new GameProfileReceiptLine("Profile", "Enhanced Profile Preview"),
                new GameProfileReceiptLine("Launch modifiers", "-skipfmv -level 850"),
            ],
            [
                "Windowed mode ready",
                "Savegames copied into this safe copy only; source savegames remain read-only.",
            ],
            [
                $"{HostJoinBoundary}.",
                "No installed-game mutation.",
            ]);
        object helperState = CreateState(
            receipt.Headline,
            receipt.Lines.Select(line => (line.Label, line.Value)).ToArray(),
            receipt.IncludedChanges.ToArray(),
            receipt.StillNotIncluded.ToArray());

        string pageOutput = InvokePageReceiptFormatter(receipt);
        string helperOutput = InvokeBuild(helperState);

        Assert.That(helperOutput, Is.EqualTo(pageOutput));
    }

    [Test]
    public void PageFormatterAndHelper_DocumentHostJoinBoundaryInjectionDeltaBeforeWiring()
    {
        var missingBoundaryReceipt = new GameProfilePrepareReceipt(
            "Safe copy ready",
            [new GameProfileReceiptLine("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            ["No installed-game mutation."]);
        object helperStateWithoutBoundary = CreateState(
            missingBoundaryReceipt.Headline,
            missingBoundaryReceipt.Lines.Select(line => (line.Label, line.Value)).ToArray(),
            missingBoundaryReceipt.IncludedChanges.ToArray(),
            missingBoundaryReceipt.StillNotIncluded.ToArray());
        object helperStateWithBoundary = CreateState(
            missingBoundaryReceipt.Headline,
            missingBoundaryReceipt.Lines.Select(line => (line.Label, line.Value)).ToArray(),
            missingBoundaryReceipt.IncludedChanges.ToArray(),
            [.. missingBoundaryReceipt.StillNotIncluded, $"{HostJoinBoundary}."]);

        string pageOutput = InvokePageReceiptFormatter(missingBoundaryReceipt);
        string helperOutputWithoutBoundary = InvokeBuild(helperStateWithoutBoundary);
        string helperOutputWithBoundary = InvokeBuild(helperStateWithBoundary);

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(pageOutput, HostJoinBoundary), Is.EqualTo(1));
            Assert.That(CountOccurrences(helperOutputWithoutBoundary, HostJoinBoundary), Is.EqualTo(0));
            Assert.That(helperOutputWithBoundary, Is.EqualTo(pageOutput));
        });
    }

    [Test]
    public void HostJoinBoundaryConstant_ComesFromSafeCopyOutcomeHelper()
    {
        Assert.That(HostJoinBoundary, Is.EqualTo("No Host/Join or online multiplayer"));
    }

    [Test]
    public void PageFormatter_AppendsHostJoinBoundaryWhenMissingAndDoesNotDuplicateWhenPresent()
    {
        string missingBoundaryOutput = InvokePageReceiptFormatter(new GameProfilePrepareReceipt(
            "Safe copy ready",
            [new GameProfileReceiptLine("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            ["No installed-game mutation."]));
        string presentBoundaryOutput = InvokePageReceiptFormatter(new GameProfilePrepareReceipt(
            "Safe copy ready",
            [new GameProfileReceiptLine("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            [$"{HostJoinBoundary}.", "No installed-game mutation."]));

        Assert.Multiple(() =>
        {
            Assert.That(CountOccurrences(missingBoundaryOutput, HostJoinBoundary), Is.EqualTo(1));
            Assert.That(missingBoundaryOutput, Does.Contain($"- {HostJoinBoundary}."));
            Assert.That(CountOccurrences(presentBoundaryOutput, HostJoinBoundary), Is.EqualTo(1));
            Assert.That(presentBoundaryOutput, Does.Contain($"- {HostJoinBoundary}."));
        });
    }

    [Test]
    public void ReceiptFormatterScaffold_StaysPrimitiveUnwiredAndBehaviorFree()
    {
        string helper = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Helpers", "PatchBenchSafeCopyReceiptText.cs");
        string model = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Models", "PatchBenchSafeCopyReceiptTextState.cs");
        string page = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(page, Does.Not.Contain("PatchBenchSafeCopyReceiptText.Build("));
            Assert.That(page, Does.Contain("GameProfilePreflightService.BuildPrepareReceipt("));
            AssertNoOwnershipTokens(helper, "receipt helper");
            AssertNoOwnershipTokens(model, "receipt model");
        });
    }

    private static IEnumerable<(string Field, object State)> CreateStatesWithHostileValue(string hostileValue)
    {
        yield return ("headline", CreateState(
            hostileValue,
            [("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            [$"{HostJoinBoundary}."]));
        yield return ("line label", CreateState(
            "Safe copy ready",
            [(hostileValue, "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            [$"{HostJoinBoundary}."]));
        yield return ("line value", CreateState(
            "Safe copy ready",
            [("Profile", hostileValue)],
            ["Windowed mode ready"],
            [$"{HostJoinBoundary}."]));
        yield return ("included change", CreateState(
            "Safe copy ready",
            [("Profile", "Enhanced Profile Preview")],
            [hostileValue],
            [$"{HostJoinBoundary}."]));
        yield return ("still-not-included limit", CreateState(
            "Safe copy ready",
            [("Profile", "Enhanced Profile Preview")],
            ["Windowed mode ready"],
            [hostileValue]));
    }

    private static object CreateState(
        string headline,
        IReadOnlyList<(string Label, string Value)> lines,
        IReadOnlyList<string> includedChanges,
        IReadOnlyList<string> stillNotIncluded)
    {
        Type lineType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchReceiptLineTextState",
            ReflectedReceiptTextSourcePaths);
        Array lineArray = Array.CreateInstance(lineType, lines.Count);
        for (int i = 0; i < lines.Count; i++)
        {
            lineArray.SetValue(CreateLine(lineType, lines[i].Label, lines[i].Value), i);
        }

        Type stateType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchSafeCopyReceiptTextState",
            ReflectedReceiptTextSourcePaths);

        return Activator.CreateInstance(
            stateType,
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
            binder: null,
            args: [headline, lineArray, includedChanges.ToArray(), stillNotIncluded.ToArray()],
            culture: null)
            ?? throw new InvalidOperationException($"Could not create {stateType.FullName}.");
    }

    private static object CreateLine(Type lineType, string label, string value)
    {
        return Activator.CreateInstance(
            lineType,
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
            binder: null,
            args: [label, value],
            culture: null)
            ?? throw new InvalidOperationException($"Could not create {lineType.FullName}.");
    }

    private static string InvokeBuild(object state)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            "Build",
            state);
    }

    private static Exception? CaptureBuildException(object state)
    {
        try
        {
            _ = InvokeBuild(state);
            return null;
        }
        catch (TargetInvocationException ex)
        {
            return ex.InnerException ?? ex;
        }
    }

    private static string InvokePageReceiptFormatter(GameProfilePrepareReceipt receipt)
    {
        Type pageType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Pages.BinaryPatchesPage",
            ReflectedPageFormatterSourcePaths);
        MethodInfo method = pageType.GetMethod("BuildSafeCopyReceiptText", BindingFlags.Static | BindingFlags.NonPublic)
            ?? throw new InvalidOperationException("Missing BinaryPatchesPage.BuildSafeCopyReceiptText.");
        return (string)(method.Invoke(null, [receipt])
            ?? throw new InvalidOperationException("BinaryPatchesPage.BuildSafeCopyReceiptText returned null."));
    }

    private static Type GetHelperType()
    {
        return ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyReceiptText",
            ReflectedReceiptTextSourcePaths);
    }

    private static string GetHostJoinBoundaryFromOutcomeHelper()
    {
        Type type = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyOutcomeText",
            ReflectedPageFormatterSourcePaths);
        FieldInfo field = type.GetField("HostJoinReceiptBoundary", BindingFlags.Static | BindingFlags.Public)
            ?? throw new InvalidOperationException("Missing PatchBenchSafeCopyOutcomeText.HostJoinReceiptBoundary.");
        return (string)(field.GetRawConstantValue()
            ?? throw new InvalidOperationException("PatchBenchSafeCopyOutcomeText.HostJoinReceiptBoundary was null."));
    }

    private static void AssertNoOwnershipTokens(string source, string label)
    {
        string[] forbiddenTokens =
        [
            "GameProfile",
            "BuildPrepareReceipt",
            "File.",
            "Directory.",
            "Path.",
            "Process",
            "Task",
            "async ",
            "await ",
            "BinaryPatch",
            "LaunchPlan",
            "CommandPreview",
            "OnlineMultiplayer",
            "HostOnlineSession",
            "JoinOnlineSession",
        ];

        foreach (string token in forbiddenTokens)
        {
            Assert.That(source, Does.Not.Contain(token), $"{label} must not own behavior token {token}");
        }
    }

    private static string ReadRepoFile(params string[] parts)
    {
        string path = Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {string.Join("/", parts)}");
        return File.ReadAllText(path);
    }

    private static int CountOccurrences(string source, string token)
    {
        int count = 0;
        int index = 0;
        while ((index = source.IndexOf(token, index, StringComparison.OrdinalIgnoreCase)) >= 0)
        {
            count++;
            index += token.Length;
        }

        return count;
    }
}
