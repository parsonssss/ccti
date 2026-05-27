#!/usr/bin/env python3
"""
Open an image with the OS default viewer. Cross-platform.

Usage:
    python open_image.py <image-path>
"""
import os
import subprocess
import sys
from pathlib import Path


def open_image(path: Path) -> None:
    if not path.exists():
        sys.stderr.write(f"[ccti/open_image] File not found: {path}\n")
        sys.exit(1)

    plat = sys.platform

    try:
        if plat == "darwin":
            # macOS — `open` always works and uses the default viewer (Preview).
            subprocess.run(["open", str(path)], check=True)
        elif plat.startswith("win"):
            # Windows — os.startfile is the native way; uses default associated viewer.
            # (Image apps like Photos / Paint / IrfanView depending on user setting.)
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            # Linux / BSD — xdg-open is the freedesktop standard.
            # Fallbacks for slim installs:
            for opener in ("xdg-open", "gio open", "gvfs-open", "kde-open5", "kde-open"):
                parts = opener.split()
                try:
                    subprocess.run(parts + [str(path)], check=True)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            else:
                sys.stderr.write(
                    "[ccti/open_image] Could not find xdg-open / gio / kde-open.\n"
                    f"Please open the image manually: {path}\n"
                )
                sys.exit(2)
    except Exception as exc:
        sys.stderr.write(f"[ccti/open_image] Failed to open: {exc}\n")
        sys.exit(3)

    print(f"[ccti/open_image] Opened {path}")


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: open_image.py <image-path>\n")
        sys.exit(1)
    open_image(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
