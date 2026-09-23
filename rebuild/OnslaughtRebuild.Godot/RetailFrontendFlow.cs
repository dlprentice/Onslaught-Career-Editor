// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The bounded released-style frontend path into the Level 100 opening slice.
/// It owns its page/input/loading lifecycle and exposes load, retry, and
/// Main Menu return seams to the existing gameplay host. Mission/HUD and audio
/// presentation remain separate owners.
/// </summary>
[Tool]
public sealed partial class RetailFrontendFlow : Control
{
    // Steam FE virtual stage (cluster hint from CFEPMain / click render).
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;
    // Production page assets, glyphs and drawing now belong to the native
    // scenes. The final retained draw/measurement provenance is in
    // Scenes/Frontend/Tests/LevelSelectReference.cs (51477f62).
    private const string FeBackStripPath =
        "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb";

    // ================= THE RELEASED PAGE-TRANSITION MACHINE =================
    //
    // Ported from the pinned GPL drop:
    //
    //   references/Onslaught/FrontEnd.cpp:563-592  CFrontEnd::SetPage(page, time)
    //       time == 0 goes straight there; time > 0 sets mTransitionCount = 0,
    //       mTransitionTime = time and parks mActivePage at FEP_TRANSITION.
    //   references/Onslaught/FrontEnd.cpp:665-675  CFrontEnd::Process()
    //       mTransitionCount++ ONCE per Process, and the destination page becomes
    //       active on the Process where mTransitionCount == mTransitionTime.
    //   references/Onslaught/FrontEnd.cpp:1291     CFrontEnd::Render()
    //       trans = float(mTransitionCount) / float(mTransitionTime).
    //   references/Onslaught/FrontEnd.cpp:1431-1438 CFrontEnd::Run()
    //       exactly one Process per rendered frame;
    //   references/Onslaught/FrontEnd.cpp:1261     Render() refuses to draw until
    //       1/60 s has passed, so a transition length is a FRAME COUNT and one
    //       frame is AT LEAST 1/60 s. Lengths are never stored as milliseconds:
    //       a wall-clock length would make the reveal host-dependent.
    //
    // Frontend.h:97 `#define MAINTIME 70` is NOT this length. It has exactly one
    // caller in the drop — FEPGoodies.cpp:1461, the Goodies BACK edge — and
    // FEPIntro.cpp is absent. The cold-start length came from the shipped bytes
    // instead; see MainMenuEntryTransitionFrames.
    //
    // NOT IMPLEMENTED, and why. FrontEnd.cpp:1291-1334 renders BOTH pages during
    // a transition (higher page ordinal first), the outgoing one at 1 - trans.
    // On this edge the outgoing page is the click page, and retail's own first
    // main-menu frame REFUTES a visible outgoing draw: at t = 14 ms
    // (run1/mm-t000014ms.png) the frame is the flat fill plus the title logo plus
    // the crosshair guides and NOTHING else, while 1 - trans = 0.98 there. The
    // ordinals are known for this edge anyway — SetPage is called with page 0 and
    // CFEPMain__Render tests dest == 0x0c, so to = 0 and from = 12, meaning
    // FrontEnd.cpp:1304 draws the click page FIRST and the main menu over it —
    // so a second draw would have to be visible under the (video-less) main menu
    // and is not. Drawing one would ADD a defect, so this lane keeps the single
    // atomic page swap it already had and records the divergence here.
    //
    /// <summary>
    /// Length of the cold-start click-to-start -> FEP_MAIN transition, in
    /// frontend frames.
    ///
    /// RECOVERED FROM THE SHIPPED BYTES, not from the drop. Read out of
    /// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>
    /// (sha256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750;
    /// the installed Steam BEA.exe is deliberately patched and is not a valid
    /// specimen). At VA 0x0051B660 / file 0x11B660, the click page's action
    /// handler:
    /// <code>
    ///   0051b660  83 7c 24 04 2c    cmp   dword [esp+4], 0x2C   ; the click action
    ///   0051b686  6a 32             push  0x32                  ; time  = 50
    ///   0051b690  6a 00             push  0                     ; page  = 0 = FEP_MAIN
    ///   0051b698  b9 58 d7 89 00    mov   ecx, 0x0089d758       ; &amp;FRONTEND
    ///   0051b69d  e8 3e b4 f4 ff    call  0x00466ae0            ; CFrontEnd::SetPage
    /// </code>
    /// So the released cold-start reveal is 50 frames, and FEP_MAIN's ordinal is 0.
    ///
    /// <para><b>The rate is the unresolved part, and it is not papered over.</b>
    /// 50 frames at the source's own 1/60 s gate settles at 817 ms. Retail's burst
    /// is settled at t = 1020 ms and NOT settled at t = 812 ms (menu-column peak
    /// channel 155 against 253 settled), so retail's realised reveal is somewhat
    /// slower than 50/60 s. FrontEnd.cpp:1261 is a floor, not a target — a frame
    /// whose work or whose <c>PLATFORM.Flip()</c> exceeds 1/60 s simply takes
    /// longer, and FrontEnd.cpp:1437 <c>while(!Render());</c> also burns whole
    /// frames without ticking the count whenever RenderStart fails, which is
    /// exactly what an async-loading video does at page entry. The frame count is
    /// evidenced; the realised frontend frame rate is NOT, and no rate constant is
    /// fitted here to close the ~15 % gap.</para>
    /// </summary>
    private const int MainMenuEntryTransitionFrames = 50;

    // WHICH BRANCH THE MAIN MENU TAKES ON THIS EDGE, and why there is no `dest`
    // variable for it. `dest` is the OTHER page of the transition, as passed at
    // FrontEnd.cpp:1299-1305 — the parameter is named for the destination but each
    // page receives its counterpart. CFEPMain__Render (0x00462D40) branches on
    // `dest == 0x0c` at five sites verified in the pristine specimen — 0x004636B2,
    // 0x00463920, 0x00463B44, 0x00463DCC and 0x0046423D, all `83 fb 0c cmp ebx,0Ch`
    // — and the page we arrive from is the click page, ordinal 12. This lane can
    // therefore only ever be on the 0x0c side, so the constant is folded into the
    // ported laws rather than carried as state. See native main_menu_laws.gd for how that
    // was settled against pixels instead of assumed.

    private int _mainTransitionCount;
    private int _mainTransitionTime;

    private GdFrontendSession _session = null!;
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];

    private Texture2D[] _feBackFrames = [];
    private string _selectLevelText = string.Empty;
    // The level-select name band and the briefing page draw the SELECTED
    // node's row through _session.SelectedLevelName; this field stays as the
    // localization-table load receipt (english.json "level100") and feeds
    // nothing on its own.
    private string _level100Text = string.Empty;
    private string _loadingText = string.Empty;
    private double _animationSeconds;
    private double _clickPulseTimer;
    private double _clickPageSeconds;
    // Seconds since the frontend left click-to-start, which is MEASURED to be
    // FEBack128's phase origin. The shared native frontend_underlay.gd owns
    // frame selection; its measurement provenance remains in the reference.
    private double _feBackSeconds;
    private RetailFrontendScreen _lastDrawnScreen = RetailFrontendScreen.ClickToStart;
    private int _loadingFrames;
    private bool _initialized;
    private bool _loadRequestRaised;
    private bool _level100Ready;
    private bool _gameplayActivationRaised;

    public event Action? Level100LoadRequested;

    public event Action? Level100LoadingStarted;

    public event Action? GameplayActivated;

    public event Action? GameplaySuspended;

    public event Action? ReturnToMainMenuRequested;

    public event Action? ExitRequested;

    internal AudioPlaybackRetirement PlaybackRetirement { get; set; } = null!;

    public event Action<RetailCareerDescriptor>? CareerSelected;

    public event Action<RetailFrontendAudioCue>? AudioCueRequested;

    public event Action<RetailFrontendCursorMode>? CursorModeRequested;

    internal RetailFrontendScreen CurrentScreen => _session.Screen;

    public void Initialize(IReadOnlyList<RetailCareerDescriptor> careerDescriptors)
    {
        if (_initialized)
        {
            throw new InvalidOperationException("The retail frontend is already initialized.");
        }

        ArgumentNullException.ThrowIfNull(careerDescriptors);
        _session?.Dispose();
        _session = new GdFrontendSession(careerDescriptors);
        LoadLocalization();
        _feBackFrames = LoadFeBackFrames(Engine.IsEditorHint() ? 1 : int.MaxValue);
        InitializeOptions();
        InitializeClick();
        InitializeMainMenu();
        InitializeQuitConfirm();
        InitializeCareerName();
        InitializeLevelSelect();
        InitializeBriefing();
        InitializeConfiguration();
        InitializeLoading();
        InitializeDebriefing();

        _initialized = true;
    }

    public override void _Notification(int what)
    {
        if (what == NotificationPredelete)
        {
            _session?.Dispose();
            _debriefingFrame?.Dispose();
        }
    }

    public void MarkLevel100Ready()
    {
        if (!_loadRequestRaised || _session.Screen != RetailFrontendScreen.Loading)
        {
            throw new InvalidOperationException(
                "Level 100 was marked ready outside the frontend loading seam.");
        }

        _level100Ready = true;
    }

    public void RestartLevel100()
    {
        RetailFrontendScreen origin = _session.Screen;
        RetailFrontendSignal signal = _session.RestartLevel100();
        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(signal);
        QueueRedraw();
    }

    public void LeaveLevel100ForMainMenu()
    {
        RetailFrontendScreen origin = _session.Screen;
        RetailFrontendSignal signal = _session.LeaveLevel100ForMainMenu();
        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(signal);
        QueueRedraw();
    }

    /// <summary>
    /// Post-Won re-entry: apply the FillOut update and show FEP_DEBRIEFING.
    /// The host tears the Level 100 world down through the existing
    /// <see cref="ReturnToMainMenuRequested"/> seam; SELECT LEVEL follows only
    /// after the player acknowledges the debriefing page.
    /// </summary>
    public void AcceptWonHandoff(
        Level100MissionOutcome outcome,
        Level100MissionTerminalState terminalState)
    {
        RetailFrontendScreen origin = _session.Screen;
        if (!_session.TryAcceptWonHandoff(outcome, terminalState))
        {
            return;
        }

        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(RetailFrontendSignal.PageChanged);
        ReturnToMainMenuRequested?.Invoke();
        QueueRedraw();
    }

    internal int LaunchWorldNumber => _session.ConsumeLaunchWorldNumber;

    internal bool SelectedWorldIsConstructible => _session.SelectedWorldIsConstructible;

    /// <summary>
    /// Loading admitted a world this reconstruction cannot build. Return to
    /// SELECT LEVEL without constructing Level 100 in its place.
    /// </summary>
    public void ReturnUnconstructibleLaunchToLevelSelect()
    {
        if (!_session.ReturnUnconstructibleLaunchToLevelSelect())
        {
            throw new InvalidOperationException(
                "An unconstructible launch can return only after its request was consumed.");
        }

        _loadRequestRaised = false;
        _level100Ready = false;
        _loadingFrames = 0;
        QueueRedraw();
    }

    internal void ConfirmForSmoke()
    {
        Confirm();
    }

    internal void SelectMainIndexForCapture(int index)
    {
        _session.SelectMainIndex(index);
        QueueRedraw();
    }

    /// <summary>
    /// Hides and freezes the frontend while retail's cold-start media owns the
    /// screen.
    ///
    /// This is not cosmetic. <see cref="_clickPulseTimer"/> and
    /// <see cref="_clickPageSeconds"/> accumulate in <c>_Process</c> whenever
    /// the session is on click-to-start, and the released splash pulse is
    /// <c>((cos(t*pi)+1)*0.375)+0.46875</c> — a function of that timer. Letting
    /// it run for the ~93 s the intro lasts would put the pulse at an arbitrary
    /// phase on the first frame the player actually sees, where retail's starts
    /// from zero because the page has only just been created.
    /// </summary>
    public void SuspendForStartupMedia()
    {
        Visible = false;
        SetProcess(false);
        SetProcessInput(false);
    }

    /// <summary>
    /// Hands the screen back after the cold-start media finishes or is skipped.
    /// The click-to-start timers are reset so the page begins from zero exactly
    /// as it does when the frontend is created cold.
    /// </summary>
    public void ResumeAfterStartupMedia()
    {
        _animationSeconds = 0d;
        _clickPulseTimer = 0d;
        _clickPageSeconds = 0d;
        Visible = true;
        SetProcess(true);
        SetProcessInput(true);
        QueueRedraw();
        _mouseCursorLayer?.QueueRedraw();
    }

    public override void _Ready()
    {
        if (Engine.IsEditorHint() && !_initialized)
        {
            try
            {
                Initialize([]);
                SetEditorPage();
            }
            catch (Exception exception)
            {
                GD.PushWarning($"Frontend assets unavailable: {exception.Message}");
                SetProcess(false);
                SetProcessInput(false);
                return;
            }
        }
        if (!_initialized)
            Initialize([]); // Running the frontend scene alone has no injected careers.
        BindSceneStage();

        if (!Engine.IsEditorHint())
            SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Ignore;
        ZIndex = 100;

        if (!Engine.IsEditorHint())
        {
            _mouseCursorLayer = new RetailMouseCursorLayer
            {
                Name = "RetailMouseCursor",
                ZIndex = 2,
            };
            _mouseCursorLayer.Configure(this);
            AddChild(_mouseCursorLayer);
        }
        SetProcess(!Engine.IsEditorHint());
        SetProcessInput(!Engine.IsEditorHint());
        QueueRedraw();
    }

    public override void _Process(double delta)
    {
        if (Engine.IsEditorHint()) return;
        double step = Math.Max(0d, delta);
        _animationSeconds += step;

        // CFrontEnd::SetPage, FrontEnd.cpp:583-591 — arm the transition on the
        // edge, exactly the edge the click page's 0x2C handler takes. Every OTHER
        // way into FEP_MAIN stays instant: FrontEnd.cpp:228-232 re-enters the
        // frontend with SetPage(FEP_MAIN, 0) on FEE_TITLE_SCREEN, and no other
        // released entry length is evidenced, so none is invented.
        if (_session.Screen == RetailFrontendScreen.MainMenu &&
            _lastDrawnScreen == RetailFrontendScreen.ClickToStart)
        {
            _mainTransitionCount = 0;
            _mainTransitionTime = MainMenuEntryTransitionFrames;
        }

        // CFrontEnd::Process, FrontEnd.cpp:665-675 — one increment per Process,
        // and the page goes active on the frame where count == time. Godot's
        // _Process is this lane's Process, and it stages the frame that _Draw
        // then rasterizes, so the first drawn frame carries count == 1 exactly as
        // FrontEnd.cpp:1433-1437 does.
        if (_mainTransitionTime > 0)
        {
            _mainTransitionCount++;
            if (_mainTransitionCount >= _mainTransitionTime)
            {
                _mainTransitionTime = 0;
            }
        }

        if (_session.Screen == RetailFrontendScreen.ClickToStart)
        {
            if (_lastDrawnScreen != RetailFrontendScreen.ClickToStart)
            {
                _clickPulseTimer = 0d;
                _clickPageSeconds = 0d;
            }

            // CFEPIntro::Process 0x0051B6B0: hold this+0x18 at 0 until
            // GetTime()-[this+4] > 1.0, seed 0x3727C5AC, then add 2*dt.
            // See RetailClickToStartPrompt. The 30 s idle write of -3 to
            // 0x008A956C is deliberately not driven here.
            _clickPageSeconds += step;
            _clickPulseTimer = RetailClickToStartPrompt.Advance(
                _clickPulseTimer,
                _clickPageSeconds,
                step);
        }
        else if (_session.Screen != RetailFrontendScreen.IntroCutscene)
        {
            // Free-runs from the moment click-to-start is left, and is NOT reset on
            // later page changes. Retail's underlay is measured to be page-anchored
            // on the main menu and NOT page-anchored on FEP_DEVSELECT or
            // FEP_LEVEL_SELECT (matched-offset cross-run material 7-44 % and
            // 5.8-63 % there against 0.4-1.5 % on the main menu), which is what a
            // single clock started once at frontend entry produces.
            //
            // IntroCutscene is excluded because retail's frontend page machine is
            // not running at all during RunIntroFMV — that call sits inside
            // CGame::RestartLoopRunLevel, not inside the frontend. Letting this
            // clock run would inject 123.8 s of phase into a MEASURED underlay
            // scroll, which is a lab artefact and not a released behaviour.
            _feBackSeconds += step;
        }

        _lastDrawnScreen = _session.Screen;

        if (_session.Screen == RetailFrontendScreen.Loading)
        {
            _loadingFrames++;
            if (!_loadRequestRaised && _loadingFrames >= 2)
            {
                if (!_session.ConsumeLevel100LaunchRequest())
                {
                    throw new InvalidOperationException("The Level 100 launch edge was lost.");
                }

                _loadRequestRaised = true;
                Level100LoadRequested?.Invoke();
            }

            if (_level100Ready)
            {
                // Retail runs the level's intro FMV HERE — after the load, with
                // the loading screen driven to 100 % and dismissed, before the
                // first gameplay frame (references/Onslaught/game.cpp:1336-1345).
                // See RetailFrontendFlow.Cutscene.cs. When there is no cutscene
                // to play this falls through to the pre-existing handoff.
                if (!TryBeginLevel100IntroCutscene())
                {
                    if (!_session.TryCompleteLoading(
                            startupMediaActive: false,
                            launchConsumed: _loadRequestRaised))
                    {
                        throw new InvalidOperationException(
                            "Level 100 can complete only after its pending launch request is consumed.");
                    }
                }
            }
        }

        if (TryRaiseGameplayActivation())
        {
            return;
        }

        QueueRedraw();
        _mouseCursorLayer?.QueueRedraw();
    }

    /// <summary>
    /// Hands the screen to gameplay on the frame the session first reaches it.
    ///
    /// Extracted from <c>_Process</c> so the intro-cutscene completion can raise
    /// the SAME edge in the SAME frame. The cutscene finishes inside its own
    /// child node's <c>_Process</c>, which Godot runs after this node's, so
    /// leaving the edge to the next frame put the session on Gameplay for one
    /// frame while nothing had been activated — a window the smoke harness
    /// observed and threw on. It is the ordering artefact, not the state, that
    /// this removes.
    /// </summary>
    private bool TryRaiseGameplayActivation()
    {
        if (_session.Screen != RetailFrontendScreen.Gameplay || _gameplayActivationRaised)
        {
            return false;
        }

        _gameplayActivationRaised = true;
        Visible = false;
        SetProcessInput(false);
        SetProcess(false);
        CursorModeRequested?.Invoke(RetailFrontendCursorMode.Captured);
        GameplayActivated?.Invoke();
        return true;
    }

    /// <summary>
    /// <c>trans</c> as FrontEnd.cpp:1291 computes it, and 1.0 once the page is
    /// active (FrontEnd.cpp:1310 renders a settled page with a literal 1.f).
    /// </summary>
    private float MainMenuTransition =>
        _mainTransitionTime <= 0
            ? 1f
            : Math.Min(1f, (float)_mainTransitionCount / _mainTransitionTime);

    public override void _Input(InputEvent inputEvent)
    {
        if (Engine.IsEditorHint()) return;
        // IntroCutscene is included because the movie owns the screen and the
        // RetailStartupSequence child owns the abort. A frontend page reacting to
        // the keypress that skips the movie would navigate an invisible page.
        if (_session.Screen is RetailFrontendScreen.Loading or
            RetailFrontendScreen.IntroCutscene or
            RetailFrontendScreen.Gameplay)
        {
            return;
        }

        // FrontEnd.cpp:551-552 — while mActivePage == FEP_TRANSITION the
        // button action is never forwarded to a page. CFEPMain::Render
        // hover is not ButtonPressed: 0x004630AC / 0x004631EF run when
        // transition > 0.9 (fcomp [0x005D8BB0]; test ah,0x41 / jne skip).
        // Motion is therefore allowed through; HandlePointerMotion applies
        // the 0.9 gate. Confirm and HandleKey stay swallowed here.
        if (RetailMainMenuHitTest.SwallowsFrontendInput(
                _mainTransitionTime > 0,
                inputEvent is InputEventMouseMotion))
        {
            return;
        }

        bool handled = inputEvent switch
        {
            InputEventMouseMotion motion => HandlePointerMotion(motion.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Left =>
                HandlePointerConfirm(button.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Right =>
                HandlePointerCancel(),
            InputEventKey key when key.Pressed && !key.Echo => HandleKey(key),
            _ => false,
        };

        if (handled)
        {
            GetViewport().SetInputAsHandled();
        }
    }

    public override void _Draw()
    {
        // Actual production page components own their drawing in the authored
        // scene. Only the outside-stage letterbox belongs to this controller.
        base.DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);
    }

    private bool HandlePointerMotion(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            if (!HandleOptionsPointerMotion(design))
            {
                return false;
            }
            QueueRedraw();
            return true;
        }

        if (_session.Screen == RetailFrontendScreen.QuitConfirm)
        {
            int choice = QuitConfirmIndexAt(design);
            if (choice < 0 || !_session.SelectQuitConfirmIndex(choice))
            {
                return false;
            }

            RequestAudioCue(RetailFrontendAudioCue.Move);
            QueueRedraw();
            return true;
        }

        if (_session.Screen != RetailFrontendScreen.MainMenu)
        {
            return false;
        }

        // 0x004630AC / 0x004631EF: hover only when transition > 0.9.
        // Language hover writes this+0x08 = -1; that is not a language
        // swap and not a button confirm. Session cannot hold -1.
        if (!RetailMainMenuHitTest.AcceptsHitTest(MainMenuTransition))
        {
            return false;
        }

        if (RetailMainMenuHitTest.LanguageHoverContains(design.X, design.Y))
        {
            return false;
        }

        int index = MainMenuIndexAt(design);
        // Retail hover requires GetActionCount ≠ 0 — ignore grayed rows.
        if (index < 0 ||
            !_session.Items[index].IsAvailable ||
            !_session.SelectMainIndex(index))
        {
            return false;
        }

        RequestAudioCue(RetailFrontendAudioCue.Move);
        QueueRedraw();
        return true;
    }

    private bool HandlePointerConfirm(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
        switch (_session.Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                // CFEPIntro::Process 0x0051B801 submits (0,0,width,width,0x2C)
                // — full window, not a glyph box. See RetailFrontendScenePath.
                if (!_session.AcceptsClickToStartMouse(
                        design.X,
                        design.Y))
                {
                    return false;
                }

                Confirm();
                return true;

            case RetailFrontendScreen.Options:
                return HandleOptionsPointerConfirm(design);

            case RetailFrontendScreen.MainMenu:
                int index = MainMenuIndexAt(design);
                if (!_session.CanAcceptMainMenuRow(index))
                {
                    return false;
                }
                if (_session.SelectMainIndex(index))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                }
                Confirm();
                return true;

            case RetailFrontendScreen.QuitConfirm:
                int choice = QuitConfirmIndexAt(design);
                if (choice < 0)
                {
                    return false;
                }
                if (_session.SelectQuitConfirmIndex(choice))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                }
                Confirm();
                return true;

            case RetailFrontendScreen.DevSelect:
                int careerTarget = CareerNameTargetAt(design);
                if (careerTarget == 1)
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal back))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(back);
                    QueueRedraw();
                    return true;
                }
                if (careerTarget == 2)
                {
                    Confirm();
                    return true;
                }
                return false;

            case RetailFrontendScreen.LevelSelect:
                int levelTarget = LevelSelectTargetAt(design);
                if (levelTarget == 1)
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal levelBack))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(levelBack);
                    QueueRedraw();
                    return true;
                }
                if (levelTarget == 2)
                {
                    Confirm();
                    return true;
                }

                // LevelNodes[0] at (148,320) — the root, world 100. The
                // measured 60x60 hit box is unchanged.
                if (levelTarget == 3)
                {
                    _ = _session.SelectWorld(RetailWorldCatalog.RootWorldNumber);
                    Confirm();
                    return true;
                }

                // LevelNodes[1] is one column pitch (60) to the right of the
                // root — the first child in the measured Episode 1 graph,
                // which the career table says is world 110. Locked until a
                // Won update unlocks it; do not Confirm the root instead.
                if (levelTarget == 4)
                {
                    if (!_session.SelectWorld(110))
                    {
                        return false;
                    }

                    Confirm();
                    return true;
                }

                return false;

            case RetailFrontendScreen.Debriefing:
                // Settled CFEPDebriefing::Render dispatches button 0x2C over
                // the entire 640x480 rectangle when mouse input is ready.
                if (!new Rect2(0f, 0f, DesignWidth, DesignHeight).HasPoint(design))
                {
                    return false;
                }

                Confirm();
                return true;

            case RetailFrontendScreen.MissionBriefing:
            case RetailFrontendScreen.SelectConfiguration:
                // Both pages carry the same two chevrons and nothing else
                // clickable this lane models.
                int pageTarget = _session.Screen == RetailFrontendScreen.SelectConfiguration
                    ? ConfigurationTargetAt(design)
                    : BriefingTargetAt(design);
                if (pageTarget == 1)
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal pageBack))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(pageBack);
                    QueueRedraw();
                    return true;
                }
                if (pageTarget == 2)
                {
                    Confirm();
                    return true;
                }
                return false;

            default:
                return false;
        }
    }

    private bool HandlePointerCancel()
    {
        if (_session.Screen != RetailFrontendScreen.Options)
        {
            return false;
        }

        return HandleOptionsPointerCancel(rightDown: true);
    }

    private bool HandleKey(InputEventKey key)
    {
        // FEP_OPTIONS owns its own selection, left/right value stepping, dropdown
        // expansion and back stack, so it takes the whole key path.
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            return HandleOptionsKey(key);
        }

        // New-career FEP_DEVSELECT is editable; Load mode mirrors the selected
        // injected save name and RetailFrontendSession rejects edits.
        if (_session.Screen == RetailFrontendScreen.DevSelect &&
            _session.CareerPageMode == RetailFrontendCareerPageMode.New)
        {
            if (IsKey(key, Key.Backspace))
            {
                if (_session.RemoveGameNameCharacter())
                {
                    QueueRedraw();
                }
                return true;
            }

            if (IsKey(key, Key.Left) || IsKey(key, Key.Up) || IsKey(key, Key.Right) || IsKey(key, Key.Down))
            {
                _session.MoveGameNameCursor(IsKey(key, Key.Right) || IsKey(key, Key.Down));
                QueueRedraw();
                return true;
            }
            if (IsKey(key, Key.Home) || IsKey(key, Key.End) || IsKey(key, Key.Delete)) return true;
            if (key.Unicode >= 32)
            {
                if (key.Unicode <= char.MaxValue &&
                    _session.AppendGameNameCharacter((char)key.Unicode, MeasureGameNameExtent(_session.GameName)))
                    QueueRedraw();
                return true;
            }
        }

        // QuitConfirm is a vertical YESNO stack. Retail
        // CFrontEnd__HandleModalPanelButton 0x0044dd60 option_mode 2:
        // BUTTON_FRONTEND_MENU_UP (0x2a) writes this+0x1fa0 = 1 (Yes, upper);
        // DOWN (0x2b) writes 0 (No, lower). PCController.cpp maps KEYCODE_UP /
        // KEYCODE_DOWN onto those buttons. Left/Right keep the session
        // 0=No / 1=Yes MovePrevious / MoveNext law.
        if (_session.Screen == RetailFrontendScreen.QuitConfirm)
        {
            if (IsKey(key, Key.Up))
            {
                if (_session.SelectQuitConfirmIndex(RetailFeMessBox.YesChoiceIndex))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                    QueueRedraw();
                }

                return true;
            }

            if (IsKey(key, Key.Down))
            {
                if (_session.SelectQuitConfirmIndex(RetailFeMessBox.DefaultChoiceIndex))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                    QueueRedraw();
                }

                return true;
            }
        }

        if (IsKey(key, Key.Up) || IsKey(key, Key.Left))
        {
            if (_session.MovePrevious())
            {
                RequestAudioCue(RetailFrontendAudioCue.Move);
                QueueRedraw();
            }
            return true;
        }
        if (IsKey(key, Key.Down) || IsKey(key, Key.Right))
        {
            if (_session.MoveNext())
            {
                RequestAudioCue(RetailFrontendAudioCue.Move);
                QueueRedraw();
            }
            return true;
        }
        if (IsKey(key, Key.Enter) || IsKey(key, Key.KpEnter) || IsKey(key, Key.Space))
        {
            if (_session.Screen == RetailFrontendScreen.ClickToStart
                && !_session.AcceptsClickToStartKey(
                    ScanCodeFor(key)))
            {
                return true;
            }

            Confirm();
            return true;
        }
        if (IsKey(key, Key.Escape))
        {
            if (_session.TryBackPage(
                    startupMediaActive: false,
                    out RetailFrontendSignal signal))
            {
                RequestAudioCue(RetailFrontendAudioCue.Back);
                HandleNavigationSignal(signal);
                QueueRedraw();
            }
            return true;
        }

        return false;
    }

    private void Confirm()
    {
        if (!_session.TryConfirmPage(
                startupMediaActive: false,
                out RetailFrontendSignal signal))
        {
            return;
        }

        // CFEPOptions::TransitionNotification reuses one persistent frontend
        // pause-menu context/tree but starts a fresh root session on each entry.
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            ResetOptions();
        }

        RequestAudioCue(RetailFrontendAudioCue.Select);
        HandleNavigationSignal(signal);
        if (signal == RetailFrontendSignal.ExitRequested)
        {
            ExitRequested?.Invoke();
        }
        QueueRedraw();
    }

    private void ResumeFrontendForNavigation(RetailFrontendScreen origin)
    {
        if (origin == RetailFrontendScreen.Gameplay)
        {
            GameplaySuspended?.Invoke();
        }

        Visible = true;
        SetProcessInput(true);
        SetProcess(true);
        QueueRedraw();
        _mouseCursorLayer?.QueueRedraw();
    }

    private void HandleNavigationSignal(RetailFrontendSignal signal)
    {
        if (signal == RetailFrontendSignal.LevelLaunchRequested)
        {
            _loadRequestRaised = false;
            _level100Ready = false;
            _gameplayActivationRaised = false;
            _loadingFrames = 0;
            Level100LoadingStarted?.Invoke();
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Hidden);
        }
        else if (signal == RetailFrontendSignal.ReturnToMainMenuRequested)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
            ReturnToMainMenuRequested?.Invoke();
        }
        else if (signal == RetailFrontendSignal.CareerLoadRequested)
        {
            RetailCareerDescriptor selectedCareer =
                _session.ConsumeSelectedCareerLoadRequest()
                ?? throw new InvalidOperationException(
                    "CareerLoadRequested did not carry a selected career descriptor.");
            CareerSelected?.Invoke(selectedCareer);
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
        }
        else if (signal == RetailFrontendSignal.PageChanged)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
        }
    }

    private int MainMenuIndexAt(Vector2 designPosition)
    {
        if (_stage is null) return -1;
        Vector2 canvasPoint = _stage.GetGlobalTransformWithCanvas() * designPosition;
        return _mainMenuView.Call("hit_test", canvasPoint).AsInt32();
    }

    private void LoadLocalization()
    {
        const string resourcePath = "res://Assets/Frontend/english.json";
        string source = Godot.FileAccess.GetFileAsString(resourcePath);
        if (string.IsNullOrEmpty(source))
        {
            throw new InvalidDataException($"Released frontend localization is missing: {resourcePath}");
        }

        using JsonDocument document = JsonDocument.Parse(source);
        JsonElement root = document.RootElement;
        if (root.GetProperty("schema").GetString() != "onslaught.frontend-strings.v1" ||
            root.GetProperty("culture").GetString() != "en" ||
            root.GetProperty("sourceSha256").GetString() !=
                "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a")
        {
            throw new InvalidDataException("Released frontend localization has unexpected identity.");
        }

        JsonElement strings = root.GetProperty("strings");
        _menuText.Add(RetailFrontendMenuItemKind.NewGame, RequiredString(strings, "newGame"));
        _menuText.Add(RetailFrontendMenuItemKind.ContinueGame, RequiredString(strings, "continueGame"));
        _menuText.Add(RetailFrontendMenuItemKind.LoadGame, RequiredString(strings, "loadGame"));
        _menuText.Add(RetailFrontendMenuItemKind.Multiplayer, RequiredString(strings, "multiplayer"));
        _menuText.Add(RetailFrontendMenuItemKind.Goodies, RequiredString(strings, "goodies"));
        _menuText.Add(RetailFrontendMenuItemKind.Options, RequiredString(strings, "options"));
        // Index 6 menu label = FrontEndText token 8 → english.dat "Quit" (KEEP).
        // Messbox copy is Localization id 0xe4 (EXE table), not drawn on the row.
        _menuText.Add(RetailFrontendMenuItemKind.Quit, RequiredString(strings, "quit"));
        _selectLevelText = RequiredString(strings, "selectLevel");
        // The band and briefing draw the SELECTED node's row through
        // RetailFrontendWorldStrings; this load receipt stays as the proof
        // the menu table itself is present and identity-checked.
        _level100Text = RequiredString(strings, "level100");
        if (_level100Text != OnslaughtRebuild.Core.RetailFrontendWorldStrings.LevelName(100))
        {
            throw new InvalidDataException(
                "english.json level100 row diverged from the decoded world-strings table.");
        }
        _loadingText = RequiredString(strings, "loading");
    }

    private static Texture2D[] LoadFeBackFrames(int maximumFrames = int.MaxValue)
    {
        using Resource recipe = GD.Load<Resource>("res://Scenes/Frontend/FrontendUnderlay.tres");
        using Variant returned = recipe.Call("load_frames", maximumFrames);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireOptionsResult(result);
        if (result["missing"].AsBool())
            GD.PushWarning($"FEBack strip missing at {FeBackStripPath}; main underlay uses solid fallback.");
        using Variant frameList = result["frames"];
        using Godot.Collections.Array frames = frameList.AsGodotArray();
        var textures = new Texture2D[frames.Count];
        for (int index = 0; index < textures.Length; index++)
        {
            using Variant frame = frames[index];
            textures[index] = frame.As<Texture2D>();
        }
        return textures;
    }

    private (float Scale, Vector2 Offset) DesignTransform()
    {
        float scale = Mathf.Min(Size.X / DesignWidth, Size.Y / DesignHeight);
        return (
            scale,
            new Vector2(
                (Size.X - (DesignWidth * scale)) * 0.5f,
                (Size.Y - (DesignHeight * scale)) * 0.5f));
    }

    private Vector2 ToDesignPosition(Vector2 viewportPosition)
    {
        (float scale, Vector2 offset) = DesignTransform();
        return scale <= 0f ? Vector2.Zero : (viewportPosition - offset) / scale;
    }

    private static string RequiredString(JsonElement strings, string key)
    {
        string? value = strings.GetProperty(key).GetString();
        return string.IsNullOrEmpty(value)
            ? throw new InvalidDataException($"Released frontend localization is missing '{key}'.")
            : value;
    }

    private static bool IsKey(InputEventKey input, Key key) =>
        input.PhysicalKeycode == key || input.Keycode == key;

    private static int ScanCodeFor(InputEventKey key)
    {
        Key code = key.PhysicalKeycode != Key.None ? key.PhysicalKeycode : key.Keycode;
        return code switch
        {
            Key.Space => 0x39,
            Key.Enter => 0x1C,
            Key.Escape => 0x01,
            Key.KpEnter => 0x9C,
            _ => 0,
        };
    }

    private void RequestAudioCue(RetailFrontendAudioCue cue) =>
        AudioCueRequested?.Invoke(cue);
}
