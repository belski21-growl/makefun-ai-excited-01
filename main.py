# SPDX-License-Identifier: MIT
"""ai-excited-01 entry: write the entry image to /output/entry.png.

The image is shipped in this repository as entry.png (a JPEG, named
entry.png per the competition rules: the file is told apart by its first
bytes). This program only copies it, byte for byte, so both graded runs
produce identical output. Standard library only, no network.

The copy is chunked (64 KiB) so memory use stays flat regardless of the
image size, and the output directory is created only when it is missing
or is a real directory -- anything else fails loudly instead of writing
into the wrong place.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
CHUNK_SIZE = 64 * 1024  # 64 KiB per read/write step
MAX_BYTES = 1024 * 1024  # competition limit: at most 1 MiB
JPEG_SOI = b"\xff\xd8"  # JPEG start-of-image marker
JPEG_EOI = b"\xff\xd9"  # JPEG end-of-image marker


def verify_jpeg(path: Path) -> None:
    """Check that path is a complete JPEG within the size limit.

    Reads only the head and tail of the file: the first two bytes must be
    the SOI marker, the last two bytes the EOI marker, and the size must
    not exceed MAX_BYTES. Raises ValueError on any mismatch so a corrupt
    or truncated image fails loudly instead of being submitted.
    """
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"{path} is {size} bytes, over the 1 MiB limit")
    if size < 4:
        raise ValueError(f"{path} is {size} bytes, too small to be a JPEG")
    with path.open("rb") as f:
        head = f.read(2)
        f.seek(-2, os.SEEK_END)
        tail = f.read(2)
    if head != JPEG_SOI:
        raise ValueError(f"{path} does not start with the JPEG SOI marker")
    if tail != JPEG_EOI:
        raise ValueError(f"{path} does not end with the JPEG EOI marker")



def fail(message: str) -> int:
    """Print an error to stderr and return a non-zero exit code."""
    print(f"ai-excited-01: error: {message}", file=sys.stderr)
    return 1


def prepare_output_dir(out_dir: Path) -> Path:
    """Return the output path, creating the directory when needed.

    Refuses to proceed when the path exists but is not a directory, so a
    stray file at the output location can never be silently overwritten.
    """
    if out_dir.exists() and not out_dir.is_dir():
        raise NotADirectoryError(f"output path is not a directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "entry.png"


def copy_chunked(src: Path, dst: Path) -> int:
    """Copy src to dst in CHUNK_SIZE blocks; return the bytes copied."""
    total = 0
    with src.open("rb") as fin, dst.open("wb") as fout:
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            fout.write(chunk)
            total += len(chunk)
    return total


def main() -> int:
    if not SRC.is_file():
        return fail(f"entry image missing: {SRC}")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        verify_jpeg(SRC)  # source must be a complete JPEG before copying
        out_path = prepare_output_dir(out_dir)
        copied = copy_chunked(SRC, out_path)
        verify_jpeg(out_path)  # output must be a complete JPEG after copying
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    if copied != SRC.stat().st_size:
        return fail(
            f"short copy: wrote {copied} bytes, expected {SRC.stat().st_size}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
