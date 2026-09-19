# SPDX-License-Identifier: GPL-3.0-or-later
# Uses the existing canonical startup cache. Add --editor for the frozen tool path.
extends SceneTree

func _initialize() -> void:
    call_deferred("run_checks")

func require(condition: bool, message: String) -> bool:
    if not condition:
        push_error(message)
        quit(1)
    return condition

func run_checks() -> void:
    var scene: PackedScene = load("res://Scenes/Frontend/Startup.tscn")
    var view: Control = scene.instantiate()
    var video: TextureRect = view.get_node("Stage/Video")
    var splash: TextureRect = view.get_node("Stage/SplashFade/Splash")
    var voice: AudioStreamPlayer = view.get_node("RetailFmvVoice")
    var stage: Control = view.get_node("Stage")
    if not require(view.get_node("Black") is ColorRect, "Startup has no native black background"): return
    if not require(video.position == Vector2(0, 40) and video.size == Vector2(640, 400), "Measured FMV quad changed"): return
    if not require(video.self_modulate.is_equal_approx(Color8(254, 254, 254, 255)), "Measured FMV diffuse changed"): return
    if not require(splash.position == Vector2.ZERO and splash.size == Vector2(640, 480), "Measured splash stage changed"): return
    if not require(not voice.autoplay and voice.stream == null and voice.process_mode == Node.PROCESS_MODE_ALWAYS, "Authored voice must start unbound and inactive"): return
    if not Engine.is_editor_hint():
        var media_root := OS.get_environment("ONSLAUGHT_STARTUP_MEDIA")
        if media_root.is_empty():
            media_root = OS.get_environment("BEA_LOCAL_LAB").path_join("startup-media")
        view.call("Initialize", media_root, 0) # FixedTick: presentation checks stay silent.
        if not require(view.get("ScheduledSeconds") > 90.0, "Verified canonical cold-start media is unavailable"): return
    var pointer_before := Input.mouse_mode
    root.add_child(view)
    await process_frame
    if Engine.is_editor_hint():
        if not require(splash.texture != null and splash.get_parent().visible, "Editor did not bind the actual splash image"): return
        if not require(splash.texture.get_size() == Vector2(512, 512), "Unexpected canonical splash dimensions"): return
        view.set("EditorCue", 0)
        if not require(video.texture != null and video.visible, "Editor cue did not bind an actual video frame"): return
        if not require(not view.is_processing() and not view.is_processing_input(), "Editor startup scene must not run or accept input"): return
    else:
        if not require(video.texture != null and video.visible, "Production schedule did not reach the authored video control"): return
        var buffers: Dictionary[RID, bool] = {}
        for tick in range(12):
            await process_frame
            buffers[video.texture.get_rid()] = true
        if not require(buffers.size() == 2, "Video must reuse exactly two alternating textures"): return
    if not require(video.texture.get_size() == Vector2(480, 300), "Canonical video frame dimensions changed"): return
    if not require(not voice.playing and voice.stream == null, "Editor/fixed-tick validation must stay silent"): return
    if not require(Input.mouse_mode == pointer_before, "Startup scene took pointer ownership"): return
    video.position += Vector2(16, 4)
    video.size += Vector2(20, 10)
    await process_frame
    if not require(video.position == Vector2(16, 44) and video.size == Vector2(660, 410), "Frame updates overwrote authored video geometry"): return
    view.size = Vector2(1280, 720)
    if not require(stage.scale == Vector2(1.5, 1.5) and stage.position == Vector2(160, 0), "Startup widescreen fit changed"): return
    var packed := PackedScene.new()
    if not require(packed.pack(view) == OK, "Startup production scene cannot be packed"): return
    var state: SceneState = packed.get_state()
    for node in range(state.get_node_count()):
        for property in range(state.get_node_property_count(node)):
            if state.get_node_property_value(node, property) is ImageTexture:
                if not require(false, "Packing startup retained private decoded pixels"): return
    if not Engine.is_editor_hint():
        view.call("AbortForHarness")
        await process_frame
        await process_frame
        if not require(not view.visible and not view.is_processing() and not view.is_processing_input(), "Abort failed to retire startup ownership"): return
        if not require(video.texture == null and splash.texture == null, "Finish retained decoded presentation buffers"): return
    print("STARTUP_SCENE_CHECKS: authored surfaces/audio, measured rectangles/tint, actual private images, no editor/autoplay input or audio, preserved edits, widescreen and transient pixels; editor=", Engine.is_editor_hint())
    view.queue_free()
    await process_frame
    if Engine.is_editor_hint():
        while EditorInterface.get_resource_filesystem().is_scanning():
            await process_frame
        await create_timer(0.25).timeout
    quit(0)
