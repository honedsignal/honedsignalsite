#!/usr/bin/env python3
"""Add the site-wide legal disclaimer to all Honed Money pages. Idempotent."""
import glob

LEGAL = (
    '<div class="hs-legal" style="max-width:680px;margin:28px auto 0;padding:20px 16px 0;'
    'border-top:1px solid #232c3d;color:#7d8698;font-size:.78rem;line-height:1.6;text-align:center;">'
    "Honed Money provides calculators and educational information for general purposes only. "
    "It is not financial, tax, legal, investment, or insurance advice. Estimates are based on "
    "the information you enter and the assumptions shown. Actual results will vary. For taxes, "
    "retirement, and government benefits, verify with "
    '<a href="https://www.irs.gov" style="color:#9aa3b5;">IRS.gov</a>, '
    '<a href="https://www.ssa.gov" style="color:#9aa3b5;">SSA.gov</a>, or '
    '<a href="https://www.va.gov" style="color:#9aa3b5;">VA.gov</a>. '
    "We don&rsquo;t sell financial products and aren&rsquo;t paid for calculator results. "
    "Use at your own risk.</div>"
)

n = 0
files = (glob.glob("money/*/index.html") + glob.glob("money/*/*/index.html")
         + glob.glob("money/*/*/*/index.html") + ["money/index.html"])
for f in sorted(set(files)):
    doc = open(f, encoding="utf-8").read()
    if "hs-legal" in doc:
        continue
    if "</body>" in doc:
        doc = doc.replace("</body>", LEGAL + "\n</body>", 1)
    else:
        print("SKIP:", f)
        continue
    open(f, "w", encoding="utf-8").write(doc)
    n += 1
print("added legal disclaimer to", n, "pages")
