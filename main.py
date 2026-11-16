# SPDX-License-Identifier: MIT
"""Write the ai-excited-01 entry image to the grading output directory.

The picture lives in this repository as ``entry.png``. Judging by its
first bytes it is a JPEG wearing a ``.png`` name, which the competition
allows: the format is decided by the leading bytes, not the extension.

This script does one job and nothing else: it streams those exact bytes
to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output`` when the variable is
unset). No network, no randomness, no decoding, no re-encoding -- the two
graded runs therefore land on byte-identical files.

Two safety nets bracket the transfer. Before a single byte moves, the
source is checked for a whole JPEG (start marker, end marker, size
within the 1 MiB cap). After the transfer the destination is checked the
same way, and the byte counts are compared. The destination folder is
also guarded: it must be a real directory, and it must hold nothing but
a previous ``entry.png``, so an unrelated folder can never be clobbered.
"""

import os
import sys
from pathlib import Path

IMAGE_NAME = "entry.png"
BLOCK_BYTES = 65536          # 64 KiB per read/write step
SIZE_CAP = 1_048_576         # competition limit: 1 MiB, inclusive
JPEG_START = b"\xff\xd8"     # JPEG start-of-image marker
JPEG_END = b"\xff\xd9"       # JPEG end-of-image marker
HERE = Path(__file__).resolve().parent


class EntryError(Exception):
    """A problem that must stop the run with a clear message."""


def die(message):
    """Report *message* on stderr and exit non-zero."""
    print("ai-excited-01: error: " + message, file=sys.stderr)
    return 1


def destination_for():
    """Work out where the entry image has to land.

    Returns the full destination path. The directory is created when it
    does not exist yet; a path that exists but is not a directory, or a
    directory holding files other than a previous entry.png, is refused
    with an EntryError so nothing unrelated is ever overwritten.
    """
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    if target_dir.exists() and not target_dir.is_dir():
        raise EntryError("output path is not a directory: %s" % target_dir)
    if target_dir.is_dir():
        strangers = sorted(
            child.name for child in target_dir.iterdir()
            if child.name != IMAGE_NAME
        )
        if strangers:
            raise EntryError(
                "output directory %s is not empty: it holds %s; refusing "
                "to write there so nothing unrelated is overwritten"
                % (target_dir, ", ".join(strangers))
            )
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / IMAGE_NAME


def check_jpeg(path):
    """Confirm *path* is a whole JPEG inside the size cap.

    Only the head and the tail are read: the file must open with the SOI
    marker, close with the EOI marker, and stay within SIZE_CAP bytes.
    Anything else raises EntryError with the reason spelled out.
    """
    size = path.stat().st_size
    if size > SIZE_CAP:
        raise EntryError(
            "%s is %d bytes, over the 1 MiB limit (%d)"
            % (path, size, SIZE_CAP)
        )
    if size < 4:
        raise EntryError(
            "%s is %d bytes, too small to be a JPEG "
            "(needs at least 4 bytes: SOI plus EOI markers)" % (path, size)
        )
    with path.open("rb") as handle:
        first = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        last = handle.read(2)
    if first != JPEG_START:
        raise EntryError(
            "%s does not start with the JPEG SOI marker: found bytes %s "
            "(expected ffd8); the file is not a JPEG, or it is cut off "
            "at the start" % (path, first.hex())
        )
    if last != JPEG_END:
        raise EntryError(
            "%s does not end with the JPEG EOI marker: found bytes %s "
            "(expected ffd9); the file is cut off at the end"
            % (path, last.hex())
        )
    return size


def stream_copy(source, destination):
    """Move *source* to *destination* in BLOCK_BYTES steps.

    Returns the number of bytes written. The file is never held in
    memory whole, so the memory footprint stays flat at any image size.
    """
    written = 0
    with source.open("rb") as reader, destination.open("wb") as writer:
        while True:
            block = reader.read(BLOCK_BYTES)
            if not block:
                break
            writer.write(block)
            written += len(block)
    return written


def run():
    """Copy the entry image, verified before and after. Returns 0 on success."""
    source = HERE / IMAGE_NAME
    if not source.is_file():
        return die(
            "entry image missing: expected %s next to main.py; the "
            "repository must ship entry.png beside this program" % source
        )
    try:
        expected = check_jpeg(source)
        destination = destination_for()
        written = stream_copy(source, destination)
        check_jpeg(destination)
    except (OSError, EntryError) as problem:
        return die(str(problem))
    if written != expected:
        return die(
            "short copy: wrote %d bytes, expected %d" % (written, expected)
        )
    return 0


if __name__ == "__main__":
    sys.exit(run())
