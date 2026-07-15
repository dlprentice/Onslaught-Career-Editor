namespace OnslaughtCareerEditor.UiTests;

public class NativeWinUiSessionResourceCleanupTests
{
    [Test]
    public void Run_StillCleansAppWhenAutomationDisposeThrows()
    {
        bool cleaned = false;

        Assert.That(
            () => NativeWinUiSessionResourceCleanup.Run(
                () => throw new InvalidOperationException("dispose"),
                () => cleaned = true),
            Throws.TypeOf<InvalidOperationException>()
                .With.Message.EqualTo("dispose"));
        Assert.That(cleaned, Is.True);
    }

    [Test]
    public void Run_DisposesAutomationBeforeCleaningApp()
    {
        var order = new List<string>();

        NativeWinUiSessionResourceCleanup.Run(
            () => order.Add("automation"),
            () => order.Add("app"));

        Assert.That(order, Is.EqualTo(new[] { "automation", "app" }));
    }
}
