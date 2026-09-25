# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Strict = preload("res://Core/strict_json.gd")
const Decimal = preload("res://Core/decimal_float64.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}


func _initialize() -> void:
    _run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
    counts[group] = int(counts.get(group, 0)) + 1
    if not _equal(actual, expected):
        failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _equal(actual: Variant, expected: Variant) -> bool:
    # Godot's built-in deep comparison/duplicate limit is shallower than the
    # admitted JSON nesting. Walk explicitly; hitting an engine recursion cap
    # must never make a deep malformed fixture look equal.
    var pending: Array = [[actual, expected]]
    while not pending.is_empty():
        var pair: Array = pending.pop_back()
        var left: Variant = pair[0]
        var right: Variant = pair[1]
        if left is Dictionary:
            if not right is Dictionary or left.size() != right.size():
                return false
            for key: Variant in left:
                if not right.has(key):
                    return false
                pending.append([left[key], right[key]])
        elif left is Array:
            if not right is Array or left.size() != right.size():
                return false
            for index: int in range(left.size()):
                pending.append([left[index], right[index]])
        elif left != right:
            return false
    return true


func _normalize(value: Strict.Value) -> Dictionary:
    match value.kind:
        "object":
            var members: Array = []
            for member: Dictionary in value.members:
                var name: Dictionary = _normalize(member.name)
                var child: Dictionary = _normalize(member.value)
                if not name.ok or not child.ok:
                    return {"ok": false}
                members.append({"name": name.value, "value": child.value})
            return {"ok": true, "value": {"kind": "object", "members": members}}
        "array":
            var items: Array = []
            for child: Strict.Value in value.items:
                var item: Dictionary = _normalize(child)
                if not item.ok:
                    return item
                items.append(item.value)
            return {"ok": true, "value": {"kind": "array", "items": items}}
        "string":
            var encoded: Dictionary = value.utf8_bytes()
            if not encoded.ok:
                return {"ok": false}
            return {"ok": true, "value": {"kind": "string", "units": Array(value.string_units), "utf8": encoded.value.hex_encode()}}
        "number":
            var integer: Dictionary = value.as_int64()
            var small: Dictionary = value.as_int32()
            var binary: Dictionary = value.as_float64()
            if not binary.ok:
                return {"ok": false}
            var bytes := PackedByteArray()
            bytes.resize(8)
            bytes.encode_double(0, binary.value)
            return {"ok": true, "value": {"kind": "number", "text": value.number_text,
                "int64": str(integer.value) if integer.ok else null,
                "int32": str(small.value) if small.ok else null, "doubleHex": bytes.hex_encode()}}
        "boolean":
            return {"ok": true, "value": {"kind": "boolean", "value": value.boolean}}
        "null":
            return {"ok": true, "value": {"kind": "null"}}
    return {"ok": false}


func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2:
        quit(2)
        return
    var vectors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
    var cases: Array = vectors.get("json", [])
    _check("admission", "nonempty oracle", not cases.is_empty(), true)
    for row: Dictionary in cases:
        var result: Dictionary = Strict.parse_bytes(row.hex.hex_decode(), row.rejectDuplicates, int(row.maxDepth))
        if result.ok:
            result = _normalize(result.value)
        _check("admission", row.name, result.ok, row.ok)
        if result.ok and row.ok:
            _check("values", row.name, result.value, row.value)
    var object: Dictionary = Strict.parse_bytes('{"a":1,"\\u0061":2}'.to_utf8_buffer(), false)
    _check("lookup", "last-property lookup", object.value.member("a").as_int64().value, 2)
    _check("lookup", "case sensitive", object.value.member("A"), null)
    var nul: Strict.Value = Strict.parse_bytes('"a\\u0000b"'.to_utf8_buffer()).value
    _check("string", "NUL native conversion explicitly refused", nul.as_string().ok, false)
    _check("string", "NUL UTF8 byte preservation", nul.utf8_bytes().value.hex_encode(), "610062")
    var unicode: Strict.Value = Strict.parse_bytes('"Aquila Ω 🚀"'.to_utf8_buffer()).value
    _check("string", "native Unicode string", unicode.as_string().value, "Aquila Ω 🚀")
    _check("admission", "invalid name rejected before schema lookup", Strict.parse_bytes('{"\\uD800":0}'.to_utf8_buffer()).ok, false)
    _check("admission", "invalid value remains a token until requested", Strict.parse_bytes('"\\uD800"'.to_utf8_buffer()).ok, true)
    _check("admission", "NUL name retained exactly", Strict.parse_bytes('{"a\\u0000":0}'.to_utf8_buffer()).ok, true)
    for token: String in ["", "+1", "01", "1.", "1e", "NaN", " true", "-", "1 2", "1e+-1"]:
        _check("decimal_admission", token, Decimal.parse(token).ok, false)
    var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(),
        "failures": failures, "completed": ["strict_json"]}
    var file := FileAccess.open(args[1], FileAccess.WRITE)
    if file == null:
        quit(2)
        return
    file.store_string(JSON.stringify(report, "\t"))
    file.close()
    print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
    quit(0 if failures.is_empty() else 1)
