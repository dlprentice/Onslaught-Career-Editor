using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Details used to name the Aurore gate check a
/// CDB proof. Text="{Binding VerifiedProof}" paints that sentence.
/// Name the safe-copy run.
/// </summary>
public class BinaryPatchVerifiedProofHonestyTests
{
    private const string PaintedSentence =
        "A safe-copy run observed the patched gate bytes, BUTTON_TOGGLE_FREE_CAMERA dispatch, free-camera-on SetCurrentCamera, and restore on the second tap.";

    private const string LeftoverSentence =
        "Safe-copy CDB proof observed the patched gate bytes, BUTTON_TOGGLE_FREE_CAMERA dispatch, free-camera-on SetCurrentCamera, and restore on the second tap.";

    [Test]
    public void TheAuroreVerifiedProofPaintsASafeCopyRunNotACdbProof()
    {
        string proof = ExtractAuroreVerifiedProofAssignment();

        Assert.That(proof, Does.Contain(PaintedSentence));
        Assert.That(proof, Does.Contain("safe-copy run"));
        Assert.That(proof, Does.Not.Contain(LeftoverSentence));
        Assert.That(proof, Does.Not.Contain("CDB"));
        Assert.That(proof, Does.Not.Contain("cdb"));
    }

    [Test]
    public void WindowedAndModsDetailsBindTheVerifiedProof()
    {
        string xaml = ReadWindowedAndModsXaml();
        string model = ReadPatchItemModel();
        string checkedBlock = ExtractWhatWasCheckedBlock(xaml);

        Assert.That(checkedBlock, Does.Contain("What was checked"));
        Assert.That(checkedBlock, Does.Contain("Text=\"{Binding VerifiedProof}\""));
        Assert.That(model, Does.Contain($"\"free_camera_aurore_gate_bypass\" => \"{PaintedSentence}\""));
        Assert.That(model, Does.Not.Contain(LeftoverSentence));
    }

    private static string ExtractAuroreVerifiedProofAssignment()
    {
        string model = ReadPatchItemModel();
        const string verifiedMark = "VerifiedProof = spec.Key switch";
        int verified = model.IndexOf(verifiedMark, StringComparison.Ordinal);
        Assert.That(verified, Is.GreaterThanOrEqualTo(0), "VerifiedProof switch is missing.");

        const string stillUnprovenMark = "StillUnproven = spec.Key switch";
        int stillUnproven = model.IndexOf(stillUnprovenMark, verified, StringComparison.Ordinal);
        Assert.That(stillUnproven, Is.GreaterThan(verified), "VerifiedProof switch has no end.");

        string verifiedSwitch = model[verified..stillUnproven];
        const string keyMark = "\"free_camera_aurore_gate_bypass\" => ";
        int key = verifiedSwitch.IndexOf(keyMark, StringComparison.Ordinal);
        Assert.That(key, Is.GreaterThanOrEqualTo(0), "Aurore VerifiedProof arm is missing.");

        int end = verifiedSwitch.IndexOf('\n', key);
        Assert.That(end, Is.GreaterThan(key), "Aurore VerifiedProof arm is unclosed.");
        return verifiedSwitch[key..end];
    }

    private static string ExtractWhatWasCheckedBlock(string xaml)
    {
        const string startMark = "<TextBlock Text=\"What was checked\"";
        int start = xaml.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "What was checked label is missing.");

        const string endMark = "<TextBlock Text=\"Not proven yet\"";
        int end = xaml.IndexOf(endMark, start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "What was checked block has no end.");
        return xaml[start..end];
    }

    private static string ReadWindowedAndModsXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
    }

    private static string ReadPatchItemModel()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Models",
            "BinaryPatchItemModel.cs"));
    }
}
