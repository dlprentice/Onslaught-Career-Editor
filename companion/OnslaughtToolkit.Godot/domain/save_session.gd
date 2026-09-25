# SPDX-License-Identifier: MIT
class_name SaveSession
extends RefCounted
## Immutable owned snapshot. Content hash and OS file identity are separate checks.

const Codec = preload("res://domain/career_save.gd")
var path: String
var identity: String
var sha256: String
var _bytes: PackedByteArray

static func digest(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()

static func from_reply(reply: Dictionary) -> Dictionary:
	if not reply.get("ok", false):
		return reply
	var payload: Variant = reply.get("bytes")
	if not payload is PackedByteArray:
		return {"ok": false, "message": "The protected read did not return save bytes."}
	var bytes: PackedByteArray = payload
	var analysis: Dictionary = Codec.inspect(bytes)
	if not analysis.get("ok", false):
		return analysis
	if bytes.size() != int(reply.get("size", -1)) or digest(bytes) != str(reply.get("sha256", "")).to_lower() or str(reply.get("identity", "")).is_empty():
		return {"ok": false, "message": "The protected read did not provide a matching content hash and file identity."}
	var session := SaveSession.new()
	session.path = str(reply.get("input", ""))
	session.identity = str(reply.identity)
	session.sha256 = digest(bytes)
	session._bytes = bytes.duplicate()
	return {"ok": true, "session": session}

func bytes() -> PackedByteArray:
	return _bytes.duplicate()

func analysis() -> Dictionary:
	return Codec.inspect(_bytes)

func prepare(selections: Dictionary) -> Dictionary:
	return Codec.preview(_bytes, selections)

func verify_publication(reply: Dictionary, prepared: PackedByteArray) -> Dictionary:
	if not reply.get("ok", false):
		return reply
	var payload: Variant = reply.get("bytes")
	if not payload is PackedByteArray:
		return {"ok": false, "may_have_output": true, "output": reply.get("output", ""),
			"message": "A copy may exist, but its verified bytes were not returned. Inspect it before use."}
	var actual: PackedByteArray = payload
	if actual != prepared or actual.size() != _bytes.size() or actual.size() != int(reply.get("size", -1)) or digest(actual) != str(reply.get("sha256", "")).to_lower() or not reply.get("original_verified", false) or not reply.get("verified", false):
		return {"ok": false, "may_have_output": true, "output": reply.get("output", ""),
			"message": "A copy may exist, but its bytes or original-file verification did not match. Inspect it before use."}
	return reply
