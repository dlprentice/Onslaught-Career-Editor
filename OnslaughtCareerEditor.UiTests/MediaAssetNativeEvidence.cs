namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetNativeEvidenceContract
{
    internal const int SchemaVersion = 1;
    internal const string InteractionMode =
        "UIA Value/SelectionItem/ScrollItem/Scroll/Focus/Invoke; no keyboard, pointer, playback, reveal, browse, clipboard, export, or package actions";

    internal static readonly IReadOnlyList<MediaAssetExpectedCapture> ExpectedCaptures =
    [
        Expected(
            "media-audio-selected-normal.png",
            "media-audio",
            "audio-selected",
            "MediaAudioSearchBox",
            1100,
            900,
            "MediaAudioSearchBox",
            "MediaAudioTreeView",
            "MediaAudioNowPlaying",
            "MediaAudioSourceSummary"),
        Expected(
            "media-audio-selected-760.png",
            "media-audio",
            "audio-selected",
            "MediaAudioSearchBox",
            760,
            820,
            "MediaAudioSearchBox",
            "MediaAudioTreeView",
            "MediaAudioNowPlaying",
            "MediaAudioSourceSummary"),
        Expected(
            "media-video-selected-normal.png",
            "media-video",
            "video-selected",
            "MediaVideoSearchBox",
            1100,
            900,
            "MediaVideoSearchBox",
            "MediaVideoTreeView",
            "MediaVideoPlayerStatus",
            "MediaVideoSelected",
            "MediaVideoSourceSummary"),
        Expected(
            "media-video-selected-760.png",
            "media-video",
            "video-selected",
            "MediaVideoSearchBox",
            760,
            820,
            "MediaVideoSearchBox",
            "MediaVideoTreeView",
            "MediaVideoPlayerStatus",
            "MediaVideoSelected",
            "MediaVideoSourceSummary"),
        Expected(
            "asset-texture-selected-normal.png",
            "asset-library",
            "texture-selected",
            "AssetSearchBox",
            1100,
            900,
            "AssetCatalogSummary",
            "AssetItemsList",
            "AssetSelectedTitle",
            "AssetTexturePreviewImage"),
        Expected(
            "asset-texture-selected-760.png",
            "asset-library",
            "texture-selected",
            "AssetSearchBox",
            760,
            820,
            "AssetCatalogSummary",
            "AssetItemsList",
            "AssetSelectedTitle",
            "AssetTexturePreviewImage"),
        Expected(
            "asset-model-wireframe-normal.png",
            "asset-library",
            "model-wireframe",
            "AssetMeshesTabButton",
            1100,
            900,
            "AssetItemsList",
            "AssetSelectedTitle",
            "AssetModelMetadataInline",
            "AssetModelWireframeStatus",
            "AssetModelWireframePanel"),
        Expected(
            "asset-model-wireframe-760.png",
            "asset-library",
            "model-wireframe",
            "AssetMeshesTabButton",
            760,
            820,
            "AssetItemsList",
            "AssetSelectedTitle",
            "AssetModelMetadataInline",
            "AssetModelWireframeStatus",
            "AssetModelWireframePanel"),
    ];

    internal static readonly IReadOnlyDictionary<string, IReadOnlyList<MediaAssetSelectionEvidence>> ExpectedSelections =
        new Dictionary<string, IReadOnlyList<MediaAssetSelectionEvidence>>(StringComparer.Ordinal)
        {
            ["media-audio"] =
            [
                new(
                    "audio-selected",
                    "TUTORIAL_intro",
                    "Tutorial • TUTORIAL_intro.ogg",
                    "play-enabled-no-playback"),
            ],
            ["media-video"] =
            [
                new(
                    "video-selected",
                    "Credits Video",
                    "Main Videos • UsTheMovie.vid",
                    "play-enabled-deferred-no-playback"),
            ],
            ["asset-library"] =
            [
                new(
                    "texture-selected",
                    "Texture One",
                    "fixture; 1 packed references; export available.",
                    "texture:fixture/texture_one.tga"),
                new(
                    "model-wireframe",
                    "fixture_mesh.msh",
                    "1 packed references; FBX export available. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review.",
                    "FBX 7400; 3 vertices; 3 polygon index entries; UV mapping: no coordinate data recorded."),
            ],
        };

    private static MediaAssetExpectedCapture Expected(
        string relativeFileName,
        string workflow,
        string phase,
        string focusAutomationId,
        int width,
        int height,
        params string[] markerAutomationIds) =>
        new(
            relativeFileName,
            workflow,
            phase,
            focusAutomationId,
            width,
            height,
            markerAutomationIds);
}

internal sealed record MediaAssetExpectedCapture(
    string RelativeFileName,
    string Workflow,
    string Phase,
    string FocusAutomationId,
    int Width,
    int Height,
    IReadOnlyList<string> MarkerAutomationIds);

internal sealed record MediaAssetAppIdentityEvidence(
    int ProcessId,
    DateTime ProcessStartTimeUtc,
    string ExecutablePath,
    string ExecutableSha256,
    string ProductAssemblyPath,
    string ProductAssemblySha256,
    long MainWindowHandle,
    long UiaNativeWindowHandle,
    int WindowOwnerProcessId);

internal sealed record MediaAssetFocusObservation(
    string AutomationId,
    int ProcessId,
    long MainWindowHandle,
    int X,
    int Y,
    int Width,
    int Height,
    bool HasKeyboardFocus);

internal sealed record MediaAssetCaptureEvidence(
    string Workflow,
    string Phase,
    string FocusAutomationId,
    string RelativeFileName,
    string Sha256,
    int Width,
    int Height,
    MediaAssetAppIdentityEvidence Identity,
    IReadOnlyList<GuidedSaveVisualMarker> Markers,
    MediaAssetFocusObservation FocusBeforeCapture,
    MediaAssetFocusObservation FocusAfterCapture);

internal sealed record MediaAssetSelectionEvidence(
    string Phase,
    string Title,
    string Summary,
    string Detail);

internal sealed record MediaAssetWorkflowEvidence(
    string Workflow,
    MediaAssetAppIdentityEvidence Identity,
    bool PlaybackModulesLoaded,
    IReadOnlyList<MediaAssetSelectionEvidence> Selections);

internal sealed record MediaAssetFixtureEvidence(
    string RootRelativePath,
    IReadOnlyList<MediaAssetNativeFixtureFile> Files);

internal sealed record MediaAssetAcceptanceManifest(
    int SchemaVersion,
    string HarnessRunId,
    string InteractionMode,
    MediaAssetFixtureEvidence Fixture,
    IReadOnlyList<MediaAssetCaptureEvidence> Captures,
    IReadOnlyList<MediaAssetWorkflowEvidence> Workflows);
