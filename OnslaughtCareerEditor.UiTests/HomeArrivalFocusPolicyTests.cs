using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

public class HomeArrivalFocusPolicyTests
{
    [Test]
    public async Task DelayedSetupRealization_ReservesPriorityUntilSetupIsReady()
    {
        var harness = new PolicyHarness(tick => tick switch
        {
            < 2 => Snapshot(windowActive: false),
            < 4 => Snapshot(setup: HomeSetupApplicability.Pending, patch: HomeFocusReadiness.Ready),
            < 7 => Snapshot(setup: HomeSetupApplicability.Applicable, setupReadiness: HomeFocusReadiness.Pending, patch: HomeFocusReadiness.Ready),
            _ => Snapshot(setup: HomeSetupApplicability.Applicable, setupReadiness: HomeFocusReadiness.Ready, patch: HomeFocusReadiness.Ready),
        });
        harness.FocusResults[HomeFocusTarget.Setup] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.Setup;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
            Assert.That(harness.FocusAttempts, Is.EqualTo(new[] { HomeFocusTarget.Setup }));
            Assert.That(harness.FocusAttemptTicks.Single(), Is.GreaterThanOrEqualTo(8), "Setup must be ready in two consecutive post-activation samples before focus is attempted.");
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ReadyState_SkipsInapplicableSetupAndFocusesPatchBench()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready,
            saveLab: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
        Assert.That(harness.FocusAttempts, Is.EqualTo(new[] { HomeFocusTarget.PatchBench }));
    }

    [Test]
    public async Task NavigationCancellation_DoesNotFallThroughToFallback()
    {
        using var cancellation = new CancellationTokenSource();
        var harness = new PolicyHarness(_ => Snapshot(setup: HomeSetupApplicability.Pending));
        harness.AfterDelay = tick =>
        {
            if (tick == 3)
            {
                cancellation.Cancel();
            }
        };

        HomeArrivalFocusOutcome outcome = await harness.RunAsync(cancellation.Token);

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.Cancelled));
            Assert.That(harness.FocusAttempts, Is.Empty);
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ToolkitUserFocusAfterNavigation_IsPreservedWithoutFallback()
    {
        var harness = new PolicyHarness(tick => Snapshot(
            setup: HomeSetupApplicability.Pending,
            userFocusEstablished: tick >= 3));

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.UserFocusPreserved));
            Assert.That(harness.FocusAttempts, Is.Empty);
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ProgrammaticAccessibilityFocusAfterNavigation_IsPreservedWithoutFallback()
    {
        var harness = new PolicyHarness(tick => Snapshot(
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready,
            userFocusEstablished: tick >= 2));

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.UserFocusPreserved));
            Assert.That(harness.FocusAttempts, Is.Empty);
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ExternalFocusBeforeActivation_DoesNotCancelArrivalOpportunity()
    {
        var harness = new PolicyHarness(tick => tick < 3
            ? Snapshot(windowActive: false, setup: HomeSetupApplicability.NotApplicable, patch: HomeFocusReadiness.Ready)
            : Snapshot(setup: HomeSetupApplicability.NotApplicable, patch: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
        Assert.That(harness.FocusAttempts, Is.EqualTo(new[] { HomeFocusTarget.PatchBench }));
    }

    [Test]
    public async Task ContentTimeout_UsesNavigationFallbackExactlyOnce()
    {
        var harness = new PolicyHarness(_ => Snapshot(setup: HomeSetupApplicability.Pending));
        harness.FallbackResult = true;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.NavigationFallbackFocused));
            Assert.That(harness.FallbackCount, Is.EqualTo(1));
            Assert.That(harness.DelayCount, Is.LessThanOrEqualTo(HomeArrivalFocusPolicy.ActivationSampleLimit + HomeArrivalFocusPolicy.ContentSampleLimit + 1));
        });
    }

    [Test]
    public async Task NavigationFallbackRequiresExactPostcondition()
    {
        var harness = new PolicyHarness(_ => Snapshot(setup: HomeSetupApplicability.Pending));
        harness.FallbackResult = true;
        harness.FallbackVerified = false;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentTimedOut));
            Assert.That(harness.FallbackCount, Is.EqualTo(1));
        });
    }

    [Test]
    public async Task ActivationTimeout_DoesNotAttemptInactiveWindowOrFallback()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            windowActive: false,
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready));

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ActivationTimedOut));
            Assert.That(harness.DelayCount, Is.EqualTo(HomeArrivalFocusPolicy.ActivationSampleLimit));
            Assert.That(harness.FocusAttempts, Is.Empty);
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ReportedTryFocusSuccessWithoutPostcondition_RetriesTwiceThenAdvances()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            setup: HomeSetupApplicability.Applicable,
            setupReadiness: HomeFocusReadiness.Ready,
            patch: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.Setup] = new Queue<bool>([true, true]);
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
            Assert.That(harness.FocusAttempts, Is.EqualTo(new[]
            {
                HomeFocusTarget.Setup,
                HomeFocusTarget.Setup,
                HomeFocusTarget.PatchBench,
            }));
            Assert.That(harness.FocusAttempts.Count(target => target == HomeFocusTarget.Setup), Is.EqualTo(HomeArrivalFocusPolicy.MaxTryFocusAttemptsPerCandidate));
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ExhaustedPatchBench_AdvancesToSaveLabInStrictPriorityOrder()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready,
            saveLab: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([false, false]);
        harness.FocusResults[HomeFocusTarget.SaveLab] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.SaveLab;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
            Assert.That(harness.FocusAttempts, Is.EqualTo(new[]
            {
                HomeFocusTarget.PatchBench,
                HomeFocusTarget.PatchBench,
                HomeFocusTarget.SaveLab,
            }));
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task VerifiedFocus_IsTerminalAndNeverStealsFocusAgain()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready,
            saveLab: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();
        int delayCountAtSuccess = harness.DelayCount;

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
            Assert.That(harness.FocusAttempts, Has.Count.EqualTo(1));
            Assert.That(harness.DelayCount, Is.EqualTo(delayCountAtSuccess));
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task ContextChangeAtTimeout_PreventsUnsafeFallback()
    {
        var harness = new PolicyHarness(tick => Snapshot(
            navigationCurrent: tick < HomeArrivalFocusPolicy.ContentSampleLimit,
            setup: HomeSetupApplicability.Pending));

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContextChanged));
            Assert.That(harness.FallbackCount, Is.Zero);
        });
    }

    [Test]
    public async Task FinalBudgetSample_DoesNotAttemptFocusWithoutPostconditionTime()
    {
        var harness = new PolicyHarness(tick => tick < 80
            ? Snapshot(setup: HomeSetupApplicability.Pending)
            : Snapshot(setup: HomeSetupApplicability.NotApplicable, patch: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.Multiple(() =>
        {
            Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentTimedOut));
            Assert.That(harness.FocusAttempts, Is.Empty, "A focus attempt without a remaining verification sample could be overwritten by fallback.");
            Assert.That(harness.FallbackCount, Is.EqualTo(1));
        });
    }

    [Test]
    public async Task DiagnosticWriterFailure_DoesNotChangeFocusBehavior()
    {
        var harness = new PolicyHarness(_ => Snapshot(
            setup: HomeSetupApplicability.NotApplicable,
            patch: HomeFocusReadiness.Ready));
        harness.FocusResults[HomeFocusTarget.PatchBench] = new Queue<bool>([true]);
        harness.VerifiedTarget = HomeFocusTarget.PatchBench;
        harness.ThrowFromDiagnostics = true;

        HomeArrivalFocusOutcome outcome = await harness.RunAsync();

        Assert.That(outcome, Is.EqualTo(HomeArrivalFocusOutcome.ContentFocused));
        Assert.That(harness.FocusAttempts, Is.EqualTo(new[] { HomeFocusTarget.PatchBench }));
    }

    [Test]
    public void NativeSmoke_GatesDiagnosticsAndDistinguishesGlobalUiaExceptions()
    {
        string smoke = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.UiTests",
            "WinUiHomeNavigationSmokeTests.cs"));

        Assert.Multiple(() =>
        {
            Assert.That(smoke, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_DIAGNOSTICS"));
            Assert.That(smoke, Does.Contain("AssertHomeArrivalFocus("));
            Assert.That(smoke, Does.Contain("FocusedAutomationProbe"));
            Assert.That(smoke, Does.Contain("ExceptionType"));
            Assert.That(smoke, Does.Contain("home-arrival-focus.jsonl"));
            Assert.That(smoke, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_RUN_ID"));
            Assert.That(smoke, Does.Contain("FocusVerified"));
            Assert.That(smoke, Does.Contain("FocusedAutomationIdAtSample"));
            Assert.That(smoke, Does.Contain("InputEpochAtSample"));
            Assert.That(smoke, Does.Contain("FinalXamlFocusedAutomationId"));
            Assert.That(smoke, Does.Contain("HomeFocusEvidenceAcceptance.TryReadEndpointStatus"));
            Assert.That(smoke, Does.Contain("ExactWindowScopedMatch"));
        });
    }

    [Test]
    public void MainWindow_WiresPolicyBeforeInitialNavigationAndPreservesHomePriority()
    {
        string shell = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "MainWindow.xaml.cs"));

        int hook = shell.IndexOf("RegisterHomeArrivalFocusTracking();", StringComparison.Ordinal);
        int initialNavigation = shell.IndexOf("NavigateToTagCore(GetInitialTag()", StringComparison.Ordinal);
        Assert.Multiple(() =>
        {
            Assert.That(hook, Is.GreaterThanOrEqualTo(0));
            Assert.That(initialNavigation, Is.GreaterThan(hook), "Activation and input tracking must exist before constructor navigation can run.");
            Assert.That(shell, Does.Contain("HomeArrivalFocusPolicy.RunAsync("));
            Assert.That(shell, Does.Contain("Content is UIElement homeArrivalInputRoot"));
            Assert.That(shell, Does.Contain("HomeSetupInfoBar"));
            Assert.That(shell, Does.Contain("HomeSetupActionButton"));
            Assert.That(shell, Does.Contain("HomeOpenPatchBenchButton"));
            Assert.That(shell, Does.Contain("HomeOpenSaveLabButton"));
            Assert.That(shell, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_DIAGNOSTICS"));
            Assert.That(shell, Does.Contain("home-arrival-focus.jsonl"));
            Assert.That(shell, Does.Contain("FocusManager.GetFocusedElement"));
            Assert.That(shell, Does.Contain("Task.FromResult(element.Focus(FocusState.Programmatic))"));
            Assert.That(shell, Does.Not.Contain("FocusManager.TryFocusAsync(element"));
            Assert.That(shell, Does.Contain("IsNavigationFallbackVerified"));
            Assert.That(shell, Does.Contain("Environment.ProcessId"));
            Assert.That(shell, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_RUN_ID"));
            Assert.That(shell, Does.Contain("HomeArrivalFocusDiagnosticSample"));
            Assert.That(shell, Does.Contain("FocusedAutomationIdAtSample"));
            Assert.That(shell, Does.Contain("InputEpochAtSample"));
            Assert.That(shell, Does.Contain("WriteHomeArrivalFocusEndpointStatus"));
            Assert.That(shell, Does.Contain("ONSLAUGHT_HOME_FOCUS_ENDPOINT:"));
            Assert.That(shell, Does.Contain("homeArrivalInputRoot.GotFocus += HomeArrivalFocusEndpointChanged"));
            Assert.That(shell, Does.Contain("bool enqueued = DispatcherQueue.TryEnqueue"));
            Assert.That(shell, Does.Contain("catch (Exception)\n            {"));
            Assert.That(shell, Does.Not.Contain("catch (Exception) when (!cancellation.IsCancellationRequested)"));
            Assert.That(shell, Does.Contain("focusDiagnostics.Add(new HomeArrivalFocusDiagnosticSample("));
            Assert.That(shell, Does.Contain("WriteHomeArrivalFocusDiagnostics("));
        });
    }

    private static HomeArrivalFocusSnapshot Snapshot(
        bool navigationCurrent = true,
        bool pageLoaded = true,
        bool windowActive = true,
        bool userFocusEstablished = false,
        HomeSetupApplicability setup = HomeSetupApplicability.Pending,
        HomeFocusReadiness setupReadiness = HomeFocusReadiness.Pending,
        HomeFocusReadiness patch = HomeFocusReadiness.Pending,
        HomeFocusReadiness saveLab = HomeFocusReadiness.Pending)
    {
        return new HomeArrivalFocusSnapshot(
            navigationCurrent,
            pageLoaded,
            windowActive,
            userFocusEstablished,
            setup,
            setupReadiness,
            patch,
            saveLab);
    }

    private sealed class PolicyHarness
    {
        private readonly Func<int, HomeArrivalFocusSnapshot> _snapshot;

        public PolicyHarness(Func<int, HomeArrivalFocusSnapshot> snapshot)
        {
            _snapshot = snapshot;
        }

        public Dictionary<HomeFocusTarget, Queue<bool>> FocusResults { get; } = [];
        public List<HomeFocusTarget> FocusAttempts { get; } = [];
        public List<int> FocusAttemptTicks { get; } = [];
        public HomeFocusTarget? VerifiedTarget { get; set; }
        public bool FallbackResult { get; set; }
        public bool FallbackVerified { get; set; } = true;
        public int FallbackCount { get; private set; }
        public int DelayCount { get; private set; }
        public Action<int>? AfterDelay { get; set; }
        public bool ThrowFromDiagnostics { get; set; }

        public Task<HomeArrivalFocusOutcome> RunAsync(CancellationToken cancellationToken = default)
        {
            return HomeArrivalFocusPolicy.RunAsync(
                new HomeArrivalFocusPolicyOperations(
                    () => _snapshot(DelayCount),
                    (target, _) =>
                    {
                        FocusAttempts.Add(target);
                        FocusAttemptTicks.Add(DelayCount);
                        bool result = FocusResults.TryGetValue(target, out Queue<bool>? results) && results.Count > 0 && results.Dequeue();
                        return Task.FromResult(result);
                    },
                    target => VerifiedTarget == target,
                    _ =>
                    {
                        FallbackCount++;
                        return Task.FromResult(FallbackResult);
                    },
                    () => FallbackVerified,
                    (_, token) =>
                    {
                        token.ThrowIfCancellationRequested();
                        DelayCount++;
                        AfterDelay?.Invoke(DelayCount);
                        token.ThrowIfCancellationRequested();
                        return Task.CompletedTask;
                    },
                    _ =>
                    {
                        if (ThrowFromDiagnostics)
                        {
                            throw new IOException("synthetic diagnostic failure");
                        }
                    }),
                cancellationToken);
        }
    }
}
