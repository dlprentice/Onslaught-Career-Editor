using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Windows.Foundation;
using Windows.System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class LorePage : Page
    {
        private const string LoreLibraryLoadFailureMessage = "The offline Lore library could not be loaded. Refresh the library or reinstall the app package if this keeps happening.";
        private const string LoreHistoryFailureMessage = "That Lore history entry could not be reopened. Refresh the library and try again.";
        private const string LoreHomeFailureMessage = "The Lore home document could not be opened. Refresh the library and try again.";
        private const string LoreExternalOpenFailureMessage = "That Lore document could not be handed to your browser. Try again once the library has finished loading.";

        private readonly LoreBrowserService _service = new();
        private readonly LoreSearchService _searchService;
        private readonly Dictionary<string, LoreDocument> _documentLookup = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, TreeViewNode> _nodeByKey = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, TreeViewNode> _nodeByPath = new(StringComparer.OrdinalIgnoreCase);
        private readonly Stack<LoreHistoryEntry> _backStack = new();
        private readonly Stack<LoreHistoryEntry> _forwardStack = new();

        private LoreIndex? _index;
        private IReadOnlyDictionary<string, FrameworkElement> _anchorTargets =
            new Dictionary<string, FrameworkElement>(StringComparer.OrdinalIgnoreCase);
        private string? _currentSourcePath;
        private string? _currentAnchor;
        private bool _hasLoaded;
        private bool _isLoading;
        private bool _isDocumentLoading;
        private bool _suppressHistory;
        private bool _suppressTreeSelection;
        private CancellationTokenSource? _searchFilterCancellation;
        private LoreBacklinkIndex? _backlinkIndex;
        private double _readerTextScale = 1.0;

        public LorePage()
        {
            InitializeComponent();
            _searchService = new LoreSearchService(_service);
            Loaded += LorePage_Loaded;
            UpdateNavButtons();
            UpdateLibraryToggleButton();
            ShowReaderPlaceholder(
                "Loading lore library...",
                "The reader will appear here once the library is ready.");
        }

        private async void LorePage_Loaded(object sender, RoutedEventArgs e)
        {
            if (_hasLoaded)
            {
                return;
            }

            _hasLoaded = true;

            // Page load runs on an async void handler, so an escaping exception
            // would take the process down rather than the page. Everything below
            // degrades to the placeholder instead.
            try
            {
                await LoadLoreIndexAsync(preserveCurrentDocument: false);
            }
            catch
            {
                ShowReaderPlaceholder("Lore library unavailable", LoreLibraryLoadFailureMessage);
                AppStatusService.SetStatus("Lore: load failed");
            }
        }

        private async Task LoadLoreIndexAsync(bool preserveCurrentDocument)
        {
            if (_isLoading)
            {
                return;
            }

            _isLoading = true;
            CancelPendingSearchFilter();
            ShowReaderPlaceholder(
                "Loading lore library...",
                "Refreshing the offline document tree and reader.");
            LibrarySummaryTextBlock.Text = "Loading lore library...";
            LibraryCountTextBlock.Text = "Indexing included documents...";
            PaneStateTextBlock.Text = "Indexing included documents...";
            AppStatusService.SetStatus("Lore: loading library");

            string? restorePath = preserveCurrentDocument ? _currentSourcePath : null;
            string? restoreAnchor = preserveCurrentDocument ? _currentAnchor : null;

            try
            {
                _index = await Task.Run(() => _service.LoadIndex());

                _documentLookup.Clear();
                foreach (LoreDocument document in _index.Documents)
                {
                    _documentLookup[document.FilePath] = document;
                }

                try
                {
                    _backlinkIndex = await Task.Run(() => _searchService.BuildBacklinkIndex(_index));
                }
                catch
                {
                    // Cross-links are depth on top of a working library; a failure to
                    // build them must not fail the load. The expander says so itself.
                    _backlinkIndex = null;
                }

                LibrarySummaryTextBlock.Text = _index.UsingContentPack
                    ? "Offline Lore library ready."
                    : _index.UsingLoreBook
                        ? "Offline Lore entry guide ready."
                        : "Repository Lore library ready.";

                ApplyTreeFilter(updateSelection: false);

                string? initialPath = restorePath;
                string? initialAnchor = restoreAnchor;
                if (string.IsNullOrWhiteSpace(initialPath) || (!_documentLookup.ContainsKey(initialPath) && !_service.DocumentExists(initialPath)))
                {
                    initialPath = _index.HomeDocument?.FilePath;
                    initialAnchor = null;
                }

                if (!string.IsNullOrWhiteSpace(initialPath))
                {
                    _suppressHistory = true;
                    await LoadDocumentAsync(initialPath, initialAnchor, addToHistory: false);
                    _suppressHistory = false;
                }
                else
                {
                    CurrentDocumentTextBlock.Text = LorePageText.EmptyLibraryNextStep;
                    CurrentPathTextBlock.Text = LorePageText.EmptyLibraryNextStep;
                    ShowReaderPlaceholder(
                        LorePageText.EmptyLibraryNextStep,
                        LorePageText.EmptyLibraryNextStep);
                }

                UpdateCounts();
                UpdateNavButtons();
                AppStatusService.SetStatus($"Lore: {_index.Documents.Count} documents ready");
            }
            catch
            {
                _index = null;
                _documentLookup.Clear();
                DocumentTree.RootNodes.Clear();
                CurrentDocumentTextBlock.Text = "Lore library unavailable";
                CurrentPathTextBlock.Text = LoreLibraryLoadFailureMessage;
                LibrarySummaryTextBlock.Text = "Lore load failed";
                LibraryCountTextBlock.Text = "Reader unavailable.";
                PaneStateTextBlock.Text = LoreLibraryLoadFailureMessage;
                ShowReaderPlaceholder("Lore library unavailable", LoreLibraryLoadFailureMessage);
                AppStatusService.SetStatus("Lore: load failed");
            }
            finally
            {
                _isLoading = false;
                _suppressHistory = false;
            }
        }

        private void ApplyTreeFilter(bool updateSelection = true)
        {
            if (_index == null)
            {
                DocumentTree.RootNodes.Clear();
                UpdateCounts();
                return;
            }

            string query = (SearchTextBox.Text ?? string.Empty).Trim();
            IReadOnlyList<LoreTreeItem> sourceItems = string.IsNullOrWhiteSpace(query)
                ? _index.RootItems
                : _service.FilterTree(_index.RootItems, query);

            ApplyTreeFilterItems(sourceItems, query, updateSelection);
        }

        private async Task ApplyTreeFilterAsync(bool updateSelection, CancellationToken cancellationToken)
        {
            if (_index == null)
            {
                DocumentTree.RootNodes.Clear();
                UpdateCounts();
                return;
            }

            string query = (SearchTextBox.Text ?? string.Empty).Trim();
            IReadOnlyList<LoreTreeItem> sourceItems = string.IsNullOrWhiteSpace(query)
                ? _index.RootItems
                : await Task.Run(() => _service.FilterTree(_index.RootItems, query), cancellationToken);

            cancellationToken.ThrowIfCancellationRequested();
            ApplyTreeFilterItems(sourceItems, query, updateSelection);
        }

        private void ApplyTreeFilterItems(IReadOnlyList<LoreTreeItem> sourceItems, string query, bool updateSelection)
        {
            HashSet<string> expandedKeys = CaptureExpandedKeys();
            RebuildTree(sourceItems, expandedKeys, expandAll: !string.IsNullOrWhiteSpace(query));

            if (updateSelection)
            {
                SyncTreeSelection(_currentSourcePath);
            }

            UpdateCounts();
        }

        private void RebuildTree(IReadOnlyList<LoreTreeItem> items, HashSet<string> expandedKeys, bool expandAll)
        {
            _nodeByKey.Clear();
            _nodeByPath.Clear();
            DocumentTree.RootNodes.Clear();

            for (int index = 0; index < items.Count; index++)
            {
                TreeViewNode node = BuildTreeNode(items[index], parentKey: null, index, expandedKeys, expandAll);
                DocumentTree.RootNodes.Add(node);
            }
        }

        private TreeViewNode BuildTreeNode(LoreTreeItem item, string? parentKey, int index, HashSet<string> expandedKeys, bool expandAll)
        {
            string key = BuildNodeKey(item, parentKey, index);
            LoreTreeNodeTag tag = new(item.Title, item.FilePath, item.RelativePath, key);
            TreeViewNode node = new()
            {
                Content = tag,
                IsExpanded = expandAll || expandedKeys.Contains(key)
            };

            _nodeByKey[key] = node;
            if (!string.IsNullOrWhiteSpace(item.FilePath))
            {
                _nodeByPath[item.FilePath] = node;
            }

            for (int childIndex = 0; childIndex < item.Children.Count; childIndex++)
            {
                node.Children.Add(BuildTreeNode(item.Children[childIndex], key, childIndex, expandedKeys, expandAll));
            }

            return node;
        }

        private void SyncTreeSelection(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath) || !_nodeByPath.TryGetValue(filePath, out TreeViewNode? node))
            {
                return;
            }

            TreeViewNode? ancestor = node.Parent;
            while (ancestor != null)
            {
                ancestor.IsExpanded = true;
                ancestor = ancestor.Parent;
            }

            _suppressTreeSelection = true;
            DocumentTree.SelectedNode = node;
            _suppressTreeSelection = false;
        }

        private HashSet<string> CaptureExpandedKeys()
        {
            HashSet<string> keys = new(StringComparer.OrdinalIgnoreCase);
            foreach (TreeViewNode node in DocumentTree.RootNodes)
            {
                CaptureExpandedKeys(node, keys);
            }

            return keys;
        }

        private void CaptureExpandedKeys(TreeViewNode node, HashSet<string> keys)
        {
            if (node.IsExpanded && node.Content is LoreTreeNodeTag tag)
            {
                keys.Add(tag.Key);
            }

            foreach (TreeViewNode child in node.Children)
            {
                CaptureExpandedKeys(child, keys);
            }
        }

        private async Task LoadDocumentAsync(string filePath, string? anchor, bool addToHistory)
        {
            string documentKey = _service.NormalizeDocumentKey(filePath);
            if (!_service.DocumentExists(documentKey))
            {
                throw new FileNotFoundException(LorePageText.DocumentLoadFailed);
            }

            if (addToHistory && !_suppressHistory && !string.IsNullOrWhiteSpace(_currentSourcePath))
            {
                if (!PathsEqual(_currentSourcePath, documentKey) || !string.Equals(_currentAnchor, anchor, StringComparison.Ordinal))
                {
                    _backStack.Push(new LoreHistoryEntry(_currentSourcePath!, _currentAnchor));
                    _forwardStack.Clear();
                }
            }

            LoreDocumentContent content = await Task.Run(() => _service.LoadDocumentContent(documentKey));

            _currentSourcePath = content.SourcePath;
            _currentAnchor = anchor;

            CurrentDocumentTextBlock.Text = ResolveDocumentTitle(content.SourcePath, content.Title);
            CurrentPathTextBlock.Text = ResolveDisplayPath(content.SourcePath);
            ToolTipService.SetToolTip(CurrentPathTextBlock, ResolveToolTipPath(content.SourcePath));

            RenderCurrentDocument(content);
            ApplyReaderTextScale();
            ScrollToAnchor(anchor);

            RefreshBacklinks(content.SourcePath);
            RefreshOutline(content);
            RefreshOutgoing(content.SourcePath);
            SyncTreeSelection(content.SourcePath);
            UpdateNavButtons();
            AppStatusService.SetStatus($"Lore: loaded {CurrentDocumentTextBlock.Text}");
        }

        private void RenderCurrentDocument(LoreDocumentContent content)
        {
            LoreRenderedDocument rendered = LoreDocumentRenderer.Render(
                content.Document,
                ResolveImageBaseDirectory(content.SourcePath),
                OnLoreLinkActivated,
                _readerTextScale);

            _anchorTargets = rendered.Anchors;
            ContentReader.Content = rendered.Root;

            if (content.Document.Blocks.Count == 0)
            {
                // A blank reader panel is exactly the failure this page was
                // rebuilt to eliminate; say so rather than painting nothing.
                ShowReaderPlaceholder(
                    LorePageText.EmptyLibraryNextStep,
                    LorePageText.EmptyLibraryNextStep);
                return;
            }

            ReaderPlaceholderBorder.Visibility = Visibility.Collapsed;
            ReaderScrollViewer.Visibility = Visibility.Visible;
        }

        private static string? ResolveImageBaseDirectory(string sourcePath)
        {
            if (IsLorePackSourcePath(sourcePath))
            {
                return null;
            }

            try
            {
                return Path.GetDirectoryName(sourcePath);
            }
            catch
            {
                return null;
            }
        }

        private void ScrollToAnchor(string? anchor)
        {
            if (string.IsNullOrWhiteSpace(anchor))
            {
                ReaderScrollViewer.ChangeView(null, 0, null, true);
                return;
            }

            ApplyAnchorScroll(anchor);

            // A freshly swapped document has not necessarily finished arranging,
            // so retry once the layout pass has run.
            DispatcherQueue.TryEnqueue(
                Microsoft.UI.Dispatching.DispatcherQueuePriority.Low,
                () => ApplyAnchorScroll(anchor));
        }

        private void ApplyAnchorScroll(string anchor)
        {
            if (!_anchorTargets.TryGetValue(anchor, out FrameworkElement? target))
            {
                return;
            }

            try
            {
                ReaderScrollViewer.UpdateLayout();
                GeneralTransform transform = target.TransformToVisual(ContentReader);
                Point offset = transform.TransformPoint(new Point(0, 0));
                ReaderScrollViewer.ChangeView(null, Math.Max(0, offset.Y), null, true);
            }
            catch
            {
                // A transform can fail while the element is detached; leaving the
                // reader where it is beats tearing the page down.
            }
        }

        private async void OnLoreLinkActivated(string target)
        {
            try
            {
                await HandleLinkActivationAsync(target);
            }
            catch
            {
                ShowReaderPlaceholder("Could not navigate link", LorePageText.LinkOpenFailed);
                AppStatusService.SetStatus("Lore: navigation failed");
            }
        }

        private async Task HandleLinkActivationAsync(string target)
        {
            if (string.IsNullOrWhiteSpace(target))
            {
                AppStatusService.SetStatus("Lore: unresolved internal link");
                return;
            }

            LoreLinkKind kind = LoreDocumentParser.ClassifyLink(target);
            if (kind is LoreLinkKind.External or LoreLinkKind.Source)
            {
                await Launcher.LaunchUriAsync(new Uri(target.Trim()));
                AppStatusService.SetStatus(kind == LoreLinkKind.Source
                    ? "Lore: opened source link in browser"
                    : "Lore: opened external link in browser");
                return;
            }

            bool handled = await TryHandleInternalNavigationAsync(target);
            if (!handled)
            {
                AppStatusService.SetStatus("Lore: unresolved internal link");
            }
        }

        private async Task<bool> TryHandleInternalNavigationAsync(string uri)
        {
            if (string.IsNullOrWhiteSpace(_currentSourcePath))
            {
                return false;
            }

            string? anchor = LoreBrowserService.ExtractAnchor(uri);
            if (uri.TrimStart().StartsWith("#", StringComparison.Ordinal))
            {
                NavigateToCurrentAnchor(anchor);
                return true;
            }

            string? localPath = TryGetLocalPath(uri);
            if (!string.IsNullOrWhiteSpace(localPath) && PathsEqual(localPath, _currentSourcePath))
            {
                NavigateToCurrentAnchor(anchor);
                return true;
            }

            string? targetPath = _service.ResolveInternalTarget(_currentSourcePath, uri);
            if (string.IsNullOrWhiteSpace(targetPath))
            {
                return false;
            }

            string fullTarget = _service.NormalizeDocumentKey(targetPath);
            if (PathsEqual(fullTarget, _currentSourcePath))
            {
                NavigateToCurrentAnchor(anchor);
                return true;
            }

            string extension = Path.GetExtension(fullTarget);
            if (IsLorePackSourcePath(fullTarget) ||
                extension.Equals(".md", StringComparison.OrdinalIgnoreCase) ||
                extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
            {
                await LoadDocumentAsync(fullTarget, anchor, addToHistory: true);
                return true;
            }

            if (File.Exists(fullTarget))
            {
                await Launcher.LaunchUriAsync(new Uri(fullTarget));
                AppStatusService.SetStatus("Lore: opened attachment externally");
                return true;
            }

            return false;
        }

        private void NavigateToCurrentAnchor(string? anchor)
        {
            _currentAnchor = anchor;
            ScrollToAnchor(anchor);

            if (!string.IsNullOrWhiteSpace(_currentSourcePath))
            {
                AppStatusService.SetStatus($"Lore: loaded {CurrentDocumentTextBlock.Text}");
            }
        }

        private async void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            CancelPendingSearchFilter();
            _searchFilterCancellation = new CancellationTokenSource();
            CancellationToken cancellationToken = _searchFilterCancellation.Token;

            try
            {
                await Task.Delay(180, cancellationToken);
                await ApplyTreeFilterAsync(updateSelection: true, cancellationToken);
                await ApplySearchHitsAsync(cancellationToken);
            }
            catch (OperationCanceledException)
            {
            }
        }

        /// <summary>
        /// Full-text matches for the current query, shown with snippets under the
        /// tree. Runs after the tree filter on the same cancellation token so typing
        /// stays responsive; a failure degrades the panel, never the library.
        /// </summary>
        private async Task ApplySearchHitsAsync(CancellationToken cancellationToken)
        {
            string query = (SearchTextBox.Text ?? string.Empty).Trim();
            if (_index is null || query.Length == 0)
            {
                LoreSearchHitsList.ItemsSource = Array.Empty<LoreSearchHitModel>();
                LoreSearchHitsStatus.Text = query.Length == 0
                    ? "Type a word to find every document containing it, with the matching sentence."
                    : "Load a library first.";
                return;
            }

            LoreIndex index = _index;
            IReadOnlyList<LoreSearchHit> hits = await Task.Run(
                () => _searchService.SearchAllDocuments(index, query),
                cancellationToken);

            cancellationToken.ThrowIfCancellationRequested();

            var models = hits.Select(hit => new LoreSearchHitModel(hit)).ToArray();
            LoreSearchHitsList.ItemsSource = models;
            int documentCount = models.Select(model => model.Hit.DocumentPath).Distinct(StringComparer.OrdinalIgnoreCase).Count();
            LoreSearchHitsStatus.Text = models.Length > 0
                ? $"{models.Length} match{(models.Length == 1 ? "" : "es")} across {documentCount} document(s). Select one to open it."
                : "No document contains that word in its text. Try another word, or clear the search.";
        }

        private async void LoreSearchHitButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not FrameworkElement { DataContext: LoreSearchHitModel model })
            {
                return;
            }

            try
            {
                _isDocumentLoading = true;
                await LoadDocumentAsync(model.Hit.DocumentPath, anchor: null, addToHistory: true);
            }
            catch
            {
                ShowReaderPlaceholder("Could not open that match", LorePageText.DocumentLoadFailed);
                AppStatusService.SetStatus("Lore: search hit failed to open");
            }
            finally
            {
                _isDocumentLoading = false;
            }
        }

        private async void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            await LoadLoreIndexAsync(preserveCurrentDocument: true);
        }

        private async void DocumentTree_ItemInvoked(TreeView sender, TreeViewItemInvokedEventArgs args)
        {
            if (_suppressTreeSelection)
            {
                return;
            }

            LoreTreeNodeTag? node = args.InvokedItem switch
            {
                TreeViewNode treeNode when treeNode.Content is LoreTreeNodeTag content => content,
                LoreTreeNodeTag content => content,
                _ => null
            };

            await TryLoadSelectedLoreNodeAsync(node);
        }

        private async void DocumentTree_SelectionChanged(TreeView sender, TreeViewSelectionChangedEventArgs args)
        {
            if (_suppressTreeSelection)
            {
                return;
            }

            LoreTreeNodeTag? node = sender.SelectedNode?.Content as LoreTreeNodeTag;
            await TryLoadSelectedLoreNodeAsync(node);
        }

        private async Task TryLoadSelectedLoreNodeAsync(LoreTreeNodeTag? node)
        {
            if (node == null || string.IsNullOrWhiteSpace(node.FilePath))
            {
                return;
            }

            if (_isLoading)
            {
                await WaitForLoreIndexIdleAsync();
            }

            if (_isLoading)
            {
                return;
            }

            if (_isDocumentLoading)
            {
                return;
            }

            try
            {
                _isDocumentLoading = true;
                await LoadDocumentAsync(node.FilePath, anchor: null, addToHistory: true);
            }
            catch
            {
                ShowReaderPlaceholder("Could not load document", LorePageText.DocumentLoadFailed);
                AppStatusService.SetStatus("Lore: load failed");
            }
            finally
            {
                _isDocumentLoading = false;
            }
        }

        private async Task WaitForLoreIndexIdleAsync()
        {
            for (int attempt = 0; attempt < 100 && _isLoading; attempt++)
            {
                await Task.Delay(50);
            }
        }

        private async void BackButton_Click(object sender, RoutedEventArgs e)
        {
            if (_backStack.Count == 0)
            {
                return;
            }

            LoreHistoryEntry entry = _backStack.Pop();
            if (!string.IsNullOrWhiteSpace(_currentSourcePath))
            {
                _forwardStack.Push(new LoreHistoryEntry(_currentSourcePath!, _currentAnchor));
            }

            try
            {
                _suppressHistory = true;
                await LoadDocumentAsync(entry.FilePath, entry.Anchor, addToHistory: false);
            }
            catch
            {
                ShowReaderPlaceholder("Could not go back", LoreHistoryFailureMessage);
                AppStatusService.SetStatus("Lore: back navigation failed");
            }
            finally
            {
                _suppressHistory = false;
                UpdateNavButtons();
            }
        }

        private async void ForwardButton_Click(object sender, RoutedEventArgs e)
        {
            if (_forwardStack.Count == 0)
            {
                return;
            }

            LoreHistoryEntry entry = _forwardStack.Pop();
            if (!string.IsNullOrWhiteSpace(_currentSourcePath))
            {
                _backStack.Push(new LoreHistoryEntry(_currentSourcePath!, _currentAnchor));
            }

            try
            {
                _suppressHistory = true;
                await LoadDocumentAsync(entry.FilePath, entry.Anchor, addToHistory: false);
            }
            catch
            {
                ShowReaderPlaceholder("Could not go forward", LoreHistoryFailureMessage);
                AppStatusService.SetStatus("Lore: forward navigation failed");
            }
            finally
            {
                _suppressHistory = false;
                UpdateNavButtons();
            }
        }

        private async void HomeButton_Click(object sender, RoutedEventArgs e)
        {
            if (_index?.HomeDocument == null)
            {
                return;
            }

            _backStack.Clear();
            _forwardStack.Clear();

            try
            {
                _suppressHistory = true;
                await LoadDocumentAsync(_index.HomeDocument.FilePath, anchor: null, addToHistory: false);
            }
            catch
            {
                ShowReaderPlaceholder("Could not open home document", LoreHomeFailureMessage);
                AppStatusService.SetStatus("Lore: home navigation failed");
            }
            finally
            {
                _suppressHistory = false;
                UpdateNavButtons();
            }
        }

        private void ToggleLibraryButton_Click(object sender, RoutedEventArgs e)
        {
            LoreSplitView.IsPaneOpen = !LoreSplitView.IsPaneOpen;
            UpdateLibraryToggleButton();
        }

        private async void OpenExternalButton_Click(object sender, RoutedEventArgs e)
        {
            string? sourcePath = _currentSourcePath;
            if (string.IsNullOrWhiteSpace(sourcePath))
            {
                return;
            }

            string? anchor = _currentAnchor;

            try
            {
                // The reader itself is native now; the HTML export exists only so
                // the shell has a file to hand to the user's browser.
                RenderedLoreDocument rendered = await Task.Run(() => _service.RenderDocument(sourcePath!, anchor));
                await Launcher.LaunchUriAsync(new Uri(rendered.DisplayUri));
                AppStatusService.SetStatus("Lore: opened current document externally");
            }
            catch
            {
                CurrentPathTextBlock.Text = LoreExternalOpenFailureMessage;
                AppStatusService.SetStatus("Lore: external open failed");
            }
        }

        private void ShowReaderPlaceholder(string title, string body)
        {
            ReaderPlaceholderTitleTextBlock.Text = title;
            ReaderPlaceholderBodyTextBlock.Text = body;
            ReaderPlaceholderBorder.Visibility = Visibility.Visible;
            ReaderScrollViewer.Visibility = Visibility.Collapsed;
        }

        private void UpdateCounts()
        {
            if (_index == null)
            {
                LibraryCountTextBlock.Text = "Reader unavailable.";
                PaneStateTextBlock.Text = "Library unavailable.";
                return;
            }

            int visibleDocuments = CountDocumentNodes(DocumentTree.RootNodes);
            string query = (SearchTextBox.Text ?? string.Empty).Trim();
            if (string.IsNullOrWhiteSpace(query))
            {
                LibraryCountTextBlock.Text = $"{_index.Documents.Count} documents ready";
                PaneStateTextBlock.Text = _index.UsingContentPack
                    ? "Showing included offline documents; Source and External links open in your browser."
                    : _index.UsingLoreBook
                        ? "Showing included Lore chapters; Source and External links open in your browser."
                        : "Showing canonical Lore documents from this source checkout.";
            }
            else
            {
                LibraryCountTextBlock.Text = $"{visibleDocuments} matching documents";
                PaneStateTextBlock.Text = LorePageText.DescribeSearchStatus(query, visibleDocuments);
            }
        }

        private static int CountDocumentNodes(IEnumerable<TreeViewNode> nodes)
        {
            int count = 0;
            foreach (TreeViewNode node in nodes)
            {
                if (node.Content is LoreTreeNodeTag tag && !string.IsNullOrWhiteSpace(tag.FilePath))
                {
                    count++;
                }

                count += CountDocumentNodes(node.Children);
            }

            return count;
        }

        private void UpdateNavButtons()
        {
            BackButton.IsEnabled = _backStack.Count > 0;
            ForwardButton.IsEnabled = _forwardStack.Count > 0;
            HomeButton.IsEnabled = _index?.HomeDocument != null;
            OpenExternalButton.IsEnabled = !string.IsNullOrWhiteSpace(_currentSourcePath);
        }

        private void UpdateLibraryToggleButton()
        {
            ToggleLibraryButton.Label = LoreSplitView.IsPaneOpen ? "Hide Library" : "Show Library";
        }

        private void CancelPendingSearchFilter()
        {
            if (_searchFilterCancellation == null)
            {
                return;
            }

            _searchFilterCancellation.Cancel();
            _searchFilterCancellation.Dispose();
            _searchFilterCancellation = null;
        }

        private string ResolveDocumentTitle(string fullPath, string fallbackTitle)
        {
            if (_documentLookup.TryGetValue(fullPath, out LoreDocument? document))
            {
                return document.Title;
            }

            return fallbackTitle;
        }

        private string ResolveDisplayPath(string fullPath)
        {
            if (_index == null)
            {
                return "Reading from the offline Lore library.";
            }

            if (_documentLookup.TryGetValue(fullPath, out LoreDocument? document) &&
                !string.IsNullOrWhiteSpace(document.RelativePath))
            {
                return $"Reading {document.Title} from the offline Lore library.";
            }

            string fileName = IsLorePackSourcePath(fullPath)
                ? "included document"
                : Path.GetFileName(fullPath);
            return string.IsNullOrWhiteSpace(fileName)
                ? "Reading from the offline Lore library."
                : $"Reading {fileName}.";
        }

        private string ResolveToolTipPath(string sourcePath)
        {
            if (_documentLookup.TryGetValue(sourcePath, out LoreDocument? document))
            {
                return LorePageText.BuildDocumentTooltip(document.Title, document.RelativePath, sourcePath);
            }

            if (IsLorePackSourcePath(sourcePath))
            {
                return LorePageText.DocumentTooltipFallback;
            }

            return LorePageText.BuildDocumentTooltip(title: null, relativePath: null, sourcePath);
        }

        private static string BuildNodeKey(LoreTreeItem item, string? parentKey, int index)
        {
            if (!string.IsNullOrWhiteSpace(item.FilePath))
            {
                return IsLorePackSourcePath(item.FilePath)
                    ? $"file:{item.FilePath}"
                    : $"file:{Path.GetFullPath(item.FilePath)}";
            }

            string parentPart = string.IsNullOrWhiteSpace(parentKey) ? "root" : parentKey;
            return $"group:{parentPart}/{index}:{item.Title}";
        }

        private static bool PathsEqual(string? left, string? right)
        {
            if (string.IsNullOrWhiteSpace(left) || string.IsNullOrWhiteSpace(right))
            {
                return false;
            }

            if (IsLorePackSourcePath(left) || IsLorePackSourcePath(right))
            {
                return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
            }

            return string.Equals(
                Path.GetFullPath(left),
                Path.GetFullPath(right),
                StringComparison.OrdinalIgnoreCase);
        }

        private static string? TryGetLocalPath(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return null;
            }

            if (Uri.TryCreate(value, UriKind.Absolute, out Uri? uri) && uri.IsFile)
            {
                return uri.LocalPath;
            }

            if (Path.IsPathRooted(value))
            {
                return RemoveAnchor(value);
            }

            return null;
        }

        private static string RemoveAnchor(string value)
        {
            int anchorIndex = value.IndexOf('#');
            return anchorIndex >= 0 ? value[..anchorIndex] : value;
        }

        private static bool IsLorePackSourcePath(string? value)
        {
            return !string.IsNullOrWhiteSpace(value) &&
                   value.StartsWith("lore-pack://", StringComparison.OrdinalIgnoreCase);
        }

        private sealed record LoreHistoryEntry(string FilePath, string? Anchor);

        /// <summary>
        /// The A-/A+ reader control: re-renders the open document at a larger or
        /// smaller text size. Steps are 10%; the renderer clamps the result. A
        /// re-render failure keeps the previous page instead of tearing the reader.
        /// </summary>
        private async void ReaderTextSizeButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_currentSourcePath) || _isDocumentLoading)
            {
                return;
            }

            bool grow = ReferenceEquals(sender, ReaderTextLargerButton);
            double next = Math.Clamp(_readerTextScale + (grow ? 0.1 : -0.1), 0.7, 1.8);
            if (Math.Abs(next - _readerTextScale) < 0.001)
            {
                return;
            }

            try
            {
                _isDocumentLoading = true;
                _readerTextScale = next;
                string anchorAtStart = _currentAnchor ?? string.Empty;

                // Reload from the service so the document is re-rendered at the new
                // size; history is not disturbed because it is the same document.
                await LoadDocumentAsync(_currentSourcePath!, anchor: anchorAtStart, addToHistory: false);
                AppStatusService.SetStatus($"Lore: text size {(grow ? "larger" : "smaller")} ({Math.Round(next * 100)}%)");
            }
            catch
            {
                ShowReaderPlaceholder("Could not change the text size", LorePageText.DocumentLoadFailed);
                AppStatusService.SetStatus("Lore: text size change failed");
            }
            finally
            {
                _isDocumentLoading = false;
            }
        }

        private void ApplyReaderTextScale()
        {
            // Kept as an explicit step after RenderCurrentDocument so future
            // non-font scaling (spacing, tables) lands in one place.
        }

        /// <summary>
        /// Fills the "What links here" panel for the open document from the index
        /// built at library load. A missing index or an unlinked document each get
        /// their own honest sentence instead of a blank panel.
        /// </summary>
        private void RefreshBacklinks(string sourcePath)
        {
            if (_backlinkIndex is null)
            {
                LoreBacklinksList.ItemsSource = Array.Empty<LoreBacklinkModel>();
                LoreBacklinksStatus.Text = "Cross-links are unavailable for this library.";
                return;
            }

            IReadOnlyList<LoreBacklink> backlinks = _searchService.GetBacklinks(_backlinkIndex, sourcePath);
            if (backlinks.Count == 0)
            {
                LoreBacklinksList.ItemsSource = Array.Empty<LoreBacklinkModel>();
                LoreBacklinksStatus.Text = "No included document links to this one yet.";
                return;
            }

            var models = backlinks.Select(link => new LoreBacklinkModel(link)).ToArray();
            LoreBacklinksList.ItemsSource = models;
            LoreBacklinksStatus.Text =
                $"{models.Length} document{(models.Length == 1 ? "" : "s")} link to this page:";
        }

        private void RefreshOutline(LoreDocumentContent content)
        {
            IReadOnlyList<LoreOutlineEntry> entries = _searchService.BuildOutline(content);
            if (entries.Count == 0)
            {
                LoreOutlineList.ItemsSource = Array.Empty<LoreOutlineEntryModel>();
                LoreOutlineStatus.Text = "This document has no headings yet.";
                return;
            }

            var models = entries.Select(entry => new LoreOutlineEntryModel(entry)).ToArray();
            LoreOutlineList.ItemsSource = models;
            LoreOutlineStatus.Text =
                $"{models.Length} heading{(models.Length == 1 ? "" : "s")} on this page:";
        }

        private void RefreshOutgoing(string sourcePath)
        {
            if (_index is null)
            {
                LoreOutgoingList.ItemsSource = Array.Empty<LoreOutgoingLinkModel>();
                LoreOutgoingStatus.Text = "Outgoing links are unavailable for this library.";
                return;
            }

            IReadOnlyList<LoreOutgoingLink> links = _searchService.GetOutgoingLinks(_index, sourcePath);
            if (links.Count == 0)
            {
                LoreOutgoingList.ItemsSource = Array.Empty<LoreOutgoingLinkModel>();
                LoreOutgoingStatus.Text = "This page does not link to another included document yet.";
                return;
            }

            var models = links.Select(link => new LoreOutgoingLinkModel(link)).ToArray();
            LoreOutgoingList.ItemsSource = models;
            LoreOutgoingStatus.Text =
                $"{models.Length} included document{(models.Length == 1 ? "" : "s")} linked from this page:";
        }

        private void LoreOutlineButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not FrameworkElement { DataContext: LoreOutlineEntryModel model })
            {
                return;
            }

            ScrollToAnchor(model.Entry.Id);
        }

        private async void LoreOutgoingButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not FrameworkElement { DataContext: LoreOutgoingLinkModel model })
            {
                return;
            }

            try
            {
                await LoadDocumentAsync(model.Link.TargetDocumentPath, anchor: null, addToHistory: true);
            }
            catch
            {
                ShowReaderPlaceholder("Could not open that link", LorePageText.DocumentLoadFailed);
                AppStatusService.SetStatus("Lore: outgoing link failed to open");
            }
        }

        private async void LoreBacklinkButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not FrameworkElement { DataContext: LoreBacklinkModel model })
            {
                return;
            }

            try
            {
                await LoadDocumentAsync(model.Link.SourceDocumentPath, anchor: null, addToHistory: true);
            }
            catch
            {
                ShowReaderPlaceholder("Could not open that link", LorePageText.DocumentLoadFailed);
                AppStatusService.SetStatus("Lore: cross-link failed to open");
            }
        }

        private sealed class LoreTreeNodeTag
        {
            public LoreTreeNodeTag(string title, string? filePath, string? relativePath, string key)
            {
                Title = title;
                FilePath = filePath;
                RelativePath = relativePath;
                Key = key;
            }

            public string Title { get; }
            public string? FilePath { get; }
            public string? RelativePath { get; }
            public string Key { get; }

            public override string ToString()
            {
                return Title;
            }
        }
    }
}
