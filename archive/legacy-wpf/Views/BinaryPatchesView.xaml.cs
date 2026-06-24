using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Binary patch surface for known-safe BEA.exe byte patches.
    /// </summary>
    public partial class BinaryPatchesView : UserControl, ILazyLoadView
    {
        private bool _isLoaded;
        private string? _verifiedSignature;

        public BinaryPatchesView()
        {
            InitializeComponent();
            Loaded += BinaryPatchesView_Loaded;
        }

        public void EnsureLoaded()
        {
            if (_isLoaded)
                return;

            _isLoaded = true;
            AutoDetectPaths();
            if (CatalogStatusTextBlock != null)
            {
                CatalogStatusTextBlock.Text = BinaryPatchEngine.CatalogStatus;
                CatalogStatusTextBlock.Foreground = BinaryPatchEngine.UsingFallbackCatalog
                    ? System.Windows.Media.Brushes.SaddleBrown
                    : System.Windows.Media.Brushes.DimGray;
            }
            UpdateControlState();
            PatchOutputTextBox.Text =
                "Select BEA.exe, choose patches, then run Verify Selected before applying.\n" +
                $"Catalog: {BinaryPatchEngine.CatalogStatus}";
        }

        private void BinaryPatchesView_Loaded(object sender, RoutedEventArgs e)
        {
            EnsureLoaded();
        }

        private void AutoDetectPaths()
        {
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            if (string.IsNullOrWhiteSpace(gameDir))
                return;

            string exePath = Path.Combine(gameDir, "BEA.exe");
            if (File.Exists(exePath))
            {
                ExePathTextBox.Text = exePath;
            }
        }

        private List<BinaryPatchSpec> GetVisibleSelectedSpecs()
        {
            var selected = new List<BinaryPatchSpec>();
            BinaryPatchSpec? resolutionSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "resolution_gate");
            BinaryPatchSpec? forceWindowedSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "force_windowed");
            BinaryPatchSpec? extraGraphicsDefaultOnSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "extra_graphics_default_on");
            BinaryPatchSpec? ignoreCardIdOverridesSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "ignore_cardid_tweak_overrides");
            BinaryPatchSpec? versionPointerSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "version_overlay_use_patched_format_pointer");
            BinaryPatchSpec? versionStringSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "version_overlay_patched_format_cave_string");
            BinaryPatchSpec? skipAutoToggleSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "skip_auto_toggle");

            if (ResolutionGatePatchCheckBox?.IsChecked == true)
            {
                if (resolutionSpec is not null)
                    selected.Add(resolutionSpec);
            }
            if (ForceWindowedPatchCheckBox?.IsChecked == true)
            {
                if (forceWindowedSpec is not null)
                    selected.Add(forceWindowedSpec);
            }
            if (ExtraGraphicsDefaultOnPatchCheckBox?.IsChecked == true)
            {
                if (extraGraphicsDefaultOnSpec is not null)
                    selected.Add(extraGraphicsDefaultOnSpec);
            }
            if (IgnoreCardIdOverridesPatchCheckBox?.IsChecked == true)
            {
                if (ignoreCardIdOverridesSpec is not null)
                    selected.Add(ignoreCardIdOverridesSpec);
            }
            if (SkipAutoTogglePatchCheckBox?.IsChecked == true)
            {
                if (skipAutoToggleSpec is not null)
                    selected.Add(skipAutoToggleSpec);
            }
            return selected;
        }

        private List<BinaryPatchSpec> GetSelectedSpecs()
        {
            var selected = GetVisibleSelectedSpecs();
            BinaryPatchSpec? versionPointerSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "version_overlay_use_patched_format_pointer");
            BinaryPatchSpec? versionStringSpec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x => x.Key == "version_overlay_patched_format_cave_string");

            // Keep runtime watermark truthful: any apply-set also tags version overlay as patched.
            if (selected.Count > 0)
            {
                if (versionPointerSpec is not null && !selected.Any(x => x.Key == versionPointerSpec.Key))
                    selected.Add(versionPointerSpec);
                if (versionStringSpec is not null && !selected.Any(x => x.Key == versionStringSpec.Key))
                    selected.Add(versionStringSpec);
            }
            return selected;
        }

        private string? BuildSelectionSignature()
        {
            string exePath = ExePathTextBox.Text?.Trim() ?? string.Empty;
            if (string.IsNullOrWhiteSpace(exePath))
                return null;

            var visibleSelected = GetVisibleSelectedSpecs();
            if (visibleSelected.Count == 0)
                return null;

            return exePath + "|" + string.Join(",", visibleSelected.Select(x => x.Key));
        }

        private void InvalidateVerification()
        {
            _verifiedSignature = null;
        }

        private string? ValidateSelection()
        {
            var visibleSelected = GetVisibleSelectedSpecs();
            if (visibleSelected.Count == 0)
                return "Select at least one patch first.";

            bool hasExperimental = visibleSelected.Any(x => string.Equals(x.Track, "Experimental", StringComparison.OrdinalIgnoreCase));
            bool hasStable = visibleSelected.Any(x => string.Equals(x.Track, "Stable", StringComparison.OrdinalIgnoreCase));
            if (hasExperimental && !hasStable)
            {
                return "Experimental startup patch should be layered on top of the stable patch set, not applied by itself.";
            }

            return null;
        }

        private bool TryGetExePath(out string exePath, bool allowMissing = false)
        {
            exePath = ExePathTextBox.Text?.Trim() ?? string.Empty;
            if (string.IsNullOrWhiteSpace(exePath) || (!allowMissing && !File.Exists(exePath)))
            {
                PatchOutputTextBox.Text = "Select a valid BEA.exe path first.";
                MainWindow.SetStatus("Binary Patches: Missing BEA.exe path");
                return false;
            }

            return true;
        }

        private void UpdateControlState()
        {
            if (ExePathTextBox == null ||
                VerifyPatchesButton == null ||
                ApplyPatchesButton == null ||
                RestoreBackupButton == null)
            {
                return;
            }

            bool hasSelected = GetVisibleSelectedSpecs().Count > 0;
            bool hasExe = File.Exists(ExePathTextBox.Text?.Trim());
            bool verifiedCurrent = string.Equals(_verifiedSignature, BuildSelectionSignature(), StringComparison.Ordinal);
            VerifyPatchesButton.IsEnabled = hasExe && hasSelected;
            ApplyPatchesButton.IsEnabled = hasExe && hasSelected && verifiedCurrent;

            string path = ExePathTextBox.Text?.Trim() ?? string.Empty;
            RestoreBackupButton.IsEnabled = !string.IsNullOrWhiteSpace(path) && File.Exists(BinaryPatchEngine.BuildBackupPath(path));
            UpdateExecutableHint(hasExe, hasSelected, verifiedCurrent);
        }

        private void UpdateExecutableHint(bool hasExe, bool hasSelected, bool verifiedCurrent)
        {
            if (ExeHintBorder == null || ExeHintTextBlock == null)
                return;

            if (!hasExe)
            {
                ExeHintBorder.Visibility = Visibility.Visible;
                ExeHintTextBlock.Text = "No BEA.exe target is currently selected. Use Game Dir to load the executable from Settings, or Browse to point at a manual install.";
                return;
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(ExePathTextBox.Text.Trim());
            string selectionState = !hasSelected
                ? "Choose at least one patch to continue."
                : verifiedCurrent
                    ? "Current selection is verified and ready to apply."
                    : "Verify Selected is required after any path or selection change.";

            ExeHintBorder.Visibility = Visibility.Visible;
            ExeHintTextBlock.Text =
                $"{selectionState} Restore rolls the executable back to the first full-file backup snapshot at {backupPath}.";
        }

        private void PatchSelectionChanged(object sender, RoutedEventArgs e)
        {
            InvalidateVerification();
            UpdateControlState();
        }

        private void BrowseExeButton_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Filter = "BEA executable (BEA.exe)|BEA.exe|Executable files (*.exe)|*.exe|All Files (*.*)|*.*",
                Title = "Select BEA.exe"
            };

            if (dialog.ShowDialog() == true)
            {
                ExePathTextBox.Text = dialog.FileName;
                InvalidateVerification();
                UpdateControlState();
                MainWindow.SetStatus("Binary Patches: Target selected");
            }
        }

        private void UseGameDirButton_Click(object sender, RoutedEventArgs e)
        {
            AutoDetectPaths();
            InvalidateVerification();
            UpdateControlState();
            MainWindow.SetStatus("Binary Patches: Loaded path from Settings game directory");
        }

        private void VerifyPatchesButton_Click(object sender, RoutedEventArgs e)
        {
            if (!TryGetExePath(out string exePath))
            {
                UpdateControlState();
                return;
            }

            string? validationError = ValidateSelection();
            if (!string.IsNullOrWhiteSpace(validationError))
            {
                PatchOutputTextBox.Text = validationError;
                MainWindow.SetStatus("Binary Patches: Selection needs review");
                UpdateControlState();
                return;
            }

            var selected = GetSelectedSpecs();
            byte[] data = File.ReadAllBytes(exePath);
            var (allKnown, allPatched, rows) = BinaryPatchEngine.VerifyPatchSpecs(data, selected);
            string summary;
            if (!allKnown)
                summary = "Verification failed: at least one patch location is in an unexpected state.";
            else if (allPatched)
                summary = "All selected patches are already applied.";
            else
                summary = "All selected patches are in original/known state and ready to apply.";

            PatchOutputTextBox.Text = BinaryPatchEngine.RenderStateReport(exePath, rows, summary);
            _verifiedSignature = allKnown ? BuildSelectionSignature() : null;
            MainWindow.SetStatus(allKnown ? "Binary Patches: Verification complete" : "Binary Patches: Verification warning");
            UpdateControlState();
        }

        private void ApplyPatchesButton_Click(object sender, RoutedEventArgs e)
        {
            if (!TryGetExePath(out string exePath))
            {
                UpdateControlState();
                return;
            }

            if (!string.Equals(_verifiedSignature, BuildSelectionSignature(), StringComparison.Ordinal))
            {
                PatchOutputTextBox.Text = "Verify Selected after your latest path/selection change before applying patches.";
                MainWindow.SetStatus("Binary Patches: Verify current selection first");
                UpdateControlState();
                return;
            }

            var selected = GetSelectedSpecs();
            var confirm = MessageBox.Show(
                "Apply the selected byte-verified patches to BEA.exe?\n\n" +
                "Notes:\n" +
                "- Restore uses the first full-file backup snapshot.\n" +
                "- Companion version watermark writes are added automatically.\n" +
                "- Verify Selected should be rerun after any later selection change.",
                "Confirm Apply Patches",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning,
                MessageBoxResult.No);

            if (confirm != MessageBoxResult.Yes)
            {
                PatchOutputTextBox.Text = "Apply canceled by user.";
                MainWindow.SetStatus("Binary Patches: Apply canceled");
                UpdateControlState();
                return;
            }

            var (success, message) = BinaryPatchEngine.ApplyPatchesToFile(exePath, selected);
            PatchOutputTextBox.Text = message;
            InvalidateVerification();
            if (!success)
                MainWindow.SetStatus("Binary Patches: Apply aborted");
            else if (message.Contains("already applied", StringComparison.OrdinalIgnoreCase))
                MainWindow.SetStatus("Binary Patches: Already patched");
            else
                MainWindow.SetStatus("Binary Patches: Apply complete");
            UpdateControlState();
        }

        private void RestoreBackupButton_Click(object sender, RoutedEventArgs e)
        {
            if (!TryGetExePath(out string exePath, allowMissing: true))
            {
                UpdateControlState();
                return;
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            if (!File.Exists(backupPath))
            {
                PatchOutputTextBox.Text = $"Backup file not found: {backupPath}";
                MainWindow.SetStatus("Binary Patches: Backup not found");
                UpdateControlState();
                return;
            }

            var confirm = MessageBox.Show(
                $"Restore {exePath} from backup?\n\nBackup:\n{backupPath}",
                "Confirm Restore Backup",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning,
                MessageBoxResult.No);

            if (confirm != MessageBoxResult.Yes)
            {
                PatchOutputTextBox.Text = "Restore canceled by user.";
                MainWindow.SetStatus("Binary Patches: Restore canceled");
                UpdateControlState();
                return;
            }

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(exePath);
            PatchOutputTextBox.Text = message;
            InvalidateVerification();
            MainWindow.SetStatus(success ? "Binary Patches: Restore complete" : "Binary Patches: Restore failed");
            UpdateControlState();
        }

    }
}
