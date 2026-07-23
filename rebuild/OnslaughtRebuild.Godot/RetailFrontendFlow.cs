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
public sealed partial class RetailFrontendFlow : Control
{
    private const float DesignWidth = 1280f;
    private const float DesignHeight = 720f;
    private const float MainMenuLeft = 735f;
    private const float MainMenuTop = 242f;
    private const float MainMenuWidth = 430f;
    private const float MainMenuRowHeight = 48f;
    private const int GlyphColumns = 16;
    private const int GlyphCellSize = 16;
    private const int FirstGlyph = 32;

    private static readonly Color ReleasedNormal = RetailColor(0xff4f4f4f);
    private static readonly Color ReleasedUnavailable = RetailColor(0x7f1f1f1f);
    private static readonly Color ReleasedSelected = RetailColor(0xffff6f3f);
    private static readonly Color ReleasedBlue = RetailColor(0xff1f4f7f);
    private static readonly Color DeepNavy = RetailColor(0xff0f0f2f);

    private readonly RetailFrontendSession _session = new();
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];

    private Texture2D _clickBackground = null!;
    private Texture2D _rockBackground = null!;
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
    private string _selectLevelText = string.Empty;
    private string _level100Text = string.Empty;
    private string _loadingText = string.Empty;
    private double _animationSeconds;
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

    public bool TryAcceptMissionTerminal(Level100MissionSnapshot mission)
    {
        if (!_session.TryAcceptMissionTerminal(mission))
        {
            return false;
        }

        PresentTerminalHandoff();
        return true;
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
        _animationSeconds += Math.Max(0d, delta);

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
        if (_session.Screen is RetailFrontendScreen.Loading or RetailFrontendScreen.Gameplay or
            RetailFrontendScreen.TerminalHandoff)
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
        DrawRect(new Rect2(Vector2.Zero, Size), DeepNavy);
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
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), DeepNavy);
        DrawTextureRect(
            _clickBackground,
            new Rect2(0f, 0f, DesignHeight, DesignHeight),
            false);
        DrawRect(
            new Rect2(480f, 0f, 800f, DesignHeight),
            new Color(0.01f, 0.025f, 0.08f, 0.72f));
        DrawRect(
            new Rect2(690f, 84f, 530f, 280f),
            new Color(0f, 0f, 0f, 0.16f));
        DrawTextureRect(_titleLogo, new Rect2(700f, 88f, 512f, 256f), false);

        float pulse = 0.72f + (Mathf.Sin((float)_animationSeconds * 2.8f) * 0.28f);
        DrawTextCentered(
            // Ghidra: Localization__GetStringById(0x77), embedded Steam text.
            "Click to start",
            new Vector2(960f, 535f),
            2.05f,
            new Color(1f, 0.44f, 0.25f, pulse));
        DrawLine(new Vector2(748f, 620f), new Vector2(1172f, 620f), ReleasedBlue, 2f);
    }

    private void DrawMainMenu()
    {
        DrawRockBackground();
        DrawTextureRect(_titleLogo, new Rect2(674f, 18f, 486f, 243f), false);

        Vector2 symbolCenter = new(350f, 414f);
        float rotation = (float)_animationSeconds * 0.20f;
        DrawCenteredRotated(
            _titleBracket01,
            symbolCenter,
            new Vector2(360f, 360f),
            rotation,
            new Color(0.68f, 0.82f, 1f, 0.72f));
        DrawCenteredRotated(
            _titleBracket02,
            symbolCenter,
            new Vector2(360f, 360f),
            -rotation * 0.72f,
            new Color(1f, 0.42f, 0.22f, 0.74f));
        DrawCenteredRotated(
            _symbolBracket01,
            symbolCenter,
            new Vector2(206f, 206f),
            -rotation * 1.4f,
            new Color(0.64f, 0.8f, 1f, 0.85f));
        DrawCenteredRotated(
            _symbolBracket02,
            symbolCenter,
            new Vector2(206f, 206f),
            rotation * 1.1f,
            new Color(1f, 0.43f, 0.23f, 0.86f));
        DrawTextureRect(
            _menuIcons[_session.SelectedMainIndex],
            new Rect2(symbolCenter - new Vector2(75f, 75f), new Vector2(150f, 150f)),
            false,
            _session.SelectedMainItem.IsAvailable
                ? Colors.White
                : new Color(0.58f, 0.62f, 0.67f, 0.66f));

        for (int index = 0; index < _session.Items.Count; index++)
        {
            RetailFrontendMenuItem item = _session.Items[index];
            float y = MainMenuTop + (index * MainMenuRowHeight);
            bool selected = index == _session.SelectedMainIndex;
            if (selected)
            {
                DrawTextureRect(
                    _titleTextBox,
                    new Rect2(MainMenuLeft - 20f, y - 8f, MainMenuWidth, 44f),
                    false,
                    item.IsAvailable
                        ? new Color(1f, 1f, 1f, 0.82f)
                        : new Color(0.55f, 0.55f, 0.55f, 0.58f));
            }

            Color textColor = selected
                ? ReleasedSelected
                : item.IsAvailable ? ReleasedNormal : ReleasedUnavailable;
            DrawText(_menuText[item.Kind], new Vector2(MainMenuLeft, y), 1.45f, textColor);
        }
    }

    private void DrawLevelSelect()
    {
        DrawRockBackground();
        DrawTextureRect(_titleLogo, new Rect2(38f, 12f, 384f, 192f), false);
        DrawTextCentered(_selectLevelText, new Vector2(640f, 82f), 2.1f, ReleasedSelected);
        DrawLine(new Vector2(424f, 126f), new Vector2(856f, 126f), ReleasedBlue, 2f);

        Vector2 center = new(640f, 374f);
        float rotation = (float)_animationSeconds * 0.16f;
        DrawCenteredRotated(
            _levelBracket01,
            center,
            new Vector2(510f, 510f),
            rotation,
            new Color(0.48f, 0.68f, 0.9f, 0.84f));
        DrawCenteredRotated(
            _levelBracket02,
            center,
            new Vector2(510f, 510f),
            -rotation * 0.66f,
            new Color(1f, 0.42f, 0.22f, 0.8f));
        DrawCenteredRotated(
            _levelRing01,
            center,
            new Vector2(150f, 150f),
            -rotation * 1.8f,
            new Color(0.5f, 0.72f, 1f, 1f));
        DrawCenteredRotated(
            _levelRing02,
            center,
            new Vector2(150f, 150f),
            rotation * 1.4f,
            ReleasedSelected);

        DrawRect(
            new Rect2(365f, 548f, 550f, 100f),
            new Color(0.015f, 0.035f, 0.09f, 0.82f));
        DrawLine(new Vector2(365f, 548f), new Vector2(915f, 548f), ReleasedSelected, 2f);
        DrawTextCentered(_level100Text, new Vector2(640f, 568f), 1.45f, Colors.White);
    }

    private void DrawLoading()
    {
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), Colors.Black);
        // The released renderer scales this exact square image to the active window.
        DrawTextureRect(
            _loadingScreen,
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false);
        DrawRect(new Rect2(0f, 620f, DesignWidth, 100f), new Color(0f, 0f, 0f, 0.58f));
        DrawText(_loadingText, new Vector2(54f, 642f), 1.3f, Colors.White);
    }

    private void DrawRockBackground()
    {
        const float scaledWidth = 1440f;
        DrawTextureRect(
            _rockBackground,
            new Rect2((DesignWidth - scaledWidth) * 0.5f, 0f, scaledWidth, DesignHeight),
            false);
        DrawRect(
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            new Color(0.005f, 0.02f, 0.08f, 0.48f));
        DrawLine(new Vector2(24f, 24f), new Vector2(1256f, 24f), ReleasedBlue, 2f);
        DrawLine(new Vector2(24f, 696f), new Vector2(1256f, 696f), ReleasedBlue, 2f);
    }

    private bool HandlePointerMotion(Vector2 position)
    {
        if (_session.Screen != RetailFrontendScreen.MainMenu)
        {
            return false;
        }

        int index = MainMenuIndexAt(ToDesignPosition(position));
        if (index < 0 || !_session.SelectMainIndex(index))
        {
            return false;
        }

        RequestAudioCue(RetailFrontendAudioCue.Move);
        QueueRedraw();
        return true;
    }

    private bool HandlePointerConfirm(Vector2 position)
    {
        switch (_session.Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                Confirm();
                return true;

            case RetailFrontendScreen.MainMenu:
                int index = MainMenuIndexAt(ToDesignPosition(position));
                if (index < 0)
                {
                    return false;
                }
                if (_session.SelectMainIndex(index))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                }
                Confirm();
                return true;

            case RetailFrontendScreen.LevelSelect:
                if (new Rect2(330f, 126f, 620f, 558f).HasPoint(ToDesignPosition(position)))
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
        if (IsKey(key, Key.Up))
        {
            if (_session.MovePrevious())
            {
                RequestAudioCue(RetailFrontendAudioCue.Move);
                QueueRedraw();
            }
            return true;
        }
        if (IsKey(key, Key.Down))
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

    private void PresentTerminalHandoff()
    {
        // The mission/HUD owner renders the released in-game terminal overlay.
        // This frontend only retains the later lifecycle handoff.
        Visible = false;
        SetProcessInput(false);
        SetProcess(false);
        CursorModeRequested?.Invoke(RetailFrontendCursorMode.Visible);
        GameplaySuspended?.Invoke();
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
            MainMenuLeft - 24f,
            MainMenuTop - 10f,
            MainMenuWidth,
            MainMenuRowHeight * _session.Items.Count);
        if (!menuRect.HasPoint(designPosition))
        {
            return -1;
        }

        int index = (int)((designPosition.Y - MainMenuTop + 10f) / MainMenuRowHeight);
        return Math.Clamp(index, 0, _session.Items.Count - 1);
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

    private void DrawCenteredRotated(
        Texture2D texture,
        Vector2 center,
        Vector2 size,
        float rotation,
        Color modulate)
    {
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

    private void DrawText(string text, Vector2 position, float scale, Color color)
    {
        float x = position.X;
        foreach (char character in text)
        {
            int code = character;
            if (code is < FirstGlyph or >= FirstGlyph + 96)
            {
                code = '?';
            }

            int glyph = code - FirstGlyph;
            float glyphWidth = _glyphWidths[glyph] * scale;
            var source = new Rect2(
                (glyph % GlyphColumns) * GlyphCellSize,
                (glyph / GlyphColumns) * GlyphCellSize,
                _glyphWidths[glyph],
                GlyphCellSize);
            var destination = new Rect2(x, position.Y, glyphWidth, GlyphCellSize * scale);
            DrawTextureRectRegion(
                _titleFont,
                new Rect2(destination.Position + new Vector2(2f, 2f), destination.Size),
                source,
                new Color(0f, 0f, 0f, color.A * 0.82f));
            DrawTextureRectRegion(_titleFont, destination, source, color);
            x += glyphWidth + scale;
        }
    }

    private float MeasureText(string text, float scale)
    {
        float width = 0f;
        foreach (char character in text)
        {
            int code = character;
            if (code is < FirstGlyph or >= FirstGlyph + 96)
            {
                code = '?';
            }
            width += (_glyphWidths[code - FirstGlyph] + 1) * scale;
        }
        return Mathf.Max(0f, width - scale);
    }

    private static int[] MeasureGlyphWidths(Image image)
    {
        var widths = new int[96];
        widths[0] = 8;
        for (int glyph = 1; glyph < widths.Length; glyph++)
        {
            int cellX = (glyph % GlyphColumns) * GlyphCellSize;
            int cellY = (glyph / GlyphColumns) * GlyphCellSize;
            int rightmost = cellX;
            for (int x = cellX + 14; x >= cellX; x--)
            {
                bool occupied = false;
                for (int y = cellY; y < cellY + 15; y++)
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
