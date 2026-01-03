from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .config import PipelineConfig
from .classify import label_by_filename, summarize_labels
from .deduplicate import find_exact_duplicates, find_near_duplicates, report_duplicates, report_near_duplicates
from .manifest import ensure_database, persist_manifest, scan_directory
from .organizer import build_plan, summarize_plan, apply_plan


def _build_config(args: argparse.Namespace) -> PipelineConfig:
    return PipelineConfig(
        source_root=Path(args.source).expanduser(),
        destination_root=Path(args.destination).expanduser(),
        database_path=Path(args.database).expanduser(),
        perceptual_hash=not args.skip_phash,
        near_duplicate_threshold=args.threshold,
        follow_symlinks=args.follow_symlinks,
        dry_run=args.dry_run,
    )


def cmd_scan(args: argparse.Namespace) -> None:
    config = _build_config(args)
    connection = ensure_database(config.database_path)
    manifest = scan_directory(config.source_root, config)
    persist_manifest(manifest, connection)
    print(f"Scanned {len(manifest.records)} media files")


def cmd_duplicates(args: argparse.Namespace) -> None:
    config = _build_config(args)
    manifest = scan_directory(Path(args.source), config)
    duplicates = list(find_exact_duplicates(manifest))
    near_duplicates = list(find_near_duplicates(manifest, config))
    print(report_duplicates(duplicates))
    print()
    print(report_near_duplicates(near_duplicates))


def cmd_organize(args: argparse.Namespace) -> None:
    config = _build_config(args)
    manifest = scan_directory(config.source_root, config)
    plan = build_plan(manifest.records, config.destination_root)
    print(summarize_plan(plan))
    apply_plan(plan, dry_run=config.dry_run)
    if config.dry_run:
        print("Dry-run enabled: no files were copied.")


def cmd_classify(args: argparse.Namespace) -> None:
    config = _build_config(args)
    manifest = scan_directory(config.source_root, config)
    labels = label_by_filename(manifest.records)
    print(summarize_labels(labels))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deduplicate and organize a media library")
    parser.add_argument("source", help="Path to source media directory")
    parser.add_argument("destination", help="Path to organized output directory")
    parser.add_argument("--database", default=".cache/photomanagement.sqlite", help="Path to SQLite database for manifest")
    parser.add_argument("--skip-phash", action="store_true", help="Skip perceptual hashing to speed up scans")
    parser.add_argument("--threshold", type=int, default=6, help="Hamming distance threshold for near-duplicate detection")
    parser.add_argument("--follow-symlinks", action="store_true", help="Include symlinks during scanning")
    parser.add_argument("--dry-run", action="store_true", help="Plan organization without copying files")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    scan_parser = subparsers.add_parser("scan", help="Build or refresh the manifest database")
    scan_parser.set_defaults(func=cmd_scan)

    dup_parser = subparsers.add_parser("duplicates", help="Report duplicates and near-duplicates")
    dup_parser.set_defaults(func=cmd_duplicates)

    org_parser = subparsers.add_parser("organize", help="Plan and optionally copy files into date folders")
    org_parser.set_defaults(func=cmd_organize)

    classify_parser = subparsers.add_parser("classify", help="Apply lightweight filename-based labels")
    classify_parser.set_defaults(func=cmd_classify)

    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
