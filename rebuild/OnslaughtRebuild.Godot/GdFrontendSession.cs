// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary managed presenter boundary. The native Session is the sole owner
/// of navigation, pending edges and campaign state. Each operation refreshes
/// detached display facts once; drawing and property reads never call GDScript.
/// Verified save objects remain with the original host and are returned by the
/// supplied descriptor ordinal, including when two descriptors compare equal.
/// </summary>
internal sealed class GdFrontendSession : IDisposable
{
    private readonly GodotObject _state;
    private readonly GodotObject _path;
    private readonly RetailCareerDescriptor[] _originalDescriptors;
    private bool _disposed;

    internal int NativeCallCount { get; private set; }
    public RetailFrontendScreen Screen { get; private set; }
    public RetailFrontendLanguage Language { get; private set; }
    public int SelectedMainIndex { get; private set; }
    public int SelectedQuitConfirmIndex { get; private set; }
    public RetailFrontendMenuItem SelectedMainItem => Items[SelectedMainIndex];
    public IReadOnlyList<RetailFrontendMenuItem> Items { get; private set; } = [];
    public IReadOnlyList<RetailCareerDescriptor> CareerDescriptors { get; }
    public IReadOnlyList<string> CareerNames { get; private set; } = [];
    public RetailFrontendCareerPageMode CareerPageMode { get; private set; }
    public int SelectedCareerIndex { get; private set; }
    public string GameName { get; private set; } = string.Empty;
    public int GameNameCursor { get; private set; }
    public bool GameNameIsFresh { get; private set; }
    public int SelectedWorldNumber { get; private set; }
    public int ConsumeLaunchWorldNumber => SelectedWorldNumber;
    public bool SelectedWorldIsConstructible { get; private set; }
    public bool Level100IntroCutscenePending { get; private set; }
    public string SelectedLevelName { get; private set; } = string.Empty;
    public IReadOnlyList<string> SelectedBriefingBody { get; private set; } = [];
    public int ConfigurationCount { get; private set; }
    public int SelectedConfigurationIndex { get; private set; }
    public RetailFrontendBattleEngineConfiguration SelectedConfiguration { get; private set; } = null!;
    public RetailFrontendMenuItemKind? UnavailableSelection { get; private set; }
    public RetailDebriefingProjection? Debriefing { get; private set; }

    public GdFrontendSession(IEnumerable<RetailCareerDescriptor>? careerDescriptors = null)
    {
        _originalDescriptors = careerDescriptors?.ToArray() ?? [];
        CareerDescriptors = Array.AsReadOnly(_originalDescriptors);
        using var supplied = new A();
        foreach (RetailCareerDescriptor descriptor in _originalDescriptors)
        {
            // Deliberately dereference descriptor here: the source constructor
            // also fails on a null record before a usable Session is returned.
            supplied.Add(new D
            {
                ["slot_number"] = descriptor.SlotNumber.HasValue ? descriptor.SlotNumber.Value : default(Variant),
                ["name"] = descriptor.Name is null ? default(Variant) : Utf16(descriptor.Name),
                ["career"] = descriptor.Career is null ? default(Variant) : new D
                {
                    ["suggested_world_number"] = descriptor.Career.SuggestedWorldNumber,
                    ["selectable_world_numbers"] = descriptor.Career.SelectableWorldNumbers.ToArray(),
                },
            });
        }
        using GodotObject factory = GD.Load<GDScript>("res://Client/frontend_session.gd").New().AsGodotObject();
        using D created = factory.Call("create", supplied).AsGodotDictionary();
        Require(created);
        _state = created["value"].AsGodotObject();
        _path = GD.Load<GDScript>("res://Client/frontend_scene_path.gd").New().AsGodotObject();
        Refresh();
    }

    public bool SelectCareerIndex(int index) => Change("select_career_index", index).AsBool();
    public bool SelectMainIndex(int index) => Change("select_main_index", index).AsBool();
    public bool SelectQuitConfirmIndex(int index) => Change("select_quit_confirm_index", index).AsBool();
    public bool SelectConfigurationIndex(int index) => Change("select_configuration_index", index).AsBool();
    public bool SelectWorld(int worldNumber) => Change("select_world", worldNumber).AsBool();
    public bool MovePrevious() => Change("move_previous").AsBool();
    public bool MoveNext() => Change("move_next").AsBool();
    public bool MoveGameNameCursor(bool right) => Change("move_game_name_cursor", right).AsBool();
    public bool RemoveGameNameCharacter() => Change("remove_game_name_character").AsBool();
    public bool AppendGameNameCharacter(char character, int currentTextWidth) =>
        Change("append_game_name_character", (int)character, currentTextWidth).AsBool();
    public RetailFrontendSignal Confirm() => (RetailFrontendSignal)Change("confirm").AsInt32();
    public RetailFrontendSignal Back() => (RetailFrontendSignal)Change("back").AsInt32();
    public bool ConsumeLevel100LaunchRequest() => Change("consume_level100_launch_request").AsBool();
    public void CompleteLevel100Load() => Change("complete_level100_load");
    public void BeginLevel100IntroCutscene() => Change("begin_level100_intro_cutscene");
    public void CompleteLevel100IntroCutscene() => Change("complete_level100_intro_cutscene");
    public RetailFrontendSignal RestartLevel100() => (RetailFrontendSignal)Change("restart_level100").AsInt32();
    public RetailFrontendSignal LeaveLevel100ForMainMenu() => (RetailFrontendSignal)Change("leave_level100_for_main_menu").AsInt32();
    public bool ReturnUnconstructibleLaunchToLevelSelect() => Change("return_unconstructible_launch_to_level_select").AsBool();

    public RetailCareerDescriptor? ConsumeSelectedCareerLoadRequest()
    {
        Variant index = Change("consume_selected_career_load_request_index");
        return index.VariantType == Variant.Type.Nil ? null : _originalDescriptors[index.AsInt32()];
    }

    public bool AcceptsClickToStartMouse(float x, float y) =>
        Call(_path, "accepts_click_to_start_mouse", (int)Screen, x, y).AsBool();
    public bool AcceptsClickToStartKey(int dik) =>
        Call(_path, "accepts_click_to_start_key", (int)Screen, dik).AsBool();
    public bool CanAcceptMainMenuRow(int index)
    {
        using D result = Call(_path, "can_accept_main_menu_row", _state, index).AsGodotDictionary();
        Require(result);
        return result["value"].AsBool();
    }

    public bool TryConfirmPage(bool startupMediaActive, out RetailFrontendSignal signal) =>
        Navigate("try_confirm_page", startupMediaActive, out signal);
    public bool TryBackPage(bool startupMediaActive, out RetailFrontendSignal signal) =>
        Navigate("try_back_page", startupMediaActive, out signal);
    public bool TryCompleteLoading(bool startupMediaActive, bool launchConsumed) =>
        ChangePath("try_complete_loading", _state, startupMediaActive, launchConsumed).AsBool();
    public bool TryCompleteIntroCutscene(bool startupMediaActive) =>
        ChangePath("try_complete_intro_cutscene", _state, startupMediaActive).AsBool();
    public bool TryAcceptWonHandoff(Level100MissionOutcome outcome, Level100MissionTerminalState terminalState) =>
        ChangePath("try_accept_won_handoff", _state, (int)outcome, (int)terminalState).AsBool();

    private bool Navigate(string method, bool startupMediaActive, out RetailFrontendSignal signal)
    {
        signal = RetailFrontendSignal.None;
        using D result = Operate(_path, method, _state, startupMediaActive);
        signal = (RetailFrontendSignal)result["signal"].AsInt32();
        return result["value"].AsBool();
    }

    private Variant Change(string method, params Variant[] arguments)
    {
        using D result = Operate(_state, method, arguments);
        return result["value"];
    }

    private Variant ChangePath(string method, params Variant[] arguments)
    {
        using D result = Operate(_path, method, arguments);
        return result["value"];
    }

    private D Operate(GodotObject owner, string method, params Variant[] arguments)
    {
        D result;
        try { result = Call(owner, method, arguments).AsGodotDictionary(); }
        finally
        {
            // Source methods can mutate before throwing (for example null-name
            // selection). Display the actual native state even on that path.
            Refresh();
        }
        try { Require(result); }
        catch { result.Dispose(); throw; }
        return result;
    }

    private Variant Call(GodotObject owner, string method, params Variant[] arguments)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        NativeCallCount++;
        return owner.Call(method, arguments);
    }

    private void Refresh()
    {
        using D snapshot = Call(_state, "snapshot").AsGodotDictionary();
        Screen = (RetailFrontendScreen)snapshot["screen"].AsInt32();
        Language = (RetailFrontendLanguage)snapshot["language"].AsInt32();
        SelectedMainIndex = snapshot["selected_main_index"].AsInt32();
        SelectedQuitConfirmIndex = snapshot["selected_quit_confirm_index"].AsInt32();
        Items = Array.AsReadOnly(snapshot["items"].AsGodotArray().Select(item =>
        {
            D row = item.AsGodotDictionary();
            return new RetailFrontendMenuItem((RetailFrontendMenuItemKind)row["kind"].AsInt32(), row["is_available"].AsBool());
        }).ToArray());
        CareerNames = Array.AsReadOnly(snapshot["career_names"].AsGodotArray().Select(value => RawString(value)!).ToArray());
        CareerPageMode = (RetailFrontendCareerPageMode)snapshot["career_page_mode"].AsInt32();
        SelectedCareerIndex = snapshot["selected_career_index"].AsInt32();
        GameName = RawString(snapshot["game_name"])!;
        GameNameCursor = snapshot["game_name_cursor"].AsInt32();
        GameNameIsFresh = snapshot["game_name_is_fresh"].AsBool();
        SelectedWorldNumber = snapshot["selected_world_number"].AsInt32();
        SelectedWorldIsConstructible = snapshot["selected_world_is_constructible"].AsBool();
        Level100IntroCutscenePending = snapshot["level100_intro_cutscene_pending"].AsBool();
        SelectedLevelName = snapshot["selected_level_name"].AsString();
        SelectedBriefingBody = Array.AsReadOnly(snapshot["selected_briefing_body"].AsGodotArray().Select(value => value.AsString()).ToArray());
        ConfigurationCount = snapshot["configuration_count"].AsInt32();
        SelectedConfigurationIndex = snapshot["selected_configuration_index"].AsInt32();
        D configuration = snapshot["selected_configuration"].AsGodotDictionary();
        SelectedConfiguration = new(configuration["catalog_record_index"].AsInt32(), configuration["authored_name"].AsString(),
            configuration["display_name"].AsString(), Weapon(configuration["walker_primary"]), Weapon(configuration["walker_secondary"]),
            Weapon(configuration["jet_primary"]), Weapon(configuration["jet_secondary"]));
        Variant unavailable = snapshot["unavailable_selection"];
        UnavailableSelection = unavailable.VariantType == Variant.Type.Nil ? null : (RetailFrontendMenuItemKind)unavailable.AsInt32();
        Variant debriefing = snapshot["debriefing"];
        if (debriefing.VariantType == Variant.Type.Nil) Debriefing = null;
        else
        {
            D row = debriefing.AsGodotDictionary();
            Variant grade = row["grade_byte"];
            Debriefing = new(row["world_finished"].AsInt32(), (RetailDebriefingMissionStatus)row["mission_status"].AsInt32(),
                (RetailDebriefingObjectiveSummary)row["primary_objectives"].AsInt32(),
                (RetailDebriefingObjectiveSummary)row["secondary_objectives"].AsInt32(),
                grade.VariantType == Variant.Type.Nil ? null : checked((byte)grade.AsInt32()),
                row["new_goodie_count"].AsInt32(), row["first_goodie"].AsBool());
        }
    }

    private static RetailFrontendWeaponConfiguration Weapon(Variant value)
    {
        D row = value.AsGodotDictionary();
        return new(row["authored_name"].AsString(), row["display_name"].AsString());
    }
    private static int[] Utf16(string value) => value.Select(character => (int)character).ToArray();
    private static string? RawString(Variant value) => value.VariantType == Variant.Type.Nil ? null :
        new string(value.AsInt32Array().Select(unit => checked((char)unit)).ToArray());

    private static void Require(D result)
    {
        if (result["ok"].AsBool()) return;
        string message = result["error"].AsString();
        string? parameter = result.TryGetValue("parameter", out Variant name) ? name.AsString() : null;
        throw result["error_type"].AsString() switch
        {
            "ArgumentNullException" => new ArgumentNullException(parameter, message),
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(parameter, message),
            "ArgumentException" => new ArgumentException(message, parameter),
            "NullReferenceException" => new NullReferenceException(message),
            "IndexOutOfRangeException" => new IndexOutOfRangeException(message),
            "OverflowException" => new OverflowException(message),
            "InvalidOperationException" => new InvalidOperationException(message),
            _ => new InvalidDataException(message),
        };
    }

    public void Dispose()
    {
        if (_disposed) return;
        _state.Dispose();
        _path.Dispose();
        _disposed = true;
    }
}
