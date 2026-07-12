using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace Onslaught___Career_Editor
{
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
        bool RequiresWindowedPair = false);

    public enum BinaryPatchState
    {
        Original,
        Patched,
        Mismatch,
        OutOfRange,
    }

    public sealed record BinaryPatchVerifyRow(BinaryPatchSpec Spec, BinaryPatchState State);

    public sealed record BinaryPatchTargetOptions(
        string ExePath,
        string AllowedRoot,
        bool AllowFallbackCatalogForTests = false,
        bool AllowByteLayoutOnlyTarget = false);

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
        private const string BackupHashSuffix = ".sha256";
        private const string CatalogRelativePath = "patches/catalog/patches.v2.json";
        private const string ExpectedPatchCatalogSha256 = "283fe89355f3ffa017e1812709cd59c95d67fa991886f72636d1fd0001d624c8";
        private const string TargetFileName = "BEA.exe";
        private const string KnownRetailSteamSha256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
        private const long KnownRetailSteamSize = 2_506_752;
        private static readonly string[] s_knownRetailSteamHashes = { KnownRetailSteamSha256 };

        private static readonly BinaryPatchSpec[] s_fallbackPatchSpecs =
        {
            new(
                Key: "resolution_gate",
                Track: "Stable",
                DisplayName: "Let non-4:3 display modes pass enumeration",
                FileOffset: 0x129696,
                Original: new byte[] { 0xCC },
                Patched: new byte[] { 0x00 },
                TargetBinaryHashes: s_knownRetailSteamHashes,
                TargetBinarySize: KnownRetailSteamSize,
                ProofLevel: "byte_verified_static_and_copied_launch_pair",
                Selectability: "profile_visible",
                PresetEligibility: new[] { "compatibility-copy", "recommended-safe-copy", "enhanced-edition-preview", "debug-camera-preview", "custom" }),
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
                    Status: $"Loaded patch catalog from {catalogPath}");
            }
            catch (Exception ex)
            {
                return new BinaryPatchCatalogLoadResult(
                    s_fallbackPatchSpecs,
                    UsingFallback: true,
                    Status: $"Catalog read failed ({ex.Message}); using built-in fallback patch specs.");
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
                StringSetEquals(actual.TargetBinaryHashes, expected.TargetBinaryHashes) &&
                StringSetEquals(actual.Dependencies, expected.Dependencies) &&
                StringSetEquals(actual.Conflicts, expected.Conflicts) &&
                string.Equals(actual.ExclusiveGroup ?? string.Empty, expected.ExclusiveGroup ?? string.Empty, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(actual.ProofLevel ?? string.Empty, expected.ProofLevel ?? string.Empty, StringComparison.Ordinal) &&
                string.Equals(actual.Selectability ?? string.Empty, expected.Selectability ?? string.Empty, StringComparison.OrdinalIgnoreCase) &&
                StringSetEquals(actual.PresetEligibility, expected.PresetEligibility) &&
                actual.RequiresWindowedPair == expected.RequiresWindowedPair;
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
                RequiresWindowedPair: requiresWindowedPair);
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
            int length = spec.Original.Length;
            if (length != spec.Patched.Length)
                return BinaryPatchState.Mismatch;
            if (spec.FileOffset < 0 || spec.FileOffset + length > data.Length)
                return BinaryPatchState.OutOfRange;

            ReadOnlySpan<byte> current = data.AsSpan(spec.FileOffset, length);
            if (current.SequenceEqual(spec.Patched))
                return BinaryPatchState.Patched;
            if (current.SequenceEqual(spec.Original))
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
                        "Apply aborted: the verified full-file backup could not be created, and the BEA.exe-only copy was not modified.\n" +
                        ex.Message);
                }
            }

            foreach (var row in rows)
            {
                if (row.State == BinaryPatchState.Original)
                {
                    row.Spec.Patched.CopyTo(data, row.Spec.FileOffset);
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
                    "Patch apply failed before atomic publication completed. The verified full-file backup remains available.\n" +
                    ex.Message);
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
            outSb.AppendLine($"Target: {exePath}");
            outSb.AppendLine($"Backup: {backupPath}");
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
                if (spec.Original.SequenceEqual(spec.Patched))
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
                .Select(spec => new
                {
                    Spec = spec,
                    Start = spec.FileOffset,
                    End = spec.FileOffset + spec.Patched.Length,
                })
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
                        selectedRanges[i].Spec.Original.SequenceEqual(selectedRanges[j].Spec.Original) &&
                        selectedRanges[i].Spec.Patched.SequenceEqual(selectedRanges[j].Spec.Patched);
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
                return (false, $"Backup file not found: {backupPath}");

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
                    $"Target: {exePath}\n" +
                    $"Backup source: {backupPath}");
            }

            byte[] restoredBytes;
            try
            {
                restoredBytes = PublishFileAtomically(exePath, backupBytes, overwrite: true, "restored BEA.exe-only copy");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return (false,
                    "Restore failed before atomic publication completed. The verified backup snapshot was left unchanged.\n" +
                    ex.Message);
            }
            if (!restoredBytes.SequenceEqual(backupBytes))
            {
                return (false,
                    "Restore failed: on-disk verification did not match the backup snapshot.\n" +
                    $"Target: {exePath}\n" +
                    $"Backup source: {backupPath}");
            }

            return (true,
                "Restore complete.\n" +
                $"Target: {exePath}\n" +
                $"Backup source: {backupPath}\n" +
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
            var unexpected = new List<BinaryPatchVerifyRow>();
            foreach (var group in specs.GroupBy(spec => (spec.FileOffset, Length: spec.Original.Length)))
            {
                BinaryPatchSpec[] groupSpecs = group.ToArray();
                BinaryPatchVerifyRow[] groupRows = rows
                    .Where(row => groupSpecs.Contains(row.Spec))
                    .ToArray();

                if (groupSpecs.Any(spec => spec.Original.Length != spec.Patched.Length) ||
                    group.Key.FileOffset < 0 ||
                    group.Key.FileOffset + group.Key.Length > data.Length)
                {
                    unexpected.AddRange(groupRows.Where(row => row.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange));
                    continue;
                }

                ReadOnlySpan<byte> current = data.AsSpan(group.Key.FileOffset, group.Key.Length);
                bool matchesKnownOriginalOrPatch = false;
                foreach (BinaryPatchSpec spec in groupSpecs)
                {
                    if (current.SequenceEqual(spec.Original) ||
                        current.SequenceEqual(spec.Patched))
                    {
                        matchesKnownOriginalOrPatch = true;
                        break;
                    }
                }

                if (!matchesKnownOriginalOrPatch)
                {
                    unexpected.AddRange(groupRows.Where(row => row.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange));
                }
            }

            return unexpected;
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
                return (false, "Select a valid BEA.exe path first.", null);

            if (!string.Equals(Path.GetFileName(target.ExePath), TargetFileName, StringComparison.OrdinalIgnoreCase))
                return (false, "Patch target must be a BEA.exe-only copy.", null);

            if (string.IsNullOrWhiteSpace(target.AllowedRoot))
                return (false, "Patch target requires an app-owned workspace root.", null);

            string fullExePath;
            string fullRoot;
            try
            {
                fullExePath = Path.GetFullPath(target.ExePath);
                fullRoot = NormalizeDirectoryRoot(target.AllowedRoot);
            }
            catch (Exception ex)
            {
                return (false, $"Patch target path could not be normalized: {ex.Message}", null);
            }

            if (IsPathUnderProtectedInstallRoot(fullExePath) || IsPathUnderProtectedInstallRoot(fullRoot))
                return (false, "Patch target refuses Program Files or another protected install root; create an app-owned copied game folder first.", null);

            if (HasKnownSteamInstallShape(fullExePath) || HasKnownSteamInstallShape(fullRoot))
                return (false, "Patch target refuses a steamapps/common/Battle Engine Aquila install root; create an app-owned copied game folder first.", null);

            if (!IsPathUnderRoot(fullExePath, fullRoot))
                return (false, "Patch target must be inside the app-owned Patch Bench workspace.", null);

            string backupPath = BuildBackupPath(fullExePath);
            if (!IsPathUnderRoot(backupPath, fullRoot))
                return (false, "Patch backup path must stay inside the app-owned Patch Bench workspace.", null);

            string backupHashPath = BuildBackupHashPath(fullExePath);
            if (!IsPathUnderRoot(backupHashPath, fullRoot))
                return (false, "Patch backup hash path must stay inside the app-owned Patch Bench workspace.", null);

            var filesystemSafety = ValidatePatchFilesystemSafety(fullExePath, backupPath, backupHashPath, fullRoot);
            if (!filesystemSafety.success)
                return (false, filesystemSafety.message, null);

            if (File.Exists(backupHashPath) && !File.Exists(backupPath))
                return (false, "Patch backup hash sidecar exists without its backup snapshot; remove the stale copied-workspace sidecar before applying patches.", null);

            if (requireCatalog && UsingFallbackCatalog && !target.AllowFallbackCatalogForTests)
                return (false, "Patch catalog is unavailable; built-in fallback patch specs are verification-only for product mutation.", null);

            byte[] data = File.ReadAllBytes(fullExePath);
            string identityLabel = requireCatalog
                ? ValidateTargetIdentity(data, selected ?? Array.Empty<BinaryPatchSpec>(), target)
                : "app-owned Patch Bench BEA.exe-only copy";

            if (identityLabel.Length == 0)
            {
                return (false,
                    "Patch target identity is not a known clean Steam retail BEA.exe. Re-select a clean source or use a byte-layout-only test/proof lane explicitly.",
                    null);
            }

            return (true, string.Empty, new PatchTargetValidationInfo(fullExePath, backupPath, backupHashPath, data, identityLabel));
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
                throw new DirectoryNotFoundException($"The containing folder for {label} does not exist.");

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
                        throw new IOException($"Staged {label} verification failed.");
                    }

                    FileMutationSafety.ReleaseStagedFileQuarantine(staged);
                }

                File.Move(stagedPath, destinationPath, overwrite);
                stagedEntryExists = false;

                using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(destinationPath, label);
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, label);
                if (OperatingSystem.IsWindows() && (identity.IsReparsePoint || identity.NumberOfLinks != 1))
                    throw new IOException($"Published {label} has an unsafe file identity.");

                using var stream = new FileStream(handle, FileAccess.Read);
                if (stream.Length > int.MaxValue)
                    throw new IOException($"Published {label} is too large to verify.");
                byte[] readBack = new byte[checked((int)stream.Length)];
                stream.ReadExactly(readBack);
                if (!readBack.SequenceEqual(bytes))
                    throw new IOException($"Published {label} verification did not match the staged bytes.");

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
                if (spec.FileOffset < 0 ||
                    spec.Original.Length != spec.Patched.Length ||
                    spec.FileOffset > currentBytes.Length - spec.Original.Length)
                {
                    return false;
                }

                ReadOnlySpan<byte> original = backupBytes.AsSpan(spec.FileOffset, spec.Original.Length);
                ReadOnlySpan<byte> current = currentBytes.AsSpan(spec.FileOffset, spec.Patched.Length);
                if (!original.SequenceEqual(spec.Original) || !current.SequenceEqual(spec.Patched))
                    continue;

                Array.Fill(allowedDifferences, true, spec.FileOffset, spec.Patched.Length);
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
                RejectExistingReparseAncestors(rootPath, "app-owned Patch Bench workspace root");
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
                return (false, ex.Message);
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
                throw new InvalidOperationException($"Patch Bench refuses reparse points in {label}.");
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
                throw new InvalidOperationException($"{label} is hardlinked to another file; refusing to patch a shared file identity.");
        }

        private static uint GetWindowsHardLinkCount(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite | FileShare.Delete);

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException($"Could not inspect hardlink count for patch target. Win32 error: {Marshal.GetLastWin32Error()}");

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
            var sb = new StringBuilder();
            sb.AppendLine($"Target: {exePath}");
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
