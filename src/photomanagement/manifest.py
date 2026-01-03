from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .config import Manifest, MediaRecord, PipelineConfig
from .hashers import perceptual_hash, sha256_file
from .metadata import capture_metadata, media_type_for


SCHEMA = """
CREATE TABLE IF NOT EXISTS manifest (
    path TEXT PRIMARY KEY,
    size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    perceptual_hash TEXT,
    media_type TEXT NOT NULL,
    capture_date TEXT,
    capture_confidence TEXT
);
"""


def ensure_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute(SCHEMA)
    connection.commit()
    return connection


def _store_record(connection: sqlite3.Connection, record: MediaRecord) -> None:
    connection.execute(
        """
        INSERT OR REPLACE INTO manifest(path, size, sha256, perceptual_hash, media_type, capture_date, capture_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(record.path),
            record.size,
            record.sha256,
            record.perceptual_hash,
            record.media_type,
            record.capture.capture_date,
            record.capture.confidence,
        ),
    )


def scan_paths(paths: Iterable[Path], config: PipelineConfig) -> Manifest:
    manifest = Manifest()
    for path in paths:
        if path.is_dir():
            continue
        media_type = media_type_for(path)
        if media_type == "unknown":
            continue

        record = MediaRecord(
            path=path,
            size=path.stat().st_size,
            sha256=sha256_file(path),
            perceptual_hash=perceptual_hash(path) if config.perceptual_hash else None,
            media_type=media_type,
            capture=capture_metadata(path),
        )
        manifest.add(record)
    return manifest


def scan_directory(root: Path, config: PipelineConfig) -> Manifest:
    paths = root.rglob("*") if config.follow_symlinks else (p for p in root.rglob("*") if not p.is_symlink())
    return scan_paths(paths, config)


def persist_manifest(manifest: Manifest, connection: sqlite3.Connection) -> None:
    for record in manifest.records:
        _store_record(connection, record)
    connection.commit()
