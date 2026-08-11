"""
Headless check for horizontal overflow at phone widths.

Horizontal overflow is the single most common way a "responsive" site is
actually broken on a phone, and it is invisible on a desktop monitor. This
renders each page inside an iframe of a given width (an iframe gets its own
viewport, so media queries evaluate correctly) and asserts that
scrollWidth == clientWidth.

Usage:
    python -m http.server 8791 --bind 127.0.0.1     # from the repo root
    python tools/check_responsive.py [--port 8791] [--widths 360,390,414]

Requires Google Chrome. Exits non-zero if any page overflows.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = os.path.join(ROOT, ".debug")
PAGES = {"home": "index.html", "about": "about/index.html",
         "menu": "menu/index.html", "hours": "hours/index.html"}

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/usr/bin/google-chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

HARNESS = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>pending</title>
<style>html,body{margin:0}iframe{border:0;display:block}</style></head><body>
<iframe id="f" src="/.debug/__PAGE__.html" width="__WIDTH__" height="1000"></iframe>
<script>
document.getElementById('f').addEventListener('load', function () {
  setTimeout(function () {
    var d = this.contentDocument, w = this.contentWindow;
    var vw = d.documentElement.clientWidth;
    var sw = d.documentElement.scrollWidth;
    var hits = [];
    d.querySelectorAll('*').forEach(function (el) {
      if (el.classList.contains('skip')) return;        // intentionally off-screen
      if (el.closest('.media-fill')) return;            // clipped by overflow:hidden
      var r = el.getBoundingClientRect();
      if (r.width > vw + 1 || r.right > vw + 1) hits.push(el);
    });
    var leaves = hits.filter(function (el) {
      return !hits.some(function (o) { return o !== el && el.contains(o); });
    }).map(function (el) {
      var r = el.getBoundingClientRect();
      return el.tagName + '.' + (el.className || '') + ' w' + r.width.toFixed(0);
    });
    document.title = 'RESULT|' + vw + '|' + sw + '|' + leaves.slice(0, 6).join(' , ');
  }.bind(this), 700);
});
</script></body></html>"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    found = shutil.which("chrome") or shutil.which("google-chrome")
    if found:
        return found
    sys.exit("Google Chrome not found — set CHROME_CANDIDATES in this script.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8791)
    ap.add_argument("--widths", default="360,390,414")
    args = ap.parse_args()
    widths = [int(w) for w in args.widths.split(",")]
    chrome = find_chrome()

    os.makedirs(DEBUG, exist_ok=True)
    # The pages set frame-ancestors 'none', so frame a CSP-stripped copy.
    for name, src in PAGES.items():
        html = open(os.path.join(ROOT, src), encoding="utf-8").read()
        html = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", html)
        open(os.path.join(DEBUG, f"{name}.html"), "w", encoding="utf-8", newline="\n").write(html)

    failures = 0
    for name in PAGES:
        for width in widths:
            harness = HARNESS.replace("__PAGE__", name).replace("__WIDTH__", str(width))
            hpath = os.path.join(DEBUG, f"h-{name}-{width}.html")
            open(hpath, "w", encoding="utf-8", newline="\n").write(harness)
            out = subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--window-size=900,1100",
                 "--virtual-time-budget=8000", "--dump-dom",
                 f"http://127.0.0.1:{args.port}/.debug/h-{name}-{width}.html"],
                capture_output=True, text=True, errors="replace").stdout
            m = re.search(r"<title>RESULT\|(\d+)\|(\d+)\|([^<]*)</title>", out)
            if not m:
                print(f"  {name:6s} @{width}: could not measure (is the server running?)")
                failures += 1
                continue
            vw, sw, leaves = int(m.group(1)), int(m.group(2)), m.group(3).strip()
            if sw > vw or leaves:
                print(f"  {name:6s} @{width}: OVERFLOW viewport={vw} scrollWidth={sw}  {leaves}")
                failures += 1
            else:
                print(f"  {name:6s} @{width}: ok (viewport={vw})")

    shutil.rmtree(DEBUG, ignore_errors=True)
    print(f"\n{failures} overflow failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
