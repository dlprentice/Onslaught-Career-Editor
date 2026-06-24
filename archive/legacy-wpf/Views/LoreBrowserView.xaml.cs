using Markdig;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using Microsoft.Web.WebView2.Core;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Lore Browser tab - renders markdown documentation.
    /// Displays curated documentation from lore-book/.
    /// </summary>
    public partial class LoreBrowserView : UserControl, ILazyLoadView
    {
        private sealed class LoreHistoryEntry
        {
            public LoreHistoryEntry(string filePath, bool isHtml = false, string? anchor = null)
            {
                FilePath = filePath;
                IsHtml = isHtml;
                Anchor = anchor;
            }

            public string FilePath { get; }
            public bool IsHtml { get; }
            public string? Anchor { get; }
        }

        private List<LoreDocument> _allDocuments = new();
        private List<LoreTreeItem> _rootNodes = new();
        private readonly MarkdownPipeline _markdownPipeline;
        private string? _projectRoot;
        private bool _hasLoaded;
        private bool _isLoading;
        private CancellationTokenSource? _loadCts;
        private string? _currentFilePath;
        private bool _currentIsHtml;
        private Task? _webViewInitTask;
        private string? _pendingAnchor;
        private string? _lastRenderPath;
        private readonly Stack<LoreHistoryEntry> _backStack = new();
        private readonly Stack<LoreHistoryEntry> _forwardStack = new();
        private bool _suppressHistory;
        private bool _webViewEventsHooked;
        private bool _usingLoreBook;
        private LoreDocument? _homeDocument;
        private IReadOnlyList<LoreTreeItem> _currentTreeItems = Array.Empty<LoreTreeItem>();
        private bool _suppressTreeSelection;

        public LoreBrowserView()
        {
            InitializeComponent();

            // Configure Markdig with common extensions
            _markdownPipeline = new MarkdownPipelineBuilder()
                .UseAdvancedExtensions()
                .Build();

            // Defer loading until the tab is first activated
        }

        private async Task EnsureWebViewInitializedAsync()
        {
            if (_webViewInitTask != null)
            {
                await _webViewInitTask;
                return;
            }

            _webViewInitTask = ContentBrowser.EnsureCoreWebView2Async();
            await _webViewInitTask;

            if (!_webViewEventsHooked && ContentBrowser.CoreWebView2 != null)
            {
                ContentBrowser.CoreWebView2.NewWindowRequested += ContentBrowser_NewWindowRequested;
                _webViewEventsHooked = true;
            }
        }

        public void EnsureLoaded()
        {
            if (_hasLoaded)
            {
                return;
            }

            LoadLoreDocuments();
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            LoadLoreDocuments();
        }

        private void LoadLoreDocuments()
        {
            if (_isLoading)
            {
                return;
            }

            _projectRoot = FindProjectRoot();
            if (string.IsNullOrEmpty(_projectRoot))
            {
                TitleBlock.Text = "Documentation directory not found";
                MainWindow.SetStatus("Lore Browser: Could not find project root");
                return;
            }

            string loreBookDir = Path.Combine(_projectRoot, "lore-book");
            if (!Directory.Exists(loreBookDir))
            {
                TitleBlock.Text = "Lore book not found";
                MainWindow.SetStatus("Lore Browser: Missing lore-book folder");
                return;
            }

            LoadLoreDocumentsAsync(_projectRoot);
        }

        private void LoadLoreDocumentsAsync(string projectRoot)
        {
            _loadCts?.Cancel();
            _loadCts = new CancellationTokenSource();
            var token = _loadCts.Token;

            _isLoading = true;
            TitleBlock.Text = "Loading documents...";
            MainWindow.SetStatus("Lore Browser: Loading...");

            Task.Run(() => BuildLoreIndex(projectRoot, token), token)
                .ContinueWith(task =>
                {
                    _isLoading = false;

                    if (task.IsCanceled)
                    {
                        return;
                    }

                    if (task.Exception != null)
                    {
                        Dispatcher.Invoke(() =>
                        {
                            TitleBlock.Text = "Failed to load documents";
                            MainWindow.SetStatus("Lore Browser: Load failed");
                        });
                        return;
                    }

                    var result = task.Result;
                    Dispatcher.Invoke(() =>
                    {
                        _allDocuments = result.Documents;
                        _rootNodes = result.TreeItems;
                        _usingLoreBook = result.UsingLoreBook;
                        DocumentTree.ItemsSource = _rootNodes;
                        _currentTreeItems = _rootNodes;
                        var defaultDoc = FindDefaultDocument(_allDocuments);
                        _homeDocument = defaultDoc;

                        if (_allDocuments.Count == 0)
                        {
                            TitleBlock.Text = "No documents found";
                            MainWindow.SetStatus("Lore Browser: No documents found");
                        }
                        else
                        {
                            TitleBlock.Text = $"Select a document ({_allDocuments.Count} files)";
                            MainWindow.SetStatus($"Lore Browser: Loaded {_allDocuments.Count} documents");
                        }

                        _hasLoaded = true;

                        if (_rootNodes.Count > 0)
                        {
                            Dispatcher.BeginInvoke(new Action(() =>
                            {
                                foreach (var item in _rootNodes)
                                {
                                    var tvi = DocumentTree.ItemContainerGenerator.ContainerFromItem(item) as TreeViewItem;
                                    if (tvi != null) tvi.IsExpanded = true;
                                }

                                if (defaultDoc != null)
                                {
                                    SelectDefaultDocument(defaultDoc);
                                }
                            }), DispatcherPriority.Loaded);
                        }
                    });
                }, TaskScheduler.Default);
        }

        private static LoreDocument? FindDefaultDocument(IReadOnlyList<LoreDocument> docs)
        {
            if (docs.Count == 0)
            {
                return null;
            }

            return docs
                .OrderBy(d => d.Order ?? int.MaxValue)
                .ThenBy(d => d.Title, StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault()
                ?? docs[0];
        }

        private void SelectDefaultDocument(LoreDocument doc)
        {
            LoadDocumentByPath(doc.FilePath, null, false);

            var node = FindNodeByPath(_rootNodes, doc.FilePath);
            if (node == null)
            {
                return;
            }

            DocumentTree.UpdateLayout();
            var container = DocumentTree.ItemContainerGenerator.ContainerFromItem(node) as TreeViewItem;
            if (container == null)
            {
                DocumentTree.UpdateLayout();
                container = DocumentTree.ItemContainerGenerator.ContainerFromItem(node) as TreeViewItem;
            }

            if (container != null)
            {
                container.IsSelected = true;
                container.BringIntoView();
            }
        }

        private static LoreTreeItem? FindNodeByPath(IEnumerable<LoreTreeItem> nodes, string filePath)
        {
            foreach (var node in nodes)
            {
                if (!string.IsNullOrEmpty(node.FilePath) &&
                    string.Equals(node.FilePath, filePath, StringComparison.OrdinalIgnoreCase))
                {
                    return node;
                }

                if (node.Children.Count > 0)
                {
                    var found = FindNodeByPath(node.Children, filePath);
                    if (found != null)
                    {
                        return found;
                    }
                }
            }

            return null;
        }

        private static LoreLoadResult BuildLoreIndex(string projectRoot, CancellationToken token)
        {
            var documents = new List<LoreDocument>();
            var roots = new List<LoreTreeItem>();
            bool usingLoreBook = false;

            string loreBookDir = Path.Combine(projectRoot, "lore-book");
            if (Directory.Exists(loreBookDir))
            {
                usingLoreBook = TryLoadLoreBook(loreBookDir, documents, roots, token);
            }

            if (!usingLoreBook && Directory.Exists(loreBookDir))
            {
                var rootNode = new LoreTreeItem { Title = "Lore Book" };
                roots.Add(rootNode);

                foreach (string file in Directory.GetFiles(loreBookDir, "*.md", SearchOption.AllDirectories))
                {
                    token.ThrowIfCancellationRequested();
                    string fileName = Path.GetFileNameWithoutExtension(file);
                    if (IsIndexFile(fileName) && ShouldSkipIndex(file, fileName))
                    {
                        continue;
                    }
                    string relativePath = Path.GetRelativePath(loreBookDir, file);
                    bool isIndex = IsIndexFile(fileName);
                    string title = ResolveTitle(fileName, file, "Lore Book", relativePath, isIndex, out int? order);

                    var doc = new LoreDocument
                    {
                        Title = title,
                        FilePath = file,
                        RelativePath = relativePath,
                        SourceDir = "Lore Book",
                        IsIndex = isIndex,
                        Order = order
                    };
                    documents.Add(doc);
                }

                DisambiguateDuplicateTitles(documents);
                foreach (var doc in documents)
                {
                    AddDocumentToTree(rootNode, doc);
                }
                SortTree(rootNode);
            }

            return new LoreLoadResult(documents, roots, usingLoreBook);
        }

        private sealed record LoreLoadResult(List<LoreDocument> Documents, List<LoreTreeItem> TreeItems, bool UsingLoreBook);

        private sealed class BookNode
        {
            public string Title { get; set; } = string.Empty;
            public string? File { get; set; }
            public int Order { get; set; }
            public List<BookNode> Children { get; set; } = new();
        }

        private static bool TryLoadLoreBook(string loreBookDir, List<LoreDocument> documents, List<LoreTreeItem> roots, CancellationToken token)
        {
            string bookPath = Path.Combine(loreBookDir, "BOOK.md");
            if (!File.Exists(bookPath))
            {
                return false;
            }

            var nodes = ParseBookMarkdown(bookPath, token);
            if (nodes.Count == 0)
            {
                return false;
            }

            var root = new LoreTreeItem { Title = "Lore Book" };
            foreach (var node in nodes)
            {
                AddBookNode(root, node, loreBookDir, documents);
            }

            roots.Add(root);
            return true;
        }

        private static List<BookNode> ParseBookMarkdown(string bookPath, CancellationToken token)
        {
            var nodes = new List<BookNode>();
            var stack = new Stack<(int Level, BookNode Node)>();
            int order = 0;
            bool inCodeBlock = false;

            foreach (var raw in File.ReadAllLines(bookPath))
            {
                token.ThrowIfCancellationRequested();
                string line = raw;
                string trimmed = line.Trim();
                if (trimmed.StartsWith("```"))
                {
                    inCodeBlock = !inCodeBlock;
                    continue;
                }
                if (inCodeBlock || string.IsNullOrWhiteSpace(trimmed))
                {
                    continue;
                }

                var match = Regex.Match(line, @"^(?<indent>[\t ]*)[-*+]\s+(?<content>.+)$");
                if (!match.Success)
                {
                    continue;
                }

                int level = ComputeIndentLevel(match.Groups["indent"].Value);
                string content = match.Groups["content"].Value.Trim();
                if (string.IsNullOrWhiteSpace(content))
                {
                    continue;
                }

                string title = content;
                string? file = null;
                var linkMatch = Regex.Match(content, @"^\[(?<title>.+?)\]\((?<file>.+?)\)$");
                if (linkMatch.Success)
                {
                    title = linkMatch.Groups["title"].Value.Trim();
                    file = linkMatch.Groups["file"].Value.Trim();
                }

                var node = new BookNode
                {
                    Title = string.IsNullOrWhiteSpace(title) ? "Untitled" : title,
                    File = file,
                    Order = order++
                };

                while (stack.Count > 0 && stack.Peek().Level >= level)
                {
                    stack.Pop();
                }

                if (stack.Count == 0)
                {
                    nodes.Add(node);
                }
                else
                {
                    stack.Peek().Node.Children.Add(node);
                }

                stack.Push((level, node));
            }

            return nodes;
        }

        private static int ComputeIndentLevel(string indent)
        {
            int level = 0;
            int spaces = 0;
            foreach (char c in indent)
            {
                if (c == '\t')
                {
                    level++;
                }
                else if (c == ' ')
                {
                    spaces++;
                    if (spaces == 2)
                    {
                        level++;
                        spaces = 0;
                    }
                }
            }
            return level + (spaces / 2);
        }

        private static void AddBookNode(LoreTreeItem parent, BookNode node, string loreBookDir, List<LoreDocument> documents)
        {
            string title = node.Title;
            string? filePath = null;
            string? relativePath = null;
            bool isIndex = false;

            if (!string.IsNullOrWhiteSpace(node.File))
            {
                string candidate = Path.GetFullPath(Path.Combine(loreBookDir, node.File));
                if (File.Exists(candidate))
                {
                    filePath = candidate;
                    relativePath = Path.GetRelativePath(loreBookDir, candidate);
                    string fileName = Path.GetFileNameWithoutExtension(candidate);
                    isIndex = IsIndexFile(fileName);
                }
            }

            var treeItem = new LoreTreeItem
            {
                Title = title,
                FilePath = filePath,
                RelativePath = relativePath,
                IsIndex = isIndex,
                Order = node.Order
            };

            if (filePath != null)
            {
                documents.Add(new LoreDocument
                {
                    Title = title,
                    FilePath = filePath,
                    RelativePath = relativePath ?? string.Empty,
                    SourceDir = "Lore Book",
                    IsIndex = isIndex,
                    Order = node.Order
                });
            }

            if (node.Children.Count > 0)
            {
                foreach (var child in node.Children)
                {
                    AddBookNode(treeItem, child, loreBookDir, documents);
                }
            }

            parent.Children.Add(treeItem);
        }
        private static void DisambiguateDuplicateTitles(List<LoreDocument> documents)
        {
            var grouped = documents.GroupBy(doc =>
                (doc.SourceDir, Folder: Path.GetDirectoryName(doc.RelativePath) ?? string.Empty, Title: doc.Title),
                StringTupleComparer.Instance);

            foreach (var group in grouped)
            {
                if (group.Count() <= 1)
                {
                    continue;
                }

                foreach (var doc in group)
                {
                    string fileName = Path.GetFileNameWithoutExtension(doc.FilePath);
                    string suffix = FormatTitleSimple(fileName);
                    doc.Title = $"{doc.Title} ({suffix})";
                }
            }
        }

        private sealed class StringTupleComparer : IEqualityComparer<(string SourceDir, string Folder, string Title)>
        {
            public static StringTupleComparer Instance { get; } = new();

            public bool Equals((string SourceDir, string Folder, string Title) x, (string SourceDir, string Folder, string Title) y)
            {
                return string.Equals(x.SourceDir, y.SourceDir, StringComparison.OrdinalIgnoreCase)
                    && string.Equals(x.Folder, y.Folder, StringComparison.OrdinalIgnoreCase)
                    && string.Equals(x.Title, y.Title, StringComparison.OrdinalIgnoreCase);
            }

            public int GetHashCode((string SourceDir, string Folder, string Title) obj)
            {
                return HashCode.Combine(
                    StringComparer.OrdinalIgnoreCase.GetHashCode(obj.SourceDir ?? string.Empty),
                    StringComparer.OrdinalIgnoreCase.GetHashCode(obj.Folder ?? string.Empty),
                    StringComparer.OrdinalIgnoreCase.GetHashCode(obj.Title ?? string.Empty));
            }
        }

        private string? FindProjectRoot()
        {
            // Try relative paths from executable to find project root
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;

            // Look for a directory that contains lore/ or other project-root markers
            string[] candidates = new[]
            {
                baseDir,
                Path.Combine(baseDir, ".."),
                Path.Combine(baseDir, "..", ".."),
                Path.Combine(baseDir, "..", "..", ".."),
                Path.Combine(baseDir, "..", "..", "..", ".."),
                Path.Combine(baseDir, "..", "..", "..", "..", ".."),
                Path.Combine(baseDir, "..", "..", "..", "..", "..", ".."),
            };

            foreach (string path in candidates)
            {
                string fullPath = Path.GetFullPath(path);
                // Check for lore-book/ directory or AGENTS.md as project root indicators
                if (Directory.Exists(Path.Combine(fullPath, "lore-book")) ||
                    Directory.Exists(Path.Combine(fullPath, "lore")) ||
                    File.Exists(Path.Combine(fullPath, "AGENTS.md")))
                    return fullPath;
            }

            return null;
        }

        private static void AddDocumentToTree(LoreTreeItem root, LoreDocument doc)
        {
            string? relDir = Path.GetDirectoryName(doc.RelativePath);
            var segments = (relDir ?? string.Empty)
                .Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                .Where(part => !string.IsNullOrWhiteSpace(part));

            var current = root;
            foreach (var segment in segments)
            {
                string title = FormatTitleSimple(segment);
                var existing = current.Children.FirstOrDefault(c => c.FilePath == null && c.Title.Equals(title, StringComparison.OrdinalIgnoreCase));
                if (existing == null)
                {
                    existing = new LoreTreeItem { Title = title };
                    current.Children.Add(existing);
                }
                current = existing;
            }

            current.Children.Add(new LoreTreeItem
            {
                Title = doc.Title,
                FilePath = doc.FilePath,
                RelativePath = doc.RelativePath,
                IsIndex = doc.IsIndex,
                Order = doc.Order
            });

            if (doc.IsIndex && doc.Order.HasValue && current.Order == null)
            {
                current.Order = doc.Order;
            }
        }

        private static void SortTree(LoreTreeItem node)
        {
            node.Children = node.Children
                .OrderBy(child => child.IsIndex ? 0 : child.FilePath == null ? 1 : 2)
                .ThenBy(child => child.Order ?? int.MaxValue)
                .ThenBy(child => child.Title, StringComparer.OrdinalIgnoreCase)
                .ToList();

            foreach (var child in node.Children)
            {
                SortTree(child);
            }
        }

        private static bool IsIndexFile(string fileName)
        {
            return string.Equals(fileName, "index", StringComparison.OrdinalIgnoreCase)
                || string.Equals(fileName, "readme", StringComparison.OrdinalIgnoreCase)
                || string.Equals(fileName, "_index", StringComparison.OrdinalIgnoreCase)
                || string.Equals(fileName, "lore-index", StringComparison.OrdinalIgnoreCase)
                || string.Equals(fileName, "re-index", StringComparison.OrdinalIgnoreCase)
                || string.Equals(fileName, "roadmap-index", StringComparison.OrdinalIgnoreCase);
        }

        private static bool ShouldSkipIndex(string filePath, string fileName)
        {
            string lower = fileName.ToLowerInvariant();
            string directory = Path.GetDirectoryName(filePath) ?? string.Empty;
            bool hasCanonicalIndex = File.Exists(Path.Combine(directory, "_index.md"));
            if (hasCanonicalIndex)
            {
                return lower != "_index";
            }

            if (lower == "readme" && File.Exists(Path.Combine(directory, "index.md")))
            {
                return true;
            }

            return false;
        }

        private static string ResolveTitle(string fileName, string filePath, string sourceLabel, string relativePath, bool isIndex, out int? order)
        {
            string? contentTitle = TryReadTitleFromContent(filePath, out order);

            if (isIndex)
            {
                if (!string.IsNullOrWhiteSpace(contentTitle) && !IsGenericTitle(contentTitle))
                {
                    return contentTitle;
                }

                string? parentDir = Path.GetDirectoryName(relativePath);
                if (string.IsNullOrEmpty(parentDir))
                {
                    return $"{sourceLabel} Index";
                }

                string parentName = Path.GetFileName(parentDir);
                return $"{FormatTitleSimple(parentName)} Index";
            }

            if (!string.IsNullOrWhiteSpace(contentTitle) && !IsGenericTitle(contentTitle))
            {
                return contentTitle;
            }

            return FormatTitleSimple(fileName);
        }

        private static bool IsGenericTitle(string title)
        {
            string lower = title.Trim().ToLowerInvariant();
            return lower is "index" or "overview" or "readme";
        }

        private static string? TryReadTitleFromContent(string filePath, out int? order)
        {
            order = null;
            try
            {
                using var reader = new StreamReader(filePath);
                bool inFrontMatter = false;
                bool sawFrontMatter = false;
                string? frontMatterTitle = null;

                for (int i = 0; i < 40; i++)
                {
                    string? line = reader.ReadLine();
                    if (line == null)
                        break;

                    string trimmed = line.Trim();
                    if (i == 0 && trimmed == "---")
                    {
                        inFrontMatter = true;
                        sawFrontMatter = true;
                        continue;
                    }

                    if (inFrontMatter)
                    {
                        if (trimmed == "---")
                        {
                            inFrontMatter = false;
                            if (!string.IsNullOrWhiteSpace(frontMatterTitle))
                            {
                                return frontMatterTitle;
                            }
                            continue;
                        }

                        if (trimmed.StartsWith("title:", StringComparison.OrdinalIgnoreCase))
                        {
                            string titleValue = trimmed.Substring(6).Trim().Trim('"');
                            if (!string.IsNullOrWhiteSpace(titleValue))
                            {
                                frontMatterTitle = titleValue;
                            }
                        }

                        if (trimmed.StartsWith("order:", StringComparison.OrdinalIgnoreCase))
                        {
                            string orderValue = trimmed.Substring(6).Trim().Trim('"');
                            if (int.TryParse(orderValue, out int parsed))
                            {
                                order = parsed;
                            }
                        }

                        continue;
                    }

                    if (sawFrontMatter)
                    {
                        // Stop scanning after front matter if we already handled title.
                        if (!string.IsNullOrWhiteSpace(frontMatterTitle))
                        {
                            return frontMatterTitle;
                        }
                    }

                    if (string.IsNullOrWhiteSpace(trimmed))
                        continue;

                    if (trimmed.StartsWith("# "))
                        return trimmed.Substring(2).Trim();
                    if (trimmed.StartsWith("## "))
                        return trimmed.Substring(3).Trim();
                }
            }
            catch
            {
                // Ignore title extraction issues; fall back to filename.
            }

            return null;
        }

        private static string StripFrontMatter(string content)
        {
            if (string.IsNullOrWhiteSpace(content))
            {
                return content;
            }

            using var reader = new StringReader(content);
            string? first = reader.ReadLine();
            if (first == null || first.Trim() != "---")
            {
                return content;
            }

            var sb = new StringBuilder();
            string? line;
            bool inFrontMatter = true;
            while ((line = reader.ReadLine()) != null)
            {
                if (inFrontMatter && line.Trim() == "---")
                {
                    inFrontMatter = false;
                    continue;
                }

                if (!inFrontMatter)
                {
                    sb.AppendLine(line);
                }
            }

            return sb.ToString();
        }

        private static string FormatTitleSimple(string fileName)
        {
            return string.Join(" ", fileName.Split('-', '_')
                .Where(word => !string.IsNullOrEmpty(word))
                .Select(FormatTitleToken));
        }

        private static string FormatTitleToken(string token)
        {
            if (token.All(ch => char.IsUpper(ch) || char.IsDigit(ch)))
                return token;

            if (token.Any(char.IsUpper) && token.Any(char.IsLower))
                return token;

            if (token.Length == 0)
                return token;

            return char.ToUpper(token[0]) + token.Substring(1).ToLower();
        }

        private void DocumentTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            if (_suppressTreeSelection)
            {
                return;
            }

            if (e.NewValue is LoreTreeItem node && !string.IsNullOrEmpty(node.FilePath))
            {
                LoadDocument(node, null, true);
            }
        }

        private async void LoadDocument(LoreTreeItem doc, string? anchor = null, bool addToHistory = true)
        {
            try
            {
                TitleBlock.Text = doc.Title;

                if (addToHistory && !_suppressHistory && !string.IsNullOrWhiteSpace(_currentFilePath))
                {
                    if (!string.Equals(_currentFilePath, doc.FilePath, StringComparison.OrdinalIgnoreCase))
                    {
                        _backStack.Push(new LoreHistoryEntry(_currentFilePath!, _currentIsHtml));
                        _forwardStack.Clear();
                    }
                }

                _currentFilePath = doc.FilePath;
                _currentIsHtml = false;
                string markdown = File.ReadAllText(doc.FilePath!);
                markdown = StripFrontMatter(markdown);
                string html = Markdown.ToHtml(markdown, _markdownPipeline);
                html = RewriteLinks(html, doc.FilePath!);

                // Wrap in styled HTML
                string? baseHref = null;
                if (!string.IsNullOrEmpty(doc.FilePath))
                {
                    string? dir = Path.GetDirectoryName(doc.FilePath);
                    if (!string.IsNullOrEmpty(dir))
                    {
                        baseHref = new Uri(dir + Path.DirectorySeparatorChar).AbsoluteUri;
                    }
                }
                string styledHtml = WrapInHtml(html, baseHref);
                try
                {
                    await EnsureWebViewInitializedAsync();
                }
                catch (Exception ex)
                {
                    TitleBlock.Text = "WebView2 initialization failed";
                    ContentBrowser.NavigateToString($"<html><body><p style='color:red;'>Error initializing WebView2: {ex.Message}</p></body></html>");
                    return;
                }
                _pendingAnchor = anchor;
                string renderPath = GetRenderPathForDoc(doc.FilePath!);
                Directory.CreateDirectory(Path.GetDirectoryName(renderPath)!);
                File.WriteAllText(renderPath, styledHtml, Encoding.UTF8);
                _lastRenderPath = renderPath;
                ContentBrowser.Source = new Uri(renderPath);
                UpdateNavButtons();
                QueueTreeSelection(doc.FilePath);
            }
            catch (Exception ex)
            {
                TitleBlock.Text = "Error loading document";
                ContentBrowser.NavigateToString($"<html><body><p style='color:red;'>Error: {ex.Message}</p></body></html>");
            }
        }

        private void LoadDocumentByPath(string filePath, string? anchor = null, bool addToHistory = true)
        {
            string extension = Path.GetExtension(filePath);
            if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
            {
                LoadHtmlDocument(filePath, addToHistory);
                return;
            }

            var match = _allDocuments.FirstOrDefault(doc =>
                string.Equals(doc.FilePath, filePath, StringComparison.OrdinalIgnoreCase));

            if (match != null)
            {
                LoadDocument(new LoreTreeItem
                {
                    Title = match.Title,
                    FilePath = match.FilePath,
                    RelativePath = match.RelativePath,
                    IsIndex = match.IsIndex
                }, anchor, addToHistory);
                return;
            }

            // Fallback for files linked outside the scanned tree (e.g., root docs)
            string title = ResolveTitle(Path.GetFileNameWithoutExtension(filePath), filePath, "Document", filePath, IsIndexFile(Path.GetFileNameWithoutExtension(filePath)), out _);
            LoadDocument(new LoreTreeItem
            {
                Title = title,
                FilePath = filePath,
                RelativePath = filePath,
                IsIndex = IsIndexFile(Path.GetFileNameWithoutExtension(filePath))
            }, anchor, addToHistory);
        }

        private void LoadHtmlDocument(string filePath, bool addToHistory)
        {
            try
            {
                if (addToHistory && !_suppressHistory && !string.IsNullOrWhiteSpace(_currentFilePath))
                {
                    if (!string.Equals(_currentFilePath, filePath, StringComparison.OrdinalIgnoreCase))
                    {
                        _backStack.Push(new LoreHistoryEntry(_currentFilePath!, _currentIsHtml));
                        _forwardStack.Clear();
                    }
                }

                _currentFilePath = filePath;
                _currentIsHtml = true;
                _pendingAnchor = null;
                _lastRenderPath = filePath;
                TitleBlock.Text = Path.GetFileNameWithoutExtension(filePath);
                ContentBrowser.Source = new Uri(filePath);
                UpdateNavButtons();
            }
            catch (Exception ex)
            {
                TitleBlock.Text = "Error loading document";
                ContentBrowser.NavigateToString($"<html><body><p style='color:red;'>Error: {ex.Message}</p></body></html>");
            }
        }

        private string RewriteLinks(string html, string currentFilePath)
        {
            string baseDir = Path.GetDirectoryName(currentFilePath) ?? string.Empty;

            return Regex.Replace(html, "href\\s*=\\s*(\"(?<url>[^\"]+)\"|'(?<url>[^']+)'|(?<url>[^\\s>]+))", match =>
            {
                string href = match.Groups["url"].Value;
                if (string.IsNullOrWhiteSpace(href))
                    return match.Value;

                if (href.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                    href.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                    href.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase))
                {
                    return match.Value;
                }

                if (href.StartsWith("#"))
                {
                    return $"href=\"doc://{Uri.EscapeDataString(currentFilePath)}{href}\"";
                }

                string linkPath = href;
                string? fragment = null;
                int hashIndex = href.IndexOf('#');
                if (hashIndex >= 0)
                {
                    linkPath = href.Substring(0, hashIndex);
                    fragment = href.Substring(hashIndex + 1);
                }

                if (string.IsNullOrWhiteSpace(linkPath))
                {
                    return match.Value;
                }

                // Strip query strings
                int queryIndex = linkPath.IndexOf('?');
                if (queryIndex >= 0)
                {
                    linkPath = linkPath.Substring(0, queryIndex);
                }

                string resolved;
                if (linkPath.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        resolved = new Uri(linkPath).LocalPath;
                    }
                    catch
                    {
                        return match.Value;
                    }
                }
                else
                {
                    resolved = Path.GetFullPath(Path.Combine(baseDir, linkPath));
                }
                string? resolvedDoc = ResolveMarkdownTarget(resolved);
                if (resolvedDoc == null && !string.IsNullOrWhiteSpace(_projectRoot))
                {
                    try
                    {
                        string fallback = Path.GetFullPath(Path.Combine(_projectRoot, linkPath.TrimStart('.', Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)));
                        resolvedDoc = ResolveMarkdownTarget(fallback);
                    }
                    catch
                    {
                        resolvedDoc = null;
                    }
                }
                if (resolvedDoc == null)
                {
                    return match.Value;
                }

                string docUri = $"doc://{Uri.EscapeDataString(resolvedDoc)}";
                if (!string.IsNullOrWhiteSpace(fragment))
                {
                    docUri += $"#{fragment}";
                }

                return $"href=\"{docUri}\"";
            }, RegexOptions.IgnoreCase);
        }

        private void TryScrollToAnchor(string anchor)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(anchor))
                    return;
                _ = ContentBrowser.ExecuteScriptAsync($"location.hash='{EscapeForScript(anchor)}'");
            }
            catch
            {
                // Ignore scroll failures.
            }
        }

        private static void TryOpenExternal(string url)
        {
            try
            {
                if (url.StartsWith("data:", StringComparison.OrdinalIgnoreCase) ||
                    url.StartsWith("file://", StringComparison.OrdinalIgnoreCase) ||
                    url.StartsWith("doc://", StringComparison.OrdinalIgnoreCase))
                {
                    return;
                }
                Process.Start(new ProcessStartInfo
                {
                    FileName = url,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Browser navigation failed for '{url}': {ex.Message}");
            }
        }

        private string WrapInHtml(string bodyContent, string? baseHref = null)
        {
            return $@"<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    {(string.IsNullOrWhiteSpace(baseHref) ? "" : $"<base href='{baseHref}' />")}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            padding: 10px 20px;
            max-width: 100%;
        }}
        h1 {{ color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 8px; }}
        h2 {{ color: #2c5282; margin-top: 24px; }}
        h3 {{ color: #3182ce; }}
        code {{
            background-color: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, monospace;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            border: 1px solid #ddd;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        blockquote {{
            border-left: 4px solid #3182ce;
            margin: 16px 0;
            padding: 8px 16px;
            background-color: #ebf4ff;
            color: #2c5282;
        }}
        a {{
            color: #3182ce;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 24px 0;
        }}
        ul, ol {{
            padding-left: 24px;
        }}
        li {{
            margin: 4px 0;
        }}
    </style>
</head>
<body>
{bodyContent}
</body>
</html>";
        }

        private void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            string query = SearchTextBox.Text.Trim().ToLower();
            var expandedKeys = CaptureExpandedKeys();

            if (string.IsNullOrEmpty(query))
            {
                if (_rootNodes.Count == 0)
                {
                    LoadLoreDocuments();
                    return;
                }

                DocumentTree.ItemsSource = _rootNodes;
                _currentTreeItems = _rootNodes;
                if (_allDocuments.Count == 0)
                {
                    TitleBlock.Text = "No documents found";
                }
                else
                {
                    TitleBlock.Text = $"Select a document ({_allDocuments.Count} files)";
                }
                SyncTreeSelection(_currentFilePath);
                QueueTreeRestore(expandedKeys);
                return;
            }

            // Filter documents
            var filtered = _allDocuments.Where(d =>
            {
                // Check title
                if (d.Title.ToLower().Contains(query))
                    return true;

                // Check content (only for queries >= 3 chars to avoid excessive I/O)
                if (query.Length >= 3)
                {
                    try
                    {
                        string content = File.ReadAllText(d.FilePath).ToLower();
                        return content.Contains(query);
                    }
                    catch (Exception ex)
                    {
                        Debug.WriteLine($"Search content read failed for '{d.FilePath}': {ex.Message}");
                    }
                }

                return false;
            }).ToList();

            List<LoreTreeItem> treeItems;
            if (_usingLoreBook)
            {
                var allowed = new HashSet<string>(filtered.Select(d => d.FilePath), StringComparer.OrdinalIgnoreCase);
                treeItems = FilterTreeNodes(_rootNodes, allowed);
            }
            else
            {
                treeItems = BuildTreeFromDocuments(filtered);
            }
            DocumentTree.ItemsSource = treeItems;
            _currentTreeItems = treeItems;
            TitleBlock.Text = $"Found {filtered.Count} document(s)";
            QueueTreeRestore(expandedKeys);
        }

        private void QueueTreeRestore(HashSet<string> expandedKeys)
        {
            Dispatcher.BeginInvoke(new Action(() =>
            {
                RestoreExpandedKeys(expandedKeys);
                SyncTreeSelection(_currentFilePath);
            }), DispatcherPriority.Loaded);
        }

        private void QueueTreeSelection(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath))
            {
                return;
            }

            Dispatcher.BeginInvoke(new Action(() => SyncTreeSelection(filePath)), DispatcherPriority.Background);
        }

        private void SyncTreeSelection(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath) || _currentTreeItems.Count == 0)
            {
                return;
            }

            var path = new List<LoreTreeItem>();
            if (!TryBuildPath(_currentTreeItems, filePath, path))
            {
                return;
            }

            SelectTreePath(path);
        }

        private static bool TryBuildPath(IEnumerable<LoreTreeItem> nodes, string filePath, List<LoreTreeItem> path)
        {
            foreach (var node in nodes)
            {
                path.Add(node);
                if (!string.IsNullOrEmpty(node.FilePath) &&
                    string.Equals(node.FilePath, filePath, StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }

                if (node.Children.Count > 0 && TryBuildPath(node.Children, filePath, path))
                {
                    return true;
                }

                path.RemoveAt(path.Count - 1);
            }

            return false;
        }

        private void SelectTreePath(IReadOnlyList<LoreTreeItem> path)
        {
            ItemsControl parent = DocumentTree;
            for (int i = 0; i < path.Count; i++)
            {
                var node = path[i];
                parent.UpdateLayout();
                var container = parent.ItemContainerGenerator.ContainerFromItem(node) as TreeViewItem;
                if (container == null)
                {
                    parent.UpdateLayout();
                    container = parent.ItemContainerGenerator.ContainerFromItem(node) as TreeViewItem;
                }

                if (container == null)
                {
                    return;
                }

                if (i < path.Count - 1)
                {
                    container.IsExpanded = true;
                    parent = container;
                    continue;
                }

                _suppressTreeSelection = true;
                container.IsSelected = true;
                _suppressTreeSelection = false;
                container.BringIntoView();
            }
        }

        private HashSet<string> CaptureExpandedKeys()
        {
            var keys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            DocumentTree.UpdateLayout();
            foreach (var item in DocumentTree.Items)
            {
                if (DocumentTree.ItemContainerGenerator.ContainerFromItem(item) is TreeViewItem container)
                {
                    CaptureExpandedKeys(container, new List<string>(), keys);
                }
            }
            return keys;
        }

        private static void CaptureExpandedKeys(TreeViewItem item, List<string> path, HashSet<string> keys)
        {
            if (item.DataContext is not LoreTreeItem node)
            {
                return;
            }

            var newPath = new List<string>(path) { node.Title };
            if (item.IsExpanded)
            {
                keys.Add(BuildNodeKey(node, newPath));
            }

            for (int i = 0; i < item.Items.Count; i++)
            {
                if (item.ItemContainerGenerator.ContainerFromIndex(i) is TreeViewItem child)
                {
                    CaptureExpandedKeys(child, newPath, keys);
                }
            }
        }

        private void RestoreExpandedKeys(HashSet<string> keys)
        {
            if (keys.Count == 0)
            {
                return;
            }

            DocumentTree.UpdateLayout();
            foreach (var item in DocumentTree.Items)
            {
                if (DocumentTree.ItemContainerGenerator.ContainerFromItem(item) is TreeViewItem container)
                {
                    RestoreExpandedKeys(container, new List<string>(), keys);
                }
            }
        }

        private static void RestoreExpandedKeys(TreeViewItem item, List<string> path, HashSet<string> keys)
        {
            if (item.DataContext is not LoreTreeItem node)
            {
                return;
            }

            var newPath = new List<string>(path) { node.Title };
            string key = BuildNodeKey(node, newPath);
            if (keys.Contains(key))
            {
                item.IsExpanded = true;
                item.UpdateLayout();
            }

            if (!item.IsExpanded)
            {
                return;
            }

            for (int i = 0; i < item.Items.Count; i++)
            {
                if (item.ItemContainerGenerator.ContainerFromIndex(i) is TreeViewItem child)
                {
                    RestoreExpandedKeys(child, newPath, keys);
                }
            }
        }

        private static string BuildNodeKey(LoreTreeItem node, IReadOnlyList<string> path)
        {
            if (!string.IsNullOrEmpty(node.FilePath))
            {
                return $"file:{node.FilePath}";
            }
            return $"title:{string.Join(">", path)}";
        }

        private static List<LoreTreeItem> FilterTreeNodes(IEnumerable<LoreTreeItem> nodes, HashSet<string> allowedPaths)
        {
            var result = new List<LoreTreeItem>();
            foreach (var node in nodes)
            {
                var filteredChildren = FilterTreeNodes(node.Children, allowedPaths);
                bool include = (!string.IsNullOrEmpty(node.FilePath) && allowedPaths.Contains(node.FilePath))
                    || filteredChildren.Count > 0;
                if (!include)
                {
                    continue;
                }

                var clone = new LoreTreeItem
                {
                    Title = node.Title,
                    FilePath = node.FilePath,
                    RelativePath = node.RelativePath,
                    IsIndex = node.IsIndex,
                    Order = node.Order,
                    Children = filteredChildren
                };
                result.Add(clone);
            }

            return result;
        }

        private static List<LoreTreeItem> BuildTreeFromDocuments(IEnumerable<LoreDocument> documents)
        {
            var roots = new Dictionary<string, LoreTreeItem>(StringComparer.OrdinalIgnoreCase);

            foreach (var doc in documents)
            {
                if (!roots.TryGetValue(doc.SourceDir, out var root))
                {
                    root = new LoreTreeItem { Title = doc.SourceDir };
                    roots[doc.SourceDir] = root;
                }
                AddDocumentToTree(root, doc);
            }

            foreach (var root in roots.Values)
            {
                SortTree(root);
            }

            string[] orderedRoots = { "Lore Book" };
            var ordered = new List<LoreTreeItem>();
            foreach (var name in orderedRoots)
            {
                if (roots.TryGetValue(name, out var root))
                {
                    ordered.Add(root);
                }
            }

            foreach (var root in roots.Values)
            {
                if (!ordered.Contains(root))
                {
                    ordered.Add(root);
                }
            }

            return ordered;
        }

        private void ContentBrowser_NavigationStarting(object sender, CoreWebView2NavigationStartingEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(e.Uri))
                return;

            if (IsRenderHtml(e.Uri))
            {
                // Allow navigation to the rendered HTML file within the WebView.
                return;
            }

            if (TryHandleInternalNavigation(e.Uri))
            {
                e.Cancel = true;
                return;
            }

            if (e.Uri.StartsWith("about:", StringComparison.OrdinalIgnoreCase))
                return;

            if (e.Uri.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                e.Uri.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                e.Uri.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase))
            {
                e.Cancel = true;
                TryOpenExternal(e.Uri);
                return;
            }

            if (e.Uri.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
            {
                e.Cancel = true;
                MainWindow.SetStatus("Lore Browser: File link not recognized");
                return;
            }

            e.Cancel = true;
            MainWindow.SetStatus("Lore Browser: Link not recognized");
        }

        private void ContentBrowser_NavigationCompleted(object sender, CoreWebView2NavigationCompletedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_pendingAnchor))
                return;

            string anchor = _pendingAnchor!;
            _pendingAnchor = null;
            _ = ContentBrowser.ExecuteScriptAsync($"location.hash='{EscapeForScript(anchor)}'");
            UpdateNavButtons();
        }

        private void ContentBrowser_NewWindowRequested(object? sender, CoreWebView2NewWindowRequestedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(e.Uri))
            {
                e.Handled = true;
                return;
            }

            if (IsRenderHtml(e.Uri))
            {
                e.Handled = true;
                ContentBrowser.Source = new Uri(e.Uri);
                return;
            }

            if (TryHandleInternalNavigation(e.Uri))
            {
                e.Handled = true;
                return;
            }

            if (e.Uri.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                e.Uri.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                e.Uri.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase))
            {
                e.Handled = true;
                TryOpenExternal(e.Uri);
                return;
            }

            if (e.Uri.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
            {
                e.Handled = true;
                MainWindow.SetStatus("Lore Browser: File link not recognized");
                return;
            }

            e.Handled = true;
            MainWindow.SetStatus("Lore Browser: Link not recognized");
        }

        private void HandleDocUri(string uri)
        {
            string target = uri;
            string? fragment = null;
            int hashIndex = target.IndexOf('#');
            if (hashIndex >= 0)
            {
                fragment = target.Substring(hashIndex + 1);
                target = target.Substring(0, hashIndex);
            }

            string decodedPath;
            if (target.StartsWith("doc://", StringComparison.OrdinalIgnoreCase))
            {
                decodedPath = Uri.UnescapeDataString(target.Substring("doc://".Length));
            }
            else if (target.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
            {
                decodedPath = new Uri(target).LocalPath;
            }
            else
            {
                decodedPath = target;
            }

            if (File.Exists(decodedPath))
            {
                bool isSame = string.Equals(decodedPath, _currentFilePath, StringComparison.OrdinalIgnoreCase);
                if (isSame)
                {
                    if (!string.IsNullOrWhiteSpace(fragment))
                    {
                        TryScrollToAnchor(fragment);
                    }
                    return;
                }

                LoadDocumentByPath(decodedPath, fragment, true);
            }
        }

        private bool TryHandleInternalNavigation(string uri)
        {
            if (uri.StartsWith("data:", StringComparison.OrdinalIgnoreCase))
            {
                if (TryHandleDataLink(uri))
                {
                    return true;
                }
                MainWindow.SetStatus("Lore Browser: Unresolved data link");
                return true;
            }

            if (uri.StartsWith("doc://", StringComparison.OrdinalIgnoreCase))
            {
                HandleDocUri(uri);
                return true;
            }

            if (uri.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
            {
                string? localPath = null;
                try
                {
                    localPath = new Uri(uri).LocalPath;
                }
                catch
                {
                    return true;
                }

                if (string.IsNullOrWhiteSpace(localPath))
                {
                    return true;
                }

                if (!IsRenderHtml(uri))
                {
                    string? resolved = ResolveMarkdownTarget(localPath);
                    if (resolved != null)
                    {
                        string? fragment = TryExtractFragment(uri);
                        LoadDocumentByPath(resolved, fragment?.TrimStart('#'), true);
                        return true;
                    }

                    string extension = Path.GetExtension(localPath);
                    if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                        extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
                    {
                        LoadHtmlDocument(localPath, true);
                        return true;
                    }
                }

                // Swallow file:// navigations we can't resolve to avoid shell prompts.
                return true;
            }

            // Handle plain local paths or relative paths without scheme.
            if (!uri.Contains("://", StringComparison.OrdinalIgnoreCase))
            {
                string candidate = uri;
                if (!Path.IsPathRooted(candidate) && !string.IsNullOrWhiteSpace(_currentFilePath))
                {
                    string baseDir = Path.GetDirectoryName(_currentFilePath) ?? string.Empty;
                    candidate = Path.GetFullPath(Path.Combine(baseDir, candidate));
                }

                if (File.Exists(candidate) || Directory.Exists(candidate))
                {
                    string? resolved = ResolveMarkdownTarget(candidate);
                    if (resolved != null)
                    {
                        LoadDocumentByPath(resolved, null, true);
                        return true;
                    }

                    string extension = Path.GetExtension(candidate);
                    if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                        extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
                    {
                        LoadHtmlDocument(candidate, true);
                        return true;
                    }
                }

                return true;
            }

            return false;
        }

        private static string? TryExtractFragment(string uri)
        {
            int hashIndex = uri.IndexOf('#');
            if (hashIndex < 0 || hashIndex == uri.Length - 1)
            {
                return hashIndex >= 0 ? "#" : null;
            }
            return uri.Substring(hashIndex);
        }

        private bool IsRenderHtml(string uri)
        {
            if (!uri.StartsWith("file://", StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            if (string.IsNullOrWhiteSpace(_lastRenderPath))
            {
                return false;
            }

            try
            {
                string local = new Uri(uri).LocalPath;
                return string.Equals(Path.GetFullPath(local), Path.GetFullPath(_lastRenderPath), StringComparison.OrdinalIgnoreCase);
            }
            catch
            {
                return false;
            }
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            if (_backStack.Count == 0)
                return;

            var entry = _backStack.Pop();
            if (!string.IsNullOrWhiteSpace(_currentFilePath))
            {
                _forwardStack.Push(new LoreHistoryEntry(_currentFilePath!, _currentIsHtml));
            }

            _suppressHistory = true;
            if (entry.IsHtml)
            {
                LoadHtmlDocument(entry.FilePath, false);
            }
            else
            {
                LoadDocumentByPath(entry.FilePath, entry.Anchor, false);
            }
            _suppressHistory = false;
            UpdateNavButtons();
        }

        private void ForwardButton_Click(object sender, RoutedEventArgs e)
        {
            if (_forwardStack.Count == 0)
                return;

            var entry = _forwardStack.Pop();
            if (!string.IsNullOrWhiteSpace(_currentFilePath))
            {
                _backStack.Push(new LoreHistoryEntry(_currentFilePath!, _currentIsHtml));
            }

            _suppressHistory = true;
            if (entry.IsHtml)
            {
                LoadHtmlDocument(entry.FilePath, false);
            }
            else
            {
                LoadDocumentByPath(entry.FilePath, entry.Anchor, false);
            }
            _suppressHistory = false;
            UpdateNavButtons();
        }

        private void HomeButton_Click(object sender, RoutedEventArgs e)
        {
            if (_homeDocument == null)
            {
                return;
            }

            _backStack.Clear();
            _forwardStack.Clear();
            _suppressHistory = true;
            SelectDefaultDocument(_homeDocument);
            _suppressHistory = false;
            UpdateNavButtons();
        }

        private void UpdateNavButtons()
        {
            if (BackButton != null)
            {
                BackButton.IsEnabled = _backStack.Count > 0;
            }
            if (ForwardButton != null)
            {
                ForwardButton.IsEnabled = _forwardStack.Count > 0;
            }
            if (HomeButton != null)
            {
                HomeButton.IsEnabled = _homeDocument != null;
            }
        }

        private bool TryHandleDataLink(string uri)
        {
            // data: URLs are used as the base for NavigateToString; relative links can end up as data:foo/bar.md
            string dataPart = uri.Substring("data:".Length);
            if (dataPart.Contains(','))
            {
                return false;
            }

            string linkPath = dataPart;
            string? fragment = null;
            int hashIndex = dataPart.IndexOf('#');
            if (hashIndex >= 0)
            {
                fragment = dataPart.Substring(hashIndex + 1);
                linkPath = dataPart.Substring(0, hashIndex);
            }

            if (string.IsNullOrWhiteSpace(linkPath) || string.IsNullOrWhiteSpace(_currentFilePath))
            {
                return false;
            }

            string baseDir = Path.GetDirectoryName(_currentFilePath) ?? string.Empty;
            string resolved = Path.GetFullPath(Path.Combine(baseDir, linkPath));

            if (File.Exists(resolved) && resolved.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
            {
                LoadDocumentByPath(resolved, fragment);
                return true;
            }

            return false;
        }

        private static string EscapeForScript(string value)
        {
            return value.Replace("\\", "\\\\").Replace("'", "\\'");
        }

        private static string? ResolveMarkdownTarget(string pathOrDir)
        {
            if (File.Exists(pathOrDir))
            {
                if (pathOrDir.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
                {
                    return pathOrDir;
                }

                if (pathOrDir.EndsWith(".html", StringComparison.OrdinalIgnoreCase) ||
                    pathOrDir.EndsWith(".htm", StringComparison.OrdinalIgnoreCase))
                {
                    string mdPath = Path.ChangeExtension(pathOrDir, ".md");
                    if (File.Exists(mdPath))
                    {
                        return mdPath;
                    }
                }

                // If extension is missing, try .md
                if (Path.GetExtension(pathOrDir) == string.Empty)
                {
                    string mdPath = pathOrDir + ".md";
                    if (File.Exists(mdPath))
                    {
                        return mdPath;
                    }
                }
                return null;
            }

            if (Directory.Exists(pathOrDir))
            {
                string[] candidates = new[]
                {
                    Path.Combine(pathOrDir, "_index.md"),
                    Path.Combine(pathOrDir, "index.md"),
                    Path.Combine(pathOrDir, "README.md"),
                    Path.Combine(pathOrDir, "readme.md")
                };

                foreach (var candidate in candidates)
                {
                    if (File.Exists(candidate))
                    {
                        return candidate;
                    }
                }
            }

            if (Path.GetExtension(pathOrDir) == string.Empty)
            {
                string mdPath = pathOrDir + ".md";
                if (File.Exists(mdPath))
                {
                    return mdPath;
                }
            }

            return null;
        }

        private static string GetRenderPathForDoc(string filePath)
        {
            string hash = ComputeHash(filePath);
            string fileName = Path.GetFileNameWithoutExtension(filePath);
            string safeName = Regex.Replace(fileName, "[^a-zA-Z0-9_-]", "_");
            string file = $"{safeName}-{hash}.html";
            return Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditor", "LoreRender", file);
        }

        private static string ComputeHash(string input)
        {
            using var sha1 = SHA1.Create();
            byte[] data = sha1.ComputeHash(Encoding.UTF8.GetBytes(input));
            return string.Concat(data.Take(6).Select(b => b.ToString("x2")));
        }
    }

    /// <summary>
    /// Represents a lore document.
    /// </summary>
    public class LoreDocument
    {
        public string Title { get; set; } = "";
        public string FilePath { get; set; } = "";
        public string RelativePath { get; set; } = "";
        public string SourceDir { get; set; } = "";
        public bool IsIndex { get; set; }
        public int? Order { get; set; }
    }

    /// <summary>
    /// Represents a node in the lore tree.
    /// </summary>
    public class LoreTreeItem
    {
        public string Title { get; set; } = "";
        public string? FilePath { get; set; }
        public string? RelativePath { get; set; }
        public bool IsIndex { get; set; }
        public int? Order { get; set; }
        public List<LoreTreeItem> Children { get; set; } = new();
    }
}
