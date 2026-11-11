"""Notification bitmap configuration for beanOS.

This module intentionally keeps only metadata and file paths so importing it
never allocates large bitmap buffers in RAM.
"""

try:
    import uos as _os
except ImportError:
    import os as _os

WIDTH = 296
HEIGHT = 128
BYTES_PER_ROW = 37
EXPECTED_BITMAP_SIZE = BYTES_PER_ROW * HEIGHT

_NOTIFICATION_BITMAP_FILES = {
    "achievement": (
        "achievement_296x128.bin",
        "achievements_296x128.bin",
        "achievement.bin",
    ),
    "bean_pack": (
        "bean_pack_296x128.bin",
        "beans_296x128.bin",
        "beans.bin",
    ),
    "maintenance": (
        "maintenance_296x128.bin",
        "elektra_296x128.bin",
        "maintenance.bin",
    ),
}


def _path_exists(path):
    try:
        _os.stat(path)
        return True
    except Exception:
        return False


def get_notification_bitmap_file(notification_type):
    """Return filesystem path for the given notification background."""
    file_names = _NOTIFICATION_BITMAP_FILES.get(notification_type)
    if not file_names:
        return None

    for file_name in file_names:
        candidates = (
            "/images/" + file_name,
            "images/" + file_name,
            "/images/pixelart/" + file_name,
            "images/pixelart/" + file_name,
        )

        for path in candidates:
            if _path_exists(path):
                return path
    return None
