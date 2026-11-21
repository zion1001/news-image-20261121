#!/usr/bin/env python3
"""Copy the front-page image to the grader's output directory.

The entry is a program that writes one image to /output/entry.png.
The image itself lives in this repository as entry.png; this program
copies it to $MAKEFUN_OUTPUT_DIR (default /output). Standard library
only, no network.
"""

import os
import sys
import tempfile

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        with open(src, "rb") as f:
            data = f.read()
    except OSError as exc:
        print(f"error: cannot read {src}: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not data.startswith(PNG_MAGIC):
        print("error: entry.png is not a PNG file", file=sys.stderr)
        raise SystemExit(1)
    # Atomic write: write a temp file in the output dir, then rename.
    # mkstemp creates the temp file mode 0600; the grader reads the
    # output as a different user, so make it world-readable before the
    # rename (round 1 failed run_completes with a 0600 output file).
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".png")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, dest)
    except OSError as exc:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        print(f"error: cannot write {dest}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
