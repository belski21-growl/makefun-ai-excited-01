# SPDX-License-Identifier: MIT
"""ai-excited-01 entry: write the entry image to /output/entry.png.

The image is shipped in this repository as entry.png (a JPEG, named
entry.png per the competition rules: the file is told apart by its first
bytes). This program only copies it, byte for byte, so both graded runs
produce identical output. Standard library only, no network.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    shutil.copyfile(SRC, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
