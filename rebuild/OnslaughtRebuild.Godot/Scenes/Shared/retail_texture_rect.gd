# SPDX-License-Identifier: GPL-3.0-or-later
@tool
class_name RetailTransientTextureRect
extends TextureRect

# Private decoded pixels are visible in the Inspector, but never serialized
# when this public production scene is saved. Its ordinary layout is retained.
func _validate_property(property: Dictionary) -> void:
    if property.name == "texture":
        property.usage = (int(property.usage) & ~PROPERTY_USAGE_STORAGE) | PROPERTY_USAGE_EDITOR | PROPERTY_USAGE_READ_ONLY
