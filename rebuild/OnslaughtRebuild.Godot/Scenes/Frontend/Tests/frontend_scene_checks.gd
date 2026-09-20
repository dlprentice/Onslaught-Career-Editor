# SPDX-License-Identifier: GPL-3.0-or-later
# Run with --headless --script; add --editor to verify the same production tool scene.
extends SceneTree

func _initialize() -> void:
    call_deferred("run_checks")

func require(condition: bool, message: String) -> bool:
    if not condition:
        push_error(message)
        quit(1)
    return condition

func run_checks() -> void:
    var scene: PackedScene = load("res://Scenes/Frontend/Frontend.tscn")
    var view: Control = scene.instantiate()
    var stage: Control = view.get_node("Stage")
    var menu: Control = view.get_node("Stage/MainMenu")
    var row: Control = menu.get_node("NewGame")
    if not require(stage.get_child_count() == 10, "Expected 10 authored frontend pages before Ready"): return
    if not require(menu.get_node("Language/Flag") is TextureRect, "Language must be a native texture control"): return
    if not require(menu.get_node("VerticalGuide") is ColorRect, "Guide must be a native color control"): return
    if not require(row.position == Vector2(99, 294) and row.size == Vector2(240, 20), "Measured default row geometry changed"): return
    if not require(row.get("Text") == "New Game", "Main-menu production text is not authored"): return
    if not require(not row.get("OverrideText"), "Authored English labels must not replace imported localization"): return
    var shadow: TextureRect = menu.get_node("TitleLogo/ShadowMotion/Shadow")
    var shadow_origin: Vector2 = shadow.position
    var old_pointer: int = Input.mouse_mode
    root.add_child(view)
    await process_frame
    if not require(menu.get_node("Language/Flag").texture != null, "Flag production pixels unavailable"): return
    if not require(menu.get_node("TitleLogo/Body").texture != null, "Title production pixels unavailable"): return
    if not require(view.get_node("Stage/Loading/Background").texture != null, "Loading production pixels unavailable"): return
    if not require(Input.mouse_mode == old_pointer, "Frontend scene changed pointer mode"): return
    if Engine.is_editor_hint():
        if not require(menu.visible and not view.is_processing() and not view.is_processing_input(), "Editor must show frozen Main Menu without processing"): return
        if not require(not view.has_node("RetailMouseCursor"), "Editor must not install the game cursor"): return
        var pages: Array[String] = ["ClickToStart", "MainMenu", "QuitConfirm", "CareerName", "LevelSelect", "MissionBriefing", "SelectConfiguration", "Loading", "Options", "Debriefing"]
        for page in range(pages.size()):
            view.set("EditorPage", page)
            if not require(stage.get_node(pages[page]).visible, "Editor page selector did not expose its actual page"): return
            if not require(not view.is_processing() and not view.is_processing_input(), "Changing editor page started processing"): return
            if pages[page] == "ClickToStart":
                var click: Control = stage.get_node("ClickToStart")
                if not require(not click.get("_frame_supplied") and click.get_node("Splash/Motion/Image").has_method("drawing_rect"), "Click editor page must expose its native production controls and frozen facts"): return
                if not require(click.view_snapshot() == {"pulse_timer": 5.0, "page_seconds": 5.0}, "Editor selection must not advance Click clocks"): return
                if not require(click.get_node("Title/Body/Motion/Image").texture == menu.get_node("TitleLogo/Body").texture, "Click and the main menu must share the production title recipe"): return
            if pages[page] == "Debriefing":
                var report: Control = stage.get_node("Debriefing")
                if not require(not report.get("_frame_supplied") and report.get_node("Report/LevelName").has_method("displayed_units"), "Debriefing must show its native frozen projection"): return
            if pages[page] == "Loading":
                var loading: Control = stage.get_node("Loading")
                if not require(not loading.get("_frame_supplied") and loading.get_node("Caption") is Node2D
                    and loading.get_node("Caption/Body").has_method("displayed_units"), "Loading must expose the same native fractional caption and frozen facts"): return
                if not require(loading.view_snapshot().facts == {"loading_frames": 0, "launch_requested": false, "ready": false}, "Editor selection must not advance or request loading"): return
        view.set("EditorPage", 1)
    else:
        if not require(view.get_node("Stage/ClickToStart").visible and not menu.visible, "Runtime frontend must start on its real click page"): return
        view.set_process(false)
        view.set_process_input(false)
    if not require(view.find_children("*", "AudioStreamPlayer", true, false).is_empty(), "Menu initialized an audio player"): return
    if not require(view.find_children("*", "Camera3D", true, false).is_empty(), "Menu initialized gameplay"): return
    var old_position: Vector2 = row.position
    row.position += Vector2(10, 5)
    row.size += Vector2(8, 2)
    await process_frame
    if not require(row.position == old_position + Vector2(10, 5), "Presentation overwrote an authored layout edit"): return
    if not require(row.get("SourceRect") == Rect2(99, 294, 240, 20), "Layout edit rewrote imported geometry"): return
    if not require(shadow.position == shadow_origin, "Animation overwrote authored shadow geometry"): return
    view.size = Vector2(1280, 720)
    if not require(stage.scale == Vector2(1.5, 1.5) and stage.position == Vector2(160, 0), "Widescreen changed the measured stage fit"): return
    var packed := PackedScene.new()
    if not require(packed.pack(view) == OK, "Frontend scene cannot be packed"): return
    var state: SceneState = packed.get_state()
    for node in range(state.get_node_count()):
        for property in range(state.get_node_property_count(node)):
            var value: Variant = state.get_node_property_value(node, property)
            if value is ImageTexture:
                if not require(false, "Public scene serialization retained private image pixels"): return
    var reloaded: Control = packed.instantiate()
    root.add_child(reloaded)
    await process_frame
    if not require(reloaded.get_node("Stage/MainMenu/TitleLogo/ShadowMotion/Shadow").position == shadow_origin, "Scene roundtrip accumulated shadow animation into layout"): return
    if not require(reloaded.get_node("Stage/MainMenu/NewGame").position == row.position, "Scene roundtrip discarded authored row position"): return
    reloaded.queue_free()
    print("FRONTEND_SCENE_CHECKS: 10 authored pages, 7 menu rows, native textures/guides, production assets, preserved authored edits, transient pixels, pointer unchanged; editor=", Engine.is_editor_hint())
    view.queue_free()
    await process_frame
    if Engine.is_editor_hint():
        while EditorInterface.get_resource_filesystem().is_scanning():
            await process_frame
        await create_timer(0.25).timeout
    quit(0)
