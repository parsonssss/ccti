#!/usr/bin/env python3
"""
Render an HTML file to a PNG screenshot using whatever headless-capable
Chromium-family browser the system has.

Cross-platform: tries known install paths on macOS / Windows / Linux,
falls back to PATH lookup. Exits non-zero with a clear message if
nothing usable is found, so the caller (the skill) can surface install
instructions.

Usage:
    python render.py <input.html> <output.png> [--width 1080] [--height 1420]
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Known install paths per platform. Order = preference.
CHROME_CANDIDATES = {
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ],
    "win32": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Chromium\Application\chrome.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ],
    "linux": [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/usr/bin/microsoft-edge",
        "/usr/bin/brave-browser",
    ],
}

# PATH-name fallbacks, used after specific paths fail.
PATH_FALLBACKS = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "msedge",
    "microsoft-edge",
    "brave-browser",
]


def find_browser() -> str | None:
    plat = sys.platform
    # Normalize: win32 covers 64-bit too; darwin = macOS.
    key = "darwin" if plat == "darwin" else "win32" if plat.startswith("win") else "linux"

    for candidate in CHROME_CANDIDATES.get(key, []):
        if candidate and Path(candidate).exists():
            return candidate

    for name in PATH_FALLBACKS:
        found = shutil.which(name)
        if found:
            return found

    return None


def file_url(path: Path) -> str:
    # Windows paths need a leading slash and forward slashes for file://.
    abs_path = path.resolve()
    if sys.platform.startswith("win"):
        return "file:///" + str(abs_path).replace("\\", "/")
    return abs_path.as_uri()


def render(html_path: Path, png_path: Path, width: int, height: int) -> None:
    browser = find_browser()
    if not browser:
        sys.stderr.write(
            "[ccti/render] No Chromium-based browser found.\n"
            "Install one of: Google Chrome, Chromium, Microsoft Edge, or Brave.\n"
            f"Looked under platform '{sys.platform}'.\n"
        )
        sys.exit(2)

    # Make sure target dir exists.
    png_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={png_path}",
        file_url(html_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        sys.stderr.write("[ccti/render] Browser timed out after 60s.\n")
        sys.exit(3)

    if not png_path.exists() or png_path.stat().st_size == 0:
        sys.stderr.write(
            f"[ccti/render] Browser ran but PNG not produced.\n"
            f"  browser: {browser}\n"
            f"  stdout: {result.stdout.strip()[:400]}\n"
            f"  stderr: {result.stderr.strip()[:400]}\n"
        )
        sys.exit(4)

    print(f"[ccti/render] OK -> {png_path} ({png_path.stat().st_size} bytes via {Path(browser).name})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="Path to source HTML file")
    ap.add_argument("png", help="Path to output PNG file")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1420)
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        sys.stderr.write(f"[ccti/render] HTML file not found: {html_path}\n")
        sys.exit(1)

    render(html_path, Path(args.png), args.width, args.height)


if __name__ == "__main__":
    main()
