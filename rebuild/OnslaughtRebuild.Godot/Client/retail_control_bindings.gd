# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## RetailControlBindings.cs presentation data. The source owner records the
## 22 action/localization codes and captured default slot labels. Two alternate
## binding slots are displayed under the retail Player 1/Player 2 headers;
## this is not a second-player or device-mapping owner. No new retail findings.

enum RowKind { HEADER = 0, SPACER = 1, BINDING = 2, INVERT_WALKER = 3, INVERT_FLIGHT = 4 }
const ROW_COUNT: int = 22
const ROW_PITCH: float = 10.0
const TOP_PAD: float = 5.0
const LEFT_COLUMN_X: float = 50.0
const RIGHT_COLUMN_RIGHT: float = 590.0
const PLAYER1_HEADER: String = "Player 1"
const PLAYER2_HEADER: String = "Player 2"
const _ROWS: Array = [
	[0x37, RowKind.HEADER, "Control configuration details", PLAYER1_HEADER, PLAYER2_HEADER],
	[0x38, RowKind.INVERT_WALKER, "Walker mode invert Y axis", "", ""],
	[0x39, RowKind.INVERT_FLIGHT, "Flight mode invert Y axis", "", ""],
	[0x3a, RowKind.SPACER, "", "", ""],
	[0x3b, RowKind.BINDING, "Movement: Forward", "UP", "Key W"],
	[0x3c, RowKind.BINDING, "Backward", "DOWN", "Key S"],
	[0x3d, RowKind.BINDING, "Left", "LEFT", "Key A"],
	[0x3e, RowKind.BINDING, "Right", "RIGHT", "Key D"],
	[0x3f, RowKind.SPACER, "", "", ""],
	[0x40, RowKind.BINDING, "Look: Up", "Mouse", "Key I"],
	[0x41, RowKind.BINDING, "Down", "Mouse", "Key K"],
	[0x42, RowKind.BINDING, "Left", "Mouse", "Key J"],
	[0x43, RowKind.BINDING, "Right", "Mouse", "Key L"],
	[0x44, RowKind.SPACER, "", "", ""],
	[0x45, RowKind.BINDING, "Zoom: In", "Mousewheel down", "Key ="],
	[0x46, RowKind.BINDING, "Out", "Mousewheel up", "Key -"],
	[0x47, RowKind.SPACER, "", "", ""],
	[0x48, RowKind.BINDING, "Others: Fire weapon", "Left Mouse Button", "Caps Lock"],
	[0x49, RowKind.BINDING, "Select Weapon", "Right Mouse Button", "Key ;"],
	[0x4a, RowKind.BINDING, "Transform", "Num 0", "Space"],
	[0x4b, RowKind.BINDING, "Air Brake", "RIGHT CONTROL", "Shift"],
	[0x4c, RowKind.BINDING, "Special function", "Right Shift", "Tab"],
]


static func rows() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for row: Array in _ROWS:
		result.append({"action_code": row[0], "kind": row[1], "label": row[2], "slot0": row[3], "slot1": row[4]})
	return result


static func invert_y_label(inverted: Variant) -> Dictionary:
	if not inverted is bool:
		return {"ok": false, "error_type": "ArgumentException", "error": "Invert-Y label requires a Boolean flag."}
	# The rendered word is deliberately opposite the flag's gameplay effect.
	return {"ok": true, "value": "Off" if inverted else "On"}
