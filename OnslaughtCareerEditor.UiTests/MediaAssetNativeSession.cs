using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal sealed class MediaAssetNativeSession : IDisposable
{
    private static readonly TimeSpan GracefulExitTimeout = TimeSpan.FromSeconds(5);
    private static readonly TimeSpan KillExitTimeout = TimeSpan.FromSeconds(5);

    private MediaAssetNativeSession(
        Application app,
        UIA3Automation automation,
        Window window,
        string executablePath,
        ReceiptBoundAppIdentity identity,
        string applicationPayloadSha256,
        NativeWinUiOwnedProcessIdentity ownedProcessIdentity)
    {
        App = app;
        Automation = automation;
        Window = window;
        ExecutablePath = executablePath;
        Identity = identity;
        ApplicationPayloadSha256 = applicationPayloadSha256;
        OwnedProcessIdentity = ownedProcessIdentity;
    }

    internal Application App { get; }

    internal UIA3Automation Automation { get; }

    internal Window Window { get; }

    internal string ExecutablePath { get; }

    internal ReceiptBoundAppIdentity Identity { get; }

    internal string ApplicationPayloadSha256 { get; }

    private NativeWinUiOwnedProcessIdentity OwnedProcessIdentity { get; }

    internal static MediaAssetNativeSession Launch(
        string executablePath,
        string appDataDirectory,
        string initialTag,
        string expectedExecutableSha256,
        string expectedProductAssemblySha256,
        string expectedApplicationPayloadSha256,
        IReadOnlyDictionary<string, string> additionalEnvironment)
    {
        string executable = Path.GetFullPath(executablePath);
        string productAssembly = Path.Combine(
            Path.GetDirectoryName(executable)!,
            "OnslaughtCareerEditor.WinUI.dll");
        Assert.Multiple(() =>
        {
            Assert.That(File.Exists(executable), Is.True, $"Repository WinUI executable is missing: {executable}");
            Assert.That(File.Exists(productAssembly), Is.True, $"Repository WinUI product assembly is missing: {productAssembly}");
            Assert.That(initialTag, Is.AnyOf("media", "assets"));
        });

        string executableHash = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(executable)));
        string productAssemblyHash = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(productAssembly)));
        string applicationPayloadHash = MediaAssetNativeApplicationPayload.Compute(Path.GetDirectoryName(executable)!);
        Assert.Multiple(() =>
        {
            Assert.That(executableHash, Is.EqualTo(expectedExecutableSha256));
            Assert.That(productAssemblyHash, Is.EqualTo(expectedProductAssemblySha256));
            Assert.That(applicationPayloadHash, Is.EqualTo(expectedApplicationPayloadSha256));
        });

        Directory.CreateDirectory(appDataDirectory);
        var startInfo = new ProcessStartInfo(executable)
        {
            WorkingDirectory = Path.GetDirectoryName(executable)!,
        };
        startInfo.Environment["APPDATA"] = Path.GetFullPath(appDataDirectory);
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = Path.GetFullPath(appDataDirectory);
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = initialTag;
        foreach ((string name, string value) in additionalEnvironment)
        {
            startInfo.Environment[name] = value;
        }

        Application? app = null;
        UIA3Automation? automation = null;
        NativeWinUiOwnedProcessIdentity? ownedProcessIdentity = null;
        try
        {
            DateTime launchRequestedUtc = DateTime.UtcNow;
            app = Application.Launch(startInfo);
            ownedProcessIdentity = NativeWinUiOwnedProcessIdentity.Capture(
                app.ProcessId,
                executable,
                launchRequestedUtc);
            automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            var operations = new FlaUiReceiptBoundVisualCaptureOperations(app, window, executable);
            ReceiptBoundAppIdentity identity = operations.ReadIdentity();
            Assert.Multiple(() =>
            {
                Assert.That(identity.ExecutableSha256, Is.EqualTo(executableHash));
                Assert.That(identity.ProductAssemblySha256, Is.EqualTo(productAssemblyHash));
                Assert.That(
                    MediaAssetNativeApplicationPayload.Compute(Path.GetDirectoryName(executable)!),
                    Is.EqualTo(applicationPayloadHash));
                Assert.That(identity.MainWindowHandle, Is.Not.EqualTo(IntPtr.Zero));
                Assert.That(identity.UiaNativeWindowHandle, Is.EqualTo(identity.MainWindowHandle));
                Assert.That(identity.WindowOwnerProcessId, Is.EqualTo(identity.ProcessId));
                Assert.That(identity.ProcessId, Is.EqualTo(ownedProcessIdentity.ProcessId));
                Assert.That(identity.ProcessStartTimeUtc, Is.EqualTo(ownedProcessIdentity.ProcessStartTimeUtc));
                Assert.That(identity.ExecutablePath, Is.EqualTo(ownedProcessIdentity.ExecutablePath).IgnoreCase);
            });
            return new MediaAssetNativeSession(
                app,
                automation,
                window,
                executable,
                identity,
                applicationPayloadHash,
                ownedProcessIdentity);
        }
        catch
        {
            NativeWinUiSessionResourceCleanup.Run(
                () => automation?.Dispose(),
                () => CloseOwnedApp(app, ownedProcessIdentity));
            throw;
        }
    }

    public void Dispose()
    {
        NativeWinUiSessionResourceCleanup.Run(
            Automation.Dispose,
            () => CloseOwnedApp(App, OwnedProcessIdentity));
    }

    internal void ValidateApplicationPayload()
    {
        Assert.That(
            MediaAssetNativeApplicationPayload.Compute(Path.GetDirectoryName(ExecutablePath)!),
            Is.EqualTo(ApplicationPayloadSha256),
            "The Toolkit-owned native application payload changed during Media/Asset acceptance.");
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        bool handleReady = Retry.WhileFalse(
            () => !app.HasExited && app.MainWindowHandle != IntPtr.Zero,
            TimeSpan.FromSeconds(30)).Success;
        Assert.That(handleReady, Is.True, "The repository WinUI launch did not expose a main HWND.");

        Window? window = Retry.WhileNull(
            () =>
            {
                try
                {
                    return automation.FromHandle(app.MainWindowHandle).AsWindow();
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(30)).Result;
        Assert.That(window, Is.Not.Null, "UIA could not bind the repository WinUI main HWND.");
        return window!;
    }

    private static void CloseOwnedApp(
        Application? app,
        NativeWinUiOwnedProcessIdentity? ownedProcessIdentity)
    {
        if (app is null || app.HasExited)
        {
            return;
        }

        if (ownedProcessIdentity is null)
        {
            app.CloseTimeout = GracefulExitTimeout;
            app.Close(killIfCloseFails: true);
            if (!app.HasExited)
            {
                throw new InvalidOperationException(
                    "The exact FlaUI-bound WinUI process remained alive before a launch receipt could be established.");
            }
            return;
        }

        Process? process = null;
        try
        {
            process = Process.GetProcessById(app.ProcessId);
            NativeWinUiOwnedProcessCleanup.CloseOrKill(
                () =>
                {
                    process.Refresh();
                    string processPath = process.MainModule?.FileName
                        ?? throw new InvalidOperationException("The owned WinUI executable path is unavailable during cleanup.");
                    ownedProcessIdentity.Validate(
                        process.Id,
                        process.StartTime.ToUniversalTime(),
                        processPath);
                },
                () => process.HasExited,
                () => process.CloseMainWindow(),
                timeout => process.WaitForExit(checked((int)Math.Ceiling(timeout.TotalMilliseconds))),
                () => process.Kill(entireProcessTree: true),
                GracefulExitTimeout,
                KillExitTimeout);
        }
        catch (ArgumentException) when (app.HasExited)
        {
            // Exact process exited between the initial check and handle acquisition.
        }
        finally
        {
            process?.Dispose();
        }
    }
}
