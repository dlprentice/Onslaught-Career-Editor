// SPDX-License-Identifier: GPL-3.0-or-later

using System.Reflection;
using System.Text.Json;
using OnslaughtRebuild.Core;
using Xunit;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Guards PROGRAM P9's Core-gate split. The default command runs the full Core
/// assembly except the expensive ferry class; an explicit command retains that
/// class's unchanged forty-run oracle; and the broad rebuild gate chains both.
/// </summary>
public class TestGateCompositionTests
{
    private const string FerryClassName =
        "OnslaughtRebuild.Core.Tests.Level100FerryLandingTests";

    private static readonly string[] FerryTestNames =
    [
        FerryClassName + ".AdverseControl_CommitsTheFallTheClearanceTermRefuses",
        FerryClassName + ".ClearanceTerms_ChangeNothingBeforeTheFerryHome",
        FerryClassName + ".FixedSweep_NeverMorphsAboveTheHandoffClearance",
        FerryClassName + ".OnePermilleSweep_NeverDrownsOnTheFerryHome",
        FerryClassName + ".WaterRule_AgreesWithTheCommittedElevationInEveryRealRun",
        FerryClassName + ".WaterRule_IsPinnedAtTheReleasedTwoHundredMillimetres",
    ];

    /// <summary>
    /// Each command owns one exact complementary filter. With no inclusion
    /// clause the default selects everything except this class; with one
    /// inclusion clause the sweep selects exactly this class.
    /// </summary>
    [Fact]
    public void TheDefaultCoreGateExcludesOnlyTheFerrySweep()
    {
        string defaultScript = ReadScript("test:rebuild-core");
        string sweepScript = ReadScript("test:rebuild-ferry-sweep");

        Assert.Equal(
            "FullyQualifiedName!~Level100FerryLandingTests",
            ReadSingleFilter(defaultScript));
        Assert.Equal(
            "FullyQualifiedName~Level100FerryLandingTests",
            ReadSingleFilter(sweepScript));

        foreach (string script in new[] { defaultScript, sweepScript })
        {
            Assert.Contains("prepare:rebuild-assets", script, StringComparison.Ordinal);
            Assert.Contains(
                "OnslaughtRebuild.Core.Tests.csproj",
                script,
                StringComparison.Ordinal);
        }
    }

    /// <summary>
    /// The explicit selection still constructs the original class fixture and
    /// exposes all six oracle facts over twenty perturbations and both arms.
    /// </summary>
    [Fact]
    public void TheExplicitSweepCommandStillSelectsTheCompleteOriginalMatrix()
    {
        Assert.Contains(
            typeof(IClassFixture<Level100FerrySweepFixture>),
            typeof(Level100FerryLandingTests).GetInterfaces());
        Assert.Equal(20, Level100LookPerturbation.Sweep.Count);
        Assert.Equal(40, Level100LookPerturbation.Sweep.Count * 2);

        string[] actual = typeof(Level100FerryLandingTests)
            .GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly)
            .Where(method => method.GetCustomAttributes<FactAttribute>().Any())
            .Select(method => FerryClassName + "." + method.Name)
            .Order(StringComparer.Ordinal)
            .ToArray();
        Assert.Equal(FerryTestNames, actual);
    }

    /// <summary>
    /// The opt-in sweep is not orphaned: the broad rebuild gate runs it after
    /// the default Core gate and before client/adaptor checks.
    /// </summary>
    [Fact]
    public void TheCrossCuttingRebuildGateStillChainsTheFerrySweep()
    {
        string rebuild = ReadScript("test:rebuild");
        int core = rebuild.IndexOf(
            "npm run test:rebuild-core",
            StringComparison.Ordinal);
        int sweep = rebuild.IndexOf(
            "npm run test:rebuild-ferry-sweep",
            StringComparison.Ordinal);
        int client = rebuild.IndexOf(
            "npm run test:rebuild-client",
            StringComparison.Ordinal);

        Assert.True(core >= 0, "test:rebuild no longer chains test:rebuild-core.");
        Assert.True(
            sweep > core,
            "test:rebuild must chain the ferry sweep after the default Core gate.");
        Assert.True(
            client > sweep,
            "test:rebuild must chain client/adaptor checks after the ferry sweep.");
    }

    private static string ReadSingleFilter(string script)
    {
        const string Marker = "--filter \"";
        int start = script.IndexOf(Marker, StringComparison.Ordinal);
        Assert.True(start >= 0, "No quoted --filter found in: " + script);
        start += Marker.Length;
        int end = script.IndexOf('"', start);
        Assert.True(end > start, "Unterminated --filter found in: " + script);
        Assert.Equal(
            -1,
            script.IndexOf(Marker, end + 1, StringComparison.Ordinal));
        return script[start..end];
    }

    private static string ReadScript(string commandKey)
    {
        using JsonDocument document = JsonDocument.Parse(
            File.ReadAllText(Path.Combine(FindRepoRoot(), "package.json")));
        Assert.True(
            document.RootElement
                .GetProperty("scripts")
                .TryGetProperty(commandKey, out JsonElement value),
            "package.json no longer declares " + commandKey + ".");
        return Assert.IsType<string>(value.GetString());
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? current = new(AppContext.BaseDirectory);
        while (current is not null)
        {
            if (File.Exists(Path.Combine(current.FullName, "package.json")) &&
                File.Exists(Path.Combine(current.FullName, "OnslaughtCareerEditor.WinUI.slnx")))
            {
                return current.FullName;
            }

            current = current.Parent;
        }

        throw new DirectoryNotFoundException(
            "Could not locate the repository root for the gate composition tests.");
    }
}
