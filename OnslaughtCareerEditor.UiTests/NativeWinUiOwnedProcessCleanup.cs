namespace OnslaughtCareerEditor.UiTests;

internal static class NativeWinUiOwnedProcessCleanup
{
    internal static void CloseOrKill(
        Action validateIdentity,
        Func<bool> hasExited,
        Action requestClose,
        Func<TimeSpan, bool> waitForExit,
        Action kill,
        TimeSpan gracefulTimeout,
        TimeSpan killTimeout)
    {
        ArgumentNullException.ThrowIfNull(validateIdentity);
        ArgumentNullException.ThrowIfNull(hasExited);
        ArgumentNullException.ThrowIfNull(requestClose);
        ArgumentNullException.ThrowIfNull(waitForExit);
        ArgumentNullException.ThrowIfNull(kill);

        if (hasExited())
        {
            return;
        }

        validateIdentity();

        Exception? gracefulError = null;
        try
        {
            requestClose();
            if (waitForExit(gracefulTimeout) || hasExited())
            {
                return;
            }
        }
        catch (Exception ex)
        {
            gracefulError = ex;
        }

        if (hasExited())
        {
            return;
        }

        validateIdentity();

        Exception? killError = null;
        try
        {
            kill();
            if (waitForExit(killTimeout) || hasExited())
            {
                return;
            }
        }
        catch (Exception ex)
        {
            killError = ex;
            try
            {
                if (hasExited())
                {
                    return;
                }
            }
            catch (Exception exitCheckError)
            {
                killError = new AggregateException(killError, exitCheckError);
            }
        }

        var errors = new List<Exception>();
        if (gracefulError is not null)
        {
            errors.Add(gracefulError);
        }
        if (killError is not null)
        {
            errors.Add(killError);
        }
        else
        {
            errors.Add(new TimeoutException($"Kill did not produce exit within {killTimeout}."));
        }

        throw new AggregateException("The exact owned WinUI process remained alive after bounded close and kill.", errors);
    }
}
