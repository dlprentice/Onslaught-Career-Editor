namespace OnslaughtCareerEditor.WinUI.Helpers;

internal enum HomeFocusTarget
{
    Setup,
    PatchBench,
    SaveLab,
}

internal enum HomeSetupApplicability
{
    Pending,
    Applicable,
    NotApplicable,
}

internal enum HomeFocusReadiness
{
    Pending,
    Unavailable,
    Ready,
}

internal enum HomeArrivalFocusOutcome
{
    ContentFocused,
    NavigationFallbackFocused,
    ActivationTimedOut,
    ContentTimedOut,
    Cancelled,
    ContextChanged,
    UserFocusPreserved,
}

internal sealed record HomeArrivalFocusSnapshot(
    bool NavigationCurrent,
    bool PageLoaded,
    bool WindowActive,
    bool UserFocusEstablished,
    HomeSetupApplicability SetupApplicability,
    HomeFocusReadiness SetupReadiness,
    HomeFocusReadiness PatchBenchReadiness,
    HomeFocusReadiness SaveLabReadiness)
{
    public HomeFocusReadiness GetReadiness(HomeFocusTarget target)
    {
        return target switch
        {
            HomeFocusTarget.Setup => SetupReadiness,
            HomeFocusTarget.PatchBench => PatchBenchReadiness,
            HomeFocusTarget.SaveLab => SaveLabReadiness,
            _ => HomeFocusReadiness.Unavailable,
        };
    }
}

internal sealed record HomeArrivalFocusDiagnostic(
    string Stage,
    int Sample,
    HomeFocusTarget? Target,
    HomeSetupApplicability SetupApplicability,
    HomeFocusReadiness? Readiness,
    bool? TryFocusSucceeded,
    bool? FocusVerified,
    HomeArrivalFocusOutcome? Outcome);

internal sealed record HomeArrivalFocusPolicyOperations(
    Func<HomeArrivalFocusSnapshot> ReadSnapshot,
    Func<HomeFocusTarget, CancellationToken, Task<bool>> TryFocusAsync,
    Func<HomeFocusTarget, bool> IsFocusVerified,
    Func<CancellationToken, Task<bool>> TryNavigationFallbackAsync,
    Func<bool> IsNavigationFallbackVerified,
    Func<TimeSpan, CancellationToken, Task> DelayAsync,
    Action<HomeArrivalFocusDiagnostic>? ReportDiagnostic = null);

internal static class HomeArrivalFocusPolicy
{
    internal static readonly TimeSpan SampleInterval = TimeSpan.FromMilliseconds(50);
    internal const int ActivationSampleLimit = 100;
    internal const int ContentSampleLimit = 80;
    internal const int MaxTryFocusAttemptsPerCandidate = 2;

    public static async Task<HomeArrivalFocusOutcome> RunAsync(
        HomeArrivalFocusPolicyOperations operations,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(operations);

        try
        {
            HomeArrivalFocusOutcome? activationExit = await WaitForActivationAsync(operations, cancellationToken);
            if (activationExit is not null)
            {
                return activationExit.Value;
            }

            return await FocusContentOrFallbackAsync(operations, cancellationToken);
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            Report(operations, new HomeArrivalFocusDiagnostic(
                "cancelled",
                0,
                null,
                HomeSetupApplicability.Pending,
                null,
                null,
                null,
                HomeArrivalFocusOutcome.Cancelled));
            return HomeArrivalFocusOutcome.Cancelled;
        }
    }

    private static async Task<HomeArrivalFocusOutcome?> WaitForActivationAsync(
        HomeArrivalFocusPolicyOperations operations,
        CancellationToken cancellationToken)
    {
        int consecutiveReadySamples = 0;
        for (int sample = 0; sample <= ActivationSampleLimit; sample++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            HomeArrivalFocusSnapshot snapshot = operations.ReadSnapshot();
            HomeArrivalFocusOutcome? stop = GetStopOutcome(snapshot);
            if (stop is not null)
            {
                ReportOutcome(operations, "activation-stop", sample, snapshot, stop.Value);
                return stop;
            }

            consecutiveReadySamples = snapshot.WindowActive && snapshot.PageLoaded
                ? consecutiveReadySamples + 1
                : 0;
            Report(operations, new HomeArrivalFocusDiagnostic(
                "activation-sample",
                sample,
                null,
                snapshot.SetupApplicability,
                null,
                null,
                null,
                null));
            if (consecutiveReadySamples >= 2)
            {
                return null;
            }

            if (sample == ActivationSampleLimit)
            {
                break;
            }

            await operations.DelayAsync(SampleInterval, cancellationToken);
        }

        HomeArrivalFocusSnapshot finalSnapshot = operations.ReadSnapshot();
        ReportOutcome(
            operations,
            "activation-timeout",
            ActivationSampleLimit,
            finalSnapshot,
            HomeArrivalFocusOutcome.ActivationTimedOut);
        return HomeArrivalFocusOutcome.ActivationTimedOut;
    }

    private static async Task<HomeArrivalFocusOutcome> FocusContentOrFallbackAsync(
        HomeArrivalFocusPolicyOperations operations,
        CancellationToken cancellationToken)
    {
        int elapsedSamples = 0;
        int consecutiveReadySamples = 0;
        int currentTargetIndex = -1;
        int[] focusAttempts = new int[3];

        while (elapsedSamples <= ContentSampleLimit)
        {
            cancellationToken.ThrowIfCancellationRequested();
            HomeArrivalFocusSnapshot snapshot = operations.ReadSnapshot();
            HomeArrivalFocusOutcome? stop = GetStopOutcome(snapshot);
            if (stop is not null)
            {
                ReportOutcome(operations, "content-stop", elapsedSamples, snapshot, stop.Value);
                return stop.Value;
            }

            if (!snapshot.WindowActive || !snapshot.PageLoaded)
            {
                ReportOutcome(
                    operations,
                    "content-context-changed",
                    elapsedSamples,
                    snapshot,
                    HomeArrivalFocusOutcome.ContextChanged);
                return HomeArrivalFocusOutcome.ContextChanged;
            }

            if (currentTargetIndex < 0)
            {
                if (snapshot.SetupApplicability == HomeSetupApplicability.Pending)
                {
                    Report(operations, new HomeArrivalFocusDiagnostic(
                        "setup-applicability-pending",
                        elapsedSamples,
                        HomeFocusTarget.Setup,
                        snapshot.SetupApplicability,
                        snapshot.SetupReadiness,
                        null,
                        null,
                        null));
                    int? nextSample = await DelayWithinContentBudgetAsync(operations, cancellationToken, elapsedSamples);
                    if (nextSample is null)
                    {
                        break;
                    }

                    elapsedSamples = nextSample.Value;

                    continue;
                }

                currentTargetIndex = snapshot.SetupApplicability == HomeSetupApplicability.Applicable ? 0 : 1;
            }

            if (currentTargetIndex > (int)HomeFocusTarget.SaveLab)
            {
                break;
            }

            HomeFocusTarget target = (HomeFocusTarget)currentTargetIndex;
            HomeFocusReadiness readiness = snapshot.GetReadiness(target);
            Report(operations, new HomeArrivalFocusDiagnostic(
                "content-sample",
                elapsedSamples,
                target,
                snapshot.SetupApplicability,
                readiness,
                null,
                null,
                null));

            if (readiness == HomeFocusReadiness.Unavailable)
            {
                currentTargetIndex++;
                consecutiveReadySamples = 0;
                continue;
            }

            if (readiness != HomeFocusReadiness.Ready)
            {
                consecutiveReadySamples = 0;
                int? nextSample = await DelayWithinContentBudgetAsync(operations, cancellationToken, elapsedSamples);
                if (nextSample is null)
                {
                    break;
                }

                elapsedSamples = nextSample.Value;

                continue;
            }

            consecutiveReadySamples++;
            if (consecutiveReadySamples < 2)
            {
                int? nextSample = await DelayWithinContentBudgetAsync(operations, cancellationToken, elapsedSamples);
                if (nextSample is null)
                {
                    break;
                }

                elapsedSamples = nextSample.Value;

                continue;
            }

            if (elapsedSamples >= ContentSampleLimit)
            {
                break;
            }

            bool tryFocusSucceeded = await operations.TryFocusAsync(target, cancellationToken);
            focusAttempts[currentTargetIndex]++;
            int? postFocusSample = await DelayWithinContentBudgetAsync(operations, cancellationToken, elapsedSamples);
            if (postFocusSample is null)
            {
                break;
            }

            elapsedSamples = postFocusSample.Value;

            HomeArrivalFocusSnapshot postFocusSnapshot = operations.ReadSnapshot();
            HomeArrivalFocusOutcome? postFocusStop = GetStopOutcome(postFocusSnapshot);
            bool focusVerified = tryFocusSucceeded
                && postFocusStop is null
                && postFocusSnapshot.WindowActive
                && postFocusSnapshot.PageLoaded
                && operations.IsFocusVerified(target);
            Report(operations, new HomeArrivalFocusDiagnostic(
                "focus-attempt",
                elapsedSamples,
                target,
                postFocusSnapshot.SetupApplicability,
                postFocusSnapshot.GetReadiness(target),
                tryFocusSucceeded,
                focusVerified,
                focusVerified ? HomeArrivalFocusOutcome.ContentFocused : postFocusStop));
            if (focusVerified)
            {
                return HomeArrivalFocusOutcome.ContentFocused;
            }

            if (postFocusStop is not null)
            {
                return postFocusStop.Value;
            }

            consecutiveReadySamples = 0;
            if (focusAttempts[currentTargetIndex] >= MaxTryFocusAttemptsPerCandidate)
            {
                currentTargetIndex++;
            }
        }

        cancellationToken.ThrowIfCancellationRequested();
        HomeArrivalFocusSnapshot finalSnapshot = operations.ReadSnapshot();
        HomeArrivalFocusOutcome? finalStop = GetStopOutcome(finalSnapshot);
        if (finalStop is not null)
        {
            ReportOutcome(operations, "fallback-suppressed", elapsedSamples, finalSnapshot, finalStop.Value);
            return finalStop.Value;
        }

        if (!finalSnapshot.WindowActive || !finalSnapshot.PageLoaded)
        {
            ReportOutcome(
                operations,
                "fallback-suppressed",
                elapsedSamples,
                finalSnapshot,
                HomeArrivalFocusOutcome.ContextChanged);
            return HomeArrivalFocusOutcome.ContextChanged;
        }

        bool fallbackReported = await operations.TryNavigationFallbackAsync(cancellationToken);
        await operations.DelayAsync(SampleInterval, cancellationToken);
        HomeArrivalFocusSnapshot postFallbackSnapshot = operations.ReadSnapshot();
        HomeArrivalFocusOutcome? postFallbackStop = GetStopOutcome(postFallbackSnapshot);
        if (postFallbackStop is not null)
        {
            ReportOutcome(operations, "fallback-postcondition-stop", elapsedSamples, postFallbackSnapshot, postFallbackStop.Value);
            return postFallbackStop.Value;
        }

        bool fallbackFocused = fallbackReported
            && postFallbackSnapshot.WindowActive
            && postFallbackSnapshot.PageLoaded
            && operations.IsNavigationFallbackVerified();
        HomeArrivalFocusOutcome outcome = fallbackFocused
            ? HomeArrivalFocusOutcome.NavigationFallbackFocused
            : HomeArrivalFocusOutcome.ContentTimedOut;
        ReportOutcome(operations, "fallback", elapsedSamples, postFallbackSnapshot, outcome);
        return outcome;
    }

    private static async Task<int?> DelayWithinContentBudgetAsync(
        HomeArrivalFocusPolicyOperations operations,
        CancellationToken cancellationToken,
        int elapsedSamples)
    {
        if (elapsedSamples >= ContentSampleLimit)
        {
            return null;
        }

        await operations.DelayAsync(SampleInterval, cancellationToken);
        return elapsedSamples + 1;
    }

    private static HomeArrivalFocusOutcome? GetStopOutcome(HomeArrivalFocusSnapshot snapshot)
    {
        if (!snapshot.NavigationCurrent)
        {
            return HomeArrivalFocusOutcome.ContextChanged;
        }

        return snapshot.UserFocusEstablished
            ? HomeArrivalFocusOutcome.UserFocusPreserved
            : null;
    }

    private static void ReportOutcome(
        HomeArrivalFocusPolicyOperations operations,
        string stage,
        int sample,
        HomeArrivalFocusSnapshot snapshot,
        HomeArrivalFocusOutcome outcome)
    {
        Report(operations, new HomeArrivalFocusDiagnostic(
            stage,
            sample,
            null,
            snapshot.SetupApplicability,
            null,
            null,
            null,
            outcome));
    }

    private static void Report(HomeArrivalFocusPolicyOperations operations, HomeArrivalFocusDiagnostic diagnostic)
    {
        try
        {
            operations.ReportDiagnostic?.Invoke(diagnostic);
        }
        catch
        {
            // Test-only diagnostics must never change focus behavior.
        }
    }
}
