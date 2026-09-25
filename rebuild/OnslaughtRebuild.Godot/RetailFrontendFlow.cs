// SPDX-License-Identifier: GPL-3.0-or-later

using System.Runtime.ExceptionServices;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary managed host boundary for the native Frontend.tscn Control. The
/// native scene owns its Session, input, clocks, page resources and handoffs.
/// This facade marshals coarse commands and synchronous effects, retains the
/// verified career object identities, and caches detached host-facing facts.
/// It borrows View; the scene tree remains responsible for the Control's life.
/// </summary>
public sealed partial class RetailFrontendFlow : IDisposable
{
    private sealed class CallScope
    {
        internal readonly HashSet<long> FailureIds = [];
    }

    private readonly Callable _hostStateChanged;
    private readonly Callable _effectHandler;
    private readonly Callable _voiceObserver;
    private readonly Stack<CallScope> _calls = new();
    private readonly Dictionary<long, ExceptionDispatchInfo> _callbackFailures = [];
    private long _failureSequence;
    private bool _disposed;
    private RetailCareerDescriptor[] _originalDescriptors = [];
    private RetailFrontendScreen _screen;
    private int _launchWorldNumber;
    private bool _selectedWorldIsConstructible;
    private D _optionsSettings = new();

    public Control View { get; }
    internal AudioPlaybackRetirement PlaybackRetirement { get; set; } = null!;
    internal int NativeCallCount { get; private set; }
    internal int PendingCallbackFailureCount => _callbackFailures.Count;
    internal IReadOnlyList<RetailCareerDescriptor> OriginalDescriptors { get; private set; } = [];
    internal RetailFrontendScreen CurrentScreen { get { RequireAlive(); return _screen; } }
    internal int LaunchWorldNumber { get { RequireAlive(); return _launchWorldNumber; } }
    internal bool SelectedWorldIsConstructible { get { RequireAlive(); return _selectedWorldIsConstructible; } }
    internal RetailOptionsSettings OptionsSettings { get { RequireAlive(); return ReadOptionsSettings(_optionsSettings); } }
    internal Control OptionsView { get { RequireAlive(); return View.GetNode<Control>("Stage/Options"); } }

    public event Action? Level100LoadRequested;
    public event Action? Level100LoadingStarted;
    public event Action? GameplayActivated;
    public event Action? GameplaySuspended;
    public event Action? ReturnToMainMenuRequested;
    public event Action? ExitRequested;
    public event Action<RetailCareerDescriptor>? CareerSelected;
    public event Action<RetailFrontendAudioCue>? AudioCueRequested;
    public event Action<RetailFrontendCursorMode>? CursorModeRequested;
    public event Action<RetailOptionsSettings>? OptionsSettingsChanged;

    private RetailFrontendFlow(Control view)
    {
        ArgumentNullException.ThrowIfNull(view);
        View = view;
        RequireAlive();
        foreach (string method in new[] { "initialize", "host_snapshot", "set_effect_handler", "set_voice_observer" })
            if (!view.HasMethod(method)) throw new InvalidDataException("Missing native frontend method: " + method);
        if (!view.HasSignal("host_state_changed"))
            throw new InvalidDataException("The native frontend has no host-state signal.");
        _hostStateChanged = Callable.From<D>(ReceiveHostState);
        _effectHandler = Callable.From<D, D, D>(DispatchEffect);
        _voiceObserver = Callable.From<AudioStreamPlayer>(ObserveVoiceStart);
        try
        {
            if (view.Connect("host_state_changed", _hostStateChanged) != Error.Ok)
                throw new InvalidDataException("The native frontend host-state signal could not be connected.");
            using Variant effect = view.Call("set_effect_handler", _effectHandler);
            using Variant voice = view.Call("set_voice_observer", _voiceObserver);
            RefreshHostFacts();
        }
        catch
        {
            Dispose();
            throw;
        }
    }

    public void Initialize(IReadOnlyList<RetailCareerDescriptor> careerDescriptors)
    {
        RequireAlive();
        // The native guard is authoritative, including Attach after _Ready.
        // Preserve the original repeated-call refusal before null arguments.
        using Variant initialized = View.Get("_initialized");
        if (initialized.VariantType != Variant.Type.Bool)
            throw new InvalidDataException("The native frontend omitted its initialization state.");
        if (initialized.AsBool()) throw new InvalidOperationException("The retail frontend is already initialized.");
        ArgumentNullException.ThrowIfNull(careerDescriptors);

        RetailCareerDescriptor[] descriptors = careerDescriptors.ToArray();
        using var supplied = new A();
        foreach (RetailCareerDescriptor descriptor in descriptors)
        {
            // Deliberately dereference null records like the old Session
            // constructor. Names travel as raw UTF-16, including null names;
            // neither this bridge nor Godot String normalizes their units.
            using var row = new D();
            row["slot_number"] = descriptor.SlotNumber.HasValue ? descriptor.SlotNumber.Value : default(Variant);
            using Variant name = descriptor.Name is null ? default(Variant)
                : descriptor.Name.Select(character => (int)character).ToArray();
            row["name"] = name;
            if (descriptor.Career is null) row["career"] = default(Variant);
            else
            {
                using Variant worlds = descriptor.Career.SelectableWorldNumbers.ToArray();
                using var career = new D
                {
                    ["suggested_world_number"] = descriptor.Career.SuggestedWorldNumber,
                    ["selectable_world_numbers"] = worlds,
                };
                using Variant careerValue = career;
                row["career"] = careerValue;
            }
            using Variant rowValue = row;
            supplied.Add(rowValue);
        }
        _originalDescriptors = descriptors;
        OriginalDescriptors = Array.AsReadOnly(descriptors);
        using Variant batch = supplied;
        using D result = InvokeNative("initialize", batch);
    }

    public void MarkLevel100Ready() => Command("mark_level100_ready");
    public void RestartLevel100() => Command("restart_level100");
    public void LeaveLevel100ForMainMenu() => Command("leave_level100_for_main_menu");
    public void AcceptWonHandoff(Level100MissionOutcome outcome, Level100MissionTerminalState terminalState) =>
        Command("accept_won_handoff", (int)outcome, (int)terminalState);
    public void ReturnUnconstructibleLaunchToLevelSelect() => Command("return_unconstructible_launch_to_level_select");
    public void SuspendForStartupMedia() => Command("suspend_for_startup_media");
    public void ResumeAfterStartupMedia() => Command("resume_after_startup_media");
    internal void ConfirmForSmoke() => Command("confirm");
    internal void SelectMainIndexForCapture(int index) => Command("select_main_index", index);
    internal void SelectOptionsRowForCapture(int index) => Command("select_options_row", index);
    internal void ConfirmOptionsForCapture() => Command("confirm_options");
    internal void BackFromOptionsForCapture() => Command("back_from_options");
    internal bool CancelOptionsForCapture()
    {
        using D result = InvokeNative("cancel_options");
        return Boolean(result, "value");
    }
    internal void SetMouseCursorDesignPositionForCapture(Vector2? position) =>
        Command("set_mouse_cursor_design_position_for_capture", position.HasValue ? position.Value : default(Variant));

    private void Command(string method, params Variant[] arguments)
    {
        using D result = InvokeNative(method, arguments);
    }

    /// <summary>Returns the whole checked result; its caller owns the wrapper.</summary>
    internal D InvokeNative(string method, params Variant[] arguments)
    {
        RequireAlive();
        var scope = new CallScope();
        _calls.Push(scope);
        D? result = null;
        Exception? failure = null;
        try
        {
            NativeCallCount++;
            using Variant returned = View.Call(method, arguments);
            result = Dictionary(returned, method);
            if (result.TryGetValue("host_exception_id", out Variant token))
            {
                using (token)
                {
                    if (token.VariantType != Variant.Type.Int || !scope.FailureIds.Remove(token.AsInt64())
                        || !_callbackFailures.Remove(token.AsInt64(), out ExceptionDispatchInfo? dispatch))
                        throw new InvalidDataException("The native frontend returned an unknown callback failure token.");
                    dispatch.Throw();
                }
            }
            RequireResult(result);
            return result;
        }
        catch (Exception error)
        {
            failure = error;
            result?.Dispose();
            result = null;
            throw;
        }
        finally
        {
            try
            {
                // Failed operations may already have changed Session/settings.
                // Cache that actual state; never replace the original exception
                // with a secondary observation failure during unwinding.
                if (!_disposed && GodotObject.IsInstanceValid(View)) RefreshHostFacts();
            }
            catch (Exception error)
            {
                result?.Dispose();
                if (failure is null) throw;
                GD.PushError("Frontend state refresh after failure: " + error);
            }
            finally
            {
                foreach (long id in scope.FailureIds) _callbackFailures.Remove(id);
                _calls.Pop();
            }
        }
    }

    private D DispatchEffect(D effect, D facts)
    {
        try
        {
            RequireAlive();
            CacheHostFacts(facts);
            switch (Text(effect, "kind"))
            {
                case "audio": AudioCueRequested?.Invoke((RetailFrontendAudioCue)Int32(effect, "cue")); break;
                case "apply_settings": OptionsSettingsChanged?.Invoke(OptionsSettings); break;
                case "level_loading_started": Level100LoadingStarted?.Invoke(); break;
                case "level_load_requested": Level100LoadRequested?.Invoke(); break;
                case "gameplay_activated": GameplayActivated?.Invoke(); break;
                case "gameplay_suspended": GameplaySuspended?.Invoke(); break;
                case "return_main_menu": ReturnToMainMenuRequested?.Invoke(); break;
                case "exit": ExitRequested?.Invoke(); break;
                case "cursor_mode": CursorModeRequested?.Invoke((RetailFrontendCursorMode)Int32(effect, "mode")); break;
                case "career_selected":
                    int index = Int32(effect, "index");
                    if ((uint)index >= (uint)_originalDescriptors.Length)
                        throw new InvalidDataException("The native frontend selected an unknown career descriptor.");
                    CareerSelected?.Invoke(_originalDescriptors[index]);
                    break;
                default: throw new InvalidDataException("Unknown native frontend effect.");
            }
            return new D { ["ok"] = true };
        }
        catch (Exception error)
        {
            var result = new D { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message };
            if (_calls.TryPeek(out CallScope? scope))
            {
                do { _failureSequence = unchecked(_failureSequence + 1); }
                while (_failureSequence == 0 || _callbackFailures.ContainsKey(_failureSequence));
                _callbackFailures.Add(_failureSequence, ExceptionDispatchInfo.Capture(error));
                scope.FailureIds.Add(_failureSequence);
                result["host_exception_id"] = _failureSequence;
            }
            else
            {
                // Engine-driven callbacks have no managed caller to consume an
                // EDI token. Log now, return failure to stop this operation, and
                // leave later native frames eligible to run.
                GD.PushError("Frontend host callback: " + error);
            }
            return result;
        }
    }

    private void ObserveVoiceStart(AudioStreamPlayer player) => PlaybackRetirement.Observe(player);

    private void ReceiveHostState(D facts)
    {
        if (_disposed) return;
        try { CacheHostFacts(facts); }
        catch (Exception error) { GD.PushError("Frontend host-state signal: " + error); }
    }

    private void RefreshHostFacts()
    {
        using Variant returned = View.Call("host_snapshot");
        using D facts = Dictionary(returned, "host_snapshot");
        CacheHostFacts(facts);
    }

    private void CacheHostFacts(D facts)
    {
        int screen = Int32(facts, "screen");
        int launchWorld = Int32(facts, "launch_world_number");
        bool constructible = Boolean(facts, "selected_world_is_constructible");
        using Variant value = Field(facts, "options_settings");
        using D settings = Dictionary(value, "options_settings");
        D detached = settings.Duplicate(true);
        _optionsSettings.Dispose();
        _optionsSettings = detached;
        _screen = (RetailFrontendScreen)screen;
        _launchWorldNumber = launchWorld;
        _selectedWorldIsConstructible = constructible;
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        // A parent's _ExitTree can run after the native child was deleted.
        // Never call into a stale View, and never free the borrowed Control.
        if (GodotObject.IsInstanceValid(View))
        {
            if (View.IsConnected("host_state_changed", _hostStateChanged))
                View.Disconnect("host_state_changed", _hostStateChanged);
            using Variant effect = View.Call("set_effect_handler", default(Callable));
            using Variant voice = View.Call("set_voice_observer", default(Callable));
        }
        _optionsSettings.Dispose();
        _callbackFailures.Clear();
        _originalDescriptors = [];
        OriginalDescriptors = [];
        Level100LoadRequested = null;
        Level100LoadingStarted = null;
        GameplayActivated = null;
        GameplaySuspended = null;
        ReturnToMainMenuRequested = null;
        ExitRequested = null;
        CareerSelected = null;
        AudioCueRequested = null;
        CursorModeRequested = null;
        OptionsSettingsChanged = null;
    }

    private void RequireAlive() => ObjectDisposedException.ThrowIf(_disposed || !GodotObject.IsInstanceValid(View), this);

    private static void RequireResult(D result)
    {
        if (Boolean(result, "ok")) return;
        string message = Text(result, "error");
        string kind = Text(result, "error_type");
        string? parameter = result.ContainsKey("parameter") ? Text(result, "parameter") : null;
        throw kind switch
        {
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(parameter, message),
            "ArgumentNullException" => new ArgumentNullException(parameter, message),
            "ArgumentException" => new ArgumentException(message, parameter),
            "NullReferenceException" => new NullReferenceException(message),
            "InvalidDataException" => new InvalidDataException(message),
            "IndexOutOfRangeException" => new IndexOutOfRangeException(message),
            "OverflowException" => new OverflowException(message),
            "KeyNotFoundException" => new KeyNotFoundException(message),
            // JsonReaderException is internal to System.Text.Json. Native
            // admission retains its failure family without a second parser.
            "JsonReaderException" or "JsonException" => new JsonException(message),
            "IOException" => new IOException(message),
            _ => new InvalidOperationException(message),
        };
    }

    private static Variant Field(D value, string field) => value.TryGetValue(field, out Variant result)
        ? result : throw new InvalidDataException("The native frontend omitted " + field + ".");
    private static D Dictionary(Variant value, string name) => value.VariantType == Variant.Type.Dictionary
        ? value.AsGodotDictionary() : throw new InvalidDataException("The native frontend did not return a Dictionary: " + name);
    private static int Int32(D owner, string field)
    {
        using Variant value = Field(owner, field);
        if (value.VariantType != Variant.Type.Int || value.AsInt64() is < int.MinValue or > int.MaxValue)
            throw new InvalidDataException("The native frontend did not return an Int32: " + field);
        return value.AsInt32();
    }
    private static bool Boolean(D owner, string field)
    {
        using Variant value = Field(owner, field);
        return value.VariantType == Variant.Type.Bool ? value.AsBool()
            : throw new InvalidDataException("The native frontend did not return a Boolean: " + field);
    }
    private static string Text(D owner, string field)
    {
        using Variant value = Field(owner, field);
        return value.VariantType == Variant.Type.String ? value.AsString()
            : throw new InvalidDataException("The native frontend did not return a String: " + field);
    }

    private static RetailOptionsSettings ReadOptionsSettings(D value) => new()
    {
        SoundVolume = value["sound_volume"].AsSingle(),
        MusicVolume = value["music_volume"].AsSingle(),
        MouseSensitivity = value["mouse_sensitivity"].AsSingle(),
        ControllerConfiguration = value["controller_configuration"].AsInt32(),
        InvertYWalkerPlayer1 = value["invert_y_walker_player1"].AsBool(),
        InvertYWalkerPlayer2 = value["invert_y_walker_player2"].AsBool(),
        InvertYFlightPlayer1 = value["invert_y_flight_player1"].AsBool(),
        InvertYFlightPlayer2 = value["invert_y_flight_player2"].AsBool(),
        OverallDetail = value["overall_detail"].AsInt32(),
        ShadowDetail = value["shadow_detail"].AsInt32(),
        GeometryDetail = value["geometry_detail"].AsInt32(),
        TrilinearMipmapping = value["trilinear_mipmapping"].AsBool(),
        VSync = value["v_sync"].AsBool(),
        LandscapeResolution = value["landscape_resolution"].AsInt32(),
        TextureResolution = value["texture_resolution"].AsInt32(),
        Enable32BitTextures = value["enable32_bit_textures"].AsInt32(),
        SwapSpeakers = value["swap_speakers"].AsBool(),
        HardwareSound = value["hardware_sound"].AsBool(),
        SoundQuality = value["sound_quality"].AsInt32(),
        SoundMethod3D = value["sound_method3_d"].AsInt32(),
    };

    // Retained temporarily for the independent debriefing comparison fixture;
    // it marshals values only and does not own a second presentation state.
    internal static D DebriefingFrame(RetailDebriefingProjection value) => new()
    {
        ["world_finished"] = value.WorldFinished,
        ["mission_status"] = (int)value.MissionStatus,
        ["primary_objectives"] = (int)value.PrimaryObjectives,
        ["secondary_objectives"] = (int)value.SecondaryObjectives,
        ["grade_byte"] = value.GradeByte is byte grade ? Variant.From((int)grade) : default,
        ["new_goodie_count"] = value.NewGoodieCount,
        ["first_goodie"] = value.FirstGoodie,
    };
}
