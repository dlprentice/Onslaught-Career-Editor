using System;
using System.IO;
using System.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class BinaryPatchRegressionTests
{
    private static byte[] SeedExe(string exePath, bool includeOptional)
    {
        int maxEnd = 0;
        foreach (var spec in BinaryPatchEngine.PatchSpecs)
        {
            if (spec.Optional && !includeOptional)
                continue;

            int end = spec.FileOffset + spec.Original.Length;
            if (end > maxEnd)
                maxEnd = end;
        }

        int fileSize = maxEnd + 0x100;
        byte[] data = Enumerable.Repeat((byte)0x90, fileSize).ToArray();

        foreach (var spec in BinaryPatchEngine.PatchSpecs)
        {
            if (spec.Optional && !includeOptional)
                continue;

            spec.Original.CopyTo(data, spec.FileOffset);
        }

        File.WriteAllBytes(exePath, data);
        return data;
    }

    [Test]
    public void BinaryPatch_ApplyThenRestore_RoundTripsWithBackup()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-apply-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: false);
            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();

            var apply = BinaryPatchEngine.ApplyPatchesToFile(exePath, selected);
            Assert.That(apply.success, Is.True, apply.message);
            Assert.That(apply.message, Does.Contain("Patch apply complete."));

            byte[] patched = File.ReadAllBytes(exePath);
            foreach (var spec in selected)
            {
                Assert.That(
                    patched.Skip(spec.FileOffset).Take(spec.Patched.Length).ToArray(),
                    Is.EqualTo(spec.Patched),
                    $"Patched bytes mismatch for {spec.Key}");
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            Assert.That(File.Exists(backupPath), Is.True, "Backup must exist after first successful apply.");
            Assert.That(File.ReadAllBytes(backupPath), Is.EqualTo(original), "Backup content should match original input bytes.");

            var restore = BinaryPatchEngine.RestoreFromBackup(exePath);
            Assert.That(restore.success, Is.True, restore.message);
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Restore should return target to original bytes.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyAbortsOnUnexpectedBytes_WithoutBackupCreation()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-mismatch-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: false);
            var firstStable = BinaryPatchEngine.PatchSpecs.First(s => s.Key == "resolution_gate");
            original[firstStable.FileOffset] = 0x41; // corrupt expected region
            File.WriteAllBytes(exePath, original);

            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();
            var apply = BinaryPatchEngine.ApplyPatchesToFile(exePath, selected);
            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("Apply aborted"));
            Assert.That(apply.message, Does.Contain("unexpected bytes"));

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            Assert.That(File.Exists(backupPath), Is.False, "Backup should not be created when apply aborts.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_VerifyReport_IncludesStableAndExperimentalTrackLabels()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-report-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: true);
            byte[] data = File.ReadAllBytes(exePath);

            var (_, _, rows) = BinaryPatchEngine.VerifyPatchSpecs(data, BinaryPatchEngine.PatchSpecs.ToArray());
            string report = BinaryPatchEngine.RenderStateReport(exePath, rows, "summary");
            Assert.That(report, Does.Contain("Stable |"));
            Assert.That(report, Does.Contain("Experimental |"));
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CardIdPreset_ApplyThenRestore_RoundTripsWithBackup()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-cardid-apply-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string cardIdPath = Path.Combine(tempDir, "cardid.txt");
        string original = "HeaderLine\n";
        File.WriteAllText(cardIdPath, original);

        try
        {
            var apply = CardIdPresetEngine.ApplyModernPresetToFile(cardIdPath);
            Assert.That(apply.success, Is.True, apply.message);
            Assert.That(apply.message, Does.Contain("preset apply complete"));

            var verify = CardIdPresetEngine.VerifyFile(cardIdPath);
            Assert.That(verify.success, Is.True);
            Assert.That(verify.state, Is.EqualTo(CardIdPresetState.Applied));

            string backupPath = CardIdPresetEngine.BuildBackupPath(cardIdPath);
            Assert.That(File.Exists(backupPath), Is.True);
            Assert.That(File.ReadAllText(backupPath), Is.EqualTo(original));

            var restore = CardIdPresetEngine.RestoreFromBackup(cardIdPath);
            Assert.That(restore.success, Is.True, restore.message);
            Assert.That(File.ReadAllText(cardIdPath), Is.EqualTo(original));
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CardIdPreset_ApplyRejectsMalformedMarkers()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-cardid-malformed-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string cardIdPath = Path.Combine(tempDir, "cardid.txt");
        File.WriteAllText(cardIdPath, $"{CardIdPresetEngine.BeginMarker}\nBROKEN\n");

        try
        {
            var apply = CardIdPresetEngine.ApplyModernPresetToFile(cardIdPath);
            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("malformed managed markers"));

            var verify = CardIdPresetEngine.VerifyFile(cardIdPath);
            Assert.That(verify.success, Is.True);
            Assert.That(verify.state, Is.EqualTo(CardIdPresetState.MalformedMarkers));

            string backupPath = CardIdPresetEngine.BuildBackupPath(cardIdPath);
            Assert.That(File.Exists(backupPath), Is.False, "No backup should be created when apply aborts.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CardIdPreset_ApplyIsIdempotent_NoDuplicateManagedBlocks()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-cardid-idempotent-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string cardIdPath = Path.Combine(tempDir, "cardid.txt");
        File.WriteAllText(cardIdPath, "HeaderLine\n");

        try
        {
            var firstApply = CardIdPresetEngine.ApplyModernPresetToFile(cardIdPath);
            Assert.That(firstApply.success, Is.True, firstApply.message);

            var secondApply = CardIdPresetEngine.ApplyModernPresetToFile(cardIdPath);
            Assert.That(secondApply.success, Is.True, secondApply.message);
            Assert.That(secondApply.message, Does.Contain("No changes needed"));

            string text = File.ReadAllText(cardIdPath);
            int beginCount = text.Split(CardIdPresetEngine.BeginMarker, StringSplitOptions.None).Length - 1;
            int endCount = text.Split(CardIdPresetEngine.EndMarker, StringSplitOptions.None).Length - 1;
            Assert.That(beginCount, Is.EqualTo(1), "Managed BEGIN marker should appear exactly once.");
            Assert.That(endCount, Is.EqualTo(1), "Managed END marker should appear exactly once.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }
}
