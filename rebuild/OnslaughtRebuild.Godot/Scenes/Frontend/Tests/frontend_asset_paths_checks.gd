# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Focused native resource checks. One fresh owned local-data directory;
## no prepared/private texture is opened and no frontend/game tree is created.
const Paths = preload("res://Scenes/Frontend/retail_frontend_asset_paths.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const RECIPE: String = "res://Scenes/Frontend/RetailFrontendAssets.tres"
const REQUIRED: Array[String] = ["resource", "routing", "unicode_whitespace", "raw_units_and_errors", "serialization", "ownership"]
const SOURCES: Array[String] = [RECIPE, "res://Scenes/Frontend/retail_frontend_asset_paths.gd",
	"res://Core/canonical_json_string.gd"]
# .NET Char.IsWhiteSpace's exact BMP set. This includes NEL/NBSP and excludes
# obsolete Mongolian-vowel-separator/zero-width-space/BOM and control 0x1c..1f.
const WHITE: Array[int] = [9, 10, 11, 12, 13, 32, 0x85, 0xa0, 0x1680,
	0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200a,
	0x2028, 0x2029, 0x202f, 0x205f, 0x3000]
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _counts: Dictionary = {}
var _source_hashes: Dictionary = {}
var _string_carrier: Dictionary = {}
var _section: String = REQUIRED[0]
var _output: String = ""
var _finished: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if DisplayServer.get_name() != "headless" or args.size() != 1 or not _owned_directory(args[0]): quit(2); return
	_output = args[0]
	var output_directory := DirAccess.open(_output)
	if output_directory == null or not output_directory.get_files().is_empty() or not output_directory.get_directories().is_empty(): quit(2); return
	for name: String in ["report.json", "roundtrip.tres", "string-carrier.tres"]:
		if output_directory.is_link(name) or FileAccess.file_exists(_output.path_join(name)) or DirAccess.dir_exists_absolute(_output.path_join(name)): quit(2); return
	create_timer(30).timeout.connect(func() -> void:
		if not _finished: _failures.append("Timeout before every routing group completed."); _finish())
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	var pointer: int = Input.mouse_mode
	var child_count: int = root.get_child_count()
	var recipe: Paths = load(RECIPE) as Paths
	if not _check(recipe != null, "The existing public resource loads with its native script."): _finish(); return
	_check(recipe.FrontendDirectory == "res://Assets/Frontend" and recipe.HudDirectory == "res://Assets/Hud"
		and recipe.PauseDirectory == "res://Assets/PauseMenu" and recipe.TextureOverrides.is_empty(), "Existing property names and default routes are unchanged.")
	var properties: Dictionary = {}
	for property: Dictionary in recipe.get_property_list(): properties[property.name] = property
	for name: String in ["FrontendDirectory", "HudDirectory", "PauseDirectory"]:
		_check(properties.has(name) and properties[name].type == TYPE_STRING and properties[name].hint == PROPERTY_HINT_DIR
			and (int(properties[name].usage) & PROPERTY_USAGE_EDITOR) != 0 and (int(properties[name].usage) & PROPERTY_USAGE_STORAGE) != 0,
			"The existing directory field remains an editable stored String with directory hint: " + name)
	_check(properties.TextureOverrides.type == TYPE_DICTIONARY and (int(properties.TextureOverrides.usage) & PROPERTY_USAGE_EDITOR) != 0,
		"The typed override dictionary remains inspector-visible.")
	_check(recipe.TextureOverrides.get_typed_key_builtin() == TYPE_STRING and recipe.TextureOverrides.get_typed_value_builtin() == TYPE_STRING,
		"Overrides retain String keys and values.")
	_check(recipe.get_script().resource_path == SOURCES[1], "Production resource has no C# script dependency.")
	_done()

	_section = REQUIRED[1]
	var paths := Paths.new()
	for item: Array in [["Frontend", "Backgrounds/rock", "res://Assets/Frontend/Backgrounds/rock.texture.aya"],
		["Hud", "font-13ps", "res://Assets/Hud/font-13ps.texture.aya"], ["PauseMenu", "blank", "res://Assets/PauseMenu/blank.texture.aya"],
		["Frontend", "", "res://Assets/Frontend/.texture.aya"], ["Frontend", "../literal\\name", "res://Assets/Frontend/../literal\\name.texture.aya"]]:
		_value(paths.texture_path(item[0], item[1]), item[2], "Ordinary route and literal path components.")
	paths.TextureOverrides["Unknown/item"] = " \t../literal\\name/\u00a0 "
	_value(paths.texture_path("Unknown", "item"), " \t../literal\\name/\u00a0 ", "A valid override precedes folder validation and is returned without trimming.")
	paths.TextureOverrides["Unknown/item"] = " \u00a0\u202f"
	_failure(paths.texture_path("Unknown", "item"), "ArgumentOutOfRangeException", "folder", "Whitespace override falls through to the invalid folder.")
	for item: Array in [["", "/unit.texture.aya"], ["/", "/unit.texture.aya"], ["///", "/unit.texture.aya"],
		["res://", "res:/unit.texture.aya"], ["res://A////", "res://A/unit.texture.aya"], ["res://A// ", "res://A// /unit.texture.aya"],
		["res://A\\", "res://A\\/unit.texture.aya"], ["\u00a0//", "\u00a0/unit.texture.aya"],
		["\ufeffA/", "\ufeffA/unit.texture.aya"], ["relative/../root///", "relative/../root/unit.texture.aya"]]:
		paths.FrontendDirectory = item[0]
		_value(paths.texture_path("Frontend", "unit"), item[1], "TrimEnd removes only all trailing ASCII slashes.")
	paths.FrontendDirectory = "res://Assets/Frontend"
	for folder: Variant in ["frontend", "HUD", "Pause", "", null]:
		_failure(paths.texture_path_units(folder, "unit"), "ArgumentOutOfRangeException", "folder", "Folder matching remains exact and case-sensitive.")
	_done()

	_section = REQUIRED[2]
	for code: int in WHITE:
		paths.TextureOverrides["Frontend/unit"] = String.chr(code)
		_value(paths.texture_path("Frontend", "unit"), "res://Assets/Frontend/unit.texture.aya", "Every .NET whitespace code selects fallback: %04x" % code)
	paths.TextureOverrides["Frontend/unit"] = ""
	_value(paths.texture_path("Frontend", "unit"), "res://Assets/Frontend/unit.texture.aya", "Empty override selects fallback.")
	for code: int in [0, 1, 8, 14, 0x1c, 0x1d, 0x1e, 0x1f, 0x7f, 0x84, 0x86, 0x180e, 0x200b, 0x200c, 0x2060, 0xfeff, 0xffff, 0xd800, 0xdc00, 0x61]:
		var units := PackedInt32Array([code])
		_units(Paths.resolve_texture_path_units("Frontend", "unit", "base", "hud", "pause", {"Frontend/unit": units}), units,
			"Nonwhitespace override units are returned exactly: %04x" % code)
		if code != 0 and (code < 0xd800 or code > 0xdfff):
			paths.TextureOverrides["Frontend/unit"] = String.chr(code)
			_units(paths.texture_path_units("Frontend", "unit"), units, "Inspector String preserves the same nonwhitespace override.")
	paths.TextureOverrides["Frontend/unit"] = "\u2002 before\u00a0after\u2029"
	_value(paths.texture_path("Frontend", "unit"), "\u2002 before\u00a0after\u2029", "Surrounding Unicode whitespace is preserved on a nonblank override.")
	_done()

	_section = REQUIRED[3]
	paths.TextureOverrides.clear()
	var raw_name := PackedInt32Array([65, 0, 66, 0xd800, 88, 0xdc00, 0xfeff])
	var expected: PackedInt32Array = Text.units("res://Assets/Frontend/").value + raw_name + Text.units(".texture.aya").value
	_units(paths.texture_path_units("Frontend", raw_name), expected, "Raw name output retains NUL and lone surrogate words.")
	_failure(paths.texture_path("Frontend", raw_name), "UnsupportedString", "", "Native String conversion refuses unrepresentable paths without truncation.")
	var nul_only := PackedInt32Array([65, 0, 66])
	_failure(paths.texture_path("Frontend", nul_only), "UnsupportedString", "", "Embedded NUL is never opened as its prefix.")
	_units(paths.texture_path_units("Frontend", null), Text.units("res://Assets/Frontend/.texture.aya").value, "Null names retain C# interpolation's empty value.")
	_units(Paths.resolve_texture_path_units(null, null, null, null, null, {"/": "override"}), Text.units("override").value,
		"Null interpolation participates in override lookup before invalid-folder refusal.")
	_failure(Paths.resolve_texture_path_units(null, null, null, null, null, {}), "ArgumentOutOfRangeException", "folder", "Missing null-folder override refuses the folder first.")
	_failure(Paths.resolve_texture_path_units("Frontend", "unit", null, "hud", "pause", {}), "NullReferenceException", "",
		"Legacy forced null directory fails only after valid folder selection.")
	_units(Paths.resolve_texture_path_units("Frontend", "unit", null, "hud", "pause", {"Frontend/unit": "override"}), Text.units("override").value,
		"A valid override bypasses a forced null directory.")
	_failure(Paths.resolve_texture_path_units("Unknown", "unit", null, null, null, {}), "ArgumentOutOfRangeException", "folder", "Invalid folder precedes unused null directories.")
	_units(Paths.resolve_texture_path_units("Frontend", "unit", "base", "hud", "pause", {"Frontend/unit": null}), Text.units("base/unit.texture.aya").value,
		"Legacy null override selects fallback.")
	_failure(paths.texture_path_units(123, "unit"), "ArgumentException", "folder", "Unsupported host types are explicitly refused.")
	_failure(paths.texture_path_units("Frontend", 123), "ArgumentException", "name", "Unsupported name types are explicitly refused.")
	var returned: Dictionary = paths.texture_path_units("Frontend", raw_name)
	if returned.ok: returned.value[0] = 88
	_units(paths.texture_path_units("Frontend", raw_name), expected, "Returned units are detached from resource fields and input words.")
	_done()

	_section = REQUIRED[4]
	paths.FrontendDirectory = "relative/../enhanced///"
	paths.HudDirectory = "atlas/\ufeffinner/"
	paths.PauseDirectory = "separate\\pause/"
	paths.TextureOverrides["Unknown/exact"] = " \u00a0literal\\override "
	var copy: Paths = paths.duplicate(true) as Paths
	_check(copy != null, "Production resource duplicates as a native resource.")
	if copy != null:
		copy.TextureOverrides["Unknown/exact"] = "copy-only"
		_value(paths.texture_path("Unknown", "exact"), " \u00a0literal\\override ", "Deep resource duplication does not share mutable override state.")
	var saved: String = _output.path_join("roundtrip.tres")
	_check(ResourceSaver.save(paths, saved) == OK, "Edited paths serialize only to the fresh owned artifact.")
	var restored: Paths = ResourceLoader.load(saved, "Resource", ResourceLoader.CACHE_MODE_IGNORE) as Paths
	_check(restored != null, "Edited native routing resource reopens.")
	if restored != null:
		_check(restored.FrontendDirectory == paths.FrontendDirectory and restored.HudDirectory == paths.HudDirectory
			and restored.PauseDirectory == paths.PauseDirectory and restored.TextureOverrides == paths.TextureOverrides,
			"All original exported field names preserve their exact authored values. Expected=%s; actual=%s" % [JSON.stringify(_resource_words(paths)), JSON.stringify(_resource_words(restored))])
		_value(restored.texture_path("Frontend", "unit"), "relative/../enhanced/unit.texture.aya", "Reopened default route preserves literal directories.")
		_value(restored.texture_path("Unknown", "exact"), " \u00a0literal\\override ", "Reopened override still precedes folder validation.")
	var source: String = FileAccess.get_file_as_string(saved)
	_check(source.contains("retail_frontend_asset_paths.gd") and not source.contains(".cs") and not source.contains("PackedByteArray")
		and not source.contains("ImageTexture"), "Serialized resource contains public path definitions and no retail payload.")
	_string_carrier_probe()
	_done()

	_section = REQUIRED[5]
	_check(root.get_child_count() == child_count and Input.mouse_mode == pointer, "Resource activity creates no nodes and never changes pointer mode.")
	for path: String in SOURCES:
		_check(_source_hashes[path].length() == 64 and FileAccess.get_sha256(path) == _source_hashes[path], "Production source remains read-only: " + path)
	_check(recipe.TextureOverrides.is_empty() and recipe.FrontendDirectory == "res://Assets/Frontend", "Independent tests never mutate the shared production recipe.")
	_done()
	paths = null
	copy = null
	restored = null
	recipe = null
	await process_frame
	_finish()


func _value(result: Dictionary, expected: String, message: String) -> void:
	_check(result.get("ok", false) and typeof(result.get("value")) == TYPE_STRING and result.value == expected, message)


static func _resource_words(paths: Paths) -> Dictionary:
	var values: Dictionary = {}
	for name: String in ["FrontendDirectory", "HudDirectory", "PauseDirectory"]: values[name] = Text.units(paths.get(name)).value
	var overrides: Array[Dictionary] = []
	for key: String in paths.TextureOverrides: overrides.append({"key": Text.units(key).value, "value": Text.units(paths.TextureOverrides[key]).value})
	values.TextureOverrides = overrides
	return values


func _string_carrier_probe() -> void:
	# ResourceLoader's text String carrier removes a leading U+FEFF, including
	# from built-in properties. Compare both actual reloads; this native port
	# must not invent stronger editor storage than the shared engine provides.
	var original := Paths.new()
	original.resource_name = "\ufeffatlas/"
	original.HudDirectory = "\ufeffatlas/"
	var expected: PackedInt32Array = Text.units("\ufeffatlas/").value
	_check(Text.units(original.resource_name).value == expected and Text.units(original.HudDirectory).value == expected,
		"The exact leading-BOM value is present in both the built-in and exported String before serialization.")
	_units(original.texture_path_units("Hud", "unit"), Text.units("\ufeffatlas/unit.texture.aya").value,
		"Routing preserves the original leading BOM before any editor serialization.")
	var path: String = _output.path_join("string-carrier.tres")
	_check(ResourceSaver.save(original, path) == OK and FileAccess.get_file_as_string(path).contains("\ufeffatlas/"),
		"The text resource stores its literal leading-BOM String content.")
	var restored: Paths = ResourceLoader.load(path, "Resource", ResourceLoader.CACHE_MODE_IGNORE) as Paths
	if not _check(restored != null, "The carrier comparison reopens its actual saved resource."): return
	_string_carrier = {"builtin_before": Text.units(original.resource_name).value, "directory_before": Text.units(original.HudDirectory).value,
		"builtin_reloaded": Text.units(restored.resource_name).value, "directory_reloaded": Text.units(restored.HudDirectory).value}
	_check(_string_carrier.builtin_reloaded == _string_carrier.directory_reloaded,
		"Native path export and built-in Resource.resource_name have the same actual reload carrier.")
	_check(_string_carrier.builtin_reloaded == Text.units("atlas/").value,
		"Pinned dev6 text-resource loading drops the leading U+FEFF in both String properties; exact raw routing is a separate contract.")


func _units(result: Dictionary, expected: PackedInt32Array, message: String) -> void:
	_check(result.get("ok", false) and result.get("value") is PackedInt32Array and result.value == expected, message)


func _failure(result: Dictionary, kind: String, parameter: String, message: String) -> void:
	_check(not result.get("ok", true) and result.get("error_type") == kind and result.get("parameter", "") == parameter
		and not result.has("value"), message)


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	_counts[_section] = int(_counts.get(_section, 0)) + 1
	if not condition:
		_failures.append(message)
		if _failures.size() <= 12: push_error(message)
	return condition


func _done() -> void:
	_completed.append(_section)


func _finish() -> void:
	if _finished: return
	_finished = true
	if _completed != REQUIRED: _failures.append("Missing or out-of-order completion group.")
	for section: String in REQUIRED:
		if int(_counts.get(section, 0)) <= 0: _failures.append("Empty group: " + section)
	var report: Dictionary = {"schema": 1, "checks": _checks, "counts": _counts, "completed": _completed,
		"failure_count": _failures.size(), "failures": _failures, "source_sha256": _source_hashes, "string_carrier": _string_carrier}
	var file := FileAccess.open(_output.path_join("report.json"), FileAccess.WRITE)
	if file == null: quit(2); return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("FRONTEND_ASSET_PATHS_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/") or path.contains("\\"): return false
	var directory := DirAccess.open("/")
	if directory == null: return false
	for part: String in path.trim_prefix("/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK: return false
	return true
