// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPIntro title-logo slam recovered from the pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, SHA-256
/// <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>.
///
/// <para><b>Body.</b> <c>CFEPIntro::Render</c> <c>0x0051BBA0</c>–<c>0x0051BD00</c>.
/// File offset = VA − <c>0x400000</c>. Five <c>CDXSurf__RenderSurface</c>
/// (<c>0x005563D0</c>) calls on <c>DAT_0089d88c</c> (title-logo). The sixth
/// z=0.02 pass after page&gt;2 is not claimed.</para>
///
/// <para>The mutation these cases kill is the one-pass
/// <c>0.35 / 0.55+0.45*sin(page*3)</c> stub in <c>DrawClickToStart</c>.</para>
/// </summary>
public sealed class RetailClickToStartTitleTests
{
    [Fact]
    public void TitleStaysHiddenUntilPageElapsedTimesOnePointTwoExceedsTwo()
    {
        // 0x0051BBAA fsub [this+4]; 0x0051BBAD fmul [1.2] at 0x005DBCE4;
        // 0x0051BBB3 fcom [2.0] at 0x005D8BA0; test ah,0x41 / jnz skip.
        Assert.Equal(1.2, RetailClickToStartTitle.TimeScale, 5);
        Assert.Equal(2.0, RetailClickToStartTitle.GateSeconds, 5);
        Assert.False(RetailClickToStartTitle.ShouldDraw(0d));
        Assert.False(RetailClickToStartTitle.ShouldDraw(2.0 / 1.2));
        Assert.True(RetailClickToStartTitle.ShouldDraw((2.0 / 1.2) + 1e-6));
    }

    [Fact]
    public void ScaleSlamsFromTwoPointFiveToOneHalfThenFreezes()
    {
        // Remaining ST after the brightness fistp is v=25-12*page while
        // v >= 1, else 1.0; then fmul [0.5] at 0x0051BC29.
        Assert.Equal(2.3f, RetailClickToStartTitle.Scale(1.7d), 5);
        Assert.Equal(0.5f, RetailClickToStartTitle.Scale(2.0d), 5);
        Assert.Equal(0.5f, RetailClickToStartTitle.Scale(3.0d), 5);
        Assert.Equal(0.5f, RetailClickToStartTitle.Scale(10.0d), 5);

        // The withdrawn stub is a constant 0.35 with a sine alpha.
        Assert.NotEqual(0.35f, RetailClickToStartTitle.Scale(3.0d));
        Assert.Equal(
            RetailClickToStartTitle.Scale(3.0d),
            RetailClickToStartTitle.Scale(4.0d));
    }

    [Fact]
    public void FiveCenteredPassesAreThePlusOrMinusTwoOutlineThenTheBody()
    {
        Assert.Equal(5, RetailClickToStartTitle.Passes.Length);
        Assert.Equal(
            new RetailClickToStartTitle.Pass(252f, 292f, 0.05f, Outline: true),
            RetailClickToStartTitle.Passes[0]);
        Assert.Equal(
            new RetailClickToStartTitle.Pass(248f, 292f, 0.05f, Outline: true),
            RetailClickToStartTitle.Passes[1]);
        Assert.Equal(
            new RetailClickToStartTitle.Pass(252f, 288f, 0.05f, Outline: true),
            RetailClickToStartTitle.Passes[2]);
        Assert.Equal(
            new RetailClickToStartTitle.Pass(248f, 288f, 0.05f, Outline: true),
            RetailClickToStartTitle.Passes[3]);
        Assert.Equal(
            new RetailClickToStartTitle.Pass(250f, 290f, 0.04f, Outline: false),
            RetailClickToStartTitle.Passes[4]);
    }

    [Fact]
    public void SettledColorsAreTheSpecimenBytePacksNotASineAlpha()
    {
        // Outline: edi=255, lea*5 / shl 5 / sub edi = *159, shl 16, and 0xFF000000.
        // Body: *255, shl 16, not / and 0x00FFFFFF / xor → 0xFEFFFFFF.
        Assert.Equal(0x9E000000u, RetailClickToStartTitle.OutlineColor(3.0d));
        Assert.Equal(0xFEFFFFFFu, RetailClickToStartTitle.BodyColor(3.0d));
        Assert.Equal(
            RetailClickToStartTitle.OutlineColor(3.0d),
            RetailClickToStartTitle.OutlineColor(8.0d));
    }

    [Fact]
    public void DrawClickToStartCallsTheRecoveredTitleLawInsteadOfTheSinStub()
    {
        string flow = File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));

        Assert.Contains("RetailClickToStartTitle.ShouldDraw", flow);
        Assert.Contains("RetailClickToStartTitle.Scale", flow);
        Assert.Contains("RetailClickToStartTitle.Passes", flow);
        Assert.DoesNotContain("0.55f + (0.45f * (0.5f + (0.5f * Mathf.Sin((float)_clickPageSeconds * 3f))))", flow);
        Assert.DoesNotContain("0.35f,\r\n                0.35f,", flow);
    }
}
