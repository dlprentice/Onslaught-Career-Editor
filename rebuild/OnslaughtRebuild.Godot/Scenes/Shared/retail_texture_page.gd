# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Texture2D
## Public, editable recipe for a private curated page. The same resource backs
## native TextureRects in the editor and game; decoded pixels are never stored.
const Aya = preload("res://Scenes/Shared/retail_aya_texture.gd")
enum PageFormat { DXT1, DXT2, RGBA8 }

@export_file("*.texture.aya") var source_path: String = "":
	set(value):
		source_path = value
		_invalidate()
@export var dimensions: Vector2i = Vector2i(128, 128):
	set(value):
		dimensions = value
		_invalidate()
@export var compression: PageFormat = PageFormat.DXT2:
	set(value):
		compression = value
		_invalidate()

var _decoded: Texture2D
var _attempted: bool = false
var _error: String = ""


func _invalidate() -> void:
	_decoded = null
	_attempted = false
	_error = ""
	emit_changed()


## Runtime scene owners admit their required recipes through this explicit
## result before reporting readiness. Virtual drawing cannot raise C# errors.
func ensure_loaded() -> Dictionary:
	var texture: Texture2D = _texture()
	return {"ok": true} if texture != null else {"ok": false, "error": _error}


func _texture() -> Texture2D:
	if not _attempted:
		_attempted = true
		if not FileAccess.file_exists(source_path):
			_error = "Curated HUD texture is missing: " + source_path
		else:
			var loader: RefCounted = Aya.new()
			_decoded = loader.load_texture(source_path, dimensions.x, dimensions.y, compression)
			_error = loader.error_message
		if _decoded == null and not Engine.is_editor_hint():
			push_error(_error)
	return _decoded


func _get_width() -> int:
	return dimensions.x


func _get_height() -> int:
	return dimensions.y


func _has_alpha() -> bool:
	return true


func _get_rid() -> RID:
	var texture: Texture2D = _texture()
	return texture.get_rid() if texture != null else RID()


func _get_image() -> Image:
	var texture: Texture2D = _texture()
	return texture.get_image() if texture != null else Image.create_empty(1, 1, false, Image.FORMAT_RGBA8)


func _draw(canvas_item: RID, position: Vector2, modulate: Color, transpose: bool) -> void:
	var texture: Texture2D = _texture()
	if texture != null:
		texture.draw(canvas_item, position, modulate, transpose)


func _draw_rect(canvas_item: RID, rect: Rect2, tile: bool, modulate: Color, transpose: bool) -> void:
	var texture: Texture2D = _texture()
	if texture != null:
		texture.draw_rect(canvas_item, rect, tile, modulate, transpose)


func _draw_rect_region(canvas_item: RID, rect: Rect2, source_rect: Rect2, modulate: Color,
		transpose: bool, clip_uv: bool) -> void:
	var texture: Texture2D = _texture()
	if texture != null:
		texture.draw_rect_region(canvas_item, rect, source_rect, modulate, transpose, clip_uv)
