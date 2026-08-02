using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using Microsoft.UI.Xaml;
using Onslaught___Career_Editor;
using WinRT.Interop;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// Listens for the trainer's key combinations while the trainer is watching a running game.
    ///
    /// Two things about this class deserve more care than its size suggests.
    ///
    /// The first is that a registered hotkey is taken from the entire machine. While one is live
    /// the combination reaches nothing else - not the game, not the browser behind it. So it is
    /// registered only while the trainer is attached and released the moment it is not, and
    /// <see cref="Start"/> reports which combinations it could not get rather than leaving a key
    /// that looks live and does nothing.
    ///
    /// The second is that catching <c>WM_HOTKEY</c> in WinUI 3 means putting our own code in the
    /// window's message path, and a fault there does not throw somewhere tidy - it takes the
    /// window with it. So the subclass procedure handles exactly one message, swallows anything
    /// thrown by the handler it calls, and forwards everything else untouched. The delegate is
    /// held in a field because the window keeps a raw pointer to it: letting it be collected is a
    /// crash, and it is the kind that happens minutes later and looks like something else.
    ///
    /// This never sends input. It only asks Windows to route a combination here instead of
    /// elsewhere, which is why it is not covered by the announce-first rule that governs
    /// synthetic input.
    /// </summary>
    internal sealed class TrainerHotkeyListener : IDisposable
    {
        private const int WmHotkey = 0x0312;
        private const uint SubclassId = 0xB4A0;

        private readonly IntPtr _windowHandle;
        private readonly Action<TrainerHotkeyAction> _onPressed;
        private readonly List<int> _registered = new();

        // Held so the GC cannot collect a delegate Windows is holding a raw pointer to.
        private readonly SubclassProc _subclassProc;

        private bool _subclassed;
        private bool _disposed;

        public TrainerHotkeyListener(Window window, Action<TrainerHotkeyAction> onPressed)
        {
            ArgumentNullException.ThrowIfNull(window);
            _onPressed = onPressed ?? throw new ArgumentNullException(nameof(onPressed));
            _windowHandle = WindowNative.GetWindowHandle(window);
            _subclassProc = SubclassProcedure;
        }

        public bool IsListening => _registered.Count > 0;

        /// <summary>
        /// Claims the combinations. Returns the display names of any that could not be claimed,
        /// which is not a failure of this app - another program already owns them - but is
        /// something the person pressing the key needs to be told.
        /// </summary>
        public IReadOnlyList<string> Start()
        {
            if (_disposed || IsListening)
                return Array.Empty<string>();

            if (!_subclassed)
            {
                _subclassed = SetWindowSubclass(_windowHandle, _subclassProc, SubclassId, IntPtr.Zero);
                if (!_subclassed)
                {
                    // Without the message hook a registration would swallow the combination and
                    // deliver it nowhere, which is worse than not registering at all.
                    var everyBinding = new List<string>();
                    foreach (TrainerHotkey binding in TrainerHotkeys.Bindings)
                        everyBinding.Add(binding.Display);
                    return everyBinding;
                }
            }

            var unavailable = new List<string>();
            foreach (TrainerHotkey binding in TrainerHotkeys.Bindings)
            {
                if (RegisterHotKey(_windowHandle, binding.Id, binding.Modifiers, binding.VirtualKey))
                    _registered.Add(binding.Id);
                else
                    unavailable.Add(binding.Display);
            }

            return unavailable;
        }

        /// <summary>Gives every combination back to the rest of the machine.</summary>
        public void Stop()
        {
            foreach (int id in _registered)
                UnregisterHotKey(_windowHandle, id);

            _registered.Clear();
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            _disposed = true;
            Stop();

            if (_subclassed)
            {
                RemoveWindowSubclass(_windowHandle, _subclassProc, SubclassId);
                _subclassed = false;
            }
        }

        private IntPtr SubclassProcedure(
            IntPtr hWnd,
            uint message,
            IntPtr wParam,
            IntPtr lParam,
            uint subclassId,
            IntPtr referenceData)
        {
            if (message == WmHotkey)
            {
                TrainerHotkey? binding = TrainerHotkeys.ForId((int)wParam);
                if (binding is not null)
                {
                    try
                    {
                        _onPressed(binding.Action);
                    }
                    catch (Exception)
                    {
                        // Deliberately swallowed. We are inside the window procedure; letting this
                        // out would take the window down over a missed keystroke. The page shows
                        // trainer state continuously, so a hotkey that did not land is visible
                        // without an error being raised from here.
                    }

                    return IntPtr.Zero;
                }
            }

            return DefSubclassProc(hWnd, message, wParam, lParam);
        }

        private delegate IntPtr SubclassProc(
            IntPtr hWnd,
            uint message,
            IntPtr wParam,
            IntPtr lParam,
            uint subclassId,
            IntPtr referenceData);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint modifiers, uint virtualKey);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        [DllImport("comctl32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool SetWindowSubclass(
            IntPtr hWnd,
            SubclassProc callback,
            uint subclassId,
            IntPtr referenceData);

        [DllImport("comctl32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool RemoveWindowSubclass(IntPtr hWnd, SubclassProc callback, uint subclassId);

        [DllImport("comctl32.dll")]
        private static extern IntPtr DefSubclassProc(IntPtr hWnd, uint message, IntPtr wParam, IntPtr lParam);
    }
}
