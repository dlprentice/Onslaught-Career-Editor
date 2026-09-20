# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production scene, standard headless runtime/editor. One argument:
## a fresh owned output directory beneath this worktree's local-data.
const ClickPage = preload("res://Scenes/Frontend/click_presentation.gd")
const Laws = preload("res://Client/click_to_start_laws.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const SECTIONS: Array[String] = ["Splash", "Prompt", "Slide", "Title", "TitleFlash"]
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "time_batches", "editing", "facts", "preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/ClickToStart.tscn", "res://Scenes/Frontend/click_presentation.gd",
	"res://Scenes/Frontend/frontend_image.gd", "res://Scenes/Frontend/frontend_bitmap_label.gd",
	"res://Client/click_to_start_laws.gd", "res://Scenes/Shared/retail_cosf.gd"]
const RECIPES: Array[Dictionary] = [
	{"node": "Splash/Motion/Image", "source": "res://Assets/Frontend/Backgrounds/click-to-start.texture.aya", "size": Vector2i(1024, 1024), "compression": 0},
	{"node": "Slide/Shadow/Motion/Image", "source": "res://Assets/Frontend/click-slide.texture.aya", "size": Vector2i(128, 128), "compression": 1},
	{"node": "Title/Body/Motion/Image", "source": "res://Assets/Frontend/title-logo.texture.aya", "size": Vector2i(512, 256), "compression": 1}]
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _output: String = ""
var _finished: bool = false
var _source_hashes: Dictionary = {}
var _asset_images: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if DisplayServer.get_name() != "headless" or args.size() != 1 or not _owned_directory(args[0]):
		quit(2)
		return
	_output = args[0]
	for name: String in ["report.json", "roundtrip.tscn"]:
		if FileAccess.file_exists(_output.path_join(name)): quit(2); return
	create_timer(80).timeout.connect(func() -> void:
		if not _finished: _failures.append("Harness timeout before completion."); _finish())
	var pointer: int = Input.mouse_mode
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	var cosine_source: String = ProjectSettings.globalize_path("res://").path_join(Laws.Cosine.SOURCE_RELATIVE_PATH).simplify_path()
	_source_hashes[cosine_source] = FileAccess.get_sha256(cosine_source)
	var input_hashes: Dictionary = {}
	for recipe: Dictionary in RECIPES: input_hashes[recipe.source] = FileAccess.get_sha256(recipe.source)
	input_hashes["res://Assets/Hud/font-13ps.texture.aya"] = FileAccess.get_sha256("res://Assets/Hud/font-13ps.texture.aya")
	var packed: PackedScene = load("res://Scenes/Frontend/ClickToStart.tscn")
	var view: ClickPage = packed.instantiate()
	if _authored(view): _done("authored_scene")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	viewport.add_child(view)
	await process_frame
	await process_frame
	if not _check(view.get("_assets_configured") and view.get("_error") == "", "Production resources admit before the page reports readiness; configured=%s, error=%s." % [view.get("_assets_configured"), view.get("_error")]):
		viewport.queue_free()
		view = null
		viewport = null
		packed = null
		await process_frame
		await process_frame
		await _settle_editor()
		_finish()
		return
	if _assets(view): _done("production_assets")
	if _time_batches(view): _done("time_batches")
	if _editing(view): _done("editing")
	if _facts_and_refusals(view): _done("facts")
	if _preview(view): _done("preview")
	var frozen: Dictionary = view.view_snapshot()
	await process_frame
	await process_frame
	_check(view.view_snapshot() == frozen, "Rendering frames never advance the supplied or Inspector time facts.")
	if _publication(view): _done("publication")
	if _ownership(view, pointer, input_hashes): _done("ownership")
	viewport.queue_free()
	view = null
	viewport = null
	packed = null
	await process_frame
	await process_frame
	await _settle_editor()
	_finish()


func _settle_editor() -> void:
	if Engine.is_editor_hint():
		while EditorInterface.get_resource_filesystem().is_scanning(): await process_frame
		await create_timer(0.25).timeout


func _authored(view: ClickPage) -> bool:
	_check(not view.is_inside_tree() and not view.is_node_ready(), "The actual scene exposes content before entering the tree or Ready.")
	_check(view.get_child_count() == 5, "Five production sections are authored.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480), "The source 640x480 design stage is authored.")
	for index: int in range(SECTIONS.size()):
		_check(view.get_child(index).name == SECTIONS[index] and view.get_child(index) is Node2D,
			"Section submit order and editable outer Node2D: " + SECTIONS[index])
	_check(view.get_node("Prompt").get_child_count() == 5 and view.get_node("Title").get_child_count() == 5,
		"All prompt/title outline and body passes exist before Ready.")
	_check(view.get_node("Slide").get_child_count() == 2, "Both slide passes exist before Ready.")
	for index: int in range(5):
		var prompt_part: Node2D = view.get_node("Prompt").get_child(index)
		var title_part: Node2D = view.get_node("Title").get_child(index)
		var label: Control = prompt_part.get_node("Motion/Text")
		_check(prompt_part.name == ClickPage.PROMPT_PARTS[index] and prompt_part.transform == Transform2D.IDENTITY
			and prompt_part.get_node("Motion").transform == Transform2D.IDENTITY
			and label.content_origin == Vector2(Laws.GLYPH_PASSES[index].dx, Laws.GLYPH_PASSES[index].y),
			"Prompt pass order and measured authored text origins: " + str(index))
		var title_image: Control = title_part.get_node("Motion/Image")
		_check(title_part.name == ClickPage.TITLE_PARTS[index] and title_part.transform == Transform2D.IDENTITY
			and title_part.get_node("Motion").transform == Transform2D.IDENTITY and title_image.centered
			and title_image.center == Vector2(Laws.TITLE_PASSES[index].x, Laws.TITLE_PASSES[index].y),
			"Title pass order and source center on the actual authored image control: " + str(index))
		_check(label is Control and label.text == "Click to start" and label.get_rect() == Rect2(0, 0, 128, 16), "Each prompt pass is a real editable production text control.")
		_check(not label.shadow and not label.body_origin and label.ink_color == (Color.WHITE if index == 4 else Color.BLACK), "Prompt outline/body colors and draw origin remain exact.")
		_check(title_image.get_rect() == Rect2(0, 0, 512, 256) and title_image.drawing_rect() == Rect2(title_image.center - Vector2(256, 128), Vector2(512, 256)), "Every title pass owns full control geometry and the measured centered draw rectangle.")
	var splash_image: Control = view.get_node("Splash/Motion/Image")
	_check(splash_image.get_rect() == Rect2(0, 0, 1024, 1024) and splash_image.centered and splash_image.center == Vector2(320, 240)
		and splash_image.drawing_rect() == Rect2(-192, -272, 1024, 1024), "Splash has actual authored dimensions, center and centered draw geometry before Ready.")
	var flash_image: Control = view.get_node("TitleFlash/Motion/Image")
	_check(view.get_node("TitleFlash").transform == Transform2D.IDENTITY and flash_image.centered and flash_image.center == Vector2(250, 290)
		and flash_image.get_rect() == Rect2(0, 0, 512, 256) and flash_image.drawing_rect() == Rect2(-6, 162, 512, 256), "The separate sixth title pass retains its authored center and full geometry.")
	for index: int in range(2):
		var part: Node2D = view.get_node("Slide").get_child(index)
		var image: Control = part.get_node("Motion/Image")
		_check(part.name == ("Shadow" if index == 0 else "Body") and part.transform == Transform2D.IDENTITY
			and part.get_node("Motion").transform == Transform2D.IDENTITY
			and not image.centered and image.center == Vector2(Laws.SLIDE_PASSES[index].x, Laws.SLIDE_PASSES[index].y), "Slide shadow precedes body with retained authored rectangle origins.")
		_check(image.get_rect() == Rect2(0, 0, 128, 128) and image.drawing_rect() == Rect2(image.center, Vector2(128, 128)), "Slide image has actual editable control bounds and draw rectangle.")
		_check(image.self_modulate == _color(int(Laws.SLIDE_PASSES[index].color)), "Slide pass retains its measured source tint.")
	for recipe: Dictionary in RECIPES:
		var texture: Texture2D = view.get_node(recipe.node).texture
		_check(texture != null and texture.get_script().resource_path == "res://Scenes/Shared/retail_texture_page.gd", "Actual native texture recipe exists before Ready.")
		_check(texture.source_path == recipe.source and texture.dimensions == recipe.size and texture.compression == recipe.compression, "Private texture route/dimensions/format are authored: " + recipe.node)
	for node: Node in view.find_children("*", "Control", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "All authored controls load in standard Godot.")
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Every presentation control ignores input.")
	return true


func _assets(view: ClickPage) -> bool:
	_check(view.font.page.source_path == "res://Assets/Hud/font-13ps.texture.aya" and view.font.page.dimensions == Vector2i(256, 256)
		and view.font.page.compression == 2 and view.font.cell_size == Vector2i(16, 16) and view.font.columns == 16 and not view.font.system_font,
		"The production font13 atlas and cell law are shared with all prompt controls.")
	_check(view.font.ensure_loaded().ok and view.font.glyph_widths().size() == 256, "Font metrics come from the admitted atlas.")
	for recipe: Dictionary in RECIPES:
		var texture: Texture2D = view.get_node(recipe.node).texture
		_check(texture.ensure_loaded().ok, "Actual page loads through its production recipe: " + recipe.node)
		var image: Image = texture.get_image()
		_check(image.get_size() == recipe.size and not image.is_empty(), "The inspectable recipe supplies its actual full-size image: " + recipe.node)
		# Recipes deliberately retain compressed DDS storage for production upload.
		# Inspect a detached CPU copy rather than require a different upload format.
		var decoded: Image = image.duplicate() as Image
		var decompressed: Error = decoded.decompress() if decoded.is_compressed() else OK
		_check(decompressed == OK, "The retained image can be decoded for bounded art inspection: " + recipe.node)
		if decompressed == OK:
			decoded.convert(Image.FORMAT_RGBA8)
			decoded.clear_mipmaps()
			var pixels: PackedByteArray = decoded.get_data()
			_check(pixels.size() == recipe.size.x * recipe.size.y * 4, "The full base-level RGBA image is present: " + recipe.node)
			var hasher := HashingContext.new()
			_check(hasher.start(HashingContext.HASH_SHA256) == OK and hasher.update(pixels) == OK, "Bounded decoded-art identity can be recorded.")
			_asset_images.append({"node": recipe.node, "format": image.get_format(), "mipmaps": image.get_mipmap_count(),
				"uploaded_bytes": image.get_data().size(), "rgba_base_bytes": pixels.size(), "rgba_base_sha256": hasher.finish().hex_encode()})
		decoded = null
		image = null
	_check(view.get_node("Slide/Shadow/Motion/Image").texture == view.get_node("Slide/Body/Motion/Image").texture, "Slide passes share the same admitted resource.")
	for part: String in ClickPage.TITLE_PARTS:
		_check(view.get_node("Title/" + part + "/Motion/Image").texture == view.get_node("TitleFlash/Motion/Image").texture, "Title and sixth pass share the same admitted resource.")
	for part: String in ClickPage.PROMPT_PARTS:
		var label: Control = view.get_node("Prompt/" + part + "/Motion/Text")
		_check(label.get("_font") == view.font and label.displayed_units() == Text.units("Click to start").value, "Every visible text pass binds the same production font and faithful label.")
	_check(not view.get("_frame_supplied") and view.view_snapshot() == {"pulse_timer": 5.0, "page_seconds": 5.0}, "Opening uses authored frozen display facts.")
	return true


func _time_batches(view: ClickPage) -> bool:
	for facts: Dictionary in [{"pulse_timer": 0.0, "page_seconds": 0.0}, {"pulse_timer": 0.333984375, "page_seconds": 1.6666666666666667},
		{"pulse_timer": 4.0, "page_seconds": 2.0}, {"pulse_timer": 4.001, "page_seconds": 2.05}, {"pulse_timer": 5.0, "page_seconds": 5.0},
		{"pulse_timer": 6.0, "page_seconds": 6.0}, {"pulse_timer": 8.0, "page_seconds": 31.0}]:
		_check(view.set_frame(facts).ok and view.view_snapshot() == facts, "One detached time batch updates production controls.")
		var timer: float = facts.pulse_timer
		var seconds: float = facts.page_seconds
		_check(view.get_node("Splash/Motion/Image").drawing_rect() == _centered_rect(Vector2(Laws.splash_x(timer), Laws.splash_y(timer)), Vector2(1024, 1024), Laws.splash_scale(timer)), "Splash forms the retained float32 rectangle before canvas transforms.")
		_check(view.get_node("Prompt").visible == Laws.prompt_visible(timer), "Prompt keeps strict visibility edges.")
		_check(view.get_node("Title").visible == Laws.title_visible(seconds) and view.get_node("TitleFlash").visible == Laws.sixth_visible(seconds), "Title and sixth pass keep their separate strict gates.")
		for index: int in range(2):
			var part: String = "Shadow" if index == 0 else "Body"
			_check(view.get_node("Slide/" + part + "/Motion/Image").drawing_rect() == Rect2(
				F.value(Laws.SLIDE_PASSES[index].x - Laws.slide_offset(timer)), Laws.SLIDE_PASSES[index].y, 128, 128), "Both slide controls form the source rectangle before canvas transforms.")
		var prompt_center: float = F.value(320.0 - F.value(F.value(int(view.font.measure(Laws.PROMPT))) * 0.5))
		for index: int in range(5):
			var label: Control = view.get_node("Prompt/" + ClickPage.PROMPT_PARTS[index] + "/Motion/Text")
			_check(label.get("_offset") == Vector2(prompt_center, 0)
				and label.content_origin == Vector2(Laws.GLYPH_PASSES[index].dx, Laws.GLYPH_PASSES[index].y), "Prompt centering uses the same font width without replacing its measured authored origin.")
		if Laws.title_visible(seconds):
			for index: int in range(5):
				var image: Control = view.get_node("Title/" + ClickPage.TITLE_PARTS[index] + "/Motion/Image")
				var color: int = Laws.title_outline_color(seconds) if index < 4 else Laws.title_body_color(seconds)
				_check(image.drawing_rect() == _centered_rect(Vector2(Laws.TITLE_PASSES[index].x, Laws.TITLE_PASSES[index].y), Vector2(512, 256), Laws.title_scale(seconds))
					and image.get("_ink") == _color(color), "Each title control receives the exact centered rectangle/color.")
		if Laws.sixth_visible(seconds):
			_check(view.get_node("TitleFlash/Motion/Image").drawing_rect() == _centered_rect(Vector2(250, 290), Vector2(512, 256), Laws.sixth_scale(seconds))
				and view.get_node("TitleFlash/Motion/Image").get("_ink") == _color(Laws.sixth_color(seconds)), "The sixth pass consumes its own centered rectangle/color.")
	return true


func _editing(view: ClickPage) -> bool:
	var authored: Dictionary = {}
	for section: String in SECTIONS:
		var node: Node2D = view.get_node(section)
		node.position += Vector2(7.25, -3.5)
		node.scale = Vector2(1.25, 0.75)
		node.rotation = 0.125
		authored[section] = node.transform
	for group: String in ["Prompt", "Slide", "Title"]:
		for child: Node2D in view.get_node(group).get_children():
			child.position += Vector2(0.25, 0.5)
			child.rotation = -0.0625
			authored[str(view.get_path_to(child))] = child.transform
	var geometry: Dictionary = {}
	var centers: Dictionary = {}
	var origins: Dictionary = {}
	for node: Control in view.find_children("*", "Control", true, false):
		node.position += Vector2(0.25, -0.5)
		node.size += Vector2(3, 2)
		geometry[str(view.get_path_to(node))] = node.get_rect()
		if node.has_method("drawing_rect"):
			node.center += Vector2(0.25, 1.5)
			centers[str(view.get_path_to(node))] = node.center
		elif node.has_method("set_content_offset"):
			node.content_origin += Vector2(0.5, -1.25)
			origins[str(view.get_path_to(node))] = node.content_origin
	for timer: float in [0.25, 2.05, 4.5, 6.0, 8.0]:
		_check(view.set_frame({"pulse_timer": timer, "page_seconds": timer}).ok, "Time batch remains admitted with deliberate authored edits.")
		for path: String in authored: _check(view.get_node(path).transform == authored[path], "Batch retains authored outer transform: " + path)
		for path: String in geometry: _check(view.get_node(path).get_rect() == geometry[path], "Batch retains authored child geometry: " + path)
		for path: String in origins: _check(view.get_node(path).content_origin == origins[path], "Batch retains the authored text draw origin: " + path)
		for path: String in centers:
			var image: Control = view.get_node(path)
			_check(image.center == centers[path], "Batch retains authored image center: " + path)
			if path.begins_with("Splash/"):
				var position := Vector2(F.value(image.center.x + F.value(Laws.splash_x(timer) - 320.0)), F.value(image.center.y + F.value(Laws.splash_y(timer) - 240.0)))
				_check(image.drawing_rect() == _centered_rect(position, image.size, Laws.splash_scale(timer)), "Edited splash size/center actually affect the production draw rectangle.")
			elif path.begins_with("Slide/"):
				_check(not image.centered and image.drawing_rect() == Rect2(F.value(image.center.x - Laws.slide_offset(timer)), image.center.y, image.size.x, image.size.y), "Edited slide size/origin actually affect the production draw rectangle.")
			elif path.begins_with("Title/") and Laws.title_visible(timer):
				_check(image.drawing_rect() == _centered_rect(image.center, image.size, Laws.title_scale(timer)), "Edited title size/center actually affect the production draw rectangle.")
			elif path.begins_with("TitleFlash/") and Laws.sixth_visible(timer):
				_check(image.drawing_rect() == _centered_rect(image.center, image.size, Laws.sixth_scale(timer)), "Edited sixth-pass size/center actually affect the production draw rectangle.")
	view.prompt = "Enhanced prompt"
	_check(not view.override_prompt, "Faithful prompt remains authoritative unless explicitly overridden.")
	for part: String in ClickPage.PROMPT_PARTS:
		_check(view.get_node("Prompt/" + part + "/Motion/Text").displayed_units() == Text.units("Click to start").value, "Inspector text alone does not silently replace retail defaults.")
	view.override_prompt = true
	var center: float = F.value(320.0 - F.value(F.value(int(view.font.measure("Enhanced prompt"))) * 0.5))
	for part: String in ClickPage.PROMPT_PARTS:
		_check(view.get_node("Prompt/" + part + "/Motion/Text").displayed_units() == Text.units("Enhanced prompt").value
			and view.get_node("Prompt/" + part + "/Motion/Text").get("_offset") == Vector2(center, 0), "Explicit override updates and recenters the actual five production passes.")
	view.override_prompt = false
	for part: String in ClickPage.PROMPT_PARTS:
		_check(view.get_node("Prompt/" + part + "/Motion/Text").displayed_units() == Text.units("Click to start").value, "Disabling enhanced text restores the faithful prompt.")
	for path: String in authored: _check(view.get_node(path).transform == authored[path], "Text refresh retains authored outer transform: " + path)
	for path: String in geometry: _check(view.get_node(path).get_rect() == geometry[path], "Text refresh retains authored child geometry: " + path)
	for path: String in centers: _check(view.get_node(path).center == centers[path], "Text refresh retains authored image center: " + path)
	for path: String in origins: _check(view.get_node(path).content_origin == origins[path], "Text refresh retains the authored text draw origin: " + path)
	return true


func _facts_and_refusals(view: ClickPage) -> bool:
	var facts: Dictionary = {"pulse_timer": 5.0, "page_seconds": 2.0, "extra": [{"sample": 4}]}
	_check(view.set_frame(facts).ok, "Host facts are accepted as one coarse display batch.")
	facts.pulse_timer = 99.0
	facts.extra[0].sample = 88
	var snapshot: Dictionary = view.view_snapshot()
	snapshot.page_seconds = 99.0
	snapshot.extra[0].sample = 77
	_check(view.view_snapshot() == {"pulse_timer": 5.0, "page_seconds": 2.0, "extra": [{"sample": 4}]}, "Inputs and returned snapshots cannot mutate stored facts.")
	var before: Dictionary = view.view_snapshot()
	var visual: Dictionary = _visual_state(view)
	for invalid: Dictionary in [{}, {"pulse_timer": 2.0}, {"pulse_timer": 2, "page_seconds": 2.0},
		{"pulse_timer": 2.0, "page_seconds": 2}, {"pulse_timer": null, "page_seconds": 2.0},
		{"pulse_timer": 2.0, "page_seconds": true}, {"pulse_timer": "2", "page_seconds": 2.0}]:
		var result: Dictionary = view.set_frame(invalid)
		_check(not result.ok and result.error_type == "InvalidDataException", "Missing or malformed binary64 facts are refused explicitly.")
		_check(view.view_snapshot() == before and _visual_state(view) == visual, "Refused facts cannot partially mutate display or stored time.")
	for paths: Dictionary in [{"splash": 7}, {7: "not a source route"}]:
		_check(not view.configure_assets(paths).ok and view.view_snapshot() == before, "Malformed asset path carriers are refused before mutation.")
	return true


func _preview(view: ClickPage) -> bool:
	var incoming: Dictionary = {"pulse_timer": 8.0, "page_seconds": 31.0}
	view.set_frame(incoming)
	view.editor_preview = view.editor_preview.duplicate(true)
	view.editor_preview.pulse_timer = 4.25
	view.editor_preview.page_seconds = 2.05
	_check(view.view_snapshot() == (view.editor_preview.snapshot() if Engine.is_editor_hint() else incoming), "Inspector updates refresh only the editor/frozen preview, never an active runtime batch.")
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied"), "An explicit preview request displays harmless resource facts.")
	view.editor_preview.pulse_timer = 5.25
	_check(view.view_snapshot() == view.editor_preview.snapshot() and not view.get("_frame_supplied"), "Changing a frozen resource refreshes the same actual page without a clock.")
	var previous: Resource = view.editor_preview
	view.editor_preview = previous.duplicate(true)
	var expected: Dictionary = view.editor_preview.snapshot()
	previous.pulse_timer = 99.0
	_check(view.view_snapshot() == expected, "Replacing preview disconnects the previous resource's changed signal.")
	previous = null
	return true


func _publication(view: ClickPage) -> bool:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "Actual configured production page remains packable.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for index: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(index)):
			_stored(state.get_node_property_value(index, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Public scene serialization writes only a fresh owned test artifact.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Saved scene contains recipes and layout, never decoded private pixels.")
	var loaded: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(loaded != null, "The serialized production scene reopens.")
	if loaded == null: return false
	var copy: ClickPage = loaded.instantiate()
	_check(not copy.is_node_ready() and copy.get_child_count() == 5, "Reopened scene exposes authored content before Ready.")
	for section: String in SECTIONS: _check(copy.get_node(section).transform == view.get_node(section).transform, "Serialized outer editing survives reopen: " + section)
	for recipe: Dictionary in RECIPES:
		_check(copy.get_node(recipe.node).get_rect() == view.get_node(recipe.node).get_rect()
			and copy.get_node(recipe.node).texture.source_path == recipe.source, "Reopen preserves edited control geometry and actual production asset route.")
		if copy.get_node(recipe.node).has_method("drawing_rect"):
			_check(copy.get_node(recipe.node).center == view.get_node(recipe.node).center, "Reopen preserves the authored centered-draw anchor.")
	for part: String in ClickPage.PROMPT_PARTS:
		var text_path: String = "Prompt/" + part + "/Motion/Text"
		_check(copy.get_node(text_path).content_origin == view.get_node(text_path).content_origin
			and copy.get_node(text_path).get_rect() == view.get_node(text_path).get_rect(), "Reopen preserves the edited production text origin and bounds.")
	copy.free()
	copy = null
	state = null
	loaded = null
	packed = null
	return true


func _ownership(view: ClickPage, pointer: int, hashes: Dictionary) -> bool:
	for node: Node in [view] + view.find_children("*", "", true, false):
		_check(not node.is_processing() and not node.is_physics_processing() and not node.is_processing_input()
			and not node.is_processing_unhandled_input(), "No authored node owns gameplay, input or a frame/physics clock: " + str(node.name))
	for type: String in ["Timer", "AnimationPlayer", "AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D", "Node3D", "Camera2D"]:
		_check(view.find_children("*", type, true, false).is_empty(), "Presentation introduces no " + type + " owner.")
	_check(Input.mouse_mode == pointer, "Scene and editor activity preserve pointer ownership.")
	for path: String in hashes: _check(FileAccess.get_sha256(path) == hashes[path], "Production source input remains unchanged: " + path)
	for path: String in _source_hashes: _check(FileAccess.get_sha256(path) == _source_hashes[path], "Production scene/script stayed frozen during this receipt: " + path)
	return true


func _visual_state(view: ClickPage) -> Dictionary:
	var result: Dictionary = {}
	for node: CanvasItem in view.find_children("*", "CanvasItem", true, false):
		result[str(view.get_path_to(node))] = {"transform": node.get_transform(), "visible": node.visible, "modulate": node.modulate}
		if node.has_method("drawing_rect"):
			result[str(view.get_path_to(node))].drawing_rect = node.drawing_rect()
			result[str(view.get_path_to(node))].ink = node.get("_ink")
		elif node.has_method("displayed_units"):
			result[str(view.get_path_to(node))].text = node.displayed_units()
			result[str(view.get_path_to(node))].content_offset = node.get("_offset")
			result[str(view.get_path_to(node))].content_origin = node.content_origin
	return result


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()): return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Serialized resource graph excludes private decoded pixels.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0: _stored(value.get(property.name), visited)
	elif value is Array:
		for item: Variant in value: _stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value: _stored(value[key], visited)


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		if _failures.size() <= 15: push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("CLICK_SCENE_SECTION: ", section)


func _finish() -> void:
	if _finished: return
	_finished = true
	for section: String in REQUIRED:
		if not _completed.has(section): _failures.append("Incomplete section: " + section)
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failures.size(), "failures": _failures,
		"completed": _completed, "editor": Engine.is_editor_hint(), "source_sha256": _source_hashes, "asset_images": _asset_images}
	var file := FileAccess.open(_output.path_join("report.json"), FileAccess.WRITE)
	if file == null: quit(2); return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("CLICK_SCENE_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _color(value: int) -> Color:
	return Color(float((value >> 16) & 255) / 255.0, float((value >> 8) & 255) / 255.0,
		float(value & 255) / 255.0, float((value >> 24) & 255) / 255.0)


static func _centered_rect(center: Vector2, dimensions: Vector2, scale: float) -> Rect2:
	var width: float = F.value(dimensions.x * scale)
	var height: float = F.value(dimensions.y * scale)
	return Rect2(F.value(center.x - F.value(width * 0.5)), F.value(center.y - F.value(height * 0.5)), width, height)


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	for part: String in path.trim_prefix(owned + "/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK: return false
	return true
