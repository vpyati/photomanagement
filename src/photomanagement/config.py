from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class PipelineConfig:
    """Configuration for processing a media library."""

    source_root: Path
    destination_root: Path
    database_path: Path
    perceptual_hash: bool = True
    video_frame_stride: int = 10
    near_duplicate_threshold: int = 6
    follow_symlinks: bool = False
    manifest_batch_size: int = 128
    dry_run: bool = True


@dataclass(slots=True)
class CaptureMetadata:
    """Capture-related metadata for a media asset."""

    capture_date: Optional[str]
    camera_model: Optional[str] = None
    location: Optional[str] = None
    confidence: str = "unknown"


@dataclass(slots=True)
class MediaRecord:
    """Normalized representation of a scanned media file."""

    path: Path
    size: int
    sha256: str
    perceptual_hash: Optional[str]
    media_type: str
    capture: CaptureMetadata
    duplicate_group: Optional[str] = None
    near_duplicate_group: Optional[str] = None

    def target_subpath(self) -> Path:
        """Generate a target subpath based on capture metadata and filename."""

        year = "unknown"
        month = "unknown"
        if self.capture.capture_date:
            parts = self.capture.capture_date.split("-")
            if len(parts) >= 2:
                year, month = parts[0], parts[1]
            elif len(parts) == 1:
                year = parts[0]
        return Path(year) / month / self.path.name


@dataclass(slots=True)
class Manifest:
    """Container for scanned media records."""

    records: list[MediaRecord] = field(default_factory=list)

    def add(self, record: MediaRecord) -> None:
        self.records.append(record)

    def by_hash(self) -> dict[str, list[MediaRecord]]:
        groups: dict[str, list[MediaRecord]] = {}
        for record in self.records:
            groups.setdefault(record.sha256, []).append(record)
        return groups

    def by_perceptual_hash(self) -> dict[str, list[MediaRecord]]:
        groups: dict[str, list[MediaRecord]] = {}
        for record in self.records:
            if record.perceptual_hash:
                groups.setdefault(record.perceptual_hash, []).append(record)
        return groups
