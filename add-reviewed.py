#!/usr/bin/env python3
"""Add 'Last reviewed' line to Honed Money tool pages. Idempotent."""
import glob, re

LINE = ('<p class="hs-reviewed" style="text-align:center;color:#8a93a3;'
        'font-size:.75rem;margin:16px auto 0;max-width:640px;padding:0 16px;">'
        'Last reviewed: October 2026.</p>')

SECTIONS = {"auto", "business", "budget", "career", "credit", "debt", "divorce",
            "estate-planning", "family", "health", "housing", "insurance",
            "investing", "military", "personal", "pets", "retirement",
            "students", "taxes", "travel", "wedding"}

n = 0
for f in glob.glob("money/*/index.html"):
    dirname = f.split("/")[1]
    if dirname in SECTIONS or dirname in ("images", "assets"):
        continue
    doc = open(f, encoding="utf-8").read()
    if "hs-reviewed" in doc:
        continue
    if "</body>" in doc:
        doc = doc.replace("</body>", LINE + "\n</body>", 1)
    elif "</html>" in doc:
        doc = doc.replace("</html>", LINE + "\n</html>", 1)
    else:
        print("SKIP (no body/html):", f)
        continue
    open(f, "w", encoding="utf-8").write(doc)
    n += 1
print("added last-reviewed to", n, "pages")
