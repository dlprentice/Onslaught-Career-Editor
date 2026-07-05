using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
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
        private bool _closeConfirmedAfterSafeCopyWarning;

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
            if (_appWindow is not null)
            {
                _appWindow.Closing += AppWindow_Closing;
            }

            Closed += MainWindow_Closed;
            RefreshFooter();
            NavigateToTag(GetInitialTag());
        }

        public void RefreshFooter()
        {
            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDirOrDetect(persistDetection: true);
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
                0 => "saves",
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
                "saves" => 0,
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

        private async void AppWindow_Closing(AppWindow sender, AppWindowClosingEventArgs args)
        {
            if (_closeConfirmedAfterSafeCopyWarning)
            {
                return;
            }

            IReadOnlyList<GameProfileRegisteredProcess> activeSafeCopies = App.SafeGameCopyProcesses.Snapshot();
            if (activeSafeCopies.Count == 0)
            {
                return;
            }

            args.Cancel = true;
            if (!await ConfirmCloseWithManagedSafeCopyAsync(activeSafeCopies.Count))
            {
                AppStatusService.SetStatus("Close canceled: copied game still running");
                return;
            }

            _closeConfirmedAfterSafeCopyWarning = true;
            Close();
        }

        private async Task<bool> ConfirmCloseWithManagedSafeCopyAsync(int processCount)
        {
            XamlRoot? root = (Content as FrameworkElement)?.XamlRoot ?? ContentFrame.XamlRoot;
            if (root is null)
            {
                return true;
            }

            string copiedGameText = processCount == 1 ? "the copied game process" : $"{processCount} copied game processes";
            ContentDialog dialog = new()
            {
                Title = "Close copied game too?",
                Content = new TextBlock
                {
                    Text = $"Closing Onslaught Toolkit will close or force-stop {copiedGameText} it launched from an app-owned safe copy. Save progress first; the installed game folder stays unchanged.",
                    TextWrapping = TextWrapping.WrapWholeWords,
                },
                PrimaryButtonText = "Close toolkit and copied game",
                CloseButtonText = "Keep running",
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = root,
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
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
