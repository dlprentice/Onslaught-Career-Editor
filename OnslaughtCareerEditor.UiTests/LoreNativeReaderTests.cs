using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Pins the Lore reader's native rendering path. The page used to host a
/// WebView2 whose content never reached the WinUI visual surface on some
/// machines; the reader now builds native controls from a presentation-neutral
/// document model, and these tests keep both halves of that honest: the page
/// surface stays WebView-free with stable automation ids, and the model keeps
/// producing the block/inline structure the renderer depends on.
/// </summary>
public class LoreNativeReaderTests
{
    private static readonly string[] StableLoreAutomationIds =
    [
        "LorePageTitle",
        "LoreSourceBoundaryStatus",
        "LoreSearchBox",
        "LoreRefreshButton",
        "LoreLibraryStatus",
        "LoreDocumentTree",
        "LoreBackButton",
        "LoreForwardButton",
        "LoreHomeButton",
        "LoreToggleLibraryButton",
        "LoreOpenExternalButton",
        "LoreCurrentDocumentTitle",
        "LoreCurrentDocumentSummary",
        "LoreReaderPanel",
        "LoreReaderScrollViewer",
        "LoreContentReader",
        "LoreReaderPlaceholder",
        "LoreReaderPlaceholderTitle",
        "LoreReaderPlaceholderBody"
    ];

    [Test]
    public void LorePage_RendersNativelyWithNoWebViewLeftBehind()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml");
        string codeBehind = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Not.Contain("WebView2"), "The Lore reader should not host a WebView2.");
            Assert.That(codeBehind, Does.Not.Contain("Microsoft.Web.WebView2"));
            Assert.That(codeBehind, Does.Not.Contain("CoreWebView2"));
            Assert.That(codeBehind, Does.Contain("LoreDocumentRenderer.Render"));
            Assert.That(codeBehind, Does.Contain("LoadDocumentContent"));
        });
    }

    [Test]
    public void LorePage_KeepsEveryStableAutomationId()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml");

        List<string> missing = StableLoreAutomationIds
            .Where(id => !xaml.Contains($"AutomationProperties.AutomationId=\"{id}\"", StringComparison.Ordinal))
            .ToList();

        Assert.That(missing, Is.Empty, "The Lore page should keep its automation ids stable for UI Automation.");
    }

    [Test]
    public void LoreReader_HostsRenderedContentInsideAScrollViewer()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml");

        Assert.That(
            xaml,
            Does.Match("<ScrollViewer[\\s\\S]*?AutomationProperties\\.AutomationId=\"LoreReaderScrollViewer\"[\\s\\S]*?AutomationProperties\\.Name=\"[^\"]+\""),
            "The reader scroll surface should be targetable and named so anchor scrolling is provable.");
        Assert.That(
            xaml,
            Does.Match("<ContentControl[\\s\\S]*?AutomationProperties\\.AutomationId=\"LoreContentReader\""),
            "Rendered lore content should live in a named host control.");
    }

    [Test]
    public void LorePageLoad_DegradesToThePlaceholderInsteadOfThrowing()
    {
        string codeBehind = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs");

        Match handler = Regex.Match(
            codeBehind,
            @"private async void LorePage_Loaded\([\s\S]*?\n        \}");

        Assert.That(handler.Success, Is.True, "Expected a LorePage_Loaded handler.");
        Assert.That(
            handler.Value,
            Does.Contain("try"),
            "LorePage_Loaded is async void; an escaping exception would take the process down.");
        Assert.That(handler.Value, Does.Contain("ShowReaderPlaceholder"));
    }

    [Test]
    public void LoreReader_KeepsItsEstablishedStatusMessages()
    {
        string codeBehind = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(codeBehind, Does.Contain("\"Lore: opened source link in browser\""));
            Assert.That(codeBehind, Does.Contain("\"Lore: opened external link in browser\""));
            Assert.That(codeBehind, Does.Contain("\"Lore: unresolved internal link\""));
            Assert.That(codeBehind, Does.Contain("$\"Lore: loaded {CurrentDocumentTextBlock.Text}\""));
        });
    }

    [Test]
    public void LoreDocumentModel_StaysFreeOfPresentationTypes()
    {
        foreach (string fileName in new[] { "LoreDocumentModel.cs", "LoreDocumentParser.cs", "LoreBrowserService.cs" })
        {
            string source = ReadRepoFile("OnslaughtCareerEditor.AppCore", fileName);
            Assert.Multiple(() =>
            {
                Assert.That(source, Does.Not.Contain("Microsoft.UI"), $"{fileName} should stay presentation-free.");
                Assert.That(source, Does.Not.Contain("Windows.UI"), $"{fileName} should stay presentation-free.");
            });
        }

        Assert.That(
            File.Exists(Path.Combine(
                TestFixturePaths.RepoRoot,
                "OnslaughtCareerEditor.WinUI",
                "Helpers",
                "LoreDocumentRenderer.cs")),
            Is.True,
            "The native renderer belongs in the WinUI layer.");
    }

    [Test]
    public void LoreBrowserService_SweepsStaleBrowserExportsFromItsOwnTempDirectory()
    {
        string source = ReadRepoFile("OnslaughtCareerEditor.AppCore", "LoreBrowserService.cs");

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("CleanupStaleRenderFilesOnce"));
            Assert.That(source, Does.Contain("RenderFileRetention"));
            Assert.That(
                source,
                Does.Contain("actual.Equals(expected, StringComparison.OrdinalIgnoreCase)"),
                "Cleanup must refuse to delete outside the toolkit's own render directory.");
        });
    }

    [Test]
    public void Parse_ProducesTheBlockStructureTheRendererSwitchesOn()
    {
        LoreDocumentModel document = LoreDocumentParser.Parse("""
# Aquila

Prose with **bold**, *italic*, `code`, and a [link](world.md).

- Alpha
  - Beta

1. First

| Frame | Role |
| --- | --- |
| Aquila | Walker |

```csharp
var tick = 20;
```

> Quoted line.

---

![Walker](images/walker.png)
""");

        Assert.Multiple(() =>
        {
            Assert.That(document.Title, Is.EqualTo("Aquila"));
            Assert.That(document.Blocks.OfType<LoreHeadingBlock>().Single().Id, Is.EqualTo("aquila"));
            Assert.That(document.Blocks.OfType<LoreParagraphBlock>().Count(), Is.EqualTo(1));
            Assert.That(document.Blocks.OfType<LoreListBlock>().Count(), Is.EqualTo(2));
            Assert.That(document.Blocks.OfType<LoreTableBlock>().Count(), Is.EqualTo(1));
            Assert.That(document.Blocks.OfType<LoreCodeBlock>().Count(), Is.EqualTo(1));
            Assert.That(document.Blocks.OfType<LoreQuoteBlock>().Count(), Is.EqualTo(1));
            Assert.That(document.Blocks.OfType<LoreThematicBreakBlock>().Count(), Is.EqualTo(1));
            Assert.That(document.Blocks.OfType<LoreImageBlock>().Single().Uri, Is.EqualTo("images/walker.png"));
        });

        LoreParagraphBlock paragraph = document.Blocks.OfType<LoreParagraphBlock>().Single();
        Assert.Multiple(() =>
        {
            Assert.That(paragraph.Inlines.OfType<LoreBoldInline>().Count(), Is.EqualTo(1));
            Assert.That(paragraph.Inlines.OfType<LoreItalicInline>().Count(), Is.EqualTo(1));
            Assert.That(paragraph.Inlines.OfType<LoreCodeInline>().Single().Text, Is.EqualTo("code"));
            Assert.That(paragraph.Inlines.OfType<LoreLinkInline>().Single().Target, Is.EqualTo("world.md"));
        });

        LoreTableBlock table = document.Blocks.OfType<LoreTableBlock>().Single();
        Assert.Multiple(() =>
        {
            Assert.That(table.Headers.Select(cell => cell.Text), Is.EqualTo(new[] { "Frame", "Role" }));
            Assert.That(table.Rows.Single().Select(cell => cell.Text), Is.EqualTo(new[] { "Aquila", "Walker" }));
        });

        LoreCodeBlock code = document.Blocks.OfType<LoreCodeBlock>().Single();
        Assert.Multiple(() =>
        {
            Assert.That(code.Language, Is.EqualTo("csharp"));
            Assert.That(code.Text, Is.EqualTo("var tick = 20;"));
        });
    }

    [Test]
    public void ClassifyLink_KeepsTheSourceAndExternalBoundaryTheChromeAdvertises()
    {
        Assert.Multiple(() =>
        {
            Assert.That(
                LoreDocumentParser.ClassifyLink("https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/README.MD"),
                Is.EqualTo(LoreLinkKind.Source));
            Assert.That(LoreDocumentParser.ClassifyLink("https://example.com/"), Is.EqualTo(LoreLinkKind.External));
            Assert.That(LoreDocumentParser.ClassifyLink("mailto:a@example.com"), Is.EqualTo(LoreLinkKind.External));
            Assert.That(LoreDocumentParser.ClassifyLink("#heading"), Is.EqualTo(LoreLinkKind.Anchor));
            Assert.That(LoreDocumentParser.ClassifyLink("lore/world.md"), Is.EqualTo(LoreLinkKind.Internal));
        });
    }

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
