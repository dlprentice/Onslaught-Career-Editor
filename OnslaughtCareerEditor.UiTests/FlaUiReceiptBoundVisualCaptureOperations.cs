using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;

namespace OnslaughtCareerEditor.UiTests;

internal sealed class FlaUiReceiptBoundVisualCaptureOperations : IReceiptBoundVisualCaptureOperations
{
    private const int GwlExstyle = -20;
    private const long WsExTopmost = 0x00000008L;
    private const int SwHide = 0;
    private const int SwRestore = 9;
    private const uint SwpNoMove = 0x0002;
    private const uint SwpNoSize = 0x0001;
    private const uint SwpShowWindow = 0x0040;
    private static readonly IntPtr HwndTop = IntPtr.Zero;
    private static readonly IntPtr HwndTopmost = new(-1);
    private static readonly IntPtr HwndNotTopmost = new(-2);

    private readonly Application _app;
    private readonly Window _window;
    private readonly string _executablePath;
    private readonly string _productAssemblyPath;
    private readonly IntPtr _hwnd;

    public FlaUiReceiptBoundVisualCaptureOperations(Application app, Window window, string executablePath)
    {
        _app = app;
        _window = window;
        _executablePath = Path.GetFullPath(executablePath);
        _productAssemblyPath = Path.Combine(Path.GetDirectoryName(_executablePath)!, "OnslaughtCareerEditor.WinUI.dll");
        _hwnd = app.MainWindowHandle;
        Assert.That(_hwnd, Is.Not.EqualTo(IntPtr.Zero), "The receipt-bound Toolkit HWND must exist before capture setup.");
    }

    public ReceiptBoundAppIdentity ReadIdentity()
    {
        bool processAlive = !_app.HasExited;
        int processId = _app.ProcessId;
        DateTime processStartTimeUtc = DateTime.MinValue;
        string liveExecutablePath = string.Empty;
        string liveProductAssemblyPath = string.Empty;
        if (processAlive)
        {
            using Process process = Process.GetProcessById(processId);
            processStartTimeUtc = process.StartTime.ToUniversalTime();
            processAlive = !process.HasExited;
            liveExecutablePath = Path.GetFullPath(process.MainModule?.FileName ?? string.Empty);
            ProcessModule? productAssembly = process.Modules
                .Cast<ProcessModule>()
                .FirstOrDefault(module => string.Equals(
                    Path.GetFileName(module.FileName),
                    Path.GetFileName(_productAssemblyPath),
                    StringComparison.OrdinalIgnoreCase));
            Assert.That(productAssembly, Is.Not.Null, "The live Toolkit process must have the product assembly loaded before capture.");
            liveProductAssemblyPath = Path.GetFullPath(productAssembly!.FileName);
        }

        Assert.That(processAlive, Is.True, "The receipt-bound Toolkit process exited before identity capture.");
        Assert.That(liveExecutablePath, Is.EqualTo(_executablePath).IgnoreCase, "The live process image path must equal the expected Toolkit executable path.");
        Assert.That(liveProductAssemblyPath, Is.EqualTo(_productAssemblyPath).IgnoreCase, "The loaded product assembly path must equal the exact adjacent Toolkit product DLL.");
        uint threadId = GetWindowThreadProcessId(_hwnd, out uint windowOwnerProcessId);
        Assert.That(threadId, Is.Not.Zero, "GetWindowThreadProcessId failed for the receipt-bound Toolkit HWND.");
        Assert.That(windowOwnerProcessId, Is.EqualTo((uint)processId), "The receipt-bound Toolkit HWND owner PID does not match the live process PID.");
        string executableSha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(liveExecutablePath)));
        string productAssemblySha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(liveProductAssemblyPath)));
        IntPtr mainWindowHandle = _app.MainWindowHandle;
        IntPtr uiaNativeWindowHandle = new(_window.Properties.NativeWindowHandle.ValueOrDefault);
        var identity = new ReceiptBoundAppIdentity(
            processId,
            processStartTimeUtc,
            liveExecutablePath,
            executableSha256,
            liveProductAssemblyPath,
            productAssemblySha256,
            mainWindowHandle,
            uiaNativeWindowHandle,
            checked((int)windowOwnerProcessId),
            processAlive);
        TestContext.Progress.WriteLine(
            $"Guided-save capture receipt: PID={identity.ProcessId}; StartUtc={identity.ProcessStartTimeUtc:o}; " +
            $"Exe={identity.ExecutablePath}; ExeSha256={identity.ExecutableSha256}; ProductDll={identity.ProductAssemblyPath}; " +
            $"ProductDllSha256={identity.ProductAssemblySha256}; HWND=0x{identity.MainWindowHandle.ToInt64():X}; " +
            $"UIA=0x{identity.UiaNativeWindowHandle.ToInt64():X}; HwndOwnerPid={identity.WindowOwnerProcessId}; Alive={identity.ProcessAlive}.");
        return identity;
    }

    public ReceiptBoundWindowState ReadWindowState()
    {
        EnsureWindowExists();
        WINDOWPLACEMENT placement = ReadPlacement();
        return new ReceiptBoundWindowState(
            ReadBounds(),
            placement.showCmd,
            IsTopmost(),
            IsWindowVisible(_hwnd),
            ToRectangle(placement.rcNormalPosition),
            new Point(placement.ptMinPosition.X, placement.ptMinPosition.Y),
            new Point(placement.ptMaxPosition.X, placement.ptMaxPosition.Y),
            placement.flags);
    }

    public void ShowRestored()
    {
        EnsureWindowExists();
        _ = ShowWindow(_hwnd, SwRestore); // Return value is prior visibility, not success.
        WaitUntil(
            () => IsWindowVisible(_hwnd) && ReadPlacement().showCmd == 1,
            TimeSpan.FromSeconds(2),
            "ShowWindow(SW_RESTORE) did not produce a visible normal Toolkit window.");
    }

    public void PositionWindow(Rectangle bounds)
    {
        EnsureWindowExists();
        ThrowIfFalse(
            SetWindowPos(_hwnd, HwndTop, bounds.X, bounds.Y, bounds.Width, bounds.Height, SwpShowWindow),
            "SetWindowPos failed while positioning the receipt-bound Toolkit HWND.");
        Assert.That(ReadBounds(), Is.EqualTo(bounds), "GetWindowRect did not match the requested receipt-bound Toolkit rectangle.");
    }

    public void SetForeground()
    {
        EnsureWindowExists();
        ThrowIfFalse(SetForegroundWindow(_hwnd), "SetForegroundWindow failed for the receipt-bound Toolkit HWND.");
    }

    public void WaitForForegroundAndBounds(Rectangle bounds, TimeSpan timeout)
    {
        WaitUntil(
            () => GetForegroundWindow() == _hwnd && ReadBounds() == bounds,
            timeout,
            "The receipt-bound Toolkit HWND did not remain foreground with the exact requested GetWindowRect dimensions.");
    }

    public void SetTopmost()
    {
        EnsureWindowExists();
        ThrowIfFalse(
            SetWindowPos(_hwnd, HwndTopmost, 0, 0, 0, 0, SwpNoMove | SwpNoSize | SwpShowWindow),
            "SetWindowPos(HWND_TOPMOST) failed for the receipt-bound Toolkit HWND.");
        Assert.That(IsTopmost(), Is.True, "The receipt-bound Toolkit HWND did not enter TOPMOST state before capture.");
    }

    public GuidedSaveVisualMarker ReadMarker(string automationId)
    {
        AutomationElement? element = _window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
        Assert.That(element, Is.Not.Null, $"Expected guided-save visual marker: {automationId}");
        Rectangle windowBounds = ReadBounds();
        Rectangle elementBounds = element!.BoundingRectangle;
        return new GuidedSaveVisualMarker(
            automationId,
            new Rectangle(
                elementBounds.Left - windowBounds.Left,
                elementBounds.Top - windowBounds.Top,
                elementBounds.Width,
                elementBounds.Height));
    }

    public Bitmap CaptureBoundWindow(IntPtr hwnd, Rectangle bounds)
    {
        Assert.That(hwnd, Is.EqualTo(_hwnd), "Capture HWND must equal the launch receipt HWND.");
        Assert.That(new IntPtr(_window.Properties.NativeWindowHandle.ValueOrDefault), Is.EqualTo(_hwnd), "UIA NativeWindowHandle changed before FlaUI capture.");
        Assert.That(GetForegroundWindow(), Is.EqualTo(_hwnd), "FlaUI capture requires the receipt-bound Toolkit HWND to remain foreground.");
        Assert.That(ReadBounds(), Is.EqualTo(bounds), "FlaUI capture bounds must equal the exact receipt-bound HWND rectangle.");

        using CaptureImage capture = Capture.Element(_window);
        Assert.That(capture.Bitmap.Width, Is.EqualTo(bounds.Width), "FlaUI returned a bitmap wider or narrower than the bound HWND rectangle.");
        Assert.That(capture.Bitmap.Height, Is.EqualTo(bounds.Height), "FlaUI returned a bitmap taller or shorter than the bound HWND rectangle.");
        return (Bitmap)capture.Bitmap.Clone();
    }

    public void RestoreWindowState(ReceiptBoundWindowState state)
    {
        EnsureWindowExists();
        IntPtr topmostTarget = state.IsTopmost ? HwndTopmost : HwndNotTopmost;
        ThrowIfFalse(
            SetWindowPos(
                _hwnd,
                topmostTarget,
                state.Bounds.X,
                state.Bounds.Y,
                state.Bounds.Width,
                state.Bounds.Height,
                0),
            state.IsTopmost
                ? "SetWindowPos(HWND_TOPMOST) failed while restoring the original Toolkit window state."
                : "SetWindowPos(HWND_NOTOPMOST) failed while restoring the original Toolkit window state.");
        var placement = new WINDOWPLACEMENT
        {
            length = Marshal.SizeOf<WINDOWPLACEMENT>(),
            flags = state.PlacementFlags,
            showCmd = state.ShowCommand,
            ptMinPosition = new POINT { X = state.MinPosition.X, Y = state.MinPosition.Y },
            ptMaxPosition = new POINT { X = state.MaxPosition.X, Y = state.MaxPosition.Y },
            rcNormalPosition = ToRect(state.NormalBounds),
        };
        ThrowIfFalse(
            SetWindowPlacement(_hwnd, ref placement),
            "SetWindowPlacement failed while restoring the original Toolkit window state.");
        _ = ShowWindow(_hwnd, state.IsVisible ? state.ShowCommand : SwHide); // Return value is prior visibility, not success.
        WaitUntil(
            () => ReadBounds() == state.Bounds &&
                  PlacementMatches(ReadPlacement(), state) &&
                  IsWindowVisible(_hwnd) == state.IsVisible &&
                  IsTopmost() == state.IsTopmost,
            TimeSpan.FromSeconds(2),
            "The original Toolkit rectangle, show state, or topmost state was not restored.");
    }

    private void EnsureWindowExists()
    {
        Assert.That(IsWindow(_hwnd), Is.True, "The receipt-bound Toolkit HWND is no longer valid.");
    }

    private Rectangle ReadBounds()
    {
        ThrowIfFalse(GetWindowRect(_hwnd, out RECT rect), "GetWindowRect failed for the receipt-bound Toolkit HWND.");
        return Rectangle.FromLTRB(rect.Left, rect.Top, rect.Right, rect.Bottom);
    }

    private WINDOWPLACEMENT ReadPlacement()
    {
        var placement = new WINDOWPLACEMENT { length = Marshal.SizeOf<WINDOWPLACEMENT>() };
        ThrowIfFalse(GetWindowPlacement(_hwnd, ref placement), "GetWindowPlacement failed for the receipt-bound Toolkit HWND.");
        return placement;
    }

    private static bool PlacementMatches(WINDOWPLACEMENT actual, ReceiptBoundWindowState expected)
    {
        return actual.showCmd == expected.ShowCommand &&
               actual.flags == expected.PlacementFlags &&
               ToRectangle(actual.rcNormalPosition) == expected.NormalBounds &&
               new Point(actual.ptMinPosition.X, actual.ptMinPosition.Y) == expected.MinPosition &&
               new Point(actual.ptMaxPosition.X, actual.ptMaxPosition.Y) == expected.MaxPosition;
    }

    private static Rectangle ToRectangle(RECT rect) => Rectangle.FromLTRB(rect.Left, rect.Top, rect.Right, rect.Bottom);

    private static RECT ToRect(Rectangle rectangle) => new()
    {
        Left = rectangle.Left,
        Top = rectangle.Top,
        Right = rectangle.Right,
        Bottom = rectangle.Bottom,
    };

    private bool IsTopmost()
    {
        Marshal.SetLastPInvokeError(0);
        IntPtr extendedStyle = GetWindowLongPtr(_hwnd, GwlExstyle);
        if (extendedStyle == IntPtr.Zero)
        {
            int error = Marshal.GetLastWin32Error();
            Assert.That(error, Is.Zero, $"GetWindowLongPtr failed for the receipt-bound Toolkit HWND (Win32 {error}).");
        }

        return (extendedStyle.ToInt64() & WsExTopmost) != 0;
    }

    private static void WaitUntil(Func<bool> condition, TimeSpan timeout, string failureMessage)
    {
        Stopwatch stopwatch = Stopwatch.StartNew();
        while (stopwatch.Elapsed < timeout)
        {
            if (condition())
            {
                return;
            }

            Thread.Sleep(50);
        }

        Assert.Fail(failureMessage);
    }

    private static void ThrowIfFalse(bool result, string message)
    {
        if (result)
        {
            return;
        }

        int error = Marshal.GetLastWin32Error();
        Assert.Fail($"{message} Win32 error: {error}.");
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct WINDOWPLACEMENT
    {
        public int length;
        public int flags;
        public int showCmd;
        public POINT ptMinPosition;
        public POINT ptMaxPosition;
        public RECT rcNormalPosition;
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll")]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool GetWindowPlacement(IntPtr hWnd, ref WINDOWPLACEMENT lpwndpl);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPlacement(IntPtr hWnd, ref WINDOWPLACEMENT lpwndpl);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    private static extern bool IsWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW", SetLastError = true)]
    private static extern IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex);
}
