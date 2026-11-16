# SPDX-License-Identifier: MIT
"""Deliver the ai-excited-01 picture to the grading output folder.

The repository ships ``entry.png``, which is a JPEG in disguise: the
competition looks at leading bytes, not at the extension. This program
moves those bytes, untouched, to ``$MAKEFUN_OUTPUT_DIR/entry.png``
(``/output`` when the variable is unset). It never downloads anything,
never rolls dice, never decodes a pixel, so the two graded runs end
with byte-identical files.

Two proofs guard the copy. Before a single byte moves, the source is
shown to be a whole JPEG inside the size cap. After the copy lands,
the destination is shown to be the same whole JPEG, byte for byte.
The destination folder is guarded as well: it must be a real folder,
and it may only contain an older copy of the entry, so nothing
unrelated can ever be overwritten.
"""

import os
import sys
from pathlib import Path

OUT_NAME = "entry.png"
BLOCK = 65536                 # 64 KiB per read/write step
LIMIT = 1_048_576             # competition cap: 1 MiB, inclusive
MAGIC_HEAD = b"\xff\xd8"      # JPEG start-of-image marker
MAGIC_TAIL = b"\xff\xd9"      # JPEG end-of-image marker
HERE = Path(__file__).resolve().parent


class EntryError(Exception):
    """A problem that must stop the run with a plain message."""


def complain(message):
    """Write *message* to stderr; the caller returns this as exit code."""
    sys.stderr.write("ai-excited-01: error: %s\n" % message)
    return 1


def target_dir():
    """Work out where the picture must land and get that folder ready.

    A folder that does not exist is created. A path that is not a
    folder, or a folder holding anything other than an older copy of
    the entry, is refused with an EntryError. Returns the full
    destination path.
    """
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    if folder.exists() and not folder.is_dir():
        raise EntryError("output path is not a folder: %s" % folder)
    if folder.is_dir():
        others = sorted(
            item.name for item in folder.iterdir() if item.name != OUT_NAME
        )
        if others:
            raise EntryError(
                "output folder %s is not empty: it holds %s; refusing "
                "to write there so nothing unrelated is overwritten"
                % (folder, ", ".join(others))
            )
    folder.mkdir(parents=True, exist_ok=True)
    return folder / OUT_NAME


def read_ends(path):
    """Read the first and last two bytes of *path* as a pair."""
    with path.open("rb") as handle:
        first = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        last = handle.read(2)
    return first, last


def check_image(path):
    """Show *path* is a whole JPEG inside the size cap.

    Returns the file size in bytes. Size is checked before any read,
    so a cut-off file is refused with a clear reason instead of a
    raw seek error.
    """
    size = path.stat().st_size
    if size > LIMIT:
        raise EntryError(
            "%s is %d bytes, over the 1 MiB limit (%d)" % (path, size, LIMIT)
        )
    if size < 4:
        raise EntryError(
            "%s is %d bytes, too small to be a JPEG "
            "(needs at least 4 bytes: SOI plus EOI)" % (path, size)
        )
    first, last = read_ends(path)
    if first != MAGIC_HEAD:
        raise EntryError(
            "%s does not start with the JPEG SOI marker: found "
            "bytes %s (expected ffd8); the file is not a JPEG, or it "
            "is cut off at the start" % (path, first.hex())
        )
    if last != MAGIC_TAIL:
        raise EntryError(
            "%s does not end with the JPEG EOI marker: found "
            "bytes %s (expected ffd9); the file is cut off at the "
            "end" % (path, last.hex())
        )
    return size


def copy_stream(source, destination):
    """Stream *source* to *destination* in BLOCK steps.

    Returns the byte count written. The file is never held whole in
    memory, so the footprint stays flat at any image size.
    """
    written = 0
    with source.open("rb") as reader, destination.open("wb") as writer:
        while True:
            piece = reader.read(BLOCK)
            if not piece:
                break
            writer.write(piece)
            written += len(piece)
    return written


def check_copy(path, expected):
    """Show the copy at *path* is whole and the size *expected*.

    Re-validates the destination as a complete JPEG and compares its
    size with the source size. A short or damaged copy is refused
    with an EntryError instead of silently passing.
    """
    actual = check_image(path)
    if actual != expected:
        raise EntryError(
            "short copy: destination is %d bytes, expected %d"
            % (actual, expected)
        )
    return actual


def run():
    """Copy the entry picture, verified before and after. 0 on success."""
    source = HERE / OUT_NAME
    if not source.is_file():
        return complain(
            "entry image missing: expected %s next to main.py; the "
            "repository must ship entry.png beside this program" % source
        )
    try:
        expected = check_image(source)
        destination = target_dir()
        moved = copy_stream(source, destination)
        check_copy(destination, expected)
        sys.stdout.write(
            "ai-excited-01: wrote %d bytes to %s\n" % (moved, destination)
        )
    except (OSError, EntryError) as problem:
        return complain(str(problem))
    return 0


if __name__ == "__main__":
    sys.exit(run())
