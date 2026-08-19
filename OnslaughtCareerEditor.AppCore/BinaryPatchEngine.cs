using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace OnslaughtCareerEditor.AppCore
{
    public sealed record BinaryPatchRegion(
        int FileOffset,
        byte[] Original,
        byte[] Patched);

    public sealed record BinaryPatchSpec(
        string Key,
        string Track,
        string DisplayName,
        int FileOffset,
        byte[] Original,
        byte[] Patched,
        bool Optional = false,
        IReadOnlyList<string>? TargetBinaryHashes = null,
        long? TargetBinarySize = null,
        IReadOnlyList<string>? Dependencies = null,
        IReadOnlyList<string>? Conflicts = null,
        string? ExclusiveGroup = null,
        string? ProofLevel = null,
        string? Selectability = null,
        IReadOnlyList<string>? PresetEligibility = null,
        bool RequiresWindowedPair = false,
        IReadOnlyList<BinaryPatchRegion>? AdditionalRegions = null);

    public enum BinaryPatchState
    {
        Original,
        Patched,
        Mismatch,
        OutOfRange,
    }

    public sealed record BinaryPatchVerifyRow(BinaryPatchSpec Spec, BinaryPatchState State);

    /// <summary>
    /// Permission to write to the executable of an installed game, which every other path here
    /// refuses outright.
    ///
    /// It cannot be constructed by asking. The only way to get one is
    /// <see cref="BinaryPatchEngine.AuthorizeInstalledGameWrite"/>, which will not return one until
    /// a full-file backup of the original executable exists beside it, carries a hash sidecar, and
    /// has been verified against a clean retail specimen. So "there is a verified backup" is not a
    /// rule the calling code has to remember - it is the reason this object exists at all, and a
    /// caller that skips the backup has nothing to pass.
    ///
    /// This is deliberately the same shape as
    /// <c>FileMutationSafety.AuthorizeAppOwnedProfileRoot</c>: a normally-forbidden write, made
    /// possible by a token that could only be obtained by satisfying the condition first.
    /// </summary>
    public sealed class InstalledGameWriteAuthorization
    {
        internal InstalledGameWriteAuthorization(
            string exePath,
            string gameRoot,
            string backupPath,
            string backupHashPath,
            string backupSha256,
            bool backupWasCreatedNow,
            bool hashSidecarWasCreatedNow,
            string summary)
        {
            ExePath = exePath;
            GameRoot = gameRoot;
            BackupPath = backupPath;
            BackupHashPath = backupHashPath;
            BackupSha256 = backupSha256;
            BackupWasCreatedNow = backupWasCreatedNow;
            HashSidecarWasCreatedNow = hashSidecarWasCreatedNow;
            Summary = summary;
        }

        /// <summary>The one executable this authorization covers. Anything else is refused.</summary>
        public string ExePath { get; }

        public string GameRoot { get; }

        /// <summary>The verified full-file backup. Restore reads from here.</summary>
        public string BackupPath { get; }

        public string BackupHashPath { get; }

        /// <summary>The backup's SHA-256, lowercase hex - the same text the sidecar holds.</summary>
        public string BackupSha256 { get; }

        /// <summary>True when this call is what made the backup, rather than finding one.</summary>
        public bool BackupWasCreatedNow { get; }

        /// <summary>
        /// True when a backup was already there but had no hash sidecar, and this call wrote one.
        /// That is the state a hand-patched install is usually in.
        /// </summary>
        public bool HashSidecarWasCreatedNow { get; }

        /// <summary>What happened, in one or two sentences a person can read.</summary>
        public string Summary { get; }
    }

    /// <param name="InstalledGame">
    /// Non-null only for a write to an installed game the user has opted into. Obtaining one
    /// requires a verified backup to already exist, so this is also the proof that it does.
    /// </param>
    public sealed record BinaryPatchTargetOptions(
        string ExePath,
        string AllowedRoot,
        bool AllowFallbackCatalogForTests = false,
        bool AllowByteLayoutOnlyTarget = false,
        InstalledGameWriteAuthorization? InstalledGame = null);

    public sealed record BinaryPatchTargetVerifyResult(
        bool Success,
        string Message,
        IReadOnlyList<BinaryPatchVerifyRow> Rows,
        string? IdentityLabel = null);

    internal sealed record BinaryPatchCatalogLoadResult(
        BinaryPatchSpec[] Specs,
        bool UsingFallback,
        string Status);

    /// <summary>
    /// Core byte-verified patch engine for BEA.exe catalog-driven patches.
    /// </summary>
    public static class BinaryPatchEngine
    {
        public const string BackupSuffix = ".original.backup";
        public const string InstalledBackupFailed =
            "The backup could not be made, so nothing was patched. Your game is untouched.";
        public const string InstalledPathUnreadable =
            "That game file could not be read. Nothing was changed.";
        public const string WorkingCopyPathUnusable =
            "That patch target could not be used. Nothing was changed.";
        public const string WorkspaceFolderRequired =
            "An app-owned workspace folder is required.";
        public const string PatchTargetMustStayInsideWorkspaceFolder =
            "Patch target must stay inside the workspace folder.";
        public const string BackupMustStayInsideWorkspaceFolder =
            "BEA.exe.original.backup must stay inside the workspace folder.";
        public const string BackupHashMustStayInsideWorkspaceFolder =
            "The backup hash file must stay inside the workspace folder.";
        public const string ProtectedInstallFolder =
            "Patch target is under Program Files or another protected install folder. Work in a copy, or choose to patch your installed game - which takes a verified backup first.";
        public const string BackupFileMissing =
            "BEA.exe.original.backup could not be found. Nothing was changed.";
        public const string BackupHashWithoutBackup =
            "The backup hash file is here without BEA.exe.original.backup. Remove that leftover hash file. Nothing was changed.";
        public const string BeaExeOnlyCopyIdentity = "BEA.exe-only copy";
        public const string TargetCannotUseLink = "That file cannot use a shortcut or link.";
        public const string FileCannotShareData = "That file cannot share its data with another file.";
        public const string StagedFileVerificationFailed = "That staged file could not be verified.";
        public const string PublishedFileDidNotMatch = "That published file did not match the staged file.";
        private const string BackupHashSuffix = ".sha256";
        private const string CatalogRelativePath = "patches/catalog/patches.v2.json";
        private const string ExpectedPatchCatalogSha256 = "48cebf987355622bb54c212d5af4705a6c80df468a25651773c6f41522619622";
        private const string TargetFileName = "BEA.exe";
        private const string KnownRetailSteamSha256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
        private const long KnownRetailSteamSize = 2_506_752;
        private static readonly string[] s_knownRetailSteamHashes = { KnownRetailSteamSha256 };
        private static readonly BinaryPatchRegion[] s_widescreenAspectRegions =
        {
            new(0x01B087, new byte[] { 0xC4, 0x8B, 0x5D }, new byte[] { 0xF0, 0x4F, 0x9D }),
            new(0x0506CE, new byte[] { 0x68, 0x00, 0x00, 0x40, 0x3F }, new byte[] { 0xE9, 0x5F, 0x78, 0x18, 0x00 }),
            new(0x12B156, new byte[] { 0xD9, 0x05, 0xF0, 0x4A, 0x5E, 0x00 }, new byte[] { 0xE9, 0x07, 0xCD, 0x0A, 0x00, 0x90 }),
            new(0x12B200, new byte[] { 0xE8, 0x3B, 0x65, 0xF1, 0xFF }, new byte[] { 0xE9, 0x98, 0xCD, 0x0A, 0x00 }),
            new(0x12B983, new byte[] { 0xF0, 0x4A, 0x5E }, new byte[] { 0xF8, 0x4F, 0x9D }),
            new(0x12C790, new byte[] { 0xF0, 0x4A, 0x5E }, new byte[] { 0xF8, 0x4F, 0x9D }),
            new(0x13E32F, new byte[] { 0x8B, 0x11, 0xFF, 0x52, 0x10 }, new byte[] { 0xE9, 0x9D, 0x9C, 0x09, 0x00 }),
            new(0x13F3B7, new byte[] { 0xD9, 0x05, 0x40, 0x8A, 0x88, 0x00 }, new byte[] { 0xE9, 0x99, 0x45, 0x06, 0x00, 0x90 }),
            new(0x141B59, new byte[] { 0xD9, 0x84, 0x24, 0xC4 }, new byte[] { 0xE9, 0x83, 0x64, 0x09 }),
            new(0x141B5E, new byte[] { 0x00, 0x00 }, new byte[] { 0x90, 0x90 }),
            new(0x1A3955, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xD9, 0x05, 0x98, 0xB3, 0x5D, 0x00, 0xD8, 0x35, 0xF8, 0x4F, 0x9D, 0x00, 0xE9, 0x57, 0xBA, 0xF9, 0xFF }),
            new(0x1D7DB5, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xD8, 0x84, 0xE4, 0xC4, 0x00, 0x00, 0x00, 0xEB, 0x28 }),
            new(0x1D7DE6, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xE9, 0x75, 0x9D, 0xF6, 0xFF }),
            new(0x1D7E42, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xE9, 0x63, 0x33, 0xF5, 0xFF }),
            new(0x1D7E62, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xDB, 0x85, 0x58, 0x2E, 0x03, 0x00, 0xDA, 0xB5, 0x5C, 0x2E, 0x03, 0x00, 0xEB, 0xD2 }),
            new(0x1D7F32, new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, new byte[] { 0xFF, 0x35, 0xF0, 0x4F, 0x9D, 0x00, 0xE9, 0x96, 0x87, 0xE7, 0xFF }),
            new(0x1D7F9D, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xDB, 0x85, 0x5C, 0x2E, 0x03 }),
            new(0x1D7FA3, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xDA, 0xB5, 0x58, 0x2E, 0x03 }),
            new(0x1D7FA9, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD9, 0x15, 0xF0, 0x4F, 0x9D }),
            new(0x1D7FAF, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD8, 0x3D, 0xC4, 0x8B, 0x5D }),
            new(0x1D7FB5, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD9, 0x15, 0xF4, 0x4F, 0x9D }),
            new(0x1D7FBB, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD8, 0x35, 0xC4, 0x8B, 0x5D }),
            new(0x1D7FC1, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD9, 0x1D, 0xF8, 0x4F, 0x9D }),
            new(0x1D7FC7, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xE8, 0x74, 0x97, 0xE6, 0xFF, 0xE9, 0x34, 0x32, 0xF5, 0xFF, 0x8B, 0x11, 0xFF, 0x52, 0x10, 0xD8, 0x0D, 0xF4, 0x4F, 0x9D }),
            new(0x1D7FDC, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xE9, 0x53, 0x63, 0xF6, 0xFF, 0xD9, 0x44, 0xE4, 0x10, 0xD9, 0xC0, 0xD8, 0x35, 0xF4, 0x4F, 0x9D }),
            new(0x1D7FED, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xD9, 0x54, 0xE4, 0x10, 0xDE, 0xE9, 0xD8, 0x0D, 0xEC, 0x85, 0x5D }),
            new(0x1D7FF9, new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00 }, new byte[] { 0xE9, 0xB7, 0xFD, 0xFF, 0xFF }),
        };

        private static readonly BinaryPatchSpec[] s_fallbackPatchSpecs =
        {
            new(
                Key: "resolution_gate",
                Track: "Stable",
                DisplayName: "Correct 16:9 gameplay aspect and field of view",
                FileOffset: 0x129696,
                Original: new byte[] { 0xCC },
                Patched: new byte[] { 0x00 },
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "copied_gameplay_runtime_16_9",
                Selectability: "profile_visible",
                PresetEligibility: new[] { "compatibility-copy", "recommended-safe-copy", "enhanced-edition-preview", "debug-camera-preview", "custom" },
                AdditionalRegions: s_widescreenAspectRegions),
            new(
                Key: "force_windowed",
                Track: "Stable",
                DisplayName: "Prefer windowed startup (when windowed-capable)",
                FileOffset: 0x12A644,
                Original: new byte[] { 0xA1, 0xF0, 0x2D, 0x66, 0x00 },
                Patched: new byte[] { 0xB8, 0x01, 0x00, 0x00, 0x00 },
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "byte_verified_static_and_copied_launch_pair",
                Selectability: "profile_visible",
                PresetEligibility: new[] { "compatibility-copy", "recommended-safe-copy", "enhanced-edition-preview", "debug-camera-preview", "custom" }),
            new(
                Key: "extra_graphics_default_on",
                Track: "Stable",
                DisplayName: "Default GEFORCE_FX_POWER tweak on",
                FileOffset: 0x0CDD40,
                Original: new byte[] { 0x6A, 0x00 },
                Patched: new byte[] { 0x6A, 0x01 },
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "byte_verified_static_and_copied_launch_smoke",
                Selectability: "profile_visible",
                PresetEligibility: new[] { "recommended-safe-copy", "enhanced-edition-preview", "custom" }),
            new(
                Key: "ignore_cardid_tweak_overrides",
                Track: "Stable",
                DisplayName: "Ignore cardid.txt vendor/device tweak overrides",
                FileOffset: 0x12AF3F,
                Original: new byte[] { 0xE8, 0x9C, 0xD7, 0xFF, 0xFF },
                Patched: new byte[] { 0x90, 0x90, 0x90, 0x90, 0x90 },
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "byte_verified_static_and_copied_launch_smoke",
                Selectability: "profile_visible",
                PresetEligibility: new[] { "recommended-safe-copy", "enhanced-edition-preview", "custom" }),
            new(
                Key: "version_overlay_use_patched_format_pointer",
                Track: "Stable",
                DisplayName: "Install PATCHED version-overlay marker pointer",
                FileOffset: 0x6416F,
                Original: new byte[] { 0x54, 0x94, 0x62, 0x00 },
                Patched: new byte[] { 0x44, 0xA4, 0x5A, 0x00 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "version_overlay_patched_format_cave_string" },
                ProofLevel: "title_screen_runtime_visual_smoke",
                Selectability: "optional_visible",
                PresetEligibility: new[] { "enhanced-edition-preview", "custom" }),
            new(
                Key: "version_overlay_patched_format_cave_string",
                Track: "Stable",
                DisplayName: "Version overlay cave format payload (V%1d.%02d - PATCHED)",
                FileOffset: 0x1AA444,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x56, 0x25, 0x31, 0x64, 0x2E, 0x25, 0x30, 0x32, 0x64, 0x20, 0x2D, 0x20, 0x50, 0x41, 0x54, 0x43, 0x48, 0x45, 0x44, 0x00 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "companion_payload_byte_verified",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>()),
            new(
                Key: "frontend_clear_screen_dark_red",
                Track: "Stable",
                DisplayName: "Frontend clear-screen dark red preset",
                FileOffset: 0x140F88,
                Original: new byte[] { 0x3F, 0x1F, 0x1F, 0x00 },
                Patched: new byte[] { 0x1F, 0x1F, 0xBF, 0x00 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "frontend_clear_screen_dark_green", "frontend_clear_screen_black" },
                ExclusiveGroup: "frontend_clear_screen_color",
                ProofLevel: "title_screen_runtime_visual_smoke",
                Selectability: "optional_visible",
                PresetEligibility: new[] { "enhanced-edition-preview", "custom" }),
            new(
                Key: "frontend_clear_screen_dark_green",
                Track: "Stable",
                DisplayName: "Frontend clear-screen dark green preset",
                FileOffset: 0x140F88,
                Original: new byte[] { 0x3F, 0x1F, 0x1F, 0x00 },
                Patched: new byte[] { 0x1F, 0xBF, 0x1F, 0x00 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "frontend_clear_screen_dark_red", "frontend_clear_screen_black" },
                ExclusiveGroup: "frontend_clear_screen_color",
                ProofLevel: "title_screen_runtime_visual_smoke",
                Selectability: "optional_visible",
                PresetEligibility: new[] { "custom" }),
            new(
                Key: "frontend_clear_screen_black",
                Track: "Stable",
                DisplayName: "Frontend clear-screen black preset",
                FileOffset: 0x140F88,
                Original: new byte[] { 0x3F, 0x1F, 0x1F, 0x00 },
                Patched: new byte[] { 0x00, 0x00, 0x00, 0x00 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "frontend_clear_screen_dark_red", "frontend_clear_screen_dark_green" },
                ExclusiveGroup: "frontend_clear_screen_color",
                ProofLevel: "title_screen_runtime_visual_smoke",
                Selectability: "optional_visible",
                PresetEligibility: new[] { "custom" }),
            new(
                Key: "goodies_gallery_display_unlock",
                Track: "Stable",
                DisplayName: "Goodies gallery display flag override",
                FileOffset: 0x05D7F4,
                Original: new byte[] { 0xE8, 0x97, 0x7C, 0x00, 0x00, 0xF7, 0xD8, 0x1B, 0xC0 },
                Patched: new byte[] { 0x83, 0xC4, 0x04, 0x83, 0xC8, 0xFF, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "goodies_wall_runtime_visual_smoke",
                Selectability: "optional_visible",
                PresetEligibility: new[] { "enhanced-edition-preview", "custom" }),
            new(
                Key: "skip_auto_toggle",
                Track: "Experimental",
                DisplayName: "Bypass one startup fullscreen toggle check",
                FileOffset: 0x12BB97,
                Original: new byte[] { 0x75, 0x20 },
                Patched: new byte[] { 0xEB, 0x20 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "experimental_byte_verified_startup_path",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "pause_o_scan_initializer_experiment",
                Track: "Experimental",
                DisplayName: "Experimental: O scan for default pause initializer",
                FileOffset: 0x1144CD,
                Original: new byte[] { 0x01 },
                Patched: new byte[] { 0x18 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "experimental_copied_runtime_cdb_ordered_o_window_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_aurore_gate_bypass",
                Track: "Experimental",
                DisplayName: "Experimental: bypass Aurore free-camera gate",
                FileOffset: 0x06F83C,
                Original: new byte[] { 0x0F, 0x84, 0x58, 0x02, 0x00, 0x00 },
                Patched: new byte[] { 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "experimental_copied_runtime_cdb_toggle_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom", "debug-camera-preview" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_forward_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-forward remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1F, 0x75, 0x09, 0xB8, 0x26, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_forward_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_forward_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-forward free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_forward_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_forward_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom", "debug-camera-preview" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_backward_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-backward remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x20, 0x75, 0x09, 0xB8, 0x27, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_backward_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_backward_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-backward free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_backward_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_backward_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_strafe_left_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-strafe-left remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1D, 0x75, 0x09, 0xB8, 0x28, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_strafe_left_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_strafe_left_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-strafe-left free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_strafe_left_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_strafe_left_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_strafe_right_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-strafe-right remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1E, 0x75, 0x09, 0xB8, 0x29, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_strafe_right_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_strafe_right_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-strafe-right free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_strafe_right_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_strafe_right_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_yaw_left_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-yaw-left remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x19, 0x75, 0x09, 0xB8, 0x24, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_yaw_left_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_yaw_left_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-yaw-left free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_yaw_left_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_yaw_left_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_yaw_right_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-yaw-right remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1B, 0x75, 0x09, 0xB8, 0x25, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_pitch_up_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_yaw_right_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_yaw_right_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-yaw-right free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_yaw_right_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_pitch_up_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_yaw_right_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_pitch_up_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-pitch-up remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1A, 0x75, 0x09, 0xB8, 0x22, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_down_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_pitch_up_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_pitch_up_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-pitch-up free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_pitch_up_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_down_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_pitch_up_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_pitch_down_q_cave",
                Track: "Experimental",
                DisplayName: "Experimental companion: free-camera Q-pitch-down remap cave",
                FileOffset: 0x1A3A15,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x83, 0xF8, 0x1C, 0x75, 0x09, 0xB8, 0x23, 0x00, 0x00, 0x00, 0x89, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00, 0xE9, 0x58, 0x6F, 0xE7, 0xFF },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Conflicts: new[] { "free_camera_keyboard_forward_q_cave", "free_camera_keyboard_backward_q_cave", "free_camera_keyboard_strafe_left_q_cave", "free_camera_keyboard_strafe_right_q_cave", "free_camera_keyboard_yaw_left_q_cave", "free_camera_keyboard_yaw_right_q_cave", "free_camera_keyboard_pitch_up_q_cave" },
                ProofLevel: "experimental_copied_runtime_cdb_q_pitch_down_proof",
                Selectability: "hidden_companion",
                PresetEligibility: Array.Empty<string>(),
                RequiresWindowedPair: true),
            new(
                Key: "free_camera_keyboard_pitch_down_q_hook",
                Track: "Experimental",
                DisplayName: "Experimental: Q-pitch-down free-camera hook",
                FileOffset: 0x01A980,
                Original: new byte[] { 0x8B, 0x44, 0x24, 0x08, 0x81, 0xEC, 0xC0, 0x00, 0x00, 0x00 },
                Patched: new byte[] { 0xE9, 0x90, 0x90, 0x18, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                Dependencies: new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_pitch_down_q_cave" },
                Conflicts: new[] { "free_camera_keyboard_forward_q_hook", "free_camera_keyboard_backward_q_hook", "free_camera_keyboard_strafe_left_q_hook", "free_camera_keyboard_strafe_right_q_hook", "free_camera_keyboard_yaw_left_q_hook", "free_camera_keyboard_yaw_right_q_hook", "free_camera_keyboard_pitch_up_q_hook" },
                ExclusiveGroup: "free_camera_keyboard_q_remap",
                ProofLevel: "experimental_copied_runtime_cdb_q_pitch_down_proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "custom" },
                RequiresWindowedPair: true),
        };

        private static readonly BinaryPatchCatalogLoadResult s_catalogLoad = LoadPatchSpecsFromCatalog();

        public static IReadOnlyList<BinaryPatchSpec> PatchSpecs => s_catalogLoad.Specs;
        public static bool UsingFallbackCatalog => s_catalogLoad.UsingFallback;
        public static string CatalogStatus => s_catalogLoad.Status;

        public static IReadOnlyList<BinaryPatchRegion> GetPatchRegions(BinaryPatchSpec spec)
        {
            ArgumentNullException.ThrowIfNull(spec);
            var regions = new List<BinaryPatchRegion>(1 + (spec.AdditionalRegions?.Count ?? 0))
            {
                new(spec.FileOffset, spec.Original, spec.Patched),
            };
            if (spec.AdditionalRegions is not null)
            {
                regions.AddRange(spec.AdditionalRegions);
            }

            return regions;
        }

        public static string BuildBackupPath(string exePath) => exePath + BackupSuffix;

        public static string BuildBackupHashPath(string exePath) => BuildBackupPath(exePath) + BackupHashSuffix;

        private static BinaryPatchCatalogLoadResult LoadPatchSpecsFromCatalog()
        {
            string? catalogPath = ResolveCatalogPath();
            if (catalogPath is null)
            {
                return new BinaryPatchCatalogLoadResult(
                    s_fallbackPatchSpecs,
                    UsingFallback: true,
                    Status: "Catalog unavailable; using built-in fallback patch specs.");
            }

            try
            {
                byte[] catalogBytes = File.ReadAllBytes(catalogPath);
                string catalogHash = ComputeSha256Hex(catalogBytes);
                if (!string.Equals(catalogHash, ExpectedPatchCatalogSha256, StringComparison.OrdinalIgnoreCase))
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog hash did not match the supported patch catalog; using built-in fallback patch specs.");
                }

                using var doc = JsonDocument.Parse(catalogBytes);
                if (!doc.RootElement.TryGetProperty("patches", out JsonElement patchesEl) ||
                    patchesEl.ValueKind != JsonValueKind.Array)
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog payload missing patch list; using built-in fallback patch specs.");
                }

                var loaded = new List<BinaryPatchSpec>();
                var invalidRows = new List<string>();
                var seenKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                int rowNumber = 0;
                foreach (JsonElement patchEl in patchesEl.EnumerateArray())
                {
                    rowNumber++;
                    if (!TryParsePatchSpec(patchEl, out BinaryPatchSpec? spec) || spec is null)
                    {
                        invalidRows.Add($"row {rowNumber}");
                        continue;
                    }

                    if (!seenKeys.Add(spec.Key))
                    {
                        invalidRows.Add($"duplicate id '{spec.Key}'");
                        continue;
                    }

                    loaded.Add(spec);
                }

                if (invalidRows.Count > 0)
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: $"Catalog contained invalid patch rows ({string.Join(", ", invalidRows)}); using built-in fallback patch specs.");
                }

                if (loaded.Count == 0)
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog contained no valid patch rows; using built-in fallback patch specs.");
                }

                var expectedKeys = s_fallbackPatchSpecs
                    .Select(spec => spec.Key)
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);
                var actualKeys = loaded
                    .Select(spec => spec.Key)
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);
                if (!expectedKeys.SetEquals(actualKeys))
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog key set did not match the supported patch set; using built-in fallback patch specs.");
                }

                if (!PatchCatalogMatchesFallbackMetadata(loaded, out string mismatch))
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: $"Catalog metadata drift detected for {mismatch}; using built-in fallback patch specs.");
                }

                return new BinaryPatchCatalogLoadResult(
                    loaded.ToArray(),
                    UsingFallback: false,
                    Status: "Loaded the patch catalog.");
            }
            catch (Exception)
            {
                return new BinaryPatchCatalogLoadResult(
                    s_fallbackPatchSpecs,
                    UsingFallback: true,
                    Status: "Catalog could not be read; using built-in fallback patch specs.");
            }
        }

        private static string? ResolveCatalogPath()
        {
            var candidates = new List<string>
            {
                Path.Combine(AppContext.BaseDirectory, CatalogRelativePath),
                Path.Combine(Environment.CurrentDirectory, CatalogRelativePath),
            };

            AddAncestorCatalogCandidates(candidates, AppContext.BaseDirectory);
            AddAncestorCatalogCandidates(candidates, Environment.CurrentDirectory);

            foreach (string candidate in candidates.Distinct(StringComparer.OrdinalIgnoreCase))
            {
                if (File.Exists(candidate))
                    return candidate;
            }

            return null;
        }

        private static void AddAncestorCatalogCandidates(List<string> candidates, string startDirectory)
        {
            DirectoryInfo? current = new(Path.GetFullPath(startDirectory));
            if (File.Exists(current.FullName))
                current = current.Parent;

            while (current is not null)
            {
                candidates.Add(Path.Combine(current.FullName, CatalogRelativePath));
                current = current.Parent;
            }
        }

        private static bool PatchCatalogMatchesFallbackMetadata(IReadOnlyList<BinaryPatchSpec> loaded, out string mismatch)
        {
            var fallbackByKey = s_fallbackPatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            foreach (BinaryPatchSpec actual in loaded)
            {
                if (!fallbackByKey.TryGetValue(actual.Key, out BinaryPatchSpec? expected))
                {
                    mismatch = actual.Key;
                    return false;
                }

                if (!MutationPolicyEquals(expected, actual))
                {
                    mismatch = actual.Key;
                    return false;
                }
            }

            mismatch = string.Empty;
            return true;
        }

        internal static bool MutationPolicyEquals(BinaryPatchSpec expected, BinaryPatchSpec actual)
        {
            return string.Equals(actual.Key, expected.Key, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(actual.Track, expected.Track, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(actual.DisplayName, expected.DisplayName, StringComparison.Ordinal) &&
                actual.FileOffset == expected.FileOffset &&
                actual.Optional == expected.Optional &&
                actual.TargetBinarySize == expected.TargetBinarySize &&
                actual.Original.SequenceEqual(expected.Original) &&
                actual.Patched.SequenceEqual(expected.Patched) &&
                RegionSequenceEquals(actual.AdditionalRegions, expected.AdditionalRegions) &&
                StringSetEquals(actual.TargetBinaryHashes, expected.TargetBinaryHashes) &&
                StringSetEquals(actual.Dependencies, expected.Dependencies) &&
                StringSetEquals(actual.Conflicts, expected.Conflicts) &&
                string.Equals(actual.ExclusiveGroup ?? string.Empty, expected.ExclusiveGroup ?? string.Empty, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(actual.ProofLevel ?? string.Empty, expected.ProofLevel ?? string.Empty, StringComparison.Ordinal) &&
                string.Equals(actual.Selectability ?? string.Empty, expected.Selectability ?? string.Empty, StringComparison.OrdinalIgnoreCase) &&
                StringSetEquals(actual.PresetEligibility, expected.PresetEligibility) &&
                actual.RequiresWindowedPair == expected.RequiresWindowedPair;
        }

        private static bool RegionSequenceEquals(
            IReadOnlyList<BinaryPatchRegion>? left,
            IReadOnlyList<BinaryPatchRegion>? right)
        {
            IReadOnlyList<BinaryPatchRegion> leftRegions = left ?? Array.Empty<BinaryPatchRegion>();
            IReadOnlyList<BinaryPatchRegion> rightRegions = right ?? Array.Empty<BinaryPatchRegion>();
            return leftRegions.Count == rightRegions.Count &&
                leftRegions.Zip(rightRegions).All(pair =>
                    pair.First.FileOffset == pair.Second.FileOffset &&
                    pair.First.Original.SequenceEqual(pair.Second.Original) &&
                    pair.First.Patched.SequenceEqual(pair.Second.Patched));
        }

        private static bool StringSetEquals(IReadOnlyList<string>? left, IReadOnlyList<string>? right)
        {
            var leftSet = (left ?? Array.Empty<string>()).ToHashSet(StringComparer.OrdinalIgnoreCase);
            var rightSet = (right ?? Array.Empty<string>()).ToHashSet(StringComparer.OrdinalIgnoreCase);
            return leftSet.SetEquals(rightSet);
        }

        private static bool TryParsePatchSpec(JsonElement patchEl, out BinaryPatchSpec? spec)
        {
            spec = null;

            if (!TryGetString(patchEl, "id", out string key) ||
                !TryGetString(patchEl, "title", out string displayName) ||
                !TryGetString(patchEl, "track", out string track) ||
                !patchEl.TryGetProperty("file_offset", out JsonElement fileOffsetEl) ||
                !TryParseOffset(fileOffsetEl, out int fileOffset) ||
                !TryGetString(patchEl, "expected_original_bytes", out string originalHex) ||
                !TryGetString(patchEl, "patched_bytes", out string patchedHex) ||
                !TryParseHexBytes(originalHex, out byte[]? originalBytesMaybe) ||
                !TryParseHexBytes(patchedHex, out byte[]? patchedBytesMaybe))
            {
                return false;
            }
            byte[] originalBytes = originalBytesMaybe!;
            byte[] patchedBytes = patchedBytesMaybe!;
            if (originalBytes.Length != patchedBytes.Length || originalBytes.SequenceEqual(patchedBytes))
                return false;

            bool optional = false;
            if (patchEl.TryGetProperty("optional", out JsonElement optionalEl) &&
                optionalEl.ValueKind == JsonValueKind.True)
            {
                optional = true;
            }

            IReadOnlyList<string> targetHashes = ParseTargetHashes(patchEl);
            long? targetBinarySize = TryGetInt64(patchEl, "target_binary_size", out long parsedSize)
                ? parsedSize
                : null;
            if (targetHashes.Count == 0 || targetBinarySize is null or <= 0)
            {
                return false;
            }

            IReadOnlyList<string> dependencies = ParseStringArray(patchEl, "dependencies");
            IReadOnlyList<string> conflicts = ParseStringArray(patchEl, "conflicts");
            string? exclusiveGroup = TryGetOptionalString(patchEl, "exclusive_group");
            string? proofLevel = TryGetOptionalString(patchEl, "proof_level");
            string? selectability = TryGetOptionalString(patchEl, "selectability");
            IReadOnlyList<string> presetEligibility = ParseStringArray(patchEl, "preset_eligibility");
            bool requiresWindowedPair = patchEl.TryGetProperty("requires_windowed_pair", out JsonElement requiresWindowedPairEl) &&
                requiresWindowedPairEl.ValueKind == JsonValueKind.True;
            if (!TryParseAdditionalRegions(patchEl, out IReadOnlyList<BinaryPatchRegion> additionalRegions))
                return false;

            spec = new BinaryPatchSpec(
                Key: key,
                Track: NormalizeTrack(track),
                DisplayName: displayName,
                FileOffset: fileOffset,
                Original: originalBytes,
                Patched: patchedBytes,
                Optional: optional,
                TargetBinaryHashes: targetHashes,
                TargetBinarySize: targetBinarySize,
                Dependencies: dependencies,
                Conflicts: conflicts,
                ExclusiveGroup: exclusiveGroup,
                ProofLevel: proofLevel,
                Selectability: selectability,
                PresetEligibility: presetEligibility,
                RequiresWindowedPair: requiresWindowedPair,
                AdditionalRegions: additionalRegions);
            return true;
        }

        private static bool TryParseAdditionalRegions(
            JsonElement patchEl,
            out IReadOnlyList<BinaryPatchRegion> regions)
        {
            regions = Array.Empty<BinaryPatchRegion>();
            if (!patchEl.TryGetProperty("additional_regions", out JsonElement regionsEl))
                return true;
            if (regionsEl.ValueKind != JsonValueKind.Array)
                return false;

            var parsed = new List<BinaryPatchRegion>();
            foreach (JsonElement regionEl in regionsEl.EnumerateArray())
            {
                if (!regionEl.TryGetProperty("file_offset", out JsonElement fileOffsetEl) ||
                    !TryParseOffset(fileOffsetEl, out int fileOffset) ||
                    !TryGetString(regionEl, "expected_original_bytes", out string originalHex) ||
                    !TryGetString(regionEl, "patched_bytes", out string patchedHex) ||
                    !TryParseHexBytes(originalHex, out byte[]? originalMaybe) ||
                    !TryParseHexBytes(patchedHex, out byte[]? patchedMaybe))
                {
                    return false;
                }

                byte[] original = originalMaybe!;
                byte[] patched = patchedMaybe!;
                if (original.Length != patched.Length || original.SequenceEqual(patched))
                    return false;
                parsed.Add(new BinaryPatchRegion(fileOffset, original, patched));
            }

            regions = parsed;
            return true;
        }

        private static IReadOnlyList<string> ParseTargetHashes(JsonElement patchEl)
        {
            if (!patchEl.TryGetProperty("target_binary_hashes", out JsonElement hashesEl) ||
                hashesEl.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<string>();
            }

            var hashes = new List<string>();
            foreach (JsonElement hashEl in hashesEl.EnumerateArray())
            {
                if (hashEl.ValueKind != JsonValueKind.String)
                    continue;

                string? hash = hashEl.GetString();
                if (string.IsNullOrWhiteSpace(hash))
                    continue;

                string normalized = hash.Trim().ToLowerInvariant();
                if (normalized.Length == 64 && normalized.All(Uri.IsHexDigit))
                    hashes.Add(normalized);
            }

            return hashes.Count == 0
                ? Array.Empty<string>()
                : hashes.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
        }

        private static string NormalizeTrack(string track)
        {
            if (string.Equals(track, "stable", StringComparison.OrdinalIgnoreCase))
                return "Stable";
            if (string.Equals(track, "experimental", StringComparison.OrdinalIgnoreCase))
                return "Experimental";
            return track.Trim();
        }

        private static bool TryGetString(JsonElement parent, string propertyName, out string value)
        {
            value = string.Empty;
            if (!parent.TryGetProperty(propertyName, out JsonElement el) || el.ValueKind != JsonValueKind.String)
                return false;

            string? raw = el.GetString();
            if (string.IsNullOrWhiteSpace(raw))
                return false;

            value = raw.Trim();
            return true;
        }

        private static string? TryGetOptionalString(JsonElement parent, string propertyName)
        {
            if (!parent.TryGetProperty(propertyName, out JsonElement el) || el.ValueKind != JsonValueKind.String)
                return null;

            string? raw = el.GetString();
            return string.IsNullOrWhiteSpace(raw) ? null : raw.Trim();
        }

        private static IReadOnlyList<string> ParseStringArray(JsonElement parent, string propertyName)
        {
            if (!parent.TryGetProperty(propertyName, out JsonElement valuesEl) ||
                valuesEl.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<string>();
            }

            var values = new List<string>();
            foreach (JsonElement valueEl in valuesEl.EnumerateArray())
            {
                if (valueEl.ValueKind != JsonValueKind.String)
                    continue;

                string? raw = valueEl.GetString();
                if (!string.IsNullOrWhiteSpace(raw))
                    values.Add(raw.Trim());
            }

            return values.Count == 0
                ? Array.Empty<string>()
                : values.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
        }

        private static bool TryParseOffset(JsonElement el, out int offset)
        {
            offset = 0;
            try
            {
                if (el.ValueKind == JsonValueKind.Number)
                {
                    return el.TryGetInt32(out offset);
                }

                if (el.ValueKind != JsonValueKind.String)
                    return false;

                string raw = (el.GetString() ?? string.Empty).Trim();
                if (raw.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                {
                    return int.TryParse(
                        raw.AsSpan(2),
                        System.Globalization.NumberStyles.HexNumber,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out offset);
                }

                return int.TryParse(raw, out offset);
            }
            catch
            {
                return false;
            }
        }

        private static bool TryGetInt64(JsonElement parent, string propertyName, out long value)
        {
            value = 0;
            if (!parent.TryGetProperty(propertyName, out JsonElement el))
                return false;

            try
            {
                if (el.ValueKind == JsonValueKind.Number)
                    return el.TryGetInt64(out value);

                if (el.ValueKind != JsonValueKind.String)
                    return false;

                string raw = (el.GetString() ?? string.Empty).Trim();
                if (raw.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                {
                    return long.TryParse(
                        raw.AsSpan(2),
                        System.Globalization.NumberStyles.HexNumber,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out value);
                }

                return long.TryParse(raw, out value);
            }
            catch
            {
                return false;
            }
        }

        private static bool TryParseHexBytes(string raw, out byte[]? bytes)
        {
            bytes = null;
            if (string.IsNullOrWhiteSpace(raw))
                return false;

            string[] tokens = raw.Split(new[] { ' ', '\t', '\r', '\n', ',', ';', '-' }, StringSplitOptions.RemoveEmptyEntries);
            var list = new List<byte>(tokens.Length);

            foreach (string token in tokens)
            {
                string t = token.Trim();
                if (t.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                    t = t.Substring(2);

                if (t.Length == 0)
                    continue;

                if (!byte.TryParse(
                        t,
                        System.Globalization.NumberStyles.HexNumber,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out byte b))
                {
                    return false;
                }

                list.Add(b);
            }

            if (list.Count == 0)
                return false;

            bytes = list.ToArray();
            return true;
        }

        public static BinaryPatchState GetPatchState(byte[] data, BinaryPatchSpec spec)
        {
            bool allOriginal = true;
            bool allPatched = true;
            foreach (BinaryPatchRegion region in GetPatchRegions(spec))
            {
                int length = region.Original.Length;
                if (length != region.Patched.Length)
                    return BinaryPatchState.Mismatch;
                if (region.FileOffset < 0 || region.FileOffset > data.Length - length)
                    return BinaryPatchState.OutOfRange;

                ReadOnlySpan<byte> current = data.AsSpan(region.FileOffset, length);
                allOriginal &= current.SequenceEqual(region.Original);
                allPatched &= current.SequenceEqual(region.Patched);
                if (!current.SequenceEqual(region.Original) && !current.SequenceEqual(region.Patched))
                    return BinaryPatchState.Mismatch;
            }

            if (allPatched)
                return BinaryPatchState.Patched;
            if (allOriginal)
                return BinaryPatchState.Original;
            return BinaryPatchState.Mismatch;
        }

        public static (bool allKnown, bool allPatched, List<BinaryPatchVerifyRow> rows) VerifyPatchSpecs(
            byte[] data,
            IReadOnlyList<BinaryPatchSpec> specs)
        {
            var rows = new List<BinaryPatchVerifyRow>(specs.Count);
            bool allKnown = true;
            bool allPatched = true;

            foreach (var spec in specs)
            {
                BinaryPatchState state = GetPatchState(data, spec);
                rows.Add(new BinaryPatchVerifyRow(spec, state));
                if (state == BinaryPatchState.Original)
                    allPatched = false;
                if (state is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange)
                {
                    allKnown = false;
                    allPatched = false;
                }
            }

            return (allKnown, allPatched, rows);
        }

        public static BinaryPatchTargetVerifyResult VerifyPatchTargetFile(
            BinaryPatchTargetOptions target,
            IReadOnlyList<BinaryPatchSpec> selected)
        {
            if (selected.Count == 0)
                return new BinaryPatchTargetVerifyResult(false, "Select at least one patch to verify.", Array.Empty<BinaryPatchVerifyRow>());

            var policy = ValidatePatchSelectionPolicy(selected);
            if (!policy.success)
                return new BinaryPatchTargetVerifyResult(false, policy.message, Array.Empty<BinaryPatchVerifyRow>());

            var validation = ValidatePatchTarget(target, requireCatalog: true, selected);
            if (!validation.success || validation.info is null)
                return new BinaryPatchTargetVerifyResult(false, validation.message, Array.Empty<BinaryPatchVerifyRow>());

            var (_, _, rows) = VerifyPatchSpecs(validation.info.Data, selected);
            if (rows.Any(r => r.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange))
            {
                return new BinaryPatchTargetVerifyResult(
                    false,
                    "Verification failed: at least one patch location is in an unexpected state.",
                    rows,
                    validation.info.IdentityLabel);
            }

            string summary = rows.All(r => r.State == BinaryPatchState.Patched)
                ? "All selected patches are already applied."
                : "All selected patches are in original or known state and ready to apply.";

            return new BinaryPatchTargetVerifyResult(
                true,
                summary,
                rows,
                validation.info.IdentityLabel);
        }

        public static (bool success, string message) ApplyPatchesToFile(BinaryPatchTargetOptions target, IReadOnlyList<BinaryPatchSpec> selected)
        {
            if (selected.Count == 0)
                return (false, "Select at least one patch to apply.");

            var policy = ValidatePatchSelectionPolicy(selected);
            if (!policy.success)
                return (false, policy.message);

            var validation = ValidatePatchTarget(target, requireCatalog: true, selected);
            if (!validation.success || validation.info is null)
                return (false, validation.message);

            string exePath = validation.info.ExePath;
            byte[] data = validation.info.Data;
            var (_, _, rows) = VerifyPatchSpecs(data, selected);

            if (rows.Any(r => r.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange))
            {
                var abortSb = new StringBuilder();
                abortSb.AppendLine("Apply aborted: unexpected patch state detected.");
                abortSb.AppendLine();
                foreach (var row in rows)
                    abortSb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
                return (false, abortSb.ToString());
            }

            if (rows.All(r => r.State == BinaryPatchState.Patched))
            {
                return (true, "No changes needed. All selected patches are already applied.\n" +
                    $"Target identity: {validation.info.IdentityLabel}");
            }

            string backupPath = validation.info.BackupPath;
            if (File.Exists(backupPath))
            {
                byte[] backupBytes = File.ReadAllBytes(backupPath);
                var backupIntegrity = ValidateBackupSnapshotIntegrity(validation.info.BackupHashPath, backupBytes);
                if (!backupIntegrity.success)
                {
                    return (false,
                        "Apply aborted: existing backup snapshot integrity could not be verified.\n" +
                        backupIntegrity.message);
                }

                var backupProvenance = ValidateBackupSnapshotProvenance(backupBytes, selected, target);
                if (!backupProvenance.success)
                {
                    return (false,
                        "Apply aborted: existing backup snapshot provenance could not be verified.\n" +
                        backupProvenance.message);
                }
            }
            else
            {
                try
                {
                    PublishFileAtomically(backupPath, data, overwrite: false, "patch backup snapshot");
                    WriteBackupHash(validation.info.BackupHashPath, data);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
                {
                    return (false,
                        "Apply aborted: the verified full-file backup could not be created, and the BEA.exe-only copy was not modified.");
                }
            }

            foreach (var row in rows)
            {
                if (row.State == BinaryPatchState.Original)
                {
                    foreach (BinaryPatchRegion region in GetPatchRegions(row.Spec))
                    {
                        region.Patched.CopyTo(data, region.FileOffset);
                    }
                }
            }

            byte[] readBackData;
            try
            {
                readBackData = PublishFileAtomically(exePath, data, overwrite: true, "patched BEA.exe-only copy");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return (false,
                    "Patch apply failed before atomic publication completed. The verified full-file backup remains available.");
            }
            var (_, allPatchedAfterWrite, afterRows) = VerifyPatchSpecs(readBackData, selected);
            if (!allPatchedAfterWrite)
            {
                var readBackSb = new StringBuilder();
                readBackSb.AppendLine("Patch apply failed: on-disk patch verification did not match selected patch bytes.");
                foreach (var row in afterRows)
                    readBackSb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
                return (false, readBackSb.ToString());
            }

            var outSb = new StringBuilder();
            outSb.AppendLine("Patch apply complete.");
            outSb.AppendLine($"Target: {TargetFileName}");
            outSb.AppendLine($"Backup: {TargetFileName}{BackupSuffix}");
            outSb.AppendLine($"Target identity: {validation.info.IdentityLabel}");
            outSb.AppendLine("Selected patch bytes verified on disk.");
            outSb.AppendLine("Restore uses the first full-file backup snapshot, not per-patch undo.");
            outSb.AppendLine();
            outSb.AppendLine("Selected patch states:");
            foreach (var row in afterRows)
                outSb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
            return (true, outSb.ToString());
        }

        public static (bool success, string message) ValidatePatchSelectionPolicy(IReadOnlyList<BinaryPatchSpec> selected)
        {
            var selectedByKey = new Dictionary<string, BinaryPatchSpec>(StringComparer.OrdinalIgnoreCase);
            foreach (BinaryPatchSpec spec in selected)
            {
                if (GetPatchRegions(spec).Any(region => region.Original.SequenceEqual(region.Patched)))
                {
                    return (false, $"Patch selection contains no-op row '{spec.Key}'.");
                }

                if (!selectedByKey.TryAdd(spec.Key, spec))
                {
                    return (false, $"Patch selection contains duplicate row '{spec.Key}'.");
                }
            }

            var selectedKeys = selectedByKey.Keys.ToHashSet(StringComparer.OrdinalIgnoreCase);

            foreach (BinaryPatchSpec spec in selected)
            {
                foreach (string dependency in spec.Dependencies ?? Array.Empty<string>())
                {
                    if (!selectedKeys.Contains(dependency))
                    {
                        return (false, $"Patch selection is missing dependency '{dependency}' required by '{spec.Key}'.");
                    }
                }

                foreach (string conflict in spec.Conflicts ?? Array.Empty<string>())
                {
                    if (selectedKeys.Contains(conflict))
                    {
                        return (false, $"Patch selection contains conflicting rows '{spec.Key}' and '{conflict}'.");
                    }
                }

                if (string.Equals(spec.Selectability, "hidden_companion", StringComparison.OrdinalIgnoreCase) &&
                    !selected.Any(candidate =>
                        !string.Equals(candidate.Selectability, "hidden_companion", StringComparison.OrdinalIgnoreCase) &&
                        (candidate.Dependencies ?? Array.Empty<string>()).Contains(spec.Key, StringComparer.OrdinalIgnoreCase)))
                {
                    return (false, $"Patch selection contains hidden companion row '{spec.Key}' without its visible dependent row.");
                }
            }

            var exclusiveGroupConflict = selected
                .Where(spec => !string.IsNullOrWhiteSpace(spec.ExclusiveGroup))
                .GroupBy(spec => spec.ExclusiveGroup!, StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault(group => group.Count() > 1);
            if (exclusiveGroupConflict is not null)
            {
                return (false, $"Patch selection contains multiple rows from exclusive group '{exclusiveGroupConflict.Key}'.");
            }

            bool hasWindowedPair =
                selectedKeys.Contains("resolution_gate") &&
                selectedKeys.Contains("force_windowed");
            if (selected.Any(spec => spec.RequiresWindowedPair) && !hasWindowedPair)
            {
                return (false, "Patch selection includes a row that requires the baseline windowed compatibility pair.");
            }

            var selectedRanges = selected
                .SelectMany(spec => GetPatchRegions(spec).Select(region => new
                {
                    Spec = spec,
                    Region = region,
                    Start = region.FileOffset,
                    End = region.FileOffset + region.Patched.Length,
                }))
                .ToArray();
            for (int i = 0; i < selectedRanges.Length; i++)
            {
                for (int j = i + 1; j < selectedRanges.Length; j++)
                {
                    bool overlaps = selectedRanges[i].Start < selectedRanges[j].End &&
                        selectedRanges[j].Start < selectedRanges[i].End;
                    bool identicalMutation =
                        selectedRanges[i].Start == selectedRanges[j].Start &&
                        selectedRanges[i].End == selectedRanges[j].End &&
                        selectedRanges[i].Region.Original.SequenceEqual(selectedRanges[j].Region.Original) &&
                        selectedRanges[i].Region.Patched.SequenceEqual(selectedRanges[j].Region.Patched);
                    if (overlaps && !identicalMutation)
                    {
                        return (false, $"Patch selection contains overlapping rows '{selectedRanges[i].Spec.Key}' and '{selectedRanges[j].Spec.Key}'.");
                    }
                }
            }

            var catalogByKey = PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            foreach (BinaryPatchSpec spec in selected)
            {
                if (!catalogByKey.TryGetValue(spec.Key, out BinaryPatchSpec? canonical) ||
                    !MutationPolicyEquals(canonical, spec))
                {
                    return (false, $"Patch selection row '{spec.Key}' is not an exact mutation from the pinned patch catalog.");
                }
            }

            return (true, string.Empty);
        }

        public static (bool success, string message) RestoreFromBackup(BinaryPatchTargetOptions target)
        {
            var validation = ValidatePatchTarget(target, requireCatalog: false, selected: null);
            if (!validation.success || validation.info is null)
                return (false, validation.message);

            string exePath = validation.info.ExePath;
            string backupPath = validation.info.BackupPath;
            if (!File.Exists(backupPath))
                return (false, BackupFileMissing);

            byte[] backupBytes = File.ReadAllBytes(backupPath);
            var backupIntegrity = ValidateBackupSnapshotIntegrity(validation.info.BackupHashPath, backupBytes);
            if (!backupIntegrity.success)
                return (false, backupIntegrity.message);

            var backupProvenance = ValidateBackupSnapshotProvenance(backupBytes, PatchSpecs, target);
            if (!backupProvenance.success)
                return (false, backupProvenance.message);

            var (_, _, currentRows) = VerifyPatchSpecs(validation.info.Data, PatchSpecs);
            IReadOnlyList<BinaryPatchVerifyRow> unexpectedRestoreRows =
                FindUnexpectedRestorePatchRows(validation.info.Data, PatchSpecs, currentRows);

            if (!currentRows.Any(row => row.State == BinaryPatchState.Patched) &&
                validation.info.Data.SequenceEqual(backupBytes))
            {
                return (true,
                    "No changes needed. The BEA.exe-only copy already matches the verified backup snapshot.\n" +
                    $"Target: {TargetFileName}\n" +
                    $"Backup source: {TargetFileName}{BackupSuffix}");
            }

            byte[] restoredBytes;
            try
            {
                restoredBytes = PublishFileAtomically(exePath, backupBytes, overwrite: true, "restored BEA.exe-only copy");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return (false,
                    "Restore failed before atomic publication completed. The verified backup snapshot was left unchanged.");
            }
            if (!restoredBytes.SequenceEqual(backupBytes))
            {
                return (false,
                    "Restore failed: on-disk verification did not match the backup snapshot.\n" +
                    $"Target: {TargetFileName}\n" +
                    $"Backup source: {TargetFileName}{BackupSuffix}");
            }

            return (true,
                "Restore complete.\n" +
                $"Target: {TargetFileName}\n" +
                $"Backup source: {TargetFileName}{BackupSuffix}\n" +
                (unexpectedRestoreRows.Count > 0
                    ? "Recovery: unexpected current patch bytes were replaced from the verified full-file backup.\n"
                    : string.Empty) +
                "Result: full executable restored from the original backup snapshot.\n" +
                "On-disk verification matched the backup snapshot.");
        }

        private static IReadOnlyList<BinaryPatchVerifyRow> FindUnexpectedRestorePatchRows(
            byte[] data,
            IReadOnlyList<BinaryPatchSpec> specs,
            IReadOnlyList<BinaryPatchVerifyRow> rows)
        {
            return rows
                .Where(row => row.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange)
                .Where(row => GetPatchRegions(row.Spec).Any(region =>
                    region.Original.Length != region.Patched.Length ||
                    region.FileOffset < 0 ||
                    region.FileOffset > data.Length - region.Original.Length ||
                    (!data.AsSpan(region.FileOffset, region.Original.Length).SequenceEqual(region.Original) &&
                     !data.AsSpan(region.FileOffset, region.Patched.Length).SequenceEqual(region.Patched))))
                .ToArray();
        }

        private sealed record PatchTargetValidationInfo(
            string ExePath,
            string BackupPath,
            string BackupHashPath,
            byte[] Data,
            string IdentityLabel);

        private static (bool success, string message, PatchTargetValidationInfo? info) ValidatePatchTarget(
            BinaryPatchTargetOptions target,
            bool requireCatalog,
            IReadOnlyList<BinaryPatchSpec>? selected)
        {
            if (string.IsNullOrWhiteSpace(target.ExePath) || !File.Exists(target.ExePath))
                return (false, "Select a valid BEA.exe first.", null);

            if (!string.Equals(Path.GetFileName(target.ExePath), TargetFileName, StringComparison.OrdinalIgnoreCase))
                return (false, "Patch target must be a BEA.exe-only copy.", null);

            // An installed-game permission carries its own root - the game folder it was granted
            // for - so a caller patching an install does not have to invent a workspace root it
            // does not have.
            if (string.IsNullOrWhiteSpace(target.AllowedRoot) && target.InstalledGame is null)
                return (false, WorkspaceFolderRequired, null);

            string fullExePath;
            string fullRoot;
            try
            {
                fullExePath = Path.GetFullPath(target.ExePath);
                fullRoot = NormalizeDirectoryRoot(
                    string.IsNullOrWhiteSpace(target.AllowedRoot)
                        ? target.InstalledGame!.GameRoot
                        : target.AllowedRoot);
            }
            catch (Exception)
            {
                return (false, WorkingCopyPathUnusable, null);
            }

            // An installed game is a legitimate target only when the caller is holding permission
            // for this exact executable - and permission cannot exist unless a verified original
            // is already sitting beside it. See AuthorizeInstalledGameWrite.
            bool installedGameAuthorized = false;
            if (target.InstalledGame is not null)
            {
                if (!string.Equals(
                        Path.GetFullPath(target.InstalledGame.ExePath),
                        fullExePath,
                        StringComparison.OrdinalIgnoreCase))
                {
                    return (false,
                        "The installed-game permission was granted for a different executable than the one being patched. Nothing was changed.",
                        null);
                }

                if (!File.Exists(target.InstalledGame.BackupPath) ||
                    !File.Exists(target.InstalledGame.BackupHashPath))
                {
                    return (false,
                        "The verified backup that this permission was granted for is no longer beside the game. Nothing was changed.",
                        null);
                }

                installedGameAuthorized = true;
                fullRoot = NormalizeDirectoryRoot(target.InstalledGame.GameRoot);
            }

            if (!installedGameAuthorized)
            {
                if (IsPathUnderProtectedInstallRoot(fullExePath) || IsPathUnderProtectedInstallRoot(fullRoot))
                    return (false, ProtectedInstallFolder, null);

                if (HasKnownSteamInstallShape(fullExePath) || HasKnownSteamInstallShape(fullRoot))
                    return (false, "Patch target is a steamapps/common/Battle Engine Aquila install. Work in a copy, or choose to patch your installed game - which takes a verified backup first.", null);
            }

            if (!IsPathUnderRoot(fullExePath, fullRoot))
                return (false, PatchTargetMustStayInsideWorkspaceFolder, null);

            string backupPath = BuildBackupPath(fullExePath);
            if (!IsPathUnderRoot(backupPath, fullRoot))
                return (false, BackupMustStayInsideWorkspaceFolder, null);

            string backupHashPath = BuildBackupHashPath(fullExePath);
            if (!IsPathUnderRoot(backupHashPath, fullRoot))
                return (false, BackupHashMustStayInsideWorkspaceFolder, null);

            var filesystemSafety = ValidatePatchFilesystemSafety(fullExePath, backupPath, backupHashPath, fullRoot);
            if (!filesystemSafety.success)
                return (false, filesystemSafety.message, null);

            if (File.Exists(backupHashPath) && !File.Exists(backupPath))
                return (false, BackupHashWithoutBackup, null);

            if (requireCatalog && UsingFallbackCatalog && !target.AllowFallbackCatalogForTests)
                return (false, "Patch catalog is unavailable; built-in fallback patch specs are verification-only for product mutation.", null);

            byte[] data = File.ReadAllBytes(fullExePath);
            string identityLabel = requireCatalog
                ? ValidateTargetIdentity(data, selected ?? Array.Empty<BinaryPatchSpec>(), target)
                : BeaExeOnlyCopyIdentity;

            if (identityLabel.Length == 0)
            {
                // Reached whenever the chosen BEA.exe is not a build this
                // catalog has byte evidence for - most often because the
                // installed game has already been modified by something else.
                // The old wording named an internal lane and left the user with
                // nothing to do; the original backup sitting beside a modified
                // executable is the usual answer, so say that.
                // Superseded 2026-08-01: this said the file "has been modified", which conflates
                // two different things. The app knows the byte layout of exactly one build - the
                // Steam release it was measured against. A disc pressing, a localised release or a
                // patched-by-something-else executable all land here identically, and telling the
                // owner of an untouched retail disc that their game has been tampered with is both
                // wrong and aimed at the audience a preservation project can least afford to
                // insult. Say what is actually known: this is not a build with byte evidence behind
                // it.
                return (false,
                    "This BEA.exe is not the build the app has byte evidence for, so it cannot tell where the patches belong and will not guess. " +
                    "That means it has been changed, or it is a different release - a disc version or another language - and the app cannot tell which from the bytes alone. " +
                    "Look next to it for BEA.exe.original.backup and choose that instead, or point the app at a Steam copy. " +
                    "Nothing was changed.",
                    null);
            }

            return (true, string.Empty, new PatchTargetValidationInfo(fullExePath, backupPath, backupHashPath, data, identityLabel));
        }

        /// <summary>
        /// Take responsibility for an installed game's executable, and hand back the permission to
        /// write to it - but only once there is a verified original to put back.
        ///
        /// This is the whole of the "backup first, no opt-out" rule, expressed as a constructor
        /// precondition rather than as a step somebody has to remember. Three states, and only the
        /// first two end with permission:
        ///
        /// 1. A backup is already there with a matching hash sidecar, and the backup is a clean
        ///    retail specimen. Nothing is written; permission is granted.
        /// 2. A backup is already there with no sidecar. If the backup is a clean retail specimen
        ///    the sidecar is written from it and permission is granted. **This is the state a
        ///    hand-patched install is usually in** - somebody kept the original by hand and no tool
        ///    ever recorded its hash.
        /// 3. No backup at all. The executable on disk must itself be a clean retail specimen,
        ///    because that is the only case where a snapshot taken now is genuinely the original. A
        ///    snapshot of an already-modified executable would be named <c>.original.backup</c> and
        ///    be nothing of the sort, and every later restore would put the modification back.
        ///
        /// The refusal in case 3 is the important one. It is not conservatism: manufacturing an
        /// "original" from a file that is not one destroys the only route back.
        /// </summary>
        public static (bool success, string message, InstalledGameWriteAuthorization? authorization)
            AuthorizeInstalledGameWrite(string exePath)
        {
            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                return (false, "Choose the BEA.exe inside your installed game folder.", null);

            string fullExePath;
            string gameRoot;
            try
            {
                fullExePath = Path.GetFullPath(exePath);
                gameRoot = Path.GetDirectoryName(fullExePath) ?? string.Empty;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException)
            {
                return (false, InstalledPathUnreadable, null);
            }

            if (!string.Equals(Path.GetFileName(fullExePath), TargetFileName, StringComparison.OrdinalIgnoreCase))
                return (false, $"Choose {TargetFileName} itself, not another file in the folder.", null);

            if (string.IsNullOrWhiteSpace(gameRoot) || !Directory.Exists(Path.Combine(gameRoot, "data")))
            {
                return (false,
                    "That does not look like an installed Battle Engine Aquila folder - there is no data folder beside the executable.",
                    null);
            }

            string backupPath = BuildBackupPath(fullExePath);
            string backupHashPath = BuildBackupHashPath(fullExePath);

            var filesystemSafety = ValidatePatchFilesystemSafety(fullExePath, backupPath, backupHashPath, gameRoot);
            if (!filesystemSafety.success)
                return (false, filesystemSafety.message, null);

            try
            {
                byte[] currentBytes = File.ReadAllBytes(fullExePath);

                if (File.Exists(backupPath))
                {
                    byte[] backupBytes = File.ReadAllBytes(backupPath);
                    string backupHash = ComputeSha256Hex(backupBytes);

                    if (!IsKnownCleanRetailSpecimen(backupBytes, backupHash))
                    {
                        return (false,
                            $"The {Path.GetFileName(backupPath)} sitting beside your game is not a clean retail BEA.exe, so it is not something the app can promise to put back. " +
                            "Nothing was changed. Move that file aside and reinstall the game if you want a backup this app can stand behind.",
                            null);
                    }

                    bool sidecarWritten = false;
                    if (File.Exists(backupHashPath))
                    {
                        string recorded = File.ReadAllText(backupHashPath).Trim();
                        if (!string.Equals(recorded, backupHash, StringComparison.OrdinalIgnoreCase))
                        {
                            return (false,
                                $"The recorded hash beside {Path.GetFileName(backupPath)} does not match the file it describes. " +
                                "Nothing was changed. Delete the .sha256 file and try again, and the app will write a fresh one.",
                                null);
                        }
                    }
                    else
                    {
                        // The hand-kept-backup case. The bytes are a clean retail specimen, so
                        // recording their hash states something already true rather than
                        // laundering an unknown file into a trusted one.
                        WriteBackupHash(backupHashPath, backupBytes);
                        sidecarWritten = true;
                    }

                    string found = sidecarWritten
                        ? $"Found {Path.GetFileName(backupPath)} beside your game and recognised it as a clean retail BEA.exe, so the app recorded its hash in {Path.GetFileName(backupHashPath)}. That is the file Restore puts back."
                        : $"Your original executable is already backed up as {Path.GetFileName(backupPath)}, and its recorded hash still matches. That is the file Restore puts back.";

                    return (true, found, new InstalledGameWriteAuthorization(
                        fullExePath,
                        gameRoot,
                        backupPath,
                        backupHashPath,
                        backupHash,
                        backupWasCreatedNow: false,
                        hashSidecarWasCreatedNow: sidecarWritten,
                        summary: found));
                }

                string currentHash = ComputeSha256Hex(currentBytes);
                if (!IsKnownCleanRetailSpecimen(currentBytes, currentHash))
                {
                    return (false,
                        "Your BEA.exe has already been changed by something, and there is no BEA.exe.original.backup beside it to go back to. " +
                        "The app will not copy a modified executable and call it the original, because every later restore would put the modification back. " +
                        "Nothing was changed. Reinstall or verify the game files first, and then this will work.",
                        null);
                }

                PublishFileAtomically(backupPath, currentBytes, overwrite: false, "installed-game backup snapshot");
                WriteBackupHash(backupHashPath, currentBytes);

                byte[] writtenBackup = File.ReadAllBytes(backupPath);
                if (!writtenBackup.SequenceEqual(currentBytes))
                {
                    return (false,
                        "The backup was written but did not read back the same, so nothing was patched. Your game is untouched.",
                        null);
                }

                string made =
                    $"Your original executable has been copied to {Path.GetFileName(backupPath)} beside it, and verified byte for byte. That is the file Restore puts back.";

                return (true, made, new InstalledGameWriteAuthorization(
                    fullExePath,
                    gameRoot,
                    backupPath,
                    backupHashPath,
                    currentHash,
                    backupWasCreatedNow: true,
                    hashSidecarWasCreatedNow: true,
                    summary: made));
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return (false, InstalledBackupFailed, null);
            }
        }

        /// <summary>
        /// Whether a file on disk is byte-for-byte the clean retail build. Reads only, writes
        /// nothing, and is safe to call while drawing a page - which is the point: a UI needs to
        /// know what it may offer without taking a backup as a side effect of asking.
        /// </summary>
        public static bool LooksLikeCleanRetailExecutable(string exePath)
        {
            return IdentifyRetailExecutable(exePath) == RetailExecutableIdentity.KnownCleanRetail;
        }

        /// <summary>
        /// Classify a BEA.exe without writing. A locked or otherwise unreadable file is
        /// <see cref="RetailExecutableIdentity.Unreadable"/>, not "already changed".
        /// </summary>
        public static RetailExecutableIdentity IdentifyRetailExecutable(string? exePath)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                    return RetailExecutableIdentity.Missing;

                if (new FileInfo(exePath).Length != KnownRetailSteamSize)
                    return RetailExecutableIdentity.DifferentFromKnownRetail;

                byte[] bytes = File.ReadAllBytes(exePath);
                return IsKnownCleanRetailSpecimen(bytes, ComputeSha256Hex(bytes))
                    ? RetailExecutableIdentity.KnownCleanRetail
                    : RetailExecutableIdentity.DifferentFromKnownRetail;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
            {
                return RetailExecutableIdentity.Unreadable;
            }
        }

        private static bool IsKnownCleanRetailSpecimen(byte[] bytes, string hash)
        {
            return bytes.LongLength == KnownRetailSteamSize &&
                   s_knownRetailSteamHashes.Contains(hash, StringComparer.OrdinalIgnoreCase);
        }

        private static void WriteBackupHash(string backupHashPath, byte[] backupBytes)
        {
            byte[] hashBytes = Encoding.UTF8.GetBytes(ComputeSha256Hex(backupBytes));
            PublishFileAtomically(backupHashPath, hashBytes, overwrite: false, "patch backup hash sidecar");
        }

        private static byte[] PublishFileAtomically(
            string destinationPath,
            byte[] bytes,
            bool overwrite,
            string label)
        {
            string? directory = Path.GetDirectoryName(destinationPath);
            if (string.IsNullOrWhiteSpace(directory) || !Directory.Exists(directory))
                throw new DirectoryNotFoundException("That folder could not be found.");

            string stagedPath = Path.Combine(directory, $".onslaught-patch-{Guid.NewGuid():N}.tmp");
            bool stagedEntryExists = false;
            try
            {
                using (FileStream staged = FileMutationSafety.CreateStagedFile(stagedPath))
                {
                    stagedEntryExists = true;
                    staged.Write(bytes);
                    staged.Flush(flushToDisk: true);
                    staged.Position = 0;
                    byte[] stagedHash = SHA256.HashData(staged);
                    if (staged.Length != bytes.LongLength ||
                        !CryptographicOperations.FixedTimeEquals(stagedHash, SHA256.HashData(bytes)))
                    {
                        throw new IOException(StagedFileVerificationFailed);
                    }

                    FileMutationSafety.ReleaseStagedFileQuarantine(staged);
                }

                File.Move(stagedPath, destinationPath, overwrite);
                stagedEntryExists = false;

                using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(destinationPath, label);
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, label);
                if (OperatingSystem.IsWindows() && identity.IsReparsePoint)
                    throw new IOException(TargetCannotUseLink);
                if (OperatingSystem.IsWindows() && identity.NumberOfLinks != 1)
                    throw new IOException(FileCannotShareData);

                using var stream = new FileStream(handle, FileAccess.Read);
                if (stream.Length > int.MaxValue)
                    throw new IOException(FileMutationSafety.FileTooLargeToRead);
                byte[] readBack = new byte[checked((int)stream.Length)];
                stream.ReadExactly(readBack);
                if (!readBack.SequenceEqual(bytes))
                    throw new IOException(PublishedFileDidNotMatch);

                return readBack;
            }
            finally
            {
                if (stagedEntryExists && File.Exists(stagedPath))
                    File.Delete(stagedPath);
            }
        }

        private static (bool success, string message) ValidateBackupSnapshotIntegrity(string backupHashPath, byte[] backupBytes)
        {
            if (!File.Exists(backupHashPath))
            {
                return (false,
                    "Restore aborted: backup snapshot integrity could not be verified.\n" +
                    "The backup hash sidecar is missing, and the BEA.exe-only copy was not overwritten.");
            }

            string expected = File.ReadAllText(backupHashPath).Trim();
            string actual = ComputeSha256Hex(backupBytes);
            if (!string.Equals(expected, actual, StringComparison.OrdinalIgnoreCase))
            {
                return (false,
                    "Restore aborted: backup snapshot integrity check failed.\n" +
                    "The BEA.exe-only copy was not overwritten.");
            }

            return (true, string.Empty);
        }

        private static (bool success, string message) ValidateBackupSnapshotProvenance(
            byte[] backupBytes,
            IReadOnlyList<BinaryPatchSpec> specs,
            BinaryPatchTargetOptions target)
        {
            string actualHash = ComputeSha256Hex(backupBytes);
            bool trustedHash = s_knownRetailSteamHashes.Contains(actualHash, StringComparer.OrdinalIgnoreCase);
            bool trustedSize = backupBytes.LongLength == KnownRetailSteamSize;

            if (!target.AllowByteLayoutOnlyTarget && (!trustedHash || !trustedSize))
            {
                return (false,
                    "Restore aborted: backup snapshot is not a trusted clean Steam retail BEA.exe specimen.\n" +
                    "The BEA.exe-only copy was not overwritten.");
            }

            var (_, _, rows) = VerifyPatchSpecs(backupBytes, specs);
            if (rows.Any(row => row.State != BinaryPatchState.Original))
            {
                var sb = new StringBuilder();
                sb.AppendLine("Restore aborted: backup snapshot does not match original patch-row bytes.");
                foreach (var row in rows.Where(row => row.State != BinaryPatchState.Original))
                    sb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
                sb.Append("The BEA.exe-only copy was not overwritten.");
                return (false, sb.ToString());
            }

            return (true, string.Empty);
        }

        private static string ComputeSha256Hex(byte[] bytes) =>
            Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

        private static string ValidateTargetIdentity(
            byte[] data,
            IReadOnlyList<BinaryPatchSpec> selected,
            BinaryPatchTargetOptions target)
        {
            string actualHash = Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
            if (s_knownRetailSteamHashes.Contains(actualHash, StringComparer.OrdinalIgnoreCase) &&
                data.LongLength == KnownRetailSteamSize)
                return "known clean Steam retail BEA.exe SHA-256";

            bool sizeMatches = data.LongLength == KnownRetailSteamSize;
            if (sizeMatches && !target.AllowByteLayoutOnlyTarget && selected.Count > 0)
            {
                if (CurrentBytesMatchTrustedCleanBackupWithCatalogTransitions(data, target))
                    return "trusted clean backup plus complete known catalog transitions";
            }

            if (!sizeMatches && !target.AllowByteLayoutOnlyTarget)
                return string.Empty;

            return target.AllowByteLayoutOnlyTarget
                ? "byte-layout-only verified selected patch offsets"
                : string.Empty;
        }

        private static bool CurrentBytesMatchTrustedCleanBackupWithCatalogTransitions(
            byte[] currentBytes,
            BinaryPatchTargetOptions target)
        {
            try
            {
                string backupPath = BuildBackupPath(target.ExePath);
                string backupHashPath = BuildBackupHashPath(target.ExePath);
                if (!File.Exists(backupPath) || !File.Exists(backupHashPath))
                    return false;

                byte[] backupBytes = File.ReadAllBytes(backupPath);
                var integrity = ValidateBackupSnapshotIntegrity(backupHashPath, backupBytes);
                if (!integrity.success)
                    return false;

                var provenance = ValidateBackupSnapshotProvenance(backupBytes, PatchSpecs, target);
                if (!provenance.success || backupBytes.Length != currentBytes.Length)
                    return false;

                return CurrentBytesContainOnlyKnownCatalogTransitions(currentBytes, backupBytes, PatchSpecs);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return false;
            }
        }

        internal static bool CurrentBytesContainOnlyKnownCatalogTransitions(
            byte[] currentBytes,
            byte[] backupBytes,
            IReadOnlyList<BinaryPatchSpec> catalogSpecs)
        {
            if (currentBytes.Length != backupBytes.Length)
                return false;

            var allowedDifferences = new bool[currentBytes.Length];
            foreach (BinaryPatchSpec spec in catalogSpecs)
            {
                foreach (BinaryPatchRegion region in GetPatchRegions(spec))
                {
                    if (region.FileOffset < 0 ||
                        region.Original.Length != region.Patched.Length ||
                        region.FileOffset > currentBytes.Length - region.Original.Length)
                    {
                        return false;
                    }

                    ReadOnlySpan<byte> original = backupBytes.AsSpan(region.FileOffset, region.Original.Length);
                    ReadOnlySpan<byte> current = currentBytes.AsSpan(region.FileOffset, region.Patched.Length);
                    if (!original.SequenceEqual(region.Original) || !current.SequenceEqual(region.Patched))
                        continue;

                    Array.Fill(allowedDifferences, true, region.FileOffset, region.Patched.Length);
                }
            }

            for (int index = 0; index < currentBytes.Length; index++)
            {
                if (currentBytes[index] != backupBytes[index] && !allowedDifferences[index])
                    return false;
            }

            return true;
        }

        private static string NormalizeDirectoryRoot(string root)
        {
            return Path.GetFullPath(root)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
        }

        private static bool IsPathUnderProtectedInstallRoot(string path)
        {
            foreach (string root in ProtectedInstallRoots())
            {
                if (IsPathUnderRoot(path, root))
                    return true;
            }

            return false;
        }

        private static IEnumerable<string> ProtectedInstallRoots()
        {
            foreach (string key in new[] { "ProgramFiles", "ProgramFiles(x86)" })
            {
                string? raw = Environment.GetEnvironmentVariable(key);
                if (string.IsNullOrWhiteSpace(raw))
                    continue;

                string fullRoot;
                try
                {
                    fullRoot = NormalizeDirectoryRoot(raw);
                }
                catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException)
                {
                    continue;
                }

                yield return fullRoot;
            }
        }

        private static bool HasKnownSteamInstallShape(string path)
        {
            string fullPath = Path.GetFullPath(path);
            string[] parts = fullPath.Split(
                new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                StringSplitOptions.RemoveEmptyEntries);

            for (int i = 0; i <= parts.Length - 3; i++)
            {
                if (string.Equals(parts[i], "steamapps", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 1], "common", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 2], "Battle Engine Aquila", StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }

            return false;
        }

        private static bool IsPathUnderRoot(string path, string normalizedRoot)
        {
            string normalizedPath = Path.GetFullPath(path);
            return normalizedPath.StartsWith(normalizedRoot, StringComparison.OrdinalIgnoreCase);
        }

        private static (bool success, string message) ValidatePatchFilesystemSafety(
            string exePath,
            string backupPath,
            string backupHashPath,
            string normalizedRoot)
        {
            try
            {
                string rootPath = NormalizeExistingRootForAttributes(normalizedRoot);
                RejectExistingReparseAncestors(rootPath, "workspace folder");
                RejectExistingReparseAncestors(exePath, "patch target path");
                RejectExistingReparseAncestors(backupPath, "patch backup path");
                RejectReparsePoint(exePath, "patch target");
                RejectMultipleHardLinks(exePath, "Patch target");

                if (File.Exists(backupPath))
                {
                    RejectReparsePoint(backupPath, "patch backup");
                    RejectMultipleHardLinks(backupPath, "Patch backup");
                }

                RejectExistingReparseAncestors(backupHashPath, "patch backup hash path");
                if (File.Exists(backupHashPath))
                {
                    RejectReparsePoint(backupHashPath, "patch backup hash");
                    RejectMultipleHardLinks(backupHashPath, "Patch backup hash");
                }

                return (true, string.Empty);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                if (ex.Message == FileCannotShareData || ex.Message == TargetCannotUseLink)
                    return (false, ex.Message);

                return (false, WorkingCopyPathUnusable);
            }
        }

        private static string NormalizeExistingRootForAttributes(string normalizedRoot)
        {
            string full = Path.GetFullPath(normalizedRoot);
            string? pathRoot = Path.GetPathRoot(full);
            if (!string.IsNullOrWhiteSpace(pathRoot) &&
                string.Equals(
                    full.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    pathRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    StringComparison.OrdinalIgnoreCase))
            {
                return pathRoot;
            }

            return full.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }

        private static void RejectReparsePoint(string path, string label)
        {
            if (!File.Exists(path) && !Directory.Exists(path))
                return;

            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException(TargetCannotUseLink);
        }

        private static void RejectExistingReparseAncestors(string path, string label)
        {
            string fullPath = Path.GetFullPath(path);
            string? current = Directory.Exists(fullPath)
                ? fullPath
                : Path.GetDirectoryName(fullPath);

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (Directory.Exists(current))
                    RejectReparsePoint(current, label);

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                    break;

                current = parent;
            }
        }

        private static void RejectMultipleHardLinks(string path, string label)
        {
            if (!OperatingSystem.IsWindows())
                return;

            uint linkCount = GetWindowsHardLinkCount(path);
            if (linkCount > 1)
                throw new InvalidOperationException(FileCannotShareData);
        }

        private static uint GetWindowsHardLinkCount(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite | FileShare.Delete);

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException(FileMutationSafety.FileCouldNotBeInspected, new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error()));

            return info.NumberOfLinks;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GetFileInformationByHandle(
            SafeFileHandle hFile,
            out ByHandleFileInformation lpFileInformation);

        [StructLayout(LayoutKind.Sequential)]
        private struct ByHandleFileInformation
        {
            public uint FileAttributes;
            public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
            public uint VolumeSerialNumber;
            public uint FileSizeHigh;
            public uint FileSizeLow;
            public uint NumberOfLinks;
            public uint FileIndexHigh;
            public uint FileIndexLow;
        }

        public static string RenderStateReport(string exePath, IReadOnlyList<BinaryPatchVerifyRow> rows, string summary)
        {
            _ = exePath;
            var sb = new StringBuilder();
            sb.AppendLine($"Target: {TargetFileName}");
            sb.AppendLine();

            foreach (var row in rows)
                sb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");

            sb.AppendLine();
            sb.AppendLine(summary);
            return sb.ToString();
        }

        public static string StateLabel(BinaryPatchState state) => state switch
        {
            BinaryPatchState.Original => "ready (original)",
            BinaryPatchState.Patched => "already patched",
            BinaryPatchState.Mismatch => "unexpected bytes",
            BinaryPatchState.OutOfRange => "offset out of range",
            _ => "unknown",
        };
    }
}
