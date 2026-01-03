from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from PIL import Image


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Stream a file and return its SHA-256 hash."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def perceptual_hash(path: Path, hash_size: int = 16) -> Optional[str]:
    """Compute a lightweight average hash for an image.

    Returns ``None`` when the file cannot be parsed as an image.
    """

    try:
        with Image.open(path) as image:
            image = image.convert("L").resize((hash_size, hash_size))
            pixels = list(image.getdata())
    except OSError:
        return None

    average = sum(pixels) / len(pixels)
    bits = ["1" if pixel >= average else "0" for pixel in pixels]
    return hex(int("".join(bits), 2))[2:].zfill(hash_size * hash_size // 4)


def hamming_distance(first: str, second: str) -> int:
    """Compute the Hamming distance between two hex-encoded hashes."""

    as_bits_first = bin(int(first, 16))[2:].zfill(len(first) * 4)
    as_bits_second = bin(int(second, 16))[2:].zfill(len(second) * 4)
    return sum(bit1 != bit2 for bit1, bit2 in zip(as_bits_first, as_bits_second))
