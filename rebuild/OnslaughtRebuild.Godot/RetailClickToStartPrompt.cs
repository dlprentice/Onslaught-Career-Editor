// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The CFEPIntro click-to-start clock — <c>this+0x18</c> — recovered from the
/// pristine specimen <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para><b>Bodies.</b> <c>CFEPIntro::Process</c> <c>0x0051B6B0</c>–<c>0x0051B83C</c>
/// owns the timer. <c>CFEPIntro::Render</c> <c>0x0051B840</c>–<c>0x0051BE66</c>
/// spends it on the splash pulse and the "Click to start" prompt. Neither body
/// is in the pinned GPL drop (<c>FEPIntro.cpp</c> is absent).</para>
///
/// <para><b>Process, in order.</b></para>
/// <list type="number">
/// <item>If the timer is 0 and <c>GetTime() - [this+4]</c> is strictly greater
/// than <c>1.0f</c> at <c>0x005D8568</c>, seed <c>[this+18]</c> with the
/// immediate <c>0x3727C5AC</c> (<c>0x0051B776</c>).</item>
/// <item>If the timer is then nonzero, add twice the frame Δ
/// (<c>fld [dt]; fadd st,st; fadd [esi+18]</c> at <c>0x0051B78D</c>).</item>
/// </list>
///
/// <para><b>Render.</b> The splash argument is <c>1.0f</c> while the timer is
/// ≤ 0 (<c>0x0051B866</c> <c>fcom [0]; test ah,0x41</c>) and the unclamped
/// timer afterwards — there is no <c>min(t, 1)</c>. The prompt is drawn only
/// when the timer is strictly greater than <c>4.0f</c> at <c>0x005D85BC</c>
/// and <c>fmod(timer, 4.0)</c> is strictly less than <c>2.0f</c> at
/// <c>0x005D8BA0</c>. The modulus is the qword <c>4.0</c> at <c>0x005DB4A0</c>,
/// consumed by the CRT <c>fmod</c> thunk at <c>0x0055E3EA</c>.</para>
///
/// <para><b>Not claimed here.</b> After 30 s with no click, Process writes
/// <c>-3</c> to the frontend quit/result global <c>0x008A956C</c>
/// (<c>fcomp [30.0f]</c> at <c>0x005DB1E4</c>). That is a lifecycle seam, not
/// a prompt law, and is left for a later slice. It is the cheapest account of
/// the measured t=32 s click-to-start fade-to-black
/// (<c>local-lab/STARTUP-FLOW-FINDINGS-2026-07-25.md</c>).</para>
///
/// <para>No Godot types. The capture rig suppresses this page's timing the
/// same way retail's <c>-skipfmv</c> does, so these numbers have to stand on
/// their own.</para>
/// </summary>
public static class RetailClickToStartPrompt
{
    /// <summary>
    /// <c>0x005D8568</c> = <c>1.0f</c>. Process will not seed <c>this+0x18</c>
    /// until page-elapsed time is strictly greater than this.
    /// </summary>
    public const double SeedDelaySeconds = 1.0;

    /// <summary>The 32-bit immediate Process writes at <c>0x0051B776</c>.</summary>
    public const uint SeedBits = 0x3727C5ACu;

    /// <summary><see cref="SeedBits"/> decoded as IEEE-754 single, widened.</summary>
    public static double SeedValue { get; } = BitConverter.UInt32BitsToSingle(SeedBits);

    /// <summary>
    /// Process adds <c>2 * dt</c> once the timer is nonzero
    /// (<c>fadd st,st</c> at <c>0x0051B793</c>).
    /// </summary>
    public const double Rate = 2.0;

    /// <summary><c>0x005D85BC</c> = <c>4.0f</c>. Prompt hidden while timer ≤ this.</summary>
    public const double PromptGateSeconds = 4.0;

    /// <summary>
    /// Qword at <c>0x005DB4A0</c> = <c>4.0</c>. The CRT <c>fmod</c> period.
    /// </summary>
    public const double BlinkPeriodSeconds = 4.0;

    /// <summary>
    /// <c>0x005D8BA0</c> = <c>2.0f</c>. Prompt on while
    /// <c>fmod(timer, period)</c> is strictly less than this.
    /// </summary>
    public const double BlinkOnSeconds = 2.0;

    /// <summary>
    /// One Process tick of <c>this+0x18</c>.
    /// <paramref name="pageSeconds"/> is wall time since the page became
    /// active, matching <c>GetTime() - [this+4]</c>.
    /// </summary>
    public static double Advance(double timer, double pageSeconds, double dt)
    {
        if (timer == 0d && pageSeconds > SeedDelaySeconds)
        {
            timer = SeedValue;
        }

        if (timer != 0d)
        {
            timer += Rate * dt;
        }

        return timer;
    }

    /// <summary>Whether Render would submit the localization-0x77 prompt.</summary>
    public static bool IsPromptVisible(double timer)
    {
        if (timer <= PromptGateSeconds)
        {
            return false;
        }

        // CRT fmod is toward-zero remainder. C# double % is the same for these
        // signs. The compare is strictly less than 2.0 (test ah,1 / jz).
        double remainder = timer % BlinkPeriodSeconds;
        if (remainder < 0d)
        {
            remainder += BlinkPeriodSeconds;
        }

        return remainder < BlinkOnSeconds;
    }

    /// <summary>
    /// Splash-pulse argument: 1.0 while the timer has not started, otherwise
    /// the live timer. Retail does not clamp this to 1 afterwards.
    /// </summary>
    public static float SplashArgument(double timer) => timer <= 0d ? 1f : (float)timer;

    /// <summary>
    /// <c>((cos(t*π)+1)*0.375)+0.46875</c> with <see cref="SplashArgument"/>.
    /// The 0.375 is <c>0.5 * 0.75</c> from the two packed multiplies at
    /// <c>0x0051B894</c> / <c>0x0051B89A</c>; 0.46875 is <c>0x005E49F0</c>.
    /// </summary>
    public static float SplashScale(double timer)
    {
        float t = SplashArgument(timer);
        return ((MathF.Cos(t * MathF.PI) + 1f) * 0.375f) + 0.46875f;
    }
}
