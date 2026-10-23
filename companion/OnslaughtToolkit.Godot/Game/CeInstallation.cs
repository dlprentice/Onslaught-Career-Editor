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
        return Outcome<string>.Success(full, "CE user folder found.");
    }

    /// <summary>A chosen launcher, or a package folder containing it. BEA itself is never accepted.</summary>
    public static Outcome<CeInstallation> Inspect(string path, string userFolder, bool? windows = null)
    {
        try
        {
            bool onWindows = windows ?? OperatingSystem.IsWindows();
            string expected = onWindows ? OnslaughtCe.WindowsLauncher : "onslaught-ce";
            string full = Path.GetFullPath(Directory.Exists(path) ? Path.Combine(path, expected) : path);
            FileInfo file = new(full);
            if (file.LinkTarget is not null) full = file.ResolveLinkTarget(returnFinalTarget: true)?.FullName ?? full;
            StringComparison comparison = onWindows ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
            if (!Path.GetFileName(full).Equals(expected, comparison) || !File.Exists(full) ||
                !onWindows && !File.Exists(Path.Combine(Path.GetDirectoryName(full)!, OnslaughtCe.LinuxLauncher)))
                return Outcome<CeInstallation>.Refusal($"Choose the CE package's {expected} launcher, not the bea game program.");
            if (!Path.IsPathFullyQualified(userFolder))
                return Outcome<CeInstallation>.Refusal("CE's user folder must be an absolute path.");
            return Outcome<CeInstallation>.Success(new CeInstallation(full, Path.GetFullPath(userFolder)), "CE launcher found.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            return Outcome<CeInstallation>.Refusal("The CE launcher could not be inspected: " + error.Message);
        }
    }

    /// <summary>Remembered choice first, then PATH and the usual per-user bin folder; no recursive disk search.</summary>
    public static CeInstallation? Find(string? remembered, string userFolder, Func<string, string?>? environment = null,
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
            if (Inspect(path, userFolder, onWindows).Value is CeInstallation installation) return installation;
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

    public Outcome<string> Launch(Func<ProcessStartInfo, bool>? start = null)
    {
        if (!Inspect(LauncherPath, UserFolder).Ok) return Outcome<string>.Refusal("The selected CE launcher is no longer available.");
        try
        {
            bool launched = start is not null ? start(StartInfo(versionOnly: false)) : StartLauncher(StartInfo(versionOnly: false));
            return launched ? Outcome<string>.Success(LauncherPath, "Started the Onslaught CE launcher. It checks and applies updates itself.") :
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
        if (!Inspect(LauncherPath, UserFolder).Ok) return Outcome<CeVersion>.Refusal("The selected CE launcher is no longer available.");
        try
        {
            string output = await (read is null ? RunVersionAsync(StartInfo(versionOnly: true), cancellationToken) :
                read(StartInfo(versionOnly: true), cancellationToken));
            return ParseVersion(output);
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
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        return full.Equals(folder, comparison) || full.StartsWith(folder + Path.DirectorySeparatorChar, comparison);
    }
}

public sealed record CeVersion(string Version, string Build, string Display);
