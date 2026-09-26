// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Media;

public sealed record MediaItem(string Name, string RelativePath, long Size, string Kind, string Format, string Extension)
{
    public string Support => "Metadata only";
    public string Classification => "Filename extension; contents not validated";
}

public sealed record MediaScan(bool Ok, bool Done, bool Complete, bool Cancelled, string Root, IReadOnlyList<MediaItem> Items,
    int Count, int Entries, int Directories, int SkippedLinks, int OtherFiles, int DepthSkips, int IssueCount,
    IReadOnlyList<string> Issues, string Message);

/// <summary>
/// A read-only filename and size inventory of one chosen folder. No payload is opened, decoded
/// or imported. Callers advance it in bounded <see cref="Step"/> batches and yield between them.
/// Link checks are metadata observations, not a transaction or identity guarantee.
/// </summary>
public sealed class MediaCatalog
{
    public const int DefaultDepth = 8, DefaultItems = 5000, DefaultEntries = 30000;

    private static readonly Dictionary<string, (string Kind, string Format)> Formats = new(StringComparer.Ordinal)
    {
        ["ogg"] = ("Audio/container", "Ogg"), ["wav"] = ("Audio", "WAVE"),
        ["mp3"] = ("Audio", "MPEG audio"), ["flac"] = ("Audio", "FLAC"),
        ["bik"] = ("Video", "Bink"), ["vid"] = ("Video/container", "VID"),
        ["ogv"] = ("Video", "Ogg video"), ["webm"] = ("Video", "WebM"),
        ["mp4"] = ("Video/container", "MP4"), ["avi"] = ("Video/container", "AVI"),
        ["png"] = ("Image", "PNG"), ["jpg"] = ("Image", "JPEG"),
        ["jpeg"] = ("Image", "JPEG"), ["bmp"] = ("Image", "BMP"),
        ["tga"] = ("Image", "TGA"), ["dds"] = ("Image", "DDS"),
        ["webp"] = ("Image", "WebP"), ["gif"] = ("Image", "GIF"),
        ["tif"] = ("Image", "TIFF"), ["tiff"] = ("Image", "TIFF"),
    };

    private static readonly EnumerationOptions Listing = new()
    {
        AttributesToSkip = 0, IgnoreInaccessible = false, RecurseSubdirectories = false, ReturnSpecialDirectories = false,
    };

    private readonly List<MediaItem> _items = [];
    private readonly List<string> _issues = [];
    private readonly Stack<(string Relative, int Depth)> _pending = new();
    private IEnumerator<FileSystemInfo>? _current;
    private string _root = "";
    private string _relative = "";
    private bool _ok, _complete, _cancelled;
    private int _depth, _maxDepth = DefaultDepth, _maxItems = DefaultItems, _maxEntries = DefaultEntries;
    private int _entries, _directories, _skippedLinks, _otherFiles, _depthSkips, _issueCount;

    public bool Done { get; private set; } = true;

    public MediaScan Begin(string root, int maxDepth = DefaultDepth, int maxItems = DefaultItems, int maxEntries = DefaultEntries)
    {
        CloseCurrent();
        Done = true;
        _ok = _complete = _cancelled = false;
        _items.Clear();
        _issues.Clear();
        _pending.Clear();
        _entries = _directories = _skippedLinks = _otherFiles = _depthSkips = _issueCount = 0;
        _root = root;
        string slashed = root.Replace('\\', '/');
        if (root.Trim().Length == 0 || root.Contains('\0') || slashed.Contains("://") || slashed.StartsWith("//") ||
            !Path.IsPathFullyQualified(root))
        {
            Issue("Choose an existing local folder using its absolute path.");
            return Result();
        }
        if (maxDepth is < 0 or > DefaultDepth || maxItems is < 1 or > DefaultItems || maxEntries is < 1 or > DefaultEntries)
        {
            Issue("The requested scan limits are outside the supported bounds.");
            return Result();
        }
        (_maxDepth, _maxItems, _maxEntries) = (maxDepth, maxItems, maxEntries);
        _root = Path.TrimEndingDirectorySeparator(Path.GetFullPath(root));
        if (HasLinkComponent(_root))
        {
            Issue("Choose the actual folder. A linked folder or linked parent is not scanned.");
            return Result();
        }
        if (!Directory.Exists(_root))
        {
            Issue("That folder is missing or cannot be accessed. Choose it again.");
            return Result();
        }
        _ok = _complete = true;
        Done = false;
        _pending.Push(("", 0));
        return Progress([]);
    }

    /// <summary>Examines at most <paramref name="budget"/> entries (clamped to 1–256) and returns the new items.</summary>
    public MediaScan Step(int budget = 64)
    {
        List<MediaItem> added = [];
        if (Done) return Progress(added);
        for (int operation = 0; operation < Math.Clamp(budget, 1, 256); operation++)
        {
            if (_current is null && !OpenNext())
            {
                if (_pending.Count == 0)
                {
                    Done = true;
                    break;
                }
                continue;
            }
            if (_entries >= _maxEntries)
            {
                StopAtLimit($"The {_maxEntries:N0}-entry scan limit was reached. Choose a smaller folder to see the remainder.");
                break;
            }
            FileSystemInfo? entry = NextEntry();
            if (entry is null)
            {
                CloseCurrent();
                continue;
            }
            _entries++;
            if (IsLink(entry))
            {
                _skippedLinks++;
                continue;
            }
            string relative = _relative.Length == 0 ? entry.Name : _relative + "/" + entry.Name;
            if (entry is DirectoryInfo)
            {
                if (_depth >= _maxDepth)
                {
                    _depthSkips++;
                    _complete = false;
                }
                else
                {
                    _pending.Push((relative, _depth + 1));
                }
                continue;
            }
            string extension = Path.GetExtension(entry.Name).TrimStart('.').ToLowerInvariant();
            if (!Formats.TryGetValue(extension, out (string Kind, string Format) format))
            {
                _otherFiles++;
                continue;
            }
            if (_items.Count >= _maxItems)
            {
                StopAtLimit($"The {_maxItems:N0}-media-item limit was reached. Choose a smaller folder to see the remainder.");
                break;
            }
            // The size is enumeration metadata; neither the file nor any codec is opened.
            long size = SizeOf(entry);
            if (size < 0) Issue($"Could not read the size of {relative}.");
            MediaItem item = new(entry.Name, relative, size, format.Kind, format.Format, extension);
            _items.Add(item);
            added.Add(item);
        }
        return Progress(added);
    }

    public void Cancel()
    {
        if (Done) return;
        _cancelled = true;
        _complete = false;
        Done = true;
        CloseCurrent();
        _pending.Clear();
    }

    public MediaScan Result() => Progress(_items.ToArray()) with { Issues = _issues.ToArray() };

    private MediaScan Progress(IReadOnlyList<MediaItem> items)
    {
        string message;
        if (!_ok)
        {
            message = _issues.Count > 0 ? _issues[0] : "Choose a folder to inspect.";
        }
        else if (!Done)
        {
            message = $"Scanning… {_items.Count:N0} media files found in {_entries:N0} examined entries.";
        }
        else if (_cancelled)
        {
            message = $"Scan cancelled. Showing {_items.Count:N0} files found so far; the list is incomplete.";
        }
        else if (!_complete)
        {
            message = $"Partial list: {_items.Count:N0} media files found. ";
            if (_depthSkips > 0) message += $"{_depthSkips:N0} folders were beyond the depth limit of {_maxDepth}. ";
            if (_issues.Count > 0) message += _issues[0];
        }
        else
        {
            message = _items.Count > 0 ? $"{_items.Count:N0} media files found. " : "No listed media file types were found. ";
            message += $"{_skippedLinks:N0} linked entries skipped; {_otherFiles:N0} other files omitted.";
        }
        return new MediaScan(_ok, Done, Done && _complete, _cancelled, _root, items, _items.Count, _entries, _directories,
            _skippedLinks, _otherFiles, _depthSkips, _issueCount, [], message.TrimEnd());
    }

    private bool OpenNext()
    {
        if (_pending.Count == 0) return false;
        (_relative, _depth) = _pending.Pop();
        string path = _relative.Length == 0 ? _root : Path.Combine(_root, _relative);
        string label = _relative.Length == 0 ? "(selected folder)" : _relative;
        if (HasLinkComponent(path))
        {
            _skippedLinks++;
            return false;
        }
        try
        {
            _current = new DirectoryInfo(path).EnumerateFileSystemInfos("*", Listing).GetEnumerator();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.Security.SecurityException)
        {
            Issue($"Could not read folder {label}.");
            return false;
        }
        _directories++;
        return true;
    }

    private FileSystemInfo? NextEntry()
    {
        try
        {
            return _current!.MoveNext() ? _current.Current : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.Security.SecurityException)
        {
            Issue($"Could not enumerate folder {(_relative.Length == 0 ? "(selected folder)" : _relative)}.");
            return null;
        }
    }

    private void CloseCurrent()
    {
        _current?.Dispose();
        _current = null;
    }

    private void StopAtLimit(string message)
    {
        Issue(message);
        Done = true;
        CloseCurrent();
        _pending.Clear();
    }

    private void Issue(string message)
    {
        _complete = false;
        _issueCount++;
        if (_issues.Count < 20) _issues.Add(message);
    }

    private static long SizeOf(FileSystemInfo entry)
    {
        try
        {
            return entry is FileInfo file ? file.Length : -1;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return -1;
        }
    }

    private static bool IsLink(FileSystemInfo entry)
    {
        try
        {
            return entry.LinkTarget is not null || entry.Attributes.HasFlag(FileAttributes.ReparsePoint);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return true;
        }
    }

    private static bool HasLinkComponent(string path)
    {
        string? current = Path.GetPathRoot(path);
        if (string.IsNullOrEmpty(current)) return false;
        foreach (string part in path[current.Length..].Split(['/', '\\'], StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            DirectoryInfo component = new(current);
            if (!component.Exists && !File.Exists(current)) return false;
            if (IsLink(component)) return true;
        }
        return false;
    }
}
