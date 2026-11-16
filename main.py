# SPDX-License-Identifier: MIT
"""Ship the ai-excited-01 entry image to the grading output directory.

The picture in this repository is called ``entry.png`` but is really a
JPEG -- the competition judges format by leading bytes, not by the name.
This program streams those bytes untouched to
``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output`` when the variable is not
set). Nothing is downloaded, nothing is random, nothing is decoded, so
the two graded runs produce byte-identical files.

The copy is checked twice: the source is proven to be a complete JPEG
before anything moves, and the destination is proven the same afterwards,
with the byte counts compared. The output directory is guarded as well --
it has to be a real directory, and it may only hold a previous copy of
the entry, so an unrelated folder can never be clobbered.
"""

import os
import sys
from pathlib import Path

OUTPUT_NAME = "entry.png"
CHUNK = 65536                # 64 KiB per read/write step
MAX_BYTES = 1_048_576        # competition limit: 1 MiB, inclusive
SOI = b"\xff\xd8"            # JPEG start-of-image marker
EOI = b"\xff\xd9"            # JPEG end-of-image marker
BASE = Path(__file__).resolve().parent


class Problem(Exception):
    """Something that must stop the run with a clear message."""


def fail(message):
    """Print *message* on stderr and return a non-zero exit code."""
    print(f"ai-excited-01: error: {message}", file=sys.stderr)
    return 1


def output_path():
    """Decide where the entry image has to land and prepare that folder.

    Returns the destination path. A missing folder is created; a path
    that is not a directory, or a directory holding anything but a
    previous entry.png, is refused with a Problem.
    """
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    if folder.exists() and not folder.is_dir():
        raise Problem(f"output path is not a directory: {folder}")
    if folder.is_dir():
        foreign = sorted(
            p.name for p in folder.iterdir() if p.name != OUTPUT_NAME
        )
        if foreign:
            raise Problem(
                f"output directory {folder} is not empty: it holds "
                f"{', '.join(foreign)}; refusing to write there so "
                "nothing unrelated is overwritten"
            )
    folder.mkdir(parents=True, exist_ok=True)
    return folder / OUTPUT_NAME


def jpeg_markers(path):
    """Read the head and the tail of *path*.

    Returns a (first_two_bytes, last_two_bytes) tuple. Callers check
    the size first, so the file is always at least 4 bytes here and
    the backwards seek is safe.
    """
    with path.open("rb") as handle:
        head = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        tail = handle.read(2)
    return head, tail


def assert_jpeg(path):
    """Prove *path* is a complete JPEG inside the size cap.

    Returns the file size in bytes. The size is checked before any
    read, so a truncated file is refused with a clear reason instead
    of a raw seek error.
    """
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise Problem(
            f"{path} is {size} bytes, over the 1 MiB limit ({MAX_BYTES})"
        )
    if size < 4:
        raise Problem(
            f"{path} is {size} bytes, too small to be a JPEG "
            "(needs at least 4 bytes: SOI plus EOI markers)"
        )
    head, tail = jpeg_markers(path)
    if head != SOI:
        raise Problem(
            f"{path} does not start with the JPEG SOI marker: found "
            f"bytes {head.hex()} (expected ffd8); the file is not a "
            "JPEG, or it is cut off at the start"
        )
    if tail != EOI:
        raise Problem(
            f"{path} does not end with the JPEG EOI marker: found "
            f"bytes {tail.hex()} (expected ffd9); the file is cut off "
            "at the end"
        )
    return size


def transfer(source, destination):
    """Stream *source* to *destination* in CHUNK steps.

    Returns the number of bytes written. The file is never held in
    memory whole, so the footprint stays flat at any image size.
    """
    total = 0
    with source.open("rb") as reader, destination.open("wb") as writer:
        while True:
            block = reader.read(CHUNK)
            if not block:
                break
            writer.write(block)
            total += len(block)
    return total


def confirm_destination(path, expected):
    """Prove the copy at *path* is whole and the right size.

    Re-validates the destination as a complete JPEG and compares its
    size against *expected* (the source size). A short or damaged copy
    is refused with a Problem instead of silently passing.
    """
    actual = assert_jpeg(path)
    if actual != expected:
        raise Problem(
            f"short copy: destination is {actual} bytes, "
            f"expected {expected}"
        )
    return actual


def main():
    """Copy the entry image, verified before and after. Returns 0 on success."""
    source = BASE / OUTPUT_NAME
    if not source.is_file():
        return fail(
            f"entry image missing: expected {source} next to main.py; "
            "the repository must ship entry.png beside this program"
        )
    try:
        expected = assert_jpeg(source)
        destination = output_path()
        transfer(source, destination)
        confirm_destination(destination, expected)
    except (OSError, Problem) as problem:
        return fail(str(problem))
    return 0


if __name__ == "__main__":
    sys.exit(main())
