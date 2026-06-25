using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text;
using Microsoft.UI.Xaml.Media;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Models
{
    public sealed class BinaryPatchItemModel : INotifyPropertyChanged
    {
        private bool _isSelected;

        public BinaryPatchItemModel(BinaryPatchSpec spec)
        {
            Spec = spec;
            Summary = spec.Key switch
            {
                "resolution_gate" => "Lets the safe game copy accept non-4:3 display modes. This works with Prefer windowed startup.",
                "force_windowed" => "Makes the safe game copy prefer windowed startup. This is the normal compatibility fix.",
                "extra_graphics_default_on" => "Sets the safe copy's extra-graphics default flag when old hardware rules would leave it off.",
                "ignore_cardid_tweak_overrides" => "Keeps the safe copy from applying old GPU-specific cardid.txt override rules.",
                "version_overlay_use_patched_format_pointer" => "Shows a small PATCHED marker on the title/menu version text so you can tell the safe copy is modded.",
                "frontend_clear_screen_dark_red" => "Changes the menu background color to dark red in the safe copy; details list what has been checked so far.",
                "frontend_clear_screen_dark_green" => "Changes the menu background color to dark green in the safe copy; details list what has been checked so far.",
                "frontend_clear_screen_black" => "Changes the menu background color to black in the safe copy; details list what has been checked so far.",
                "goodies_gallery_display_unlock" => "Changes Goodies-wall display state for bounded checked entries in the safe copy without editing your saves or awarding them.",
                "skip_auto_toggle" => "Experimental startup branch fallback for setups that still fight windowed mode after the normal compatibility fixes.",
                "pause_o_scan_initializer_experiment" => "Experimental copied-executable patch that tests whether the O key can drive pause in a copied runtime.",
                "free_camera_aurore_gate_bypass" => "Experimental camera toggle test for copied games. It is not a full camera mode.",
                "free_camera_keyboard_forward_q_hook" => "Experimental one-key camera movement test for copied games.",
                "free_camera_keyboard_backward_q_hook" => "Experimental one-key camera movement test for copied games.",
                "free_camera_keyboard_strafe_left_q_hook" => "Experimental one-key camera movement test for copied games.",
                "free_camera_keyboard_strafe_right_q_hook" => "Experimental one-key camera movement test for copied games.",
                "free_camera_keyboard_yaw_left_q_hook" => "Experimental one-key camera rotation test for copied games.",
                "free_camera_keyboard_yaw_right_q_hook" => "Experimental one-key camera rotation test for copied games.",
                "free_camera_keyboard_pitch_up_q_hook" => "Experimental one-key camera pitch test for copied games.",
                "free_camera_keyboard_pitch_down_q_hook" => "Experimental one-key camera pitch test for copied games.",
                _ => spec.DisplayName,
            };
            ProofStatus = spec.Key switch
            {
                "resolution_gate" => "Tested locally as part of the windowed compatibility pair. This does not prove widescreen field-of-view parity.",
                "force_windowed" => "Tested locally as part of the windowed compatibility pair. Some machines can still need the experimental fullscreen branch fallback.",
                "extra_graphics_default_on" => "Launch tested in a safe copy. A visible graphics difference has not been proven yet.",
                "ignore_cardid_tweak_overrides" => "Launch tested in a safe copy. A visible graphics difference has not been proven yet.",
                "version_overlay_use_patched_format_pointer" => "Visible proof: one title/menu frame showed V1.00 - PATCHED. Gameplay overlay paths are still untested.",
                "frontend_clear_screen_dark_red" => "Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show red-family margins. Broader menu coverage is still pending.",
                "frontend_clear_screen_dark_green" => "Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show green-family margins. Broader menu coverage is still pending.",
                "frontend_clear_screen_black" => "Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show black-family margins. Broader menu coverage is still pending.",
                "goodies_gallery_display_unlock" => "Visible proof: two Goodies-wall comparisons changed display state, and one Tatiana page was captured. Model/FMV playback and every-entry browsing remain unproven.",
                "skip_auto_toggle" => "Experimental byte-only proof. Use only after the normal windowed pair is insufficient.",
                "pause_o_scan_initializer_experiment" => "CDB proof: one bounded free-camera run recorded O-query, BUTTON_PAUSE dispatch, and pause/unpause evidence. A separate level-100 normal-gameplay proof recorded O opening pause and Enter resuming from it.",
                "free_camera_aurore_gate_bypass" => "CDB proof: a safe-copy run reached the patched Aurore gate, toggled the free camera on, installed a new camera pointer, and restored the old camera.",
                "free_camera_keyboard_forward_q_hook" => "CDB proof: a hardened safe-copy run hit the Q-forward cave 20 times, read back post-cave button 38, and recorded 20 camera interpolation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_backward_q_hook" => "CDB proof: a safe-copy run hit the Q-backward cave 21 times, read back post-cave button 39, and recorded 21 camera interpolation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_strafe_left_q_hook" => "CDB proof: a safe-copy run hit the Q-strafe-left cave 32 times, read back post-cave button 40, and recorded 32 camera interpolation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_strafe_right_q_hook" => "CDB proof: a safe-copy run hit the Q-strafe-right cave 31 times, read back post-cave button 41, and recorded 31 camera interpolation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_yaw_left_q_hook" => "CDB proof: a safe-copy run hit the Q-yaw-left cave 33 times, read back post-cave button 36, and recorded 33 camera-orientation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_yaw_right_q_hook" => "CDB proof: a safe-copy run hit the Q-yaw-right cave 32 times, read back post-cave button 37, and recorded 32 camera-orientation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_pitch_up_q_hook" => "CDB proof: a safe-copy run hit the Q-pitch-up cave 31 times, read back post-cave button 34, and recorded 31 camera-orientation deltas. This is one key path, not full camera controls.",
                "free_camera_keyboard_pitch_down_q_hook" => "CDB proof: a safe-copy run hit the Q-pitch-down cave 33 times, read back post-cave button 35, and recorded 33 camera-orientation deltas. This is one key path, not full camera controls.",
                _ => "Selected bytes are verified before and after apply.",
            };
            UserFacingStatus = spec.Key switch
            {
                "resolution_gate" => "Safe-copy compatibility fix. Open Details and limits for what was checked.",
                "force_windowed" => "Safe-copy compatibility fix. Open Details and limits for what was checked.",
                "extra_graphics_default_on" => "Safe-copy graphics option. Needs visual comparison on your machine.",
                "ignore_cardid_tweak_overrides" => "Safe-copy graphics option. Needs visual comparison on your machine.",
                "version_overlay_use_patched_format_pointer" => "Safe-copy title-screen marker. Open Details and limits for what was checked.",
                "frontend_clear_screen_dark_red" => "Safe-copy menu color test. Broader menu coverage is still pending.",
                "frontend_clear_screen_dark_green" => "Safe-copy menu color test. Broader menu coverage is still pending.",
                "frontend_clear_screen_black" => "Safe-copy menu color test. Broader menu coverage is still pending.",
                "goodies_gallery_display_unlock" => "Safe-copy Goodies display test. It does not edit saves or award unlocks.",
                "skip_auto_toggle" => "Experimental fallback. Use only if the normal compatibility fixes are insufficient.",
                "pause_o_scan_initializer_experiment" => "Experimental pause-key test. Details list the bounded runtime checks.",
                "free_camera_aurore_gate_bypass" => "Experimental camera toggle test. Not a full camera mode.",
                "free_camera_keyboard_forward_q_hook" => "Experimental camera movement test. One key path only.",
                "free_camera_keyboard_backward_q_hook" => "Experimental camera movement test. One key path only.",
                "free_camera_keyboard_strafe_left_q_hook" => "Experimental camera movement test. One key path only.",
                "free_camera_keyboard_strafe_right_q_hook" => "Experimental camera movement test. One key path only.",
                "free_camera_keyboard_yaw_left_q_hook" => "Experimental camera rotation test. One key path only.",
                "free_camera_keyboard_yaw_right_q_hook" => "Experimental camera rotation test. One key path only.",
                "free_camera_keyboard_pitch_up_q_hook" => "Experimental camera pitch test. One key path only.",
                "free_camera_keyboard_pitch_down_q_hook" => "Experimental camera pitch test. One key path only.",
                _ => "Byte-verified copied-executable patch. Open Details and limits for what was checked.",
            };
            ExpectedVisibleResult = spec.Key switch
            {
                "resolution_gate" => "The safe copy can keep non-4:3 display modes in the display-mode path.",
                "force_windowed" => "The safe copy should prefer a windowed startup path when the runtime supports it.",
                "extra_graphics_default_on" => "The safe copy starts with the old extra-graphics feature gate defaulted on.",
                "ignore_cardid_tweak_overrides" => "The safe copy ignores old cardid.txt GPU override rules and uses executable defaults.",
                "version_overlay_use_patched_format_pointer" => "The title/menu version text can show V1.00 - PATCHED.",
                "frontend_clear_screen_dark_red" => "The title-screen and one navigated frontend menu state can show dark red clear margins.",
                "frontend_clear_screen_dark_green" => "The title-screen and one navigated frontend menu state can show dark green clear margins.",
                "frontend_clear_screen_black" => "The title-screen and one navigated frontend menu state can show black clear margins.",
                "goodies_gallery_display_unlock" => "The Goodies wall can show bounded checked entries as unlocked in the safe copy.",
                "skip_auto_toggle" => "One startup fullscreen-toggle branch is bypassed as a fallback.",
                "pause_o_scan_initializer_experiment" => "The copied executable initializes BUTTON_PAUSE with DirectInput scan 0x18 instead of scan 0x01.",
                "free_camera_aurore_gate_bypass" => "The Aurore cheat gate is bypassed for the existing debug free-camera toggle path.",
                "free_camera_keyboard_forward_q_hook" => "Q can reach the copied-runtime Q-forward free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_backward_q_hook" => "Q can reach the copied-runtime Q-backward free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_strafe_left_q_hook" => "Q can reach the copied-runtime Q-strafe-left free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_strafe_right_q_hook" => "Q can reach the copied-runtime Q-strafe-right free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_yaw_left_q_hook" => "Q can reach the copied-runtime Q-yaw-left free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_yaw_right_q_hook" => "Q can reach the copied-runtime Q-yaw-right free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_pitch_up_q_hook" => "Q can reach the copied-runtime Q-pitch-up free-camera hook path after the debug camera is toggled on.",
                "free_camera_keyboard_pitch_down_q_hook" => "Q can reach the copied-runtime Q-pitch-down free-camera hook path after the debug camera is toggled on.",
                _ => "The selected bytes change only the copied executable.",
            };
            VerifiedProof = spec.Key switch
            {
                "resolution_gate" => "Byte verification plus safe-copy launch/capture/stop smoke with unchanged source hashes.",
                "force_windowed" => "Byte verification plus safe-copy launch/capture/stop smoke with unchanged source hashes.",
                "extra_graphics_default_on" => "Byte verification plus safe-copy launch/capture/stop smoke with the modern graphics rows applied.",
                "ignore_cardid_tweak_overrides" => "Byte verification plus safe-copy launch/capture/stop smoke with the modern graphics rows applied.",
                "version_overlay_use_patched_format_pointer" => "One copied-game title/menu frame showed the V1.00 - PATCHED marker.",
                "frontend_clear_screen_dark_red" => "One copied-game title-screen capture showed red clear-screen margins; one later Goodies-menu run preserved red-family margins after scoped input.",
                "frontend_clear_screen_dark_green" => "One copied-game title-screen capture showed green clear-screen margins; one later Goodies-menu run preserved green-family margins after scoped input.",
                "frontend_clear_screen_black" => "One copied-game title-screen capture showed black clear-screen margins; one later Goodies-menu run preserved black-family margins after scoped input.",
                "goodies_gallery_display_unlock" => "Two baseline-vs-patched Goodies-wall comparisons changed display state; one selected Tatiana page was captured.",
                "skip_auto_toggle" => "Experimental byte-only proof; use after the normal windowed compatibility pair is insufficient.",
                "pause_o_scan_initializer_experiment" => "Safe-copy CDB proof observed copied byte 0x18, live table row 34 keyArg 0x18, exact safe-copy PID/path binding, and ordered same-window O-query, BUTTON_PAUSE dispatch, and pause/unpause evidence in a bounded free-camera context. A level-100 proof separately observed ordered O-query, BUTTON_PAUSE dispatch, CGame__Pause, pause-menu init, and Enter resume.",
                "free_camera_aurore_gate_bypass" => "Safe-copy CDB proof observed the patched gate bytes, BUTTON_TOGGLE_FREE_CAMERA dispatch, free-camera-on SetCurrentCamera, and restore on the second tap.",
                "free_camera_keyboard_forward_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-31 dispatch, and changing free-camera position through PrepareForInterpolation.",
                "free_camera_keyboard_backward_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-32 dispatch, post-cave button-39 readback, and changing free-camera position through PrepareForInterpolation.",
                "free_camera_keyboard_strafe_left_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-29 dispatch, post-cave button-40 readback, and changing free-camera position through PrepareForInterpolation.",
                "free_camera_keyboard_strafe_right_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-30 dispatch, post-cave button-41 readback, and changing free-camera position through PrepareForInterpolation.",
                "free_camera_keyboard_yaw_left_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-25 dispatch, post-cave button-36 readback, and changing free-camera orientation through PrepareForInterpolation.",
                "free_camera_keyboard_yaw_right_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-27 dispatch, post-cave button-37 readback, and changing free-camera orientation through PrepareForInterpolation.",
                "free_camera_keyboard_pitch_up_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-26 dispatch with negative vertical analogue value, post-cave button-34 readback, and changing free-camera orientation through PrepareForInterpolation.",
                "free_camera_keyboard_pitch_down_q_hook" => "Safe-copy CDB proof observed hook bytes, cave bytes, Q/button-28 dispatch with positive vertical analogue value, post-cave button-35 readback, and changing free-camera orientation through PrepareForInterpolation.",
                _ => "Patch bytes are checked before and after apply.",
            };
            StillUnproven = spec.Key switch
            {
                "resolution_gate" => "Field-of-view parity, aspect-ratio gameplay parity, and every display setup.",
                "force_windowed" => "Staying windowed on every machine and wrapper setup.",
                "extra_graphics_default_on" => "Specific visual quality changes and rendering parity.",
                "ignore_cardid_tweak_overrides" => "Specific visual quality changes and rendering parity.",
                "version_overlay_use_patched_format_pointer" => "Every overlay path, version-cheat path, gameplay visibility, and long-session behavior.",
                "frontend_clear_screen_dark_red" => "Every menu state, whole-menu theming, textures, fonts, HUD colors, and gameplay colors.",
                "frontend_clear_screen_dark_green" => "Every menu state, whole-menu theming, textures, fonts, HUD colors, and gameplay colors.",
                "frontend_clear_screen_black" => "Every menu state, whole-menu theming, textures, fonts, HUD colors, and gameplay colors.",
                "goodies_gallery_display_unlock" => "Model/FMV playback, every-entry browsing, save persistence, and permanent unlocks.",
                "skip_auto_toggle" => "Whether it helps a specific runtime setup.",
                "pause_o_scan_initializer_experiment" => "Second-O normal-gameplay unpause, broad pause/menu safety, gameplay safety, control feel, all profiles, long-session behavior, render parity, online/netcode, rebuild parity, and no-noticeable-difference parity.",
                "free_camera_aurore_gate_bypass" => "Full camera behavior remains unproven beyond bounded toggle and companion movement/orientation paths; gameplay safety, pause/menu behavior, render parity, online/netcode, rebuild parity, and no-noticeable-difference parity.",
                "free_camera_keyboard_forward_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_backward_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_strafe_left_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_strafe_right_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_yaw_left_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_yaw_right_q_hook" => "Control feel, all remaining keybind combinations, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_pitch_up_q_hook" => "Full free-camera controls, control feel, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                "free_camera_keyboard_pitch_down_q_hook" => "Full free-camera controls, control feel, joystick/analog coverage, pause/menu safety, gameplay safety, render parity, online/netcode, rebuild parity, no-noticeable-difference parity, and long-session behavior.",
                _ => "Runtime behavior beyond the byte patch.",
            };
            ProofReference = spec.Key switch
            {
                "resolution_gate" => "Public proof: Windowed & Mods safety register.",
                "force_windowed" => "Public proof: Windowed & Mods safety register.",
                "extra_graphics_default_on" => "Public proof: Windowed & Mods safety register.",
                "ignore_cardid_tweak_overrides" => "Public proof: Windowed & Mods safety register.",
                "version_overlay_use_patched_format_pointer" => "Public proof: patch catalog and safety register.",
                "frontend_clear_screen_dark_red" => "Public proof: frontend color patch contract.",
                "frontend_clear_screen_dark_green" => "Public proof: frontend color patch contract.",
                "frontend_clear_screen_black" => "Public proof: frontend color patch contract.",
                "goodies_gallery_display_unlock" => "Public proof: Goodies display patch contract.",
                "skip_auto_toggle" => "Public proof: Windowed & Mods safety register.",
                "pause_o_scan_initializer_experiment" => "Public diagnostic: control mapping contract.",
                "free_camera_aurore_gate_bypass" => "Public proof: free-camera gate contract.",
                "free_camera_keyboard_forward_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_backward_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_strafe_left_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_strafe_right_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_yaw_left_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_yaw_right_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_pitch_up_q_hook" => "Public proof: free-camera movement contract.",
                "free_camera_keyboard_pitch_down_q_hook" => "Public proof: free-camera movement contract.",
                _ => "Public proof: patches/README.md.",
            };
        }

        public BinaryPatchSpec Spec { get; }

        public bool IsSelected
        {
            get => _isSelected;
            set
            {
                if (_isSelected == value)
                    return;

                _isSelected = value;
                OnPropertyChanged();
            }
        }

        public string DisplayName => Spec.Key switch
        {
            "resolution_gate" => "Allow non-4:3 display modes",
            "force_windowed" => "Prefer windowed startup",
            "extra_graphics_default_on" => "Set extra graphics default",
            "ignore_cardid_tweak_overrides" => "Ignore old GPU override rules",
            "version_overlay_use_patched_format_pointer" => "Show PATCHED on the title screen",
            "frontend_clear_screen_dark_red" => "Red menu background",
            "frontend_clear_screen_dark_green" => "Green menu background",
            "frontend_clear_screen_black" => "Black menu background",
            "goodies_gallery_display_unlock" => "Goodies wall display-state override",
            "skip_auto_toggle" => "Experimental fullscreen branch fallback",
            "pause_o_scan_initializer_experiment" => "Experimental O-key pause test",
            "free_camera_aurore_gate_bypass" => "Experimental free-camera gate byte change",
            "free_camera_keyboard_forward_q_hook" => "Experimental Q-forward free-camera hook",
            "free_camera_keyboard_backward_q_hook" => "Experimental Q-backward free-camera hook",
            "free_camera_keyboard_strafe_left_q_hook" => "Experimental Q-strafe-left free-camera hook",
            "free_camera_keyboard_strafe_right_q_hook" => "Experimental Q-strafe-right free-camera hook",
            "free_camera_keyboard_yaw_left_q_hook" => "Experimental Q-yaw-left free-camera hook",
            "free_camera_keyboard_yaw_right_q_hook" => "Experimental Q-yaw-right free-camera hook",
            "free_camera_keyboard_pitch_up_q_hook" => "Experimental Q-pitch-up free-camera hook",
            "free_camera_keyboard_pitch_down_q_hook" => "Experimental Q-pitch-down free-camera hook",
            _ => Spec.DisplayName,
        };

        public string AccessibilityHelpText =>
            $"{DisplayName}. {Summary} {UserFacingStatus} Safe copy only. Use the adjacent Details and limits expander for what was checked and remaining limits.";

        public string DetailsHeader => $"Details and limits for {DisplayName}";

        public string RowAutomationId => BuildAutomationId("PatchBenchPatchRow", Spec.Key);

        public string CheckBoxAutomationId => BuildAutomationId("PatchBenchPatchCheckBox", Spec.Key);

        public string DetailsAutomationId => BuildAutomationId("PatchBenchPatchDetails", Spec.Key);

        public string Summary { get; }

        public string ProofStatus { get; }

        public string UserFacingStatus { get; }

        public string ExpectedVisibleResult { get; }

        public string VerifiedProof { get; }

        public string StillUnproven { get; }

        public string ProofReference { get; }

        public string FunctionalArea => Spec.Key switch
        {
            "resolution_gate" => "Display & Startup",
            "force_windowed" => "Display & Startup",
            "skip_auto_toggle" => "Display & Startup",
            "pause_o_scan_initializer_experiment" => "Controls & Pause",
            "extra_graphics_default_on" => "Graphics & Hardware Overrides",
            "ignore_cardid_tweak_overrides" => "Graphics & Hardware Overrides",
            "version_overlay_use_patched_format_pointer" => "UI & Diagnostics",
            "frontend_clear_screen_dark_red" => "Frontend Color Mods",
            "frontend_clear_screen_dark_green" => "Frontend Color Mods",
            "frontend_clear_screen_black" => "Frontend Color Mods",
            "goodies_gallery_display_unlock" => "Goodies Gallery Mods",
            "free_camera_aurore_gate_bypass" => "Debug Camera Mods",
            "free_camera_keyboard_forward_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_backward_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_strafe_left_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_strafe_right_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_yaw_left_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_yaw_right_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_pitch_up_q_hook" => "Debug Camera Mods",
            "free_camera_keyboard_pitch_down_q_hook" => "Debug Camera Mods",
            _ => "Other",
        };

        public string TrackLabel => Spec.Key switch
        {
            "resolution_gate" => "SAFE COPY REQUIRED",
            "force_windowed" => "SAFE COPY REQUIRED",
            "version_overlay_use_patched_format_pointer" => "VISIBLE MARKER",
            "frontend_clear_screen_dark_red" => "MENU COLOR CHECK",
            "frontend_clear_screen_dark_green" => "MENU COLOR CHECK",
            "frontend_clear_screen_black" => "MENU COLOR CHECK",
            "goodies_gallery_display_unlock" => "GOODIES DISPLAY CHECK",
            "free_camera_aurore_gate_bypass" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_forward_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_backward_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_strafe_left_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_strafe_right_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_yaw_left_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_yaw_right_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_pitch_up_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "free_camera_keyboard_pitch_down_q_hook" => "EXPERIMENTAL CAMERA TEST",
            "skip_auto_toggle" => "EXPERIMENTAL FALLBACK",
            "pause_o_scan_initializer_experiment" => "EXPERIMENTAL PAUSE TEST",
            "extra_graphics_default_on" => "BASIC LAUNCH CHECK",
            "ignore_cardid_tweak_overrides" => "BASIC LAUNCH CHECK",
            _ when string.Equals(Spec.Track, "Experimental", System.StringComparison.OrdinalIgnoreCase) => "EXPERIMENTAL: RUNTIME UNPROVEN",
            _ when string.Equals(Spec.Track, "Dangerous", System.StringComparison.OrdinalIgnoreCase) => "DANGEROUS",
            _ => "BYTE VERIFIED",
        };

        public Brush TrackBrush => Spec.Key switch
        {
            "extra_graphics_default_on" => ThemeBrushes.Warning(),
            "ignore_cardid_tweak_overrides" => ThemeBrushes.Warning(),
            "version_overlay_use_patched_format_pointer" => ThemeBrushes.Warning(),
            "frontend_clear_screen_dark_red" => ThemeBrushes.Warning(),
            "frontend_clear_screen_dark_green" => ThemeBrushes.Warning(),
            "frontend_clear_screen_black" => ThemeBrushes.Warning(),
            "goodies_gallery_display_unlock" => ThemeBrushes.Warning(),
            _ when string.Equals(Spec.Track, "Experimental", System.StringComparison.OrdinalIgnoreCase) => ThemeBrushes.Warning(),
            _ when string.Equals(Spec.Track, "Dangerous", System.StringComparison.OrdinalIgnoreCase) => ThemeBrushes.Danger(),
            _ => ThemeBrushes.Success(),
        };

        public string OffsetText => $"Offset 0x{Spec.FileOffset:X}";

        public event PropertyChangedEventHandler? PropertyChanged;

        private static string BuildAutomationId(string prefix, string key)
        {
            var builder = new StringBuilder(prefix.Length + key.Length + 1);
            builder.Append(prefix);
            builder.Append('_');

            foreach (char character in key)
            {
                bool useLiteralCharacter = character is '_' or '-' || char.IsLetterOrDigit(character);
                builder.Append(useLiteralCharacter ? character : '_');
            }

            return builder.ToString();
        }

        private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
