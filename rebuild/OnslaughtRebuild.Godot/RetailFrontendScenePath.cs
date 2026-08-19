// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The Godot scene's player-visible frontend path: Lost Toys / opening
/// FMV / splash skip, then CFEPIntro click-to-start, then CFEPMain row
/// accept (Campaign / Options / Exit), then Options apply pulse and
/// dropdown confirm / right-click cancel.
///
/// <para>No Godot types. <see cref="RetailFrontendFlow"/> and
/// <see cref="RetailStartupSequence"/> call the same accept/skip predicates
/// the focused test drives, so the host is not a second copy of the
/// session Confirm path.</para>
/// </summary>
public sealed class RetailFrontendScenePath
{
    public bool StartupMediaActive { get; private set; }

    public static bool IsStartupSuppressed(IReadOnlyList<string> arguments) =>
        RetailStartupSchedule.IsSuppressedByArguments(arguments);

    public static bool AcceptsStartupSkip(bool left, bool middle, bool right, int dik) =>
        RetailFmvSkip.AcceptsMouseLatch(left, middle, right)
        || RetailFmvSkip.AcceptsDefaultSkipScanCode(dik);

    public static bool AcceptsClickToStartMouse(
        RetailFrontendScreen screen,
        float x,
        float y) =>
        screen == RetailFrontendScreen.ClickToStart
        && RetailClickToStartInput.AcceptsMouseAt(x, y);

    public static bool AcceptsClickToStartKey(RetailFrontendScreen screen, int dik) =>
        screen == RetailFrontendScreen.ClickToStart
        && RetailClickToStartInput.AcceptsDefaultConfirmScanCode(dik);

    public static bool CanAcceptMainMenuRow(RetailFrontendSession session, int index)
    {
        ArgumentNullException.ThrowIfNull(session);
        return session.Screen == RetailFrontendScreen.MainMenu
            && index >= 0
            && index < session.Items.Count
            && session.Items[index].IsAvailable;
    }

    public void Begin(IReadOnlyList<string> arguments)
    {
        ArgumentNullException.ThrowIfNull(arguments);
        StartupMediaActive = !IsStartupSuppressed(arguments);
    }

    public void CompleteStartup() => StartupMediaActive = false;

    public bool TrySkipStartup(bool left, bool middle, bool right, int dik)
    {
        if (!StartupMediaActive || !AcceptsStartupSkip(left, middle, right, dik))
        {
            return false;
        }

        StartupMediaActive = false;
        return true;
    }

    public bool TryAcceptClickToStartMouse(RetailFrontendSession session, float x, float y)
    {
        ArgumentNullException.ThrowIfNull(session);
        if (StartupMediaActive || !AcceptsClickToStartMouse(session.Screen, x, y))
        {
            return false;
        }

        return session.Confirm() == RetailFrontendSignal.PageChanged
            && session.Screen == RetailFrontendScreen.MainMenu;
    }

    public bool TryAcceptClickToStartKey(RetailFrontendSession session, int dik)
    {
        ArgumentNullException.ThrowIfNull(session);
        if (StartupMediaActive || !AcceptsClickToStartKey(session.Screen, dik))
        {
            return false;
        }

        return session.Confirm() == RetailFrontendSignal.PageChanged
            && session.Screen == RetailFrontendScreen.MainMenu;
    }

    public bool TryAcceptMainMenuRow(RetailFrontendSession session, int index)
    {
        ArgumentNullException.ThrowIfNull(session);
        if (StartupMediaActive || !CanAcceptMainMenuRow(session, index))
        {
            return false;
        }

        session.SelectMainIndex(index);
        return session.Confirm() == RetailFrontendSignal.PageChanged;
    }

    /// <summary>
    /// Right-mouse latch SET into the expanded-list cancel leftover.
    /// The helper fields sit idle on the frontend page.
    /// </summary>
    public static bool AcceptsOptionsPointerCancel(bool rightDown) =>
        RetailOptionsDropdownListCancel.Applies(
            helperNonzero: false,
            latch: RetailFrontendLatchToButton.Set(rightDown));

    public static bool ApplyPulseIsPending(RetailOptionsMenu menu)
    {
        ArgumentNullException.ThrowIfNull(menu);
        return RetailOptionsApplyPulse.ShouldPulse(menu.HasPendingChanges);
    }

    public bool TryConfirmOptions(RetailOptionsMenu menu, out RetailOptionsSignal signal) =>
        TryConfirmOptions(menu, StartupMediaActive, out signal);

    public static bool TryConfirmOptions(
        RetailOptionsMenu menu,
        bool startupMediaActive,
        out RetailOptionsSignal signal)
    {
        ArgumentNullException.ThrowIfNull(menu);
        signal = RetailOptionsSignal.None;
        if (startupMediaActive)
        {
            return false;
        }

        signal = menu.Confirm();
        return signal != RetailOptionsSignal.None;
    }

    public bool TryCancelOptionsDropdown(RetailOptionsMenu menu, bool rightDown)
    {
        ArgumentNullException.ThrowIfNull(menu);
        if (StartupMediaActive || !AcceptsOptionsPointerCancel(rightDown))
        {
            return false;
        }

        return menu.CancelExpanded();
    }
}
