namespace OnslaughtCareerEditor.UiTests;

public class HomeSessionResourceCleanupTests
{
    [Test]
    public void Run_InvokesAppCleanupWhenAutomationDisposeThrows()
    {
        bool appCleanupCalled = false;

        Assert.That(
            () => HomeSessionResourceCleanup.Run(
                () => throw new InvalidOperationException("automation-dispose"),
                () => appCleanupCalled = true),
            Throws.TypeOf<InvalidOperationException>()
                .With.Message.EqualTo("automation-dispose"));
        Assert.That(appCleanupCalled, Is.True);
    }

    [Test]
    public void Run_DisposesAutomationBeforeAppCleanupOnSuccess()
    {
        var order = new List<string>();

        HomeSessionResourceCleanup.Run(
            () => order.Add("automation"),
            () => order.Add("app"));

        Assert.That(order, Is.EqualTo(new[] { "automation", "app" }));
    }
}
