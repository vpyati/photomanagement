from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .config import PipelineConfig
from .deduplicate import find_exact_duplicates, find_near_duplicates
from .manifest import ensure_database, persist_manifest, scan_directory, scan_paths
from .organizer import apply_plan, build_plan


def execute(config: PipelineConfig) -> dict[str, str]:
    """Run the full pipeline and return human-readable summaries."""

    summaries: dict[str, str] = {}
    connection = ensure_database(config.database_path)

    manifest = scan_directory(config.source_root, config)
    persist_manifest(manifest, connection)

    duplicates = list(find_exact_duplicates(manifest))
    near_duplicates = list(find_near_duplicates(manifest, config))

    organization_plan = build_plan(manifest.records, config.destination_root)
    apply_plan(organization_plan, dry_run=config.dry_run)

    summaries["manifest"] = f"Scanned {len(manifest.records)} media files"
    summaries["duplicates"] = f"Found {len(duplicates)} duplicate groups"
    summaries["near_duplicates"] = f"Found {len(near_duplicates)} near-duplicate anchors"
    summaries["organization"] = f"Planned {len(organization_plan)} copy operations"
    return summaries


def batch_execute(config: PipelineConfig, batches: Iterable[List[Path]]) -> list[dict[str, str]]:
    """Process batches of paths to limit memory use."""

    results: list[dict[str, str]] = []
    connection = ensure_database(config.database_path)
    for batch_paths in batches:
        manifest = scan_paths(batch_paths, config)
        persist_manifest(manifest, connection)
        duplicates = list(find_exact_duplicates(manifest))
        near_duplicates = list(find_near_duplicates(manifest, config))
        organization_plan = build_plan(manifest.records, config.destination_root)
        apply_plan(organization_plan, dry_run=config.dry_run)
        results.append(
            {
                "manifest": f"Scanned {len(manifest.records)} media files",
                "duplicates": f"Found {len(duplicates)} duplicate groups",
                "near_duplicates": f"Found {len(near_duplicates)} near-duplicate anchors",
                "organization": f"Planned {len(organization_plan)} copy operations",
            }
        )
    return results
