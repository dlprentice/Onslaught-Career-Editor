"""Backup-safe manager for Battle Engine Aquila cardid.txt modern preset block."""

from __future__ import annotations

from pathlib import Path

BEGIN_MARKER = "// BEGIN OCE_PRESET_MODERN"
END_MARKER = "// END OCE_PRESET_MODERN"
BACKUP_SUFFIX = ".original.backup"

STATE_ABSENT = "absent"
STATE_APPLIED = "applied"
STATE_CUSTOM_MANAGED = "custom managed block"
STATE_MALFORMED = "malformed markers"


def modern_block() -> str:
    return "\n".join(
        [
            BEGIN_MARKER,
            "// Managed by cardid_preset core (Onslaught Toolkit)",
            "// Stable companion lane: modern high-quality tweak defaults.",
            "Tweak:GEFORCE_FX_POWER 1",
            "Tweak:SRT_ENABLE 1",
            "Tweak:IMPOSTOR_ENABLE 1",
            "Tweak:LANDSCAPE_LIGHTING 1",
            "Tweak:SNOW_ENABLE 1",
            "Tweak:GEFORCE_PARTICLE_FOG 1",
            END_MARKER,
            "",
        ]
    )


def build_backup_path(cardid_path: Path) -> Path:
    return Path(str(cardid_path) + BACKUP_SUFFIX)


def _normalize_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _managed_block_bounds(text: str) -> tuple[bool, int, int, str]:
    start = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)

    if start < 0 or end < 0:
        return False, -1, -1, "managed markers not both present"
    if end < start:
        return False, -1, -1, "END marker appears before BEGIN marker"

    end_after = end + len(END_MARKER)
    while end_after < len(text) and text[end_after] in "\r\n":
        end_after += 1

    return True, start, end_after, ""


def get_state(text: str) -> str:
    has_begin = BEGIN_MARKER in text
    has_end = END_MARKER in text

    if not has_begin and not has_end:
        return STATE_ABSENT
    if has_begin != has_end:
        return STATE_MALFORMED

    ok, start, end_after, _ = _managed_block_bounds(text)
    if not ok:
        return STATE_MALFORMED

    current = text[start:end_after]
    if _normalize_newlines(current) == _normalize_newlines(modern_block()):
        return STATE_APPLIED
    return STATE_CUSTOM_MANAGED


def verify_file(cardid_path: Path) -> tuple[bool, str, str]:
    if not cardid_path.exists():
        return False, "Select a valid cardid.txt path first.", STATE_ABSENT

    text = cardid_path.read_text(encoding="utf-8", errors="replace")
    state = get_state(text)
    if state == STATE_ABSENT:
        msg = "Managed modern preset block is not present in cardid.txt."
    elif state == STATE_APPLIED:
        msg = "Managed modern preset block is present and current."
    elif state == STATE_CUSTOM_MANAGED:
        msg = "Managed markers found, but block content differs from current preset."
    else:
        msg = "Malformed managed markers found (missing BEGIN or END partner)."
    return True, msg, state


def apply_modern_preset(cardid_path: Path) -> tuple[bool, str]:
    if not cardid_path.exists():
        return False, "Select a valid cardid.txt path first."

    original = cardid_path.read_text(encoding="utf-8", errors="replace")
    state = get_state(original)
    if state == STATE_MALFORMED:
        return (
            False,
            "Apply aborted: malformed managed markers detected in cardid.txt. "
            "Restore from backup or fix markers first.",
        )

    ok, start, end_after, _ = _managed_block_bounds(original)
    if ok:
        updated = original[:start] + modern_block() + original[end_after:]
        action = "replaced"
    else:
        sep = "" if original.endswith("\n") else "\n"
        updated = original + sep + modern_block()
        action = "appended"

    if _normalize_newlines(updated) == _normalize_newlines(original):
        return True, "No changes needed: managed modern preset block is already current."

    backup = build_backup_path(cardid_path)
    if not backup.exists():
        backup.write_bytes(cardid_path.read_bytes())

    cardid_path.write_text(updated, encoding="utf-8")
    return (
        True,
        "cardid.txt preset apply complete.\n"
        f"Target: {cardid_path}\n"
        f"Backup: {backup}\n"
        f"Action: {action}",
    )


def restore_from_backup(cardid_path: Path) -> tuple[bool, str]:
    if not cardid_path.exists():
        return False, "Select a valid cardid.txt path first."

    backup = build_backup_path(cardid_path)
    if not backup.exists():
        return False, f"Backup file not found: {backup}"

    cardid_path.write_bytes(backup.read_bytes())
    return (
        True,
        "Restore complete.\n"
        f"Target: {cardid_path}\n"
        f"Backup source: {backup}",
    )
