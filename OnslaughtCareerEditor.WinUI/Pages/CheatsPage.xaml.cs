using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Onslaught___Career_Editor;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    /// <summary>
    /// The Cheats page.
    ///
    /// It writes no process memory and patches no executable. The released game turns its own
    /// cheats on when the save game name contains a particular word, so the whole feature is one
    /// verbatim copy of a save the player already has, under a different name. That is why it is
    /// safe, why it is reversible, and why the page can say plainly what it does.
    ///
    /// Every claim about what a cheat does comes from <see cref="CheatCodeCatalog"/> rather than
    /// from copy typed here, so a cheat cannot be described as tested when it was only read out
    /// of the executable.
    /// </summary>
    public sealed partial class CheatsPage : Page
    {
        private readonly Dictionary<string, CheckBox> _checkBoxesByCheatId;
        private IReadOnlyList<CheatSaveTarget> _safeCopyTargets = Array.Empty<CheatSaveTarget>();
        private string? _sourceSavePath;
        private string? _chosenOutputFolder;
        private bool _isRefreshingDestinations;
        private bool _isWriting;

        public CheatsPage()
        {
            InitializeComponent();

            _checkBoxesByCheatId = new Dictionary<string, CheckBox>(StringComparer.OrdinalIgnoreCase)
            {
                [CheatCodeCatalog.AllGoodiesId] = AllGoodiesCheckBox,
                [CheatCodeCatalog.AllLevelsId] = AllLevelsCheckBox,
                [CheatCodeCatalog.GodModeId] = GodModeCheckBox,
                [CheatCodeCatalog.FreeCameraId] = FreeCameraCheckBox,
                [CheatCodeCatalog.GoodieGatingBypassId] = GoodieGatingBypassCheckBox,
            };

            ApplyCatalogCopy();
            RefreshSafeCopyTargets();
            RefreshComposition();
            AppStatusService.SetStatus("Cheats: page ready");
        }

        /// <summary>
        /// Fills the effect and evidence lines from the catalog. The tick-box labels stay in XAML
        /// so they carry stable automation ids; a test pins them against the catalog names.
        /// </summary>
        private void ApplyCatalogCopy()
        {
            SetCheatCopy(CheatCodeCatalog.AllGoodiesId, AllGoodiesEffectTextBlock, AllGoodiesEvidenceTextBlock);
            SetCheatCopy(CheatCodeCatalog.AllLevelsId, AllLevelsEffectTextBlock, AllLevelsEvidenceTextBlock);
            SetCheatCopy(CheatCodeCatalog.GodModeId, GodModeEffectTextBlock, GodModeEvidenceTextBlock);
            SetCheatCopy(CheatCodeCatalog.FreeCameraId, FreeCameraEffectTextBlock, FreeCameraEvidenceTextBlock);
            SetCheatCopy(
                CheatCodeCatalog.GoodieGatingBypassId,
                GoodieGatingBypassEffectTextBlock,
                GoodieGatingBypassEvidenceTextBlock);
        }

        private void SetCheatCopy(string cheatId, TextBlock effect, TextBlock evidence)
        {
            CheatCode? cheat = CheatCodeCatalog.FindById(cheatId);
            if (cheat is null)
            {
                return;
            }

            effect.Text = cheat.WhatItDoes;
            evidence.Text = cheat.WhatWeKnow;
        }

        private IReadOnlyList<string> GetSelectedCheatIds()
        {
            return CheatCodeCatalog.All
                .Where(cheat => _checkBoxesByCheatId.TryGetValue(cheat.Id, out CheckBox? box) && box.IsChecked == true)
                .Select(cheat => cheat.Id)
                .ToArray();
        }

        private CheatSaveName BuildComposition()
        {
            return CheatSaveNameComposer.Compose(BaseNameTextBox.Text, GetSelectedCheatIds());
        }

        private string? GetDestinationDirectory()
        {
            if (DestinationComboBox.SelectedItem is ComboBoxItem { Tag: string tag } && tag.Length > 0)
            {
                return tag;
            }

            return _chosenOutputFolder;
        }

        private CheatSaveTarget? GetSelectedSafeCopy()
        {
            if (DestinationComboBox.SelectedItem is not ComboBoxItem { Tag: string tag } || tag.Length == 0)
            {
                return null;
            }

            return _safeCopyTargets.FirstOrDefault(target =>
                string.Equals(target.SavegamesDirectory, tag, StringComparison.OrdinalIgnoreCase));
        }

        private void RefreshSafeCopyTargets()
        {
            _isRefreshingDestinations = true;
            try
            {
                string? previous = GetDestinationDirectory();
                _safeCopyTargets = CheatSaveWriterService.FindSafeCopyTargets();
                DestinationComboBox.Items.Clear();

                foreach (CheatSaveTarget target in _safeCopyTargets)
                {
                    DestinationComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = target.DisplayName,
                        Tag = target.SavegamesDirectory,
                    });
                }

                if (!string.IsNullOrWhiteSpace(_chosenOutputFolder))
                {
                    DestinationComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = Path.GetFileName(Path.TrimEndingDirectorySeparator(_chosenOutputFolder)),
                        Tag = _chosenOutputFolder,
                    });
                }

                DestinationComboBox.IsEnabled = DestinationComboBox.Items.Count > 0;
                if (DestinationComboBox.Items.Count == 0)
                {
                    return;
                }

                int restored = -1;
                if (!string.IsNullOrWhiteSpace(previous))
                {
                    for (int index = 0; index < DestinationComboBox.Items.Count; index++)
                    {
                        if (DestinationComboBox.Items[index] is ComboBoxItem { Tag: string tag } &&
                            string.Equals(tag, previous, StringComparison.OrdinalIgnoreCase))
                        {
                            restored = index;
                            break;
                        }
                    }
                }

                DestinationComboBox.SelectedIndex = restored >= 0 ? restored : 0;
            }
            finally
            {
                _isRefreshingDestinations = false;
            }
        }

        private void RefreshComposition()
        {
            CheatSaveName composition = BuildComposition();
            ComposedNameTextBlock.Text = CheatsPageText.BuildNameHeadline(composition);
            ComposedNameExplanationTextBlock.Text = CheatsPageText.BuildNameExplanation(composition);
            SourceSaveTextBlock.Text = CheatsPageText.BuildSourceSummary(_sourceSavePath);
            DestinationTextBlock.Text = CheatsPageText.BuildDestinationSummary(
                GetSelectedSafeCopy(),
                GetSelectedSafeCopy() is null ? GetDestinationDirectory() : null);

            string? blocker = CheatsPageText.DescribeWhatIsStillNeeded(
                _sourceSavePath,
                composition,
                GetDestinationDirectory());
            WriteCheatSaveButton.IsEnabled = blocker is null && !_isWriting;
        }

        private void CheatSelectionChanged(object sender, RoutedEventArgs e)
        {
            RefreshComposition();
        }

        private void BaseNameTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            RefreshComposition();
        }

        private void DestinationComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isRefreshingDestinations)
            {
                return;
            }

            RefreshComposition();
        }

        private void RefreshSafeCopiesButton_Click(object sender, RoutedEventArgs e)
        {
            RefreshSafeCopyTargets();
            RefreshComposition();
            SetStatus(
                InfoBarSeverity.Informational,
                "Ready",
                _safeCopyTargets.Count == 0
                    ? "No safe copies found yet. Make one in Windowed & Mods, or pick a folder to write into."
                    : $"Found {_safeCopyTargets.Count} safe {(_safeCopyTargets.Count == 1 ? "copy" : "copies")}.");
        }

        private async void ChooseSourceSaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes" });
            if (string.IsNullOrWhiteSpace(path))
            {
                return;
            }

            string? rejection = SaveEditorService.DescribeCareerSaveInputRejection(path);
            if (rejection is not null)
            {
                _sourceSavePath = null;
                SetStatus(InfoBarSeverity.Warning, "That file will not work", rejection);
                RefreshComposition();
                return;
            }

            _sourceSavePath = path;
            SetStatus(
                InfoBarSeverity.Informational,
                "Save chosen",
                $"{Path.GetFileName(path)} will be copied exactly as it is. Nothing is written to it.");
            RefreshComposition();
        }

        private async void ChooseDestinationFolderButton_Click(object sender, RoutedEventArgs e)
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

            _chosenOutputFolder = folder;
            RefreshSafeCopyTargets();
            SelectDestination(folder);
            RefreshComposition();
        }

        private void SelectDestination(string directory)
        {
            for (int index = 0; index < DestinationComboBox.Items.Count; index++)
            {
                if (DestinationComboBox.Items[index] is ComboBoxItem { Tag: string tag } &&
                    string.Equals(tag, directory, StringComparison.OrdinalIgnoreCase))
                {
                    DestinationComboBox.SelectedIndex = index;
                    return;
                }
            }
        }

        private void OpenDebugCameraPreviewButton_Click(object sender, RoutedEventArgs e)
        {
            App.MainWindowInstance?.NavigateToTag("binary");
        }

        private async void WriteCheatSaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isWriting)
            {
                return;
            }

            CheatSaveName composition = BuildComposition();
            string? destination = GetDestinationDirectory();
            string? blocker = CheatsPageText.DescribeWhatIsStillNeeded(_sourceSavePath, composition, destination);
            if (blocker is not null)
            {
                SetStatus(InfoBarSeverity.Warning, "Not quite ready", blocker);
                return;
            }

            _isWriting = true;
            WriteCheatSaveButton.IsEnabled = false;
            try
            {
                var request = new CheatSaveWriteRequest
                {
                    InputPath = _sourceSavePath!,
                    OutputDirectory = destination!,
                    Name = composition.Name,
                };

                CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(request);
                if (!outcome.Success && outcome.NeedsOverwriteConfirmation)
                {
                    string fileName = Path.GetFileName(outcome.OutputPath ?? composition.FileName);
                    bool replace = await ConfirmAsync(
                        "Replace that save?",
                        CheatsPageText.BuildOverwriteQuestion(fileName),
                        primaryButtonText: "Replace it");
                    if (!replace)
                    {
                        SetStatus(InfoBarSeverity.Informational, "Nothing written", "Your existing save is untouched.");
                        return;
                    }

                    outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
                    {
                        InputPath = request.InputPath,
                        OutputDirectory = request.OutputDirectory,
                        Name = request.Name,
                        AllowOverwrite = true,
                    });
                }

                if (outcome.Success)
                {
                    SetStatus(InfoBarSeverity.Success, "Done", outcome.Message);
                    AppStatusService.SetStatus("Cheats: cheat save written");
                }
                else
                {
                    SetStatus(InfoBarSeverity.Warning, "Nothing written", outcome.Message);
                }
            }
            finally
            {
                _isWriting = false;
                RefreshComposition();
            }
        }

        private void SetStatus(InfoBarSeverity severity, string title, string message)
        {
            CheatsInfoBar.Severity = severity;
            CheatsInfoBar.Title = title;
            CheatsInfoBar.Message = message;
            CheatsInfoBar.IsOpen = true;
        }

        private async Task<bool> ConfirmAsync(
            string title,
            string body,
            string primaryButtonText = "Continue",
            string closeButtonText = "Cancel")
        {
            var dialog = new ContentDialog
            {
                Title = title,
                Content = new TextBlock
                {
                    Text = body,
                    TextWrapping = TextWrapping.WrapWholeWords,
                },
                PrimaryButtonText = primaryButtonText,
                CloseButtonText = closeButtonText,
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = XamlRoot,
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
        }
    }
}
