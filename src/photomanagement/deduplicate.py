from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

from .config import Manifest, MediaRecord, PipelineConfig
from .hashers import hamming_distance


@dataclass(slots=True)
class DuplicateGroup:
    key: str
    members: list[MediaRecord]


@dataclass(slots=True)
class NearDuplicateGroup:
    representative: MediaRecord
    members: list[MediaRecord]


def find_exact_duplicates(manifest: Manifest) -> Iterator[DuplicateGroup]:
    for key, items in manifest.by_hash().items():
        if len(items) > 1:
            yield DuplicateGroup(key=key, members=items)


def find_near_duplicates(manifest: Manifest, config: PipelineConfig) -> Iterator[NearDuplicateGroup]:
    groups = manifest.by_perceptual_hash()
    for _, items in groups.items():
        for index, anchor in enumerate(items):
            cluster = [candidate for i, candidate in enumerate(items) if i != index and hamming_distance(anchor.perceptual_hash or "", candidate.perceptual_hash or "") <= config.near_duplicate_threshold]
            if cluster:
                yield NearDuplicateGroup(representative=anchor, members=cluster)


def report_duplicates(duplicates: Iterable[DuplicateGroup]) -> str:
    lines = ["Exact duplicates:"]
    for group in duplicates:
        lines.append(f"- {len(group.members)} files share hash {group.key[:12]}…")
        for member in group.members:
            lines.append(f"  • {member.path} ({member.size} bytes)")
    return "\n".join(lines)


def report_near_duplicates(groups: Iterable[NearDuplicateGroup]) -> str:
    lines = ["Near duplicates:"]
    for group in groups:
        lines.append(f"- Representative: {group.representative.path}")
        for member in group.members:
            distance = hamming_distance(group.representative.perceptual_hash or "", member.perceptual_hash or "")
            lines.append(f"  • {member.path} (distance {distance})")
    return "\n".join(lines)
