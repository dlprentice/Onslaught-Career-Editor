using System.Collections.ObjectModel;
using System.Globalization;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;
using Windows.ApplicationModel.DataTransfer;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SavesPage
    {
        private IReadOnlyList<SaveAnalyzerFileItem> _configurationDetectedFiles = Array.Empty<SaveAnalyzerFileItem>();
        private readonly ObservableCollection<ConfigurationKeybindRow> _configurationKeybindRows = new();
        private ConfigurationSnapshot? _configurationSnapshot;
        private bool _configurationInputValid;

        private void InitializeConfigurationSurface()
        {
            ConfigurationKeybindListView.ItemsSource = _configurationKeybindRows;
            ConfigurationInvertWalkerP1ComboBox.SelectedIndex = 0;
            ConfigurationInvertWalkerP2ComboBox.SelectedIndex = 0;
            ConfigurationInvertFlightP1ComboBox.SelectedIndex = 0;
            ConfigurationInvertFlightP2ComboBox.SelectedIndex = 0;
            ConfigurationVibrationP1ComboBox.SelectedIndex = 0;
            ConfigurationVibrationP2ComboBox.SelectedIndex = 0;
            ConfigurationSoundVolumeNumberBox.Value = 0.8;
            ConfigurationMusicVolumeNumberBox.Value = 0.8;
            ConfigurationCurrentSettingsTextBlock.Text = "Select a .bea file to inspect the current boot-time global settings.";
            ConfigurationCurrentTailTextBlock.Text = "Keybind and tail details will appear here after a valid options file is loaded.";
            ConfigurationOutputTextBox.Text = "Select a .bea input to begin. Game Options patches write to a separate output file by default.";
            UpdateConfigurationFieldState();
            UpdateConfigurationActionState();
        }

        private void LoadConfigurationDetectedFiles()
        {
            string selectedPath = (ConfigurationDetectedFilesComboBox.SelectedItem as SaveAnalyzerFileItem)?.Path
                ?? (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim();
            string? gameDir = AppConfig.Load().GetGameDir();
            _configurationDetectedFiles = ConfigurationEditorService.GetDetectedOptionsFiles(gameDir);
            ConfigurationDetectedFilesComboBox.ItemsSource = _configurationDetectedFiles;
            ConfigurationDetectedFilesComboBox.PlaceholderText = _configurationDetectedFiles.Count == 0
                ? "No detected options files yet"
                : "Choose an options file";
            RestoreConfigurationDetectedFileSelection(selectedPath);
            ConfigurationDetectedFilesStatusTextBlock.Text = _configurationDetectedFiles.Count == 0
                ? "No .bea options files were detected. Set the game directory in Settings or browse manually."
                : $"{_configurationDetectedFiles.Count} detected options file(s) available.";
        }

        private void RefreshConfigurationDetectedFilesButton_Click(object sender, RoutedEventArgs e)
        {
            LoadConfigurationDetectedFiles();
            AppStatusService.SetStatus($"Game Options: refreshed detected options list ({_configurationDetectedFiles.Count})");
        }

        private void RestoreConfigurationDetectedFileSelection(string? selectedPath)
        {
            if (string.IsNullOrWhiteSpace(selectedPath))
            {
                return;
            }

            SaveAnalyzerFileItem? match = _configurationDetectedFiles.FirstOrDefault(item =>
                string.Equals(item.Path, selectedPath, StringComparison.OrdinalIgnoreCase));
            if (match is not null)
            {
                ConfigurationDetectedFilesComboBox.SelectedItem = match;
            }
        }

        private void ConfigurationDetectedFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ConfigurationDetectedFilesComboBox.SelectedItem is SaveAnalyzerFileItem selected)
            {
                ConfigurationInputFileTextBox.Text = selected.Path;
                ConfigurationOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(selected.Path);
                LoadConfigurationSnapshotIfPossible();
                AppStatusService.SetStatus($"Game Options: selected {selected.Name}");
            }
        }

        private async void BrowseConfigurationInputButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bea", "*" });
                if (!string.IsNullOrWhiteSpace(path))
                {
                    ConfigurationInputFileTextBox.Text = path;
                    ConfigurationOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(path);
                    LoadConfigurationSnapshotIfPossible();
                }
            }
            catch (Exception ex)
            {
                ConfigurationOutputTextBox.Text = $"Could not browse for options file.\n{ex.Message}";
                AppStatusService.SetStatus("Game Options: browse failed");
            }
        }

        private async void BrowseConfigurationOutputButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? folder = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
                if (string.IsNullOrWhiteSpace(folder))
                {
                    return;
                }

                string inputPath = (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim();
                string fileName = SaveEditorService.IsOptionsLikeFilePath(inputPath)
                    ? Path.GetFileName(inputPath)
                    : "defaultoptions.bea";
                ConfigurationOutputFileTextBox.Text = Path.Combine(folder, string.IsNullOrWhiteSpace(fileName) ? "defaultoptions.bea" : fileName);
                UpdateConfigurationActionState();
            }
            catch (Exception ex)
            {
                ConfigurationOutputTextBox.Text = $"Could not choose output folder.\n{ex.Message}";
                AppStatusService.SetStatus("Game Options: output browse failed");
            }
        }

        private async void BrowseConfigurationCopySourceButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes", ".bea", "*" });
                if (!string.IsNullOrWhiteSpace(path))
                {
                    ConfigurationCopySourceTextBox.Text = path;
                    UpdateConfigurationActionState();
                }
            }
            catch (Exception ex)
            {
                ConfigurationOutputTextBox.Text = $"Could not browse for copy-source file.\n{ex.Message}";
                AppStatusService.SetStatus("Game Options: copy-source browse failed");
            }
        }

        private void ClearConfigurationCopySourceButton_Click(object sender, RoutedEventArgs e)
        {
            ConfigurationCopySourceTextBox.Text = string.Empty;
            ConfigurationCopyOptionsEntriesCheckBox.IsChecked = false;
            ConfigurationCopyOptionsTailCheckBox.IsChecked = false;
            UpdateConfigurationActionState();
        }

        private void ConfigurationPathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (ReferenceEquals(sender, ConfigurationInputFileTextBox) && string.IsNullOrWhiteSpace(ConfigurationOutputFileTextBox.Text))
            {
                string inputPath = (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim();
                if (SaveEditorService.IsOptionsLikeFilePath(inputPath))
                {
                    ConfigurationOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(inputPath);
                }
            }

            if (ReferenceEquals(sender, ConfigurationInputFileTextBox))
            {
                LoadConfigurationSnapshotIfPossible();
            }
            else
            {
                UpdateConfigurationActionState();
            }
        }

        private void ConfigurationCopySourceTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateConfigurationActionState();
        }

        private void ConfigurationOverrideToggle_Toggled(object sender, RoutedEventArgs e)
        {
            UpdateConfigurationFieldState();
            UpdateConfigurationActionState();
        }

        private void ConfigurationOptionSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateConfigurationActionState();
        }

        private void ConfigurationNumberBox_ValueChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
        {
            UpdateConfigurationActionState();
        }

        private void ConfigurationControllerConfigTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateConfigurationActionState();
        }

        private void ConfigurationKeybindTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateConfigurationActionState();
        }

        private void LoadConfigurationKeybindsFromInputButton_Click(object sender, RoutedEventArgs e)
        {
            if (_configurationSnapshot is null)
            {
                ConfigurationOutputTextBox.Text = "Load a valid .bea input first before copying keybind tokens into override fields.";
                return;
            }

            ConfigurationEditorService.LoadOverridesFromSnapshot(_configurationKeybindRows);
            ConfigurationOutputTextBox.Text = "Loaded keybind overrides from the current input file. Edit only the rows you want to change before patching.";
            UpdateConfigurationActionState();
        }

        private void LoadConfigurationKeybindsFromCopySourceButton_Click(object sender, RoutedEventArgs e)
        {
            string path = (ConfigurationCopySourceTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(path))
            {
                ConfigurationOutputTextBox.Text = "Select a valid copy-source file first.";
                return;
            }

            try
            {
                ApplyConfigurationKeybindOverrides(ConfigurationEditorService.LoadKeybindRowsFromFile(path));
                ConfigurationOutputTextBox.Text = "Loaded keybind overrides from the selected copy-source file.";
                UpdateConfigurationActionState();
            }
            catch (Exception ex)
            {
                ConfigurationOutputTextBox.Text = $"Error loading keybinds from copy source: {ex.Message}";
                UpdateConfigurationActionState();
            }
        }

        private void ClearConfigurationKeybindsButton_Click(object sender, RoutedEventArgs e)
        {
            ConfigurationEditorService.ClearOverrideTokens(_configurationKeybindRows);
            ConfigurationOutputTextBox.Text = "Cleared keybind overrides. Blank fields preserve the file's existing bindings.";
            UpdateConfigurationActionState();
        }

        private void ApplyConfigurationKeybindOverrides(IReadOnlyList<ConfigurationKeybindRow> sourceRows)
        {
            var lookup = sourceRows.ToDictionary(row => row.EntryId);
            foreach (ConfigurationKeybindRow target in _configurationKeybindRows)
            {
                if (lookup.TryGetValue(target.EntryId, out ConfigurationKeybindRow? source))
                {
                    target.Player1Token = source.CurrentPlayer1Token == "-" ? string.Empty : source.CurrentPlayer1Token;
                    target.Player2Token = source.CurrentPlayer2Token == "-" ? string.Empty : source.CurrentPlayer2Token;
                }
            }
        }

        private void LoadConfigurationSnapshotIfPossible()
        {
            string inputPath = (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim();
            if (inputPath.Length == 0)
            {
                _configurationInputValid = false;
                _configurationSnapshot = null;
                _configurationKeybindRows.Clear();
                ConfigurationCurrentSettingsTextBlock.Text = "Select a .bea file to inspect the current boot-time global settings.";
                ConfigurationCurrentTailTextBlock.Text = "Keybind and tail details will appear here after a valid options file is loaded.";
                UpdateConfigurationActionState();
                return;
            }

            try
            {
                _configurationSnapshot = ConfigurationEditorService.LoadConfigurationSnapshot(inputPath);
                _configurationInputValid = true;
                RenderConfigurationSnapshot(_configurationSnapshot);
                AppStatusService.SetStatus($"Game Options: loaded {Path.GetFileName(inputPath)}");
            }
            catch (Exception ex)
            {
                _configurationInputValid = false;
                _configurationSnapshot = null;
                _configurationKeybindRows.Clear();
                ConfigurationCurrentSettingsTextBlock.Text = $"Input is not ready: {ex.Message}";
                ConfigurationCurrentTailTextBlock.Text = "Game Options expects a valid .bea / defaultoptions.bea snapshot.";
                AppStatusService.SetStatus("Game Options: invalid input");
            }

            UpdateConfigurationActionState();
        }

        private void RenderConfigurationSnapshot(ConfigurationSnapshot snapshot)
        {
            ConfigurationCurrentSettingsTextBlock.Text =
                $"Current settings from {snapshot.FileName}\n" +
                $"Sound {snapshot.SoundVolume:0.00} | Music {snapshot.MusicVolume:0.00}\n" +
                $"Walker InvertY P1 {(snapshot.InvertWalkerP1 ? "On" : "Off")} | P2 {(snapshot.InvertWalkerP2 ? "On" : "Off")}\n" +
                $"Flight InvertY P1 {(snapshot.InvertFlightP1 ? "On" : "Off")} | P2 {(snapshot.InvertFlightP2 ? "On" : "Off")}\n" +
                $"Vibration P1 {(snapshot.VibrationP1 ? "On" : "Off")} | P2 {(snapshot.VibrationP2 ? "On" : "Off")}\n" +
                $"Controller config P1 {snapshot.ControllerConfigP1} | P2 {snapshot.ControllerConfigP2}";

            ConfigurationCurrentTailTextBlock.Text =
                $"Options entries {snapshot.OptionsEntryCount} | MouseSensitivity {snapshot.MouseSensitivity:0.###} | Scheme {snapshot.ControlSchemeIndex} | Lang {snapshot.LanguageIndex}\n" +
                $"ScreenShape {snapshot.ScreenShape} (0=4:3,1=16:9,2=1:1) | D3DDeviceIndex {snapshot.D3DDeviceIndex}";

            _configurationKeybindRows.Clear();
            foreach (ConfigurationKeybindRow row in snapshot.KeybindRows.Select(row => row.CloneForEditing()))
            {
                _configurationKeybindRows.Add(row);
            }
        }

        private void UpdateConfigurationFieldState()
        {
            bool soundEnabled = ConfigurationOverrideSoundVolumeToggle.IsOn;
            bool musicEnabled = ConfigurationOverrideMusicVolumeToggle.IsOn;
            ConfigurationSoundVolumeNumberBox.IsEnabled = soundEnabled;
            ConfigurationMusicVolumeNumberBox.IsEnabled = musicEnabled;
        }

        private void UpdateConfigurationActionState()
        {
            string inputPath = (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim();
            string outputPath = (ConfigurationOutputFileTextBox.Text ?? string.Empty).Trim();
            string copySourcePath = (ConfigurationCopySourceTextBox.Text ?? string.Empty).Trim();
            bool hasInput = inputPath.Length > 0;
            bool hasOutput = outputPath.Length > 0;
            bool outputIsOptionsLike = SaveEditorService.IsOptionsLikeFilePath(outputPath);
            bool copySourceSelected = copySourcePath.Length > 0;
            bool copySourcePathValid = !copySourceSelected || File.Exists(copySourcePath);
            bool copyRequested = ConfigurationCopyOptionsEntriesCheckBox.IsChecked == true || ConfigurationCopyOptionsTailCheckBox.IsChecked == true;
            bool controllerConfigValid =
                TryParseOptionalUInt(ConfigurationControllerConfigP1TextBox.Text, out _) &&
                TryParseOptionalUInt(ConfigurationControllerConfigP2TextBox.Text, out _);

            ConfigurationPatchRequest request = BuildConfigurationRequest();
            IReadOnlyList<string> keybindErrors = ConfigurationEditorService.ValidateKeybindRows(_configurationKeybindRows);
            bool hasPending = ConfigurationEditorService.HasPendingChanges(request);

            ConfigurationPendingChangesTextBlock.Text = ConfigurationEditorService.BuildPendingChangesSummary(request);
            ConfigurationKeybindHintTextBlock.Text = keybindErrors.Count == 0
                ? "Accepted tokens include keyboard keys such as Key W, arrows, numpad names, plus the retail-backed mouse tokens used by look/zoom/fire/select rows."
                : string.Join("\n", keybindErrors.Take(4)) + (keybindErrors.Count > 4 ? "\n..." : string.Empty);

            if (!_configurationInputValid && hasInput)
            {
                ConfigurationSafetyHintTextBlock.Text = "Input must be a valid .bea / defaultoptions.bea file before patching is enabled.";
            }
            else if (!hasPending)
            {
                ConfigurationSafetyHintTextBlock.Text = "Choose at least one settings override, copied options region, or keybind change.";
            }
            else if (!controllerConfigValid)
            {
                ConfigurationSafetyHintTextBlock.Text = "Controller config fields must be blank or non-negative integers.";
            }
            else if (keybindErrors.Count > 0)
            {
                ConfigurationSafetyHintTextBlock.Text = "Fix invalid keybind tokens before patching.";
            }
            else if (copyRequested && !copySourcePathValid)
            {
                ConfigurationSafetyHintTextBlock.Text = "Copy-source toggles require a valid existing .bes or .bea file.";
            }
            else if (!outputIsOptionsLike)
            {
                ConfigurationSafetyHintTextBlock.Text = "Output path must remain a .bea / defaultoptions.bea path.";
            }
            else if (AreSamePaths(inputPath, outputPath))
            {
                ConfigurationSafetyHintTextBlock.Text = "Choose a separate output .bea file. In-place options patching is blocked.";
            }
            else
            {
                ConfigurationSafetyHintTextBlock.Text = "Game options patching is ready. The source options file will not be modified.";
            }

            ConfigurationPatchButton.IsEnabled =
                _configurationInputValid &&
                hasInput &&
                hasOutput &&
                outputIsOptionsLike &&
                !AreSamePaths(inputPath, outputPath) &&
                controllerConfigValid &&
                keybindErrors.Count == 0 &&
                (!copyRequested || copySourcePathValid) &&
                hasPending;

            ConfigurationCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(ConfigurationOutputTextBox.Text);
        }

        private ConfigurationPatchRequest BuildConfigurationRequest()
        {
            TryParseOptionalUInt(ConfigurationControllerConfigP1TextBox.Text, out uint? controllerConfigP1);
            TryParseOptionalUInt(ConfigurationControllerConfigP2TextBox.Text, out uint? controllerConfigP2);

            return new ConfigurationPatchRequest
            {
                InputPath = (ConfigurationInputFileTextBox.Text ?? string.Empty).Trim(),
                OutputPath = (ConfigurationOutputFileTextBox.Text ?? string.Empty).Trim(),
                SoundVolumeOverride = ConfigurationOverrideSoundVolumeToggle.IsOn ? ClampNumberBoxToFloat(ConfigurationSoundVolumeNumberBox, 0.8f) : null,
                MusicVolumeOverride = ConfigurationOverrideMusicVolumeToggle.IsOn ? ClampNumberBoxToFloat(ConfigurationMusicVolumeNumberBox, 0.8f) : null,
                InvertWalkerP1Override = ParseTriStateBool(ConfigurationInvertWalkerP1ComboBox),
                InvertWalkerP2Override = ParseTriStateBool(ConfigurationInvertWalkerP2ComboBox),
                InvertFlightP1Override = ParseTriStateBool(ConfigurationInvertFlightP1ComboBox),
                InvertFlightP2Override = ParseTriStateBool(ConfigurationInvertFlightP2ComboBox),
                VibrationP1Override = ParseTriStateBool(ConfigurationVibrationP1ComboBox),
                VibrationP2Override = ParseTriStateBool(ConfigurationVibrationP2ComboBox),
                ControllerConfigP1Override = controllerConfigP1,
                ControllerConfigP2Override = controllerConfigP2,
                CopyOptionsFromPath = string.IsNullOrWhiteSpace(ConfigurationCopySourceTextBox.Text) ? null : ConfigurationCopySourceTextBox.Text.Trim(),
                CopyOptionsEntries = ConfigurationCopyOptionsEntriesCheckBox.IsChecked == true,
                CopyOptionsTail = ConfigurationCopyOptionsTailCheckBox.IsChecked == true,
                KeybindRows = _configurationKeybindRows.Select(row => row.CloneForEditing()).ToArray()
            };
        }

        private async void ConfigurationPatchButton_Click(object sender, RoutedEventArgs e)
        {
            ConfigurationPatchRequest? request = null;
            try
            {
                request = BuildConfigurationRequest();
                if (File.Exists(request.OutputPath) &&
                    !await ConfirmAsync(
                        "Overwrite output file?",
                        $"The output file already exists:\n{request.OutputPath}\n\nOverwrite it?"))
                {
                    AppStatusService.SetStatus("Game Options: overwrite canceled");
                    return;
                }

                ConfigurationPatchButton.IsEnabled = false;
                ConfigurationOutputTextBox.Text = "Patching game options...";
                AppStatusService.SetStatus("Game Options: patching...");

                PatchResult result = await Task.Run(() => ConfigurationEditorService.PatchConfiguration(request));
                string displayMessage = FormatConfigurationPatchResultForUi(result, request);
                ConfigurationOutputTextBox.Text = displayMessage;
                ConfigurationCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(displayMessage);
                ConfigurationInfoBar.Title = result.Success ? "Game options patch complete" : "Game options patch blocked";
                ConfigurationInfoBar.Message = displayMessage;
                ConfigurationInfoBar.Severity = result.Success ? InfoBarSeverity.Success : InfoBarSeverity.Warning;
                ConfigurationInfoBar.Visibility = Visibility.Visible;
                AppStatusService.SetStatus(result.Success ? "Game Options: patch complete" : "Game Options: patch blocked");
            }
            catch (Exception ex) when (IsUserFacingConfigurationPatchException(ex))
            {
                string detail = request is null ? ex.Message : RedactConfigurationPatchPaths(ex.Message, request);
                string message = $"Game options patch failed.\n{detail}";
                ConfigurationOutputTextBox.Text = message;
                ConfigurationCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(message);
                ConfigurationInfoBar.Title = "Game options patch failed";
                ConfigurationInfoBar.Message = message;
                ConfigurationInfoBar.Severity = InfoBarSeverity.Error;
                ConfigurationInfoBar.Visibility = Visibility.Visible;
                AppStatusService.SetStatus("Game Options: patch failed");
            }
            finally
            {
                UpdateConfigurationActionState();
            }
        }

        private static bool IsUserFacingConfigurationPatchException(Exception ex)
        {
            return ex is System.IO.IOException
                or System.UnauthorizedAccessException
                or System.ArgumentException
                or System.NotSupportedException;
        }

        private static string FormatConfigurationPatchResultForUi(PatchResult result, ConfigurationPatchRequest request)
        {
            if (result.Success)
            {
                string outputFileName = Path.GetFileName(request.OutputPath);
                if (string.IsNullOrWhiteSpace(outputFileName))
                {
                    outputFileName = "selected options file";
                }

                return
                    "Successfully patched game options to selected output file.\n" +
                    $"Output file: {outputFileName}\n" +
                    "The source options file was not modified.";
            }

            string message = string.IsNullOrWhiteSpace(result.Message)
                ? "The game options patch could not be completed."
                : RedactConfigurationPatchPaths(result.Message, request);

            return "Game options patch failed.\n" + message;
        }

        private static string RedactConfigurationPatchPaths(string message, ConfigurationPatchRequest request)
        {
            string redacted = message;
            redacted = ReplacePath(redacted, request.InputPath, "selected input options file");
            redacted = ReplacePath(redacted, request.OutputPath, "selected output options file");
            redacted = ReplacePath(redacted, request.CopyOptionsFromPath, "selected copy-source file");
            return redacted;
        }

        private static string ReplacePath(string text, string? path, string label)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return text;
            }

            return text.Replace(path.Trim(), label, StringComparison.OrdinalIgnoreCase);
        }

        private void ConfigurationCopyOutputButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(ConfigurationOutputTextBox.Text))
            {
                return;
            }

            DataPackage package = new();
            package.SetText(ConfigurationOutputTextBox.Text);
            Clipboard.SetContent(package);
            AppStatusService.SetStatus("Game Options: copied output");
        }

        private static bool? ParseTriStateBool(ComboBox comboBox)
        {
            string? tag = (comboBox.SelectedItem as ComboBoxItem)?.Tag as string;
            return tag switch
            {
                "ON" => true,
                "OFF" => false,
                _ => null
            };
        }

        private static bool TryParseOptionalUInt(string? text, out uint? value)
        {
            value = null;
            string trimmed = text?.Trim() ?? string.Empty;
            if (trimmed.Length == 0)
            {
                return true;
            }

            if (uint.TryParse(trimmed, NumberStyles.Integer, CultureInfo.InvariantCulture, out uint parsed))
            {
                value = parsed;
                return true;
            }

            return false;
        }

        private static float ClampNumberBoxToFloat(NumberBox numberBox, float fallback)
        {
            if (double.IsNaN(numberBox.Value) || double.IsInfinity(numberBox.Value))
            {
                return fallback;
            }

            return (float)Math.Max(0, Math.Min(1, numberBox.Value));
        }
    }
}
