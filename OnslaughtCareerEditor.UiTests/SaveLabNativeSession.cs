using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal sealed class SaveLabNativeSession : IDisposable
{
    private SaveLabNativeSession(
        Application app,
        UIA3Automation automation,
        Window window,
        string executablePath,
        ReceiptBoundAppIdentity identity)
    {
        App = app;
        Automation = automation;
        Window = window;
        ExecutablePath = executablePath;
        Identity = identity;
    }

    internal Application App { get; }

    internal UIA3Automation Automation { get; }

    internal Window Window { get; }

    internal string ExecutablePath { get; }

    internal ReceiptBoundAppIdentity Identity { get; }

    internal static SaveLabNativeSession Launch(
        string executablePath,
        string appDataDirectory,
        string initialSaveTab,
        string expectedExecutableSha256,
        string expectedProductAssemblySha256,
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
        });

        string executableHash = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(executable)));
        string productAssemblyHash = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(productAssembly)));
        Assert.Multiple(() =>
        {
            Assert.That(executableHash, Is.EqualTo(expectedExecutableSha256), "WinUI executable changed after the outer runner build receipt.");
            Assert.That(productAssemblyHash, Is.EqualTo(expectedProductAssemblySha256), "WinUI product assembly changed after the outer runner build receipt.");
        });

        Directory.CreateDirectory(appDataDirectory);
        var startInfo = new ProcessStartInfo(executable)
        {
            WorkingDirectory = Path.GetDirectoryName(executable)!,
        };
        startInfo.Environment["APPDATA"] = Path.GetFullPath(appDataDirectory);
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = Path.GetFullPath(appDataDirectory);
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = initialSaveTab;
        foreach ((string name, string value) in additionalEnvironment)
        {
            startInfo.Environment[name] = value;
        }

        Application? app = null;
        UIA3Automation? automation = null;
        try
        {
            app = Application.Launch(startInfo);
            automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            var operations = new FlaUiReceiptBoundVisualCaptureOperations(app, window, executable);
            ReceiptBoundAppIdentity identity = operations.ReadIdentity();
            Assert.Multiple(() =>
            {
                Assert.That(identity.ExecutableSha256, Is.EqualTo(executableHash));
                Assert.That(identity.ProductAssemblySha256, Is.EqualTo(productAssemblyHash));
                Assert.That(identity.MainWindowHandle, Is.Not.EqualTo(IntPtr.Zero));
                Assert.That(identity.UiaNativeWindowHandle, Is.EqualTo(identity.MainWindowHandle));
                Assert.That(identity.WindowOwnerProcessId, Is.EqualTo(identity.ProcessId));
            });
            return new SaveLabNativeSession(app, automation, window, executable, identity);
        }
        catch
        {
            NativeWinUiSessionResourceCleanup.Run(
                () => automation?.Dispose(),
                () => CloseOwnedApp(app));
            throw;
        }
    }

    public void Dispose()
    {
        NativeWinUiSessionResourceCleanup.Run(
            Automation.Dispose,
            () => CloseOwnedApp(App));
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

    private static void CloseOwnedApp(Application? app)
    {
        if (app is null)
        {
            return;
        }

        try
        {
            app.Close();
        }
        catch
        {
            // The harness owns this exact launch and may use the bounded kill fallback below.
        }

        try
        {
            if (!app.HasExited)
            {
                app.Kill();
            }
        }
        catch
        {
            // The outer runner's exact process census is the final cleanup authority.
        }
    }
}
