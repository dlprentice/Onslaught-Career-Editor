// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The bounded released-style frontend path into the Level 100 opening slice.
/// It owns its page/input/loading lifecycle and exposes load, retry, and
/// Main Menu return seams to the existing gameplay host. Mission/HUD and audio
/// presentation remain separate owners.
/// </summary>
public sealed partial class RetailFrontendFlow : Control
{
    // Steam FE virtual stage (cluster hint from CFEPMain / click render).
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;
    private const float MenuColumnX = 219f;
    private const float MenuStartY = 304f;
    private const float MenuPitch = 20f;
    private const float MenuHitHalfWidth = 120f;
    // mustbe_TitleFont.tga — 256² atlas, 32px cells, 8 columns (A–Z / digits in lower rows).
    private const int GlyphColumns = 8;
    private const int GlyphCellSize = 32;
    private const int FirstGlyph = 32;
    private const int GlyphSlotCount = 64;

    private static readonly Color ReleasedNormal = RetailColor(0xff4f4f4f);
    private static readonly Color ReleasedUnavailable = RetailColor(0x7f1f1f1f);
    private static readonly Color ReleasedSelected = RetailColor(0xffff6f3f);
    private static readonly Color ReleasedBlue = RetailColor(0xff1f4f7f);
    private static readonly Color TitleLogoTint = RetailColor(0xfeafcfff);
    private static readonly Color HighlightTint = RetailColor(0x7e000000);
    private static readonly Color BracketTint = RetailColor(0xfeffffff);
    private static readonly Color ChromeTint = RetailColor(0x3ecfffff);
    private static readonly Color ClickSlideShadow = RetailColor(0x3f000000);
    private static readonly Color ShadowTint = RetailColor(0x3e000000);
    private static readonly Color VersionTint = RetailColor(0xff102025);
    // Settled additive gray: (((255*0x7f)>>8)*0x10101) → RGB 0x7e; keep α modest for Add blend.
    private static readonly Color GlowTint = new(0x7e / 255f, 0x7e / 255f, 0x7e / 255f, 0.5f);
    private const string VersionText = "V1.00 - PATCHED";
    private const float ShadowScaleBoost = 1.05f;
    // Materialized decode of data/video/FEBack128.vid (128² BIKi → rgb24 @15fps).
    private const string FeBackStripPath =
        "res://Assets/Frontend/Backgrounds/fe-back-128x128x15.rgb";
    private const int FeBackWidth = 128;
    private const int FeBackHeight = 128;
    private const int FeBackFps = 15;
    private const int FeBackFrameBytes = FeBackWidth * FeBackHeight * 3;
    // Fallback only when the strip is missing (materialize not run).
    private static readonly Color MainUnderlayFallback = new(23f / 255f, 23f / 255f, 48f / 255f, 1f);

    private readonly RetailFrontendSession _session = new();
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];

    private Texture2D _clickBackground = null!;
    private Texture2D _clickSlide = null!;
    private Texture2D _rockBackground = null!;
    private Texture2D[] _feBackFrames = [];
    private Texture2D _forsetiWritingLarge = null!;
    private Texture2D _reflectionMap = null!;
    private Texture2D _titleLogo = null!;
    private Texture2D _titleBracket01 = null!;
    private Texture2D _titleBracket02 = null!;
    private Texture2D _titleTextBox = null!;
    private Texture2D _symbolBracket01 = null!;
    private Texture2D _symbolBracket02 = null!;
    private Texture2D _levelBracket01 = null!;
    private Texture2D _levelBracket02 = null!;
    private Texture2D _levelRing01 = null!;
    private Texture2D _levelRing02 = null!;
    private Texture2D _loadingScreen = null!;
    private Texture2D _titleFont = null!;
    private Texture2D[] _menuIcons = [];
    private int[] _glyphWidths = [];
    private CanvasItemMaterial? _additiveMaterial;
    private string _selectLevelText = string.Empty;
    private string _level100Text = string.Empty;
    private string _loadingText = string.Empty;
    // Localization__GetStringById(0xe4) — English table in BEA.exe, not english.dat.
    private const string QuitConfirmPrompt = "Are you sure you want to quit the game?";
    private double _animationSeconds;
    private double _clickPulseTimer;
    private double _clickPageSeconds;
    private RetailFrontendScreen _lastDrawnScreen = RetailFrontendScreen.ClickToStart;
    private int _loadingFrames;
    private bool _initialized;
    private bool _loadRequestRaised;
    private bool _level100Ready;
    private bool _gameplayActivationRaised;

    public event Action? Level100LoadRequested;

    public event Action? GameplayActivated;

    public event Action? GameplaySuspended;

    public event Action? ReturnToMainMenuRequested;

    public event Action<RetailFrontendAudioCue>? AudioCueRequested;

    public event Action<RetailFrontendCursorMode>? CursorModeRequested;

    internal RetailFrontendScreen CurrentScreen => _session.Screen;

    public void Initialize()
    {
        if (_initialized)
        {
            throw new InvalidOperationException("The retail frontend is already initialized.");
        }

        LoadLocalization();
        LoadTextures();
        _feBackFrames = LoadFeBackFrames();
        _glyphWidths = MeasureGlyphWidths(_titleFont.GetImage());

        _initialized = true;
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

    internal void ConfirmForSmoke()
    {
        Confirm();
    }

    public override void _Ready()
    {
        if (!_initialized)
        {
            throw new InvalidOperationException("Initialize the retail frontend before adding it to the tree.");
        }

        AnchorRight = 1f;
        AnchorBottom = 1f;
        MouseFilter = MouseFilterEnum.Ignore;
        ZIndex = 100;
        QueueRedraw();
    }

    public override void _Process(double delta)
    {
        double step = Math.Max(0d, delta);
        _animationSeconds += step;
        if (_session.Screen == RetailFrontendScreen.ClickToStart)
        {
            if (_lastDrawnScreen != RetailFrontendScreen.ClickToStart)
            {
                _clickPulseTimer = 0d;
                _clickPageSeconds = 0d;
            }

            // Retail Process accumulates roughly 2 * frameΔ into this+0x18.
            _clickPulseTimer += 2d * step;
            _clickPageSeconds += step;
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
                _session.CompleteLevel100Load();
            }
        }

        if (_session.Screen == RetailFrontendScreen.Gameplay && !_gameplayActivationRaised)
        {
            _gameplayActivationRaised = true;
            Visible = false;
            SetProcessInput(false);
            SetProcess(false);
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Captured);
            GameplayActivated?.Invoke();
            return;
        }

        QueueRedraw();
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_session.Screen is RetailFrontendScreen.Loading or RetailFrontendScreen.Gameplay)
        {
            return;
        }

        bool handled = inputEvent switch
        {
            InputEventMouseMotion motion => HandlePointerMotion(motion.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Left =>
                HandlePointerConfirm(button.Position),
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
        // Letterbox outside the 640-class stage; no invented navy FE clear.
        DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);
        (float scale, Vector2 offset) = DesignTransform();
        DrawSetTransform(offset, 0f, new Vector2(scale, scale));

        switch (_session.Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                DrawClickToStart();
                break;
            case RetailFrontendScreen.MainMenu:
                DrawMainMenu();
                break;
            case RetailFrontendScreen.QuitConfirm:
                DrawMainMenu();
                DrawQuitConfirm();
                break;
            case RetailFrontendScreen.LevelSelect:
                DrawLevelSelect();
                break;
            case RetailFrontendScreen.Loading:
                DrawLoading();
                break;
        }

        DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
    }

    private void DrawClickToStart()
    {
        // FUN_0051b840 splash pulse — DAT_0089d880 / fe_splash1.
        float t = Mathf.Min((float)_clickPulseTimer, 1f);
        float splashScale = ((Mathf.Cos(t * Mathf.Pi) + 1f) * 0.375f) + 0.46875f;
        // Call-site x/y are center anchors at settled scale ≈ (320, 240).
        float splashX = (558f - (splashScale * 238f)) - 126.4375f;
        float splashY = 135.9375f + (222f * splashScale);
        DrawSurfaceCentered(
            _clickBackground,
            splashX,
            splashY,
            splashScale,
            splashScale,
            Colors.White);

        // Prompt after timer > 4. Blink duty cycle is stubbed (retail FPU thunk WAIT).
        if (_clickPulseTimer > 4d && (Mathf.PosMod((float)_clickPulseTimer, 2f) < 1.6f))
        {
            const string prompt = "CLICK TO START"; // Localization 0x77; TitleFont is uppercase atlas
            const float textScale = 1f;
            float width = MeasureText(prompt, textScale);
            var origin = new Vector2(320f - (width * 0.5f), 400f);
            // Retail: four ±1 black outline passes + white body (no extra drop-shadow).
            DrawTextFlat(prompt, origin + new Vector2(-1f, 1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(1f, 1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(-1f, -1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(1f, -1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin, textScale, Colors.White);
        }

        // DAT_0089d7bc LostToys sliding pair after prompt gate.
        if (_clickPulseTimer > 4d)
        {
            float fade = Mathf.Clamp((float)_clickPulseTimer - 4f, 0f, 1f);
            float off = (1f - fade) * (1f - fade) * 400f;
            // Call sites use mode 0 (top-left style) at these XY with sx=sy=1.
            DrawTextureRect(
                _clickSlide,
                new Rect2(124f - off, -6f, _clickSlide.GetWidth(), _clickSlide.GetHeight()),
                false,
                ClickSlideShadow);
            DrawTextureRect(
                _clickSlide,
                new Rect2(120f - off, -10f, _clickSlide.GetWidth(), _clickSlide.GetHeight()),
                false,
                Colors.White);
        }

        // Title micro-pulse near (250,290) after ~2s (simplified vs multi-pass retail).
        if (_clickPageSeconds * 1.2d > 2d)
        {
            float logoPulse = 0.55f + (0.45f * (0.5f + (0.5f * Mathf.Sin((float)_clickPageSeconds * 3f))));
            DrawSurfaceCentered(
                _titleLogo,
                250f,
                290f,
                0.35f,
                0.35f,
                new Color(TitleLogoTint.R, TitleLogoTint.G, TitleLogoTint.B, logoPulse));
        }
    }

    private void DrawMainMenu()
    {
        DrawMainUnderlay();

        // DAT_0089d7f0 Forseti writing chrome — three settled tiles (Y thunk ≈ 175).
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f, 1f, 1f, ChromeTint);
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f + 350f, 1f, 1f, ChromeTint);
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f + 700f, 1f, 1f, ChromeTint);

        for (int index = 0; index < _session.Items.Count; index++)
        {
            RetailFrontendMenuItem item = _session.Items[index];
            float rowY = MenuStartY + (index * MenuPitch);
            bool selected = index == _session.SelectedMainIndex;
            // TitleFont atlas is A–Z / digit rows; english.dat mixed case → uppercase for draw.
            // 32px cells need ~0.5 scale to fit the retail 20px menu pitch.
            string label = _menuText[item.Kind].ToUpperInvariant();
            const float textScale = 0.5f;
            float textWidth = MeasureText(label, textScale);
            var textPos = new Vector2(MenuColumnX - (textWidth * 0.5f), rowY - 8f);

            if (selected)
            {
                // Highlight sx/Y still WEAKEN vs retail; geometry is reconstruction stub.
                float boxWidth = Mathf.Max(160f, textWidth + 24f);
                DrawTextureRect(
                    _titleTextBox,
                    new Rect2(MenuColumnX - (boxWidth * 0.5f), rowY - 10f, boxWidth, 20f),
                    false,
                    HighlightTint);
            }

            Color textColor = selected
                ? ReleasedSelected
                : item.IsAvailable ? ReleasedNormal : ReleasedUnavailable;
            DrawText(label, textPos, textScale, textColor);
        }

        // Shadows (offset bases; GetShadowOffset* ≈ 0 settled), then bodies.
        const float bracketScale = 1.25f;
        float bracketShadowScale = bracketScale * ShadowScaleBoost;
        DrawSurfaceCentered(_titleBracket01, 224f, 349f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_titleBracket01, 219f, 344f, bracketScale, bracketScale, BracketTint);
        DrawSurfaceCentered(_symbolBracket01, 462f, 365f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_symbolBracket01, 457f, 355f, bracketScale, bracketScale, BracketTint);

        Texture2D icon = _menuIcons[_session.SelectedMainIndex];
        Color iconTint = _session.SelectedMainItem.IsAvailable ? BracketTint : ReleasedUnavailable;
        DrawSurfaceCentered(icon, 462f, 365f, ShadowScaleBoost, ShadowScaleBoost, ShadowTint);
        DrawSurfaceCentered(icon, 457f, 355f, 1f, 1f, iconTint);

        DrawTextFlat(VersionText, new Vector2(0f, DesignHeight - 16f), 0.5f, VersionTint);

        // DAT_0089d7fc reflection streaks — retail additive over the stage.
        // Draw before the logo so a failed additive fallback cannot bury Title2.
        // x ≈ (256 - FpuThunk()) + 65 with thunk≈0.
        const float glowX0 = 256f + 65f;
        DrawAdditiveSurfaceCentered(_reflectionMap, glowX0, 120f, 1f, 2f, GlowTint);
        DrawAdditiveSurfaceCentered(_reflectionMap, glowX0 + 512f, 120f, 1f, 2f, GlowTint);

        DrawSurfaceCentered(_titleLogo, 325f, 140f, ShadowScaleBoost, ShadowScaleBoost, ShadowTint);
        DrawSurfaceCentered(_titleLogo, 320f, 130f, 1f, 1f, TitleLogoTint);
    }

    private void DrawMainUnderlay()
    {
        // CFEPMain → CDXFrontEndVideo__Render on FEBack128.vid; stretch 128² → stage.
        if (_feBackFrames.Length == 0)
        {
            DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), MainUnderlayFallback);
            return;
        }

        int index = (int)(_animationSeconds * FeBackFps) % _feBackFrames.Length;
        DrawTextureRect(
            _feBackFrames[index],
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false,
            Colors.White);
    }

    private void DrawQuitConfirm()
    {
        // Reconstruction messbox chrome (Steam FEMessBox layout not fully ported).
        DrawRect(new Rect2(70f, 160f, 500f, 140f), new Color(0f, 0f, 0f, 0.82f));
        DrawTextCentered(QuitConfirmPrompt, new Vector2(320f, 190f), 0.85f, Colors.White);

        DrawQuitConfirmChoice("No", 220f, _session.SelectedQuitConfirmIndex == 0);
        DrawQuitConfirmChoice("Yes", 420f, _session.SelectedQuitConfirmIndex == 1);
    }

    private void DrawQuitConfirmChoice(string label, float centerX, bool selected)
    {
        Color color = selected ? ReleasedSelected : ReleasedNormal;
        if (selected)
        {
            float width = Mathf.Max(72f, MeasureText(label, 1f) + 20f);
            DrawTextureRect(
                _titleTextBox,
                new Rect2(centerX - (width * 0.5f), 248f, width, 20f),
                false,
                HighlightTint);
        }

        DrawTextCentered(label, new Vector2(centerX, 250f), 1f, color);
    }

    private void DrawLevelSelect()
    {
        // Out-of-lane chrome kept functional on the 640 stage; not parity-claimed.
        DrawTextureRect(
            _rockBackground,
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false);
        DrawSurfaceCentered(_titleLogo, 160f, 70f, 0.55f, 0.55f, TitleLogoTint);
        DrawTextCentered(_selectLevelText, new Vector2(320f, 48f), 1.2f, ReleasedSelected);

        Vector2 center = new(320f, 240f);
        float rotation = (float)_animationSeconds * 0.16f;
        DrawCenteredRotated(
            _levelBracket01,
            center,
            new Vector2(280f, 280f),
            rotation,
            new Color(0.48f, 0.68f, 0.9f, 0.84f));
        DrawCenteredRotated(
            _levelBracket02,
            center,
            new Vector2(280f, 280f),
            -rotation * 0.66f,
            new Color(1f, 0.42f, 0.22f, 0.8f));
        DrawCenteredRotated(
            _levelRing01,
            center,
            new Vector2(80f, 80f),
            -rotation * 1.8f,
            new Color(0.5f, 0.72f, 1f, 1f));
        DrawCenteredRotated(
            _levelRing02,
            center,
            new Vector2(80f, 80f),
            rotation * 1.4f,
            ReleasedSelected);

        DrawRect(
            new Rect2(140f, 390f, 360f, 60f),
            new Color(0.015f, 0.035f, 0.09f, 0.82f));
        DrawLine(new Vector2(140f, 390f), new Vector2(500f, 390f), ReleasedSelected, 2f);
        DrawTextCentered(_level100Text, new Vector2(320f, 408f), 1.1f, Colors.White);
    }

    private void DrawLoading()
    {
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), Colors.Black);
        DrawTextureRect(
            _loadingScreen,
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false);
        DrawRect(new Rect2(0f, 420f, DesignWidth, 60f), new Color(0f, 0f, 0f, 0.58f));
        DrawText(_loadingText, new Vector2(24f, 436f), 1f, Colors.White);
    }

    private bool HandlePointerMotion(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
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
                Confirm();
                return true;

            case RetailFrontendScreen.MainMenu:
                int index = MainMenuIndexAt(design);
                if (index < 0 || !_session.Items[index].IsAvailable)
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

            case RetailFrontendScreen.LevelSelect:
                if (new Rect2(80f, 80f, 480f, 360f).HasPoint(design))
                {
                    Confirm();
                    return true;
                }
                return false;

            default:
                return false;
        }
    }

    private bool HandleKey(InputEventKey key)
    {
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
            Confirm();
            return true;
        }
        if (IsKey(key, Key.Escape))
        {
            RetailFrontendSignal signal = _session.Back();
            if (signal != RetailFrontendSignal.None)
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
        RetailFrontendSignal signal = _session.Confirm();
        if (signal == RetailFrontendSignal.None)
        {
            return;
        }

        RequestAudioCue(RetailFrontendAudioCue.Select);
        HandleNavigationSignal(signal);
        if (signal == RetailFrontendSignal.ExitRequested)
        {
            GetTree().Quit(0);
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
    }

    private void HandleNavigationSignal(RetailFrontendSignal signal)
    {
        if (signal == RetailFrontendSignal.Level100LaunchRequested)
        {
            _loadRequestRaised = false;
            _level100Ready = false;
            _gameplayActivationRaised = false;
            _loadingFrames = 0;
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Hidden);
        }
        else if (signal == RetailFrontendSignal.ReturnToMainMenuRequested)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Visible);
            ReturnToMainMenuRequested?.Invoke();
        }
        else if (signal == RetailFrontendSignal.PageChanged)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Visible);
        }
    }

    private int MainMenuIndexAt(Vector2 designPosition)
    {
        var menuRect = new Rect2(
            MenuColumnX - MenuHitHalfWidth,
            MenuStartY - (MenuPitch * 0.5f),
            MenuHitHalfWidth * 2f,
            MenuPitch * _session.Items.Count);
        if (!menuRect.HasPoint(designPosition))
        {
            return -1;
        }

        int index = (int)((designPosition.Y - MenuStartY + (MenuPitch * 0.5f)) / MenuPitch);
        return Math.Clamp(index, 0, _session.Items.Count - 1);
    }

    private static int QuitConfirmIndexAt(Vector2 designPosition)
    {
        if (new Rect2(160f, 240f, 120f, 36f).HasPoint(designPosition))
        {
            return 0;
        }

        if (new Rect2(360f, 240f, 120f, 36f).HasPoint(designPosition))
        {
            return 1;
        }

        return -1;
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
        _level100Text = RequiredString(strings, "level100");
        _loadingText = RequiredString(strings, "loading");
    }

    private void LoadTextures()
    {
        _clickBackground = LoadTexture(
            "Backgrounds/click-to-start",
            1024,
            1024,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _rockBackground = LoadTexture(
            "Backgrounds/rock",
            1024,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _clickSlide = LoadTexture("click-slide", 128, 128);
        _forsetiWritingLarge = LoadTexture("forseti-writing-large", 128, 512);
        _reflectionMap = LoadTexture(
            "reflection-map",
            512,
            128,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _titleLogo = LoadTexture("title-logo", 512, 256);
        _titleBracket01 = LoadTexture("title-bracket-01", 256, 256);
        _titleBracket02 = LoadTexture("title-bracket-02", 256, 256);
        _titleTextBox = LoadTexture("title-text-box", 256, 32);
        _symbolBracket01 = LoadTexture("symbol-bracket-01", 128, 128);
        _symbolBracket02 = LoadTexture("symbol-bracket-02", 128, 128);
        _levelBracket01 = LoadTexture("level-bracket-01", 512, 512);
        _levelBracket02 = LoadTexture("level-bracket-02", 512, 512);
        _levelRing01 = LoadTexture("level-ring-01", 64, 64);
        _levelRing02 = LoadTexture("level-ring-02", 64, 64);
        _loadingScreen = LoadTexture(
            "loading-screen",
            512,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _titleFont = LoadTexture(
            "title-font",
            256,
            256,
            CuratedAyaTextureLoader.Compression.Rgba8);
        // Must match RetailFrontendSession Steam-drawn row order (Update/icons).
        _menuIcons =
        [
            LoadTexture("Icons/new-game", 128, 128),
            LoadTexture("Icons/continue-game", 128, 128),
            LoadTexture("Icons/load-game", 128, 128),
            LoadTexture("Icons/multiplayer", 128, 128),
            LoadTexture("Icons/goodies", 128, 128),
            LoadTexture("Icons/options", 128, 128),
            LoadTexture("Icons/quit", 128, 128),
        ];
    }

    private static Texture2D[] LoadFeBackFrames()
    {
        string absolute = ProjectSettings.GlobalizePath(FeBackStripPath);
        if (!File.Exists(absolute))
        {
            GD.PushWarning(
                $"FEBack strip missing at {FeBackStripPath}; main underlay uses solid fallback.");
            return [];
        }

        byte[] strip = File.ReadAllBytes(absolute);
        if (strip.Length == 0 || strip.Length % FeBackFrameBytes != 0)
        {
            throw new InvalidDataException(
                $"FEBack strip length {strip.Length} is not a multiple of {FeBackFrameBytes}.");
        }

        int frameCount = strip.Length / FeBackFrameBytes;
        var frames = new Texture2D[frameCount];
        for (int index = 0; index < frameCount; index++)
        {
            byte[] frame = new byte[FeBackFrameBytes];
            Buffer.BlockCopy(strip, index * FeBackFrameBytes, frame, 0, FeBackFrameBytes);
            Image image = Image.CreateFromData(
                FeBackWidth,
                FeBackHeight,
                false,
                Image.Format.Rgb8,
                frame);
            frames[index] = ImageTexture.CreateFromImage(image);
        }

        return frames;
    }

    private static Texture2D LoadTexture(
        string name,
        int width,
        int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2) =>
        CuratedAyaTextureLoader.Load(
            $"res://Assets/Frontend/{name}.texture.aya",
            width,
            height,
            compression);

    private void DrawSurfaceCentered(
        Texture2D texture,
        float centerX,
        float centerY,
        float widthScale,
        float heightScale,
        Color modulate)
    {
        float width = texture.GetWidth() * widthScale;
        float height = texture.GetHeight() * heightScale;
        DrawTextureRect(
            texture,
            new Rect2(centerX - (width * 0.5f), centerY - (height * 0.5f), width, height),
            false,
            modulate);
    }

    private void DrawAdditiveSurfaceCentered(
        Texture2D texture,
        float centerX,
        float centerY,
        float widthScale,
        float heightScale,
        Color modulate)
    {
        _additiveMaterial ??= new CanvasItemMaterial
        {
            BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
        };
        Material = _additiveMaterial;
        DrawSurfaceCentered(texture, centerX, centerY, widthScale, heightScale, modulate);
        Material = null;
    }

    private void DrawCenteredRotated(
        Texture2D texture,
        Vector2 center,
        Vector2 size,
        float rotation,
        Color modulate)
    {
        // CONSENSUS_C: single window↔stage map. DrawSetTransform replaces (does not nest);
        // re-apply letterbox around the design-space pivot, then restore design space.
        (float scale, Vector2 offset) = DesignTransform();
        DrawSetTransform(
            offset + (center * scale),
            rotation,
            new Vector2(scale, scale));
        DrawTextureRect(texture, new Rect2(-size * 0.5f, size), false, modulate);
        DrawSetTransform(offset, 0f, new Vector2(scale, scale));
    }

    private void DrawTextCentered(string text, Vector2 center, float scale, Color color)
    {
        float width = MeasureText(text, scale);
        DrawText(text, new Vector2(center.X - (width * 0.5f), center.Y), scale, color);
    }

    private void DrawText(string text, Vector2 position, float scale, Color color) =>
        DrawTextCore(text, position, scale, color, dropShadow: true);

    private void DrawTextFlat(string text, Vector2 position, float scale, Color color) =>
        DrawTextCore(text, position, scale, color, dropShadow: false);

    private void DrawTextCore(string text, Vector2 position, float scale, Color color, bool dropShadow)
    {
        float x = position.X;
        foreach (char character in text)
        {
            int glyph = GlyphIndex(character);
            float glyphWidth = _glyphWidths[glyph] * scale;
            var source = new Rect2(
                (glyph % GlyphColumns) * GlyphCellSize,
                (glyph / GlyphColumns) * GlyphCellSize,
                _glyphWidths[glyph],
                GlyphCellSize);
            var destination = new Rect2(x, position.Y, glyphWidth, GlyphCellSize * scale);
            if (dropShadow)
            {
                DrawTextureRectRegion(
                    _titleFont,
                    new Rect2(destination.Position + new Vector2(2f, 2f), destination.Size),
                    source,
                    new Color(0f, 0f, 0f, color.A * 0.82f));
            }

            DrawTextureRectRegion(_titleFont, destination, source, color);
            x += glyphWidth + scale;
        }
    }

    private float MeasureText(string text, float scale)
    {
        float width = 0f;
        foreach (char character in text)
        {
            width += (_glyphWidths[GlyphIndex(character)] + 1) * scale;
        }
        return Mathf.Max(0f, width - scale);
    }

    private static int GlyphIndex(char character)
    {
        int code = character;
        if (code is >= 'a' and <= 'z')
        {
            code -= 32;
        }

        if (code is < FirstGlyph or >= FirstGlyph + GlyphSlotCount)
        {
            code = '?';
        }

        return code - FirstGlyph;
    }

    private static int[] MeasureGlyphWidths(Image image)
    {
        var widths = new int[GlyphSlotCount];
        widths[0] = 8;
        int scanMax = GlyphCellSize - 2;
        for (int glyph = 1; glyph < widths.Length; glyph++)
        {
            int cellX = (glyph % GlyphColumns) * GlyphCellSize;
            int cellY = (glyph / GlyphColumns) * GlyphCellSize;
            int rightmost = cellX;
            for (int x = cellX + scanMax; x >= cellX; x--)
            {
                bool occupied = false;
                for (int y = cellY; y < cellY + GlyphCellSize - 1; y++)
                {
                    if (image.GetPixel(x, y).A > (16f / 255f))
                    {
                        occupied = true;
                        break;
                    }
                }
                if (occupied)
                {
                    rightmost = x;
                    break;
                }
            }
            widths[glyph] = (rightmost - cellX) + 2;
        }
        return widths;
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

    private void RequestAudioCue(RetailFrontendAudioCue cue) =>
        AudioCueRequested?.Invoke(cue);

    private static Color RetailColor(uint argb) => new(
        ((argb >> 16) & 0xff) / 255f,
        ((argb >> 8) & 0xff) / 255f,
        (argb & 0xff) / 255f,
        ((argb >> 24) & 0xff) / 255f);
}
