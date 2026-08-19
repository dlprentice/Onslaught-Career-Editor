using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    /// <summary>
    /// The Cheats page.
    ///
    /// It writes no process memory and patches no executable. The released game turns its own
    /// cheats on when the save game name contains a particular word, so the whole feature is one
    /// verbatim copy of a save the player already has, under a different name. That is why it is
    /// safe, why it is reversible, and why the page can say plainly what it does.
    ///
    /// Every claim about what a cheat does comes from <see cref="CheatCodeCatalog"/> rather than
    /// from copy typed here, so a cheat cannot be described as tested when it was only read out
    /// of the executable.
    /// </summary>
    public sealed partial class CheatsPage : Page
    {
        private readonly Dictionary<string, CheckBox> _checkBoxesByCheatId;
        private IReadOnlyList<CheatSaveTarget> _safeCopyTargets = Array.Empty<CheatSaveTarget>();
        private string? _sourceSavePath;
        private string? _chosenOutputFolder;
        private bool _isRefreshingDestinations;
        private bool _isWriting;

        private LiveTrainerSession? _trainerSession;
        private LiveTrainerHold? _trainerHold;
        private DispatcherTimer? _trainerTimer;
        private LiveTrainerReadResult? _lastTrainerReading;
        private bool _suppressHoldToggleEvents;
        private TrainerHotkeyListener? _trainerHotkeys;

        public CheatsPage()
        {
            InitializeComponent();

            _checkBoxesByCheatId = new Dictionary<string, CheckBox>(StringComparer.OrdinalIgnoreCase)
            {
                [CheatCodeCatalog.AllGoodiesId] = AllGoodiesCheckBox,
                [CheatCodeCatalog.AllLevelsId] = AllLevelsCheckBox,
                [CheatCodeCatalog.GodModeId] = GodModeCheckBox,
                [CheatCodeCatalog.FreeCameraId] = FreeCameraCheckBox,
                [CheatCodeCatalog.GoodieGatingBypassId] = GoodieGatingBypassCheckBox,
            };

            ApplyCatalogCopy();
            RefreshSafeCopyTargets();
            RefreshComposition();
            ApplyLiveTrainerCopy();
            InitializeTrainerMusic();
            RefreshLiveTrainerControls();

            // Leaving the page must end the attachment. A handle on another process's memory that
            // outlives the screen offering it is exactly the thing this feature must not become.
            // The music goes with it, and its device handle is released rather than left open.
            Unloaded += (_, _) =>
            {
                DetachLiveTrainer("You left the page, so the app stopped watching.");
                _trainerMusic?.Dispose();
                _trainerMusic = null;

                // The hotkeys are taken from the whole machine while they are registered, so the
                // page giving them back is not tidiness - it is the difference between a tool and
                // a nuisance. DetachLiveTrainer has already released them; this drops the window
                // subclass too, because the page is gone.
                _trainerHotkeys?.Dispose();
                _trainerHotkeys = null;
            };

            AppStatusService.SetStatus("Cheats: page ready");
        }

        /// <summary>
        /// Fills the effect line, the collapsed evidence line, and the short marker from the
        /// catalog. The tick-box labels stay in XAML so they carry stable automation ids; a test
        /// pins them against the catalog names.
        /// </summary>
        private void ApplyCatalogCopy()
        {
            SetCheatCopy(
                CheatCodeCatalog.AllGoodiesId,
                AllGoodiesEffectTextBlock,
                AllGoodiesEvidenceTextBlock,
                AllGoodiesEvidenceExpander,
                AllGoodiesEvidenceTagTextBlock,
                AllGoodiesEvidenceTagBorder);
            SetCheatCopy(
                CheatCodeCatalog.AllLevelsId,
                AllLevelsEffectTextBlock,
                AllLevelsEvidenceTextBlock,
                AllLevelsEvidenceExpander,
                AllLevelsEvidenceTagTextBlock,
                AllLevelsEvidenceTagBorder);
            SetCheatCopy(
                CheatCodeCatalog.GodModeId,
                GodModeEffectTextBlock,
                GodModeEvidenceTextBlock,
                GodModeEvidenceExpander,
                GodModeEvidenceTagTextBlock,
                GodModeEvidenceTagBorder);
            SetCheatCopy(
                CheatCodeCatalog.FreeCameraId,
                FreeCameraEffectTextBlock,
                FreeCameraEvidenceTextBlock,
                FreeCameraEvidenceExpander,
                FreeCameraEvidenceTagTextBlock,
                FreeCameraEvidenceTagBorder);
            SetCheatCopy(
                CheatCodeCatalog.GoodieGatingBypassId,
                GoodieGatingBypassEffectTextBlock,
                GoodieGatingBypassEvidenceTextBlock,
                GoodieGatingBypassEvidenceExpander,
                GoodieGatingBypassEvidenceTagTextBlock,
                GoodieGatingBypassEvidenceTagBorder);
        }

        /// <summary>
        /// One cheat's copy, in the two places it now lives. The effect sentence and the tag stay
        /// on screen; the evidence sentence goes behind the disclosure. The tag is derived from the
        /// catalog rather than written into the markup, so a cheat that is downgraded to
        /// code-reading-only later starts carrying its marker without anyone editing this page.
        /// </summary>
        private void SetCheatCopy(
            string cheatId,
            TextBlock effect,
            TextBlock evidence,
            Expander disclosure,
            TextBlock tag,
            FrameworkElement tagHost)
        {
            CheatCode? cheat = CheatCodeCatalog.FindById(cheatId);
            if (cheat is null)
            {
                return;
            }

            effect.Text = cheat.WhatItDoes;
            evidence.Text = cheat.WhatWeKnow;
            AutomationProperties.SetName(disclosure, CheatsPageText.BuildEvidenceDisclosureName(cheat));

            string? marker = CheatsPageText.DescribeEvidenceTag(cheat);
            tag.Text = marker ?? string.Empty;
            tagHost.Visibility = marker is null ? Visibility.Collapsed : Visibility.Visible;
        }

        private IReadOnlyList<string> GetSelectedCheatIds()
        {
            return CheatCodeCatalog.All
                .Where(cheat => _checkBoxesByCheatId.TryGetValue(cheat.Id, out CheckBox? box) && box.IsChecked == true)
                .Select(cheat => cheat.Id)
                .ToArray();
        }

        private CheatSaveName BuildComposition()
        {
            return CheatSaveNameComposer.Compose(BaseNameTextBox.Text, GetSelectedCheatIds());
        }

        private string? GetDestinationDirectory()
        {
            if (DestinationComboBox.SelectedItem is ComboBoxItem { Tag: string tag } && tag.Length > 0)
            {
                return tag;
            }

            return _chosenOutputFolder;
        }

        private CheatSaveTarget? GetSelectedSafeCopy()
        {
            if (DestinationComboBox.SelectedItem is not ComboBoxItem { Tag: string tag } || tag.Length == 0)
            {
                return null;
            }

            return _safeCopyTargets.FirstOrDefault(target =>
                string.Equals(target.SavegamesDirectory, tag, StringComparison.OrdinalIgnoreCase));
        }

        private void RefreshSafeCopyTargets()
        {
            _isRefreshingDestinations = true;
            try
            {
                string? previous = GetDestinationDirectory();
                _safeCopyTargets = CheatSaveWriterService.FindSafeCopyTargets();
                DestinationComboBox.Items.Clear();

                foreach (CheatSaveTarget target in _safeCopyTargets)
                {
                    DestinationComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = target.DisplayName,
                        Tag = target.SavegamesDirectory,
                    });
                }

                if (!string.IsNullOrWhiteSpace(_chosenOutputFolder))
                {
                    DestinationComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = Path.GetFileName(Path.TrimEndingDirectorySeparator(_chosenOutputFolder)),
                        Tag = _chosenOutputFolder,
                    });
                }

                DestinationComboBox.IsEnabled = DestinationComboBox.Items.Count > 0;
                if (DestinationComboBox.Items.Count == 0)
                {
                    return;
                }

                int restored = -1;
                if (!string.IsNullOrWhiteSpace(previous))
                {
                    for (int index = 0; index < DestinationComboBox.Items.Count; index++)
                    {
                        if (DestinationComboBox.Items[index] is ComboBoxItem { Tag: string tag } &&
                            string.Equals(tag, previous, StringComparison.OrdinalIgnoreCase))
                        {
                            restored = index;
                            break;
                        }
                    }
                }

                DestinationComboBox.SelectedIndex = restored >= 0 ? restored : 0;
            }
            finally
            {
                _isRefreshingDestinations = false;
            }
        }

        private void RefreshComposition()
        {
            CheatSaveName composition = BuildComposition();
            ComposedNameTextBlock.Text = CheatsPageText.BuildNameHeadline(composition);
            ComposedNameExplanationTextBlock.Text = CheatsPageText.BuildNameExplanation(composition);
            SourceSaveTextBlock.Text = CheatsPageText.BuildSourceSummary(_sourceSavePath);
            DestinationTextBlock.Text = CheatsPageText.BuildDestinationSummary(
                GetSelectedSafeCopy(),
                GetSelectedSafeCopy() is null ? GetDestinationDirectory() : null);

            string? blocker = CheatsPageText.DescribeWhatIsStillNeeded(
                _sourceSavePath,
                composition,
                GetDestinationDirectory());
            WriteCheatSaveButton.IsEnabled = blocker is null && !_isWriting;
        }

        private void CheatSelectionChanged(object sender, RoutedEventArgs e)
        {
            RefreshComposition();
        }

        private void BaseNameTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            RefreshComposition();
        }

        private void DestinationComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isRefreshingDestinations)
            {
                return;
            }

            RefreshComposition();
        }

        private void RefreshSafeCopiesButton_Click(object sender, RoutedEventArgs e)
        {
            RefreshSafeCopyTargets();
            RefreshComposition();
            SetStatus(
                InfoBarSeverity.Informational,
                _safeCopyTargets.Count == 0 ? "No safe copies yet" : "Ready",
                _safeCopyTargets.Count == 0
                    ? CheatsPageText.NoSafeCopiesFoundNote
                    : $"Found {_safeCopyTargets.Count} safe {(_safeCopyTargets.Count == 1 ? "copy" : "copies")}.");
        }

        private async void ChooseSourceSaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes" });
            if (string.IsNullOrWhiteSpace(path))
            {
                return;
            }

            string? rejection = SaveEditorService.DescribeCareerSaveInputRejection(path);
            if (rejection is not null)
            {
                _sourceSavePath = null;
                SetStatus(InfoBarSeverity.Warning, "That file will not work", rejection);
                RefreshComposition();
                return;
            }

            _sourceSavePath = path;
            SetStatus(
                InfoBarSeverity.Informational,
                "Save chosen",
                $"{Path.GetFileName(path)} will be copied exactly as it is. Nothing is written to it.");
            RefreshComposition();
        }

        private async void ChooseDestinationFolderButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? folder = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (string.IsNullOrWhiteSpace(folder))
            {
                return;
            }

            _chosenOutputFolder = folder;
            RefreshSafeCopyTargets();
            SelectDestination(folder);
            RefreshComposition();
        }

        private void SelectDestination(string directory)
        {
            for (int index = 0; index < DestinationComboBox.Items.Count; index++)
            {
                if (DestinationComboBox.Items[index] is ComboBoxItem { Tag: string tag } &&
                    string.Equals(tag, directory, StringComparison.OrdinalIgnoreCase))
                {
                    DestinationComboBox.SelectedIndex = index;
                    return;
                }
            }
        }

        private void OpenDebugCameraPreviewButton_Click(object sender, RoutedEventArgs e)
        {
            App.MainWindowInstance?.NavigateToTag("binary");
        }

        private async void WriteCheatSaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isWriting)
            {
                return;
            }

            CheatSaveName composition = BuildComposition();
            string? destination = GetDestinationDirectory();
            string? blocker = CheatsPageText.DescribeWhatIsStillNeeded(_sourceSavePath, composition, destination);
            if (blocker is not null)
            {
                SetStatus(InfoBarSeverity.Warning, "Not quite ready", blocker);
                return;
            }

            _isWriting = true;
            WriteCheatSaveButton.IsEnabled = false;
            try
            {
                var request = new CheatSaveWriteRequest
                {
                    InputPath = _sourceSavePath!,
                    OutputDirectory = destination!,
                    Name = composition.Name,
                };

                CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(request);
                if (!outcome.Success && outcome.NeedsOverwriteConfirmation)
                {
                    string fileName = Path.GetFileName(outcome.OutputPath ?? composition.FileName);
                    bool replace = await ConfirmAsync(
                        "Replace that save?",
                        CheatsPageText.BuildOverwriteQuestion(fileName),
                        primaryButtonText: "Replace it");
                    if (!replace)
                    {
                        SetStatus(InfoBarSeverity.Informational, "Nothing written", "Your existing save is untouched.");
                        return;
                    }

                    outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
                    {
                        InputPath = request.InputPath,
                        OutputDirectory = request.OutputDirectory,
                        Name = request.Name,
                        AllowOverwrite = true,
                    });
                }

                if (outcome.Success)
                {
                    SetStatus(InfoBarSeverity.Success, "Done", CheatsPageText.DescribeWriteOutcome(outcome));
                    AppStatusService.SetStatus("Cheats: cheat save written");
                }
                else
                {
                    SetStatus(InfoBarSeverity.Warning, "Nothing written", CheatsPageText.DescribeWriteOutcome(outcome));
                }
            }
            finally
            {
                _isWriting = false;
                RefreshComposition();
            }
        }

        // ================================================================ live trainer

        private void ApplyLiveTrainerCopy()
        {
            LiveTrainerIntroTextBlock.Text = LiveTrainerPageText.Introduction;
            LiveTrainerSafeCopyNoteTextBlock.Text = LiveTrainerPageText.SafeCopyOnlyNote;
            LiveTrainerMissionNoteTextBlock.Text = LiveTrainerPageText.MissionRunningNote;
            LiveTrainerEvidenceHeadlineTextBlock.Text = LiveTrainerPageText.EvidenceHeadline;
            LiveTrainerEvidenceTextBlock.Text = LiveTrainerPageText.EvidenceNote;
            LiveTrainerHoldExplanationTextBlock.Text = LiveTrainerPageText.HoldExplanation;
            LiveTrainerLifeEvidenceTextBlock.Text = LiveTrainerPageText.LifeEvidenceNote;
            LiveTrainerEnergyEvidenceTextBlock.Text = LiveTrainerPageText.EnergyEvidenceNote;
            LiveTrainerShieldsHoldWarningTextBlock.Text = LiveTrainerPageText.ShieldsHoldWarning;
            LiveTrainerShieldsEvidenceTextBlock.Text = LiveTrainerPageText.ShieldsEvidenceNote;
            LiveTrainerStateEvidenceTextBlock.Text = LiveTrainerPageText.StateEvidenceNote;
            LiveTrainerHotkeyHeadlineTextBlock.Text = LiveTrainerPageText.HotkeysHeadline;
            LiveTrainerHotkeyNoteTextBlock.Text = LiveTrainerPageText.HotkeysNote;
            LiveTrainerHotkeyListTextBlock.Text = LiveTrainerPageText.DescribeHotkeys();
            LiveTrainerVulnerableHeadlineTextBlock.Text = LiveTrainerPageText.VulnerableHeadline;
            LiveTrainerVulnerableUseCheatTextBlock.Text = LiveTrainerPageText.VulnerableUseTheCheatInstead;
            LiveTrainerVulnerableEvidenceTextBlock.Text = LiveTrainerPageText.VulnerableNote;
            LiveTrainerNothingOfferedHeadlineTextBlock.Text = LiveTrainerPageText.NothingOfferedHeadline;
            LiveTrainerNothingOfferedTextBlock.Text = LiveTrainerPageText.NothingOfferedNote;
        }

        /// <summary>
        /// Attaches to the newest copy this app launched that is genuinely still running. The
        /// registry decides what "genuinely" means, and AppCore's attach gate refuses anything
        /// that is not a process this app started and can still prove the identity of.
        /// </summary>
        private void LiveTrainerWatchButton_Click(object sender, RoutedEventArgs e)
        {
            DetachLiveTrainer(null);

            App.SafeGameCopyProcesses.PruneDeadLeases();
            if (!App.SafeGameCopyProcesses.TryResolveLiveManagedProcess(out GameProfileRegisteredProcess registered))
            {
                _lastTrainerReading = null;
                LiveTrainerAttachStatusTextBlock.Text = LiveTrainerPageText.BuildAttachSummary(false, null, null);
                SetLiveTrainerStatus(
                    InfoBarSeverity.Informational,
                    "Nothing to watch",
                    LiveTrainerPageText.NothingRunningNote);
                RefreshLiveTrainerControls();
                return;
            }

            LiveTrainerAttachOutcome outcome = LiveTrainerSession.Attach(
                registered.Process,
                App.SafeGameCopyProcesses);

            if (!outcome.Success || outcome.Session is null)
            {
                _lastTrainerReading = null;
                string refusal = LiveTrainerPageText.DescribeAttachRefusal(outcome.Decision.Refusal);
                LiveTrainerAttachStatusTextBlock.Text = LiveTrainerPageText.BuildAttachSummary(false, null, refusal);
                SetLiveTrainerStatus(InfoBarSeverity.Warning, "Not watching", refusal);
                RefreshLiveTrainerControls();
                return;
            }

            _trainerSession = outcome.Session;
            _trainerHold = new LiveTrainerHold(_trainerSession);
            LiveTrainerAttachStatusTextBlock.Text = LiveTrainerPageText.BuildAttachSummary(
                true,
                LiveTrainerPageText.DescribeCopyName(registered.Process),
                null);

            StartLiveTrainerTimer(LiveTrainerHold.IdleInterval);
            LiveTrainerTick();
            StartTrainerHotkeys();
            SetLiveTrainerStatus(InfoBarSeverity.Informational, "Watching", LiveTrainerPageText.EvidenceHeadline);
            AppStatusService.SetStatus("Cheats: watching a running copy");
        }

        private void LiveTrainerStopWatchingButton_Click(object sender, RoutedEventArgs e)
        {
            DetachLiveTrainer("Stopped watching. Nothing is being read or written.");
        }

        /// <summary>
        /// Ends the attachment, clears every hold, and closes the handles. Called from the Stop
        /// button, when the page unloads, and whenever a read says the game has gone.
        /// </summary>
        private void DetachLiveTrainer(string? message)
        {
            _trainerHotkeys?.Stop();

            // The line said "the keys below are live". They are not any more, and leaving that
            // sentence on screen is the app telling a small lie about the state of the machine.
            LiveTrainerHotkeyStatusTextBlock.Text = string.Empty;

            _trainerTimer?.Stop();
            _trainerTimer = null;

            _trainerHold?.ReleaseAll();
            _trainerHold = null;

            _trainerSession?.Dispose();
            _trainerSession = null;
            _lastTrainerReading = null;

            _suppressHoldToggleEvents = true;
            try
            {
                LiveTrainerHoldLifeToggle.IsOn = false;
                LiveTrainerHoldEnergyToggle.IsOn = false;
                LiveTrainerHoldShieldsToggle.IsOn = false;

                // The music belongs to the attachment, not to the page. Leaving it playing after
                // the game has gone would be the app performing enthusiasm at nothing.
                TrainerMusicToggle.IsOn = false;
            }
            finally
            {
                _suppressHoldToggleEvents = false;
            }

            _trainerMusic?.Stop();

            if (!string.IsNullOrWhiteSpace(message))
            {
                LiveTrainerAttachStatusTextBlock.Text = LiveTrainerPageText.BuildAttachSummary(false, null, message);
                SetLiveTrainerStatus(InfoBarSeverity.Informational, "Not watching", message);
            }

            RefreshLiveTrainerControls();
        }

        /// <summary>
        /// Two rates, both slow. Watching runs at 2 Hz; holding runs at 10 Hz, half the game's own
        /// update rate, which is the lowest that visibly holds a value.
        /// </summary>
        private void StartLiveTrainerTimer(TimeSpan interval)
        {
            TimeSpan clamped = LiveTrainerHold.ClampInterval(interval);
            if (_trainerTimer is null)
            {
                _trainerTimer = new DispatcherTimer();
                _trainerTimer.Tick += (_, _) => LiveTrainerTick();
            }

            if (_trainerTimer.Interval != clamped)
            {
                _trainerTimer.Stop();
                _trainerTimer.Interval = clamped;
            }

            _trainerTimer.Start();
        }

        private void LiveTrainerTick()
        {
            if (_trainerSession is null || _trainerHold is null)
            {
                return;
            }

            LiveTrainerHoldTick tick = _trainerHold.Tick();
            _lastTrainerReading = tick.Reading;

            if (tick.Reading.Status == LiveTrainerReadStatus.ProcessGone)
            {
                DetachLiveTrainer("The copied game closed, so the app stopped watching.");
                return;
            }

            if (tick.StoppedItself)
            {
                _suppressHoldToggleEvents = true;
                try
                {
                    LiveTrainerHoldLifeToggle.IsOn = false;
                    LiveTrainerHoldEnergyToggle.IsOn = false;
                    LiveTrainerHoldShieldsToggle.IsOn = false;
                }
                finally
                {
                    _suppressHoldToggleEvents = false;
                }

                SetLiveTrainerStatus(
                    InfoBarSeverity.Informational,
                    "Holding stopped",
                    LiveTrainerPageText.DescribeHoldStop(tick));
            }

            StartLiveTrainerTimer(_trainerHold.IsHolding ? LiveTrainerHold.DefaultInterval : LiveTrainerHold.IdleInterval);
            RefreshLiveTrainerControls();
        }

        /// <summary>
        /// The one place that decides what the trainer half of the page shows and which of its
        /// controls are live. Every write control is gated on
        /// <see cref="LiveTrainerPageText.DescribeWhyWritingIsBlocked"/> returning null, which in
        /// turn needs a read that came back looking like real numbers.
        /// </summary>
        private void RefreshLiveTrainerControls()
        {
            bool attached = _trainerSession is not null;
            LivePlayerVitals? vitals = _lastTrainerReading?.Vitals;

            LiveTrainerStopWatchingButton.IsEnabled = attached;
            SetLineText(
                LiveTrainerReadingStatusTextBlock,
                LiveTrainerPageText.BuildReadingSummary(_lastTrainerReading));
            LiveTrainerLifeValueTextBlock.Text = LiveTrainerPageText.FormatVital(vitals?.Life);
            LiveTrainerEnergyValueTextBlock.Text = LiveTrainerPageText.FormatVital(vitals?.Energy);
            LiveTrainerShieldsValueTextBlock.Text = LiveTrainerPageText.FormatVital(vitals?.Shields);
            LiveTrainerStateValueTextBlock.Text = LiveTrainerPageText.FormatState(vitals);
            LiveTrainerVulnerableValueTextBlock.Text = LiveTrainerPageText.DescribeVulnerable(vitals);

            string? blocked = LiveTrainerPageText.DescribeWhyWritingIsBlocked(attached, _lastTrainerReading);
            SetLineText(LiveTrainerWritingBlockedTextBlock, blocked ?? string.Empty);

            bool canWrite = blocked is null;
            SetLiveTrainerWriteControlsEnabled(
                canWrite && vitals is not null && vitals.Life.LooksLikeAVital,
                LiveTrainerLifeNumberBox,
                LiveTrainerSetLifeButton,
                LiveTrainerHoldLifeToggle);
            SetLiveTrainerWriteControlsEnabled(
                canWrite && vitals is not null && vitals.Energy.LooksLikeAVital,
                LiveTrainerEnergyNumberBox,
                LiveTrainerSetEnergyButton,
                LiveTrainerHoldEnergyToggle);
            SetLiveTrainerWriteControlsEnabled(
                canWrite && vitals is not null && vitals.Shields.LooksLikeAVital,
                LiveTrainerShieldsNumberBox,
                LiveTrainerSetShieldsButton,
                LiveTrainerHoldShieldsToggle);
        }

        /// <summary>
        /// A status line that takes up no room when it has nothing to say. An empty line still
        /// reserves its height, and a page whose empty state is a column of blank gaps reads as
        /// broken rather than as ready.
        /// </summary>
        private static void SetLineText(TextBlock line, string text)
        {
            line.Text = text;
            line.Visibility = string.IsNullOrWhiteSpace(text) ? Visibility.Collapsed : Visibility.Visible;
        }

        private static void SetLiveTrainerWriteControlsEnabled(
            bool enabled,
            NumberBox valueBox,
            Button setButton,
            ToggleSwitch holdToggle)
        {
            valueBox.IsEnabled = enabled;
            setButton.IsEnabled = enabled;
            holdToggle.IsEnabled = enabled;
        }

        private void LiveTrainerSetLifeButton_Click(object sender, RoutedEventArgs e) =>
            WriteLiveTrainerVital(LiveTrainerVital.Life, LiveTrainerLifeNumberBox.Value);

        private void LiveTrainerSetEnergyButton_Click(object sender, RoutedEventArgs e) =>
            WriteLiveTrainerVital(LiveTrainerVital.Energy, LiveTrainerEnergyNumberBox.Value);

        private void LiveTrainerSetShieldsButton_Click(object sender, RoutedEventArgs e) =>
            WriteLiveTrainerVital(LiveTrainerVital.Shields, LiveTrainerShieldsNumberBox.Value);

        private void WriteLiveTrainerVital(LiveTrainerVital vital, double requested)
        {
            if (_trainerSession is null)
            {
                return;
            }

            if (double.IsNaN(requested))
            {
                SetLiveTrainerStatus(InfoBarSeverity.Warning, "Nothing written", "Type a number first.");
                return;
            }

            LiveTrainerWriteOutcome outcome = _trainerSession.Write(vital, (float)requested);
            string note = LiveTrainerPageText.DescribeWriteOutcome(outcome);
            SetLiveTrainerStatus(
                outcome.Success ? InfoBarSeverity.Success : InfoBarSeverity.Warning,
                outcome.Success ? "Set" : "Nothing written",
                note);
            LiveTrainerTick();
        }

        // ------------------------------------------------------------ trainer music

        private TrainerMusicPlayer? _trainerMusic;

        /// <summary>
        /// Fills the tune picker once. The names come from AppCore so the CLI and the page cannot
        /// end up calling the same track different things.
        /// </summary>
        private void InitializeTrainerMusic()
        {
            foreach (TrainerMusicTrack track in Enum.GetValues<TrainerMusicTrack>())
            {
                TrainerMusicTrackComboBox.Items.Add(new ComboBoxItem
                {
                    Content = TrainerMusicSynth.GetDisplayName(track),
                    Tag = track,
                });
            }

            TrainerMusicTrackComboBox.SelectedIndex = 0;
        }

        private TrainerMusicTrack GetSelectedTrainerMusicTrack()
        {
            return (TrainerMusicTrackComboBox.SelectedItem as ComboBoxItem)?.Tag is TrainerMusicTrack track
                ? track
                : TrainerMusicTrack.Ascent;
        }

        private void ShowTrainerMusicStatus(string? note)
        {
            if (string.IsNullOrWhiteSpace(note))
            {
                TrainerMusicStatusTextBlock.Visibility = Visibility.Collapsed;
                return;
            }

            TrainerMusicStatusTextBlock.Text = note;
            TrainerMusicStatusTextBlock.Visibility = Visibility.Visible;
        }

        private void TrainerMusicToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_suppressHoldToggleEvents)
                return;

            if (!TrainerMusicToggle.IsOn)
            {
                _trainerMusic?.Stop();
                ShowTrainerMusicStatus(null);
                return;
            }

            _trainerMusic ??= new TrainerMusicPlayer();
            _trainerMusic.Volume = (float)(TrainerMusicVolumeSlider.Value / 100.0);

            if (!_trainerMusic.Play(GetSelectedTrainerMusicTrack()))
            {
                // No output device, or one that will not take this format. Not worth an error
                // dialog over a tune - say it and put the switch back.
                TrainerMusicToggle.IsOn = false;
                ShowTrainerMusicStatus("Could not open an audio device, so there is no music. Everything else still works.");
            }
        }

        private void TrainerMusicTrackComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_trainerMusic is null || !_trainerMusic.IsPlaying)
                return;

            _trainerMusic.Play(GetSelectedTrainerMusicTrack());
        }

        private void TrainerMusicVolumeSlider_ValueChanged(
            object sender,
            Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
        {
            if (_trainerMusic is not null)
            {
                _trainerMusic.Volume = (float)(e.NewValue / 100.0);
            }
        }

        private void LiveTrainerHoldLifeToggle_Toggled(object sender, RoutedEventArgs e) =>
            ToggleLiveTrainerHold(LiveTrainerVital.Life, LiveTrainerHoldLifeToggle, LiveTrainerLifeNumberBox);

        private void LiveTrainerHoldEnergyToggle_Toggled(object sender, RoutedEventArgs e) =>
            ToggleLiveTrainerHold(LiveTrainerVital.Energy, LiveTrainerHoldEnergyToggle, LiveTrainerEnergyNumberBox);

        private void LiveTrainerHoldShieldsToggle_Toggled(object sender, RoutedEventArgs e) =>
            ToggleLiveTrainerHold(LiveTrainerVital.Shields, LiveTrainerHoldShieldsToggle, LiveTrainerShieldsNumberBox);

        /// <summary>
        /// Claims the key combinations, and says so on the page - including which ones it could
        /// not get. A hotkey that looks live and does nothing is worse than no hotkey, because the
        /// person pressing it is in a fight and believes something happened.
        /// </summary>
        private void StartTrainerHotkeys()
        {
            if (App.MainWindowInstance is not Window window)
            {
                // No window means no message path, and a registration without one would eat the
                // combination and deliver it nowhere.
                LiveTrainerHotkeyStatusTextBlock.Text = LiveTrainerPageText.HotkeysUnavailable;
                return;
            }

            _trainerHotkeys ??= new TrainerHotkeyListener(window, OnTrainerHotkeyPressed);

            IReadOnlyList<string> unavailable = _trainerHotkeys.Start();
            LiveTrainerHotkeyStatusTextBlock.Text = LiveTrainerPageText.DescribeHotkeyState(unavailable);
        }

        /// <summary>
        /// A hotkey does exactly what clicking the switch does, by clicking the switch. Routing it
        /// through the same control keeps one path rather than two: the refusals, the value in the
        /// box, and the reason writing is blocked all still apply, and they cannot drift apart
        /// from what the mouse does because there is nothing to drift.
        /// </summary>
        private void OnTrainerHotkeyPressed(TrainerHotkeyAction action)
        {
            // WM_HOTKEY arrives on the UI thread, but say so rather than depending on it.
            if (!DispatcherQueue.HasThreadAccess)
            {
                DispatcherQueue.TryEnqueue(() => OnTrainerHotkeyPressed(action));
                return;
            }

            if (_trainerHold is null)
                return;

            if (action == TrainerHotkeyAction.ReleaseAll)
            {
                LiveTrainerHoldLifeToggle.IsOn = false;
                LiveTrainerHoldEnergyToggle.IsOn = false;
                LiveTrainerHoldShieldsToggle.IsOn = false;
                AppStatusService.SetStatus("Cheats: let go of everything");
                return;
            }

            ToggleSwitch? toggle = TrainerHotkeys.VitalFor(action) switch
            {
                LiveTrainerVital.Life => LiveTrainerHoldLifeToggle,
                LiveTrainerVital.Energy => LiveTrainerHoldEnergyToggle,
                LiveTrainerVital.Shields => LiveTrainerHoldShieldsToggle,
                _ => null,
            };

            // Disabled means the numbers did not look like vitals, or nothing has been read. A
            // hotkey does not get to go around that - it is the gate, not decoration on the mouse.
            if (toggle is null || !toggle.IsEnabled)
                return;

            toggle.IsOn = !toggle.IsOn;
        }

        private void ToggleLiveTrainerHold(LiveTrainerVital vital, ToggleSwitch toggle, NumberBox valueBox)
        {
            if (_suppressHoldToggleEvents || _trainerHold is null)
            {
                return;
            }

            if (!toggle.IsOn)
            {
                _trainerHold.Release(vital);
                StartLiveTrainerTimer(_trainerHold.IsHolding ? LiveTrainerHold.DefaultInterval : LiveTrainerHold.IdleInterval);
                return;
            }

            string refusal = "Type a number first.";
            bool held = !double.IsNaN(valueBox.Value) &&
                _trainerHold.TryHold(vital, (float)valueBox.Value, out refusal);
            if (!held)
            {
                _suppressHoldToggleEvents = true;
                try
                {
                    toggle.IsOn = false;
                }
                finally
                {
                    _suppressHoldToggleEvents = false;
                }

                SetLiveTrainerStatus(
                    InfoBarSeverity.Warning,
                    "Not holding",
                    string.IsNullOrWhiteSpace(refusal) ? "Type a number first." : refusal);
                return;
            }

            StartLiveTrainerTimer(LiveTrainerHold.DefaultInterval);
        }

        private void SetLiveTrainerStatus(InfoBarSeverity severity, string title, string message)
        {
            LiveTrainerInfoBar.Severity = severity;
            LiveTrainerInfoBar.Title = title;
            LiveTrainerInfoBar.Message = message;
            LiveTrainerInfoBar.IsOpen = true;
        }

        private void SetStatus(InfoBarSeverity severity, string title, string message)
        {
            CheatsInfoBar.Severity = severity;
            CheatsInfoBar.Title = title;
            CheatsInfoBar.Message = message;
            CheatsInfoBar.IsOpen = true;
        }

        private async Task<bool> ConfirmAsync(
            string title,
            string body,
            string primaryButtonText = "Continue",
            string closeButtonText = "Cancel")
        {
            var dialog = new ContentDialog
            {
                Title = title,
                Content = new TextBlock
                {
                    Text = body,
                    TextWrapping = TextWrapping.WrapWholeWords,
                },
                PrimaryButtonText = primaryButtonText,
                CloseButtonText = closeButtonText,
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = XamlRoot,
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
        }
    }
}
