from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from .config import MediaRecord, PipelineConfig


def build_plan(records: Iterable[MediaRecord], destination_root: Path) -> list[tuple[Path, Path]]:
    plan: list[tuple[Path, Path]] = []
    for record in records:
        target = destination_root / record.target_subpath()
        plan.append((record.path, target))
    return plan


def apply_plan(plan: list[tuple[Path, Path]], dry_run: bool = True) -> None:
    for source, target in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            continue
        shutil.copy2(source, target)


def summarize_plan(plan: list[tuple[Path, Path]]) -> str:
    lines = ["Organization plan:"]
    for source, target in plan:
        lines.append(f"- {source} -> {target}")
    return "\n".join(lines)
