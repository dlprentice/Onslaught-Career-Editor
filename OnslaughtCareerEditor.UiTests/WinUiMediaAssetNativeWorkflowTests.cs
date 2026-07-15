using System.Diagnostics;
using System.Drawing;
using System.Security.Cryptography;
using System.Text.Json;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public class WinUiMediaAssetNativeWorkflowTests
{
    private const string RunIdEnvironment = "ONSLAUGHT_MEDIA_ASSET_NATIVE_ACCEPTANCE_RUN_ID";
    private const string ExpectedExecutableHashEnvironment = "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_EXE_SHA256";
    private const string ExpectedProductHashEnvironment = "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_DLL_SHA256";
    private const string ExpectedPayloadHashEnvironment = "ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_PAYLOAD_SHA256";
    private const string GameDirectoryCandidatesEnvironment = "ONSLAUGHT_GAME_DIR_CANDIDATES";
    private const string SteamRootCandidatesEnvironment = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";
    private static readonly Rectangle NormalBounds = new(16, 16, 1100, 900);
    private static readonly Rectangle CompactBounds = new(16, 16, 760, 820);

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Runs generated Media and Asset Library catalog workflows and publishes receipt-bound ignored/local evidence without playback.")]
    [Apartment(ApartmentState.STA)]
    public void MediaAndAssetLibrary_PublishDeterministicNativeEvidence()
    {
        string? runId = Environment.GetEnvironmentVariable(RunIdEnvironment);
        Assert.That(Guid.TryParseExact(runId, "N", out _), Is.True);
        Assert.That(runId, Is.EqualTo(runId!.ToLowerInvariant()));
        string expectedExecutableHash = RequireUpperSha256(ExpectedExecutableHashEnvironment);
        string expectedProductHash = RequireUpperSha256(ExpectedProductHashEnvironment);
        string expectedPayloadHash = RequireUpperSha256(ExpectedPayloadHashEnvironment);

        string repoRoot = TestFixturePaths.RepoRoot;
        string executablePath = Path.Combine(
            repoRoot,
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.exe");
        ValidateApplicationPayload(executablePath, expectedPayloadHash);
        string evidenceRoot = Path.Combine(repoRoot, "local-lab", "winui-media-asset-native-workflow");
        string runName = $"media-asset-x-{runId}";
        string stagingDirectory = Path.Combine(evidenceRoot, $".{runName}.partial");
        string acceptedDirectory = Path.Combine(evidenceRoot, runName);
        MediaAssetOwnedPathGuard.RequireEvidenceRoot(repoRoot, evidenceRoot);
        Assert.That(Directory.Exists(stagingDirectory), Is.False, "Media/Asset partial destination must be fresh.");
        Assert.That(Directory.Exists(acceptedDirectory), Is.False, "Media/Asset accepted destination must be fresh.");
        Directory.CreateDirectory(stagingDirectory);
        MediaAssetOwnedPathGuard.RequireEvidenceRoot(repoRoot, evidenceRoot);
        MediaAssetOwnedPathGuard.RequireDirectChild(evidenceRoot, stagingDirectory);

        MediaAssetNativeFixture fixture = MediaAssetNativeFixtureBuilder.Build(
            Path.Combine(stagingDirectory, "fixtures"));
        var captures = new List<MediaAssetCaptureEvidence>();
        var workflows = new List<MediaAssetWorkflowEvidence>();
        RunMediaAudioWorkflow(
            executablePath,
            stagingDirectory,
            fixture,
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            captures,
            workflows);
        RunMediaVideoWorkflow(
            executablePath,
            stagingDirectory,
            fixture,
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            captures,
            workflows);
        RunAssetLibraryWorkflow(
            executablePath,
            stagingDirectory,
            fixture,
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            captures,
            workflows);
        ValidateApplicationPayload(executablePath, expectedPayloadHash);

        var manifest = new MediaAssetAcceptanceManifest(
            MediaAssetNativeEvidenceContract.SchemaVersion,
            runId!,
            MediaAssetNativeEvidenceContract.InteractionMode,
            new MediaAssetFixtureEvidence("fixtures", fixture.Files),
            captures,
            workflows);
        MediaAssetNativeFixtureBuilder.Validate(fixture);
        MediaAssetOwnedPathGuard.RequireEvidenceRoot(repoRoot, evidenceRoot);
        MediaAssetOwnedPathGuard.RequireDirectChild(evidenceRoot, stagingDirectory);
        MediaAssetNativeEvidenceAcceptance.Publish(stagingDirectory, acceptedDirectory, manifest);
    }

    private static void RunMediaAudioWorkflow(
        string executablePath,
        string stagingDirectory,
        MediaAssetNativeFixture fixture,
        string expectedExecutableHash,
        string expectedProductHash,
        string expectedPayloadHash,
        ICollection<MediaAssetCaptureEvidence> captures,
        ICollection<MediaAssetWorkflowEvidence> workflows)
    {
        string appDataDirectory = PrepareAppData(
            Path.Combine(stagingDirectory, "a"),
            fixture.MediaGameDirectory,
            lastMediaSubTab: 0);
        IReadOnlyDictionary<string, string> environment = BuildEnvironment(
            Path.Combine(stagingDirectory, "sa"),
            ("ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB", "0"));
        using var session = MediaAssetNativeSession.Launch(
            executablePath,
            appDataDirectory,
            "media",
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            environment);
        Window window = session.Window;
        WaitForName(window, "MediaAudioGameDirectorySummary", "media-game");
        SetTextBox(window, "MediaAudioSearchBox", "TUTORIAL_intro");
        SelectNamedItem(window, "MediaAudioTreeView", ControlType.TreeItem, "TUTORIAL_intro");
        WaitForName(window, "MediaAudioNowPlaying", "TUTORIAL_intro");
        string sourceSummary = RequireName(window, "MediaAudioSourceSummary");
        Assert.Multiple(() =>
        {
            Assert.That(sourceSummary, Is.EqualTo("Tutorial • TUTORIAL_intro.ogg"));
            Assert.That(FindByAutomationId(window, "MediaAudioPlayButton").IsEnabled, Is.True);
            Assert.That(FindByAutomationId(window, "MediaAudioPauseButton").IsEnabled, Is.False);
            Assert.That(FindByAutomationId(window, "MediaAudioStopButton").IsEnabled, Is.False);
            Assert.That(HasPlaybackModulesLoaded(session.Identity.ProcessId), Is.False);
        });

        AddCaptures(
            captures,
            session,
            stagingDirectory,
            "media-audio",
            "audio-selected",
            "MediaAudioSearchBox",
            ["MediaAudioSearchBox", "MediaAudioTreeView", "MediaAudioNowPlaying", "MediaAudioSourceSummary"],
            "media-audio-selected-normal.png",
            "media-audio-selected-760.png");
        workflows.Add(new MediaAssetWorkflowEvidence(
            "media-audio",
            MediaAssetNativeVisualCapture.ToEvidence(session),
            PlaybackModulesLoaded: false,
            [
                new MediaAssetSelectionEvidence(
                    "audio-selected",
                    RequireName(window, "MediaAudioNowPlaying"),
                    sourceSummary,
                    "play-enabled-no-playback"),
            ]));
    }

    private static void RunMediaVideoWorkflow(
        string executablePath,
        string stagingDirectory,
        MediaAssetNativeFixture fixture,
        string expectedExecutableHash,
        string expectedProductHash,
        string expectedPayloadHash,
        ICollection<MediaAssetCaptureEvidence> captures,
        ICollection<MediaAssetWorkflowEvidence> workflows)
    {
        string appDataDirectory = PrepareAppData(
            Path.Combine(stagingDirectory, "v"),
            fixture.MediaGameDirectory,
            lastMediaSubTab: 1);
        IReadOnlyDictionary<string, string> environment = BuildEnvironment(
            Path.Combine(stagingDirectory, "sv"),
            ("ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB", "1"));
        using var session = MediaAssetNativeSession.Launch(
            executablePath,
            appDataDirectory,
            "media",
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            environment);
        Window window = session.Window;
        FindByAutomationId(window, "MediaVideoSearchBox");
        SetTextBox(window, "MediaVideoSearchBox", "UsTheMovie");
        SelectNamedItem(window, "MediaVideoTreeView", ControlType.TreeItem, "Credits Video");
        WaitForName(window, "MediaVideoSelected", "Credits Video");
        string sourceSummary = RequireName(window, "MediaVideoSourceSummary");
        Assert.Multiple(() =>
        {
            Assert.That(sourceSummary, Is.EqualTo("Main Videos • UsTheMovie.vid"));
            Assert.That(RequireName(window, "MediaVideoPlayerStatus"), Is.EqualTo("Video player starts on demand"));
            Assert.That(FindByAutomationId(window, "MediaVideoPlayButton").IsEnabled, Is.True);
            Assert.That(FindByAutomationId(window, "MediaVideoPauseButton").IsEnabled, Is.False);
            Assert.That(FindByAutomationId(window, "MediaVideoStopButton").IsEnabled, Is.False);
            Assert.That(HasPlaybackModulesLoaded(session.Identity.ProcessId), Is.False);
        });

        AddCaptures(
            captures,
            session,
            stagingDirectory,
            "media-video",
            "video-selected",
            "MediaVideoSearchBox",
            ["MediaVideoSearchBox", "MediaVideoTreeView", "MediaVideoPlayerStatus", "MediaVideoSelected", "MediaVideoSourceSummary"],
            "media-video-selected-normal.png",
            "media-video-selected-760.png");
        bool playbackModulesLoaded = HasPlaybackModulesLoaded(session.Identity.ProcessId);
        Assert.That(playbackModulesLoaded, Is.False);
        workflows.Add(new MediaAssetWorkflowEvidence(
            "media-video",
            MediaAssetNativeVisualCapture.ToEvidence(session),
            playbackModulesLoaded,
            [
                new MediaAssetSelectionEvidence(
                    "video-selected",
                    RequireName(window, "MediaVideoSelected"),
                    sourceSummary,
                    "play-enabled-deferred-no-playback"),
            ]));
    }

    private static void RunAssetLibraryWorkflow(
        string executablePath,
        string stagingDirectory,
        MediaAssetNativeFixture fixture,
        string expectedExecutableHash,
        string expectedProductHash,
        string expectedPayloadHash,
        ICollection<MediaAssetCaptureEvidence> captures,
        ICollection<MediaAssetWorkflowEvidence> workflows)
    {
        string appDataDirectory = PrepareAppData(
            Path.Combine(stagingDirectory, "l"),
            gameDirectory: null,
            lastMediaSubTab: 0);
        IReadOnlyDictionary<string, string> environment = BuildEnvironment(
            Path.Combine(stagingDirectory, "sl"),
            ("ONSLAUGHT_WINUI_TEST_INITIAL_ASSET_TAB", "0"),
            ("ONSLAUGHT_WINUI_TEST_ASSET_CATALOG", fixture.AssetCatalogPath),
            ("ONSLAUGHT_WINUI_TEST_GOODIE_SAVE", string.Empty));
        using var session = MediaAssetNativeSession.Launch(
            executablePath,
            appDataDirectory,
            "assets",
            expectedExecutableHash,
            expectedProductHash,
            expectedPayloadHash,
            environment);
        Window window = session.Window;
        WaitForName(window, "AssetCatalogSummary", "1 textures, 1 loose meshes, 1 embedded meshes, 1 goodies");
        SetTextBox(window, "AssetSearchBox", "texture_one");
        WaitForName(window, "AssetSelectedTitle", "Texture One");
        string textureSummary = RequireName(window, "AssetSelectedSummary");
        Assert.Multiple(() =>
        {
            Assert.That(textureSummary, Is.EqualTo("fixture; 1 packed references; export available."));
            Assert.That(FindByAutomationId(window, "AssetOpenExportButton").IsEnabled, Is.True);
            Assert.That(HasPlaybackModulesLoaded(session.Identity.ProcessId), Is.False);
        });

        AddCaptures(
            captures,
            session,
            stagingDirectory,
            "asset-library",
            "texture-selected",
            "AssetSearchBox",
            ["AssetCatalogSummary", "AssetItemsList", "AssetSelectedTitle", "AssetTexturePreviewImage"],
            "asset-texture-selected-normal.png",
            "asset-texture-selected-760.png");

        InvokeButton(window, "AssetMeshesTabButton");
        SetTextBox(window, "AssetSearchBox", "fixture_mesh");
        WaitForName(window, "AssetSelectedTitle", "fixture_mesh.msh");
        string modelSummary = RequireName(window, "AssetSelectedSummary");
        string modelDetail = RequireName(window, "AssetModelMetadataInline");
        Assert.Multiple(() =>
        {
            Assert.That(
                modelSummary,
                Is.EqualTo("1 packed references; FBX export available. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review."));
            Assert.That(
                modelDetail,
                Is.EqualTo("Binary FBX 7400; 3 vertices; 3 polygon index entries; UV mapping: no coordinate data recorded."));
            Assert.That(RequireName(window, "AssetModelWireframeStatus"), Does.StartWith("Wireframe preview available"));
            Assert.That(HasPlaybackModulesLoaded(session.Identity.ProcessId), Is.False);
        });

        AddCaptures(
            captures,
            session,
            stagingDirectory,
            "asset-library",
            "model-wireframe",
            "AssetMeshesTabButton",
            ["AssetItemsList", "AssetPreviewTitle", "AssetModelWireframeStatus", "AssetModelWireframePanel"],
            "asset-model-wireframe-normal.png",
            "asset-model-wireframe-760.png",
            previewScrollHostAutomationId: "AssetPreviewScrollViewer");
        workflows.Add(new MediaAssetWorkflowEvidence(
            "asset-library",
            MediaAssetNativeVisualCapture.ToEvidence(session),
            PlaybackModulesLoaded: false,
            [
                new MediaAssetSelectionEvidence(
                    "texture-selected",
                    "Texture One",
                    textureSummary,
                    "texture:fixture/texture_one.tga"),
                new MediaAssetSelectionEvidence(
                    "model-wireframe",
                    RequireName(window, "AssetSelectedTitle"),
                    modelSummary,
                    modelDetail),
            ]));
    }

    private static void AddCaptures(
        ICollection<MediaAssetCaptureEvidence> captures,
        MediaAssetNativeSession session,
        string stagingDirectory,
        string workflow,
        string phase,
        string focusAutomationId,
        IReadOnlyList<string> markers,
        string normalFileName,
        string compactFileName,
        string? previewScrollHostAutomationId = null)
    {
        captures.Add(Capture(
            session,
            workflow,
            phase,
            focusAutomationId,
            NormalBounds,
            stagingDirectory,
            normalFileName,
            markers,
            previewScrollHostAutomationId));
        captures.Add(Capture(
            session,
            workflow,
            phase,
            focusAutomationId,
            CompactBounds,
            stagingDirectory,
            compactFileName,
            markers,
            previewScrollHostAutomationId));
    }

    private static MediaAssetCaptureEvidence Capture(
        MediaAssetNativeSession session,
        string workflow,
        string phase,
        string focusAutomationId,
        Rectangle bounds,
        string stagingDirectory,
        string fileName,
        IReadOnlyList<string> markers,
        string? previewScrollHostAutomationId)
    {
        return MediaAssetNativeVisualCapture.Capture(
            session,
            workflow,
            phase,
            focusAutomationId,
            bounds,
            Path.Combine(stagingDirectory, fileName),
            markers,
            () => RealizeMarkers(session.Window, markers, previewScrollHostAutomationId));
    }

    private static void RealizeMarkers(
        Window window,
        IReadOnlyList<string> markerAutomationIds,
        string? previewScrollHostAutomationId)
    {
        if (!string.IsNullOrWhiteSpace(previewScrollHostAutomationId))
        {
            AutomationElement scrollHost = FindByAutomationId(window, previewScrollHostAutomationId);
            Assert.That(scrollHost.Patterns.Scroll.IsSupported, Is.True);
            Assert.That(
                scrollHost.Patterns.Scroll.Pattern.HorizontallyScrollable.Value,
                Is.False,
                $"{previewScrollHostAutomationId} must not expose horizontal overflow.");
        }

        foreach (string automationId in markerAutomationIds)
        {
            AutomationElement element = FindByAutomationId(window, automationId);
            if (element.Patterns.ScrollItem.IsSupported)
            {
                element.Patterns.ScrollItem.Pattern.ScrollIntoView();
            }
        }

        Thread.Sleep(250);
    }

    private static IReadOnlyDictionary<string, string> BuildEnvironment(
        string emptySteamRoot,
        params (string Name, string Value)[] additions)
    {
        Directory.CreateDirectory(emptySteamRoot);
        var environment = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [GameDirectoryCandidatesEnvironment] = string.Empty,
            [SteamRootCandidatesEnvironment] = Path.GetFullPath(emptySteamRoot),
        };
        foreach ((string name, string value) in additions)
        {
            environment[name] = value;
        }
        return environment;
    }

    private static string PrepareAppData(
        string appDataDirectory,
        string? gameDirectory,
        int lastMediaSubTab)
    {
        string configDirectory = Path.Combine(appDataDirectory, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDirectory);
        string configPath = Path.Combine(configDirectory, "config.json");
        string gameDirectoryJson = JsonSerializer.Serialize(gameDirectory);
        string json = $$"""
            {
              "gameDirectory": {{gameDirectoryJson}},
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1100,
              "windowHeight": 900,
              "lastTab": 0,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": {{lastMediaSubTab}},
              "assetCatalogPath": null,
              "allowBackgroundAudio": false,
              "allowBackgroundVideo": false,
              "preventAudioVideoOverlap": true
            }
            """;
        using FileStream stream = new(configPath, FileMode.CreateNew, FileAccess.Write, FileShare.None);
        using var writer = new StreamWriter(stream, new System.Text.UTF8Encoding(false), leaveOpen: true);
        writer.Write(json);
        writer.Flush();
        stream.Flush(flushToDisk: true);
        return appDataDirectory;
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        Assert.That(textBox.Patterns.Value.IsSupported, Is.True);
        Assert.That(textBox.Patterns.Value.Pattern.IsReadOnly.Value, Is.False);
        textBox.Focus();
        textBox.Patterns.Value.Pattern.SetValue(text);
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(textBox.Patterns.Value.Pattern.Value.Value, text, StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True);
    }

    private static void SelectNamedItem(
        Window window,
        string rootAutomationId,
        ControlType itemControlType,
        string namePrefix)
    {
        AutomationElement root = FindByAutomationId(window, rootAutomationId);
        AutomationElement? item = Retry.WhileNull(
            () => root.FindAllDescendants()
                .FirstOrDefault(candidate =>
                    candidate.ControlType == itemControlType &&
                    TryName(candidate)?.StartsWith(namePrefix, StringComparison.OrdinalIgnoreCase) == true),
            TimeSpan.FromSeconds(15)).Result;
        Assert.That(item, Is.Not.Null, $"Expected {rootAutomationId} item starting with {namePrefix}.");
        Assert.That(item!.Patterns.SelectionItem.IsSupported, Is.True);
        if (item.Patterns.ScrollItem.IsSupported)
        {
            item.Patterns.ScrollItem.Pattern.ScrollIntoView();
        }
        item.Patterns.SelectionItem.Pattern.Select();
        Assert.That(
            Retry.WhileFalse(
                () => item.Patterns.SelectionItem.Pattern.IsSelected.Value,
                TimeSpan.FromSeconds(5)).Success,
            Is.True);
    }

    private static void InvokeButton(Window window, string automationId)
    {
        AutomationElement button = FindByAutomationId(window, automationId);
        Assert.That(button.Patterns.Invoke.IsSupported, Is.True);
        button.Patterns.Invoke.Pattern.Invoke();
    }

    private static void WaitForName(Window window, string automationId, string expected)
    {
        string actual = string.Empty;
        bool matched = Retry.WhileFalse(
            () =>
            {
                actual = TryName(FindByAutomationId(window, automationId)) ?? string.Empty;
                return string.Equals(actual, expected, StringComparison.Ordinal);
            },
            TimeSpan.FromSeconds(15)).Success;
        Assert.That(matched, Is.True, $"Expected {automationId} name '{expected}', actual '{actual}'.");
    }

    private static string RequireName(Window window, string automationId)
    {
        string? name = TryName(FindByAutomationId(window, automationId));
        Assert.That(name, Is.Not.Null.And.Not.Empty, $"Expected {automationId} to expose a UIA name.");
        return name!;
    }

    private static string? TryName(AutomationElement element)
    {
        try
        {
            return element.Name;
        }
        catch
        {
            return null;
        }
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () =>
            {
                try
                {
                    return window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected Media/Asset automation element: {automationId}");
        return element!;
    }

    private static bool HasPlaybackModulesLoaded(int processId)
    {
        using Process process = Process.GetProcessById(processId);
        return process.Modules
            .Cast<ProcessModule>()
            .Select(module => Path.GetFileName(module.FileName))
            .Any(fileName =>
                string.Equals(fileName, "libvlc.dll", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(fileName, "libvlccore.dll", StringComparison.OrdinalIgnoreCase));
    }

    private static string RequireUpperSha256(string environmentName)
    {
        string? value = Environment.GetEnvironmentVariable(environmentName);
        Assert.That(value, Does.Match("^[0-9A-F]{64}$"), $"Missing or malformed {environmentName}.");
        return value!;
    }

    private static void ValidateApplicationPayload(string executablePath, string expectedPayloadHash)
    {
        string applicationRoot = Path.GetDirectoryName(Path.GetFullPath(executablePath))!;
        Assert.That(
            MediaAssetNativeApplicationPayload.Compute(applicationRoot),
            Is.EqualTo(expectedPayloadHash),
            "The Toolkit-owned native application payload changed during Media/Asset acceptance.");
    }
}
