using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed record SafeCopyProfileModule(
        string Id,
        string DisplayName,
        string Category,
        string ProofStatus,
        string ClaimBoundary,
        IReadOnlyList<string> PatchKeys,
        IReadOnlyList<string> LaunchArguments,
        IReadOnlyList<string> CopiedOptionsEdits,
        string RestoreStrategy,
        IReadOnlyList<string> EvidenceRefs,
        IReadOnlyList<string> NonClaims);

    public sealed record SafeCopyProfilePreset(
        string Id,
        string DisplayName,
        string Description,
        IReadOnlyList<string> PatchKeys,
        bool IsSelectable,
        string ProofStatus,
        int? DefaultControllerConfiguration = null,
        bool DefaultPersistControllerConfigInOptions = false,
        bool DefaultSharpenMouseLook = false,
        IReadOnlyList<SafeCopyProfileModule> Modules = null!);

    internal sealed record SafeCopyProfileCatalogLoadResult(
        SafeCopyProfilePreset[] Presets,
        string SchemaVersion,
        string Sha256,
        bool UsingFallback,
        string Status);

    /// <summary>
    /// Shared binary patch selection policy for both WPF and WinUI hosts.
    /// Keeps UI-specific dialogs/status separate from the actual patch-selection rules.
    /// </summary>
    public static class BinaryPatchPlanBuilder
    {
        private const string VersionOverlayPointerKey = "version_overlay_use_patched_format_pointer";
        private const string VersionOverlayCaveStringKey = "version_overlay_patched_format_cave_string";
        private const string FreeCameraKeyboardForwardQCaveKey = "free_camera_keyboard_forward_q_cave";
        private const string FreeCameraKeyboardBackwardQCaveKey = "free_camera_keyboard_backward_q_cave";
        private const string FreeCameraKeyboardStrafeLeftQCaveKey = "free_camera_keyboard_strafe_left_q_cave";
        private const string FreeCameraKeyboardStrafeRightQCaveKey = "free_camera_keyboard_strafe_right_q_cave";
        private const string FreeCameraKeyboardYawLeftQCaveKey = "free_camera_keyboard_yaw_left_q_cave";
        private const string FreeCameraKeyboardYawRightQCaveKey = "free_camera_keyboard_yaw_right_q_cave";
        private const string FreeCameraKeyboardPitchUpQCaveKey = "free_camera_keyboard_pitch_up_q_cave";
        private const string FreeCameraKeyboardPitchDownQCaveKey = "free_camera_keyboard_pitch_down_q_cave";
        private const string ResolutionGateKey = "resolution_gate";
        private const string ForceWindowedKey = "force_windowed";
        private const string SkipAutoToggleKey = "skip_auto_toggle";
        private const string ProfileCatalogRelativePath = "patches/catalog/safe-copy-profiles.v1.json";
        private const string ProfileCatalogSchemaVersion = "safe-copy-profiles.v1";
        public const string CompatibilityProfileId = "compatibility-copy";
        public const string RecommendedProfileId = "recommended-safe-copy";
        public const string EnhancedPreviewProfileId = "enhanced-edition-preview";
        public const string DebugCameraPreviewProfileId = "debug-camera-preview";
        public const string CustomProfileId = "custom";

        private static readonly string[] s_windowedCompatibilityKeys =
        {
            ResolutionGateKey,
            ForceWindowedKey,
        };

        private static readonly string[] s_recommendedSafeCopyKeys =
        {
            ResolutionGateKey,
            ForceWindowedKey,
            "extra_graphics_default_on",
            "ignore_cardid_tweak_overrides",
        };

        private static readonly string[] s_enhancedPreviewKeys =
        {
            ResolutionGateKey,
            ForceWindowedKey,
            "extra_graphics_default_on",
            "ignore_cardid_tweak_overrides",
            VersionOverlayPointerKey,
            "frontend_clear_screen_dark_red",
            "goodies_gallery_display_unlock",
        };

        private static readonly string[] s_debugCameraPreviewKeys =
        {
            ResolutionGateKey,
            ForceWindowedKey,
            "free_camera_aurore_gate_bypass",
            "free_camera_keyboard_forward_q_hook",
        };

        private static readonly SafeCopyProfileModule[] s_compatibilityModules =
        {
            new(
                "windowed-compatibility",
                "Windowed compatibility",
                "Executable patch rows",
                "Byte-verified copied-executable compatibility baseline.",
                "Allows the safe copy to prefer windowed startup and accept non-4:3 display-mode candidates; does not prove aspect-ratio gameplay parity.",
                s_windowedCompatibilityKeys,
                Array.Empty<string>(),
                Array.Empty<string>(),
                "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; the installed Steam executable is never changed.",
                new[]
                {
                    "patches/README.md",
                    "release/readiness/winui_safe_copy_live_runtime_smoke_2026-06-17.md",
                    "reverse-engineering/binary-analysis/windowed-mode-analysis.md",
                    "reverse-engineering/binary-analysis/widescreen-patch-analysis.md",
                },
                new[]
                {
                    "No widescreen field-of-view parity.",
                    "No all-machine windowing guarantee.",
                    "No installed-game mutation.",
                }),
        };

        private static readonly SafeCopyProfileModule[] s_recommendedModules =
            s_compatibilityModules
                .Concat(new[]
                {
                    new SafeCopyProfileModule(
                        "graphics-defaults",
                        "Graphics default rows",
                        "Executable patch rows",
                        "Byte-verified rows with copied-game launch proof; visible graphics parity remains unproven.",
                        "Requests modern/default graphics behavior in the safe copy; does not prove rendering quality or no-noticeable-difference parity.",
                        new[] { "extra_graphics_default_on", "ignore_cardid_tweak_overrides" },
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; cardid.txt/source files are not rewritten.",
                        new[]
                        {
                            "patches/README.md",
                            "release/readiness/winui_modern_graphics_live_runtime_smoke_2026-06-17.md",
                            "reverse-engineering/binary-analysis/extra-graphics-feature-gate-patch.md",
                        },
                        new[]
                        {
                            "No proven visible graphics improvement.",
                            "No rendering correctness or no-noticeable-difference parity.",
                            "No GPU/driver compatibility guarantee.",
                        }),
                })
                .ToArray();

        private static readonly SafeCopyProfileModule[] s_enhancedPreviewModules =
            s_recommendedModules
                .Concat(new[]
                {
                    new SafeCopyProfileModule(
                        "title-marker",
                        "PATCHED title marker",
                        "Executable patch rows",
                        "One copied-game title/menu frame showed the V1.00 - PATCHED marker.",
                        "Marks the safe copy as modded in one proven title/menu path; does not prove every overlay path or gameplay visibility.",
                        new[] { VersionOverlayPointerKey },
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; the cave string is only written inside the copied executable.",
                        new[]
                        {
                            "patches/README.md",
                            "release/readiness/winui_version_overlay_runtime_smoke_2026-06-17.md",
                            "reverse-engineering/binary-analysis/version-overlay-patch.md",
                        },
                        new[]
                        {
                            "No every-overlay-path proof.",
                            "No gameplay overlay visibility proof.",
                            "No long-session marker proof.",
                        }),
                    new SafeCopyProfileModule(
                        "frontend-red-margins",
                        "Red frontend margins",
                        "Executable patch rows",
                        "Copied-game proof covers title-screen red margins plus one navigated Goodies-menu red-family margin run.",
                        "Changes one frontend clear-screen immediate in the safe copy; does not prove every menu state, whole-menu theming, HUD colors, or gameplay colors.",
                        new[] { "frontend_clear_screen_dark_red" },
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; no art, texture, save, or installed-game files are rewritten.",
                        new[]
                        {
                            "patches/README.md",
                            "release/readiness/winui_frontend_clear_screen_color_patch_2026-06-16.md",
                            "reverse-engineering/binary-analysis/frontend-clear-screen-color-patch.md",
                        },
                        new[]
                        {
                            "No whole-menu theme replacement.",
                            "No HUD or gameplay color change.",
                            "No every-frontend-state visual proof.",
                        }),
                    new SafeCopyProfileModule(
                        "goodies-display-preview",
                        "Goodies display preview",
                        "Executable patch rows",
                        "Two Goodies-wall comparisons changed display state, and one Tatiana page was captured.",
                        "Forces the bounded Goodies-wall display-state path in the safe copy; does not edit saves, permanently award Goodies, or prove model/FMV playback.",
                        new[] { "goodies_gallery_display_unlock" },
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; copied and source saves are not modified.",
                        new[]
                        {
                            "patches/README.md",
                            "release/readiness/winui_goodies_gallery_display_unlock_2026-06-17.md",
                            "reverse-engineering/binary-analysis/goodies-gallery-display-unlock-patch.md",
                        },
                        new[]
                        {
                            "No permanent Goodies awards.",
                            "No save-file edit.",
                            "No model-viewer or FMV playback proof.",
                            "No every-entry Goodies coverage.",
                        }),
                    new SafeCopyProfileModule(
                        "copied-options-control-defaults",
                        "Copied control defaults",
                        "Copied defaultoptions.bea edits",
                        "Manifest/read-back proof only; runtime control feel remains unproven.",
                        "Persists controller config 1 and a test mouse-look sensitivity in the copied defaultoptions.bea only; does not prove improved feel, deadzones, look curves, camera behavior, or movement changes.",
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        new[] { "controllerConfiguration=1", "mouseLookSensitivity=2.25" },
                        "Restore the copied defaultoptions.bea backup or recreate the safe copy; the installed defaultoptions.bea is never rewritten.",
                        new[]
                        {
                            "release/readiness/winui_safe_copy_control_options_2026-06-17.md",
                            "roadmap/mod-patch-runtime-rebuild-register.md",
                            "reverse-engineering/save-file/save-format.md",
                        },
                        new[]
                        {
                            "No improved control-feel proof.",
                            "No deadzone or look-curve byte patch.",
                            "No physical gamepad runtime proof.",
                        }),
                })
                .ToArray();

        private static readonly SafeCopyProfileModule[] s_debugCameraPreviewModules =
            s_compatibilityModules
                .Concat(new[]
                {
                    new SafeCopyProfileModule(
                        "debug-camera-q-forward",
                        "Debug camera Q-forward path",
                        "Experimental executable patch rows",
                        "Accepted copied-runtime CDB proofs cover the Aurore gate bypass and one Q-forward free-camera movement path.",
                        "Selects the free-camera debug toggle gate bypass and one Q-forward remap path for the safe copy; does not create a full camera control scheme or prove gameplay safety.",
                        new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_forward_q_hook" },
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        "Restore the copied BEA.exe.original.backup snapshot or recreate the safe copy; the installed Steam executable is never changed.",
                        new[]
                        {
                            "patches/README.md",
                            "release/readiness/winui_safe_copy_free_camera_toggle_2026-06-18.md",
                            "release/readiness/winui_free_camera_q_forward_runtime_2026-06-18.md",
                            "reverse-engineering/binary-analysis/free-camera-aurore-gate-bypass-patch.md",
                        },
                        new[]
                        {
                            "No full free-camera control scheme proof.",
                            "No joystick or analog camera proof.",
                            "No gameplay safety or long-session proof.",
                            "No render parity or rebuild parity proof.",
                        }),
                })
                .ToArray();

        private static readonly SafeCopyProfilePreset[] s_safeCopyProfilePresets =
        {
            new(
                CompatibilityProfileId,
                "Compatibility Copy",
                "Windowed startup and non-4:3 display-mode acceptance only.",
                s_windowedCompatibilityKeys,
                IsSelectable: true,
                "Byte-verified safe-copy compatibility baseline.",
                Modules: s_compatibilityModules),
            new(
                RecommendedProfileId,
                "Windowed + Graphics Defaults",
                "Compatibility Copy plus the graphics-default rows that have copied-game launch proof.",
                s_recommendedSafeCopyKeys,
                IsSelectable: true,
                "Byte-verified rows with copied-game launch proof; visible graphics parity remains unproven.",
                Modules: s_recommendedModules),
            new(
                EnhancedPreviewProfileId,
                "Enhanced Profile Preview",
                "Preview profile that layers the compatibility baseline, graphics defaults, PATCHED title marker, red frontend clear-screen color, and bounded Goodies-wall display override.",
                s_enhancedPreviewKeys,
                IsSelectable: true,
                "Proof-bounded preset over reversible rows with accepted combined safe-copy launch/capture/source-safety proof; not a full overhaul, online mode, control-feel fix, or gameplay parity claim.",
                DefaultControllerConfiguration: 1,
                DefaultPersistControllerConfigInOptions: true,
                DefaultSharpenMouseLook: true,
                Modules: s_enhancedPreviewModules),
            new(
                DebugCameraPreviewProfileId,
                "Debug Camera Preview",
                "Experimental safe-copy profile for the bounded free-camera toggle plus one Q-forward movement path.",
                s_debugCameraPreviewKeys,
                IsSelectable: true,
                "Experimental copied-runtime CDB proofs for the toggle and one Q-forward movement path; not a full free-camera mode, gameplay safety proof, or camera-control overhaul.",
                Modules: s_debugCameraPreviewModules),
            new(
                CustomProfileId,
                "Custom",
                "Manual visible-row selection; safe copies still add the required windowed compatibility pair.",
                Array.Empty<string>(),
                IsSelectable: true,
                "Manual selection surface; each row keeps its own proof boundary.",
                Modules: Array.Empty<SafeCopyProfileModule>()),
        };

        private static readonly HashSet<string> s_frontendClearScreenColorKeys =
            new(
                new[]
                {
                    "frontend_clear_screen_dark_red",
                    "frontend_clear_screen_dark_green",
                    "frontend_clear_screen_black",
                },
                StringComparer.OrdinalIgnoreCase);

        private static readonly HashSet<string> s_hiddenCompanionKeys =
            new(
                new[]
                {
                    VersionOverlayCaveStringKey,
                    FreeCameraKeyboardForwardQCaveKey,
                    FreeCameraKeyboardBackwardQCaveKey,
                    FreeCameraKeyboardStrafeLeftQCaveKey,
                    FreeCameraKeyboardStrafeRightQCaveKey,
                    FreeCameraKeyboardYawLeftQCaveKey,
                    FreeCameraKeyboardYawRightQCaveKey,
                    FreeCameraKeyboardPitchUpQCaveKey,
                    FreeCameraKeyboardPitchDownQCaveKey
                },
                StringComparer.OrdinalIgnoreCase);

        private static readonly SafeCopyProfileCatalogLoadResult s_profileCatalogLoad = LoadSafeCopyProfileCatalog();

        public static IReadOnlyList<BinaryPatchSpec> GetVisibleSpecs()
        {
            return BinaryPatchEngine.PatchSpecs
                .Where(spec => !IsHiddenCompanionSpec(spec))
                .ToArray();
        }

        public static IReadOnlyList<SafeCopyProfilePreset> GetSafeCopyProfilePresets()
        {
            return s_profileCatalogLoad.Presets.ToArray();
        }

        public static SafeCopyProfilePreset GetSafeCopyProfilePreset(string profileId)
        {
            SafeCopyProfilePreset? preset = s_profileCatalogLoad.Presets.FirstOrDefault(preset =>
                string.Equals(preset.Id, profileId, StringComparison.OrdinalIgnoreCase));
            return preset ?? throw new InvalidOperationException($"Unknown safe-copy profile preset: {profileId}");
        }

        public static string SafeCopyProfileCatalogVersion => s_profileCatalogLoad.SchemaVersion;

        public static string SafeCopyProfileCatalogSha256 => s_profileCatalogLoad.Sha256;

        public static bool UsingFallbackSafeCopyProfileCatalog => s_profileCatalogLoad.UsingFallback;

        public static string SafeCopyProfileCatalogStatus => s_profileCatalogLoad.Status;

        public static IReadOnlyList<string> BuildSafeCopyProfilePatchKeys(string profileId)
        {
            SafeCopyProfilePreset preset = GetSafeCopyProfilePreset(profileId);
            if (!preset.IsSelectable)
            {
                throw new InvalidOperationException($"{preset.DisplayName} cannot produce patch keys yet.");
            }

            return preset.PatchKeys.ToArray();
        }

        public static IReadOnlyList<BinaryPatchSpec> BuildSelectedSpecs(IEnumerable<string> visibleSelectedKeys)
        {
            var keySet = new HashSet<string>(visibleSelectedKeys ?? Array.Empty<string>(), StringComparer.OrdinalIgnoreCase);
            var selected = BinaryPatchEngine.PatchSpecs
                .Where(spec => keySet.Contains(spec.Key))
                .ToList();

            AddDependencySpecs(selected);

            return selected;
        }

        public static string? ValidateVisibleSelection(IEnumerable<string> visibleSelectedKeys)
        {
            var visibleKeySet = new HashSet<string>(visibleSelectedKeys ?? Array.Empty<string>(), StringComparer.OrdinalIgnoreCase);
            BinaryPatchSpec[] visibleSpecs = GetVisibleSpecs().ToArray();
            string? unknownKey = visibleKeySet.FirstOrDefault(key =>
                !string.IsNullOrWhiteSpace(key) &&
                !visibleSpecs.Any(spec => string.Equals(spec.Key, key, StringComparison.OrdinalIgnoreCase)));
            if (!string.IsNullOrWhiteSpace(unknownKey))
            {
                return $"Unknown or hidden patch row is not selectable: {unknownKey}.";
            }

            var selected = visibleSpecs
                .Where(spec => visibleKeySet.Contains(spec.Key))
                .ToList();

            if (selected.Count == 0)
            {
                return "Select at least one patch first.";
            }

            bool hasExperimental = selected.Any(x => string.Equals(x.Track, "Experimental", StringComparison.OrdinalIgnoreCase));
            bool hasWindowedPair = selected.Any(x => string.Equals(x.Key, ResolutionGateKey, StringComparison.OrdinalIgnoreCase)) &&
                selected.Any(x => string.Equals(x.Key, ForceWindowedKey, StringComparison.OrdinalIgnoreCase));
            bool hasSkipAutoToggle = selected.Any(x => string.Equals(x.Key, SkipAutoToggleKey, StringComparison.OrdinalIgnoreCase));
            string[] selectedFrontendColorKeys = selected
                .Select(x => x.Key)
                .Where(key => s_frontendClearScreenColorKeys.Contains(key))
                .ToArray();
            var exclusiveGroupConflict = selected
                .Where(spec => !string.IsNullOrWhiteSpace(spec.ExclusiveGroup))
                .GroupBy(spec => spec.ExclusiveGroup!, StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault(group => group.Count() > 1);
            if (selectedFrontendColorKeys.Length > 1)
            {
                return "Choose only one frontend clear-screen color preset at a time.";
            }

            if (exclusiveGroupConflict is not null)
            {
                return $"Choose only one {FormatExclusiveGroupLabel(exclusiveGroupConflict.Key)} preset at a time.";
            }

            if ((hasSkipAutoToggle || selected.Any(spec => spec.RequiresWindowedPair)) && !hasWindowedPair)
            {
                return "Rows that require the baseline windowed compatibility pair must be layered on top of Allow non-4:3 mode candidates and Prefer windowed launch.";
            }

            if (hasExperimental && !hasWindowedPair)
            {
                return "Experimental patch rows require the baseline windowed compatibility pair in this workflow.";
            }

            var resolvedSelectionPolicy = BinaryPatchEngine.ValidatePatchSelectionPolicy(BuildSelectedSpecs(visibleKeySet));
            if (!resolvedSelectionPolicy.success)
            {
                return resolvedSelectionPolicy.message;
            }

            return null;
        }

        public static string? BuildSelectionSignature(string? exePath, IEnumerable<string> visibleSelectedKeys)
        {
            if (string.IsNullOrWhiteSpace(exePath))
            {
                return null;
            }

            string[] keys = (visibleSelectedKeys ?? Array.Empty<string>())
                .Where(key => !string.IsNullOrWhiteSpace(key))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();

            if (keys.Length == 0)
            {
                return null;
            }

            return exePath.Trim() + "|" + string.Join(",", keys);
        }

        private static void AddDependencySpecs(List<BinaryPatchSpec> selected)
        {
            var specsByKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            var selectedKeys = selected
                .Select(spec => spec.Key)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);

            for (int index = 0; index < selected.Count; index++)
            {
                foreach (string dependencyKey in selected[index].Dependencies ?? Array.Empty<string>())
                {
                    if (!specsByKey.TryGetValue(dependencyKey, out BinaryPatchSpec? dependency) ||
                        !selectedKeys.Add(dependency.Key))
                    {
                        continue;
                    }

                    selected.Add(dependency);
                }
            }

            if (selectedKeys.Contains(VersionOverlayPointerKey) &&
                !selectedKeys.Contains(VersionOverlayCaveStringKey) &&
                specsByKey.TryGetValue(VersionOverlayCaveStringKey, out BinaryPatchSpec? legacyVersionOverlayCompanion))
            {
                selected.Add(legacyVersionOverlayCompanion);
            }
        }

        private static bool IsHiddenCompanionSpec(BinaryPatchSpec spec)
        {
            return s_hiddenCompanionKeys.Contains(spec.Key) ||
                string.Equals(spec.Selectability, "hidden_companion", StringComparison.OrdinalIgnoreCase);
        }

        private static SafeCopyProfileCatalogLoadResult LoadSafeCopyProfileCatalog()
        {
            string? catalogPath = ResolveProfileCatalogPath();
            if (catalogPath is null)
            {
                return FallbackProfileCatalog("Profile catalog unavailable; using built-in safe-copy profile presets.");
            }

            try
            {
                byte[] catalogBytes = File.ReadAllBytes(catalogPath);
                string catalogHash = ComputeSha256Hex(catalogBytes);
                using var doc = JsonDocument.Parse(catalogBytes);
                if (!TryGetString(doc.RootElement, "schema_version", out string schemaVersion) ||
                    !string.Equals(schemaVersion, ProfileCatalogSchemaVersion, StringComparison.Ordinal) ||
                    !doc.RootElement.TryGetProperty("profiles", out JsonElement profilesEl) ||
                    profilesEl.ValueKind != JsonValueKind.Array)
                {
                    return FallbackProfileCatalog("Profile catalog payload is invalid; using built-in safe-copy profile presets.");
                }

                var loaded = new List<SafeCopyProfilePreset>();
                var invalidRows = new List<string>();
                var seenIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                int rowNumber = 0;
                foreach (JsonElement profileEl in profilesEl.EnumerateArray())
                {
                    rowNumber++;
                    if (!TryParseSafeCopyProfilePreset(profileEl, out SafeCopyProfilePreset? preset) || preset is null)
                    {
                        invalidRows.Add($"profile row {rowNumber}");
                        continue;
                    }

                    if (!seenIds.Add(preset.Id))
                    {
                        invalidRows.Add($"duplicate profile id '{preset.Id}'");
                        continue;
                    }

                    if (!ValidateProfilePatchPolicy(preset, out string profileError))
                    {
                        invalidRows.Add($"{preset.Id}: {profileError}");
                        continue;
                    }

                    loaded.Add(preset);
                }

                if (invalidRows.Count > 0 || loaded.Count == 0)
                {
                    string details = invalidRows.Count == 0 ? "no profiles" : string.Join(", ", invalidRows);
                    return FallbackProfileCatalog($"Profile catalog contained invalid profile rows ({details}); using built-in safe-copy profile presets.");
                }

                if (!ProfileCatalogMatchesFallbackShape(loaded, out string mismatch))
                {
                    return FallbackProfileCatalog($"Profile catalog shape drift detected for {mismatch}; using built-in safe-copy profile presets.");
                }

                return new SafeCopyProfileCatalogLoadResult(
                    loaded.ToArray(),
                    schemaVersion,
                    catalogHash,
                    UsingFallback: false,
                    Status: $"Loaded safe-copy profile catalog from {catalogPath}");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException or InvalidOperationException)
            {
                return FallbackProfileCatalog($"Profile catalog read failed ({ex.Message}); using built-in safe-copy profile presets.");
            }
        }

        private static SafeCopyProfileCatalogLoadResult FallbackProfileCatalog(string status)
        {
            return new SafeCopyProfileCatalogLoadResult(
                s_safeCopyProfilePresets,
                "built-in-fallback",
                string.Empty,
                UsingFallback: true,
                Status: status);
        }

        private static string? ResolveProfileCatalogPath()
        {
            var candidates = new List<string>
            {
                Path.Combine(AppContext.BaseDirectory, ProfileCatalogRelativePath),
                Path.Combine(Environment.CurrentDirectory, ProfileCatalogRelativePath),
            };

            AddAncestorProfileCatalogCandidates(candidates, AppContext.BaseDirectory);
            AddAncestorProfileCatalogCandidates(candidates, Environment.CurrentDirectory);

            foreach (string candidate in candidates.Distinct(StringComparer.OrdinalIgnoreCase))
            {
                if (File.Exists(candidate))
                    return candidate;
            }

            return null;
        }

        private static void AddAncestorProfileCatalogCandidates(List<string> candidates, string startDirectory)
        {
            DirectoryInfo? current = new(Path.GetFullPath(startDirectory));
            if (File.Exists(current.FullName))
                current = current.Parent;

            while (current is not null)
            {
                candidates.Add(Path.Combine(current.FullName, ProfileCatalogRelativePath));
                current = current.Parent;
            }
        }

        private static bool TryParseSafeCopyProfilePreset(JsonElement profileEl, out SafeCopyProfilePreset? preset)
        {
            preset = null;
            if (!TryGetString(profileEl, "id", out string id) ||
                !TryGetString(profileEl, "display_name", out string displayName) ||
                !TryGetString(profileEl, "description", out string description) ||
                !TryGetString(profileEl, "proof_status", out string proofStatus) ||
                !TryGetBoolean(profileEl, "is_selectable", out bool isSelectable))
            {
                return false;
            }

            IReadOnlyList<string> patchKeys = ParseStringArray(profileEl, "patch_keys");
            int? defaultControllerConfiguration = TryGetNullableInt32(profileEl, "default_controller_configuration");
            bool defaultPersistControllerConfig = TryGetOptionalBoolean(profileEl, "default_persist_controller_config_in_options");
            bool defaultSharpenMouseLook = TryGetOptionalBoolean(profileEl, "default_sharpen_mouse_look");
            IReadOnlyList<SafeCopyProfileModule> modules = ParseModules(profileEl);
            if (!string.Equals(id, CustomProfileId, StringComparison.OrdinalIgnoreCase) && modules.Count == 0)
                return false;

            preset = new SafeCopyProfilePreset(
                id,
                displayName,
                description,
                patchKeys,
                isSelectable,
                proofStatus,
                defaultControllerConfiguration,
                defaultPersistControllerConfig,
                defaultSharpenMouseLook,
                modules);
            return true;
        }

        private static IReadOnlyList<SafeCopyProfileModule> ParseModules(JsonElement profileEl)
        {
            if (!profileEl.TryGetProperty("modules", out JsonElement modulesEl) ||
                modulesEl.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<SafeCopyProfileModule>();
            }

            var modules = new List<SafeCopyProfileModule>();
            foreach (JsonElement moduleEl in modulesEl.EnumerateArray())
            {
                if (!TryParseSafeCopyProfileModule(moduleEl, out SafeCopyProfileModule? module) || module is null)
                {
                    return Array.Empty<SafeCopyProfileModule>();
                }

                modules.Add(module);
            }

            return modules.ToArray();
        }

        private static bool TryParseSafeCopyProfileModule(JsonElement moduleEl, out SafeCopyProfileModule? module)
        {
            module = null;
            if (!TryGetString(moduleEl, "id", out string id) ||
                !TryGetString(moduleEl, "display_name", out string displayName) ||
                !TryGetString(moduleEl, "category", out string category) ||
                !TryGetString(moduleEl, "proof_status", out string proofStatus) ||
                !TryGetString(moduleEl, "claim_boundary", out string claimBoundary) ||
                !TryGetString(moduleEl, "restore_strategy", out string restoreStrategy))
            {
                return false;
            }

            IReadOnlyList<string> patchKeys = ParseStringArray(moduleEl, "patch_keys");
            IReadOnlyList<string> launchArguments = ParseStringArray(moduleEl, "launch_arguments");
            IReadOnlyList<string> copiedOptionsEdits = ParseStringArray(moduleEl, "copied_options_edits");
            IReadOnlyList<string> evidenceRefs = ParseStringArray(moduleEl, "evidence_refs");
            IReadOnlyList<string> nonClaims = ParseStringArray(moduleEl, "non_claims");
            if (evidenceRefs.Count == 0 || nonClaims.Count == 0)
                return false;

            module = new SafeCopyProfileModule(
                id,
                displayName,
                category,
                proofStatus,
                claimBoundary,
                patchKeys,
                launchArguments,
                copiedOptionsEdits,
                restoreStrategy,
                evidenceRefs,
                nonClaims);
            return true;
        }

        private static bool ValidateProfilePatchPolicy(SafeCopyProfilePreset preset, out string error)
        {
            error = string.Empty;
            var specsByKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            foreach (string key in preset.PatchKeys)
            {
                if (!specsByKey.TryGetValue(key, out BinaryPatchSpec? spec))
                {
                    error = $"unknown patch key {key}";
                    return false;
                }

                if (IsHiddenCompanionSpec(spec))
                {
                    error = $"hidden companion patch key {key} cannot be a direct profile key";
                    return false;
                }

                if (!(spec.PresetEligibility ?? Array.Empty<string>()).Contains(preset.Id, StringComparer.OrdinalIgnoreCase))
                {
                    error = $"patch key {key} does not allow profile {preset.Id}";
                    return false;
                }
            }

            var profileKeySet = preset.PatchKeys.ToHashSet(StringComparer.OrdinalIgnoreCase);
            foreach (SafeCopyProfileModule module in preset.Modules)
            {
                if (string.IsNullOrWhiteSpace(module.RestoreStrategy) ||
                    module.EvidenceRefs.Count == 0 ||
                    module.NonClaims.Count == 0)
                {
                    error = $"module {module.Id} is missing restore/evidence/non-claim metadata";
                    return false;
                }

                foreach (string key in module.PatchKeys)
                {
                    if (!profileKeySet.Contains(key))
                    {
                        error = $"module {module.Id} references patch key {key} outside profile patch set";
                        return false;
                    }

                    if (!specsByKey.TryGetValue(key, out BinaryPatchSpec? spec) || IsHiddenCompanionSpec(spec))
                    {
                        error = $"module {module.Id} references unknown or hidden patch key {key}";
                        return false;
                    }
                }
            }

            return true;
        }

        private static bool ProfileCatalogMatchesFallbackShape(IReadOnlyList<SafeCopyProfilePreset> loaded, out string mismatch)
        {
            var fallbackById = s_safeCopyProfilePresets.ToDictionary(preset => preset.Id, StringComparer.OrdinalIgnoreCase);
            var loadedById = loaded.ToDictionary(preset => preset.Id, StringComparer.OrdinalIgnoreCase);
            if (!fallbackById.Keys.ToHashSet(StringComparer.OrdinalIgnoreCase).SetEquals(loadedById.Keys))
            {
                mismatch = "profile id set";
                return false;
            }

            foreach (SafeCopyProfilePreset expected in s_safeCopyProfilePresets)
            {
                SafeCopyProfilePreset actual = loadedById[expected.Id];
                if (!string.Equals(actual.DisplayName, expected.DisplayName, StringComparison.Ordinal) ||
                    !string.Equals(actual.Description, expected.Description, StringComparison.Ordinal) ||
                    actual.IsSelectable != expected.IsSelectable ||
                    !string.Equals(actual.ProofStatus, expected.ProofStatus, StringComparison.Ordinal) ||
                    actual.DefaultControllerConfiguration != expected.DefaultControllerConfiguration ||
                    actual.DefaultPersistControllerConfigInOptions != expected.DefaultPersistControllerConfigInOptions ||
                    actual.DefaultSharpenMouseLook != expected.DefaultSharpenMouseLook ||
                    !StringSequenceEquals(actual.PatchKeys, expected.PatchKeys) ||
                    !StringSequenceEquals(actual.Modules.Select(module => module.Id).ToArray(), expected.Modules.Select(module => module.Id).ToArray()))
                {
                    mismatch = actual.Id;
                    return false;
                }
            }

            mismatch = string.Empty;
            return true;
        }

        private static bool StringSequenceEquals(IReadOnlyList<string> left, IReadOnlyList<string> right)
        {
            return left.SequenceEqual(right, StringComparer.OrdinalIgnoreCase);
        }

        private static IReadOnlyList<string> ParseStringArray(JsonElement parent, string propertyName)
        {
            if (!parent.TryGetProperty(propertyName, out JsonElement arrayEl) ||
                arrayEl.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<string>();
            }

            var values = new List<string>();
            foreach (JsonElement itemEl in arrayEl.EnumerateArray())
            {
                if (itemEl.ValueKind != JsonValueKind.String)
                    continue;

                string? value = itemEl.GetString();
                if (!string.IsNullOrWhiteSpace(value))
                    values.Add(value.Trim());
            }

            return values.ToArray();
        }

        private static bool TryGetString(JsonElement parent, string propertyName, out string value)
        {
            value = string.Empty;
            if (!parent.TryGetProperty(propertyName, out JsonElement el) ||
                el.ValueKind != JsonValueKind.String)
            {
                return false;
            }

            string? raw = el.GetString();
            if (string.IsNullOrWhiteSpace(raw))
                return false;

            value = raw.Trim();
            return true;
        }

        private static bool TryGetBoolean(JsonElement parent, string propertyName, out bool value)
        {
            value = false;
            if (!parent.TryGetProperty(propertyName, out JsonElement el))
                return false;

            if (el.ValueKind == JsonValueKind.True)
            {
                value = true;
                return true;
            }

            if (el.ValueKind == JsonValueKind.False)
                return true;

            return false;
        }

        private static bool TryGetOptionalBoolean(JsonElement parent, string propertyName)
        {
            return parent.TryGetProperty(propertyName, out JsonElement el) &&
                el.ValueKind == JsonValueKind.True;
        }

        private static int? TryGetNullableInt32(JsonElement parent, string propertyName)
        {
            if (!parent.TryGetProperty(propertyName, out JsonElement el) ||
                el.ValueKind == JsonValueKind.Null)
            {
                return null;
            }

            return el.TryGetInt32(out int value) ? value : null;
        }

        private static string ComputeSha256Hex(byte[] bytes)
        {
            return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        }

        private static string FormatExclusiveGroupLabel(string exclusiveGroup)
        {
            return string.Equals(exclusiveGroup, "frontend_clear_screen_color", StringComparison.OrdinalIgnoreCase)
                ? "frontend clear-screen color"
                : exclusiveGroup.Replace('_', ' ');
        }
    }
}
