from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

from PIL import ExifTags, Image

from .config import CaptureMetadata


def _read_exif_datetime(path: Path) -> Optional[str]:
    try:
        with Image.open(path) as image:
            exif_data = image._getexif() or {}
    except OSError:
        return None

    lookup = {ExifTags.TAGS.get(tag, str(tag)): value for tag, value in exif_data.items()}
    value = lookup.get("DateTimeOriginal") or lookup.get("DateTime")
    if not value:
        return None

    value = value.strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d"):
        try:
            parsed = dt.datetime.strptime(value, fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    return None


def _filesystem_date(path: Path) -> str:
    timestamp = path.stat().st_mtime
    return dt.date.fromtimestamp(timestamp).isoformat()


def capture_metadata(path: Path) -> CaptureMetadata:
    capture_date = _read_exif_datetime(path)
    confidence = "exif" if capture_date else "filesystem"
    if not capture_date:
        capture_date = _filesystem_date(path)
    return CaptureMetadata(capture_date=capture_date, confidence=confidence)


def media_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".heic", ".webp", ".tiff"}:
        return "image"
    if suffix in {".mp4", ".mov", ".avi", ".mkv"}:
        return "video"
    return "unknown"
