using System;
using System.Collections.Generic;
using System.IO;
using Microsoft.UI;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Pages;
using Onslaught___Career_Editor;
using Windows.Graphics;
using WinRT.Interop;

namespace OnslaughtCareerEditor.WinUI
{
    public sealed partial class MainWindow : Window
    {
        private readonly Dictionary<string, NavigationViewItem> _itemByTag;
        private readonly Dictionary<string, Type> _pageByTag;
        private readonly Dictionary<Type, object> _pageCache = new();
        private readonly AppWindow? _appWindow;

        public MainWindow()
        {
            InitializeComponent();
            _appWindow = TryGetAppWindow();
            ApplySavedWindowSize();

            _itemByTag = new Dictionary<string, NavigationViewItem>(StringComparer.OrdinalIgnoreCase)
            {
                ["home"] = HomeNavigationItem,
                ["saves"] = SavesNavigationItem,
                ["media"] = MediaNavigationItem,
                ["assets"] = AssetLibraryNavigationItem,
                ["lore"] = LoreNavigationItem,
                ["binary"] = BinaryNavigationItem,
                ["settings"] = SettingsNavigationItem,
                ["about"] = AboutNavigationItem,
            };

            _pageByTag = new Dictionary<string, Type>(StringComparer.OrdinalIgnoreCase)
            {
                ["home"] = typeof(HomePage),
                ["saves"] = typeof(SavesPage),
                ["media"] = typeof(MediaPage),
                ["assets"] = typeof(AssetLibraryPage),
                ["lore"] = typeof(LorePage),
                ["binary"] = typeof(BinaryPatchesPage),
                ["settings"] = typeof(SettingsPage),
                ["about"] = typeof(AboutPage),
            };

            AppStatusService.StatusChanged += HandleStatusChanged;
            Closed += MainWindow_Closed;
            RefreshFooter();
            NavigateToTag(GetInitialTag());
        }

        public void RefreshFooter()
        {
            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            GameDirectoryTextBlock.Text = BuildGameDirectoryLabel(gameDir);
            ToolTipService.SetToolTip(
                GameDirectoryTextBlock,
                string.IsNullOrWhiteSpace(gameDir) ? "Set the game directory in Settings." : gameDir);
            StatusTextBlock.Text = AppStatusService.CurrentStatus;
            ToolTipService.SetToolTip(
                ReviewSetupButton,
                string.IsNullOrWhiteSpace(gameDir)
                    ? "Open Settings to choose the Battle Engine Aquila install used as read-only source material."
                    : "Open Settings to review the configured install and safe app-owned workspace behavior.");
        }

        public void MaximizeForUserWorkspace()
        {
            if (_appWindow?.Presenter is OverlappedPresenter presenter)
            {
                presenter.Maximize();
            }
        }

        private void HandleStatusChanged(string status)
        {
            DispatcherQueue.TryEnqueue(() => StatusTextBlock.Text = status);
        }

        private string GetInitialTag()
        {
            string? testInitialTag = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_INITIAL_TAG");
            if (!string.IsNullOrWhiteSpace(testInitialTag) && _pageByTag.ContainsKey(testInitialTag))
            {
                return testInitialTag;
            }

            int lastTab = AppConfig.Load().LastTab;
            return lastTab switch
            {
                1 => "media",
                2 => "lore",
                3 => "binary",
                4 => "settings",
                5 => "about",
                6 => "assets",
                _ => "home",
            };
        }

        private void ShellNavigationView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.SelectedItemContainer?.Tag is string tag)
            {
                NavigateToTag(tag);
            }
        }

        public void NavigateToTag(string tag, int? saveSubTab = null)
        {
            if (!_pageByTag.TryGetValue(tag, out Type? pageType) ||
                !_itemByTag.TryGetValue(tag, out NavigationViewItem? navItem))
            {
                return;
            }

            ShellNavigationView.SelectedItem = navItem;
            ContentFrame.Content = GetOrCreatePage(pageType);

            if (saveSubTab is int tabIndex && ContentFrame.Content is SavesPage savesPage)
            {
                savesPage.NavigateToSubTab(tabIndex);
            }

            AppConfig config = AppConfig.Load();
            config.LastTab = tag switch
            {
                "home" => -1,
                "media" => 1,
                "assets" => 6,
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

        private AppWindow? TryGetAppWindow()
        {
            try
            {
                IntPtr handle = WindowNative.GetWindowHandle(this);
                WindowId windowId = Win32Interop.GetWindowIdFromWindow(handle);
                return AppWindow.GetFromWindowId(windowId);
            }
            catch
            {
                return null;
            }
        }

        private void ApplySavedWindowSize()
        {
            if (_appWindow is null)
            {
                return;
            }

            AppConfig config = AppConfig.Load();
            int width = Math.Clamp(config.WindowWidth, AppConfig.MinWindowWidth, AppConfig.MaxWindowWidth);
            int height = Math.Clamp(config.WindowHeight, AppConfig.MinWindowHeight, AppConfig.MaxWindowHeight);
            _appWindow.Resize(new SizeInt32(width, height));
        }

        private void MainWindow_Closed(object sender, WindowEventArgs args)
        {
            App.SafeGameCopyProcesses.StopAll();

            if (_appWindow is null)
            {
                return;
            }

            SizeInt32 size = _appWindow.Size;
            AppConfig config = AppConfig.Load();
            config.WindowWidth = Math.Clamp(size.Width, AppConfig.MinWindowWidth, AppConfig.MaxWindowWidth);
            config.WindowHeight = Math.Clamp(size.Height, AppConfig.MinWindowHeight, AppConfig.MaxWindowHeight);
            config.Save();
        }

        private static string BuildGameDirectoryLabel(string? gameDir)
        {
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                return "Not set";
            }

            string trimmed = gameDir.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string folderName = Path.GetFileName(trimmed);
            return string.IsNullOrWhiteSpace(folderName) ? "Configured" : folderName;
        }

        private void ReviewSetupButton_Click(object sender, RoutedEventArgs e)
        {
            NavigateToTag("settings");
            AppStatusService.SetStatus("Settings: review the read-only game install and app-owned working-copy behavior");
            RefreshFooter();
        }
    }
}
