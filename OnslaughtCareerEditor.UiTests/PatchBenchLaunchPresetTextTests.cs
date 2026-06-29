using System;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchLaunchPresetTextTests
{
    private static readonly string[] ReflectedLaunchPresetSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedChoiceState.cs",
    ];

    [Test]
    public void ChoiceStateBuilders_PreserveLaunchPresetAutomationNames()
    {
        Assert.Multiple(() =>
        {
            AssertChoiceState(
                "BuildQuietCaptureChoiceState",
                "Set quiet capture launch options for safe copy",
                "Selected: quiet capture launch preset");
            AssertChoiceState(
                "BuildHighDetailChoiceState",
                "Set high detail launch options for safe copy",
                "Selected: high detail launch preset");
            AssertChoiceState(
                "BuildControlBaselineChoiceState",
                "Set control diagnostics baseline config 1",
                "Selected: control diagnostics baseline config 1");
            AssertChoiceState(
                "BuildControlSharpenedChoiceState",
                "Set control diagnostics sensitivity test config 1",
                "Selected: control diagnostics sensitivity test config 1");
            AssertChoiceState(
                "BuildControlConfig2ChoiceState",
                "Set control diagnostics swapped sticks config 2",
                "Selected: control diagnostics swapped config 2");
            AssertChoiceState(
                "BuildControlConfig3ChoiceState",
                "Set control diagnostics alternate morph jets config 3",
                "Selected: control diagnostics alternate morph jets config 3");
            AssertChoiceState(
                "BuildControlConfig4ChoiceState",
                "Set control diagnostics swapped alternate config 4",
                "Selected: control diagnostics swapped alternate config 4");
        });
    }

    [Test]
    public void StatusMessageBuilders_PreserveLaunchPresetStatusText()
    {
        Assert.Multiple(() =>
        {
            Assert.That(InvokeString("BuildAdminLevelPresetTrainingWorld100StatusMessage"), Is.EqualTo("admin level preset campaign training world 100 selected"));
            Assert.That(InvokeString("BuildAdminLevelPresetFinalWorld800StatusMessage"), Is.EqualTo("admin level preset final campaign world 800 selected"));
            Assert.That(InvokeString("BuildAdminLevelPresetLocalMultiplayerWorld850StatusMessage"), Is.EqualTo("admin level preset local multiplayer world 850 selected"));
            Assert.That(InvokeString("BuildAdminLevelPresetLocalMultiplayerWorld851StatusMessage"), Is.EqualTo("admin level preset local multiplayer world 851 selected"));
            Assert.That(InvokeString("BuildLocalMultiplayerProbeStatusMessage"), Is.EqualTo("local multiplayer level 850 launch probe selected"));
            Assert.That(InvokeString("BuildQuietCaptureStatusMessage"), Is.EqualTo("quiet capture launch preset selected"));
            Assert.That(InvokeString("BuildHighDetailStatusMessage"), Is.EqualTo("high detail launch preset selected"));
            Assert.That(InvokeString("BuildControlBaselineStatusMessage"), Is.EqualTo("control diagnostics baseline config 1 selected"));
            Assert.That(InvokeString("BuildControlSharpenedStatusMessage"), Is.EqualTo("control diagnostics sensitivity test config 1 selected"));
            Assert.That(InvokeString("BuildControlConfig2StatusMessage"), Is.EqualTo("control diagnostics swapped config 2 selected"));
            Assert.That(InvokeString("BuildControlConfig3StatusMessage"), Is.EqualTo("control diagnostics alternate config 3 selected"));
            Assert.That(InvokeString("BuildControlConfig4StatusMessage"), Is.EqualTo("control diagnostics swapped alternate config 4 selected"));
            Assert.That(InvokeString("BuildClearLaunchOptionsStatusMessage"), Is.EqualTo("launch options cleared"));
        });
    }

    private static void AssertChoiceState(
        string methodName,
        string expectedNormalAutomationName,
        string expectedSelectedAutomationName)
    {
        object normalState = InvokeChoiceState(methodName, false);
        object selectedState = InvokeChoiceState(methodName, true);

        Assert.That(
            ReflectedWinUiTestSupport.GetStringProperty(normalState, "NormalAutomationName"),
            Is.EqualTo(expectedNormalAutomationName));
        Assert.That(
            ReflectedWinUiTestSupport.GetStringProperty(normalState, "SelectedAutomationName"),
            Is.EqualTo(expectedSelectedAutomationName));
        Assert.That(
            ReflectedWinUiTestSupport.GetStringProperty(normalState, "AutomationName"),
            Is.EqualTo(expectedNormalAutomationName));
        Assert.That(
            ReflectedWinUiTestSupport.GetStringProperty(selectedState, "AutomationName"),
            Is.EqualTo(expectedSelectedAutomationName));
    }

    private static object InvokeChoiceState(string methodName, bool isSelected)
    {
        return ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            methodName,
            isSelected);
    }

    private static string InvokeString(string methodName)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            methodName);
    }

    private static Type GetHelperType()
    {
        return ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchLaunchPresetText",
            ReflectedLaunchPresetSourcePaths);
    }
}
