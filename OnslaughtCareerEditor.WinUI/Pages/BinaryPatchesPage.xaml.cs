using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Models;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class BinaryPatchesPage : Page
    {
        private readonly List<BinaryPatchItemModel> _allPatchItems;
        private readonly List<BinaryPatchGroupModel> _patchGroups;
        private string? _verifiedSignature;

        public BinaryPatchesPage()
        {
            InitializeComponent();

            _allPatchItems = BinaryPatchPlanBuilder.GetVisibleSpecs()
                .Select(spec => new BinaryPatchItemModel(spec)
                {
                    IsSelected = string.Equals(spec.Track, "Stable", StringComparison.OrdinalIgnoreCase)
                })
                .ToList();
            _patchGroups = BuildPatchGroups(_allPatchItems);

            PatchGroupsItemsControl.ItemsSource = _patchGroups;

            OperationLogTextBox.Text =
                "Select BEA.exe, choose patches, verify the current selection, then apply.\n" +
                $"Catalog: {BinaryPatchEngine.CatalogStatus}";

            LoadPathFromConfig();
            UpdateControlState();
        }

        private IEnumerable<BinaryPatchItemModel> AllItems => _allPatchItems;

        private static List<BinaryPatchGroupModel> BuildPatchGroups(IEnumerable<BinaryPatchItemModel> items)
        {
            List<BinaryPatchItemModel> itemList = items.ToList();
            var groups = new List<BinaryPatchGroupModel>();

            void AddGroup(string title, string description)
            {
                List<BinaryPatchItemModel> groupItems = itemList
                    .Where(item => string.Equals(item.FunctionalArea, title, StringComparison.OrdinalIgnoreCase))
                    .ToList();
                if (groupItems.Count > 0)
                {
                    groups.Add(new BinaryPatchGroupModel(title, description, groupItems));
                }
            }

            AddGroup(
                "Display & Startup",
                "Display-mode compatibility, preferred windowed startup, and the optional fullscreen fallback all live together here.");
            AddGroup(
                "Graphics & Hardware Overrides",
                "Use these when you want the executable defaults to ignore legacy hardware gating and cardid.txt override rules.");

            return groups;
        }

        private IEnumerable<string> GetVisibleSelectedKeys()
        {
            return AllItems.Where(item => item.IsSelected).Select(item => item.Spec.Key);
        }

        private void LoadPathFromConfig()
        {
            string? gameDir = AppConfig.Load().GetGameDir();
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                return;
            }

            string candidate = Path.Combine(gameDir, "BEA.exe");
            if (File.Exists(candidate))
            {
                ExePathTextBox.Text = candidate;
            }
        }

        private void InvalidateVerification()
        {
            _verifiedSignature = null;
        }

        private void UpdateControlState()
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            bool hasExe = File.Exists(exePath);
            string[] visibleSelectedKeys = GetVisibleSelectedKeys().ToArray();
            bool hasSelected = visibleSelectedKeys.Length > 0;
            bool verifiedCurrent = string.Equals(
                _verifiedSignature,
                BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, visibleSelectedKeys),
                StringComparison.Ordinal);

            VerifyButton.IsEnabled = hasExe && hasSelected;
            ApplyButton.IsEnabled = hasExe && hasSelected && verifiedCurrent;
            RestoreButton.IsEnabled = hasExe && File.Exists(BinaryPatchEngine.BuildBackupPath(exePath));

            SelectionSummaryTextBlock.Text = hasSelected
                ? $"{visibleSelectedKeys.Length} visible patch(es) selected. Version watermark companions are added automatically at apply time."
                : "No patches selected.";

            WorkflowHintTextBlock.Text = !hasExe
                ? "Select a valid BEA.exe path to continue."
                : !hasSelected
                    ? "Choose at least one patch to continue."
                    : verifiedCurrent
                        ? "Current selection is verified and ready to apply."
                        : "Verify is required after any path or selection change.";
        }

        private void PatchCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            InvalidateVerification();
            UpdateControlState();
        }

        private void ExePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            InvalidateVerification();
            UpdateControlState();
        }

        private async void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".exe", "*" });
            if (!string.IsNullOrWhiteSpace(path))
            {
                ExePathTextBox.Text = path;
                AppStatusService.SetStatus("Binary Patches: target executable selected");
            }
        }

        private void UseGameDirButton_Click(object sender, RoutedEventArgs e)
        {
            LoadPathFromConfig();
            AppStatusService.SetStatus("Binary Patches: loaded path from shared settings");
        }

        private void VerifyButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(exePath))
            {
                OperationLogTextBox.Text = "Select a valid BEA.exe path first.";
                AppStatusService.SetStatus("Binary Patches: missing BEA.exe path");
                UpdateControlState();
                return;
            }

            string? validationError = BinaryPatchPlanBuilder.ValidateVisibleSelection(GetVisibleSelectedKeys());
            if (!string.IsNullOrWhiteSpace(validationError))
            {
                OperationLogTextBox.Text = validationError;
                AppStatusService.SetStatus("Binary Patches: selection needs review");
                UpdateControlState();
                return;
            }

            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(GetVisibleSelectedKeys());
            byte[] data = File.ReadAllBytes(exePath);
            var (allKnown, allPatched, rows) = BinaryPatchEngine.VerifyPatchSpecs(data, selected);
            string summary = !allKnown
                ? "Verification failed: at least one patch location is in an unexpected state."
                : allPatched
                    ? "All selected patches are already applied."
                    : "All selected patches are in original or known state and ready to apply.";

            OperationLogTextBox.Text = BinaryPatchEngine.RenderStateReport(exePath, rows, summary);
            _verifiedSignature = allKnown
                ? BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, GetVisibleSelectedKeys())
                : null;
            AppStatusService.SetStatus(allKnown ? "Binary Patches: verification complete" : "Binary Patches: verification warning");
            UpdateControlState();
        }

        private async void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            string? currentSignature = BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, GetVisibleSelectedKeys());
            if (!string.Equals(_verifiedSignature, currentSignature, StringComparison.Ordinal))
            {
                OperationLogTextBox.Text = "Verify the current selection before applying patches.";
                AppStatusService.SetStatus("Binary Patches: verify current selection first");
                UpdateControlState();
                return;
            }

            if (!await ConfirmAsync(
                    "Apply selected patches?",
                    "The selected byte-verified patches will be applied to BEA.exe. Restore uses the first full-file backup snapshot, not a per-patch undo."))
            {
                AppStatusService.SetStatus("Binary Patches: apply canceled");
                return;
            }

            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(GetVisibleSelectedKeys());
            var (success, message) = BinaryPatchEngine.ApplyPatchesToFile(exePath, selected);
            OperationLogTextBox.Text = message;
            InvalidateVerification();
            AppStatusService.SetStatus(success ? "Binary Patches: apply complete" : "Binary Patches: apply aborted");
            UpdateControlState();
        }

        private async void RestoreButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)))
            {
                OperationLogTextBox.Text = "Backup file not found for the selected executable.";
                AppStatusService.SetStatus("Binary Patches: backup not found");
                UpdateControlState();
                return;
            }

            if (!await ConfirmAsync(
                    "Restore backup?",
                    "The current BEA.exe will be replaced with the original full-file backup snapshot."))
            {
                AppStatusService.SetStatus("Binary Patches: restore canceled");
                return;
            }

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(exePath);
            OperationLogTextBox.Text = message;
            InvalidateVerification();
            AppStatusService.SetStatus(success ? "Binary Patches: restore complete" : "Binary Patches: restore failed");
            UpdateControlState();
        }

        private async System.Threading.Tasks.Task<bool> ConfirmAsync(string title, string body)
        {
            var dialog = new ContentDialog
            {
                Title = title,
                Content = new TextBlock
                {
                    Text = body,
                    TextWrapping = TextWrapping.WrapWholeWords
                },
                PrimaryButtonText = "Continue",
                CloseButtonText = "Cancel",
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = XamlRoot
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
        }
    }
}
