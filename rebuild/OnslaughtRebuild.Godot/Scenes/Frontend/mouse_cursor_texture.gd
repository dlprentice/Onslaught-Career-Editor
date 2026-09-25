# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Shared/retail_texture_page.gd"
## Public mouse.tga recipe. The existing curated decoder validates all eight
## stored mip levels and converts DXT2 to the measured RGBA8 upload format.
## Missing files are optional at draw time: retain the old lazy retry behavior.
## Decoded images remain transient, inherited from the shared page resource.


func _texture() -> Texture2D:
	if _decoded != null: return _decoded
	if not FileAccess.file_exists(source_path):
		_error = "Frontend cursor texture is missing: " + source_path
		return null
	_attempted = true
	var loader: RefCounted = Aya.new()
	_decoded = loader.load_texture(source_path, dimensions.x, dimensions.y, compression, Image.FORMAT_RGBA8, 8)
	_error = loader.error_message
	if _decoded == null and not Engine.is_editor_hint(): push_error(_error)
	return _decoded
