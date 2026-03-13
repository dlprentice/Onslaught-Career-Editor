using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Pages;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI
{
    public sealed partial class MainWindow : Window
    {
        private readonly Dictionary<string, NavigationViewItem> _itemByTag;
        private readonly Dictionary<string, Type> _pageByTag;
        private readonly Dictionary<Type, object> _pageCache = new();

        public MainWindow()
        {
            InitializeComponent();

            _itemByTag = new Dictionary<string, NavigationViewItem>(StringComparer.OrdinalIgnoreCase)
            {
                ["saves"] = SavesNavigationItem,
                ["media"] = MediaNavigationItem,
                ["lore"] = LoreNavigationItem,
                ["binary"] = BinaryNavigationItem,
                ["settings"] = SettingsNavigationItem,
                ["about"] = AboutNavigationItem,
            };

            _pageByTag = new Dictionary<string, Type>(StringComparer.OrdinalIgnoreCase)
            {
                ["saves"] = typeof(SavesPage),
                ["media"] = typeof(MediaPage),
                ["lore"] = typeof(LorePage),
                ["binary"] = typeof(BinaryPatchesPage),
                ["settings"] = typeof(SettingsPage),
                ["about"] = typeof(AboutPage),
            };

            AppStatusService.StatusChanged += HandleStatusChanged;
            RefreshFooter();
            NavigateToTag(GetInitialTag());
        }

        public void RefreshFooter()
        {
            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            GameDirectoryTextBlock.Text = string.IsNullOrWhiteSpace(gameDir) ? "Not set" : gameDir;
            StatusTextBlock.Text = AppStatusService.CurrentStatus;
            string? exePath = ResolveGameExecutablePath(gameDir);
            LaunchGameButton.IsEnabled = !string.IsNullOrWhiteSpace(exePath);
            ToolTipService.SetToolTip(
                LaunchGameButton,
                string.IsNullOrWhiteSpace(exePath)
                    ? "Set a valid Battle Engine Aquila game directory in Settings to launch BEA.exe."
                    : $"Launch {Path.GetFileName(exePath)} from the configured game directory.");
        }

        private void HandleStatusChanged(string status)
        {
            DispatcherQueue.TryEnqueue(() => StatusTextBlock.Text = status);
        }

        private string GetInitialTag()
        {
            int lastTab = AppConfig.Load().LastTab;
            return lastTab switch
            {
                1 => "media",
                2 => "lore",
                3 => "binary",
                4 => "settings",
                5 => "about",
                _ => "saves",
            };
        }

        private void ShellNavigationView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.SelectedItemContainer?.Tag is string tag)
            {
                NavigateToTag(tag);
            }
        }

        private void NavigateToTag(string tag)
        {
            if (!_pageByTag.TryGetValue(tag, out Type? pageType) ||
                !_itemByTag.TryGetValue(tag, out NavigationViewItem? navItem))
            {
                return;
            }

            ShellNavigationView.SelectedItem = navItem;
            ContentFrame.Content = GetOrCreatePage(pageType);

            AppConfig config = AppConfig.Load();
            config.LastTab = tag switch
            {
                "media" => 1,
                "lore" => 2,
                "binary" => 3,
                "settings" => 4,
                "about" => 5,
                _ => 0,
            };
            config.Save();
        }

        private object GetOrCreatePage(Type pageType)
        {
            if (!_pageCache.TryGetValue(pageType, out object? page))
            {
                page = Activator.CreateInstance(pageType)
                    ?? throw new InvalidOperationException($"Could not create page {pageType.FullName}.");
                _pageCache[pageType] = page;
            }

            return page;
        }

        private static string? ResolveGameExecutablePath(string? gameDir)
        {
            if (string.IsNullOrWhiteSpace(gameDir) || !Directory.Exists(gameDir))
            {
                return null;
            }

            string upper = Path.Combine(gameDir, "BEA.exe");
            if (File.Exists(upper))
            {
                return upper;
            }

            string lower = Path.Combine(gameDir, "bea.exe");
            return File.Exists(lower) ? lower : null;
        }

        private void LaunchGameButton_Click(object sender, RoutedEventArgs e)
        {
            string? gameDir = AppConfig.Load().GetGameDir();
            string? exePath = ResolveGameExecutablePath(gameDir);
            if (string.IsNullOrWhiteSpace(exePath))
            {
                AppStatusService.SetStatus("Launch Game: configure a valid BEA.exe path in Settings first");
                RefreshFooter();
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = exePath,
                    WorkingDirectory = Path.GetDirectoryName(exePath) ?? gameDir ?? string.Empty,
                    UseShellExecute = true
                });

                AppStatusService.SetStatus("Launch Game: started BEA.exe");
                RefreshFooter();
            }
            catch (Exception ex)
            {
                AppStatusService.SetStatus($"Launch Game: failed to start BEA.exe ({ex.Message})");
                RefreshFooter();
            }
        }
    }
}
