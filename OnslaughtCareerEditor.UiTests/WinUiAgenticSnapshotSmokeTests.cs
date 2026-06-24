using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public partial class WinUiAgenticSnapshotSmokeTests
{
    private const string Schema = "winui-agentic-accessibility-snapshot.v1";
    private const int MaxDepth = 8;
    private const int MaxNodesPerScenario = 1200;
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
    };

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI and writes deterministic UIA tree snapshots for agent inspection under subagents/.")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_WritesAgentReadableAccessibilitySnapshots()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-agentic-ui-snapshot", "current");
        Directory.CreateDirectory(evidenceDir);
        foreach (string oldJson in Directory.GetFiles(evidenceDir, "*.json"))
        {
            File.Delete(oldJson);
        }

        SnapshotScenario[] scenarios =
        [
            new("home", "home", "Start Here", "HomeOpenPatchBenchButton"),
            new("windowed-mods", "binary", "Safe game copy", "PatchBenchScrollViewer"),
        ];

        List<SnapshotManifestEntry> manifestEntries = [];
        foreach (SnapshotScenario scenario in scenarios)
        {
            using SnapshotSession session = LaunchScenario(exePath, evidenceDir, scenario);
            WaitForText(session.Window, scenario.ExpectedText, TimeSpan.FromSeconds(25));
            _ = FindByAutomationId(session.Window, scenario.ExpectedAutomationId);

            SnapshotBuildResult snapshot = BuildSnapshot(session.Window);
            Assert.That(snapshot.Nodes, Has.Count.GreaterThan(20), $"Expected a useful UIA tree for {scenario.Id}.");
            Assert.That(
                snapshot.Nodes.Any(node => node.AutomationId == scenario.ExpectedAutomationId),
                Is.True,
                $"Expected snapshot to include automation id {scenario.ExpectedAutomationId}.");
            Assert.That(
                snapshot.Nodes.Any(node => node.Name.Contains(scenario.ExpectedText, StringComparison.OrdinalIgnoreCase)),
                Is.True,
                $"Expected snapshot to include visible text {scenario.ExpectedText}.");

            string fileName = $"{scenario.Id}.uia.json";
            SnapshotDocument document = new(
                Schema,
                scenario.Id,
                scenario.InitialTag,
                scenario.ExpectedAutomationId,
                scenario.ExpectedText,
                snapshot.LocalPathRedactionCount,
                snapshot.Nodes);
            File.WriteAllText(Path.Combine(evidenceDir, fileName), JsonSerializer.Serialize(document, JsonOptions));

            manifestEntries.Add(new SnapshotManifestEntry(
                scenario.Id,
                fileName,
                scenario.InitialTag,
                snapshot.Nodes.Count,
                snapshot.Nodes.Count(node => !string.IsNullOrWhiteSpace(node.AutomationId)),
                snapshot.Nodes.Count(node => !string.IsNullOrWhiteSpace(node.Name)),
                snapshot.LocalPathRedactionCount));
        }

        SnapshotManifest manifest = new(
            Schema,
            "Agent-readable WinUI UI Automation snapshots. Artifacts are generated under ignored subagents/ and path-redacted before serialization.",
            manifestEntries);
        File.WriteAllText(Path.Combine(evidenceDir, "manifest.json"), JsonSerializer.Serialize(manifest, JsonOptions));

        Assert.That(Directory.GetFiles(evidenceDir, "*.json").Select(Path.GetFileName), Is.EquivalentTo(new[]
        {
            "home.uia.json",
            "windowed-mods.uia.json",
            "manifest.json",
        }));
    }

    private static SnapshotBuildResult BuildSnapshot(Window window)
    {
        List<SnapshotNode> nodes = [];
        int ordinal = 0;
        int localPathRedactionCount = 0;

        void Visit(AutomationElement element, int depth)
        {
            if (nodes.Count >= MaxNodesPerScenario)
            {
                return;
            }

            string name = CleanText(TryGetName(element), ref localPathRedactionCount);
            string automationId = CleanText(TryGetAutomationId(element), ref localPathRedactionCount);
            string className = CleanText(TryGetClassName(element), ref localPathRedactionCount);
            nodes.Add(new SnapshotNode(
                ordinal++,
                depth,
                TryGetControlType(element),
                automationId,
                name,
                className,
                TryGetIsEnabled(element),
                TryGetIsOffscreen(element)));

            if (depth >= MaxDepth)
            {
                return;
            }

            AutomationElement[] children;
            try
            {
                children = element.FindAllChildren();
            }
            catch
            {
                return;
            }

            foreach (AutomationElement child in children)
            {
                Visit(child, depth + 1);
            }
        }

        Visit(window, 0);
        return new SnapshotBuildResult(nodes, localPathRedactionCount);
    }

    private sealed class SnapshotSession : IDisposable
    {
        public SnapshotSession(Application app, UIA3Automation automation, Window window)
        {
            App = app;
            Automation = automation;
            Window = window;
        }

        public Application App { get; }

        public UIA3Automation Automation { get; }

        public Window Window { get; }

        public void Dispose()
        {
            Automation.Dispose();
            try
            {
                App.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (!App.HasExited)
            {
                App.Kill();
            }
        }
    }

    private static SnapshotSession LaunchScenario(string exePath, string evidenceDir, SnapshotScenario scenario)
    {
        string appDataDir = PrepareIsolatedAppData(evidenceDir, scenario.Id);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = scenario.InitialTag;

        Application app = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        Window window = WaitForMainWindow(app, automation);
        return new SnapshotSession(app, automation, window);
    }

    private static string PrepareIsolatedAppData(string evidenceDir, string scenarioId)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata", scenarioId);
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            """
            {
              "gameDirectory": null,
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": -1,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": 0,
              "assetCatalogPath": null,
              "allowBackgroundAudio": true,
              "allowBackgroundVideo": false,
              "preventAudioVideoOverlap": true
            }
            """);
        return appDataDir;
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId)),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        bool handleReady = Retry.WhileFalse(
            () => app.MainWindowHandle != IntPtr.Zero,
            TimeSpan.FromSeconds(30)).Success;

        if (!handleReady)
        {
            Assert.Ignore("Main window handle not available; ensure the app can launch in this desktop session.");
        }

        Window? window = Retry.WhileNull(
            () =>
            {
                try
                {
                    return automation.FromHandle(app.MainWindowHandle).AsWindow();
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(30)).Result;

        Assert.That(window, Is.Not.Null);
        return window!;
    }

    private static string CleanText(string? value, ref int localPathRedactionCount)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return string.Empty;
        }

        string cleaned = WhitespacePattern().Replace(value.Replace('\r', ' ').Replace('\n', ' '), " ").Trim();
        if (LocalPathPattern().IsMatch(cleaned))
        {
            localPathRedactionCount++;
            cleaned = LocalPathPattern().Replace(cleaned, "[local-path-redacted]");
        }

        return cleaned.Length <= 180 ? cleaned : $"{cleaned[..177]}...";
    }

    private static string? TryGetName(AutomationElement element)
    {
        try
        {
            return element.Name;
        }
        catch
        {
            return null;
        }
    }

    private static string? TryGetAutomationId(AutomationElement element)
    {
        try
        {
            return element.AutomationId;
        }
        catch
        {
            return null;
        }
    }

    private static string? TryGetClassName(AutomationElement element)
    {
        try
        {
            return element.ClassName;
        }
        catch
        {
            return null;
        }
    }

    private static string TryGetControlType(AutomationElement element)
    {
        try
        {
            ControlType controlType = element.ControlType;
            return controlType.ToString();
        }
        catch
        {
            return "Unknown";
        }
    }

    private static bool? TryGetIsEnabled(AutomationElement element)
    {
        try
        {
            return element.IsEnabled;
        }
        catch
        {
            return null;
        }
    }

    private static bool? TryGetIsOffscreen(AutomationElement element)
    {
        try
        {
            return element.Properties.IsOffscreen.ValueOrDefault;
        }
        catch
        {
            return null;
        }
    }

    private static string ResolveWinUiAppPath()
    {
        string? explicitExePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_EXE_PATH");
        if (!string.IsNullOrWhiteSpace(explicitExePath))
        {
            return explicitExePath;
        }

        return Path.Combine(
            ResolveRepoRoot(),
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.exe");
    }

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }

    [GeneratedRegex(@"[A-Za-z]:\\[^\s""']+")]
    private static partial Regex LocalPathPattern();

    [GeneratedRegex(@"\s+")]
    private static partial Regex WhitespacePattern();

    private sealed record SnapshotScenario(
        string Id,
        string InitialTag,
        string ExpectedText,
        string ExpectedAutomationId);

    private sealed record SnapshotBuildResult(
        IReadOnlyList<SnapshotNode> Nodes,
        int LocalPathRedactionCount);

    private sealed record SnapshotDocument(
        string Schema,
        string ScenarioId,
        string InitialTag,
        string ExpectedAutomationId,
        string ExpectedText,
        int LocalPathRedactionCount,
        IReadOnlyList<SnapshotNode> Nodes);

    private sealed record SnapshotNode(
        int Ordinal,
        int Depth,
        string ControlType,
        string AutomationId,
        string Name,
        string ClassName,
        bool? IsEnabled,
        bool? IsOffscreen);

    private sealed record SnapshotManifest(
        string Schema,
        string Purpose,
        IReadOnlyList<SnapshotManifestEntry> Scenarios);

    private sealed record SnapshotManifestEntry(
        string ScenarioId,
        string OutputFile,
        string InitialTag,
        int NodeCount,
        int AutomationIdCount,
        int NamedNodeCount,
        int LocalPathRedactionCount);
}
