using System;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchLabCreationInputTextTests
{
    private static readonly string[] ReflectedSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLabCreationInputText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchLabCreationInputState.cs",
    ];

    [TestCase(0, 0, 0, false, false, false, "Extra settings for next copy: none active.")]
    [TestCase(1, 0, 0, false, false, false, "Extra settings for next copy: 1 patch choice.")]
    [TestCase(2, 1, 2, true, false, false, "Extra settings for next copy: 2 patch choices; 1 launch modifier; 2 copied-options changes; 1 create-time music experiment.")]
    [TestCase(0, 0, 0, false, true, false, "Extra settings for next copy: 1 Level 100 English text mod.")]
    [TestCase(0, 0, 0, false, false, true, "Extra settings for next copy: 1 Level 100 gameplay mod.")]
    public void Status_ListsOnlyCreationInputCategories(
        int patches,
        int launch,
        int copiedOptions,
        bool music,
        bool level100TextMod,
        bool level100EarlyFlightMod,
        string expected)
    {
        object state = CreateState(patches, launch, copiedOptions, music, level100TextMod, level100EarlyFlightMod);
        string actual = InvokeString("BuildStatus", state);

        Assert.That(actual, Is.EqualTo(expected));
    }

    [Test]
    public void ConfirmationSection_UsesTheSameCreationInputProjection()
    {
        object state = CreateState(1, 2, 0, false, false, false);

        Assert.That(
            InvokeString("BuildConfirmationSection", state),
            Is.EqualTo($"Settings affecting this copy:{Environment.NewLine}Extra settings for next copy: 1 patch choice; 2 launch modifiers."));
    }

    [Test]
    public void PublicFormatterBoundary_CannotAcceptNonCreationOperationState()
    {
        Type helper = GetHelperType();
        Type state = GetStateType();

        MethodInfo[] publicMethods = helper.GetMethods(BindingFlags.Public | BindingFlags.Static);
        Assert.Multiple(() =>
        {
            Assert.That(publicMethods.Select(method => method.Name), Is.EquivalentTo(new[] { "BuildStatus", "BuildConfirmationSection" }));
            Assert.That(publicMethods.All(method => method.GetParameters().Select(parameter => parameter.ParameterType).SequenceEqual(new[] { state })), Is.True);
            Assert.That(state.GetConstructors().Single().GetParameters().Select(parameter => parameter.Name),
                Is.EqualTo(new[] { "OptionalPatchCount", "LaunchModifierCount", "CopiedOptionsCount", "HasCreateTimeMusicExperiment", "HasLevel100TextMod", "HasLevel100EarlyFlightMod" }));
        });
    }

    private static object CreateState(
        int patches,
        int launch,
        int copiedOptions,
        bool music,
        bool level100TextMod,
        bool level100EarlyFlightMod)
    {
        return Activator.CreateInstance(GetStateType(), patches, launch, copiedOptions, music, level100TextMod, level100EarlyFlightMod)
            ?? throw new InvalidOperationException("Could not create Lab creation-input state.");
    }

    private static string InvokeString(string methodName, object state)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(GetHelperType(), methodName, state);
    }

    private static Type GetHelperType() => ReflectedWinUiTestSupport.GetRequiredType(
        "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchLabCreationInputText",
        ReflectedSourcePaths);

    private static Type GetStateType() => ReflectedWinUiTestSupport.GetRequiredType(
        "OnslaughtCareerEditor.WinUI.Models.PatchBenchLabCreationInputState",
        ReflectedSourcePaths);
}
