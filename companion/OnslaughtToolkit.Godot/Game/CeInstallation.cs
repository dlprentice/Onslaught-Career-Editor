// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Diagnostics;
using System.Text;
using System.Text.RegularExpressions;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// A CE package and its separate writable user folder. Contract: Onslaught CE commit
/// 72a44140c6db3e093cc07b1bed40a0584fdfecd2, port/tools/package.py and port/updater/ce_launch.c.
/// Packages may be extracted anywhere; finding a launcher never creates or changes a user folder.
/// </summary>
public sealed partial record CeInstallation(string LauncherPath, string UserFolder)
{
    public string Folder => Path.GetDirectoryName(LauncherPath)!;
    public string SettingsPath => Path.Combine(UserFolder, "ce.ini");
    public string SavegamesPath => Path.Combine(UserFolder, "savegames");

    /// <summary>CE's actual precedence, rather than the conservative exclusion list in OnslaughtCe.UserFolders.</summary>
    public static Outcome<string> ResolveUserFolder(Func<string, string?>? environment = null, bool? windows = null, string? home = null)
    {
        try
        {
            return ResolveFolder(environment, windows, home);
        }
        catch (Exception error) when (error is ArgumentException or NotSupportedException or IOException)
        {
            return Outcome<string>.Refusal("CE's user folder could not be resolved: " + error.Message);
        }
    }

    private static Outcome<string> ResolveFolder(Func<string, string?>? environment, bool? windows, string? home)
    {
        environment ??= Environment.GetEnvironmentVariable;
        bool onWindows = windows ?? OperatingSystem.IsWindows();
        home ??= Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        string? chosen = environment("BEA_USER_DIR");
        if (string.IsNullOrEmpty(chosen))
        {
            string? root = environment(onWindows ? "APPDATA" : "XDG_DATA_HOME");
            chosen = !string.IsNullOrEmpty(root) ? Path.Combine(root, onWindows ? "Onslaught CE" : "onslaught-ce") :
                !onWindows && !string.IsNullOrEmpty(home) ? Path.Combine(home, ".local", "share", "onslaught-ce") : null;
        }
        if (string.IsNullOrEmpty(chosen) || !Path.IsPathFullyQualified(chosen))
            return Outcome<string>.Refusal("CE's user folder is not an absolute path. Choose an absolute BEA_USER_DIR before opening the companion.");
        string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(chosen));
        string? drive = Path.GetPathRoot(full);
        if (string.Equals(full, Path.TrimEndingDirectorySeparator(drive ?? ""), StringComparison.OrdinalIgnoreCase) ||
            !string.IsNullOrEmpty(home) && IsInside(home, full))
            return Outcome<string>.Refusal("CE's user folder must not be the home folder, its parent or a drive root.");
        RejectFolderInAnyPackage(full, "CE's user folder");
        return Outcome<string>.Success(full, "CE user folder found.");
    }

    /// <summary>A chosen launcher, or a package folder containing it. BEA itself is never accepted.</summary>
    public static Outcome<CeInstallation> Inspect(string path, string userFolder, bool? windows = null)
    {
        try
        {
            Outcome<string> launcher = InspectLauncher(path, windows);
            if (launcher.Value is not string full) return Outcome<CeInstallation>.Refusal(launcher.Message);
            if (!Path.IsPathFullyQualified(userFolder))
                return Outcome<CeInstallation>.Refusal("CE's user folder must be an absolute path.");
            RejectFolderInAnyPackage(userFolder, "CE's user folder");
            RejectFolderInPackage(userFolder, Path.GetDirectoryName(full)!, "CE's user folder");
            return Outcome<CeInstallation>.Success(new CeInstallation(full, Path.GetFullPath(userFolder)), "CE launcher found.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            return Outcome<CeInstallation>.Refusal("The CE launcher could not be inspected: " + error.Message);
        }
    }

    /// <summary>Retains the package identity even when its configured user folder is unsafe.</summary>
    public static Outcome<string> InspectPackageFolder(string path, bool? windows = null)
    {
        Outcome<string> launcher = InspectLauncher(path, windows);
        return launcher.Value is string full ? Outcome<string>.Success(Path.GetDirectoryName(full)!, "CE package found.") : launcher;
    }

    private static Outcome<string> InspectLauncher(string path, bool? windows)
    {
        try
        {
            bool onWindows = windows ?? OperatingSystem.IsWindows();
            string expected = onWindows ? OnslaughtCe.WindowsLauncher : "onslaught-ce";
            string full = Path.GetFullPath(Directory.Exists(path) ? Path.Combine(path, expected) : path);
            full = SteamLibraries.Canonical(full) ?? throw new IOException("The CE launcher path could not be resolved.");
            StringComparison comparison = onWindows ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
            if (!Path.GetFileName(full).Equals(expected, comparison) || !File.Exists(full) ||
                !onWindows && !File.Exists(Path.Combine(Path.GetDirectoryName(full)!, OnslaughtCe.LinuxLauncher)))
                return Outcome<string>.Refusal($"Choose the CE package's {expected} launcher, not the bea game program.");
            return Outcome<string>.Success(full, "CE launcher found.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            return Outcome<string>.Refusal("The CE launcher could not be inspected: " + error.Message);
        }
    }

    /// <summary>
    /// Writable user data and backups must survive replacement of the selected launcher package. Check both the
    /// named paths and every resolved ancestor, including when the writable folder does not exist yet. Call again
    /// before writes: a successful discovery is not a lasting guarantee about a directory or its links.
    /// </summary>
    public static void RejectFolderInPackage(string folder, string packageRoot, string label)
        => RejectFolderInTree(folder, packageRoot, label,
            " must be outside the CE package folder, which launcher updates replace.");

    internal static void RejectFolderInTree(string folder, string packageRoot, string label, string reason)
    {
        if (!Path.IsPathFullyQualified(folder) || !Path.IsPathFullyQualified(packageRoot))
            throw new IOException("The CE package and " + label + " must use absolute paths.");
        string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(folder));
        string package = Path.GetFullPath(packageRoot);
        string resolvedPackage = SteamLibraries.Canonical(package) ?? throw new IOException("The CE package folder could not be resolved safely.");
        foreach (string current in AncestorChain(full))
        {
            string resolved = SteamLibraries.Canonical(current) ?? throw new IOException(label + " could not be resolved safely.");
            // An alias can enter the package and then follow another link back out. That route still depends on
            // package contents surviving an update, even when the final directory is physically outside it.
            if (IsInside(current, package) || IsInside(current, resolvedPackage) || IsInside(resolved, resolvedPackage))
                throw new IOException(label + reason);
        }
    }

    /// <summary>
    /// Protects writable folders even before a launcher is selected. Package markers in either platform's layout
    /// are sufficient; discovery does not execute a launcher or search beyond the supplied folder's ancestors.
    /// </summary>
    public static void RejectFolderInAnyPackage(string folder, string label)
    {
        if (!Path.IsPathFullyQualified(folder)) throw new IOException(label + " must use an absolute path.");
        HashSet<string> inspected = new(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (string current in AncestorChain(Path.GetFullPath(folder)))
        {
            Check(current);
            string resolved = SteamLibraries.Canonical(current) ?? throw new IOException(label + " could not be resolved safely.");
            foreach (string ancestor in AncestorChain(resolved)) Check(ancestor);
        }

        void Check(string candidate)
        {
            if (!inspected.Add(candidate)) return;
            if (File.Exists(Path.Combine(candidate, OnslaughtCe.WindowsLauncher)) ||
                File.Exists(Path.Combine(candidate, "onslaught-ce")) && File.Exists(Path.Combine(candidate, OnslaughtCe.LinuxLauncher)))
                throw new IOException(label + " must be outside the CE package folder, which launcher updates replace.");
        }
    }

    private static IEnumerable<string> AncestorChain(string path)
    {
        for (string? current = Path.TrimEndingDirectorySeparator(path); current is not null; current = Path.GetDirectoryName(current))
            yield return current;
    }

    /// <summary>Remembered choice first, then PATH and the usual per-user bin folder; no recursive disk search.</summary>
    public static CeInstallation? Find(string? remembered, string userFolder, Func<string, string?>? environment = null,
        bool? windows = null, string? home = null)
    {
        string? package = FindPackageFolder(remembered, environment, windows, home);
        return package is null ? null : Inspect(package, userFolder, windows).Value;
    }

    /// <summary>Finds the selected package independently of whether its configured user folder can be used safely.</summary>
    public static string? FindPackageFolder(string? remembered, Func<string, string?>? environment = null,
        bool? windows = null, string? home = null)
    {
        environment ??= Environment.GetEnvironmentVariable;
        bool onWindows = windows ?? OperatingSystem.IsWindows();
        string expected = onWindows ? OnslaughtCe.WindowsLauncher : "onslaught-ce";
        List<string> paths = [];
        if (!string.IsNullOrEmpty(remembered)) paths.Add(remembered);
        foreach (string directory in (environment("PATH") ?? "").Split(onWindows ? ';' : ':', StringSplitOptions.RemoveEmptyEntries))
            if (Path.IsPathFullyQualified(directory)) paths.Add(Path.Combine(directory, expected));
        home ??= Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        if (!onWindows && !string.IsNullOrEmpty(home)) paths.Add(Path.Combine(home, ".local", "bin", expected));
        foreach (string path in paths.Distinct(onWindows ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal))
            if (InspectPackageFolder(path, onWindows).Value is string package) return package;
        return null;
    }

    /// <summary>Explicit environment ties the launched game to the folder shown in the companion.</summary>
    public ProcessStartInfo StartInfo(bool versionOnly)
    {
        ProcessStartInfo start = new(LauncherPath) { UseShellExecute = false, WorkingDirectory = Folder,
            RedirectStandardOutput = versionOnly, RedirectStandardError = versionOnly, CreateNoWindow = versionOnly };
        if (versionOnly) start.ArgumentList.Add("--version");
        start.Environment["BEA_USER_DIR"] = UserFolder;
        return start;
    }

    /// <summary>Where players are sent instead of starting an affected launcher.</summary>
    public const string MigrationUrl = "https://github.com/dlprentice/onslaught-ce#manual-migration-from-affected-launchers";

    /// <summary>
    /// Released CE launchers 0.1.0 to 0.1.6 delete neighbouring "&lt;package folder&gt;.old-*" paths when they start,
    /// even with update checks off, and CE's guidance is not to start them even to read a version. Before executing
    /// anything, the package's README.txt header (written by package.py since 0.1.0) must name 0.1.7 or later. An
    /// unreadable or missing header is refused: the companion cannot tell such a package is safe.
    /// </summary>
    public Outcome<string> CheckLauncherSafety() => CheckPackageSafety(Folder);

    public static Outcome<string> CheckPackageSafety(string packageFolder)
    {
        string? version;
        try
        {
            version = PackageVersion(packageFolder);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            version = null;
        }
        if (version is null)
            return Outcome<string>.Refusal("The companion could not read this CE package's version from its README.txt, so it " +
                "will not start it. Onslaught CE 0.1.0–0.1.6 launchers can delete neighbouring folders when they start. " +
                "Install 0.1.7 or later by hand into a new empty folder: " + MigrationUrl);
        if (IsAffectedVersion(version))
            return Outcome<string>.Refusal($"This package is Onslaught CE {version}. Its launcher can delete neighbouring " +
                "\"<program folder>.old-*\" paths when it starts, so the companion will not start it, not even to read its " +
                "version. Keep the old folder and its neighbours untouched and install 0.1.7 or later by hand into a new " +
                "empty folder: " + MigrationUrl);
        return Outcome<string>.Success(version, "CE package " + version + " is not an affected launcher.");
    }

    /// <summary>The version on README.txt's first line ("Onslaught CE X.Y[.Z] (preview)"), or null.</summary>
    public static string? PackageVersion(string packageFolder)
    {
        string path = Path.Combine(packageFolder, "README.txt");
        if (!File.Exists(path)) return null;
        byte[] buffer = new byte[256];
        int count;
        using (FileStream stream = File.OpenRead(path)) count = stream.ReadAtLeast(buffer, buffer.Length, throwOnEndOfStream: false);
        string text = Encoding.UTF8.GetString(buffer, 0, count);
        int end = text.IndexOfAny(['\r', '\n']);
        if (end < 0) return null;
        Match match = PackageHeader().Match(text[..end]);
        return match.Success ? match.Groups[1].Value : null;
    }

    /// <summary>0.1, 0.1.0 ... 0.1.6 are affected; anything unparsable counts as affected.</summary>
    public static bool IsAffectedVersion(string version)
    {
        string[] parts = version.Split('.');
        if (parts.Length is < 2 or > 3) return true;
        int[] numbers = new int[3];
        for (int i = 0; i < parts.Length; i++)
            if (!int.TryParse(parts[i], System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out numbers[i]))
                return true;
        return numbers[0] == 0 && numbers[1] == 1 && numbers[2] <= 6;
    }

    public Outcome<string> Launch(Func<ProcessStartInfo, bool>? start = null)
    {
        Outcome<CeInstallation> inspected = Inspect(LauncherPath, UserFolder);
        if (inspected.Value is not CeInstallation current) return Outcome<string>.Refusal(inspected.Message);
        Outcome<string> safety = current.CheckLauncherSafety();
        if (!safety.Ok) return Outcome<string>.Refusal(safety.Message);
        try
        {
            bool launched = start is not null ? start(current.StartInfo(versionOnly: false)) : StartLauncher(current.StartInfo(versionOnly: false));
            return launched ? Outcome<string>.Success(LauncherPath, "Started the Onslaught CE launcher.") :
                Outcome<string>.Refusal("The CE launcher could not be started.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or Win32Exception or InvalidOperationException)
        {
            return Outcome<string>.Refusal("The CE launcher could not be started: " + error.Message);
        }
    }

    public async Task<Outcome<CeVersion>> ReadVersionAsync(CancellationToken cancellationToken = default,
        Func<ProcessStartInfo, CancellationToken, Task<string>>? read = null)
    {
        Outcome<CeInstallation> inspected = Inspect(LauncherPath, UserFolder);
        if (inspected.Value is not CeInstallation current) return Outcome<CeVersion>.Refusal(inspected.Message);
        Outcome<string> safety = current.CheckLauncherSafety();
        if (safety.Value is not string packaged) return Outcome<CeVersion>.Refusal(safety.Message);
        try
        {
            string output = await (read is null ? RunVersionAsync(current.StartInfo(versionOnly: true), cancellationToken) :
                read(current.StartInfo(versionOnly: true), cancellationToken));
            Outcome<CeVersion> parsed = ParseVersion(output);
            // The README header chose to execute this launcher; its own answer must agree with it.
            if (parsed.Value is CeVersion reported && reported.Version != packaged)
                return Outcome<CeVersion>.Refusal($"The CE launcher reports version {reported.Version}, but its package says " +
                    $"{packaged}. The companion will not start a mixed package. Install 0.1.7 or later by hand into a new " +
                    "empty folder: " + MigrationUrl);
            return parsed;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or Win32Exception or InvalidOperationException or OperationCanceledException)
        {
            return Outcome<CeVersion>.Refusal("CE's version could not be read: " + error.Message);
        }
    }

    public static Outcome<CeVersion> ParseVersion(string output)
    {
        if (output.Length > 4096) return Outcome<CeVersion>.Refusal("CE's version reply was too long.");
        Match match = VersionLine().Match(output.Trim());
        return match.Success ? Outcome<CeVersion>.Success(new CeVersion(match.Groups[1].Value, match.Groups[2].Value, output.Trim()), "CE version read.") :
            Outcome<CeVersion>.Refusal("CE did not return a readable version. You can still start it from Home.");
    }

    [GeneratedRegex(@"\AOnslaught CE v([^\s,]+)(?: \([^\r\n]*\))?, build ([^\s,]+)\z", RegexOptions.CultureInvariant)]
    private static partial Regex VersionLine();

    [GeneratedRegex(@"\AOnslaught CE ([0-9]+\.[0-9]+(?:\.[0-9]+)?)(?: \([^\r\n]*\))?\z", RegexOptions.CultureInvariant)]
    private static partial Regex PackageHeader();

    private static bool StartLauncher(ProcessStartInfo start)
    {
        using Process? process = Process.Start(start);
        return process is not null;
    }

    private static async Task<string> RunVersionAsync(ProcessStartInfo start, CancellationToken cancellationToken)
    {
        using Process process = new() { StartInfo = start };
        if (!process.Start()) throw new IOException("The launcher did not start.");
        using CancellationTokenSource deadline = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        deadline.CancelAfter(TimeSpan.FromSeconds(5));
        try
        {
            Task<string> output = ReadBoundedAsync(process.StandardOutput, deadline.Token);
            Task<string> error = ReadBoundedAsync(process.StandardError, deadline.Token);
            await Task.WhenAll(process.WaitForExitAsync(deadline.Token), output, error);
            if (process.ExitCode != 0) throw new IOException($"The launcher returned exit code {process.ExitCode}.");
            return await output;
        }
        finally
        {
            // This Process instance is ours; never kill by name or touch another launcher.
            if (!process.HasExited)
            {
                process.Kill();
                await process.WaitForExitAsync(CancellationToken.None);
            }
        }
    }

    private static async Task<string> ReadBoundedAsync(StreamReader reader, CancellationToken token)
    {
        StringBuilder text = new();
        char[] buffer = new char[512];
        bool oversized = false;
        int count;
        while ((count = await reader.ReadAsync(buffer.AsMemory(), token)) > 0)
        {
            if (text.Length + count <= 4096) text.Append(buffer, 0, count);
            else oversized = true; // Keep draining to avoid filling a pipe, but retain only bounded output.
        }
        if (oversized) throw new IOException("The launcher returned too much output.");
        return text.ToString();
    }

    private static bool IsInside(string path, string folder)
    {
        string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        folder = Path.TrimEndingDirectorySeparator(Path.GetFullPath(folder));
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        return full.Equals(folder, comparison) || full.StartsWith(Path.EndsInDirectorySeparator(folder) ? folder :
            folder + Path.DirectorySeparatorChar, comparison);
    }
}

public sealed record CeVersion(string Version, string Build, string Display);
