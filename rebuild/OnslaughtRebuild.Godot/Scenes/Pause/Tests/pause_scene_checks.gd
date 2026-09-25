# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const PauseScene: PackedScene = preload("res://Scenes/Pause/PauseMenu.tscn")
const AyaTexture = preload("res://Scenes/Shared/retail_aya_texture.gd")
const BitmapFont = preload("res://Scenes/Shared/retail_bitmap_font.gd")
const F32 = preload("res://Scenes/Shared/retail_float32.gd")
const ROOT_LABELS: Array[String] = ["Continue", "Message Log", "Briefing", "Controller Options", "Sound Options", "Video Options", "Retry", "Quit"]

var _checks: int = 0
var _failed: bool = false
var _capture_directory: String = ""
var _completed_sections: Dictionary = {}
var _requested_captures: Array[String] = []
var _completed_captures: Array[String] = []

func _initialize() -> void:
    _run.call_deferred()

func _run() -> void:
    for argument: String in OS.get_cmdline_user_args():
        if argument.begins_with("--pause-scene-capture-dir="):
            _capture_directory = argument.trim_prefix("--pause-scene-capture-dir=")
            if not _check(_capture_directory.is_absolute_path() and DirAccess.dir_exists_absolute(_capture_directory), "Capture directory must exist at an absolute task-owned path."):
                await _finish()
                return
    _check(F32.round_even(2.5) == 2.0 and F32.round_even(3.5) == 4.0 and
        F32.round_even(-2.5) == -2.0 and F32.round_even(-3.5) == -4.0, "Presentation rounding retains C# ties-to-even.")
    _check_aya_bounds()
    _check_font_boundaries()
    var pointer_before: int = Input.mouse_mode
    var view: CanvasLayer = PauseScene.instantiate()
    var surface: Control = view.get_node("Surface")
    var native: Control = surface.get_node("Native")
    var root_range: Control = native.get_node("RootRange")
    var prompt: Control = native.get_node("ConfirmationRange")
    var root_rows: Array[Node] = root_range.get_node("Rows").get_children()
    var prompt_rows: Array[Node] = prompt.get_node("Rows").get_children()
    var frame: Control = prompt.get_node("Frame")
    _check(root_rows.size() == 8 and prompt_rows.size() == 2, "Production rows exist before _ready.")
    _check(root_range.get_node_or_null("Frame") == null and frame.get_child_count() == 9, "Only confirmation owns the nine native panel cells.")
    _check(native.get_child_count() == 4 and surface.get_child_count() == 2, "Production surface contains only the retained overlay, circles and ranges.")
    for index: int in range(root_rows.size()):
        var row: Control = root_rows[index]
        _check(row.get("text") == ROOT_LABELS[index], "Authored root text and order match the retained contract.")
        _check(row.position == Vector2(0, 175 + 20 * index) and row.size == Vector2(640, 20), "Retained authored root row rectangle.")
    _check(root_range.get_node("Title").position.y == 145.0, "Root title uses its measured origin.")
    _check(prompt.get_node("Title").position.y == 285.0 and prompt_rows[0].position.y == 315.0 and
        prompt_rows[1].position.y == 335.0, "Confirmation title and rows use their measured origins.")
    var viewport := SubViewport.new()
    viewport.size = Vector2i(640, 480)
    viewport.disable_3d = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    root.add_child(viewport)
    viewport.add_child(view)
    await process_frame
    if not _check(bool(view.get("assets_loaded")), "The actual AYA atlases loaded with standard Godot."):
        await _finish(viewport)
        return
    _check(not view.is_processing() and not view.is_processing_input() and not view.is_processing_unhandled_input(), "The presentation has no independent clock or input loop.")
    _check(Input.mouse_mode == pointer_before, "Loading presentation never changes pointer ownership.")
    _check_public_scene_pack(view)
    _check_private_dds_contract()
    if Engine.is_editor_hint():
        _check(surface.visible and root_range.visible and not prompt.visible, "Editor uses the same authored root in a frozen open state.")
        _check(not bool(view.get("input_ready")) and int(view.call("point_at", Vector2(320, 295))) == -1, "Editor activity cannot activate a menu row.")
        var frozen_scale: Vector2 = native.get_node("Circle01").scale
        view.call("open_panel")
        view.call("close_panel")
        view.call("reset_panel")
        view.call("advance_animation", 10.0)
        _check(surface.visible and native.get_node("Circle01").scale == frozen_scale and not bool(view.get("is_closing")), "Runtime entrypoints cannot start or advance editor gameplay.")
        _check(not bool(view.call("set_snapshot", _snapshot())), "Editor rejects runtime model snapshots.")
        view.set("preview_confirmation", true)
        _check(root_range.visible and prompt.visible, "Editor confirmation retains the production root beneath it.")
        _check_confirmation(root_range, prompt)
        _check(Input.mouse_mode == pointer_before, "Editor preview preserves pointer policy.")
        await _capture(viewport, "pause-editor-confirmation.png")
        await _finish(viewport)
        return
    _check(not surface.visible and not bool(view.get("input_ready")), "Standalone runtime presentation starts inactive.")
    var snapshot: Dictionary = _snapshot()
    _check(bool(view.call("set_snapshot", snapshot)), "The production scene accepts the authoritative snapshot schema.")
    snapshot.root_entries[0].label = "Changed outside scene"
    snapshot.entries[0].label = "Changed outside scene"
    view.call("open_panel")
    _check(not bool(view.get("input_ready")) and not root_range.visible, "Opening gates input and rows during the fade.")
    for delta: float in [NAN, INF, -1.0, 0.0]:
        view.call("advance_animation", delta)
    _check(not bool(view.get("input_ready")), "Invalid time deltas cannot complete opening.")
    view.call("advance_animation", 0.2)
    var overlay: TextureRect = surface.get_node("Overlay")
    var circle_01: TextureRect = native.get_node("Circle01")
    var circle_02: TextureRect = native.get_node("Circle02")
    _near(overlay.self_modulate.a, F32.value(96.0 / 255.0), "Half-fade overlay alpha.")
    _near(circle_01.scale.x, F32.value(1.2), "Circle growth finishes at 0.2 seconds.")
    _near(circle_01.rotation, 0.0, "Circle rotation begins after growth.")
    _check(not bool(view.get("input_ready")), "Input is still gated at 0.2 seconds.")
    view.call("advance_animation", 0.2)
    _check(bool(view.get("input_ready")) and root_range.visible and not prompt.visible, "Root opens at 0.4 seconds.")
    _check(root_rows[0].get("text") == "Continue", "Presentation snapshots cannot be mutated through a producer's old dictionary.")
    _near(overlay.self_modulate.a, F32.value(192.0 / 255.0), "Retained overlay alpha ceiling.")
    _near(circle_01.rotation, F32.value(-0.2), "First circle rotation.")
    _near(circle_02.rotation, F32.value(0.2), "Second circle rotation.")
    _check(int(view.call("point_at", Vector2(0, 175))) == 0, "Inclusive left and top row boundary.")
    _check(int(view.call("point_at", Vector2(640, 194.999))) == 0, "Inclusive right and interior row edge.")
    _check(int(view.call("point_at", Vector2(640.001, 175))) == -1, "Outside the native horizontal region is refused.")
    _check(int(view.call("point_at", Vector2(320, 195))) == -1, "Disabled row begins at the previous row's exclusive end.")
    _check(int(view.call("point_at", Vector2(320, 295))) == 6, "Retry owns its authored hit rectangle.")
    _check(root_rows[0].get("text_color") == Color(1, 204.0 / 255.0, 0, 1), "Hit testing never mutates menu selection.")
    var retry: Control = root_rows[6]
    retry.position.y += 2.0
    _check(int(view.call("point_at", Vector2(320, 295))) == -1 and int(view.call("point_at", Vector2(320, 297))) == 6,
        "Inspector row-position edits move actual production hit regions.")
    retry.position.y -= 2.0
    await _capture(viewport, "pause-root.png")
    _check(bool(view.call("set_snapshot", _snapshot(1, 0, 6))), "Retry confirmation snapshot accepted.")
    _check(root_range.visible and prompt.visible, "Confirmation keeps drawing the root list beneath its panel.")
    _check_confirmation(root_range, prompt)
    _check(int(view.call("point_at", Vector2(320, 335))) == 1, "Confirmation Yes owns its authored row boundary.")
    await _capture(viewport, "pause-confirmation.png")
    view.call("close_panel")
    _check(not bool(view.get("input_ready")) and bool(view.get("is_closing")), "Closing immediately gates input.")
    view.call("advance_animation", 0.1)
    _check(not root_range.visible and not prompt.visible, "Rows disappear during the retained closing transition.")
    view.call("advance_animation", 0.3)
    _check(not surface.visible and not bool(view.get("is_closing")) and not bool(view.get("input_ready")), "Closing finishes after 0.4 seconds.")
    view.call("set_snapshot", _snapshot())
    view.call("open_panel")
    view.call("advance_animation", 0.4)
    viewport.size = Vector2i(1280, 720)
    await process_frame
    _near(native.scale.x, 1.5, "Native UI scales by viewport height.")
    _near(native.position.x, 160.0, "Native UI stays horizontally centred.")
    _check(int(view.call("point_at", Vector2(640, 442.5))) == 6, "Widescreen hit conversion still selects Retry.")
    _check(Input.mouse_mode == pointer_before, "Every presentation transition leaves pointer policy unchanged.")
    await _finish(viewport)

func _snapshot(page: int = 0, selected: int = 0, underlying: int = 0) -> Dictionary:
    # Explicit test inputs, not a competing production menu model.
    var root_entries: Array = []
    for index: int in range(ROOT_LABELS.size()):
        root_entries.append({"label": ROOT_LABELS[index], "enabled": index == 0 or index >= 6})
    return {
        "page": page, "selected_index": selected, "underlying_root_selection": underlying,
        "root_entries": root_entries,
        "entries": root_entries if page == 0 else [{"label": "No", "enabled": true}, {"label": "Yes", "enabled": true}],
    }

func _check_confirmation(root_range: Control, prompt: Control) -> void:
    var rows: Array[Node] = prompt.get_node("Rows").get_children()
    var title: Control = prompt.get_node("Title")
    _check(root_range.get_node("Rows/Retry").get("text_color") == Color(1, 204.0 / 255.0, 0, 1), "Underlying root selection stays highlighted.")
    _check(not bool(title.get("shadow")) and bool(rows[0].get("shadow")) and bool(rows[1].get("shadow")), "Title and item shadows preserve retail policy.")
    _check(title.get("text_color") == Color(80.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0, 1), "Retail title colour remains unchanged.")
    var widest: float = maxf(float(title.call("measure", "Are you sure?")), maxf(float(rows[0].call("measure", "No")), float(rows[1].call("measure", "Yes"))))
    var raw_width: float = F32.value((widest + 16.0) * F32.value(1.1))
    var width: float = maxf(64.0, F32.round_even(raw_width))
    var left: float = F32.round_even(F32.value(320.0 - F32.value(raw_width * 0.5)))
    var top_left: TextureRect = prompt.get_node("Frame/CornerTopLeft")
    var bottom_right: TextureRect = prompt.get_node("Frame/CornerBottomRight")
    _check(top_left.position == Vector2(left, 280) and top_left.size == Vector2(32, 32), "Panel centres before minimum-size clamping and preserves native corners.")
    _check(bottom_right.position == Vector2(left + width - 32, 327), "Confirmation frame retains its measured extent.")
    _check(top_left.flip_h and not top_left.flip_v and not bottom_right.flip_h and bottom_right.flip_v, "Corner UV mirrors face the panel interior.")
    _check(top_left.self_modulate == Color(0, 0, 0, 192.0 / 255.0), "Frame tint preserves ROUND(1.2*160)/255.")
    _completed_sections["confirmation"] = true

func _check_public_scene_pack(view: CanvasLayer) -> void:
    var packed := PackedScene.new()
    if not _check(packed.pack(view) == OK, "Production scene packs after private texture binding."):
        return
    var state: SceneState = packed.get_state()
    var texture_count: int = 0
    for node: int in range(state.get_node_count()):
        if state.get_node_type(node) != &"TextureRect":
            continue
        texture_count += 1
        var embeds_texture: bool = false
        for property: int in range(state.get_node_property_count(node)):
            embeds_texture = embeds_texture or state.get_node_property_name(node, property) == &"texture"
        _check(not embeds_texture, "Packing a public scene cannot embed decoded private texture bytes.")
    _check(texture_count == 12, "All twelve overlay/circle/frame texture controls have the serialization guard.")
    _completed_sections["pack"] = true

func _check_aya_bounds() -> void:
    var loader := AyaTexture.new()
    var payload: PackedByteArray = "A bounded synthetic texture stream.".to_ascii_buffer()
    var record: PackedByteArray = _aya_record(payload)
    _check(loader.inflate_aya(record) == payload and loader.error_message.is_empty(), "Strict AYA reader accepts a complete zlib record.")
    _check(loader.inflate_aya(record + _aya_record(payload)) == payload + payload, "Multiple AYA records concatenate their decoded payloads.")
    var cases: Array[PackedByteArray] = [PackedByteArray(), PackedByteArray([1, 2, 3]), PackedByteArray([0, 0, 0, 0]),
        PackedByteArray([255, 255, 255, 255]), PackedByteArray([8, 0, 0, 0, 1]), record + PackedByteArray([1])]
    var compressed: PackedByteArray = payload.compress(FileAccess.COMPRESSION_DEFLATE)
    cases.append(_framed(compressed + PackedByteArray([7, 8])))
    cases.append(_framed(compressed + compressed))
    for missing: int in range(1, mini(compressed.size(), 7)):
        cases.append(_framed(compressed.slice(0, compressed.size() - missing)))
    var corrupt: PackedByteArray = compressed.duplicate()
    corrupt[corrupt.size() - 1] ^= 1
    cases.append(_framed(corrupt))
    var oversized := PackedByteArray()
    oversized.resize(AyaTexture.MAXIMUM_SOURCE_BYTES + 1)
    cases.append(oversized)
    for malformed: PackedByteArray in cases:
        _check(loader.inflate_aya(malformed).is_empty() and not loader.error_message.is_empty(), "Malformed, truncated, oversized or trailing AYA input is refused.")
    var decoded_limit := PackedByteArray()
    decoded_limit.resize(AyaTexture.MAXIMUM_DDS_BYTES)
    _check(loader.inflate_aya(_aya_record(decoded_limit)).size() == AyaTexture.MAXIMUM_DDS_BYTES and loader.error_message.is_empty(), "Decoded AYA size permits the retained exact bound.")
    decoded_limit.append(0)
    _check(loader.inflate_aya(_aya_record(decoded_limit)).is_empty() and not loader.error_message.is_empty(), "Decoded AYA expansion beyond 8 MiB is refused.")
    _completed_sections["aya"] = true

func _check_private_dds_contract() -> void:
    var loader := AyaTexture.new()
    var source: PackedByteArray = FileAccess.get_file_as_bytes("res://Assets/PauseMenu/blank.texture.aya")
    var dds: PackedByteArray = loader.inflate_aya(source)
    if not _check(dds.size() >= 128, "Actual private DDS header is present."):
        return
    _check(loader.decode_image(source, 16, 16, AyaTexture.Compression.DXT1) != null, "Actual DXT1 texture matches its fixed identity.")
    _check(loader.decode_image(source, 16, 16, AyaTexture.Compression.DXT2) == null, "Unexpected FourCC is refused.")
    _check(loader.decode_image(source, 17, 16, AyaTexture.Compression.DXT1) == null, "Unexpected DDS dimensions are refused before native allocation.")
    _check(loader.decode_image(source, 16, 16, AyaTexture.Compression.DXT1, -1, int(dds.decode_u32(28)) + 1) == null, "Unexpected mip count is refused.")
    var malformed: PackedByteArray = dds.duplicate()
    malformed.encode_u32(16, 0x7fffffff)
    _check(loader.decode_image(_aya_record(malformed), 16, 16, AyaTexture.Compression.DXT1) == null, "Untrusted huge dimensions cannot reach the native image allocator.")
    _check(loader.decode_image(_aya_record(dds.slice(0, 127)), 16, 16, AyaTexture.Compression.DXT1) == null, "A short DDS header is refused.")
    malformed = dds.duplicate()
    malformed[0] = 0
    _check(loader.decode_image(_aya_record(malformed), 16, 16, AyaTexture.Compression.DXT1) == null, "DDS magic is checked.")
    var font_source: PackedByteArray = FileAccess.get_file_as_bytes("res://Assets/Hud/font-13ps.texture.aya")
    var font_dds: PackedByteArray = loader.inflate_aya(font_source)
    _check(loader.decode_image(font_source, 256, 256, AyaTexture.Compression.RGBA8) != null, "The production RGBA font preserves its exact channel-mask contract.")
    font_dds.encode_u32(92, 0x000000ff)
    _check(loader.decode_image(_aya_record(font_dds), 256, 256, AyaTexture.Compression.RGBA8) == null, "Incorrect RGBA channel masks are refused.")
    _completed_sections["dds"] = true

func _check_font_boundaries() -> void:
    var image: Image = Image.create(64, 24, false, Image.FORMAT_RGBA8)
    image.fill(Color.TRANSPARENT)
    # Four-pixel cells: '!' starts at x=4. The last row/column are excluded;
    # alpha exactly 16/255 is excluded, while alpha 17/255 determines width.
    image.set_pixel(6, 0, Color(1, 1, 1, 16.0 / 255.0))
    image.set_pixel(5, 0, Color(1, 1, 1, 17.0 / 255.0))
    image.set_pixel(7, 0, Color.WHITE)
    image.set_pixel(6, 3, Color.WHITE)
    var font := BitmapFont.new(ImageTexture.create_from_image(image), 4)
    _check(font.measure("!") == 3.0, "Glyph widths retain the strict binary32 alpha cutoff and excluded cell edges.")
    _check(font.measure(" ") == 2.0 and font.measure("!!") == 7.0, "Spaces and inter-glyph spacing retain measured cell rules.")
    _check(font.measure("") == 0.0 and font.measure("🚀") == font.measure("??"), "Unsupported UTF-16 surrogate pairs retain two fallback glyphs.")
    _completed_sections["font"] = true

func _aya_record(payload: PackedByteArray) -> PackedByteArray:
    return _framed(payload.compress(FileAccess.COMPRESSION_DEFLATE))

func _framed(compressed: PackedByteArray) -> PackedByteArray:
    var record := PackedByteArray()
    record.resize(4)
    record.encode_u32(0, compressed.size())
    record.append_array(compressed)
    return record

func _capture(viewport: SubViewport, filename: String) -> void:
    if _capture_directory.is_empty():
        return
    _requested_captures.append(filename)
    var destination: String = _capture_directory.path_join(filename)
    if not _check(not FileAccess.file_exists(destination), "Capture cannot overwrite an earlier observation."):
        return
    await RenderingServer.frame_post_draw
    if _check(viewport.get_texture().get_image().save_png(destination) == OK, "Saved requested capture in the task-owned directory."):
        _completed_captures.append(filename)

func _near(actual: float, expected: float, description: String) -> void:
    _check(absf(actual - expected) < 0.00001, description + " Expected %s, got %s." % [expected, actual])

func _check(condition: bool, description: String) -> bool:
    _checks += 1
    if not condition:
        _failed = true
        push_error(description)
    return condition

func _finish(viewport: SubViewport = null) -> void:
    # A GDScript runtime error may abort one helper and return to its caller.
    # Reaching this marker requires every invoked check group to reach its end.
    for section: String in ["aya", "font", "dds", "pack", "confirmation"]:
        _check(bool(_completed_sections.get(section, false)), "Check group completed without a script abort: " + section)
    _check(_requested_captures == _completed_captures, "Every requested capture completed without a script abort.")
    if viewport != null:
        viewport.queue_free()
    await process_frame
    await process_frame
    print("PAUSE_GDSCRIPT_CHECKS: %s checks; %s; editor=%s" % [_checks, "FAILED" if _failed else "passed", Engine.is_editor_hint()])
    quit(1 if _failed else 0)
