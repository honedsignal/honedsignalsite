#!/usr/bin/env python3
"""Add artwork hero banners to Honed Money section + tool pages. Idempotent.

- Section pages get their own artwork; tool pages get their parent
  section's artwork (resolved from section card links).
- The page's existing H1 is moved into the banner (id preserved),
  so there is still exactly one H1 per page.
- Skips the welcome page (money/index.html) and browse page.
"""
import glob, os, re

MONEY = "money"
IMG = {
    "auto": "auto", "budget": "budget", "business": "business",
    "career": "career", "credit": "credit", "debt": "debt",
    "divorce": "divorce", "estate-planning": "estate", "family": "family",
    "health": "health", "housing": "housing", "insurance": "insurance",
    "investing": "investing", "military": "military", "personal": "personal",
    "pets": "pets", "retirement": "retirement", "students": "students",
    "taxes": "taxes", "travel": "travel", "wedding": "wedding",
}
SECTIONS = set(IMG)

CSS = """<style data-hs-hero>
.hs-hero{position:relative;border-radius:18px;overflow:hidden;margin:20px 0 30px;min-height:230px;display:flex;align-items:flex-end;background:#121720}
.hs-hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hs-hero .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,14,20,.08) 0%,rgba(11,14,20,.82) 100%)}
.hs-hero h1{position:relative;z-index:1;margin:0;padding:30px clamp(20px,4vw,38px);font-size:clamp(1.7rem,4.6vw,2.5rem);line-height:1.18;color:#f5f5f5;font-weight:700;letter-spacing:-.01em}
@media(max-width:640px){.hs-hero{min-height:165px;margin:14px 0 22px}.hs-hero h1{padding:22px 20px}}
</style>"""

def tool_section():
    """slug -> section, parsed from section cards."""
    m = {}
    for sec in SECTIONS:
        p = os.path.join(MONEY, sec, "index.html")
        if not os.path.exists(p):
            continue
        doc = open(p, encoding="utf-8").read()
        for b in re.finditer(r"<article\b[^>]*>(.*?)</article>", doc, re.S):
            block = b.group(1)
            hm = re.search(r'href="(https://honedsignal\.com)?(/money/([^"/]+)/)"', block)
            if hm:
                m[hm.group(3)] = sec
    return m

def hero(img, h1_inner, h1_id):
    idattr = f' id="{h1_id}"' if h1_id else ""
    return (
        CSS + "\n" +
        f'<div class="hs-hero">\n'
        f'  <img src="/money/images/{img}.webp" alt="" aria-hidden="true">\n'
        f'  <div class="shade"></div>\n'
        f'  <h1{idattr} class="hs-hero-title">{h1_inner}</h1>\n'
        f'</div>'
    )

def process(path, img):
    doc = open(path, encoding="utf-8").read()
    if "hs-hero" in doc:
        return "skip"
    m = re.search(r"<h1([^>]*)>(.*?)</h1>", doc, re.S)
    if not m:
        return "no-h1"
    attrs, inner = m.group(1), m.group(2)
    idm = re.search(r'id="([^"]+)"', attrs)
    hid = idm.group(1) if idm else ""
    doc = doc[:m.start()] + hero(img, inner.strip(), hid) + doc[m.end():]
    open(path, "w", encoding="utf-8").write(doc)
    return "ok"

def main():
    ts = tool_section()
    stats = {}
    for sec in sorted(SECTIONS):
        r = process(os.path.join(MONEY, sec, "index.html"), IMG[sec])
        stats[r] = stats.get(r, 0) + 1
    for slug, sec in sorted(ts.items()):
        p = os.path.join(MONEY, slug, "index.html")
        if not os.path.exists(p):
            stats["missing-page"] = stats.get("missing-page", 0) + 1
            continue
        r = process(p, IMG[sec])
        stats[r] = stats.get(r, 0) + 1
    print(stats)

if __name__ == "__main__":
    main()
