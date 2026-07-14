using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.UI;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Pages;
using Onslaught___Career_Editor;
using Windows.Graphics;
using WinRT.Interop;

namespace OnslaughtCareerEditor.WinUI
{
    public sealed partial class MainWindow : Window
    {
        private enum NavigationEntrySource
        {
            NavigationView,
            InPageAction,
            Programmatic,
        }

        private readonly Dictionary<string, NavigationViewItem> _itemByTag;
        private readonly Dictionary<string, Type> _pageByTag;
        private readonly Dictionary<Type, object> _pageCache = new();
        private readonly AppWindow? _appWindow;
        private bool _closeConfirmedAfterSafeCopyWarning;
        private bool _isSelectingNavigationItem;
        private bool _navigationInProgress;
        private int _navigationGeneration;
        private int _homeArrivalInputEpoch;
        private bool _isWindowActive;
        private CancellationTokenSource? _homeArrivalFocusCancellation;
        private string _activeTag = "home";

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
            RegisterHomeArrivalFocusTracking();
            RefreshFooter();
            NavigateToTagCore(GetInitialTag(), saveSubTab: null, NavigationEntrySource.Programmatic);
        }

        public void RefreshFooter()
        {
            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDirOrDetect(persistDetection: true) ?? config.GameDirectory;
            bool gameDirectoryReady = AppConfig.InspectGameDirectory(gameDir).Status == GameDirectoryStatus.FullInstall;
            string gameDirectoryLabel = gameDirectoryReady
                ? BuildGameDirectoryLabel(gameDir)
                : string.IsNullOrWhiteSpace(gameDir) ? "Not set" : "Needs review";
            GameDirectoryTextBlock.Text = gameDirectoryLabel;
            AutomationProperties.SetName(GameDirectoryTextBlock, $"Game folder: {gameDirectoryLabel}");
            ToolTipService.SetToolTip(
                GameDirectoryTextBlock,
                gameDirectoryReady
                    ? gameDir
                    : "Open Settings and choose the full Battle Engine Aquila install.");
            ToolTipService.SetToolTip(
                ReviewSetupButton,
                !gameDirectoryReady
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
            if (_navigationInProgress || !IsStatusVisibleForActivePage(status, _activeTag))
            {
                return;
            }

            if (DispatcherQueue.HasThreadAccess)
            {
                SetDisplayedStatus(status);
                return;
            }

            string activeTagAtQueue = _activeTag;
            DispatcherQueue.TryEnqueue(() =>
            {
                if (!_navigationInProgress &&
                    string.Equals(activeTagAtQueue, _activeTag, StringComparison.OrdinalIgnoreCase) &&
                    IsStatusVisibleForActivePage(status, _activeTag))
                {
                    SetDisplayedStatus(status);
                }
            });
        }

        private void SetDisplayedStatus(string status)
        {
            StatusTextBlock.Text = status;
            AutomationProperties.SetName(StatusTextBlock, $"Application status: {status}");
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
            if (!_isSelectingNavigationItem && args.SelectedItemContainer?.Tag is string tag)
            {
                NavigateToTagCore(tag, saveSubTab: null, NavigationEntrySource.NavigationView);
            }
        }

        public void NavigateToTag(string tag, int? saveSubTab = null)
        {
            NavigateToTagCore(tag, saveSubTab, NavigationEntrySource.InPageAction);
        }

        private void NavigateToTagCore(string tag, int? saveSubTab, NavigationEntrySource entrySource)
        {
            if (!_pageByTag.TryGetValue(tag, out Type? pageType) ||
                !_itemByTag.TryGetValue(tag, out NavigationViewItem? navItem))
            {
                return;
            }

            CancelHomeArrivalFocus();
            int navigationGeneration = ++_navigationGeneration;
            _activeTag = tag;
            _navigationInProgress = true;
            object page;
            try
            {
                if (!ReferenceEquals(ShellNavigationView.SelectedItem, navItem))
                {
                    _isSelectingNavigationItem = true;
                    try
                    {
                        ShellNavigationView.SelectedItem = navItem;
                    }
                    finally
                    {
                        _isSelectingNavigationItem = false;
                    }
                }

                page = GetOrCreatePage(pageType);
                ContentFrame.Content = page;

                if (page is HomePage homePage)
                {
                    homePage.RefreshForNavigation();
                }

                if (saveSubTab is int tabIndex && page is SavesPage savesPage)
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
            finally
            {
                _navigationInProgress = false;
            }

            AppStatusService.SetStatus(BuildPageEntryStatus(tag));
            ScheduleNavigationFocus(page, navItem, tag, saveSubTab, entrySource, navigationGeneration);
        }

        private void ScheduleNavigationFocus(
            object page,
            NavigationViewItem navItem,
            string tag,
            int? saveSubTab,
            NavigationEntrySource entrySource,
            int navigationGeneration)
        {
            if (page is not FrameworkElement pageRoot)
            {
                navItem.Focus(FocusState.Programmatic);
                return;
            }

            if (entrySource == NavigationEntrySource.Programmatic &&
                string.Equals(tag, "home", StringComparison.OrdinalIgnoreCase))
            {
                ScheduleHomeArrivalFocus(pageRoot, navItem, navigationGeneration);
                return;
            }

            void QueueFocus()
            {
                DispatcherQueue.TryEnqueue(() =>
                    MoveFocusAfterNavigationAsync(pageRoot, navItem, tag, saveSubTab, entrySource, navigationGeneration));
            }

            if (pageRoot.IsLoaded)
            {
                QueueFocus();
                return;
            }

            RoutedEventHandler? loadedHandler = null;
            loadedHandler = (_, _) =>
            {
                pageRoot.Loaded -= loadedHandler;
                QueueFocus();
            };
            pageRoot.Loaded += loadedHandler;
        }

        private void RegisterHomeArrivalFocusTracking()
        {
            Activated += MainWindow_Activated;
            if (Content is UIElement homeArrivalInputRoot)
            {
                homeArrivalInputRoot.AddHandler(
                    UIElement.PointerPressedEvent,
                    new PointerEventHandler(ShellNavigationView_UserInput),
                    handledEventsToo: true);
                homeArrivalInputRoot.AddHandler(
                    UIElement.KeyDownEvent,
                    new KeyEventHandler(ShellNavigationView_UserInput),
                    handledEventsToo: true);
            }
        }

        private void MainWindow_Activated(object sender, WindowActivatedEventArgs args)
        {
            _isWindowActive = args.WindowActivationState != WindowActivationState.Deactivated;
        }

        private void ShellNavigationView_UserInput(object sender, RoutedEventArgs args)
        {
            _homeArrivalInputEpoch++;
            CancelHomeArrivalFocus();
        }

        private void ScheduleHomeArrivalFocus(
            FrameworkElement pageRoot,
            NavigationViewItem navItem,
            int navigationGeneration)
        {
            var cancellation = new CancellationTokenSource();
            _homeArrivalFocusCancellation = cancellation;
            int inputEpoch = _homeArrivalInputEpoch;
            DependencyObject? initialFocusedElement = pageRoot.XamlRoot is null
                ? null
                : FocusManager.GetFocusedElement(pageRoot.XamlRoot) as DependencyObject;
            bool enqueued = DispatcherQueue.TryEnqueue(() =>
                MoveHomeArrivalFocusAsync(
                    pageRoot,
                    navItem,
                    navigationGeneration,
                    inputEpoch,
                    initialFocusedElement,
                    cancellation));
            if (!enqueued)
            {
                if (ReferenceEquals(_homeArrivalFocusCancellation, cancellation))
                {
                    _homeArrivalFocusCancellation = null;
                }

                cancellation.Cancel();
                cancellation.Dispose();
            }
        }

        private async void MoveHomeArrivalFocusAsync(
            FrameworkElement pageRoot,
            NavigationViewItem navItem,
            int navigationGeneration,
            int inputEpoch,
            DependencyObject? initialFocusedElement,
            CancellationTokenSource cancellation)
        {
            var focusDiagnostics = new List<HomeArrivalFocusDiagnostic>();
            try
            {
                HomeArrivalFocusPolicyOperations operations = new(
                    () => ReadHomeArrivalFocusSnapshot(
                        pageRoot,
                        navigationGeneration,
                        inputEpoch,
                        initialFocusedElement),
                    (target, token) =>
                    {
                        token.ThrowIfCancellationRequested();
                        if (FindHomeArrivalFocusTarget(pageRoot, target) is not FrameworkElement element)
                        {
                            return Task.FromResult(false);
                        }

                        return Task.FromResult(element.Focus(FocusState.Programmatic));
                    },
                    target => IsHomeArrivalFocusVerified(pageRoot, target),
                    token =>
                    {
                        token.ThrowIfCancellationRequested();
                        return Task.FromResult(navItem.Focus(FocusState.Programmatic));
                    },
                    () => IsNavigationFallbackVerified(navItem),
                    (delay, token) => Task.Delay(delay, token),
                    diagnostic => focusDiagnostics.Add(diagnostic));

                await HomeArrivalFocusPolicy.RunAsync(operations, cancellation.Token);
            }
            catch (Exception)
            {
                focusDiagnostics.Add(new HomeArrivalFocusDiagnostic(
                    "integration-exception",
                    0,
                    null,
                    HomeSetupApplicability.Pending,
                    null,
                    null,
                    null,
                    HomeArrivalFocusOutcome.ContextChanged));
            }
            finally
            {
                WriteHomeArrivalFocusDiagnostics(pageRoot, navigationGeneration, focusDiagnostics);
                if (ReferenceEquals(_homeArrivalFocusCancellation, cancellation))
                {
                    _homeArrivalFocusCancellation = null;
                }

                cancellation.Dispose();
            }
        }

        private HomeArrivalFocusSnapshot ReadHomeArrivalFocusSnapshot(
            FrameworkElement pageRoot,
            int navigationGeneration,
            int inputEpoch,
            DependencyObject? initialFocusedElement)
        {
            bool navigationCurrent = navigationGeneration == _navigationGeneration
                && inputEpoch == _homeArrivalInputEpoch
                && string.Equals(_activeTag, "home", StringComparison.OrdinalIgnoreCase)
                && ReferenceEquals(ContentFrame.Content, pageRoot);
            HomeSetupApplicability setupApplicability = ReadSetupApplicability(pageRoot);
            return new HomeArrivalFocusSnapshot(
                navigationCurrent,
                pageRoot.IsLoaded,
                _isWindowActive,
                HasToolkitUserEstablishedFocus(pageRoot, initialFocusedElement),
                setupApplicability,
                ReadHomeTargetReadiness(pageRoot, HomeFocusTarget.Setup),
                ReadHomeTargetReadiness(pageRoot, HomeFocusTarget.PatchBench),
                ReadHomeTargetReadiness(pageRoot, HomeFocusTarget.SaveLab));
        }

        private static HomeSetupApplicability ReadSetupApplicability(FrameworkElement pageRoot)
        {
            if (pageRoot.FindName("HomeSetupInfoBar") is not InfoBar setupInfoBar || setupInfoBar.XamlRoot is null)
            {
                return HomeSetupApplicability.Pending;
            }

            return setupInfoBar.IsOpen
                ? HomeSetupApplicability.Applicable
                : HomeSetupApplicability.NotApplicable;
        }

        private static HomeFocusReadiness ReadHomeTargetReadiness(
            FrameworkElement pageRoot,
            HomeFocusTarget target)
        {
            if (FindHomeArrivalFocusTarget(pageRoot, target) is not FrameworkElement element ||
                element.XamlRoot is null ||
                element.ActualWidth <= 0 ||
                element.ActualHeight <= 0)
            {
                return HomeFocusReadiness.Pending;
            }

            return element.Visibility != Visibility.Visible || element is Control { IsEnabled: false }
                ? HomeFocusReadiness.Unavailable
                : HomeFocusReadiness.Ready;
        }

        private static FrameworkElement? FindHomeArrivalFocusTarget(
            FrameworkElement pageRoot,
            HomeFocusTarget target)
        {
            string targetName = target switch
            {
                HomeFocusTarget.Setup => "HomeSetupActionButton",
                HomeFocusTarget.PatchBench => "HomeOpenPatchBenchButton",
                HomeFocusTarget.SaveLab => "HomeOpenSaveLabButton",
                _ => string.Empty,
            };
            return pageRoot.FindName(targetName) as FrameworkElement;
        }

        private static bool IsHomeArrivalFocusVerified(FrameworkElement pageRoot, HomeFocusTarget target)
        {
            FrameworkElement? expected = FindHomeArrivalFocusTarget(pageRoot, target);
            return expected?.XamlRoot is not null
                && ReferenceEquals(FocusManager.GetFocusedElement(expected.XamlRoot), expected);
        }

        private static bool IsNavigationFallbackVerified(NavigationViewItem navItem)
        {
            return navItem.XamlRoot is not null
                && ReferenceEquals(FocusManager.GetFocusedElement(navItem.XamlRoot), navItem);
        }

        private static bool HasToolkitUserEstablishedFocus(
            FrameworkElement pageRoot,
            DependencyObject? initialFocusedElement)
        {
            if (pageRoot.XamlRoot is null || FocusManager.GetFocusedElement(pageRoot.XamlRoot) is not DependencyObject focused)
            {
                return false;
            }

            if (ReferenceEquals(focused, initialFocusedElement) ||
                ReferenceEquals(focused, pageRoot) ||
                focused is NavigationViewItem or NavigationView or Frame)
            {
                return false;
            }

            return !Enum.GetValues<HomeFocusTarget>()
                .Select(target => FindHomeArrivalFocusTarget(pageRoot, target))
                .Any(target => ReferenceEquals(target, focused));
        }

        private static void WriteHomeArrivalFocusDiagnostics(
            FrameworkElement pageRoot,
            int navigationGeneration,
            IReadOnlyList<HomeArrivalFocusDiagnostic> diagnostics)
        {
            if (!string.Equals(
                    Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_FOCUS_DIAGNOSTICS"),
                    "1",
                    StringComparison.Ordinal))
            {
                return;
            }

            try
            {
                string? finalFocusedAutomationId = pageRoot.XamlRoot is null
                    ? null
                    : FocusManager.GetFocusedElement(pageRoot.XamlRoot) is DependencyObject focused
                        ? AutomationProperties.GetAutomationId(focused)
                        : null;
                IEnumerable<string> lines = diagnostics.Select(diagnostic => JsonSerializer.Serialize(new
                    {
                        ProcessId = Environment.ProcessId,
                        RunId = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_FOCUS_RUN_ID"),
                        NavigationGeneration = navigationGeneration,
                        diagnostic.Stage,
                        diagnostic.Sample,
                        Target = diagnostic.Target?.ToString(),
                        SetupApplicability = diagnostic.SetupApplicability.ToString(),
                        Readiness = diagnostic.Readiness?.ToString(),
                        diagnostic.TryFocusSucceeded,
                        diagnostic.FocusVerified,
                        Outcome = diagnostic.Outcome?.ToString(),
                        FinalXamlFocusedAutomationId = finalFocusedAutomationId,
                    }));
                File.AppendAllLines(
                    Path.Combine(AppConfig.GetConfigDir(), "home-arrival-focus.jsonl"),
                    lines);
            }
            catch
            {
                // Test-only diagnostics are best effort and must not affect focus behavior.
            }
        }

        private void CancelHomeArrivalFocus()
        {
            CancellationTokenSource? cancellation = _homeArrivalFocusCancellation;
            _homeArrivalFocusCancellation = null;
            try
            {
                cancellation?.Cancel();
            }
            catch (ObjectDisposedException)
            {
                // The completed focus operation owns disposal.
            }
        }

        private async void MoveFocusAfterNavigationAsync(
            FrameworkElement pageRoot,
            NavigationViewItem navItem,
            string tag,
            int? saveSubTab,
            NavigationEntrySource entrySource,
            int navigationGeneration)
        {
            try
            {
                if (navigationGeneration != _navigationGeneration ||
                    !ReferenceEquals(ContentFrame.Content, pageRoot))
                {
                    return;
                }

                bool focusContent = entrySource == NavigationEntrySource.InPageAction ||
                    (entrySource == NavigationEntrySource.Programmatic && string.Equals(tag, "home", StringComparison.OrdinalIgnoreCase));
                if (focusContent)
                {
                    foreach (string targetName in GetContentFocusTargetNames(pageRoot, tag, saveSubTab))
                    {
                        if (pageRoot.FindName(targetName) is not FrameworkElement target ||
                            target.XamlRoot is null ||
                            target.ActualWidth <= 0 ||
                            target.ActualHeight <= 0 ||
                            target.Visibility != Visibility.Visible ||
                            target is Control { IsEnabled: false })
                        {
                            continue;
                        }

                        FocusMovementResult result = await FocusManager.TryFocusAsync(target, FocusState.Programmatic);
                        if (navigationGeneration != _navigationGeneration ||
                            !ReferenceEquals(ContentFrame.Content, pageRoot))
                        {
                            return;
                        }

                        if (result.Succeeded)
                        {
                            return;
                        }
                    }
                }
            }
            catch
            {
                // Fall back to the selected visible navigation item below.
            }

            if (navigationGeneration == _navigationGeneration &&
                ReferenceEquals(ContentFrame.Content, pageRoot))
            {
                navItem.Focus(FocusState.Programmatic);
            }
        }

        private static IReadOnlyList<string> GetContentFocusTargetNames(
            FrameworkElement pageRoot,
            string tag,
            int? saveSubTab)
        {
            return tag.ToLowerInvariant() switch
            {
                "home" => ["HomeSetupActionButton", "HomeOpenPatchBenchButton", "HomeOpenSaveLabButton"],
                "saves" when saveSubTab == 2 => ["ConfigurationInputFileTextBox"],
                "saves" when saveSubTab == 1 => ["EditorInputFileTextBox"],
                "saves" => ["AnalyzeTaskButton"],
                "media" when MediaHandoffService.HasPendingVideoRequest => ["VideoTabButton"],
                "media" when pageRoot is MediaPage mediaPage => [mediaPage.PreferredFocusTargetName],
                "assets" => ["BrowseCatalogButton", "LoadCatalogButton"],
                "lore" => ["SearchTextBox"],
                "binary" => ["PatchBenchTopUseGameFolderButton"],
                "settings" => ["SettingsBrowseGameDirectoryButton"],
                _ => [],
            };
        }

        private static string BuildPageEntryStatus(string tag)
        {
            return tag.ToLowerInvariant() switch
            {
                "home" => "Home: choose a task",
                "saves" => "Save Lab: page ready",
                "media" => "Media: page ready",
                "assets" => "Asset Library: page ready",
                "lore" => "Lore: page ready",
                "binary" => "Windowed & Mods: page ready",
                "settings" => "Settings: page ready",
                "about" => "About: page ready",
                _ => "Ready",
            };
        }

        private static bool IsStatusVisibleForActivePage(string status, string activeTag)
        {
            string? ownerTag = GetStatusOwnerTag(status);
            return ownerTag is null || string.Equals(ownerTag, activeTag, StringComparison.OrdinalIgnoreCase);
        }

        private static string? GetStatusOwnerTag(string status)
        {
            if (status.StartsWith("Home:", StringComparison.OrdinalIgnoreCase))
            {
                return "home";
            }

            if (status.StartsWith("Save Lab:", StringComparison.OrdinalIgnoreCase) ||
                status.StartsWith("Save Analyzer:", StringComparison.OrdinalIgnoreCase) ||
                status.StartsWith("Save Editor:", StringComparison.OrdinalIgnoreCase) ||
                status.StartsWith("Game Options:", StringComparison.OrdinalIgnoreCase))
            {
                return "saves";
            }

            if (status.StartsWith("Media:", StringComparison.OrdinalIgnoreCase))
            {
                return "media";
            }

            if (status.StartsWith("Asset Library:", StringComparison.OrdinalIgnoreCase))
            {
                return "assets";
            }

            if (status.StartsWith("Lore:", StringComparison.OrdinalIgnoreCase))
            {
                return "lore";
            }

            if (status.StartsWith("Windowed & Mods:", StringComparison.OrdinalIgnoreCase))
            {
                return "binary";
            }

            if (status.StartsWith("Settings:", StringComparison.OrdinalIgnoreCase))
            {
                return "settings";
            }

            return status.StartsWith("About:", StringComparison.OrdinalIgnoreCase) ? "about" : null;
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
            CancelHomeArrivalFocus();
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
            RefreshFooter();
        }
    }
}
