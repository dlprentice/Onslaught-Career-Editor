// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Package-boundary checks use only owned folders and marker launchers, with no real processes or profiles.</summary>
internal static class CePackageSafetyTests
{
    internal static async Task RunAsync(string outputDirectory, Checks check)
    {
        check.Suite("CE package safety");
        string root = Path.Combine(outputDirectory, "ce-package-safety");
        string package = Path.Combine(root, "package"), user = Path.Combine(root, "user");
        string backups = Path.Combine(root, "backups"), nested = Path.Combine(package, "nested", "user");
        Directory.CreateDirectory(package);
        Directory.CreateDirectory(user);
        Directory.CreateDirectory(backups);
        string launcher = Path.Combine(package, OperatingSystem.IsWindows() ? OnslaughtCe.WindowsLauncher : "onslaught-ce");
        File.WriteAllText(launcher, "test-only launcher marker; never run");
        File.WriteAllText(Path.Combine(package, OnslaughtCe.LinuxLauncher), "test-only launcher marker; never run");
        check.That(!CeInstallation.Inspect(launcher, package).Ok && !CeInstallation.Inspect(launcher, nested).Ok &&
            !Directory.Exists(nested), "The CE user folder cannot be the package or an uncreated descendant of it.");
        check.That(CeInstallation.Inspect(launcher, Path.Combine(root, "package-user")).Ok,
            "An adjacent user folder sharing the package name's prefix remains valid.");
        check.That(Refuses(package, package) && Refuses(nested, package) && !Refuses(user, package),
            "The operation-time folder guard distinguishes the package, its descendants and external folders.");
        check.That(RefusesAny(package) && RefusesAny(nested) && !RefusesAny(user) &&
            !RefusesAny(Path.Combine(root, "package-user")),
            "Package markers protect the package and uncreated nested folders even without a selected launcher.");
        check.That(!CeInstallation.ResolveUserFolder(name => name == "BEA_USER_DIR" ? nested : null, home: root).Ok,
            "An environment-selected CE user folder inside a package is refused before launcher discovery.");
        string windowsPackage = Path.Combine(root, "windows-package");
        Directory.CreateDirectory(windowsPackage);
        File.WriteAllText(Path.Combine(windowsPackage, OnslaughtCe.WindowsLauncher), "test-only launcher marker; never run");
        check.That(RefusesAny(Path.Combine(windowsPackage, "nested", "user")) &&
            !CeInstallation.Inspect(launcher, Path.Combine(windowsPackage, "user")).Ok,
            "A Windows package's marker protects its descendants even when another package is selected.");
        string? Env(string name) => name == "PATH" ? package : null;
        check.That(CeInstallation.Find(launcher, nested, Env, home: root) is null &&
            CeInstallation.FindPackageFolder(launcher, Env, home: root) == package &&
            CeInstallation.InspectPackageFolder(launcher).Value == package,
            "An unsafe user folder cannot hide the selected package identity from career and backup checks.");

        if (OperatingSystem.IsLinux())
        {
            string alias = Path.Combine(root, "package-alias"), userAlias = Path.Combine(root, "user-alias");
            Directory.CreateSymbolicLink(alias, package);
            Directory.CreateSymbolicLink(userAlias, package);
            check.That(!CeInstallation.Inspect(alias, package).Ok &&
                !CeInstallation.Inspect(launcher, Path.Combine(userAlias, "missing", "user")).Ok &&
                Refuses(Path.Combine(userAlias, "missing", "backups"), package) && Refuses(nested, alias) &&
                RefusesAny(Path.Combine(userAlias, "missing", "user")),
                "Package aliases and linked user or backup ancestors cannot evade package containment checks.");
            check.That(CeInstallation.Inspect(alias, user).Value?.LauncherPath == launcher,
                "A linked launcher package with an external user folder resolves to its actual package.");
            Directory.CreateSymbolicLink(Path.Combine(package, "user-outside"), user);
            check.That(!CeInstallation.Inspect(launcher, Path.Combine(alias, "user-outside")).Ok &&
                Refuses(Path.Combine(alias, "user-outside", "missing"), package) &&
                RefusesAny(Path.Combine(alias, "user-outside", "missing")),
                "A route through package links is refused even if its final directory resolves back outside the package.");
            string packageChild = Path.Combine(package, "child"), childAlias = Path.Combine(root, "child-alias");
            Directory.CreateDirectory(packageChild);
            Directory.CreateSymbolicLink(childAlias, packageChild);
            check.That(RefusesAny(Path.Combine(childAlias, "missing", "user")),
                "An alias directly into a package child is checked against that child's resolved ancestors.");
            string launcherAliasFolder = Path.Combine(root, "bin");
            Directory.CreateDirectory(launcherAliasFolder);
            string launcherAlias = Path.Combine(launcherAliasFolder, "onslaught-ce");
            File.CreateSymbolicLink(launcherAlias, launcher);
            check.That(!CeInstallation.Inspect(launcherAlias, nested).Ok &&
                CeInstallation.InspectPackageFolder(launcherAlias).Value == package,
                "A launcher link retains the package that updates replace, even when user-folder validation fails.");

            string laterUser = Path.Combine(root, "user-linked-later");
            CeInstallation earlier = CeInstallation.Inspect(launcher, laterUser).Value!;
            Directory.CreateSymbolicLink(laterUser, package);
            bool invoked = false;
            var play = earlier.Launch(_ => { invoked = true; return true; });
            var version = await earlier.ReadVersionAsync(read: (_, _) =>
            {
                invoked = true;
                return Task.FromResult("Onslaught CE v0.1.2, build fixture");
            });
            check.That(!play.Ok && !version.Ok && !invoked && play.Message.Contains("outside the CE package folder", StringComparison.Ordinal),
                "Play and version reads recheck a user folder changed into a package link, preserving the refusal reason.");
        }

        string path = Path.Combine(user, "ce.ini");
        const string original = "update_check=1\nrecord_sessions=0\n";
        File.WriteAllText(path, original);
        CeSettings settings = CeSettings.Read(user).Value!;
        DateTime now = new(2026, 10, 23, 12, 0, 0);
        string packageBackups = Path.Combine(package, "backups");
        Directory.CreateDirectory(packageBackups);
        check.That(!settings.Save(false, true, package, () => false, now, packageRoot: package).Ok &&
            !settings.Save(false, true, packageBackups, () => false, now, packageRoot: package).Ok &&
            Directory.GetFileSystemEntries(packageBackups).Length == 0 && File.ReadAllText(path) == original,
            "ce.ini backups inside the package or a nested folder refuse before creating a backup or editing settings.");
        check.That(!settings.Save(false, true, package, () => false, now).Ok &&
            !settings.Save(false, true, packageBackups, () => false, now).Ok &&
            Directory.GetFileSystemEntries(packageBackups).Length == 0 && File.ReadAllText(path) == original,
            "Settings backups inside a package are also blocked when no package root was selected or supplied.");

        string packagedUser = Path.Combine(package, "user");
        Directory.CreateDirectory(packagedUser);
        string packagedSettingsPath = Path.Combine(packagedUser, "ce.ini");
        File.WriteAllText(packagedSettingsPath, original);
        CeSettings packagedSettings = CeSettings.Read(packagedUser).Value!;
        check.That(!packagedSettings.Save(false, true, backups, () => false, now, packageRoot: package).Ok &&
            !packagedSettings.Save(false, true, backups, () => false, now).Ok &&
            Directory.GetFileSystemEntries(backups).Length == 0 && File.ReadAllText(packagedSettingsPath) == original,
            "A retained settings snapshot inside the package refuses before backup or editing, with or without a selected package.");

        string latePackage = Path.Combine(root, "markers-before-swap");
        Directory.CreateDirectory(latePackage);
        string latePath = Path.Combine(latePackage, "ce.ini");
        File.WriteAllText(latePath, original);
        CeSettings beforeMarkers = CeSettings.Read(latePackage).Value!;
        InstallReceipt marked = beforeMarkers.Save(false, true, backups, () => false, now,
            beforeSwap: () => File.WriteAllText(Path.Combine(latePackage, OnslaughtCe.WindowsLauncher), "test-only launcher marker; never run"));
        check.That(!marked.Ok && marked.BackupFolder is string prior && File.ReadAllText(Path.Combine(prior, "ce.ini")) == original &&
            File.ReadAllText(latePath) == original,
            "Package markers introduced after backup are rechecked before a settings swap without a selected package.");

        if (OperatingSystem.IsLinux())
        {
            string backupAlias = Path.Combine(root, "backup-alias");
            Directory.CreateSymbolicLink(backupAlias, packageBackups);
            check.That(!settings.Save(false, true, backupAlias, () => false, now, packageRoot: package).Ok &&
                !settings.Save(false, true, packageBackups, () => false, now, packageRoot: Path.Combine(root, "package-alias")).Ok &&
                Directory.GetFileSystemEntries(packageBackups).Length == 0 && File.ReadAllText(path) == original,
                "Settings backup checks resolve links in either the chosen backup folder or package folder.");

            string packageAtSwap = Path.Combine(root, "package-linked-before-swap");
            InstallReceipt changed = settings.Save(false, true, backups, () => false, now,
                beforeSwap: () => Directory.CreateSymbolicLink(packageAtSwap, user), packageRoot: packageAtSwap);
            check.That(!changed.Ok && changed.BackupFolder is string recovery && File.Exists(Path.Combine(recovery, "ce.ini")) &&
                File.ReadAllText(path) == original,
                "The settings publisher rechecks package containment immediately before its swap and preserves the recovery copy.");
        }
        InstallReceipt saved = settings.Save(false, true, backups, () => false, now, packageRoot: package);
        check.That(saved.Ok && saved.BackupFolder is string externalBackup &&
            File.ReadAllText(Path.Combine(externalBackup, "ce.ini")) == original &&
            File.ReadAllText(path) == "update_check=0\nrecord_sessions=1\n",
            "An external CE user folder and backup folder still support a verified settings change.");
    }

    private static bool Refuses(string folder, string package)
    {
        try { CeInstallation.RejectFolderInPackage(folder, package, "The folder"); return false; }
        catch (IOException) { return true; }
    }

    private static bool RefusesAny(string folder)
    {
        try { CeInstallation.RejectFolderInAnyPackage(folder, "The folder"); return false; }
        catch (IOException) { return true; }
    }
}
