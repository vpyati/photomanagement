# photomanagement

Local-first Python toolkit for deduplicating and organizing large photo/video libraries using SHA-256 hashes, perceptual hashes, EXIF dates, and lightweight heuristics. It is inspired by the earlier plan to scan ~2 TB of media without incurring cloud costs.

## Features
- **Manifest builder**: stream files, compute SHA-256 hashes, and store metadata in SQLite.
- **Duplicate detection**: exact matches by content hash and near-duplicates via perceptual hashing for images.
- **Date-based organization**: derive capture dates from EXIF when available, then fall back to filesystem timestamps to place files under `YYYY/MM/` folders.
- **Theme hints**: simple filename-based labels (e.g., birthday, wedding, travel) to seed later clustering.
- **CLI workflow**: scan, report duplicates, plan/copy organization, and labeling in a dry-run-friendly manner.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[cli]
```

## Usage
The CLI expects a source directory and an output directory. The default mode is safe-by-default (dry-run for organization; scanning never deletes files).

### Build or refresh a manifest
```bash
photomanagement /path/to/source /path/to/output scan --database .cache/photomanagement.sqlite
```

### Report duplicates and near-duplicates
```bash
photomanagement /path/to/source /path/to/output duplicates --threshold 6
```

### Plan organization (dry-run) or copy files
```bash
photomanagement /path/to/source /path/to/output organize --dry-run
# Remove --dry-run to actually copy with metadata preserved
```

### Apply filename-based labels
```bash
photomanagement /path/to/source /path/to/output classify
```

## Notes
- Perceptual hashing is skipped automatically for files Pillow cannot read; videos currently rely on exact hashes.
- All operations avoid mutating the source directory. The SQLite manifest can be inspected or backed up for auditing.
- The project is modular—extend `classify.py` for embedding-based labeling or `organizer.py` for more elaborate folder schemes.
