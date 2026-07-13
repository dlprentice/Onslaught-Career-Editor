using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[TestFixture]
public sealed class ModernControllerSetupGuidanceTests
{
    [Test]
    public void GameOptions_ExposesEvidenceBoundedModernControllerSetup()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        XDocument document = XDocument.Parse(xaml);

        Assert.Multiple(() =>
        {
            AssertAutomationId(document, "ModernControllerSetupCard");
            AssertAutomationId(document, "ModernControllerSetupHeading");
            AssertAutomationId(document, "ModernControllerSetupSteps");
            AssertAutomationId(document, "ModernControllerSetupBoundary");
            AssertAutomationId(document, "OpenZigguratControllerGuideButton");
            AssertAutomationId(document, "ControllerConfigNumericCaveat");

            Assert.That(xaml, Does.Contain("Modern controller setup"));
            Assert.That(xaml, Does.Contain("1. In Steam Input, select Aquila - Gamepad with Mouse Aiming."));
            Assert.That(xaml, Does.Contain("2. In the game's Controller Options, bind the buttons, then map left-stick up to Movement: Forward so the movement directions are assigned."));
            Assert.That(xaml, Does.Contain("3. Lower the game's mouse sensitivity to minimum. Adjust walking and flying inversion there if needed."));
            Assert.That(xaml, Does.Contain("The Toolkit can edit a copied options file. It does not configure Steam Input, detect your connected controller, or prove improved control feel."));
            Assert.That(xaml, Does.Contain("These P1/P2 controller config fields are raw numeric values preserved or written in the copied options data; they are not named modern-gamepad profiles."));
            Assert.That(xaml, Does.Contain("Open Ziggurat's Steam setup guide in browser"));
            Assert.That(code, Does.Contain("https://steamcommunity.com/app/1346400/discussions/0/2942494909163878759/"));
            Assert.That(code, Does.Contain("OpenZigguratControllerGuideButton_Click"));
            Assert.That(code, Does.Contain("Launcher.LaunchUriAsync(ZigguratControllerGuideUri)"));
        });
    }

    private static void AssertAutomationId(XContainer container, string automationId)
    {
        Assert.That(
            container.Descendants().Any(element =>
                string.Equals(
                    (string?)element.Attribute("AutomationProperties.AutomationId"),
                    automationId,
                    StringComparison.Ordinal)),
            Is.True,
            $"Expected AutomationProperties.AutomationId={automationId}.");
    }

    private static string ReadRepoFile(params string[] parts)
    {
        string root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
        return File.ReadAllText(Path.Combine(new[] { root }.Concat(parts).ToArray()));
    }
}
