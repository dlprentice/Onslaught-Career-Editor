// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client.Tests;

public sealed class FirstFlightLaunchOptionsTests
{
    [Fact]
    public void NormalLaunchAdmitsRepeatedCareerSelectionsAndStartupMediaWithoutReadingThem()
    {
        FirstFlightLaunchOptions options = FirstFlightLaunchOptions.Parse(
            ["--career-save=/missing/first.bes", "--career-save=/missing/second.bes",
             "--startup-media=/missing/media"]);
        Assert.False(options.Smoke);
        Assert.False(options.SkipStartupMedia);
        Assert.False(options.CaptureArgumentsPresent);
        Assert.Null(options.RecordTapePath);
    }

    [Fact]
    public void LaunchKeepsRecordingAndMediaOptionsIndependent()
    {
        string tape = Path.GetFullPath("recording.json");
        FirstFlightLaunchOptions options = FirstFlightLaunchOptions.Parse(
            ["--skipfmv", "--intro", $"--record-tape={tape}", "--capture-plan=mainmenu"]);
        Assert.Equal(tape, options.RecordTapePath);
        Assert.True(options.SkipStartupMedia);
        Assert.True(options.ForceStartupMedia);
        Assert.True(options.CaptureArgumentsPresent);
    }

    [Theory]
    [InlineData("--career-svae=/missing/save.bes")]
    [InlineData("/missing/save.bes")]
    [InlineData("--post-mission-event=Won")]
    public void UnknownArgumentsRemainRefused(string argument) =>
        Assert.Throws<ArgumentException>(() => FirstFlightLaunchOptions.Parse([argument]));

    [Theory]
    [InlineData("--record-tape=relative.json")]
    [InlineData("--record-tape=/tmp/save.bes")]
    [InlineData("--record-tape=")]
    public void RecordingRequiresAnExplicitJsonDestination(string argument) =>
        Assert.Throws<ArgumentException>(() => FirstFlightLaunchOptions.Parse([argument]));

    [Fact]
    public void SmokeRequiresAnAbsoluteReportDestination()
    {
        Assert.Throws<ArgumentException>(() => FirstFlightLaunchOptions.Parse(["--smoke"]));
        Assert.Throws<ArgumentException>(() => FirstFlightLaunchOptions.Parse(
            ["--smoke", "--report=relative.json"]));
        string report = Path.GetFullPath("smoke.json");
        FirstFlightLaunchOptions options = FirstFlightLaunchOptions.Parse(
            ["--smoke", $"--report={report}"]);
        Assert.True(options.Smoke);
        Assert.Equal(report, options.ReportPath);
    }
}
