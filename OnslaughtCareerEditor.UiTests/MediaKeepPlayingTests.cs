using System;
using System.Collections.Generic;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Media page holds three and a half hours of a soundtrack that was never released, and it
/// used to stop dead after every track. This is the "what plays next" decision, kept out of the
/// page so its edge cases can be reached without a running app - because the edge cases are
/// exactly where a music player becomes annoying again.
/// </summary>
[TestFixture]
public class MediaKeepPlayingTests
{
    private static MediaAudioItem Track(string name) =>
        new(name, $@"X:\music\{name}.ogg", "Music", 0, "3:00");

    private static IReadOnlyList<MediaAudioItem> Order(params string[] names)
    {
        var list = new List<MediaAudioItem>();
        foreach (string name in names)
            list.Add(Track(name));

        return list;
    }

    [Test]
    public void PlaysTheNextTrackInTheOrderShown()
    {
        IReadOnlyList<MediaAudioItem> order = Order("one", "two", "three");

        MediaAudioItem? next = MediaKeepPlaying.FindNext(order, order[0]);

        Assert.That(next, Is.Not.Null);
        Assert.That(next!.Name, Is.EqualTo("two"));
    }

    /// <summary>The end of the list is still an end. It must not wrap round to the start.</summary>
    [Test]
    public void StopsAtTheEndRatherThanLoopingForever()
    {
        IReadOnlyList<MediaAudioItem> order = Order("one", "two");

        Assert.That(MediaKeepPlaying.FindNext(order, order[1]), Is.Null);
    }

    /// <summary>
    /// A search can narrow the tree while a track is playing. Guessing a position then would start
    /// something the person cannot see on screen.
    /// </summary>
    [Test]
    public void StopsWhenTheFinishedTrackIsNoLongerInTheList()
    {
        Assert.That(MediaKeepPlaying.FindNext(Order("one", "two"), Track("filtered-away")), Is.Null);
    }

    [Test]
    public void HandlesNothingToPlayWithoutThrowing()
    {
        Assert.Multiple(() =>
        {
            Assert.That(MediaKeepPlaying.FindNext(Array.Empty<MediaAudioItem>(), Track("one")), Is.Null);
            Assert.That(MediaKeepPlaying.FindNext(Order("one"), null), Is.Null);
            Assert.That(MediaKeepPlaying.FindNext(null, Track("one")), Is.Null);
        });
    }

    /// <summary>
    /// Identity is the path, not the display name: the same file appears under more than one
    /// heading, and two different files can share a name.
    /// </summary>
    private static MediaVideoItem Video(string name, string section) =>
        new(name, $@"X:ideo\{name}.vid", section, 0, "10 MB");

    /// <summary>
    /// The theater starts at the first cutscene, not at the NVIDIA logo. The section is the join
    /// because the catalog is what decides which videos are story and which are logos, briefings
    /// or the menu background.
    /// </summary>
    [Test]
    public void TheStoryStartsAtTheFirstCutsceneNotTheFirstVideo()
    {
        var order = new[]
        {
            Video("NVIDIA Logo", "Main Videos"),
            Video("Lost Toys Logo", "Main Videos"),
            Video("Cutscene 01", "Cutscenes"),
            Video("Cutscene 02", "Cutscenes"),
        };

        Assert.That(MediaKeepPlaying.FirstCutscene(order)!.Name, Is.EqualTo("Cutscene 01"));
    }

    [Test]
    public void TheStoryRollsOnToTheNextCutscene()
    {
        var order = new[] { Video("Cutscene 01", "Cutscenes"), Video("Cutscene 02", "Cutscenes") };

        Assert.That(MediaKeepPlaying.FindNextVideo(order, order[0])!.Name, Is.EqualTo("Cutscene 02"));
        Assert.That(MediaKeepPlaying.FindNextVideo(order, order[1]), Is.Null, "The last one is the end.");
    }

    [Test]
    public void AnInstallWithNoCutscenesOffersNothingRatherThanTheWrongThing()
    {
        Assert.Multiple(() =>
        {
            Assert.That(MediaKeepPlaying.FirstCutscene(new[] { Video("NVIDIA Logo", "Main Videos") }), Is.Null);
            Assert.That(MediaKeepPlaying.FirstCutscene(Array.Empty<MediaVideoItem>()), Is.Null);
            Assert.That(MediaKeepPlaying.FirstCutscene(null), Is.Null);
        });
    }

    [Test]
    public void MatchesOnThePathSoARepeatedNameDoesNotJumpTheQueue()
    {
        var first = new MediaAudioItem("intro", @"X:\a\intro.ogg", "Music", 0, "1:00");
        var decoy = new MediaAudioItem("intro", @"X:\b\intro.ogg", "Voice", 1, "1:00");
        var last = new MediaAudioItem("outro", @"X:\b\outro.ogg", "Voice", 1, "1:00");

        MediaAudioItem? next = MediaKeepPlaying.FindNext(new[] { first, decoy, last }, decoy);

        Assert.That(next!.Name, Is.EqualTo("outro"));
    }
}
