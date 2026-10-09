#!/usr/bin/env python3
"""Inject the hm-recent recorder script into Honed Money tool pages only.

A page qualifies as a calculator/tool page when it carries the
"@type":"WebApplication" JSON-LD marker — which is exactly the 222 tool
pages and excludes hub/section/browse/search/decide/about/contact/glossary
pages plus the 11 decision-entry pages.
"""
import os
import sys

ROOT = os.path.expanduser("~/workspace/honedsignal-site/money")
TAG = '<script src="/money/recent-tools.js" defer></script>'
MARKER = '"@type":"WebApplication"'

injected = 0
skipped = 0
already = 0

for dirpath, _dirnames, filenames in os.walk(ROOT):
    if "index.html" not in filenames:
        continue
    path = os.path.join(dirpath, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if TAG in html:
        already += 1
        continue
    if MARKER not in html:
        skipped += 1
        continue
    if "</body>" not in html:
        print(f"NO </body>: {path}")
        skipped += 1
        continue
    html = html.replace("</body>", TAG + "\n</body>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    injected += 1

print(f"injected={injected} skipped={skipped} already_present={already}")
