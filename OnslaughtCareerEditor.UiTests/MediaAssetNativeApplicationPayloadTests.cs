namespace OnslaughtCareerEditor.UiTests;

public class MediaAssetNativeApplicationPayloadTests
{
    [Test]
    public void Compute_BindsTheCanonicalToolkitOwnedPayloadClosure()
    {
        using var fixture = PayloadFixture.Create();

        string first = MediaAssetNativeApplicationPayload.Compute(fixture.Root);
        string second = MediaAssetNativeApplicationPayload.Compute(fixture.Root);
        File.AppendAllText(
            Path.Combine(fixture.Root, "Pages", "MediaPage.xbf"),
            "changed");
        string changed = MediaAssetNativeApplicationPayload.Compute(fixture.Root);

        Assert.Multiple(() =>
        {
            Assert.That(MediaAssetNativeApplicationPayload.RelativePaths, Has.Count.EqualTo(18));
            Assert.That(
                MediaAssetNativeApplicationPayload.RelativePaths,
                Is.EqualTo(MediaAssetNativeApplicationPayload.RelativePaths.OrderBy(path => path, StringComparer.Ordinal)));
            Assert.That(first, Does.Match("^[0-9A-F]{64}$"));
            Assert.That(second, Is.EqualTo(first));
            Assert.That(changed, Is.Not.EqualTo(first));
        });
    }

    [Test]
    public void Compute_RejectsMissingOrReparseRoutedPayloadFile()
    {
        using var fixture = PayloadFixture.Create();
        File.Delete(Path.Combine(fixture.Root, "OnslaughtCareerEditor.AppCore.dll"));

        Assert.That(
            () => MediaAssetNativeApplicationPayload.Compute(fixture.Root),
            Throws.TypeOf<InvalidOperationException>());
    }

    private sealed class PayloadFixture : IDisposable
    {
        private PayloadFixture(string root)
        {
            Root = root;
        }

        internal string Root { get; }

        internal static PayloadFixture Create()
        {
            string root = Path.Combine(
                Path.GetTempPath(),
                "onslaught-media-asset-payload-tests",
                Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            foreach (string relativePath in MediaAssetNativeApplicationPayload.RelativePaths)
            {
                string path = Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                File.WriteAllText(path, $"payload:{relativePath}");
            }
            return new PayloadFixture(root);
        }

        public void Dispose()
        {
            if (Directory.Exists(Root))
            {
                Directory.Delete(Root, recursive: true);
            }
        }
    }
}
