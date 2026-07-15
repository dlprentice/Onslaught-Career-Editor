namespace OnslaughtCareerEditor.UiTests;

public class NativeWinUiOwnedProcessCleanupTests
{
    [Test]
    public void CloseOrKill_ReturnsAfterGracefulExitWithoutKilling()
    {
        bool exited = false;
        bool killed = false;

        NativeWinUiOwnedProcessCleanup.CloseOrKill(
            () => { },
            () => exited,
            () => exited = true,
            _ => exited,
            () => killed = true,
            TimeSpan.Zero,
            TimeSpan.Zero);

        Assert.That(killed, Is.False);
    }

    [Test]
    public void CloseOrKill_UsesBoundedKillFallbackAndRequiresObservedExit()
    {
        bool exited = false;
        int waits = 0;

        NativeWinUiOwnedProcessCleanup.CloseOrKill(
            () => { },
            () => exited,
            () => throw new InvalidOperationException("close failed"),
            _ =>
            {
                waits++;
                return exited;
            },
            () => exited = true,
            TimeSpan.Zero,
            TimeSpan.Zero);

        Assert.That(waits, Is.EqualTo(1));
    }

    [Test]
    public void CloseOrKill_PropagatesWhenKillCannotProduceExit()
    {
        Assert.That(
            () => NativeWinUiOwnedProcessCleanup.CloseOrKill(
                () => { },
                () => false,
                () => throw new InvalidOperationException("close failed"),
                _ => false,
                () => throw new InvalidOperationException("kill failed"),
                TimeSpan.Zero,
                TimeSpan.Zero),
            Throws.TypeOf<AggregateException>()
                .With.Message.Contains("owned WinUI process remained alive"));
    }

    [Test]
    public void CloseOrKill_IdentityMismatchPreventsCloseAndKill()
    {
        bool closeRequested = false;
        bool killRequested = false;

        Assert.That(
            () => NativeWinUiOwnedProcessCleanup.CloseOrKill(
                () => throw new InvalidOperationException("identity mismatch"),
                () => false,
                () => closeRequested = true,
                _ => false,
                () => killRequested = true,
                TimeSpan.Zero,
                TimeSpan.Zero),
            Throws.TypeOf<InvalidOperationException>().With.Message.Contains("identity mismatch"));
        Assert.Multiple(() =>
        {
            Assert.That(closeRequested, Is.False);
            Assert.That(killRequested, Is.False);
        });
    }

    [Test]
    public void OwnedProcessIdentity_RejectsStartTimeOrExecutableMismatch()
    {
        DateTime start = new(2026, 7, 14, 12, 0, 0, DateTimeKind.Utc);
        var identity = new NativeWinUiOwnedProcessIdentity(42, start, @"C:\repo\OnslaughtCareerEditor.WinUI.exe");

        Assert.DoesNotThrow(() => identity.Validate(42, start, @"C:\repo\OnslaughtCareerEditor.WinUI.exe"));
        Assert.That(
            () => identity.Validate(42, start.AddTicks(1), @"C:\repo\OnslaughtCareerEditor.WinUI.exe"),
            Throws.TypeOf<InvalidOperationException>().With.Message.Contains("start time"));
        Assert.That(
            () => identity.Validate(42, start, @"C:\other\OnslaughtCareerEditor.WinUI.exe"),
            Throws.TypeOf<InvalidOperationException>().With.Message.Contains("executable path"));
    }

    [Test]
    public void OwnedProcessIdentity_WaitsForTemporarilyUnavailableExecutablePath()
    {
        int observations = 0;

        string executablePath = NativeWinUiOwnedProcessIdentity.WaitForExecutablePath(
            () =>
            {
                observations++;
                return observations < 3
                    ? new NativeWinUiExecutablePathObservation(ProcessExited: false, ExecutablePath: null)
                    : new NativeWinUiExecutablePathObservation(
                        ProcessExited: false,
                        ExecutablePath: @"C:\repo\OnslaughtCareerEditor.WinUI.exe");
            },
            maxAttempts: 3,
            waitBetweenAttempts: () => { });

        Assert.Multiple(() =>
        {
            Assert.That(executablePath, Is.EqualTo(@"C:\repo\OnslaughtCareerEditor.WinUI.exe"));
            Assert.That(observations, Is.EqualTo(3));
        });
    }

    [Test]
    public void OwnedProcessIdentity_FailsImmediatelyWhenProcessExitsBeforePathIsAvailable()
    {
        int waits = 0;

        Assert.That(
            () => NativeWinUiOwnedProcessIdentity.WaitForExecutablePath(
                () => new NativeWinUiExecutablePathObservation(ProcessExited: true, ExecutablePath: null),
                maxAttempts: 3,
                waitBetweenAttempts: () => waits++),
            Throws.TypeOf<InvalidOperationException>()
                .With.Message.Contains("exited before its executable path became available"));
        Assert.That(waits, Is.Zero);
    }

    [Test]
    public void OwnedProcessIdentity_FailsClosedAfterBoundedPathReadinessAttempts()
    {
        int observations = 0;
        int waits = 0;

        Assert.That(
            () => NativeWinUiOwnedProcessIdentity.WaitForExecutablePath(
                () =>
                {
                    observations++;
                    return new NativeWinUiExecutablePathObservation(ProcessExited: false, ExecutablePath: null);
                },
                maxAttempts: 3,
                waitBetweenAttempts: () => waits++),
            Throws.TypeOf<InvalidOperationException>()
                .With.Message.Contains("unavailable after 3 bounded readiness attempts"));
        Assert.Multiple(() =>
        {
            Assert.That(observations, Is.EqualTo(3));
            Assert.That(waits, Is.EqualTo(2));
        });
    }
}
