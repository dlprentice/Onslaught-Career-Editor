using Microsoft.Win32;
using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace Onslaught___Career_Editor.Views
{
    public enum SaveEditorMode
    {
        Save,
        Configuration
    }

    /// <summary>
    /// Save Editor / Configuration Editor shared view.
    ///
    /// Modes:
    /// - Save mode: career saves (*.bes)
    /// - Configuration mode: defaultoptions.bea/global options (*.bea)
    /// </summary>
    public partial class SaveEditorView : UserControl
    {
        private const string NoCopySourcePlaceholder = "(No copy source selected)";
        private SaveEditorMode _editorMode = SaveEditorMode.Save;
        private const int NodeBaseOffset = 0x0006;
        private const int NodeSize = 64;
        private const int NodeCount = 100;
        private const int NodeRankOffset = 0x3C;
        private static readonly int[] DefaultKillThresholdSeeds = { 100, 100, 25, 40, 20 };
        private static readonly Dictionary<uint, string> RankBitsToName = new()
        {
            { 0x3F800000u, "S" },
            { 0x3F4CCCCDu, "A" },
            { 0x3F19999Au, "B" },
            { 0x3EB33333u, "C" },
            { 0x3E19999Au, "D" },
            { 0x00000000u, "E" },
            { 0xBF800000u, "NONE" },
        };

        private sealed class MissionRankOverrideRow
        {
            private static readonly string[] s_rankChoices = { "Keep", "S", "A", "B", "C", "D", "E", "NONE" };

            public int NodeIndexZeroBased { get; }
            public string NodeLabel { get; }
            public string MissionLabel { get; }
            public string CurrentRank { get; set; } = "-";
            public IReadOnlyList<string> RankChoices => s_rankChoices;
            public string SelectedRank { get; set; } = "Keep";

            public MissionRankOverrideRow(int nodeIndexZeroBased, string nodeLabel, string missionLabel)
            {
                NodeIndexZeroBased = nodeIndexZeroBased;
                NodeLabel = nodeLabel;
                MissionLabel = missionLabel;
            }
        }

        private sealed class CategoryKillOverrideDescriptor
        {
            public int CategoryIndex { get; }
            public string CategoryName { get; }
            public CheckBox? CheckBox { get; }
            public Slider? Slider { get; }
            public TextBox? TextBox { get; }
            public TextBlock? CurrentTextBlock { get; }

            public CategoryKillOverrideDescriptor(
                int categoryIndex,
                string categoryName,
                CheckBox? checkBox,
                Slider? slider,
                TextBox? textBox,
                TextBlock? currentTextBlock)
            {
                CategoryIndex = categoryIndex;
                CategoryName = categoryName;
                CheckBox = checkBox;
                Slider = slider;
                TextBox = textBox;
                CurrentTextBlock = currentTextBlock;
            }
        }

        private sealed class KeybindOverrideDescriptor
        {
            public string ActionLabel { get; }
            public int EntryId { get; }
            public uint KeyboardDeviceCode { get; }
            public bool AllowLookMouse { get; }
            public bool AllowZoomWheel { get; }
            public bool AllowMouseButtons { get; }
            public int? MirrorEntryId { get; }
            public uint? MirrorKeyboardDeviceCode { get; }
            public TextBox? P1TextBox { get; }
            public TextBox? P2TextBox { get; }

            public KeybindOverrideDescriptor(
                string actionLabel,
                int entryId,
                uint keyboardDeviceCode,
                bool allowLookMouse,
                bool allowZoomWheel,
                bool allowMouseButtons,
                int? mirrorEntryId,
                uint? mirrorKeyboardDeviceCode,
                TextBox? p1TextBox,
                TextBox? p2TextBox)
            {
                ActionLabel = actionLabel;
                EntryId = entryId;
                KeyboardDeviceCode = keyboardDeviceCode;
                AllowLookMouse = allowLookMouse;
                AllowZoomWheel = allowZoomWheel;
                AllowMouseButtons = allowMouseButtons;
                MirrorEntryId = mirrorEntryId;
                MirrorKeyboardDeviceCode = mirrorKeyboardDeviceCode;
                P1TextBox = p1TextBox;
                P2TextBox = p2TextBox;
            }
        }

        private readonly BesFilePatcher _patcher;
        private List<string> _saveFiles = new();
        private bool _inputValid;
        private bool _keybindOverridesValid = true;
        private readonly List<MissionRankOverrideRow> _missionRankRows = new();

        public SaveEditorMode EditorMode
        {
            get => _editorMode;
            set
            {
                _editorMode = value;
                if (!IsLoaded)
                    return;
                ApplyEditorModeUi();
                LoadSaveFiles();
            }
        }

        private bool IsConfigurationMode => _editorMode == SaveEditorMode.Configuration;

        private static readonly int[] MissionWorldNumbers =
        {
            100,110,200,211,212,221,222,231,232,300,311,312,321,322,331,332,400,411,412,421,422,431,432,
            500,511,512,521,522,523,524,600,611,612,621,622,700,710,720,731,732,741,742,800
        };

        private sealed record KeybindRule(
            int EntryId,
            bool AllowLookMouse,
            bool AllowZoomWheel,
            bool AllowMouseButtons,
            object? OriginalToolTip);

        private readonly Dictionary<TextBox, KeybindRule> _keybindRuleByTextBox = new();
        private readonly List<KeybindOverrideDescriptor> _keybindOverrideDescriptors = new();
        private readonly List<CategoryKillOverrideDescriptor> _categoryKillOverrideDescriptors = new();
        private readonly int[] _loadedKillCounts = DefaultKillThresholdSeeds.ToArray();
        private bool _hasLoadedKillCounts;
        private bool _loadedKillCountsMixed;
        private bool _killsOnlyRestoreCaptured;
        private bool _killsOnlyRestoreNodes = true;
        private bool _killsOnlyRestoreLinks = true;
        private bool _killsOnlyRestoreGoodies = true;
        private bool _killsOnlyRestoreKills = true;
        private bool _suppressCategoryKillTextSync;
        private bool _suppressGlobalKillTextSync;
        private bool _suppressPatchPresetSync;

        public SaveEditorView()
        {
            InitializeComponent();
            _patcher = new BesFilePatcher();
            StatusTextBox.Text = "Select an input file to begin. Save mode expects .bes career files; Configuration mode expects .bea options files.";
            MainWindow.SetStatus("Save Editor: Ready");
            InitializeMissionRankOverrides();
            InitializeCategoryKillOverrideDescriptors();
            InitializeKeybindOverrideDescriptors();
            InitializeOverrideControlState();
            SetCopyOptionsSourcePath(null);
            ApplyEditorModeUi();
            LoadSaveFiles();
            HookKeybindValidation();
            HookPendingChangeTracking();
            SyncGlobalKillTextFromSlider();
        }

        private void InitializeCategoryKillOverrideDescriptors()
        {
            _categoryKillOverrideDescriptors.Clear();
            _categoryKillOverrideDescriptors.Add(new CategoryKillOverrideDescriptor(
                BesFilePatcher.KILL_AIRCRAFT, "Aircraft", AircraftOverrideCheckBox, AircraftKillsSlider, AircraftKillsTextBox, AircraftCurrentKillsTextBlock));
            _categoryKillOverrideDescriptors.Add(new CategoryKillOverrideDescriptor(
                BesFilePatcher.KILL_VEHICLES, "Vehicles", VehicleOverrideCheckBox, VehicleKillsSlider, VehicleKillsTextBox, VehicleCurrentKillsTextBlock));
            _categoryKillOverrideDescriptors.Add(new CategoryKillOverrideDescriptor(
                BesFilePatcher.KILL_EMPLACEMENTS, "Emplacements", EmplacementOverrideCheckBox, EmplacementKillsSlider, EmplacementKillsTextBox, EmplacementCurrentKillsTextBlock));
            _categoryKillOverrideDescriptors.Add(new CategoryKillOverrideDescriptor(
                BesFilePatcher.KILL_INFANTRY, "Infantry", InfantryOverrideCheckBox, InfantryKillsSlider, InfantryKillsTextBox, InfantryCurrentKillsTextBlock));
            _categoryKillOverrideDescriptors.Add(new CategoryKillOverrideDescriptor(
                BesFilePatcher.KILL_MECHS, "Mechs", MechOverrideCheckBox, MechKillsSlider, MechKillsTextBox, MechCurrentKillsTextBlock));
        }

        private void InitializeKeybindOverrideDescriptors()
        {
            _keybindOverrideDescriptors.Clear();

            // Movement
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Movement: Forward", 0x1F, 9, false, false, false, null, null, MoveForwardP1TextBox, MoveForwardP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Movement: Backward", 0x20, 9, false, false, false, null, null, MoveBackwardP1TextBox, MoveBackwardP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Movement: Left", 0x1D, 9, false, false, false, null, null, MoveLeftP1TextBox, MoveLeftP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Movement: Right", 0x1E, 9, false, false, false, null, null, MoveRightP1TextBox, MoveRightP2TextBox));

            // Look
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Look: Up", 0x1A, 9, true, false, false, null, null, LookUpP1TextBox, LookUpP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Look: Down", 0x1C, 9, true, false, false, null, null, LookDownP1TextBox, LookDownP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Look: Left", 0x19, 9, true, false, false, null, null, LookLeftP1TextBox, LookLeftP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Look: Right", 0x1B, 9, true, false, false, null, null, LookRightP1TextBox, LookRightP2TextBox));

            // Zoom
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Zoom: In", 0x10, 9, false, true, false, null, null, ZoomInP1TextBox, ZoomInP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Zoom: Out", 0x11, 9, false, true, false, null, null, ZoomOutP1TextBox, ZoomOutP2TextBox));

            // Others
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Others: Fire weapon", 0x12, 10, false, false, true, 0x13, 9u, FireWeaponP1TextBox, FireWeaponP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Others: Select weapon", 0x14, 10, false, false, true, null, null, SelectWeaponP1TextBox, SelectWeaponP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Others: Transform", 0x21, 8, false, false, false, null, null, TransformP1TextBox, TransformP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Others: Air brake", 0x15, 9, false, false, false, null, null, AirBrakeP1TextBox, AirBrakeP2TextBox));
            _keybindOverrideDescriptors.Add(new KeybindOverrideDescriptor("Others: Special function", 0x3B, 8, false, false, false, null, null, SpecialFunctionP1TextBox, SpecialFunctionP2TextBox));
        }

        private void ApplyEditorModeUi()
        {
            bool configMode = IsConfigurationMode;

            if (ModeBannerBorder != null)
            {
                ModeBannerBorder.Visibility = configMode ? Visibility.Visible : Visibility.Collapsed;
            }

            if (PatchOptionsGroupBox != null)
            {
                PatchOptionsGroupBox.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
            }

            if (PatchSectionsGroupBox != null)
            {
                PatchSectionsGroupBox.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
            }

            if (ShowAdvancedCheckBox != null)
            {
                ShowAdvancedCheckBox.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
                if (configMode)
                {
                    ShowAdvancedCheckBox.IsChecked = true;
                }
            }

            if (AdvancedOptionsPanel != null && configMode)
            {
                AdvancedOptionsPanel.Visibility = Visibility.Visible;
            }

            if (CareerAdvancedSectionsPanel != null)
            {
                CareerAdvancedSectionsPanel.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
            }

            if (CareerProgressExpander != null)
            {
                CareerProgressExpander.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
                if (configMode)
                {
                    CareerProgressExpander.IsExpanded = false;
                }
            }

            if (CareerSettingsExpander != null)
            {
                CareerSettingsExpander.Header = configMode
                    ? "Configuration Settings Overrides"
                    : "Career Settings Overrides";
                CareerSettingsExpander.IsExpanded = configMode;
            }

            if (CareerSettingsDescriptionTextBlock != null)
            {
                CareerSettingsDescriptionTextBlock.Text = configMode
                    ? "Edit global configuration values read from defaultoptions.bea at boot. Leave blank / Keep to preserve existing values."
                    : "Optional: override settings stored in the fixed CCareer block. Leave blank / Keep to preserve existing values.";
            }

            if (CareerSettingsSteamNoteTextBlock != null)
            {
                CareerSettingsSteamNoteTextBlock.Text = configMode
                    ? "Configuration mode writes defaultoptions.bea directly. This file is authoritative at boot for keybinds and most global options, so changes here are the most reliable way to affect startup settings."
                    : "Note (Steam build): loading a .bes save preserves current Sound/Music volumes and does not immediately apply options entries/tail (keybinds, mouse sensitivity, screen shape). For deterministic global settings changes, patch defaultoptions.bea directly; alternatively, load/save frontend flows can sync a .bes buffer into defaultoptions.bea for next boot (restart still required).";
            }

            if (GodModeNoteTextBlock != null)
            {
                GodModeNoteTextBlock.Visibility = configMode ? Visibility.Collapsed : Visibility.Visible;
            }

            if (KeybindSettingsExpander != null)
            {
                KeybindSettingsExpander.Header = configMode
                    ? "Keybind and Global Settings Overrides (defaultoptions.bea)"
                    : "Keybind and Global Settings Overrides (Advanced)";
                if (!configMode)
                {
                    KeybindSettingsExpander.IsExpanded = false;
                }
            }

            if (SaveEditorHintText != null)
            {
                SaveEditorHintText.Text = configMode
                    ? "Configuration mode targets defaultoptions.bea (global options + keybinds)."
                    : "Save mode is focused on career progress files (.bes). Use Save Analyzer to inspect either format.";
            }

            if (OutputPathHintText != null)
            {
                OutputPathHintText.Text = configMode
                    ? "Configuration mode can patch defaultoptions.bea in place after confirmation. The app creates a timestamped .bak before replacing the original file."
                    : "Save mode always writes to a separate .bes output path. In-place save patching is blocked on purpose.";
            }

            if (PatchButton != null)
            {
                PatchButton.Content = configMode ? "Patch Configuration" : "Patch Save";
                PatchButton.ToolTip = configMode
                    ? "Apply patches to the selected configuration file (.bea)."
                    : "Apply patches to the selected save file (.bes).";
            }

            if (configMode)
            {
                if (PatchNodesCheckBox != null)
                {
                    PatchNodesCheckBox.IsChecked = false;
                    PatchNodesCheckBox.IsEnabled = false;
                }
                if (PatchLinksCheckBox != null)
                {
                    PatchLinksCheckBox.IsChecked = false;
                    PatchLinksCheckBox.IsEnabled = false;
                }
                if (PatchGoodiesCheckBox != null)
                {
                    PatchGoodiesCheckBox.IsChecked = false;
                    PatchGoodiesCheckBox.IsEnabled = false;
                }
                if (PatchKillsCheckBox != null)
                {
                    PatchKillsCheckBox.IsChecked = false;
                    PatchKillsCheckBox.IsEnabled = false;
                }
                if (KillsOnlyCheckBox != null)
                {
                    KillsOnlyCheckBox.IsChecked = false;
                    KillsOnlyCheckBox.IsEnabled = false;
                }
            }
            else
            {
                if (PatchNodesCheckBox != null) PatchNodesCheckBox.IsEnabled = true;
                if (PatchLinksCheckBox != null) PatchLinksCheckBox.IsEnabled = true;
                if (PatchGoodiesCheckBox != null) PatchGoodiesCheckBox.IsEnabled = true;
                if (PatchKillsCheckBox != null) PatchKillsCheckBox.IsEnabled = true;
                if (KillsOnlyCheckBox != null) KillsOnlyCheckBox.IsEnabled = true;
                KillsOnlyCheckBox_Changed(this, new RoutedEventArgs());
            }

            UpdatePatchButtonState();
        }

        private void InitializeMissionRankOverrides()
        {
            _missionRankRows.Clear();

            for (int i = 0; i < MissionWorldNumbers.Length; i++)
            {
                int world = MissionWorldNumbers[i];
                string note = world switch
                {
                    100 => "Training",
                    110 => "Tutorial",
                    500 => "Branching",
                    800 => "Final",
                    _ => string.Empty,
                };
                string missionLabel = string.IsNullOrWhiteSpace(note)
                    ? $"level{world}"
                    : $"level{world} ({note})";

                _missionRankRows.Add(new MissionRankOverrideRow(
                    nodeIndexZeroBased: i,
                    nodeLabel: $"{i + 1:00}",
                    missionLabel: missionLabel));
            }

            if (MissionRanksDataGrid != null)
            {
                MissionRanksDataGrid.ItemsSource = _missionRankRows;
            }
        }

        private static string DecodeRankBits(uint rankBits)
        {
            if (RankBitsToName.TryGetValue(rankBits, out string? exact))
                return exact;

            float f = BitConverter.ToSingle(BitConverter.GetBytes(rankBits), 0);
            if (f >= 0.9f) return $"~S ({f:F2})";
            if (f >= 0.7f) return $"~A ({f:F2})";
            if (f >= 0.5f) return $"~B ({f:F2})";
            if (f >= 0.25f) return $"~C ({f:F2})";
            if (f >= 0.1f) return $"~D ({f:F2})";
            if (f > 0f) return $"~D ({f:F2})";
            if (f == 0f) return "E";
            if (f < 0f) return "NONE";
            return $"0x{rankBits:X8}";
        }

        private void PopulateCurrentRanksFromFile(string? filePath)
        {
            foreach (var row in _missionRankRows)
            {
                row.CurrentRank = "-";
            }

            if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
            {
                MissionRanksDataGrid?.Items.Refresh();
                return;
            }

            try
            {
                byte[] buf = File.ReadAllBytes(filePath);
                if (buf.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
                {
                    MissionRanksDataGrid?.Items.Refresh();
                    return;
                }

                for (int i = 0; i < _missionRankRows.Count; i++)
                {
                    int nodeOff = NodeBaseOffset + i * NodeSize;
                    if (nodeOff + NodeSize > buf.Length || i >= NodeCount)
                        continue;

                    uint rankBits = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(nodeOff + NodeRankOffset, 4));
                    _missionRankRows[i].CurrentRank = DecodeRankBits(rankBits);
                }
            }
            catch
            {
                // Non-fatal: leave CurrentRank as "-" when the source file can't be decoded.
            }

            MissionRanksDataGrid?.Items.Refresh();
        }

        private void PopulateKillStateFromFile(string? filePath)
        {
            int[] counts = DefaultKillThresholdSeeds.ToArray();
            _hasLoadedKillCounts = false;
            _loadedKillCountsMixed = false;

            if (!string.IsNullOrWhiteSpace(filePath) && File.Exists(filePath))
            {
                try
                {
                    SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(filePath);
                    if (analysis.IsValid && analysis.KillCounts.Length >= 5)
                    {
                        for (int i = 0; i < 5; i++)
                        {
                            counts[i] = analysis.KillCounts[i];
                        }

                        _hasLoadedKillCounts = true;
                        _loadedKillCountsMixed = counts.Distinct().Count() > 1;
                    }
                }
                catch
                {
                    _hasLoadedKillCounts = false;
                    _loadedKillCountsMixed = false;
                }
            }

            Array.Copy(counts, _loadedKillCounts, _loadedKillCounts.Length);
            ApplyLoadedKillStateToControls();
        }

        private void ApplyLoadedKillStateToControls()
        {
            foreach (CategoryKillOverrideDescriptor descriptor in _categoryKillOverrideDescriptors)
            {
                int value = _loadedKillCounts[descriptor.CategoryIndex];
                SetCurrentKillText(descriptor.CurrentTextBlock, value);
                if (descriptor.CheckBox != null)
                    descriptor.CheckBox.IsChecked = false;
                SetCategoryEditorValue(descriptor.Slider, descriptor.TextBox, value);
            }

            int baselineSeed = _hasLoadedKillCounts
                ? (_loadedKillCountsMixed ? _loadedKillCounts.Max() : _loadedKillCounts[0])
                : DefaultKillThresholdSeeds[0];

            SetGlobalKillEditorValue(baselineSeed);
            UpdateCategoryKillOverrideState();

            if (KillBaselineSummaryText != null)
            {
                KillBaselineSummaryText.Text = _hasLoadedKillCounts
                    ? (_loadedKillCountsMixed
                        ? $"Loaded save uses mixed category counts. The default write value was seeded to the highest current count ({baselineSeed:N0}) so an unchecked-row patch does not silently lower a category."
                        : $"Loaded save uses a shared kill value of {baselineSeed:N0} across all five categories.")
                    : "No save is loaded yet. This field is only the write value used for unchecked categories; it is not a cumulative score.";
            }
        }

        private void SetGlobalKillEditorValue(int value)
        {
            if (KillCountSlider == null || KillCountTextBox == null)
                return;

            int clamped = ClampGlobalKillValue(value);
            _suppressGlobalKillTextSync = true;
            KillCountSlider.Value = Math.Min(clamped, (int)KillCountSlider.Maximum);
            _suppressGlobalKillTextSync = false;
            KillCountTextBox.Text = clamped.ToString(CultureInfo.InvariantCulture);
        }

        private void SetCategoryEditorValue(Slider? slider, TextBox? textBox, int value)
        {
            if (slider == null || textBox == null)
                return;

            int clamped = ClampCategoryKillValue(value, 0x00FFFFFF);
            _suppressCategoryKillTextSync = true;
            slider.Value = Math.Min(clamped, (int)slider.Maximum);
            _suppressCategoryKillTextSync = false;
            textBox.Text = clamped.ToString(CultureInfo.InvariantCulture);
        }

        private void SetCurrentKillText(TextBlock? textBlock, int value)
        {
            if (textBlock == null)
                return;

            textBlock.Text = _hasLoadedKillCounts
                ? value.ToString("N0", CultureInfo.InvariantCulture)
                : "-";
        }

        private void InitializeOverrideControlState()
        {
            PopulateKillStateFromFile(null);
            UpdateCategoryKillOverrideState();
            SyncAllCategoryKillTextBoxesFromSliders();
            UpdateVolumeOverrideState();
        }

        private void HookKeybindValidation()
        {
            _keybindRuleByTextBox.Clear();

            // Minimal UX guardrail: keybind overrides are free-text, but only a small set of tokens are valid
            // per action. Keep registration descriptor-driven to avoid drift between UI rows and parser rules.
            void add(TextBox? tb, KeybindOverrideDescriptor descriptor)
            {
                if (tb == null)
                    return;

                _keybindRuleByTextBox[tb] = new KeybindRule(
                    descriptor.EntryId,
                    descriptor.AllowLookMouse,
                    descriptor.AllowZoomWheel,
                    descriptor.AllowMouseButtons,
                    tb.ToolTip);

                tb.TextChanged -= KeybindOverride_TextChanged;
                tb.LostFocus -= KeybindOverride_LostFocus;
                tb.TextChanged += KeybindOverride_TextChanged;
                tb.LostFocus += KeybindOverride_LostFocus;
            }

            foreach (KeybindOverrideDescriptor descriptor in _keybindOverrideDescriptors)
            {
                add(descriptor.P1TextBox, descriptor);
                add(descriptor.P2TextBox, descriptor);
            }

            ValidateAllKeybindOverrides(showStatusWarning: false);
        }

        private void HookPendingChangeTracking()
        {
            void hookCheck(CheckBox? checkBox)
            {
                if (checkBox == null)
                    return;
                checkBox.Checked += PendingChangeRouted;
                checkBox.Unchecked += PendingChangeRouted;
            }

            void hookCombo(ComboBox? comboBox)
            {
                if (comboBox == null)
                    return;
                comboBox.SelectionChanged += PendingChangeSelectionChanged;
            }

            void hookText(TextBox? textBox)
            {
                if (textBox == null)
                    return;
                textBox.TextChanged += PendingChangeTextChanged;
            }

            var checkBoxes = new List<CheckBox?>
            {
                NewGoodiesCheckBox,
                PatchNodesCheckBox, PatchLinksCheckBox, PatchGoodiesCheckBox, PatchKillsCheckBox, KillsOnlyCheckBox,
                ShowAdvancedCheckBox,
                OverrideSoundVolumeCheckBox, OverrideMusicVolumeCheckBox,
                CopyOptionsEntriesCheckBox, CopyOptionsTailCheckBox
            };
            checkBoxes.AddRange(_categoryKillOverrideDescriptors.Select(d => d.CheckBox));

            foreach (CheckBox? checkBox in checkBoxes)
            {
                hookCheck(checkBox);
            }

            foreach (var comboBox in new[]
            {
                RankComboBox,
                InvertYP1ComboBox, InvertYP2ComboBox,
                InvertFlightP1ComboBox, InvertFlightP2ComboBox,
                ControllerVibrationP1ComboBox, ControllerVibrationP2ComboBox,
                PatchPresetComboBox
            })
            {
                hookCombo(comboBox);
            }

            foreach (var textBox in new[]
            {
                KillCountTextBox,
                SoundVolumeTextBox, MusicVolumeTextBox,
                ControllerConfigP1TextBox, ControllerConfigP2TextBox
            })
            {
                hookText(textBox);
            }

            if (MissionRanksDataGrid != null)
            {
                MissionRanksDataGrid.CurrentCellChanged += PendingChangeCurrentCellChanged;
                MissionRanksDataGrid.CellEditEnding += PendingChangeCellEditEnding;
            }
        }

        private void PendingChangeRouted(object sender, RoutedEventArgs e) => UpdatePatchButtonState();

        private void PendingChangeSelectionChanged(object sender, SelectionChangedEventArgs e) => UpdatePatchButtonState();

        private void PendingChangeTextChanged(object sender, TextChangedEventArgs e) => UpdatePatchButtonState();

        private void PendingChangeCurrentCellChanged(object? sender, EventArgs e) => UpdatePatchButtonState();

        private void PendingChangeCellEditEnding(object? sender, DataGridCellEditEndingEventArgs e) => UpdatePatchButtonState();

        private static int ClampGlobalKillValue(int value)
        {
            if (value < 0)
                return 0;
            if (value > 0x00FFFFFF)
                return 0x00FFFFFF;
            return value;
        }

        private static bool TryParseGlobalKillValue(string? text, out int value)
        {
            value = 0;
            string raw = text?.Trim() ?? string.Empty;
            if (raw.Length == 0)
                return false;

            if (int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed) && parsed >= 0)
            {
                value = ClampGlobalKillValue(parsed);
                return true;
            }

            if (double.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out double parsedInvariant) && parsedInvariant >= 0)
            {
                value = ClampGlobalKillValue((int)Math.Round(parsedInvariant, MidpointRounding.AwayFromZero));
                return true;
            }

            if (double.TryParse(raw, NumberStyles.Float, CultureInfo.CurrentCulture, out double parsedCurrent) && parsedCurrent >= 0)
            {
                value = ClampGlobalKillValue((int)Math.Round(parsedCurrent, MidpointRounding.AwayFromZero));
                return true;
            }

            return false;
        }

        private void SyncGlobalKillTextFromSlider()
        {
            if (_suppressGlobalKillTextSync || KillCountSlider == null || KillCountTextBox == null)
                return;

            KillCountTextBox.Text = ((int)Math.Round(KillCountSlider.Value)).ToString(CultureInfo.InvariantCulture);
        }

        private void KillCountSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (_suppressGlobalKillTextSync || KillCountTextBox == null || KillCountTextBox.IsKeyboardFocusWithin)
                return;

            SyncGlobalKillTextFromSlider();
            UpdatePatchButtonState();
        }

        private void KillCountTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key != Key.Enter)
                return;

            CommitGlobalKillTextBox();
            e.Handled = true;
        }

        private void KillCountTextBox_LostFocus(object sender, RoutedEventArgs e)
        {
            CommitGlobalKillTextBox();
        }

        private void CommitGlobalKillTextBox()
        {
            if (KillCountSlider == null || KillCountTextBox == null)
                return;

            string raw = KillCountTextBox.Text?.Trim() ?? string.Empty;
            if (raw.Length == 0)
            {
                SyncGlobalKillTextFromSlider();
                UpdatePatchButtonState();
                return;
            }

            if (!TryParseGlobalKillValue(raw, out int parsed))
            {
                StatusTextBox.Text = "Error: Global kill baseline must be a non-negative whole number (0 to 16777215).";
                SyncGlobalKillTextFromSlider();
                UpdatePatchButtonState();
                return;
            }

            _suppressGlobalKillTextSync = true;
            KillCountSlider.Value = Math.Min(parsed, (int)KillCountSlider.Maximum);
            _suppressGlobalKillTextSync = false;
            KillCountTextBox.Text = parsed.ToString(CultureInfo.InvariantCulture);
            UpdatePatchButtonState();
        }

        private void KeybindOverride_TextChanged(object sender, TextChangedEventArgs e)
        {
            // Validate eagerly so "Patch Save" can't be pressed with invalid tokens.
            ValidateAllKeybindOverrides(showStatusWarning: false);
        }

        private void KeybindOverride_LostFocus(object sender, RoutedEventArgs e)
        {
            // On focus loss, show a warning if any invalid fields remain.
            ValidateAllKeybindOverrides(showStatusWarning: true);
        }

        private void ValidateAllKeybindOverrides(bool showStatusWarning)
        {
            bool allValid = true;
            foreach (var (tb, rule) in _keybindRuleByTextBox)
            {
                bool ok = ValidateOneKeybindOverride(tb, rule);
                allValid &= ok;
            }

            _keybindOverridesValid = allValid;
            UpdatePatchButtonState();

            if (!showStatusWarning)
                return;

            if (!_keybindOverridesValid)
            {
                // Use "Warning:" prefix so UpdatePatchButtonState won't overwrite it.
                if (!StatusTextBox.Text.StartsWith("Error:", StringComparison.OrdinalIgnoreCase))
                {
                    StatusTextBox.Text =
                        "Warning: One or more keybind override fields are invalid (highlighted in red). " +
                        "Fix them or clear them to preserve existing bindings.";
                }
            }
        }

        private static bool TryValidateLookToken(string token)
        {
            string tl = token.Trim().ToLowerInvariant();
            if (tl is "mouse" or "mousex" or "mousey")
                return true;

            if (tl is "mousex+" or "mousex-" or "mousey+" or "mousey-")
                return true;

            // Analyzer can emit "Mouse(0)" for unknown axis scans. Allow it to round-trip.
            if (tl.StartsWith("mouse(", StringComparison.Ordinal) && tl.EndsWith(")", StringComparison.Ordinal))
            {
                string inner = tl["mouse(".Length..^1];
                return int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out _);
            }

            return false;
        }

        private static bool TryValidateMouseButtonToken(int entryId, string token, out string? error)
        {
            error = null;
            string tl = token.Trim().ToLowerInvariant();
            if (tl == "mouseleft")
            {
                if (entryId is 0x12 or 0x13)
                    return true;
                error = "MouseLeft is only supported for Others: Fire weapon.";
                return false;
            }

            if (tl == "mouseright")
            {
                if (entryId == 0x14)
                    return true;
                error = "MouseRight is only supported for Others: Select weapon.";
                return false;
            }

            error = "Use MouseLeft/MouseRight.";
            return false;
        }

        private static bool TryValidateKeybindToken(
            int entryId,
            bool allowLookMouse,
            bool allowZoomWheel,
            bool allowMouseButtons,
            string token,
            out string? error)
        {
            error = null;
            if (string.IsNullOrWhiteSpace(token))
                return true; // blank => preserve existing binding

            string t = token.Trim();
            if (t.Equals("keep", StringComparison.OrdinalIgnoreCase) ||
                t.Equals("preserve", StringComparison.OrdinalIgnoreCase) ||
                t.Equals("unchanged", StringComparison.OrdinalIgnoreCase))
                return true; // UI parity with PyQt

            // "Mouse" tokens
            if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
            {
                if (TryValidateLookToken(t))
                    return true;
                error = "Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.";
                return false;
            }

            if (allowZoomWheel && (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
                return true;

            if (allowMouseButtons && (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
                return TryValidateMouseButtonToken(entryId, t, out error);

            // Keyboard token
            if (BesFilePatcher.TryParseKeyboardPackedKey(t, out _, out string? err))
                return true;

            error = err ?? "Unrecognized key token.";
            return false;
        }

        private static void MarkKeybindTextBoxInvalid(TextBox tb, KeybindRule rule, string error)
        {
            tb.BorderBrush = System.Windows.Media.Brushes.OrangeRed;
            tb.BorderThickness = new Thickness(2);
            tb.Background = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(0xFF, 0xF0, 0xF0));
            tb.ToolTip = rule.OriginalToolTip is string s && !string.IsNullOrWhiteSpace(s)
                ? $"{s}\nInvalid: {error}"
                : $"Invalid: {error}";
        }

        private static void ClearKeybindTextBoxInvalid(TextBox tb, KeybindRule rule)
        {
            tb.ClearValue(TextBox.BorderBrushProperty);
            tb.ClearValue(TextBox.BorderThicknessProperty);
            tb.ClearValue(TextBox.BackgroundProperty);
            tb.ToolTip = rule.OriginalToolTip;
        }

        private static bool ValidateOneKeybindOverride(TextBox tb, KeybindRule rule)
        {
            if (TryValidateKeybindToken(rule.EntryId, rule.AllowLookMouse, rule.AllowZoomWheel, rule.AllowMouseButtons, tb.Text ?? string.Empty, out string? error))
            {
                ClearKeybindTextBoxInvalid(tb, rule);
                return true;
            }

            MarkKeybindTextBoxInvalid(tb, rule, error ?? "Invalid token.");
            return false;
        }

        private void LoadSaveFiles()
        {
            _saveFiles.Clear();
            SaveFilesComboBox.Items.Clear();

            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();

            if (string.IsNullOrEmpty(gameDir))
            {
                SaveFilesComboBox.Items.Add("(Set game directory in Settings)");
                SaveFilesComboBox.SelectedIndex = 0;
                InputFileTextBox.Text = string.Empty;
                OutputFileTextBox.Text = string.Empty;
                _inputValid = false;
                PopulateCurrentRanksFromFile(null);
                UpdatePatchButtonState();
                return;
            }

            // Use AppConfig's robust save file finder
            var saveInfos = AppConfig.FindSaveFiles(gameDir);

            if (saveInfos.Count > 0)
            {
                foreach (var save in saveInfos)
                {
                    if (IsConfigurationMode && !IsOptionsLikeFilePath(save.Path))
                        continue;
                    if (!IsConfigurationMode && IsOptionsLikeFilePath(save.Path))
                        continue;

                    _saveFiles.Add(save.Path);
                    string validity = save.IsValid ? "" : " [invalid file]";
                    string displayName = $"{Path.GetFileName(save.Path)} ({save.Modified:MMM dd, HH:mm}){validity}";
                    SaveFilesComboBox.Items.Add(displayName);
                }
            }

            if (_saveFiles.Count == 0)
            {
                SaveFilesComboBox.Items.Add(IsConfigurationMode
                    ? "(No .bea options files found)"
                    : "(No .bes career saves found)");
                InputFileTextBox.Text = string.Empty;
                OutputFileTextBox.Text = string.Empty;
                _inputValid = false;
                PopulateCurrentRanksFromFile(null);
            }

            SaveFilesComboBox.SelectedIndex = 0;
            UpdatePatchButtonState();
        }

        private void SaveFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            int index = SaveFilesComboBox.SelectedIndex;
            if (index >= 0 && index < _saveFiles.Count)
            {
                _ = TryLoadInputFile(_saveFiles[index], out _);
            }
        }

        private void RefreshSaveFiles_Click(object sender, RoutedEventArgs e)
        {
            LoadSaveFiles();
            string modeLabel = IsConfigurationMode ? "options file(s)" : "career save(s)";
            StatusTextBox.Text = $"Found {_saveFiles.Count} {modeLabel}";
            MainWindow.SetStatus($"Save Editor: Found {_saveFiles.Count} {modeLabel}");
        }

        private void BrowseInputButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = IsConfigurationMode
                    ? "BEA Options Files (*.bea)|*.bea|All Files (*.*)|*.*"
                    : "BEA Career Saves (*.bes)|*.bes|All Files (*.*)|*.*",
                Title = IsConfigurationMode
                    ? "Select Input Options File (.bea)"
                    : "Select Input Career Save (.bes)"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                if (!TryLoadInputFile(openFileDialog.FileName, out string error))
                {
                    StatusTextBox.Text = error;
                }
            }
        }

        public bool TryLoadInputFile(string filePath, out string error)
        {
            error = string.Empty;
            if (string.IsNullOrWhiteSpace(filePath))
            {
                error = "Input path is empty.";
                UpdatePatchButtonState();
                return false;
            }

            if (!File.Exists(filePath))
            {
                error = $"Input file not found: {filePath}";
                UpdatePatchButtonState();
                return false;
            }

            if (IsConfigurationMode && !IsOptionsLikeFilePath(filePath))
            {
                error = "Configuration mode requires a .bea options file (typically defaultoptions.bea).";
                UpdatePatchButtonState();
                return false;
            }

            if (!IsConfigurationMode && IsOptionsLikeFilePath(filePath))
            {
                error = "Save mode expects a .bes career save file.";
                UpdatePatchButtonState();
                return false;
            }

            InputFileTextBox.Text = filePath;
            OutputFileTextBox.Text = BuildDefaultOutputPath(filePath);
            ValidateInputFile(filePath);
            ApplySafeDefaultsForOptionsFile(filePath);
            ApplySafeDefaultsForOptionsFile(OutputFileTextBox.Text);
            PopulateCurrentRanksFromFile(IsConfigurationMode ? null : filePath);
            PopulateKillStateFromFile(IsConfigurationMode ? null : filePath);
            UpdatePatchButtonState();
            return true;
        }

        private static bool IsOptionsLikeFilePath(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath))
                return false;

            string trimmed = filePath.Trim();
            return string.Equals(Path.GetExtension(trimmed), ".bea", StringComparison.OrdinalIgnoreCase);
        }

        private string BuildDefaultOutputPath(string inputPath)
        {
            if (IsConfigurationMode)
                return inputPath;

            string? directory = Path.GetDirectoryName(inputPath);
            string fileName = Path.GetFileNameWithoutExtension(inputPath);
            string extension = Path.GetExtension(inputPath);
            directory ??= string.Empty;
            return Path.Combine(directory, $"{fileName}_patched{extension}");
        }

        private static string BuildTimestampedBackupPath(string targetPath)
        {
            string? directory = Path.GetDirectoryName(targetPath);
            string fileName = Path.GetFileName(targetPath);
            string stamp = DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
            string candidate = Path.Combine(directory ?? string.Empty, $"{fileName}.{stamp}.bak");
            int n = 1;
            while (File.Exists(candidate))
            {
                candidate = Path.Combine(directory ?? string.Empty, $"{fileName}.{stamp}.{n}.bak");
                n++;
            }

            return candidate;
        }

        private static bool TryGetCanonicalPath(string? path, out string canonicalPath)
        {
            canonicalPath = string.Empty;
            if (string.IsNullOrWhiteSpace(path))
                return false;

            try
            {
                canonicalPath = Path.GetFullPath(path.Trim());
                return true;
            }
            catch
            {
                return false;
            }
        }

        private bool IsInputOutputSamePath()
        {
            if (!TryGetCanonicalPath(InputFileTextBox?.Text, out string inputPath))
                return false;
            if (!TryGetCanonicalPath(OutputFileTextBox?.Text, out string outputPath))
                return false;

            return string.Equals(inputPath, outputPath, StringComparison.OrdinalIgnoreCase);
        }

        private void ApplySafeDefaultsForOptionsFile(string filePath)
        {
            // `defaultoptions.bea` is a global options snapshot (Steam build). It shares the same 10,004-byte
            // format as a career save, but patching mission progress/goodies into it is usually unintended.
            if (!IsOptionsLikeFilePath(filePath))
                return;

            // If the user has already customized these checkboxes, don't fight them. Only flip from the unsafe
            // "everything enabled" default to a safer "settings only" default.
            bool allSectionsEnabled =
                PatchNodesCheckBox.IsChecked == true &&
                PatchLinksCheckBox.IsChecked == true &&
                PatchGoodiesCheckBox.IsChecked == true &&
                PatchKillsCheckBox.IsChecked == true;

            if (!allSectionsEnabled)
                return;

            PatchNodesCheckBox.IsChecked = false;
            PatchLinksCheckBox.IsChecked = false;
            PatchGoodiesCheckBox.IsChecked = false;
            PatchKillsCheckBox.IsChecked = false;
            KillsOnlyCheckBox.IsChecked = false;

            StatusTextBox.Text =
                "Note: defaultoptions.bea is a global options file. Career patch sections were disabled by default to avoid\n" +
                "accidentally writing mission progress/goodies into the options snapshot. Use a .bes file for career progress.\n\n" +
                StatusTextBox.Text;
        }

        private bool HasCareerSectionPatchingEnabled()
        {
            return PatchNodesCheckBox.IsChecked == true ||
                   PatchLinksCheckBox.IsChecked == true ||
                   PatchGoodiesCheckBox.IsChecked == true ||
                   PatchKillsCheckBox.IsChecked == true ||
                   KillsOnlyCheckBox.IsChecked == true;
        }

        private bool ConfirmOptionsFilePatchRiskIfNeeded()
        {
            bool inputOptionsLike = IsOptionsLikeFilePath(InputFileTextBox.Text);
            bool outputOptionsLike = IsOptionsLikeFilePath(OutputFileTextBox.Text);
            if (!inputOptionsLike && !outputOptionsLike)
                return true;

            if (!HasCareerSectionPatchingEnabled())
                return true;

            var result = MessageBox.Show(
                "You are patching career sections (missions/links/goodies/kills) while input or output is an options-style file (.bea/defaultoptions.bea).\n\n" +
                "This can unintentionally push career progression data into global options snapshots.\n\n" +
                "Continue anyway?",
                "Confirm Options File Patch",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning,
                MessageBoxResult.No);

            if (result != MessageBoxResult.Yes)
            {
                StatusTextBox.Text = "Patch canceled by user: options-file safety confirmation declined.";
                MainWindow.SetStatus("Save Editor: Patch canceled");
                return false;
            }

            return true;
        }

        private void ValidateInputFile(string filePath)
        {
            try
            {
                var fileInfo = new FileInfo(filePath);
                if (!fileInfo.Exists)
                {
                    _inputValid = false;
                    StatusTextBox.Text = "Error: File not found.";
                    MainWindow.SetStatus("Save Editor: File not found");
                    return;
                }

                if (IsConfigurationMode && !IsOptionsLikeFilePath(filePath))
                {
                    _inputValid = false;
                    StatusTextBox.Text = "Configuration mode requires a .bea options file (typically defaultoptions.bea).";
                    MainWindow.SetStatus("Save Editor: Configuration mode expects .bea");
                    return;
                }
                if (!IsConfigurationMode && IsOptionsLikeFilePath(filePath))
                {
                    _inputValid = false;
                    StatusTextBox.Text = "Save mode expects a .bes career save file.";
                    MainWindow.SetStatus("Save Editor: Save mode expects .bes");
                    return;
                }

                if (BesFilePatcher.IsValidBesFile(filePath))
                {
                    _inputValid = true;
                    StatusTextBox.Text = IsConfigurationMode
                        ? $"Valid options file ({BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes). Ready to patch configuration."
                        : $"Valid career save ({BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes). Ready to patch.";
                    MainWindow.SetStatus($"Save Editor: Valid file - {Path.GetFileName(filePath)}");
                }
                else
                {
                    _inputValid = false;
                    StatusTextBox.Text =
                        $"Warning: File is not a valid BEA save/options file (size {fileInfo.Length:N0}, expected {BesFilePatcher.EXPECTED_FILE_SIZE:N0}, version 0x{BesFilePatcher.VERSION_WORD:X4}). " +
                        "Patching is disabled.";
                    MainWindow.SetStatus("Save Editor: Warning - invalid file format");
                }
            }
            catch (Exception ex)
            {
                _inputValid = false;
                StatusTextBox.Text = $"Error reading file: {ex.Message}";
                MainWindow.SetStatus($"Save Editor: Error - {ex.Message}");
            }
        }

        private void BrowseOutputButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFileDialog saveFileDialog = new SaveFileDialog
            {
                Filter = IsConfigurationMode
                    ? "BEA Options Files (*.bea)|*.bea|All Files (*.*)|*.*"
                    : "BEA Career Saves (*.bes)|*.bes|All Files (*.*)|*.*",
                Title = IsConfigurationMode
                    ? "Select Output Options File (.bea)"
                    : "Select Output Career Save (.bes)"
            };

            if (!string.IsNullOrEmpty(OutputFileTextBox.Text))
            {
                saveFileDialog.FileName = OutputFileTextBox.Text;
            }

            if (saveFileDialog.ShowDialog() == true)
            {
                if (IsConfigurationMode && !IsOptionsLikeFilePath(saveFileDialog.FileName))
                {
                    StatusTextBox.Text = "Configuration mode output should be a .bea options file.";
                    UpdatePatchButtonState();
                    return;
                }
                if (!IsConfigurationMode && IsOptionsLikeFilePath(saveFileDialog.FileName))
                {
                    StatusTextBox.Text = "Save mode output should be a .bes career save file.";
                    UpdatePatchButtonState();
                    return;
                }

                OutputFileTextBox.Text = saveFileDialog.FileName;
                ApplySafeDefaultsForOptionsFile(OutputFileTextBox.Text);
                UpdatePatchButtonState();
            }
        }

        private void BrowseCopyOptionsFromButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "BEA Save/Options Files (*.bes;*.bea)|*.bes;*.bea|All Files (*.*)|*.*",
                Title = "Select Source Save/Options File (Copy Options From)"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                SetCopyOptionsSourcePath(openFileDialog.FileName);
            }
        }

        private void ClearCopyOptionsFromButton_Click(object sender, RoutedEventArgs e)
        {
            SetCopyOptionsSourcePath(null);
        }

        private void PatchButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string inputPath = InputFileTextBox.Text?.Trim() ?? string.Empty;
                string outputPath = OutputFileTextBox.Text?.Trim() ?? string.Empty;
                bool samePath = IsInputOutputSamePath();
                bool inPlaceConfigPatch = IsConfigurationMode && samePath;

                if (string.IsNullOrWhiteSpace(inputPath) || string.IsNullOrWhiteSpace(outputPath))
                {
                    StatusTextBox.Text = "Select both input and output files before patching.";
                    MainWindow.SetStatus("Save Editor: Missing input/output path");
                    UpdatePatchButtonState();
                    return;
                }

                if (samePath && !inPlaceConfigPatch)
                {
                    StatusTextBox.Text = "Output file must be different from input file. In-place patching is blocked.";
                    MainWindow.SetStatus("Save Editor: Output path must differ from input");
                    UpdatePatchButtonState();
                    return;
                }

                if (inPlaceConfigPatch)
                {
                    var inPlaceConfirm = MessageBox.Show(
                        "Configuration mode will patch this .bea file in place and create a timestamped .bak backup first.\n\n" +
                        $"Target:\n{outputPath}\n\n" +
                        "Continue?",
                        "Confirm In-Place Configuration Patch",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Warning,
                        MessageBoxResult.No);
                    if (inPlaceConfirm != MessageBoxResult.Yes)
                    {
                        StatusTextBox.Text = "Patch canceled by user: in-place configuration patch not confirmed.";
                        MainWindow.SetStatus("Save Editor: Patch canceled");
                        return;
                    }
                }
                else if (!string.IsNullOrWhiteSpace(outputPath) && File.Exists(outputPath))
                {
                    var overwrite = MessageBox.Show(
                        $"Output file already exists:\n{outputPath}\n\nOverwrite it?",
                        "Confirm Overwrite",
                        MessageBoxButton.YesNo,
                        MessageBoxImage.Warning,
                        MessageBoxResult.No);
                    if (overwrite != MessageBoxResult.Yes)
                    {
                        StatusTextBox.Text = "Patch canceled by user: overwrite not confirmed.";
                        MainWindow.SetStatus("Save Editor: Patch canceled");
                        return;
                    }
                }

                PatchButton.IsEnabled = false;
                StatusTextBox.Text = "Patching file...";
                MainWindow.SetStatus("Save Editor: Patching file...");

                if (!ConfirmOptionsFilePatchRiskIfNeeded())
                    return;

                ConfigurePatcher();

                string patchOutputPath = outputPath;
                string? tempInPlaceOutput = null;
                if (inPlaceConfigPatch)
                {
                    string tmpName = Path.GetFileName(outputPath) + ".tmp." + Guid.NewGuid().ToString("N");
                    tempInPlaceOutput = Path.Combine(Path.GetDirectoryName(outputPath) ?? string.Empty, tmpName);
                    patchOutputPath = tempInPlaceOutput;
                }

                var result = _patcher.PatchFile(inputPath, patchOutputPath);

                if (result.Success && inPlaceConfigPatch && tempInPlaceOutput != null)
                {
                    try
                    {
                        string backupPath = BuildTimestampedBackupPath(outputPath);
                        File.Copy(outputPath, backupPath, overwrite: false);
                        File.Copy(tempInPlaceOutput, outputPath, overwrite: true);
                        File.Delete(tempInPlaceOutput);
                        result = PatchResult.Ok(
                            $"Successfully patched configuration in place:\n{outputPath}\n\nBackup created:\n{backupPath}");
                    }
                    catch (Exception ex)
                    {
                        result = PatchResult.Fail(
                            "Patched output was created, but in-place replace failed.\n" +
                            $"Temp patched file: {tempInPlaceOutput}\n" +
                            $"Error: {ex.Message}");
                    }
                }

                StatusTextBox.Text = result.Message;
                MainWindow.SetStatus(result.Success ? "Save Editor: Patch complete!" : "Save Editor: Patch failed!");
            }
            catch (Exception ex)
            {
                StatusTextBox.Text = $"Error: {ex.Message}";
                MainWindow.SetStatus($"Save Editor: Error - {ex.Message}");
            }
            finally
            {
                PatchButton.IsEnabled = true;
            }
        }

        private void LoadKeybindsFromInputButton_Click(object sender, RoutedEventArgs e) =>
            LoadKeybindOverridesFromPath(InputFileTextBox.Text, "main input");

        private void LoadKeybindsFromCopySourceButton_Click(object sender, RoutedEventArgs e) =>
            LoadKeybindOverridesFromPath(NormalizeOptionalPath(CopyOptionsFromTextBox?.Text), "copy source");

        private static string? NormalizeOptionalPath(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return null;

            string t = value.Trim();
            if (string.Equals(t, NoCopySourcePlaceholder, StringComparison.OrdinalIgnoreCase))
                return null;

            return t;
        }

        private void SetCopyOptionsSourcePath(string? path)
        {
            if (CopyOptionsFromTextBox == null)
                return;

            bool hadSource = !string.IsNullOrWhiteSpace(NormalizeOptionalPath(CopyOptionsFromTextBox.Text));
            string? normalized = NormalizeOptionalPath(path);
            bool hasSource = !string.IsNullOrWhiteSpace(normalized);
            if (string.IsNullOrWhiteSpace(normalized))
            {
                CopyOptionsFromTextBox.Text = NoCopySourcePlaceholder;
                CopyOptionsFromTextBox.Foreground = Brushes.Gray;
            }
            else
            {
                CopyOptionsFromTextBox.Text = normalized;
                CopyOptionsFromTextBox.Foreground = Brushes.Black;
            }

            if (!hasSource)
            {
                // Safe baseline when no copy source is selected.
                if (CopyOptionsEntriesCheckBox != null)
                    CopyOptionsEntriesCheckBox.IsChecked = false;
                if (CopyOptionsTailCheckBox != null)
                    CopyOptionsTailCheckBox.IsChecked = false;
            }
            else if (!hadSource)
            {
                // First source selection remains opt-in in both modes.
                if (CopyOptionsEntriesCheckBox != null)
                    CopyOptionsEntriesCheckBox.IsChecked = false;
                if (CopyOptionsTailCheckBox != null)
                    CopyOptionsTailCheckBox.IsChecked = false;
            }

            if (CopyOptionsEntriesCheckBox != null)
                CopyOptionsEntriesCheckBox.IsEnabled = hasSource;
            if (CopyOptionsTailCheckBox != null)
                CopyOptionsTailCheckBox.IsEnabled = hasSource;
            if (LoadKeybindsFromCopySourceButton != null)
                LoadKeybindsFromCopySourceButton.IsEnabled = hasSource;
            UpdatePatchButtonState();
        }

        private void LoadKeybindOverridesFromPath(string? pathRaw, string sourceLabel)
        {
            try
            {
                string path = pathRaw?.Trim() ?? string.Empty;
                if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
                {
                    StatusTextBox.Text = $"Error: Select a valid {sourceLabel} file first.";
                    return;
                }

                var analysis = BesFilePatcher.AnalyzeSave(path);
                if (!analysis.IsValid || analysis.OptionsTailStart == 0 || analysis.OptionsEntryCount <= 0)
                {
                    StatusTextBox.Text = $"Error: {sourceLabel} file does not contain an options entries block.";
                    return;
                }

                byte[] buf = File.ReadAllBytes(path);
                const int optionsStart = 0x24BE;
                const int entrySize = 0x20;
                int n = analysis.OptionsEntryCount;

                var entries = new Dictionary<int, (uint S0Dev, uint S0Key, uint S1Dev, uint S1Key)>();
                for (int i = 0; i < n; i++)
                {
                    int off = optionsStart + entrySize * i;
                    if (off + entrySize > buf.Length)
                        break;
                    int entryId = BinaryPrimitives.ReadInt32LittleEndian(buf.AsSpan(off + 0x04, 4));
                    uint s0Dev = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x0C, 4));
                    uint s0Key = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x10, 4));
                    uint s1Dev = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x18, 4));
                    uint s1Key = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x1C, 4));
                    entries[entryId] = (s0Dev, s0Key, s1Dev, s1Key);
                }

                static string fmt(uint dev, uint key, int entryId) => BesFilePatcher.FormatBinding(dev, key, entryId);

                string get(int entryId, bool p1)
                {
                    if (!entries.TryGetValue(entryId, out var e))
                        return string.Empty;

                    uint dev = p1 ? e.S0Dev : e.S1Dev;
                    uint key = p1 ? e.S0Key : e.S1Key;
                    return fmt(dev, key, entryId);
                }

                // Populate fields as slot0=P1 and slot1=P2 for retail save/options files.
                foreach (KeybindOverrideDescriptor descriptor in _keybindOverrideDescriptors)
                {
                    int loadEntryId = descriptor.EntryId;
                    if (!entries.ContainsKey(loadEntryId) &&
                        descriptor.MirrorEntryId.HasValue &&
                        entries.ContainsKey(descriptor.MirrorEntryId.Value))
                    {
                        loadEntryId = descriptor.MirrorEntryId.Value;
                    }

                    if (descriptor.P1TextBox != null)
                        descriptor.P1TextBox.Text = get(loadEntryId, true);
                    if (descriptor.P2TextBox != null)
                        descriptor.P2TextBox.Text = get(loadEntryId, false);
                }

                StatusTextBox.Text =
                    $"Loaded keybind values from {sourceLabel} file.\n" +
                    "Edit only the fields you want to change, then click Patch.\n" +
                    "Columns map slot0->Player 1 and slot1->Player 2.\n" +
                    "Tip: global keybinds apply at boot from defaultoptions.bea; load/save flows may sync it from .bes for next boot.";
            }
            catch (Exception ex)
            {
                StatusTextBox.Text = $"Error loading keybinds: {ex.Message}";
            }
        }

        private void ClearKeybindOverridesButton_Click(object sender, RoutedEventArgs e)
        {
            // Leave blanks to preserve existing bindings.
            foreach (KeybindOverrideDescriptor descriptor in _keybindOverrideDescriptors)
            {
                if (descriptor.P1TextBox != null)
                    descriptor.P1TextBox.Text = string.Empty;
                if (descriptor.P2TextBox != null)
                    descriptor.P2TextBox.Text = string.Empty;
            }

            StatusTextBox.Text = "Cleared keybind overrides. Blank fields preserve the file's existing bindings.";
        }

        private void ConfigurePatcher()
        {
            _patcher.UseNewGoodiesInstead = NewGoodiesCheckBox.IsChecked == true;

            if (RankComboBox.SelectedItem is ComboBoxItem selectedItem && selectedItem.Tag is string rank)
            {
                _patcher.Rank = rank;
            }
            else
            {
                _patcher.Rank = "S";
            }

            _patcher.PatchNodes = PatchNodesCheckBox.IsChecked == true;
            _patcher.PatchLinks = PatchLinksCheckBox.IsChecked == true;
            _patcher.PatchGoodies = PatchGoodiesCheckBox.IsChecked == true;
            _patcher.PatchKills = PatchKillsCheckBox.IsChecked == true;

            if (IsConfigurationMode)
            {
                // In configuration mode we intentionally block career progress/goodie mutations.
                _patcher.PatchNodes = false;
                _patcher.PatchLinks = false;
                _patcher.PatchGoodies = false;
                _patcher.PatchKills = false;
            }

            if (_patcher.PatchKills)
            {
                if (!TryParseGlobalKillValue(KillCountTextBox.Text, out int killCount))
                {
                    throw new ArgumentException($"Invalid global kill count '{KillCountTextBox.Text}'. Expected a non-negative integer.");
                }
                _patcher.GlobalKillCount = killCount;
            }

            MissionRanksDataGrid?.CommitEdit(DataGridEditingUnit.Cell, true);
            MissionRanksDataGrid?.CommitEdit(DataGridEditingUnit.Row, true);
            _patcher.LevelRanks = ParseLevelRanksFromGrid();
            _patcher.PerCategoryKills = ParsePerCategoryKills();

            if (IsConfigurationMode)
            {
                _patcher.LevelRanks = null;
                _patcher.PerCategoryKills = null;
            }

            // Optional CCareer settings overrides (blank/Keep = preserve existing)
            _patcher.SoundVolumeOverride = OverrideSoundVolumeCheckBox?.IsChecked == true
                ? ParseOptionalFloat01(SoundVolumeTextBox?.Text, "Sound volume")
                : null;
            _patcher.MusicVolumeOverride = OverrideMusicVolumeCheckBox?.IsChecked == true
                ? ParseOptionalFloat01(MusicVolumeTextBox?.Text, "Music volume")
                : null;

            _patcher.InvertYAxisP1Override = ParseKeepOnOffCombo(InvertYP1ComboBox, "Invert Y (Walker) (P1)");
            _patcher.InvertYAxisP2Override = ParseKeepOnOffCombo(InvertYP2ComboBox, "Invert Y (Walker) (P2)");
            _patcher.InvertFlightP1Override = ParseKeepOnOffCombo(InvertFlightP1ComboBox, "Invert Y (Flight) (P1)");
            _patcher.InvertFlightP2Override = ParseKeepOnOffCombo(InvertFlightP2ComboBox, "Invert Y (Flight) (P2)");
            _patcher.VibrationP1Override = ParseKeepOnOffCombo(ControllerVibrationP1ComboBox, "Controller Vibration (P1)");
            _patcher.VibrationP2Override = ParseKeepOnOffCombo(ControllerVibrationP2ComboBox, "Controller Vibration (P2)");

            _patcher.ControllerConfigP1Override = ParseOptionalUInt(ControllerConfigP1TextBox?.Text, "Controller config (P1)");
            _patcher.ControllerConfigP2Override = ParseOptionalUInt(ControllerConfigP2TextBox?.Text, "Controller config (P2)");

            // Options entries + tail snapshot copy (raw byte copy)
            _patcher.CopyOptionsFromPath = string.IsNullOrWhiteSpace(CopyOptionsFromTextBox?.Text)
                ? null
                : NormalizeOptionalPath(CopyOptionsFromTextBox.Text);
            bool hasCopySource = !string.IsNullOrWhiteSpace(_patcher.CopyOptionsFromPath);
            _patcher.CopyOptionsEntries = hasCopySource && (CopyOptionsEntriesCheckBox?.IsChecked == true);
            _patcher.CopyOptionsTail = hasCopySource && (CopyOptionsTailCheckBox?.IsChecked == true);

            // Keybind overrides (options entries)
            _patcher.OptionsEntryOverrides = ParseKeybindOverrides();
        }

        private Dictionary<int, BesFilePatcher.OptionsEntryOverride>? ParseKeybindOverrides()
        {
            static bool isEmpty(string? s) => string.IsNullOrWhiteSpace(s);

            var dict = new Dictionary<int, BesFilePatcher.OptionsEntryOverride>();

            void setSlot(int entryId, int slotIndex, uint deviceCode, uint packedKey)
            {
                if (!dict.TryGetValue(entryId, out var ov))
                {
                    ov = new BesFilePatcher.OptionsEntryOverride();
                    dict[entryId] = ov;
                }

                var slot = slotIndex == 0 ? ov.Slot0 : ov.Slot1;
                slot.DeviceCode = deviceCode;
                slot.PackedKey = packedKey;
            }

            static (uint Dev, uint Key) parseLookMouse(int entryId)
            {
                // Steam preset uses:
                // - device 11: positive direction, device 12: negative direction
                // - packed_key scan: 0 => X axis, 1 => Y axis
                return entryId switch
                {
                    0x1B => (11u, 0u), // Look Right  (MouseX+)
                    0x19 => (12u, 0u), // Look Left   (MouseX-)
                    0x1A => (11u, 1u), // Look Up     (MouseY+)
                    0x1C => (12u, 1u), // Look Down   (MouseY-)
                    _ => throw new ArgumentException($"Internal error: entry_id 0x{entryId:X} is not a Look entry."),
                };
            }

            static (uint Dev, uint Key) parseLookToken(int entryId, string token)
            {
                // Accept the simple UI token ("Mouse") and the more explicit verbose tokens ("MouseX+/MouseY-")
                // that show up in analyzer output.
                string t = token.Trim();
                string tl = t.ToLowerInvariant();
                if (tl is "mouse" or "mousex" or "mousey")
                    return parseLookMouse(entryId);

                if (tl.StartsWith("mousex", StringComparison.Ordinal))
                {
                    // X axis: scan=0
                    uint key = 0u;
                    if (tl.EndsWith("-", StringComparison.Ordinal))
                        return (12u, key);
                    if (tl.EndsWith("+", StringComparison.Ordinal))
                        return (11u, key);
                    return parseLookMouse(entryId);
                }

                if (tl.StartsWith("mousey", StringComparison.Ordinal))
                {
                    // Y axis: scan=1
                    uint key = 1u;
                    if (tl.EndsWith("-", StringComparison.Ordinal))
                        return (12u, key);
                    if (tl.EndsWith("+", StringComparison.Ordinal))
                        return (11u, key);
                    return parseLookMouse(entryId);
                }

                if (tl.StartsWith("mouse(", StringComparison.Ordinal) && tl.EndsWith(")", StringComparison.Ordinal))
                {
                    string inner = tl["mouse(".Length..^1];
                    if (int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out int scanSigned))
                    {
                        var (devDefault, _) = parseLookMouse(entryId);
                        return (devDefault, unchecked((uint)scanSigned));
                    }
                }

                throw new ArgumentException($"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.");
            }

            static (uint Dev, uint Key) parseZoomMouseWheel(string t)
            {
                if (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase))
                    return (16u, 3u);
                if (t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase))
                    return (16u, 4u);
                throw new ArgumentException($"Invalid zoom binding '{t}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.");
            }

            static (uint Dev, uint Key) parseMouseButton(int entryId, string t)
            {
                if (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase))
                {
                    // Steam build uses these device codes for Fire weapon:
                    // - entry 0x12: dev 17, key 0
                    // - entry 0x13: dev 15, key 0
                    return entryId switch
                    {
                        0x12 => (17u, 0u),
                        0x13 => (15u, 0u),
                        _ => throw new ArgumentException($"MouseLeft is only supported for Fire weapon (entry 0x12/0x13)."),
                    };
                }

                if (t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase))
                {
                    // Steam build uses device 16 scan 2 for Select weapon.
                    return entryId switch
                    {
                        0x14 => (16u, 2u),
                        _ => throw new ArgumentException($"MouseRight is only supported for Select weapon (entry 0x14)."),
                    };
                }

                throw new ArgumentException($"Invalid mouse button binding '{t}'. Use MouseLeft/MouseRight.");
            }

            static uint parseKeyboardPacked(string t, string fieldName)
            {
                if (!BesFilePatcher.TryParseKeyboardPackedKey(t, out uint packed, out string? err))
                    throw new ArgumentException($"Invalid {fieldName}: {err}");
                return packed;
            }

            void parseRow(
                int entryId,
                uint keyboardDeviceCode,
                bool allowLookMouse,
                bool allowZoomWheel,
                bool allowMouseButtons,
                string? p1,
                string? p2,
                string label)
            {
                static bool isKeepToken(string? token)
                {
                    if (string.IsNullOrWhiteSpace(token))
                        return true;
                    string t = token.Trim();
                    return t.Equals("keep", StringComparison.OrdinalIgnoreCase) ||
                           t.Equals("preserve", StringComparison.OrdinalIgnoreCase) ||
                           t.Equals("unchanged", StringComparison.OrdinalIgnoreCase);
                }

                if (!isEmpty(p1))
                {
                    string t = p1!.Trim();
                    if (isKeepToken(t))
                    {
                        // Preserve existing slot value from file.
                    }
                    else if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
                    {
                        var (dev, key) = parseLookToken(entryId, t);
                        setSlot(entryId, 0, dev, key);
                    }
                    else if (allowZoomWheel && (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseZoomMouseWheel(t);
                        setSlot(entryId, 0, dev, key);
                    }
                    else if (allowMouseButtons && (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseMouseButton(entryId, t);
                        setSlot(entryId, 0, dev, key);
                    }
                    else
                    {
                        uint packed = parseKeyboardPacked(t, $"{label} (P1)");
                        setSlot(entryId, 0, keyboardDeviceCode, packed);
                    }
                }

                if (!isEmpty(p2))
                {
                    string t = p2!.Trim();
                    if (isKeepToken(t))
                    {
                        // Preserve existing slot value from file.
                    }
                    else if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
                    {
                        var (dev, key) = parseLookToken(entryId, t);
                        setSlot(entryId, 1, dev, key);
                    }
                    else if (allowZoomWheel && (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseZoomMouseWheel(t);
                        setSlot(entryId, 1, dev, key);
                    }
                    else if (allowMouseButtons && (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseMouseButton(entryId, t);
                        setSlot(entryId, 1, dev, key);
                    }
                    else
                    {
                        uint packed = parseKeyboardPacked(t, $"{label} (P2)");
                        setSlot(entryId, 1, keyboardDeviceCode, packed);
                    }
                }
            }

            foreach (KeybindOverrideDescriptor descriptor in _keybindOverrideDescriptors)
            {
                string? p1 = descriptor.P1TextBox?.Text;
                string? p2 = descriptor.P2TextBox?.Text;
                if (isEmpty(p1) && isEmpty(p2))
                    continue;

                parseRow(
                    descriptor.EntryId,
                    descriptor.KeyboardDeviceCode,
                    descriptor.AllowLookMouse,
                    descriptor.AllowZoomWheel,
                    descriptor.AllowMouseButtons,
                    p1,
                    p2,
                    descriptor.ActionLabel);

                if (descriptor.MirrorEntryId.HasValue)
                {
                    parseRow(
                        descriptor.MirrorEntryId.Value,
                        descriptor.MirrorKeyboardDeviceCode ?? descriptor.KeyboardDeviceCode,
                        descriptor.AllowLookMouse,
                        descriptor.AllowZoomWheel,
                        descriptor.AllowMouseButtons,
                        p1,
                        p2,
                        descriptor.ActionLabel);
                }
            }

            return dict.Count == 0 ? null : dict;
        }

        private static float? ParseOptionalFloat01(string? text, string fieldName)
        {
            if (string.IsNullOrWhiteSpace(text))
                return null;

            string t = text.Trim();
            if (!float.TryParse(t, NumberStyles.Float, CultureInfo.InvariantCulture, out float val) &&
                !float.TryParse(t, NumberStyles.Float, CultureInfo.CurrentCulture, out val))
            {
                throw new ArgumentException($"Invalid {fieldName} value '{text}'. Expected a number like 0.75.");
            }

            // Clamp for safety; the patcher writes raw float bits.
            if (val < 0.0f) val = 0.0f;
            if (val > 1.0f) val = 1.0f;
            return val;
        }

        private static uint? ParseOptionalUInt(string? text, string fieldName)
        {
            if (string.IsNullOrWhiteSpace(text))
                return null;

            string t = text.Trim();
            if (!uint.TryParse(t, NumberStyles.Integer, CultureInfo.InvariantCulture, out uint val) &&
                !uint.TryParse(t, NumberStyles.Integer, CultureInfo.CurrentCulture, out val))
            {
                throw new ArgumentException($"Invalid {fieldName} value '{text}'. Expected a non-negative integer.");
            }
            return val;
        }

        private static bool? ParseKeepOnOffCombo(ComboBox? combo, string fieldName)
        {
            if (combo?.SelectedItem is not ComboBoxItem item || item.Tag is not string tag)
                return null;

            return tag switch
            {
                "KEEP" => null,
                "ON" => true,
                "OFF" => false,
                _ => throw new ArgumentException($"Invalid {fieldName} selection '{tag}'."),
            };
        }

        private Dictionary<int, string>? ParseLevelRanksFromGrid()
        {
            var result = new Dictionary<int, string>();
            var valid = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "S", "A", "B", "C", "D", "E", "NONE" };

            foreach (var row in _missionRankRows)
            {
                string selected = (row.SelectedRank ?? "Keep").Trim();
                if (selected.Equals("Keep", StringComparison.OrdinalIgnoreCase))
                    continue;

                string normalized = selected.ToUpperInvariant();
                if (!valid.Contains(normalized))
                {
                    throw new ArgumentException(
                        $"Invalid rank override '{selected}' for mission node {row.NodeLabel}. Valid values: Keep, S, A, B, C, D, E, NONE.");
                }

                result[row.NodeIndexZeroBased] = normalized;
            }

            return result.Count > 0 ? result : null;
        }

        private Dictionary<int, int>? ParsePerCategoryKills()
        {
            var result = new Dictionary<int, int>();

            const int maxKillValue = 0x00FFFFFF;

            foreach (CategoryKillOverrideDescriptor descriptor in _categoryKillOverrideDescriptors)
            {
                int? parsed = ParseCategoryKillOverride(descriptor, maxKillValue);
                if (parsed.HasValue)
                    result[descriptor.CategoryIndex] = parsed.Value;
            }

            return result.Count > 0 ? result : null;
        }

        private static int ClampCategoryKillValue(int value, int maxKillValue)
        {
            if (value < 0) return 0;
            if (value > maxKillValue) return maxKillValue;
            return value;
        }

        private int? ParseCategoryKillOverride(
            CategoryKillOverrideDescriptor descriptor,
            int maxKillValue)
        {
            if (descriptor.CheckBox?.IsChecked != true)
                return null;
            if (descriptor.Slider == null || descriptor.TextBox == null)
                return null;

            string raw = descriptor.TextBox.Text?.Trim() ?? string.Empty;
            if (raw.Length == 0)
            {
                int seeded = ClampCategoryKillValue((int)Math.Round(descriptor.Slider.Value), maxKillValue);
                descriptor.TextBox.Text = seeded.ToString(CultureInfo.InvariantCulture);
                return seeded;
            }

            if (!int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed))
            {
                throw new ArgumentException(
                    $"{descriptor.CategoryName} kill override must be a whole number (0 to {maxKillValue}).");
            }

            int clamped = ClampCategoryKillValue(parsed, maxKillValue);
            _suppressCategoryKillTextSync = true;
            descriptor.Slider.Value = Math.Min(clamped, (int)descriptor.Slider.Maximum);
            _suppressCategoryKillTextSync = false;
            descriptor.TextBox.Text = clamped.ToString(CultureInfo.InvariantCulture);
            return clamped;
        }

        private void SetMissionRanksToDefaultButton_Click(object sender, RoutedEventArgs e)
        {
            string defaultRank = "S";
            if (RankComboBox?.SelectedItem is ComboBoxItem item && item.Tag is string tag && !string.IsNullOrWhiteSpace(tag))
            {
                defaultRank = tag.Trim().ToUpperInvariant();
            }

            foreach (var row in _missionRankRows)
            {
                row.SelectedRank = defaultRank;
            }

            MissionRanksDataGrid?.Items.Refresh();
            StatusTextBox.Text = $"Set all mission rank overrides to {defaultRank}.";
            UpdatePatchButtonState();
        }

        private void ClearMissionRanksButton_Click(object sender, RoutedEventArgs e)
        {
            foreach (var row in _missionRankRows)
            {
                row.SelectedRank = "Keep";
            }

            MissionRanksDataGrid?.Items.Refresh();
            StatusTextBox.Text = "Cleared per-mission rank overrides (all rows set to Keep).";
            UpdatePatchButtonState();
        }

        private void CategoryKillOverrideCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            UpdateCategoryKillOverrideState();
            UpdatePatchButtonState();
        }

        private void UpdateCategoryKillOverrideState()
        {
            foreach (CategoryKillOverrideDescriptor descriptor in _categoryKillOverrideDescriptors)
            {
                SetCategoryOverrideState(descriptor);
            }
        }

        private void SyncAllCategoryKillTextBoxesFromSliders()
        {
            foreach (CategoryKillOverrideDescriptor descriptor in _categoryKillOverrideDescriptors)
            {
                SyncCategoryKillTextBoxFromSlider(descriptor.Slider, descriptor.TextBox);
            }
        }

        private static void SyncCategoryKillTextBoxFromSlider(Slider? slider, TextBox? textBox)
        {
            if (slider == null || textBox == null)
                return;
            textBox.Text = ((int)Math.Round(slider.Value)).ToString(CultureInfo.InvariantCulture);
        }

        private void SetCategoryOverrideState(CategoryKillOverrideDescriptor descriptor)
        {
            if (descriptor.CheckBox == null || descriptor.Slider == null || descriptor.TextBox == null)
                return;

            bool enabled = descriptor.CheckBox.IsChecked == true;
            descriptor.Slider.IsEnabled = enabled;
            descriptor.TextBox.IsEnabled = enabled;

            if (!enabled)
            {
                return;
            }

            if (!TryParseGlobalKillValue(descriptor.TextBox.Text, out int explicitValue))
            {
                SyncCategoryKillTextBoxFromSlider(descriptor.Slider, descriptor.TextBox);
                return;
            }

            descriptor.TextBox.Text = ClampCategoryKillValue(explicitValue, 0x00FFFFFF).ToString(CultureInfo.InvariantCulture);
        }

        private void CategoryKillSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (_suppressCategoryKillTextSync)
                return;

            if (sender is not Slider slider)
                return;

            CategoryKillOverrideDescriptor? descriptor = _categoryKillOverrideDescriptors.FirstOrDefault(d => ReferenceEquals(d.Slider, slider));
            TextBox? textBox = descriptor?.TextBox;

            if (textBox == null || textBox.IsKeyboardFocusWithin)
                return;

            SyncCategoryKillTextBoxFromSlider(slider, textBox);
        }

        private void CategoryKillTextBox_LostFocus(object sender, RoutedEventArgs e)
        {
            CommitCategoryKillTextBox(sender as TextBox);
        }

        private void CategoryKillTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key != Key.Enter)
                return;

            CommitCategoryKillTextBox(sender as TextBox);
            e.Handled = true;
        }

        private void CommitCategoryKillTextBox(TextBox? textBox)
        {
            if (textBox == null)
                return;

            CategoryKillOverrideDescriptor? descriptor = _categoryKillOverrideDescriptors.FirstOrDefault(d => ReferenceEquals(d.TextBox, textBox));
            if (descriptor?.Slider == null)
                return;

            string raw = textBox.Text?.Trim() ?? string.Empty;
            if (raw.Length == 0)
            {
                SyncCategoryKillTextBoxFromSlider(descriptor.Slider, textBox);
                return;
            }

            if (!int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed))
            {
                StatusTextBox.Text = "Error: " + descriptor.CategoryName + " override must be a whole number (0 to 16777215).";
                SyncCategoryKillTextBoxFromSlider(descriptor.Slider, textBox);
                return;
            }

            int clamped = ClampCategoryKillValue(parsed, maxKillValue: 0x00FFFFFF);
            _suppressCategoryKillTextSync = true;
            descriptor.Slider.Value = Math.Min(clamped, (int)descriptor.Slider.Maximum);
            _suppressCategoryKillTextSync = false;
            textBox.Text = clamped.ToString(CultureInfo.InvariantCulture);
        }

        private void VolumeOverrideCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            UpdateVolumeOverrideState();
        }

        private void UpdateVolumeOverrideState()
        {
            SetVolumeOverrideState(OverrideSoundVolumeCheckBox, SoundVolumeSlider, SoundVolumeTextBox);
            SetVolumeOverrideState(OverrideMusicVolumeCheckBox, MusicVolumeSlider, MusicVolumeTextBox);
        }

        private static void SetVolumeOverrideState(CheckBox? checkBox, Slider? slider, TextBox? textBox)
        {
            bool enabled = checkBox?.IsChecked == true;
            if (slider != null)
                slider.IsEnabled = enabled;
            if (textBox != null)
                textBox.IsEnabled = enabled;
        }

        private void KillsOnlyCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            bool killsOnly = KillsOnlyCheckBox.IsChecked == true;

            if (killsOnly)
            {
                _killsOnlyRestoreNodes = PatchNodesCheckBox.IsChecked == true;
                _killsOnlyRestoreLinks = PatchLinksCheckBox.IsChecked == true;
                _killsOnlyRestoreGoodies = PatchGoodiesCheckBox.IsChecked == true;
                _killsOnlyRestoreKills = PatchKillsCheckBox.IsChecked == true;
                _killsOnlyRestoreCaptured = true;

                PatchNodesCheckBox.IsChecked = false;
                PatchLinksCheckBox.IsChecked = false;
                PatchGoodiesCheckBox.IsChecked = false;
                PatchKillsCheckBox.IsChecked = true;
            }
            else
            {
                // On first load we keep whatever defaults/preset already set.
                // Only restore prior values after the user actually toggles Kills Only on once.
                if (_killsOnlyRestoreCaptured)
                {
                    PatchNodesCheckBox.IsChecked = _killsOnlyRestoreNodes;
                    PatchLinksCheckBox.IsChecked = _killsOnlyRestoreLinks;
                    PatchGoodiesCheckBox.IsChecked = _killsOnlyRestoreGoodies;
                    PatchKillsCheckBox.IsChecked = _killsOnlyRestoreKills;
                }
            }

            PatchNodesCheckBox.IsEnabled = !killsOnly;
            PatchLinksCheckBox.IsEnabled = !killsOnly;
            PatchGoodiesCheckBox.IsEnabled = !killsOnly;
            PatchKillsCheckBox.IsEnabled = !killsOnly;
            PatchSectionCheckBox_Changed(sender, e);
        }

        private void PatchPresetComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_suppressPatchPresetSync || PatchPresetComboBox == null)
                return;
            if (KillsOnlyCheckBox == null ||
                PatchNodesCheckBox == null ||
                PatchLinksCheckBox == null ||
                PatchGoodiesCheckBox == null ||
                PatchKillsCheckBox == null)
                return;

            string preset = (PatchPresetComboBox.SelectedItem as ComboBoxItem)?.Tag as string ?? "QUICK";
            _suppressPatchPresetSync = true;
            try
            {
                if (preset == "SAFE")
                {
                    KillsOnlyCheckBox.IsChecked = false;
                    PatchNodesCheckBox.IsChecked = false;
                    PatchLinksCheckBox.IsChecked = false;
                    PatchGoodiesCheckBox.IsChecked = false;
                    PatchKillsCheckBox.IsChecked = false;
                }
                else if (preset == "QUICK")
                {
                    KillsOnlyCheckBox.IsChecked = false;
                    PatchNodesCheckBox.IsChecked = true;
                    PatchLinksCheckBox.IsChecked = true;
                    PatchGoodiesCheckBox.IsChecked = true;
                    PatchKillsCheckBox.IsChecked = true;
                }
            }
            finally
            {
                _suppressPatchPresetSync = false;
            }

            UpdatePatchButtonState();
        }

        private void PatchSectionCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (_suppressPatchPresetSync || PatchPresetComboBox == null)
                return;
            if (KillsOnlyCheckBox == null ||
                PatchNodesCheckBox == null ||
                PatchLinksCheckBox == null ||
                PatchGoodiesCheckBox == null ||
                PatchKillsCheckBox == null)
                return;

            bool quick =
                KillsOnlyCheckBox.IsChecked != true &&
                PatchNodesCheckBox.IsChecked == true &&
                PatchLinksCheckBox.IsChecked == true &&
                PatchGoodiesCheckBox.IsChecked == true &&
                PatchKillsCheckBox.IsChecked == true;

            bool safe =
                KillsOnlyCheckBox.IsChecked != true &&
                PatchNodesCheckBox.IsChecked != true &&
                PatchLinksCheckBox.IsChecked != true &&
                PatchGoodiesCheckBox.IsChecked != true &&
                PatchKillsCheckBox.IsChecked != true;

            string target = quick ? "QUICK" : safe ? "SAFE" : "CUSTOM";
            _suppressPatchPresetSync = true;
            try
            {
                foreach (var item in PatchPresetComboBox.Items.OfType<ComboBoxItem>())
                {
                    if (string.Equals(item.Tag as string, target, StringComparison.Ordinal))
                    {
                        PatchPresetComboBox.SelectedItem = item;
                        break;
                    }
                }
            }
            finally
            {
                _suppressPatchPresetSync = false;
            }

            UpdatePatchButtonState();
        }

        private void ShowAdvancedCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (AdvancedOptionsPanel == null || ShowAdvancedCheckBox == null)
                return;

            AdvancedOptionsPanel.Visibility = ShowAdvancedCheckBox.IsChecked == true
                ? Visibility.Visible
                : Visibility.Collapsed;

            if (ShowAdvancedCheckBox.IsChecked == true)
            {
                if (CareerProgressExpander != null)
                    CareerProgressExpander.IsExpanded = false;
                if (CareerSettingsExpander != null)
                    CareerSettingsExpander.IsExpanded = IsConfigurationMode;
                if (KeybindSettingsExpander != null)
                    KeybindSettingsExpander.IsExpanded = false;
            }
        }

        private bool HasMissionRankOverrides()
        {
            return _missionRankRows.Any(row => !string.Equals(row.SelectedRank, "Keep", StringComparison.OrdinalIgnoreCase));
        }

        private bool HasCategoryKillOverrides()
        {
            return _categoryKillOverrideDescriptors.Any(d => d.CheckBox?.IsChecked == true);
        }

        private bool HasConfigurationFieldOverrides()
        {
            static bool comboHasOverride(ComboBox? comboBox)
            {
                return comboBox?.SelectedItem is ComboBoxItem item &&
                       item.Tag is string tag &&
                       !string.Equals(tag, "KEEP", StringComparison.OrdinalIgnoreCase);
            }

            return OverrideSoundVolumeCheckBox?.IsChecked == true ||
                   OverrideMusicVolumeCheckBox?.IsChecked == true ||
                   comboHasOverride(InvertYP1ComboBox) ||
                   comboHasOverride(InvertYP2ComboBox) ||
                   comboHasOverride(InvertFlightP1ComboBox) ||
                   comboHasOverride(InvertFlightP2ComboBox) ||
                   comboHasOverride(ControllerVibrationP1ComboBox) ||
                   comboHasOverride(ControllerVibrationP2ComboBox) ||
                   !string.IsNullOrWhiteSpace(ControllerConfigP1TextBox?.Text) ||
                   !string.IsNullOrWhiteSpace(ControllerConfigP2TextBox?.Text);
        }

        private bool HasCopySelections()
        {
            return !string.IsNullOrWhiteSpace(NormalizeOptionalPath(CopyOptionsFromTextBox?.Text)) &&
                   (CopyOptionsEntriesCheckBox?.IsChecked == true || CopyOptionsTailCheckBox?.IsChecked == true);
        }

        private bool HasKeybindOverrides()
        {
            return _keybindOverrideDescriptors.Any(d =>
                (d.P1TextBox != null && !string.IsNullOrWhiteSpace(d.P1TextBox.Text)) ||
                (d.P2TextBox != null && !string.IsNullOrWhiteSpace(d.P2TextBox.Text)));
        }

        private bool HasSaveSectionSelections()
        {
            return !IsConfigurationMode &&
                   (KillsOnlyCheckBox?.IsChecked == true ||
                    PatchNodesCheckBox?.IsChecked == true ||
                    PatchLinksCheckBox?.IsChecked == true ||
                    PatchGoodiesCheckBox?.IsChecked == true ||
                    PatchKillsCheckBox?.IsChecked == true);
        }

        private bool HasPendingChanges()
        {
            if (IsConfigurationMode)
            {
                return HasConfigurationFieldOverrides() || HasCopySelections() || HasKeybindOverrides();
            }

            return HasSaveSectionSelections() ||
                   HasMissionRankOverrides() ||
                   HasCategoryKillOverrides() ||
                   HasConfigurationFieldOverrides() ||
                   HasCopySelections() ||
                   HasKeybindOverrides();
        }

        private string BuildPendingChangesSummary(bool hasPendingChanges)
        {
            if (!hasPendingChanges)
            {
                return IsConfigurationMode
                    ? "No pending configuration changes selected yet."
                    : "No pending save changes selected yet.";
            }

            var parts = new List<string>();
            if (!IsConfigurationMode)
            {
                if (HasSaveSectionSelections())
                    parts.Add("save sections");
                if (HasMissionRankOverrides())
                    parts.Add("mission rank overrides");
                if (HasCategoryKillOverrides())
                    parts.Add("category kill overrides");
            }

            if (HasConfigurationFieldOverrides())
                parts.Add("settings overrides");
            if (HasCopySelections())
                parts.Add("copied settings");
            if (HasKeybindOverrides())
                parts.Add("keybind overrides");

            return "Pending: " + string.Join(", ", parts) + ".";
        }

        private void UpdatePatchButtonState()
        {
            bool samePath = IsInputOutputSamePath();
            bool allowInPlaceConfigPatch = IsConfigurationMode && samePath;
            bool modePathValid = !IsConfigurationMode ||
                                 (IsOptionsLikeFilePath(InputFileTextBox.Text) &&
                                  IsOptionsLikeFilePath(OutputFileTextBox.Text));
            bool hasPendingChanges = HasPendingChanges();

            PatchButton.IsEnabled = _inputValid &&
                                   !string.IsNullOrWhiteSpace(InputFileTextBox.Text) &&
                                   !string.IsNullOrWhiteSpace(OutputFileTextBox.Text) &&
                                   _keybindOverridesValid &&
                                   hasPendingChanges &&
                                   (allowInPlaceConfigPatch || !samePath) &&
                                   modePathValid;

            if (PendingChangesText != null)
            {
                PendingChangesText.Text = BuildPendingChangesSummary(hasPendingChanges);
            }

            // Only update status if it doesn't contain a validation warning
            string currentStatus = StatusTextBox.Text;
            bool hasWarning = currentStatus.StartsWith("Warning:", StringComparison.OrdinalIgnoreCase) ||
                              currentStatus.StartsWith("Error:", StringComparison.OrdinalIgnoreCase);

            if (!hasWarning)
            {
                if (PatchButton.IsEnabled)
                {
                    StatusTextBox.Text = IsConfigurationMode ? "Ready to patch configuration." : "Ready to patch save.";
                }
                else if (!_keybindOverridesValid)
                {
                    StatusTextBox.Text = "Fix invalid keybind overrides (highlighted in red) to enable patching.";
                }
                else if (!hasPendingChanges)
                {
                    StatusTextBox.Text = IsConfigurationMode
                        ? "Choose at least one configuration override, copied setting, or keybind change to enable patching."
                        : "Choose at least one save section or advanced override to enable patching.";
                }
                else if (samePath && !IsConfigurationMode)
                {
                    StatusTextBox.Text = "Output file must be different from input file. In-place patching is blocked.";
                }
                else if (samePath && IsConfigurationMode)
                {
                    StatusTextBox.Text = "Ready to patch configuration in place. A timestamped .bak backup will be created.";
                }
                else if (!modePathValid)
                {
                    StatusTextBox.Text = "Configuration mode requires .bea input and output paths.";
                }
                else if (!string.IsNullOrWhiteSpace(InputFileTextBox.Text))
                {
                    StatusTextBox.Text = IsConfigurationMode
                        ? "Select an output .bea path to enable patching."
                        : "Select an output .bes path to enable patching.";
                }
                else
                {
                    StatusTextBox.Text = IsConfigurationMode
                        ? "Select .bea input and output files to enable patching."
                        : "Select input and output files to enable patching.";
                }
            }
        }

        private void CopyOutputButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrWhiteSpace(StatusTextBox.Text))
                {
                    Clipboard.SetText(StatusTextBox.Text);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Copy output failed: {ex.Message}");
            }
        }
    }
}
