# SPDX-License-Identifier: GPL-3.0-or-later
# Run with --headless --editor --script; checks the actual production tool scene.
extends SceneTree

func _initialize() -> void:
    call_deferred("check_editor_scene")

func check_editor_scene() -> void:
    assert(Engine.is_editor_hint(), "This check requires --editor.")
    var pointer_before := Input.mouse_mode
    var scene: PackedScene = load("res://Scenes/Hud/FirstFlightHud.tscn")
    var view: Node = scene.instantiate()
    var viewport := SubViewport.new()
    viewport.size = Vector2i(640, 480)
    viewport.disable_3d = true
    root.add_child(viewport)
    viewport.add_child(view)
    await process_frame
    await process_frame
    var stage: Control = view.get_node("Surface/DesignStage")
    assert(stage.get_child_count() == 3)
    assert(stage.get_node("Base/Compass").size == Vector2(256, 256))
    assert(view.get("ShowEditorIllustration"))
    assert(stage.get_node("Base").material is ShaderMaterial)
    assert(stage.get_node("Glow").material is ShaderMaterial)
    assert(stage.get_node("Text").material is ShaderMaterial)
    view.set("ShowEditorIllustration", false)
    assert(not view.get_node("Surface").visible)
    view.set("ShowEditorIllustration", true)
    assert(view.get_node("Surface").visible)
    for property in stage.get_node("Base/Compass").get_property_list():
        if property["name"] in ["Part", "SourceRect"]:
            assert((property["usage"] & PROPERTY_USAGE_READ_ONLY) != 0)
    assert(stage.get_node("Base/ScannerBackdrop").texture.get_image().get_width() == 128)
    assert(view.find_children("*", "AudioStreamPlayer", true, false).is_empty())
    assert(view.find_children("*", "Camera3D", true, false).is_empty())
    assert(Input.mouse_mode == pointer_before)
    print("HUD_EDITOR_CHECKS: actual tool scene initializes private presentation assets and native content without gameplay, audio or pointer capture.")
    viewport.queue_free()
    await process_frame
    var filesystem: EditorFileSystem = EditorInterface.get_resource_filesystem()
    await create_timer(1.0).timeout
    while filesystem.is_scanning():
        await process_frame
    await create_timer(0.25).timeout
    quit(0)
