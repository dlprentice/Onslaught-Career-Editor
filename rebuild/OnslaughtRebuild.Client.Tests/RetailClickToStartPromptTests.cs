// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPIntro click-to-start clock recovered from the pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, SHA-256
/// <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>.
///
/// <para><b>Bodies.</b> <c>CFEPIntro::Process</c> <c>0x0051B6B0</c>–<c>0x0051B83C</c>
/// and <c>CFEPIntro::Render</c> <c>0x0051B840</c>–<c>0x0051BE66</c>. File offset =
/// VA − <c>0x400000</c>. This class does not claim the 30 s idle write of
/// <c>-3</c> to <c>0x008A956C</c>; that is a later lifecycle seam.</para>
///
/// <para>What is asserted is the LAW, not Godot pixels. The previous prompt
/// condition <c>PosMod(timer, 2) &lt; 1.6</c> was a stub for the CRT
/// <c>fmod</c> thunk at <c>0x0055E3EA</c> and is the mutation these cases
/// kill.</para>
/// </summary>
public sealed class RetailClickToStartPromptTests
{
    [Fact]
    public void ProcessHoldsTheTimerAtZeroUntilWallTimeExceedsOneSecond()
    {
        // 0x0051B749 fcomp [0.0]; jz already-running. 0x0051B769 fcomp [1.0]
        // (0x005D8568) with test ah,0x41 / jnz skip-seed: seed only when
        // GetTime()-[this+4] is strictly greater than 1.
        Assert.Equal(0d, RetailClickToStartPrompt.Advance(0d, pageSeconds: 1.0, dt: 0.05));
        Assert.Equal(0d, RetailClickToStartPrompt.Advance(0d, pageSeconds: 0.5, dt: 0.05));
    }

    [Fact]
    public void ProcessSeedsTheExactImmediateThenAddsTwiceDtOnTheSameTick()
    {
        // 0x0051B776 mov [esi+18], 0x3727C5AC then, because the timer is no
        // longer 0, 0x0051B78D fld [dt]; fadd st,st; fadd [esi+18].
        double next = RetailClickToStartPrompt.Advance(0d, pageSeconds: 1.0 + 1e-6, dt: 0.05);

        Assert.Equal(
            RetailClickToStartPrompt.SeedValue + (RetailClickToStartPrompt.Rate * 0.05),
            next,
            12);
        Assert.Equal(0x3727C5ACu, RetailClickToStartPrompt.SeedBits);
    }

    [Fact]
    public void AlreadyRunningTimerOnlyAddsTwiceDt()
    {
        Assert.Equal(4.1d, RetailClickToStartPrompt.Advance(4.0d, pageSeconds: 10d, dt: 0.05), 12);
    }

    [Fact]
    public void PromptStaysHiddenUntilTheTimerIsStrictlyAboveFour()
    {
        // 0x0051B8F8 fcomp [4.0] (0x005D85BC); test ah,0x41 / jnz skip.
        Assert.False(RetailClickToStartPrompt.IsPromptVisible(0d));
        Assert.False(RetailClickToStartPrompt.IsPromptVisible(4.0d));
        Assert.True(RetailClickToStartPrompt.IsPromptVisible(4.0d + 1e-6));
    }

    [Fact]
    public void PromptBlinkIsFmodPeriodFourOnLessThanTwoNotTheStubDuty()
    {
        // 0x0051B913 fld qword [0x005DB4A0] = 4.0; call CRT fmod 0x0055E3EA;
        // 0x0051B91E fcomp [2.0] (0x005D8BA0); test ah,1 / jz skip if remainder >= 2.
        Assert.True(RetailClickToStartPrompt.IsPromptVisible(5.7d));
        Assert.False(RetailClickToStartPrompt.IsPromptVisible(6.0d));
        Assert.False(RetailClickToStartPrompt.IsPromptVisible(6.5d));
        Assert.True(RetailClickToStartPrompt.IsPromptVisible(8.0d + 1e-6));

        // The withdrawn stub PosMod(t, 2) < 1.6 disagrees at both 5.7 and 6.5.
        Assert.False(StubDutyVisible(5.7d));
        Assert.True(StubDutyVisible(6.5d));
    }

    [Fact]
    public void SplashPulseUsesOneWhenTheTimerHasNotStartedAndDoesNotClampAfterwards()
    {
        // 0x0051B866 fcom [0]; test ah,0x41 / jnz keep: timer<=0 is replaced
        // with 1.0. There is no later min(t, 1) — that freeze is a rebuild defect.
        float atRest = RetailClickToStartPrompt.SplashScale(0d);
        float atOne = RetailClickToStartPrompt.SplashScale(1d);
        float later = RetailClickToStartPrompt.SplashScale(2d);

        Assert.Equal(atOne, atRest);
        Assert.NotEqual(atOne, later);
        Assert.Equal(ExpectedSplashScale(1f), atRest, 5);
        Assert.Equal(ExpectedSplashScale(2f), later, 5);
    }

    [Fact]
    public void DrawClickToStartCallsTheRecoveredLawInsteadOfTheStubDuty()
    {
        string flow = File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));

        Assert.Contains("RetailClickToStartPrompt.IsPromptVisible", flow);
        Assert.Contains("RetailClickToStartPrompt.SplashScale", flow);
        Assert.Contains("RetailClickToStartPrompt.Advance", flow);
        Assert.DoesNotContain("PosMod((float)_clickPulseTimer, 2f) < 1.6f", flow);
        Assert.DoesNotContain("Mathf.Min((float)_clickPulseTimer, 1f)", flow);
    }

    private static bool StubDutyVisible(double timer) =>
        timer > 4d && PositiveMod(timer, 2d) < 1.6d;

    private static double PositiveMod(double value, double modulus)
    {
        double remainder = value % modulus;
        return remainder < 0d ? remainder + modulus : remainder;
    }

    private static float ExpectedSplashScale(float t) =>
        ((MathF.Cos(t * MathF.PI) + 1f) * 0.375f) + 0.46875f;
}
