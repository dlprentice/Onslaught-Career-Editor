using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class BinaryPatchRegressionTests
{
    private static readonly string[] FreeCameraKeyboardCaveKeys =
    {
        "free_camera_keyboard_forward_q_cave",
        "free_camera_keyboard_backward_q_cave",
        "free_camera_keyboard_strafe_left_q_cave",
        "free_camera_keyboard_strafe_right_q_cave",
        "free_camera_keyboard_yaw_left_q_cave",
        "free_camera_keyboard_yaw_right_q_cave",
        "free_camera_keyboard_pitch_up_q_cave",
        "free_camera_keyboard_pitch_down_q_cave",
    };

    private static readonly string[] FreeCameraKeyboardHookKeys =
    {
        "free_camera_keyboard_forward_q_hook",
        "free_camera_keyboard_backward_q_hook",
        "free_camera_keyboard_strafe_left_q_hook",
        "free_camera_keyboard_strafe_right_q_hook",
        "free_camera_keyboard_yaw_left_q_hook",
        "free_camera_keyboard_yaw_right_q_hook",
        "free_camera_keyboard_pitch_up_q_hook",
        "free_camera_keyboard_pitch_down_q_hook",
    };

    private static BinaryPatchTargetOptions BuildTestTarget(
        string exePath,
        string allowedRoot,
        bool allowByteLayoutOnly = true)
    {
        return new BinaryPatchTargetOptions(
            ExePath: exePath,
            AllowedRoot: allowedRoot,
            AllowFallbackCatalogForTests: true,
            AllowByteLayoutOnlyTarget: allowByteLayoutOnly);
    }

    private static byte[] SeedExe(string exePath, bool includeOptional)
    {
        return SeedExe(exePath, includeOptional, fileSize: null);
    }

    private static byte[] SeedKnownSizeExe(string exePath, bool includeOptional)
    {
        return SeedExe(exePath, includeOptional, fileSize: 2_506_752);
    }

    private static byte[] SeedExe(string exePath, bool includeOptional, int? fileSize)
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

        int size = fileSize ?? maxEnd + 0x100;
        byte[] data = Enumerable.Repeat((byte)0x90, size).ToArray();

        foreach (var spec in BinaryPatchEngine.PatchSpecs)
        {
            if (spec.Optional && !includeOptional)
                continue;

            spec.Original.CopyTo(data, spec.FileOffset);
        }

        File.WriteAllBytes(exePath, data);
        return data;
    }

    private static string Sha256Hex(byte[] bytes)
    {
        return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    }

    private static string ResolveRepoRoot()
    {
        DirectoryInfo? current = new(AppContext.BaseDirectory);
        while (current is not null)
        {
            if (File.Exists(Path.Combine(current.FullName, "patches", "catalog", "patches.v2.json")))
            {
                return current.FullName;
            }

            current = current.Parent;
        }

        throw new DirectoryNotFoundException("Could not locate repo root from test directory.");
    }

    [Test]
    public void BinaryPatch_ApplyThenRestore_RoundTripsWithBackup()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-apply-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);
            Assert.That(apply.message, Does.Contain("Patch apply complete."));
        Assert.That(apply.message, Does.Contain("Selected patch bytes verified on disk."));
            Assert.That(apply.message, Does.Contain("Target identity: byte-layout-only verified selected patch offsets"));

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

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));
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
    public void BinaryPatch_VerifyTargetFile_UsesSameIdentityGateAsApply()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-verify-identity-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: false);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var verify = BinaryPatchEngine.VerifyPatchTargetFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                selected);

            Assert.That(verify.Success, Is.False);
            Assert.That(verify.Message, Does.Contain("known clean Steam retail BEA.exe"));
            Assert.That(verify.Rows, Is.Empty);
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
            byte[] original = SeedExe(exePath, includeOptional: true);
            var firstStable = BinaryPatchEngine.PatchSpecs.First(s => s.Key == "resolution_gate");
            original[firstStable.FileOffset] = 0x41; // corrupt expected region
            File.WriteAllBytes(exePath, original);

            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();
            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
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
    public void BinaryPatch_ApplyRejectsExistingBackupWithoutHashSidecar()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-apply-backup-no-hash-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            File.WriteAllBytes(backupPath, original);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("existing backup snapshot integrity"));
            Assert.That(apply.message, Does.Contain("hash sidecar"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Apply must not mutate when the pre-existing backup is not integrity-verified.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_RestoreRejectsUnexpectedCurrentPatchBytesWithoutOverwriting()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-mismatch-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            byte[] corrupted = File.ReadAllBytes(exePath);
            corrupted[selected[0].FileOffset] = 0x41;
            File.WriteAllBytes(exePath, corrupted);

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Does.Contain("unexpected patch state"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(corrupted), "Restore must not overwrite a target whose current patch bytes are not verified.");
            Assert.That(File.ReadAllBytes(BinaryPatchEngine.BuildBackupPath(exePath)), Is.EqualTo(original));
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_RestoreRejectsCorruptedBackupWithoutOverwriting()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-backup-corrupt-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            byte[] corruptedBackup = File.ReadAllBytes(backupPath);
            corruptedBackup[0x20] ^= 0x7F;
            File.WriteAllBytes(backupPath, corruptedBackup);
            byte[] patchedBeforeRestore = File.ReadAllBytes(exePath);

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Does.Contain("backup snapshot integrity"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(patchedBeforeRestore), "Restore must not overwrite from a corrupted backup snapshot.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [TestCase("frontend_clear_screen_dark_red")]
    [TestCase("frontend_clear_screen_dark_green")]
    [TestCase("frontend_clear_screen_black")]
    public void BinaryPatch_RestoreAllowsOneMutuallyExclusiveFrontendColorPreset(string colorPatchKey)
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-color-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { colorPatchKey });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            byte[] patched = File.ReadAllBytes(exePath);
            Assert.That(
                patched.Skip(selected[0].FileOffset).Take(selected[0].Patched.Length).ToArray(),
                Is.EqualTo(selected[0].Patched),
                $"Color preset bytes were not applied for {colorPatchKey}.");

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));

            Assert.That(restore.success, Is.True, restore.message);
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Restore should accept one known same-offset color preset and restore from backup.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsPolicyInvalidSelectionBeforeWriting()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-policy-invalid-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            var byKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);

            var missingDependencyApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir),
                new[] { byKey["version_overlay_use_patched_format_pointer"] });
            Assert.That(missingDependencyApply.success, Is.False);
            Assert.That(missingDependencyApply.message, Does.Contain("missing dependency"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Missing dependency must fail before any bytes are written.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False, "Policy-invalid selection must not create a backup.");

            var colorConflictApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir),
                new[]
                {
                    byKey["frontend_clear_screen_dark_red"],
                    byKey["frontend_clear_screen_dark_green"],
                });
            Assert.That(colorConflictApply.success, Is.False);
            Assert.That(colorConflictApply.message, Does.Contain("conflicting rows").Or.Contain("exclusive group").Or.Contain("overlapping rows"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Conflicting color rows must fail before any bytes are written.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False, "Policy-invalid selection must not create a backup.");

            var hiddenCompanionApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir),
                new[] { byKey["version_overlay_patched_format_cave_string"] });
            Assert.That(hiddenCompanionApply.success, Is.False);
            Assert.That(hiddenCompanionApply.message, Does.Contain("hidden companion"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Hidden companion alone must fail before any bytes are written.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False, "Policy-invalid selection must not create a backup.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_RestoreRejectsBackupWithoutHashSidecar()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-backup-no-hash-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(exePath);
            File.Delete(backupHashPath);
            byte[] patchedBeforeRestore = File.ReadAllBytes(exePath);

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Does.Contain("hash sidecar"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(patchedBeforeRestore), "Restore must not overwrite from a backup without a hash sidecar.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_RestoreRejectsBackupWithoutTrustedCleanProvenance()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-backup-provenance-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedKnownSizeExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(exePath);
            File.WriteAllText(backupHashPath, Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(backupPath))).ToLowerInvariant());
            byte[] patchedBeforeRestore = File.ReadAllBytes(exePath);

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Does.Contain("trusted clean Steam retail BEA.exe"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(patchedBeforeRestore), "Restore must not overwrite from a backup with only self-authored sidecar provenance.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_RestoreRepairsUnrelatedDriftWhenBackupIsVerified()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-restore-unrelated-drift-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: true);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, tempDir), selected);
            Assert.That(apply.success, Is.True, apply.message);

            var restore = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));
            Assert.That(restore.success, Is.True, restore.message);
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original));

            byte[] drifted = File.ReadAllBytes(exePath);
            drifted[0x20] ^= 0x7F;
            File.WriteAllBytes(exePath, drifted);

            var repair = BinaryPatchEngine.RestoreFromBackup(BuildTestTarget(exePath, tempDir));

            Assert.That(repair.success, Is.True, repair.message);
            Assert.That(repair.message, Does.Contain("Restore complete."));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Restore should repair unrelated copied-executable drift when the backup is verified.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsTargetOutsideAllowedRoot_WithoutBackupCreation()
    {
        string allowedRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-allowed-{Guid.NewGuid():N}");
        string outsideRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-outside-{Guid.NewGuid():N}");
        Directory.CreateDirectory(allowedRoot);
        Directory.CreateDirectory(outsideRoot);
        string exePath = Path.Combine(outsideRoot, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: false);
            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, allowedRoot), selected);
            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("app-owned Patch Bench workspace"));
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False);
        }
        finally
        {
            if (Directory.Exists(allowedRoot))
                Directory.Delete(allowedRoot, recursive: true);
            if (Directory.Exists(outsideRoot))
                Directory.Delete(outsideRoot, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsSteamLibraryShapedAllowedRoot_WithoutBackupCreation()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-steam-shape-{Guid.NewGuid():N}");
        string allowedRoot = Path.Combine(tempDir, "steamapps", "common", "Battle Engine Aquila");
        Directory.CreateDirectory(allowedRoot);
        string exePath = Path.Combine(allowedRoot, "BEA.exe");

        try
        {
            byte[] original = SeedExe(exePath, includeOptional: false);
            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();

            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(exePath, allowedRoot), selected);

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("steamapps/common/Battle Engine Aquila"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(original), "Steam-library-shaped targets must not be mutated.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsReparsePointTargetInsideAllowedRoot()
    {
        string allowedRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-link-allowed-{Guid.NewGuid():N}");
        string outsideRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-link-outside-{Guid.NewGuid():N}");
        Directory.CreateDirectory(allowedRoot);
        Directory.CreateDirectory(outsideRoot);
        string outsideExe = Path.Combine(outsideRoot, "BEA.exe");
        string linkedExe = Path.Combine(allowedRoot, "BEA.exe");

        try
        {
            byte[] original = SeedExe(outsideExe, includeOptional: false);
            try
            {
                File.CreateSymbolicLink(linkedExe, outsideExe);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
            {
                Assert.Ignore($"File symlink could not be created on this host: {ex.Message}");
            }

            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();
            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(linkedExe, allowedRoot), selected);

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("reparse"));
            Assert.That(File.ReadAllBytes(outsideExe), Is.EqualTo(original), "Linked outside executable must not be mutated.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(linkedExe)), Is.False);
        }
        finally
        {
            if (Directory.Exists(allowedRoot))
                Directory.Delete(allowedRoot, recursive: true);
            if (Directory.Exists(outsideRoot))
                Directory.Delete(outsideRoot, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsHardlinkTargetInsideAllowedRoot()
    {
        if (!OperatingSystem.IsWindows())
        {
            Assert.Ignore("Hardlink safety regression uses Win32 CreateHardLink.");
        }

        string allowedRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-hardlink-allowed-{Guid.NewGuid():N}");
        string outsideRoot = Path.Combine(Path.GetTempPath(), $"onslaught-binary-hardlink-outside-{Guid.NewGuid():N}");
        Directory.CreateDirectory(allowedRoot);
        Directory.CreateDirectory(outsideRoot);
        string outsideExe = Path.Combine(outsideRoot, "BEA.exe");
        string linkedExe = Path.Combine(allowedRoot, "BEA.exe");

        try
        {
            byte[] original = SeedExe(outsideExe, includeOptional: false);
            if (!CreateHardLink(linkedExe, outsideExe, IntPtr.Zero))
            {
                Assert.Ignore($"Hardlink could not be created on this host. Win32 error: {Marshal.GetLastWin32Error()}");
            }

            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();
            var apply = BinaryPatchEngine.ApplyPatchesToFile(BuildTestTarget(linkedExe, allowedRoot), selected);

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("hardlink").IgnoreCase);
            Assert.That(File.ReadAllBytes(outsideExe), Is.EqualTo(original), "Hardlinked outside executable must not be mutated.");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(linkedExe)), Is.False);
        }
        finally
        {
            if (Directory.Exists(allowedRoot))
                Directory.Delete(allowedRoot, recursive: true);
            if (Directory.Exists(outsideRoot))
                Directory.Delete(outsideRoot, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsUnknownSpecimenWithoutExplicitByteLayoutAllowance()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-identity-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedExe(exePath, includeOptional: false);
            var selected = BinaryPatchEngine.PatchSpecs.Where(s => !s.Optional).ToArray();

            var apply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                selected);

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("known clean Steam retail BEA.exe"));
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsAlreadyPatchedKnownSizeCopyWithoutTrustedBackupProvenance()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-idempotent-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedKnownSizeExe(exePath, includeOptional: false);
            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" });

            var firstApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: true),
                selected);
            Assert.That(firstApply.success, Is.True, firstApply.message);

            byte[] afterFirstApply = File.ReadAllBytes(exePath);
            File.Delete(BinaryPatchEngine.BuildBackupPath(exePath));
            File.Delete(BinaryPatchEngine.BuildBackupHashPath(exePath));

            var secondApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                selected);

            Assert.That(secondApply.success, Is.False, secondApply.message);
            Assert.That(secondApply.message, Does.Contain("known clean Steam retail BEA.exe"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(afterFirstApply), "Rejected no-op apply must not rewrite the copied executable.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsAlreadyPatchedKnownSizeCopyWithUnrelatedByteDrift()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-idempotent-drift-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            byte[] original = SeedKnownSizeExe(exePath, includeOptional: false);
            BinaryPatchSpec sourceSpec = BinaryPatchEngine.PatchSpecs.First(spec => spec.Key == "resolution_gate");
            var selectedSpec = new BinaryPatchSpec(
                Key: sourceSpec.Key,
                Track: sourceSpec.Track,
                DisplayName: sourceSpec.DisplayName,
                FileOffset: sourceSpec.FileOffset,
                Original: sourceSpec.Original,
                Patched: sourceSpec.Patched,
                TargetBinaryHashes: new[] { Sha256Hex(original) },
                TargetBinarySize: original.LongLength);

            var firstApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                new[] { selectedSpec });
            Assert.That(firstApply.success, Is.True, firstApply.message);

            byte[] drifted = File.ReadAllBytes(exePath);
            drifted[0x20] = 0x42;
            File.WriteAllBytes(exePath, drifted);

            var secondApply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                new[] { selectedSpec });

            Assert.That(secondApply.success, Is.False, secondApply.message);
            Assert.That(secondApply.message, Does.Contain("known clean Steam retail BEA.exe"));
            Assert.That(File.ReadAllBytes(exePath), Is.EqualTo(drifted), "Rejected idempotent apply must not overwrite unrelated drift.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_ApplyRejectsAlreadyPatchedRowsWithoutTargetIdentityMetadata()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-binary-missing-identity-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string exePath = Path.Combine(tempDir, "BEA.exe");

        try
        {
            SeedKnownSizeExe(exePath, includeOptional: false);
            BinaryPatchSpec sourceSpec = BinaryPatchEngine.PatchSpecs.First(spec => spec.Key == "resolution_gate");
            var missingIdentitySpec = new BinaryPatchSpec(
                Key: sourceSpec.Key,
                Track: sourceSpec.Track,
                DisplayName: sourceSpec.DisplayName,
                FileOffset: sourceSpec.FileOffset,
                Original: sourceSpec.Original,
                Patched: sourceSpec.Patched);

            byte[] data = File.ReadAllBytes(exePath);
            missingIdentitySpec.Patched.CopyTo(data, missingIdentitySpec.FileOffset);
            File.WriteAllBytes(exePath, data);

            var apply = BinaryPatchEngine.ApplyPatchesToFile(
                BuildTestTarget(exePath, tempDir, allowByteLayoutOnly: false),
                new[] { missingIdentitySpec });

            Assert.That(apply.success, Is.False);
            Assert.That(apply.message, Does.Contain("known clean Steam retail BEA.exe"));
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)), Is.False);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void BinaryPatch_CatalogSpecsCarryTargetIdentity()
    {
        string[] expectedKeys =
        {
            "resolution_gate",
            "force_windowed",
            "extra_graphics_default_on",
            "ignore_cardid_tweak_overrides",
            "version_overlay_use_patched_format_pointer",
            "version_overlay_patched_format_cave_string",
            "frontend_clear_screen_dark_red",
            "frontend_clear_screen_dark_green",
            "frontend_clear_screen_black",
            "goodies_gallery_display_unlock",
            "skip_auto_toggle",
            "pause_o_scan_initializer_experiment",
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_forward_q_cave",
            "free_camera_keyboard_forward_q_hook",
            "free_camera_keyboard_backward_q_cave",
            "free_camera_keyboard_backward_q_hook",
            "free_camera_keyboard_strafe_left_q_cave",
            "free_camera_keyboard_strafe_left_q_hook",
            "free_camera_keyboard_strafe_right_q_cave",
            "free_camera_keyboard_strafe_right_q_hook",
            "free_camera_keyboard_yaw_left_q_cave",
            "free_camera_keyboard_yaw_left_q_hook",
            "free_camera_keyboard_yaw_right_q_cave",
            "free_camera_keyboard_yaw_right_q_hook",
            "free_camera_keyboard_pitch_up_q_cave",
            "free_camera_keyboard_pitch_up_q_hook",
            "free_camera_keyboard_pitch_down_q_cave",
            "free_camera_keyboard_pitch_down_q_hook",
        };

        Assert.That(BinaryPatchEngine.UsingFallbackCatalog, Is.False, BinaryPatchEngine.CatalogStatus);
        Assert.That(BinaryPatchEngine.PatchSpecs, Is.Not.Empty);
        Assert.That(
            BinaryPatchEngine.PatchSpecs.Select(spec => spec.Key).ToArray(),
            Is.EquivalentTo(expectedKeys));

        string catalogPath = Path.Combine(ResolveRepoRoot(), "patches", "catalog", "patches.v2.json");
        using JsonDocument catalog = JsonDocument.Parse(File.ReadAllText(catalogPath));
        string[] catalogKeys = catalog.RootElement.GetProperty("patches")
            .EnumerateArray()
            .Select(row => row.GetProperty("id").GetString())
            .Where(key => !string.IsNullOrWhiteSpace(key))
            .Select(key => key!)
            .ToArray();
        Assert.That(catalogKeys, Is.EquivalentTo(expectedKeys));

        var catalogRowsByKey = catalog.RootElement.GetProperty("patches")
            .EnumerateArray()
            .ToDictionary(row => row.GetProperty("id").GetString()!, StringComparer.OrdinalIgnoreCase);
        foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
        {
            JsonElement row = catalogRowsByKey[spec.Key];
            bool optional = row.TryGetProperty("optional", out JsonElement optionalEl) &&
                optionalEl.ValueKind == JsonValueKind.True;
            Assert.That(optional, Is.EqualTo(spec.Optional), spec.Key);
            string fileOffsetHex = row.GetProperty("file_offset").GetString()!
                .Replace("0x", string.Empty, StringComparison.OrdinalIgnoreCase);
            Assert.That(Convert.ToInt32(fileOffsetHex, 16), Is.EqualTo(spec.FileOffset), spec.Key);
            Assert.That(row.GetProperty("title").GetString(), Is.EqualTo(spec.DisplayName), spec.Key);
        }

        JsonElement goodiesCatalogRow = catalog.RootElement.GetProperty("patches")
            .EnumerateArray()
            .Single(row => string.Equals(
                row.GetProperty("id").GetString(),
                "goodies_gallery_display_unlock",
                StringComparison.OrdinalIgnoreCase));
        Assert.That(goodiesCatalogRow.GetProperty("title").GetString(), Is.EqualTo("Goodies gallery display flag override"));
        Assert.That(goodiesCatalogRow.GetProperty("file_offset").GetString(), Is.EqualTo("0x05D7F4"));
        Assert.That(goodiesCatalogRow.GetProperty("expected_original_bytes").GetString(), Is.EqualTo("E8 97 7C 00 00 F7 D8 1B C0"));
        Assert.That(goodiesCatalogRow.GetProperty("patched_bytes").GetString(), Is.EqualTo("83 C4 04 83 C8 FF 90 90 90"));

        foreach (var spec in BinaryPatchEngine.PatchSpecs)
        {
            Assert.That(spec.TargetBinaryHashes ?? Array.Empty<string>(), Has.Member("74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"), spec.Key);
            Assert.That(spec.TargetBinarySize, Is.EqualTo(2_506_752), spec.Key);
            Assert.That(spec.ProofLevel, Is.Not.Null.And.Not.Empty, spec.Key);
            Assert.That(spec.Selectability, Is.Not.Null.And.Not.Empty, spec.Key);
            Assert.That(spec.PresetEligibility, Is.Not.Null, spec.Key);
        }

        BinaryPatchSpec colorSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "frontend_clear_screen_dark_red");
        Assert.That(colorSpec.FileOffset, Is.EqualTo(0x140F88));
        Assert.That(colorSpec.Original, Is.EqualTo(new byte[] { 0x3F, 0x1F, 0x1F, 0x00 }));
        Assert.That(colorSpec.Patched, Is.EqualTo(new byte[] { 0x1F, 0x1F, 0xBF, 0x00 }));

        BinaryPatchSpec greenColorSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "frontend_clear_screen_dark_green");
        Assert.That(greenColorSpec.FileOffset, Is.EqualTo(0x140F88));
        Assert.That(greenColorSpec.Original, Is.EqualTo(new byte[] { 0x3F, 0x1F, 0x1F, 0x00 }));
        Assert.That(greenColorSpec.Patched, Is.EqualTo(new byte[] { 0x1F, 0xBF, 0x1F, 0x00 }));

        BinaryPatchSpec blackColorSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "frontend_clear_screen_black");
        Assert.That(blackColorSpec.FileOffset, Is.EqualTo(0x140F88));
        Assert.That(blackColorSpec.Original, Is.EqualTo(new byte[] { 0x3F, 0x1F, 0x1F, 0x00 }));
        Assert.That(blackColorSpec.Patched, Is.EqualTo(new byte[] { 0x00, 0x00, 0x00, 0x00 }));

        BinaryPatchSpec goodiesSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "goodies_gallery_display_unlock");
        Assert.That(goodiesSpec.FileOffset, Is.EqualTo(0x05D7F4));
        Assert.That(goodiesSpec.Original, Is.EqualTo(new byte[] { 0xE8, 0x97, 0x7C, 0x00, 0x00, 0xF7, 0xD8, 0x1B, 0xC0 }));
        Assert.That(goodiesSpec.Patched, Is.EqualTo(new byte[] { 0x83, 0xC4, 0x04, 0x83, 0xC8, 0xFF, 0x90, 0x90, 0x90 }));
        Assert.That(
            goodiesSpec.Patched.Take(3).ToArray(),
            Is.EqualTo(new byte[] { 0x83, 0xC4, 0x04 }),
            "The skipped IsCheatActive(0) call follows a pushed argument; the patch must discard it before forcing EAX.");

        BinaryPatchSpec freeCameraSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_aurore_gate_bypass");
        Assert.That(freeCameraSpec.FileOffset, Is.EqualTo(0x06F83C));
        Assert.That(freeCameraSpec.Original, Is.EqualTo(new byte[] { 0x0F, 0x84, 0x58, 0x02, 0x00, 0x00 }));
        Assert.That(freeCameraSpec.Patched, Is.EqualTo(new byte[] { 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 }));

        BinaryPatchSpec freeCameraCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_forward_q_cave");
        Assert.That(freeCameraCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(freeCameraCaveSpec.Patched.Length, Is.EqualTo(29));
        Assert.That(freeCameraCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraCaveSpec.Key })));

        BinaryPatchSpec freeCameraHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_forward_q_hook");
        Assert.That(freeCameraHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_forward_q_cave" }));
        Assert.That(freeCameraHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraHookSpec.Key })));
        Assert.That(freeCameraHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraBackwardCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_backward_q_cave");
        Assert.That(freeCameraBackwardCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraBackwardCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraBackwardCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x20, 0x75, 0x09, 0xB8, 0x27, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraBackwardCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraBackwardCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraBackwardCaveSpec.Key })));

        BinaryPatchSpec freeCameraBackwardHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_backward_q_hook");
        Assert.That(freeCameraBackwardHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraBackwardHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraBackwardHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraBackwardHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_backward_q_cave" }));
        Assert.That(freeCameraBackwardHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraBackwardHookSpec.Key })));
        Assert.That(freeCameraBackwardHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraStrafeLeftCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_strafe_left_q_cave");
        Assert.That(freeCameraStrafeLeftCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraStrafeLeftCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraStrafeLeftCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1D, 0x75, 0x09, 0xB8, 0x28, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraStrafeLeftCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraStrafeLeftCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraStrafeLeftCaveSpec.Key })));

        BinaryPatchSpec freeCameraStrafeLeftHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_strafe_left_q_hook");
        Assert.That(freeCameraStrafeLeftHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraStrafeLeftHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraStrafeLeftHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraStrafeLeftHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_strafe_left_q_cave" }));
        Assert.That(freeCameraStrafeLeftHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraStrafeLeftHookSpec.Key })));
        Assert.That(freeCameraStrafeLeftHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraStrafeRightCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_strafe_right_q_cave");
        Assert.That(freeCameraStrafeRightCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraStrafeRightCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraStrafeRightCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1E, 0x75, 0x09, 0xB8, 0x29, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraStrafeRightCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraStrafeRightCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraStrafeRightCaveSpec.Key })));

        BinaryPatchSpec freeCameraStrafeRightHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_strafe_right_q_hook");
        Assert.That(freeCameraStrafeRightHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraStrafeRightHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraStrafeRightHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraStrafeRightHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_strafe_right_q_cave" }));
        Assert.That(freeCameraStrafeRightHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraStrafeRightHookSpec.Key })));
        Assert.That(freeCameraStrafeRightHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraYawLeftCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_yaw_left_q_cave");
        Assert.That(freeCameraYawLeftCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraYawLeftCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraYawLeftCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x19, 0x75, 0x09, 0xB8, 0x24, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraYawLeftCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraYawLeftCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraYawLeftCaveSpec.Key })));

        BinaryPatchSpec freeCameraYawLeftHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_yaw_left_q_hook");
        Assert.That(freeCameraYawLeftHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraYawLeftHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraYawLeftHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraYawLeftHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_yaw_left_q_cave" }));
        Assert.That(freeCameraYawLeftHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraYawLeftHookSpec.Key })));
        Assert.That(freeCameraYawLeftHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraYawRightCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_yaw_right_q_cave");
        Assert.That(freeCameraYawRightCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraYawRightCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraYawRightCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1B, 0x75, 0x09, 0xB8, 0x25, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraYawRightCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraYawRightCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraYawRightCaveSpec.Key })));

        BinaryPatchSpec freeCameraYawRightHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_yaw_right_q_hook");
        Assert.That(freeCameraYawRightHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraYawRightHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraYawRightHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraYawRightHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_yaw_right_q_cave" }));
        Assert.That(freeCameraYawRightHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraYawRightHookSpec.Key })));
        Assert.That(freeCameraYawRightHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraPitchUpCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_pitch_up_q_cave");
        Assert.That(freeCameraPitchUpCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraPitchUpCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraPitchUpCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1A, 0x75, 0x09, 0xB8, 0x22, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraPitchUpCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraPitchUpCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraPitchUpCaveSpec.Key })));

        BinaryPatchSpec freeCameraPitchUpHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_pitch_up_q_hook");
        Assert.That(freeCameraPitchUpHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraPitchUpHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraPitchUpHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraPitchUpHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_pitch_up_q_cave" }));
        Assert.That(freeCameraPitchUpHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraPitchUpHookSpec.Key })));
        Assert.That(freeCameraPitchUpHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec freeCameraPitchDownCaveSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_pitch_down_q_cave");
        Assert.That(freeCameraPitchDownCaveSpec.FileOffset, Is.EqualTo(0x1A3A15));
        Assert.That(freeCameraPitchDownCaveSpec.Original, Is.EqualTo(Enumerable.Repeat((byte)0xCC, 29).ToArray()));
        Assert.That(
            freeCameraPitchDownCaveSpec.Patched,
            Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1C, 0x75, 0x09, 0xB8, 0x23, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF }));
        Assert.That(freeCameraPitchDownCaveSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(freeCameraPitchDownCaveSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardCaveKeys.Except(new[] { freeCameraPitchDownCaveSpec.Key })));

        BinaryPatchSpec freeCameraPitchDownHookSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "free_camera_keyboard_pitch_down_q_hook");
        Assert.That(freeCameraPitchDownHookSpec.FileOffset, Is.EqualTo(0x01A980));
        Assert.That(freeCameraPitchDownHookSpec.Original, Is.EqualTo(new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 }));
        Assert.That(freeCameraPitchDownHookSpec.Patched, Is.EqualTo(new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 }));
        Assert.That(freeCameraPitchDownHookSpec.Dependencies, Is.EquivalentTo(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_pitch_down_q_cave" }));
        Assert.That(freeCameraPitchDownHookSpec.Conflicts, Is.EquivalentTo(FreeCameraKeyboardHookKeys.Except(new[] { freeCameraPitchDownHookSpec.Key })));
        Assert.That(freeCameraPitchDownHookSpec.ExclusiveGroup, Is.EqualTo("free_camera_keyboard_q_remap"));

        BinaryPatchSpec overlayPointerSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "version_overlay_use_patched_format_pointer");
        Assert.That(overlayPointerSpec.Dependencies, Is.EquivalentTo(new[] { "version_overlay_patched_format_cave_string" }));

        BinaryPatchSpec overlayPayloadSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "version_overlay_patched_format_cave_string");
        Assert.That(overlayPayloadSpec.Selectability, Is.EqualTo("hidden_companion"));
        Assert.That(overlayPayloadSpec.PresetEligibility ?? Array.Empty<string>(), Is.Empty);

        Assert.That(colorSpec.ExclusiveGroup, Is.EqualTo("frontend_clear_screen_color"));
        Assert.That(colorSpec.Conflicts, Is.EquivalentTo(new[] { "frontend_clear_screen_dark_green", "frontend_clear_screen_black" }));
        Assert.That(freeCameraSpec.RequiresWindowedPair, Is.True);

        BinaryPatchSpec skipAutoToggleSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "skip_auto_toggle");
        Assert.That(skipAutoToggleSpec.RequiresWindowedPair, Is.True);
        Assert.That(skipAutoToggleSpec.PresetEligibility, Is.EquivalentTo(new[] { "custom" }));

        BinaryPatchSpec pauseInitializerSpec = BinaryPatchEngine.PatchSpecs.Single(spec => spec.Key == "pause_o_scan_initializer_experiment");
        Assert.That(pauseInitializerSpec.FileOffset, Is.EqualTo(0x1144CD));
        Assert.That(pauseInitializerSpec.Original, Is.EqualTo(new byte[] { 0x01 }));
        Assert.That(pauseInitializerSpec.Patched, Is.EqualTo(new byte[] { 0x18 }));
        Assert.That(pauseInitializerSpec.RequiresWindowedPair, Is.True);
        Assert.That(pauseInitializerSpec.ProofLevel, Is.EqualTo("experimental_copied_runtime_cdb_ordered_o_window_proof"));
        Assert.That(pauseInitializerSpec.PresetEligibility, Is.EquivalentTo(new[] { "custom" }));
    }

    [Test]
    public void BinaryPatch_CatalogPresetEligibilityMatchesProfileDefinitions()
    {
        var specsByKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
        foreach (SafeCopyProfilePreset preset in BinaryPatchPlanBuilder.GetSafeCopyProfilePresets())
        {
            foreach (string key in preset.PatchKeys)
            {
                Assert.That(specsByKey.ContainsKey(key), Is.True, $"{preset.Id} references unknown patch key {key}");
                Assert.That(specsByKey[key].PresetEligibility ?? Array.Empty<string>(), Has.Member(preset.Id), $"{key} should allow {preset.Id}");
            }
        }

        string[] compatibilityEligible = BinaryPatchEngine.PatchSpecs
            .Where(spec => (spec.PresetEligibility ?? Array.Empty<string>()).Contains(BinaryPatchPlanBuilder.CompatibilityProfileId, StringComparer.OrdinalIgnoreCase))
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(
            compatibilityEligible,
            Is.EquivalentTo(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId)));

        string[] recommendedEligible = BinaryPatchEngine.PatchSpecs
            .Where(spec => (spec.PresetEligibility ?? Array.Empty<string>()).Contains(BinaryPatchPlanBuilder.RecommendedProfileId, StringComparer.OrdinalIgnoreCase))
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(
            recommendedEligible,
            Is.EquivalentTo(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.RecommendedProfileId)));

        string[] enhancedEligible = BinaryPatchEngine.PatchSpecs
            .Where(spec => (spec.PresetEligibility ?? Array.Empty<string>()).Contains(BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparer.OrdinalIgnoreCase))
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(
            enhancedEligible,
            Is.EquivalentTo(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.EnhancedPreviewProfileId)));

        string[] debugCameraEligible = BinaryPatchEngine.PatchSpecs
            .Where(spec => (spec.PresetEligibility ?? Array.Empty<string>()).Contains(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, StringComparer.OrdinalIgnoreCase))
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(
            debugCameraEligible,
            Is.EquivalentTo(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId)));

        foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs.Where(spec =>
            (spec.PresetEligibility ?? Array.Empty<string>()).Contains(BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparer.OrdinalIgnoreCase)))
        {
            Assert.That(spec.Track, Is.EqualTo("Stable"), $"{spec.Key} must not make the Enhanced Profile Preview depend on experimental byte rows.");
            Assert.That(spec.ProofLevel, Is.Not.Null.And.Not.Empty, $"{spec.Key} must carry a proof level before joining Enhanced Profile Preview.");
            Assert.That(spec.Selectability, Is.Not.Null.And.Not.Empty, $"{spec.Key} must carry selectability before joining Enhanced Profile Preview.");
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
    public void BinaryPatchPlanBuilder_OnlyAddsVersionOverlayCompanionWhenOverlayIsSelected()
    {
        string[] visibleKeys = BinaryPatchPlanBuilder.GetVisibleSpecs()
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(visibleKeys, Does.Contain("version_overlay_use_patched_format_pointer"));
        Assert.That(visibleKeys, Does.Contain("goodies_gallery_display_unlock"));
        Assert.That(visibleKeys, Does.Contain("free_camera_aurore_gate_bypass"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_forward_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_backward_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_strafe_left_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_strafe_right_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_yaw_left_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_yaw_right_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_pitch_up_q_hook"));
        Assert.That(visibleKeys, Does.Contain("free_camera_keyboard_pitch_down_q_hook"));
        Assert.That(visibleKeys, Does.Contain("pause_o_scan_initializer_experiment"));
        Assert.That(visibleKeys, Does.Contain("frontend_clear_screen_dark_green"));
        Assert.That(visibleKeys, Does.Contain("frontend_clear_screen_black"));
        Assert.That(visibleKeys, Does.Not.Contain("version_overlay_patched_format_cave_string"));
        foreach (string caveKey in FreeCameraKeyboardCaveKeys)
        {
            Assert.That(visibleKeys, Does.Not.Contain(caveKey));
        }

        string[] windowedSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(windowedSelection, Is.EquivalentTo(new[] { "resolution_gate", "force_windowed" }));

        string[] overlaySelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "version_overlay_use_patched_format_pointer" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            overlaySelection,
            Is.EquivalentTo(new[]
            {
                "version_overlay_use_patched_format_pointer",
                "version_overlay_patched_format_cave_string"
            }));

        string[] freeCameraKeyboardForwardSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_forward_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardForwardSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_forward_q_cave",
                "free_camera_keyboard_forward_q_hook"
            }));

        string[] freeCameraKeyboardBackwardSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_backward_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardBackwardSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_backward_q_cave",
                "free_camera_keyboard_backward_q_hook"
            }));

        string[] freeCameraKeyboardStrafeLeftSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_strafe_left_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardStrafeLeftSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_strafe_left_q_cave",
                "free_camera_keyboard_strafe_left_q_hook"
            }));

        string[] freeCameraKeyboardStrafeRightSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_strafe_right_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardStrafeRightSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_strafe_right_q_cave",
                "free_camera_keyboard_strafe_right_q_hook"
            }));

        string[] freeCameraKeyboardYawLeftSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_yaw_left_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardYawLeftSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_yaw_left_q_cave",
                "free_camera_keyboard_yaw_left_q_hook"
            }));

        string[] freeCameraKeyboardYawRightSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_yaw_right_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardYawRightSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_yaw_right_q_cave",
                "free_camera_keyboard_yaw_right_q_hook"
            }));

        string[] freeCameraKeyboardPitchUpSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_pitch_up_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardPitchUpSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_pitch_up_q_cave",
                "free_camera_keyboard_pitch_up_q_hook"
            }));

        string[] freeCameraKeyboardPitchDownSelection = BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "free_camera_keyboard_pitch_down_q_hook" })
            .Select(spec => spec.Key)
            .ToArray();

        Assert.That(
            freeCameraKeyboardPitchDownSelection,
            Is.EquivalentTo(new[]
            {
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_pitch_down_q_cave",
                "free_camera_keyboard_pitch_down_q_hook"
            }));
    }

    [Test]
    public void BinaryPatchPlanBuilder_SafeCopyProfilePresetsCarryExpectedPolicy()
    {
        Assert.That(BinaryPatchPlanBuilder.UsingFallbackSafeCopyProfileCatalog, Is.False, BinaryPatchPlanBuilder.SafeCopyProfileCatalogStatus);
        Assert.That(BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion, Is.EqualTo("safe-copy-profiles.v1"));
        Assert.That(BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256, Has.Length.EqualTo(64));
        Assert.That(BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256.All(Uri.IsHexDigit), Is.True);

        var presets = BinaryPatchPlanBuilder.GetSafeCopyProfilePresets()
            .ToDictionary(preset => preset.Id, StringComparer.OrdinalIgnoreCase);

        Assert.That(
            presets.Keys,
            Is.EquivalentTo(new[]
            {
                BinaryPatchPlanBuilder.CompatibilityProfileId,
                BinaryPatchPlanBuilder.RecommendedProfileId,
                BinaryPatchPlanBuilder.EnhancedPreviewProfileId,
                BinaryPatchPlanBuilder.DebugCameraPreviewProfileId,
                BinaryPatchPlanBuilder.CustomProfileId,
            }));

        Assert.That(presets[BinaryPatchPlanBuilder.CompatibilityProfileId].DisplayName, Is.EqualTo("Compatibility Copy"));
        Assert.That(presets[BinaryPatchPlanBuilder.CompatibilityProfileId].IsSelectable, Is.True);
        Assert.That(
            BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId),
            Is.EqualTo(new[] { "resolution_gate", "force_windowed" }));
        Assert.That(presets[BinaryPatchPlanBuilder.CompatibilityProfileId].DefaultControllerConfiguration, Is.Null);
        Assert.That(presets[BinaryPatchPlanBuilder.CompatibilityProfileId].DefaultPersistControllerConfigInOptions, Is.False);
        Assert.That(presets[BinaryPatchPlanBuilder.CompatibilityProfileId].DefaultSharpenMouseLook, Is.False);

        Assert.That(presets[BinaryPatchPlanBuilder.RecommendedProfileId].DisplayName, Is.EqualTo("Windowed + Graphics Defaults"));
        Assert.That(presets[BinaryPatchPlanBuilder.RecommendedProfileId].IsSelectable, Is.True);
        string[] recommendedKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.RecommendedProfileId).ToArray();
        Assert.That(
            recommendedKeys,
            Is.EqualTo(new[]
            {
                "resolution_gate",
                "force_windowed",
                "extra_graphics_default_on",
                "ignore_cardid_tweak_overrides",
            }));
        Assert.That(BinaryPatchPlanBuilder.ValidateVisibleSelection(recommendedKeys), Is.Null);
        Assert.That(presets[BinaryPatchPlanBuilder.RecommendedProfileId].DefaultControllerConfiguration, Is.Null);
        Assert.That(presets[BinaryPatchPlanBuilder.RecommendedProfileId].DefaultPersistControllerConfigInOptions, Is.False);
        Assert.That(presets[BinaryPatchPlanBuilder.RecommendedProfileId].DefaultSharpenMouseLook, Is.False);

        Assert.That(presets[BinaryPatchPlanBuilder.CustomProfileId].DisplayName, Is.EqualTo("Custom"));
        Assert.That(presets[BinaryPatchPlanBuilder.CustomProfileId].IsSelectable, Is.True);
        Assert.That(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CustomProfileId), Is.Empty);
        Assert.That(presets[BinaryPatchPlanBuilder.CustomProfileId].DefaultControllerConfiguration, Is.Null);
        Assert.That(presets[BinaryPatchPlanBuilder.CustomProfileId].DefaultPersistControllerConfigInOptions, Is.False);
        Assert.That(presets[BinaryPatchPlanBuilder.CustomProfileId].DefaultSharpenMouseLook, Is.False);

        foreach (SafeCopyProfilePreset preset in presets.Values.Where(preset =>
            preset.IsSelectable &&
            !string.Equals(preset.Id, BinaryPatchPlanBuilder.CustomProfileId, StringComparison.OrdinalIgnoreCase)))
        {
            Assert.That(preset.Modules, Is.Not.Empty, $"{preset.Id} should explain what the profile includes before safe-copy creation.");
            Assert.That(preset.Modules, Has.All.Matches<SafeCopyProfileModule>(module =>
                !string.IsNullOrWhiteSpace(module.DisplayName) &&
                !string.IsNullOrWhiteSpace(module.ProofStatus) &&
                !string.IsNullOrWhiteSpace(module.ClaimBoundary) &&
                !string.IsNullOrWhiteSpace(module.RestoreStrategy) &&
                module.EvidenceRefs.Count > 0 &&
                module.NonClaims.Count > 0), $"{preset.Id} modules should carry evidence, restore, and non-claim copy for the WinUI preset details surface.");
        }

        SafeCopyProfilePreset enhancedPreset = presets[BinaryPatchPlanBuilder.EnhancedPreviewProfileId];
        Assert.That(enhancedPreset.DisplayName, Is.EqualTo("Enhanced Profile Preview"));
        Assert.That(enhancedPreset.IsSelectable, Is.True);
        Assert.That(enhancedPreset.DefaultControllerConfiguration, Is.EqualTo(1));
        Assert.That(enhancedPreset.DefaultPersistControllerConfigInOptions, Is.True);
        Assert.That(enhancedPreset.DefaultSharpenMouseLook, Is.True);
        string[] enhancedKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.EnhancedPreviewProfileId).ToArray();
        Assert.That(
            enhancedKeys,
            Is.EqualTo(new[]
            {
                "resolution_gate",
                "force_windowed",
                "extra_graphics_default_on",
                "ignore_cardid_tweak_overrides",
                "version_overlay_use_patched_format_pointer",
                "frontend_clear_screen_dark_red",
                "goodies_gallery_display_unlock",
            }));
        Assert.That(enhancedKeys, Does.Not.Contain("skip_auto_toggle"));
        Assert.That(enhancedKeys, Does.Not.Contain("pause_o_scan_initializer_experiment"));
        Assert.That(enhancedKeys, Does.Not.Contain("free_camera_aurore_gate_bypass"));
        Assert.That(enhancedKeys, Does.Not.Contain("frontend_clear_screen_dark_green"));
        Assert.That(enhancedKeys, Does.Not.Contain("frontend_clear_screen_black"));
        Assert.That(enhancedKeys, Does.Not.Contain(GameProfileMusicReplacementService.UseBea02ForBea01PresetId));
        Assert.That(enhancedKeys, Does.Not.Contain(GameProfileMusicReplacementService.UseBea01ForBea02PresetId));
        Assert.That(BinaryPatchPlanBuilder.ValidateVisibleSelection(enhancedKeys), Is.Null);
        Assert.That(
            enhancedPreset.Modules.Select(module => module.Id),
            Is.EqualTo(new[]
            {
                "windowed-compatibility",
                "graphics-defaults",
                "title-marker",
                "frontend-red-margins",
                "goodies-display-preview",
                "copied-options-control-defaults",
            }));
        Assert.That(enhancedPreset.Modules, Has.All.Matches<SafeCopyProfileModule>(module =>
            !string.IsNullOrWhiteSpace(module.RestoreStrategy) &&
            module.EvidenceRefs.Count > 0 &&
            module.NonClaims.Count > 0));
        Assert.That(enhancedPreset.Modules.Select(module => module.Id), Does.Not.Contain("music-swap-presets"));
        SafeCopyProfileModule copiedControlModule = enhancedPreset.Modules.Single(module => module.Id == "copied-options-control-defaults");
        Assert.That(copiedControlModule.PatchKeys, Is.Empty);
        Assert.That(copiedControlModule.CopiedOptionsEdits, Is.EqualTo(new[] { "controllerConfiguration=1", "mouseLookSensitivity=2.25" }));
        Assert.That(copiedControlModule.ClaimBoundary, Does.Contain("does not prove improved feel"));
        Assert.That(copiedControlModule.RestoreStrategy, Does.Contain("copied defaultoptions.bea backup"));
        Assert.That(copiedControlModule.EvidenceRefs, Does.Contain("release/readiness/winui_safe_copy_control_options_2026-06-17.md"));
        Assert.That(copiedControlModule.NonClaims, Does.Contain("No improved control-feel proof."));

        string[] enhancedExpandedKeys = BinaryPatchPlanBuilder.BuildSelectedSpecs(enhancedKeys)
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(enhancedExpandedKeys, Does.Contain("version_overlay_patched_format_cave_string"));
        Assert.That(enhancedExpandedKeys, Does.Not.Contain("skip_auto_toggle"));
        Assert.That(enhancedExpandedKeys, Does.Not.Contain("pause_o_scan_initializer_experiment"));
        Assert.That(enhancedExpandedKeys, Does.Not.Contain("free_camera_aurore_gate_bypass"));

        SafeCopyProfilePreset debugCameraPreset = presets[BinaryPatchPlanBuilder.DebugCameraPreviewProfileId];
        Assert.That(debugCameraPreset.DisplayName, Is.EqualTo("Debug Camera Preview"));
        Assert.That(debugCameraPreset.IsSelectable, Is.True);
        Assert.That(debugCameraPreset.ProofStatus, Does.Contain("Experimental"));
        string[] debugCameraKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId).ToArray();
        Assert.That(
            debugCameraKeys,
            Is.EqualTo(new[]
            {
                "resolution_gate",
                "force_windowed",
                "free_camera_aurore_gate_bypass",
                "free_camera_keyboard_forward_q_hook",
            }));
        Assert.That(BinaryPatchPlanBuilder.ValidateVisibleSelection(debugCameraKeys), Is.Null);
        Assert.That(debugCameraPreset.Modules.Select(module => module.Id), Is.EqualTo(new[]
        {
            "windowed-compatibility",
            "debug-camera-q-forward",
        }));
        SafeCopyProfileModule debugCameraModule = debugCameraPreset.Modules.Single(module => module.Id == "debug-camera-q-forward");
        Assert.That(debugCameraModule.ClaimBoundary, Does.Contain("Q-forward"));
        Assert.That(debugCameraModule.NonClaims, Does.Contain("No full free-camera control scheme proof."));
        string[] debugCameraExpandedKeys = BinaryPatchPlanBuilder.BuildSelectedSpecs(debugCameraKeys)
            .Select(spec => spec.Key)
            .ToArray();
        Assert.That(debugCameraExpandedKeys, Is.EquivalentTo(new[]
        {
            "resolution_gate",
            "force_windowed",
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_forward_q_cave",
            "free_camera_keyboard_forward_q_hook",
        }));
    }

    [Test]
    public void BinaryPatchPlanBuilder_RejectsMultipleFrontendColorPresets()
    {
        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[]
            {
                "frontend_clear_screen_dark_red",
                "frontend_clear_screen_dark_green"
            }),
            Does.Contain("only one frontend clear-screen color preset"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[]
            {
                "frontend_clear_screen_black",
                "resolution_gate",
                "force_windowed"
            }),
            Is.Null);
    }

    [Test]
    public void BinaryPatchPlanBuilder_RejectsUnknownOrHiddenVisibleSelection()
    {
        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "version_overlay_patched_format_cave_string" }),
            Does.Contain("not selectable"));

        foreach (string caveKey in FreeCameraKeyboardCaveKeys)
        {
            Assert.That(
                BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { caveKey }),
                Does.Contain("not selectable"));
        }

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "not_a_patch_row" }),
            Does.Contain("not selectable"));
    }

    [Test]
    public void BinaryPatchPlanBuilder_RequiresWindowedPairForExperimentalFullscreenFallback()
    {
        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "skip_auto_toggle" }),
            Does.Contain("Allow non-4:3 mode candidates"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "skip_auto_toggle", "version_overlay_use_patched_format_pointer" }),
            Does.Contain("Allow non-4:3 mode candidates"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "skip_auto_toggle", "extra_graphics_default_on" }),
            Does.Contain("Allow non-4:3 mode candidates"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "skip_auto_toggle", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "pause_o_scan_initializer_experiment", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_aurore_gate_bypass", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_forward_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_backward_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_strafe_left_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_strafe_right_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_yaw_left_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_yaw_right_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_pitch_up_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_pitch_down_q_hook", "resolution_gate", "force_windowed" }),
            Is.Null);

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(FreeCameraKeyboardHookKeys.Concat(new[] { "resolution_gate", "force_windowed" })),
            Does.Contain("free camera keyboard q remap"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_forward_q_hook", "resolution_gate", "force_windowed" }),
            Does.Contain("free camera keyboard q remap"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_aurore_gate_bypass", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "pause_o_scan_initializer_experiment", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_forward_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_backward_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_strafe_left_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_strafe_right_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_yaw_left_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_yaw_right_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_pitch_up_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));

        Assert.That(
            BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "free_camera_keyboard_pitch_down_q_hook", "extra_graphics_default_on" }),
            Does.Contain("baseline windowed compatibility pair"));
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

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CreateHardLink(
        string lpFileName,
        string lpExistingFileName,
        IntPtr lpSecurityAttributes);
}
