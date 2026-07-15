namespace OnslaughtCareerEditor.UiTests;

public class MediaAssetNativeProducerSourceTests
{
    [Test]
    public void Producer_UsesExactUiaOnlyNoPlaybackBoundary()
    {
        string sourcePath = Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.UiTests",
            "WinUiMediaAssetNativeWorkflowTests.cs");
        string source = File.ReadAllText(sourcePath);

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("ONSLAUGHT_MEDIA_ASSET_NATIVE_ACCEPTANCE_RUN_ID"));
            Assert.That(source, Does.Contain("ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"));
            Assert.That(source, Does.Contain("HasPlaybackModulesLoaded"));
            Assert.That(source, Does.Contain("SelectionItem.Pattern.Select"));
            Assert.That(source, Does.Contain("MediaAssetNativeEvidenceAcceptance.Publish"));
            foreach (MediaAssetExpectedCapture capture in MediaAssetNativeEvidenceContract.ExpectedCaptures)
            {
                Assert.That(source, Does.Contain(capture.RelativeFileName));
            }

            Assert.That(source, Does.Not.Contain(".Click("));
            Assert.That(source, Does.Not.Contain("Keyboard"));
            Assert.That(source, Does.Not.Contain("Mouse"));
            Assert.That(source, Does.Not.Contain("MediaAudioPlayButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("MediaVideoPlayButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("MediaRevealVideoButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("AssetOpenExportButton\").AsButton().Invoke"));
        });
    }
}
