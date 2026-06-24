using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Asset Browser tab - file-oriented browser for game assets by category/search.
    /// </summary>
    public partial class AssetBrowserView : UserControl
    {
        private static readonly HashSet<string> PreviewImageExts = new(StringComparer.OrdinalIgnoreCase)
        {
            ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"
        };

        private static readonly HashSet<string> ModelExts = new(StringComparer.OrdinalIgnoreCase)
        {
            ".fbx", ".obj", ".gltf", ".glb"
        };

        private static readonly string[] AyaExtractorExeCandidates = new[]
        {
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net10.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net9.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net8.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net7.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net6.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Release", "net10.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Release", "net9.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Release", "net8.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Release", "net7.0-windows", "AYAResourceExtractor.exe"),
            Path.Combine("references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Release", "net6.0-windows", "AYAResourceExtractor.exe"),
        };

        private readonly List<AssetRow> _allRows = new();
        private string? _rootDir;
        private string? _selectedFullPath;

        private sealed class AssetRow
        {
            public string FullPath { get; init; } = "";
            public string RelativePath { get; init; } = "";
            public string Category { get; init; } = "";
            public long SizeBytes { get; init; }
            public string SizeDisplay { get; init; } = "";
            public DateTime Modified { get; init; }
            public string ModifiedDisplay { get; init; } = "";
        }

        public AssetBrowserView()
        {
            InitializeComponent();
            CategoryFilterComboBox.SelectedIndex = 0;
            UseConfiguredGameDirectory();
        }

        private void UseConfiguredGameDirectory()
        {
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            if (!string.IsNullOrWhiteSpace(gameDir) && Directory.Exists(gameDir))
            {
                SetRootDirectory(gameDir);
            }
            else
            {
                _rootDir = null;
                RootDirTextBox.Text = "";
                _allRows.Clear();
                AssetsDataGrid.ItemsSource = null;
                SummaryTextBlock.Text = "Game directory is not configured. Set it in Settings or browse manually.";
                DetailsTextBlock.Text = "";
                PreviewTextBox.Text = "";
                PreviewImage.Source = null;
                MainWindow.SetStatus("Asset Browser: Game directory not set");
            }
        }

        private void SetRootDirectory(string path)
        {
            _rootDir = path;
            RootDirTextBox.Text = path;
            ScanAssets();
        }

        private void UseConfigButton_Click(object sender, RoutedEventArgs e)
        {
            UseConfiguredGameDirectory();
        }

        private void BrowseRootButton_Click(object sender, RoutedEventArgs e)
        {
            var folderDialog = new OpenFileDialog
            {
                Title = "Select Asset Root Directory",
                CheckFileExists = false,
                CheckPathExists = true,
                ValidateNames = false,
                FileName = "Select this folder",
                Filter = "Folders|*."
            };

            if (folderDialog.ShowDialog() == true)
            {
                string? selectedDir = Path.GetDirectoryName(folderDialog.FileName);
                if (!string.IsNullOrWhiteSpace(selectedDir) && Directory.Exists(selectedDir))
                {
                    SetRootDirectory(selectedDir);
                }
            }
        }

        private void RescanButton_Click(object sender, RoutedEventArgs e)
        {
            ScanAssets();
        }

        private static string GetExtractorOutputDefaultDir()
        {
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "Battle Engine Aquila Models");
        }

        private void UseExtractorOutputButton_Click(object sender, RoutedEventArgs e)
        {
            string outputDir = GetExtractorOutputDefaultDir();
            if (!Directory.Exists(outputDir))
            {
                MessageBox.Show(
                    "Extractor output folder was not found yet.\n\n" +
                    $"Expected:\n{outputDir}\n\n" +
                    "Run AYAResourceExtractor first, or browse to another extracted-assets folder.",
                    "AYA Integration",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information);
                return;
            }

            SetRootDirectory(outputDir);
        }

        private void CategoryFilterComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            ApplyFilters();
        }

        private void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ApplyFilters();
        }

        private void AssetsDataGrid_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (AssetsDataGrid.SelectedItem is AssetRow row)
            {
                _selectedFullPath = row.FullPath;
                DetailsTextBlock.Text = $"Selected: {row.FullPath}";
                PreviewTextBox.Text = BuildAssetDescription(row.FullPath, row.Category);
                SetPreviewImage(ResolvePreviewImagePath(row.FullPath));
            }
            else
            {
                _selectedFullPath = null;
                DetailsTextBlock.Text = "";
                PreviewTextBox.Text = "";
                PreviewImage.Source = null;
            }
        }

        private void OpenSelectedButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_selectedFullPath) || !File.Exists(_selectedFullPath))
            {
                MessageBox.Show("Select a file first.", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = _selectedFullPath,
                    UseShellExecute = true,
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Unable to open file: {ex.Message}", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void ExtractSelectedAyaButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_selectedFullPath) || !File.Exists(_selectedFullPath))
            {
                MessageBox.Show("Select a file first.", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            if (!string.Equals(Path.GetExtension(_selectedFullPath), ".aya", StringComparison.OrdinalIgnoreCase))
            {
                MessageBox.Show("Selected file is not an .aya archive.", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            string? repoRoot = FindRepoRoot();
            if (string.IsNullOrWhiteSpace(repoRoot))
            {
                MessageBox.Show("Could not resolve repo root from current runtime path.", "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            string? exePath = FindAyaExtractorExe(repoRoot);
            if (string.IsNullOrWhiteSpace(exePath))
            {
                string projectDir = Path.Combine(repoRoot, "references", "AYAResourceExtractor", "Code", "AyaResourceExtractor");
                MessageBox.Show(
                    "AYAResourceExtractor executable was not found under expected bin paths.\n\n" +
                    $"Build from:\n{projectDir}\n\n" +
                    "Then retry extraction.",
                    "AYA Integration",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information);
                return;
            }

            string outputDir = GetExtractorOutputDefaultDir();
            string? gameRoot = AppConfig.Load().GetGameDir();

            var psi = new ProcessStartInfo
            {
                FileName = exePath,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
            };
            psi.ArgumentList.Add("--extract");
            psi.ArgumentList.Add(_selectedFullPath);
            psi.ArgumentList.Add("--output");
            psi.ArgumentList.Add(outputDir);
            if (!string.IsNullOrWhiteSpace(gameRoot))
            {
                psi.ArgumentList.Add("--root");
                psi.ArgumentList.Add(gameRoot);
            }

            try
            {
                MainWindow.SetStatus("Asset Browser: Running AYA extractor for selected archive...");
                ExtractSelectedAyaButton.IsEnabled = false;

                int exitCode = -1;
                string stdout = "";
                string stderr = "";

                await Task.Run(() =>
                {
                    using var process = Process.Start(psi);
                    if (process == null)
                    {
                        throw new InvalidOperationException("Failed to start AYAResourceExtractor process.");
                    }

                    stdout = process.StandardOutput.ReadToEnd();
                    stderr = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                    exitCode = process.ExitCode;
                });

                if (exitCode != 0)
                {
                    string message = $"Extractor failed (exit code {exitCode}).";
                    if (!string.IsNullOrWhiteSpace(stderr))
                    {
                        message += "\n\n" + stderr.Trim();
                    }
                    else if (!string.IsNullOrWhiteSpace(stdout))
                    {
                        message += "\n\n" + stdout.Trim();
                    }
                    MessageBox.Show(message, "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Error);
                    MainWindow.SetStatus($"Asset Browser: Extractor failed (code {exitCode})");
                    return;
                }

                var summary = new StringBuilder();
                summary.AppendLine("Extraction completed.");
                summary.AppendLine();
                summary.AppendLine($"Output folder:");
                summary.AppendLine(outputDir);
                if (!string.IsNullOrWhiteSpace(stdout))
                {
                    summary.AppendLine();
                    summary.AppendLine(stdout.Trim());
                }

                MessageBox.Show(summary.ToString(), "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Information);

                if (Directory.Exists(outputDir))
                {
                    SetRootDirectory(outputDir);
                }

                MainWindow.SetStatus("Asset Browser: Extraction completed");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Unable to run extractor: {ex.Message}", "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Error);
                MainWindow.SetStatus("Asset Browser: Extraction failed");
            }
            finally
            {
                ExtractSelectedAyaButton.IsEnabled = true;
            }
        }

        private void OpenContainingButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_selectedFullPath) || !File.Exists(_selectedFullPath))
            {
                MessageBox.Show("Select a file first.", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = "explorer.exe",
                    Arguments = $"/select,\"{_selectedFullPath}\"",
                    UseShellExecute = true,
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Unable to open Explorer: {ex.Message}", "Asset Browser", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void OpenAyaRepoButton_Click(object sender, RoutedEventArgs e)
        {
            string? repoRoot = FindRepoRoot();
            if (string.IsNullOrWhiteSpace(repoRoot))
            {
                MessageBox.Show("Could not resolve repo root from current runtime path.", "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            string ayaRepo = Path.Combine(repoRoot, "references", "AYAResourceExtractor");
            if (!Directory.Exists(ayaRepo))
            {
                MessageBox.Show($"AYAResourceExtractor folder not found:\n{ayaRepo}", "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = $"\"{ayaRepo}\"",
                UseShellExecute = true,
            });
        }

        private void LaunchAyaExtractorButton_Click(object sender, RoutedEventArgs e)
        {
            string? repoRoot = FindRepoRoot();
            if (string.IsNullOrWhiteSpace(repoRoot))
            {
                MessageBox.Show("Could not resolve repo root from current runtime path.", "AYA Integration", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            string? exePath = FindAyaExtractorExe(repoRoot);
            if (string.IsNullOrWhiteSpace(exePath))
            {
                string projectDir = Path.Combine(repoRoot, "references", "AYAResourceExtractor", "Code", "AyaResourceExtractor");
                MessageBox.Show(
                    "AYAResourceExtractor executable was not found under expected bin paths.\n\n" +
                    $"Build from:\n{projectDir}\n\n" +
                    "Then click 'Launch Extractor' again.",
                    "AYA Integration",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information);
                return;
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = exePath,
                UseShellExecute = true,
            });
        }

        private void ScanAssets()
        {
            if (string.IsNullOrWhiteSpace(_rootDir) || !Directory.Exists(_rootDir))
            {
                SummaryTextBlock.Text = "Set a valid root directory before scanning.";
                _allRows.Clear();
                AssetsDataGrid.ItemsSource = null;
                return;
            }

            MainWindow.SetStatus("Asset Browser: Scanning files...");

            var rows = new List<AssetRow>();
            foreach (var file in EnumerateFilesSafe(_rootDir))
            {
                try
                {
                    var info = new FileInfo(file);
                    rows.Add(new AssetRow
                    {
                        FullPath = file,
                        RelativePath = Path.GetRelativePath(_rootDir, file),
                        Category = ClassifyCategory(file),
                        SizeBytes = info.Length,
                        SizeDisplay = FormatSize(info.Length),
                        Modified = info.LastWriteTime,
                        ModifiedDisplay = info.LastWriteTime.ToString("yyyy-MM-dd HH:mm"),
                    });
                }
                catch (IOException)
                {
                    // Skip inaccessible files
                }
                catch (UnauthorizedAccessException)
                {
                    // Skip inaccessible files
                }
            }

            _allRows.Clear();
            _allRows.AddRange(rows.OrderBy(r => r.RelativePath, StringComparer.OrdinalIgnoreCase));
            ApplyFilters();
            MainWindow.SetStatus($"Asset Browser: Loaded {_allRows.Count:N0} file(s)");
        }

        private static IEnumerable<string> EnumerateFilesSafe(string rootDir)
        {
            var pending = new Stack<string>();
            pending.Push(rootDir);

            while (pending.Count > 0)
            {
                var current = pending.Pop();
                IEnumerable<string> dirs;
                IEnumerable<string> files;

                try
                {
                    dirs = Directory.EnumerateDirectories(current);
                }
                catch
                {
                    continue;
                }

                foreach (var dir in dirs)
                {
                    pending.Push(dir);
                }

                try
                {
                    files = Directory.EnumerateFiles(current);
                }
                catch
                {
                    continue;
                }

                foreach (var file in files)
                {
                    yield return file;
                }
            }
        }

        private void ApplyFilters()
        {
            string category = (CategoryFilterComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString() ?? "All";
            string search = (SearchTextBox.Text ?? string.Empty).Trim();

            var filtered = _allRows.Where(row =>
                (string.Equals(category, "All", StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(row.Category, category, StringComparison.OrdinalIgnoreCase)) &&
                (string.IsNullOrWhiteSpace(search) ||
                 row.RelativePath.Contains(search, StringComparison.OrdinalIgnoreCase)))
                .ToList();

            AssetsDataGrid.ItemsSource = filtered;

            if (string.IsNullOrWhiteSpace(_rootDir))
            {
                SummaryTextBlock.Text = "Set a root directory to browse assets.";
            }
            else
            {
                SummaryTextBlock.Text =
                    $"Root: {_rootDir} | Showing {filtered.Count:N0} of {_allRows.Count:N0} files. " +
                    "Categories include AYA archives, media, saves/options, and text/data files.";
            }

            _selectedFullPath = null;
            DetailsTextBlock.Text = "";
            PreviewTextBox.Text = "";
            PreviewImage.Source = null;
        }

        private static string BuildAssetDescription(string fullPath, string category)
        {
            string ext = Path.GetExtension(fullPath).ToLowerInvariant();
            string lower = fullPath.ToLowerInvariant();

            var hints = new List<string>();
            if (string.Equals(ext, ".aya", StringComparison.OrdinalIgnoreCase))
            {
                if (lower.Contains(@"\data\resources\meshes\") || lower.Contains("/data/resources/meshes/"))
                {
                    hints.Add("Likely compressed model archive from data/resources/meshes.");
                }
                else if (lower.Contains(@"\data\resources\dxtntextures\") || lower.Contains("/data/resources/dxtntextures/"))
                {
                    hints.Add("Likely compressed texture archive from data/resources/dxtntextures.");
                }
                hints.Add("Use 'Extract Selected AYA' for one-click extraction, or 'Launch Extractor' for batch/manual runs.");
            }
            else if (ModelExts.Contains(ext))
            {
                hints.Add("Extracted model file. Open with Blender or Windows 3D Viewer.");
            }
            else if (PreviewImageExts.Contains(ext))
            {
                hints.Add("Texture/image asset previewed inline.");
            }
            else if (string.Equals(ext, ".bea", StringComparison.OrdinalIgnoreCase) ||
                     string.Equals(ext, ".bes", StringComparison.OrdinalIgnoreCase))
            {
                if (Path.GetFileName(fullPath).StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase))
                {
                    hints.Add("Global options snapshot loaded at boot in the Steam build.");
                }
                else
                {
                    hints.Add("Career/options save buffer (10,004 bytes expected).");
                }
            }

            string hintText = hints.Count > 0
                ? string.Join(Environment.NewLine, hints)
                : "No specialized hint for this asset type.";

            return
                $"Type: {category}{Environment.NewLine}" +
                $"Name: {Path.GetFileName(fullPath)}{Environment.NewLine}" +
                $"Extension: {(string.IsNullOrWhiteSpace(ext) ? "(none)" : ext)}{Environment.NewLine}" +
                hintText;
        }

        private static string? ResolvePreviewImagePath(string fullPath)
        {
            string ext = Path.GetExtension(fullPath).ToLowerInvariant();
            if (PreviewImageExts.Contains(ext) && File.Exists(fullPath))
            {
                return fullPath;
            }

            string stem = Path.GetFileNameWithoutExtension(fullPath);
            string parent = Path.GetDirectoryName(fullPath) ?? "";
            string grandParent = Directory.GetParent(parent)?.FullName ?? "";

            var candidates = new[]
            {
                Path.Combine(parent, "MeshTextures", stem + ".png"),
                Path.Combine(parent, "MeshTextures", stem.ToLowerInvariant() + ".png"),
                Path.Combine(grandParent, "MeshTextures", stem + ".png"),
                Path.Combine(grandParent, "MeshTextures", stem.ToLowerInvariant() + ".png"),
            };

            foreach (string candidate in candidates)
            {
                if (File.Exists(candidate))
                {
                    return candidate;
                }
            }

            return null;
        }

        private void SetPreviewImage(string? imagePath)
        {
            if (string.IsNullOrWhiteSpace(imagePath) || !File.Exists(imagePath))
            {
                PreviewImage.Source = null;
                return;
            }

            try
            {
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                bmp.UriSource = new Uri(imagePath);
                bmp.EndInit();
                bmp.Freeze();
                PreviewImage.Source = bmp;
            }
            catch
            {
                PreviewImage.Source = null;
            }
        }

        private static string ClassifyCategory(string filePath)
        {
            string ext = Path.GetExtension(filePath).ToLowerInvariant();

            return ext switch
            {
                ".aya" => "AYA Archives",
                ".vid" or ".bik" or ".avi" or ".wmv" or ".mp4" => "Video",
                ".wav" or ".ogg" or ".mp3" or ".wma" => "Audio",
                ".bes" or ".bea" => "Saves/Options",
                ".txt" or ".md" or ".ini" or ".cfg" or ".dat" or ".json" or ".xml" or ".csv" or ".tsv" => "Text/Data",
                _ => "Other"
            };
        }

        private static string FormatSize(long size)
        {
            if (size < 1024)
                return $"{size} B";
            if (size < 1024 * 1024)
                return $"{size / 1024.0:0.0} KB";
            if (size < 1024L * 1024 * 1024)
                return $"{size / (1024.0 * 1024.0):0.0} MB";
            return $"{size / (1024.0 * 1024.0 * 1024.0):0.00} GB";
        }

        private static string? FindRepoRoot()
        {
            var dir = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            int depth = 0;
            while (dir != null && depth < 12)
            {
                string candidate = Path.Combine(dir.FullName, "references", "AYAResourceExtractor");
                if (Directory.Exists(candidate))
                    return dir.FullName;

                dir = dir.Parent;
                depth++;
            }
            return null;
        }

        private static string? FindAyaExtractorExe(string repoRoot)
        {
            foreach (var rel in AyaExtractorExeCandidates)
            {
                string candidate = Path.Combine(repoRoot, rel);
                if (File.Exists(candidate))
                    return candidate;
            }
            return null;
        }
    }
}
