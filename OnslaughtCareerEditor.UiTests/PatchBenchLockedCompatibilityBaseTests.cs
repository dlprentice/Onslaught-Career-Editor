using System;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchLockedCompatibilityBaseTests
{
    private const string RequiredCopy = "Required and automatically included in every safe game copy";

    private static readonly string[] ReflectedSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopySelectionReadiness.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopySelectionReadinessState.cs",
        "OnslaughtCareerEditor.WinUI/Models/BinaryPatchItemModel.cs",
    ];

    [Test]
    public void PatchRows_LockOnlyTheExactRequiredCompatibilityPair()
    {
        AssertRequiredRow("resolution_gate");
        AssertRequiredRow("force_windowed");
        AssertOptionalRow("extra_graphics_default_on");
        AssertOptionalRow("ignore_cardid_tweak_overrides");
    }

    [TestCase(true, false, null, 0, true, "Required compatibility base ready. No optional mods selected.")]
    [TestCase(true, false, null, 1, true, "Required compatibility base ready with 1 optional mod selected.")]
    [TestCase(true, false, null, 2, true, "Required compatibility base ready with 2 optional mods selected.")]
    [TestCase(false, false, null, 0, false, "Selection is valid. Choose a read-only BEA.exe source to create a safe game copy.")]
    [TestCase(true, true, null, 1, false, "Safe game copy work is already in progress.")]
    [TestCase(true, false, "Choose only one frontend margin color.", 2, false, "Review optional mods: Choose only one frontend margin color.")]
    public void SafeCopyReadiness_ProjectsBoundedSelectionState(
        bool hasSourceExecutable,
        bool isBusy,
        string? validationError,
        int optionalPatchCount,
        bool expectedCanCreate,
        string expectedStatus)
    {
        Type helperType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopySelectionReadiness",
            ReflectedSourcePaths);

        object state = ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            helperType,
            "Build",
            hasSourceExecutable,
            isBusy,
            validationError,
            optionalPatchCount);

        Assert.Multiple(() =>
        {
            Assert.That(GetProperty<bool>(state, "CanCreate"), Is.EqualTo(expectedCanCreate));
            Assert.That(GetProperty<string>(state, "Status"), Is.EqualTo(expectedStatus));
        });
    }

    [Test]
    public void PageSelectionPaths_ReassertRequiredBaseAndUseBaseAwareChoiceSemantics()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("private readonly HashSet<string> _requiredCompatibilityKeys;"));
            Assert.That(code, Does.Contain("_requiredCompatibilityKeys = defaultProfileKeys.ToHashSet(StringComparer.OrdinalIgnoreCase);"));
            Assert.That(code, Does.Contain("selected.UnionWith(_requiredCompatibilityKeys);"));
            Assert.That(code, Does.Contain("private void EnsureRequiredCompatibilitySelected()"));
            Assert.That(code, Does.Contain("EnsureRequiredCompatibilitySelected();"));
            Assert.That(code, Does.Contain("SetEquals(selectedKeys, _requiredCompatibilityKeys)"));
            Assert.That(code, Does.Contain("SetEquals(selectedKeys, _requiredCompatibilityKeys.Concat(s_modernGraphicsKeys).ToArray())"));
            Assert.That(code, Does.Contain("SelectOnlyKeys(Array.Empty<string>());"));
        });
    }

    [Test]
    public void LabRows_LockSelectionWithoutDisablingDetailsOrChangingAutomationIds()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("IsEnabled=\"{Binding CanChangeSelection}\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding RowAutomationId}\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding CheckBoxAutomationId}\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding DetailsAutomationId}\""));
            Assert.That(xaml, Does.Not.Contain("<Expander IsEnabled=\"{Binding CanChangeSelection}\""));
        });
    }

    [Test]
    public void SafeCopyCreateButtons_ShareContinuousSelectionReadiness()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchSafeCopySelectionReadiness\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"PatchBenchSafeCopySelectionReadiness\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.Name=\"Safe copy selection readiness\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.LiveSetting=\"Polite\""));
            Assert.That(code, Does.Contain("BinaryPatchPlanBuilder.ValidateVisibleSelection(visibleSelectedKeys)"));
            Assert.That(code, Does.Contain("!_requiredCompatibilityKeys.Contains(key)"));
            Assert.That(code, Does.Contain("PatchBenchSafeCopySelectionReadiness.Build("));
            Assert.That(code, Does.Contain("PatchBenchPrepareCopiedProfileButton.IsEnabled = readiness.CanCreate;"));
            Assert.That(code, Does.Contain("PatchBenchTopCreateSafeCopyButton.IsEnabled = readiness.CanCreate;"));
            Assert.That(code, Does.Contain("PatchBenchSafeCopySelectionReadiness.Text = readiness.Status;"));
            Assert.That(code, Does.Contain("AutomationProperties.SetName(PatchBenchSafeCopySelectionReadiness, readiness.Status);"));
        });
    }

    [Test]
    public void SafeCopyClick_RevalidatesAndReturnsBeforeConfirmationOrMutation()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string handler = ExtractMethod(code, "private async void PrepareCopiedProfileButton_Click", "private async void LaunchCopiedProfileButton_Click");
        int guardIndex = handler.IndexOf("if (!readiness.CanCreate)", StringComparison.Ordinal);
        int returnIndex = guardIndex >= 0
            ? handler.IndexOf("return;", guardIndex, StringComparison.Ordinal)
            : -1;
        int confirmIndex = handler.IndexOf("ConfirmAsync(", StringComparison.Ordinal);
        int prepareIndex = handler.IndexOf("GameProfilePreflightService.PrepareWindowedCompatibilityProfile", StringComparison.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(handler, Does.Contain("EnsureRequiredCompatibilitySelected();"));
            Assert.That(handler, Does.Contain("BuildSafeCopySelectionReadiness()"));
            Assert.That(handler, Does.Contain("OperationLogTextBox.Text = readiness.Status;"));
            Assert.That(guardIndex, Is.GreaterThanOrEqualTo(0));
            Assert.That(returnIndex, Is.GreaterThan(guardIndex));
            Assert.That(confirmIndex, Is.GreaterThan(returnIndex));
            Assert.That(prepareIndex, Is.GreaterThan(confirmIndex));
            Assert.That(handler[..confirmIndex], Does.Not.Contain("Directory.CreateDirectory"));
            Assert.That(handler[..confirmIndex], Does.Not.Contain("File.Copy"));
        });
    }

    [Test]
    public void SafeCopyClick_LatchesBusyBeforeConfirmationAndAlwaysReleasesIt()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string handler = ExtractMethod(code, "private async void PrepareCopiedProfileButton_Click", "private async void LaunchCopiedProfileButton_Click");
        int latchIndex = handler.IndexOf("_isPreparingCopiedProfile = true;", StringComparison.Ordinal);
        int tryIndex = handler.IndexOf("try", latchIndex, StringComparison.Ordinal);
        int controlRefreshIndex = handler.IndexOf("UpdateControlState();", latchIndex, StringComparison.Ordinal);
        int confirmIndex = handler.IndexOf("ConfirmAsync(", StringComparison.Ordinal);
        int awaitingIndex = handler.IndexOf("_isAwaitingCopiedProfileConfirmation = true;", StringComparison.Ordinal);
        int confirmedIndex = handler.IndexOf("_isAwaitingCopiedProfileConfirmation = false;", confirmIndex, StringComparison.Ordinal);
        int finallyIndex = handler.LastIndexOf("finally", StringComparison.Ordinal);
        int releaseIndex = handler.LastIndexOf("_isPreparingCopiedProfile = false;", StringComparison.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(latchIndex, Is.GreaterThanOrEqualTo(0));
            Assert.That(tryIndex, Is.GreaterThan(latchIndex));
            Assert.That(controlRefreshIndex, Is.GreaterThan(tryIndex));
            Assert.That(confirmIndex, Is.GreaterThan(controlRefreshIndex));
            Assert.That(awaitingIndex, Is.GreaterThanOrEqualTo(latchIndex));
            Assert.That(awaitingIndex, Is.LessThan(confirmIndex));
            Assert.That(confirmedIndex, Is.GreaterThan(confirmIndex));
            Assert.That(finallyIndex, Is.GreaterThan(confirmIndex));
            Assert.That(releaseIndex, Is.GreaterThan(finallyIndex));
            Assert.That(code, Does.Contain("Waiting for safe copy confirmation."));
        });
    }

    private static void AssertRequiredRow(string key)
    {
        object model = CreatePatchItemModel(key);
        Assert.Multiple(() =>
        {
            Assert.That(GetProperty<bool>(model, "IsRequiredCompatibilityBase"), Is.True);
            Assert.That(GetProperty<bool>(model, "CanChangeSelection"), Is.False);
            Assert.That(GetProperty<string>(model, "UserFacingStatus"), Does.StartWith(RequiredCopy));
            Assert.That(GetProperty<string>(model, "AccessibilityHelpText"), Does.Contain(RequiredCopy));
        });
    }

    private static void AssertOptionalRow(string key)
    {
        object model = CreatePatchItemModel(key);
        Assert.Multiple(() =>
        {
            Assert.That(GetProperty<bool>(model, "IsRequiredCompatibilityBase"), Is.False);
            Assert.That(GetProperty<bool>(model, "CanChangeSelection"), Is.True);
            Assert.That(GetProperty<string>(model, "UserFacingStatus"), Does.Not.Contain(RequiredCopy));
        });
    }

    private static object CreatePatchItemModel(string key)
    {
        BinaryPatchSpec spec = BinaryPatchPlanBuilder.GetVisibleSpecs()
            .Single(candidate => string.Equals(candidate.Key, key, StringComparison.Ordinal));
        Type modelType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.BinaryPatchItemModel",
            ReflectedSourcePaths);

        return Activator.CreateInstance(modelType, spec)
            ?? throw new InvalidOperationException($"Could not create {modelType.FullName} for {key}.");
    }

    private static T GetProperty<T>(object instance, string propertyName)
    {
        PropertyInfo property = instance.GetType().GetProperty(propertyName, BindingFlags.Instance | BindingFlags.Public)
            ?? throw new InvalidOperationException($"Missing property {instance.GetType().FullName}.{propertyName}.");
        return (T)(property.GetValue(instance)
            ?? throw new InvalidOperationException($"Property {instance.GetType().FullName}.{propertyName} was null."));
    }

    private static string ReadRepoFile(params string[] parts)
    {
        string path = Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }

    private static string ExtractMethod(string code, string startMarker, string endMarker)
    {
        int start = code.IndexOf(startMarker, StringComparison.Ordinal);
        int end = code.IndexOf(endMarker, start, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), $"Missing method start marker: {startMarker}");
        Assert.That(end, Is.GreaterThan(start), $"Missing method end marker: {endMarker}");
        return code[start..end];
    }
}
