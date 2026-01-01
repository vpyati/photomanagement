from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import MediaRecord


THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "birthday": ("birthday", "bday", "turning"),
    "wedding": ("wedding", "bride", "groom", "marriage"),
    "graduation": ("graduation", "grad", "commencement"),
    "holiday": ("christmas", "xmas", "halloween", "diwali", "eid"),
    "travel": ("vacation", "holiday", "trip", "beach", "hike"),
}


@dataclass(slots=True)
class ThemeLabel:
    record: MediaRecord
    labels: list[str]


def label_by_filename(records: Iterable[MediaRecord]) -> list[ThemeLabel]:
    labeled: list[ThemeLabel] = []
    for record in records:
        name = record.path.name.lower()
        labels = [theme for theme, keywords in THEME_KEYWORDS.items() if any(keyword in name for keyword in keywords)]
        labeled.append(ThemeLabel(record=record, labels=labels))
    return labeled


def summarize_labels(labels: Iterable[ThemeLabel]) -> str:
    lines = ["Theme labels (filename heuristics):"]
    for label in labels:
        theme_list = ", ".join(label.labels) if label.labels else "unlabeled"
        lines.append(f"- {label.record.path}: {theme_list}")
    return "\n".join(lines)
