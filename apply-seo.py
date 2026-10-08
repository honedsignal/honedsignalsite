#!/usr/bin/env python3
"""Honed Money on-page SEO pass.

Idempotent: safe to re-run after re-exporting artifacts. It
1. Parses every section page's tool cards (title, description, href).
2. Rewrites each tool page title, adds meta description + JSON-LD.
3. Rewrites section pages title + meta description + CollectionPage schema.
4. Rewrites the hub title + meta description + WebSite schema.
5. Regenerates sitemap.xml and robots.txt at the site root.

Run from the repo root:  python3 apply-seo.py
"""
import re
import os
import glob
import html as ihtml
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
MONEY = os.path.join(ROOT, "money")
BASE = "https://honedsignal.com"
TODAY = date.today().isoformat()

SECTIONS = {
    "auto": "Auto", "business": "Business", "budget": "Budget",
    "career": "Career", "credit": "Credit", "debt": "Debt",
    "divorce": "Divorce", "estate-planning": "Estate Planning",
    "family": "Family", "health": "Health", "housing": "Housing",
    "insurance": "Insurance", "investing": "Investing", "military": "Military",
    "personal": "Personal", "pets": "Pets", "retirement": "Retirement",
    "students": "Students", "taxes": "Taxes", "travel": "Travel",
    "wedding": "Wedding",
}

START = "<!-- honed-seo-start -->"
END = "<!-- honed-seo-end -->"


def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def split_head(doc):
    m = re.search(r"<head(\s[^>]*)?>", doc)
    assert m, "no <head> found"
    hs = m.start()
    he = doc.index("</head>", hs) + len("</head>")
    return doc[:hs], doc[hs:he], doc[he:]


def clean_head(head):
    head = re.sub(re.escape(START) + r".*?" + re.escape(END), "", head, flags=re.S)
    head = re.sub(r'<meta\s+name="description"[^>]*>\s*', "", head)
    head = re.sub(r'<link\s+rel="canonical"[^>]*>\s*', "", head)
    return head


def set_title(head, title):
    title = ihtml.escape(title)
    head = re.sub(r"<title>.*?</title>", "<title>" + title + "</title>", head, flags=re.S, count=1)
    return head


def inject(head, block):
    return head.replace("</head>", START + "\n" + block + "\n" + END + "\n</head>", 1)


def tool_schema(name, desc, url):
    return (
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"WebApplication",\n'
        '"name":' + jstr(name) + ',"applicationCategory":"FinanceApplication",'
        '"operatingSystem":"Any",\n'
        '"url":' + jstr(url) + ',"description":' + jstr(desc) + ",\n"
        '"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}}\n'
        "</script>"
    )


def parse_cards(sec):
    """Return list of (slug, card_title, card_desc) for a section page."""
    p = os.path.join(MONEY, sec, "index.html")
    if not os.path.exists(p):
        print("WARN: missing section page " + sec)
        return []
    doc = read(p)
    out = []
    for m in re.finditer(r"<article\b[^>]*>(.*?)</article>", doc, re.S):
        block = m.group(1)
        hm = re.search(r'href="(https://honedsignal\.com)?(/money/([^"/]+)/)"', block)
        tm = re.search(r"<h[23][^>]*>(.*?)</h[23]>", block, re.S)
        if not (hm and tm):
            continue
        slug = hm.group(3)
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", tm.group(1))).strip()
        dm = re.search(r"<p(\s[^>]*)?>(.*?)</p>", block, re.S)
        desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", dm.group(2))).strip() if dm else ""
        if title.lower().startswith("open tool"):
            continue
        out.append((slug, title, desc))
    return out


def main():
    tools = {}
    for sec, sec_name in SECTIONS.items():
        for slug, title, desc in parse_cards(sec):
            tools[slug] = (title, desc, sec_name)
    print("found %d tool cards across sections" % len(tools))

    sitemap_urls = [BASE + "/money/"]

    for slug in sorted(tools):
        card_title, card_desc, sec_name = tools[slug]
        p = os.path.join(MONEY, slug, "index.html")
        if not os.path.exists(p):
            print("WARN: missing tool page " + slug)
            continue
        doc = read(p)
        pre, head, post = split_head(doc)
        mt = re.search(r"<title>(.*?)</title>", head, re.S)
        page_title = re.sub(r"\s+", " ", mt.group(1)).strip() if mt else card_title
        page_title = re.sub(r"\s*\|\s*Honed Money\s*$", "", page_title)
        tool_noun = page_title.lower()
        desc = card_desc if card_desc.endswith(".") or not card_desc else card_desc + "."
        meta_desc = (desc + " Free " + tool_noun
                     + " from Honed Money \u2014 plain-English results, no signup needed.").strip()
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."
        url = BASE + "/money/" + slug + "/"
        sitemap_urls.append(url)

        head = clean_head(head)
        head = set_title(head, page_title + " | Honed Money")
        block = ('<meta name="description" content="' + ihtml.escape(meta_desc, quote=True) + '" />\n'
                 + '<link rel="canonical" href="' + url + '" />\n'
                 + tool_schema(page_title, meta_desc, url))
        head = inject(head, block)
        write(p, pre + head + post)

    # decision center pages (generated by build-decide.py; already have
    # title/desc/canonical — just ensure they're in the sitemap)
    dp = os.path.join(MONEY, "decide", "index.html")
    if os.path.exists(dp):
        sitemap_urls.append(BASE + "/money/decide/")
        for d in sorted(glob.glob(os.path.join(MONEY, "decide", "*", "index.html"))):
            slug = d.split(os.sep)[-2]
            sitemap_urls.append(BASE + f"/money/decide/{slug}/")

    for sec, sec_name in SECTIONS.items():
        p = os.path.join(MONEY, sec, "index.html")
        if not os.path.exists(p):
            continue
        doc = read(p)
        pre, head, post = split_head(doc)
        title = sec_name + " Money Calculators | Honed Money"
        meta_desc = ("Free " + sec_name.lower() + " calculators from Honed Money \u2014 "
                     "plain-English answers to real money questions, no signup needed.")
        url = BASE + "/money/" + sec + "/"
        sitemap_urls.append(url)
        head = clean_head(head)
        head = set_title(head, title)
        block = ('<meta name="description" content="' + ihtml.escape(meta_desc, quote=True) + '" />\n'
                 + '<link rel="canonical" href="' + url + '" />\n'
                 + '<script type="application/ld+json">\n'
                 + '{"@context":"https://schema.org","@type":"CollectionPage",\n'
                 + '"name":' + jstr(title) + ',"url":' + jstr(url) + ",\n"
                 + '"description":' + jstr(meta_desc) + "}\n"
                 + "</script>")
        head = inject(head, block)
        write(p, pre + head + post)

    p = os.path.join(MONEY, "index.html")
    doc = read(p)
    pre, head, post = split_head(doc)
    hub_title = "Honed Money \u2014 Free Personal Finance Calculators"
    hub_desc = ("%d free money calculators from Honed Money: budgeting, debt payoff, "
                "mortgages, retirement, taxes, insurance and more. "
                "Plain-English results, no signup." % len(tools))
    head = clean_head(head)
    head = set_title(head, hub_title)
    block = ('<meta name="description" content="' + ihtml.escape(hub_desc, quote=True) + '" />\n'
             + '<link rel="canonical" href="' + BASE + '/money/" />\n'
             + '<script type="application/ld+json">\n'
             + '{"@context":"https://schema.org","@type":"WebSite",\n'
             + '"name":"Honed Money","url":' + jstr(BASE + "/money/") + ",\n"
             + '"description":' + jstr(hub_desc) + "}\n"
             + "</script>")
    head = inject(head, block)
    write(p, pre + head + post)

    # browse page (visual gateway hub, moved from /money/)    p = os.path.join(MONEY, "browse", "index.html")
    if os.path.exists(p):
        doc = read(p)
        pre, head, post = split_head(doc)
        b_title = "Browse All Money Calculators | Honed Money"
        b_desc = ("Browse all Honed Money calculator collections by topic — "
                  "21 illustrated sections covering every money question, "
                  "from budgeting to estate planning.")
        b_url = BASE + "/money/browse/"
        sitemap_urls.append(b_url)
        head = clean_head(head)
        head = set_title(head, b_title)
        block = ('<meta name="description" content="' + ihtml.escape(b_desc, quote=True) + '" />\n'
                 + '<link rel="canonical" href="' + b_url + '" />\n'
                 + '<script type="application/ld+json">\n'
                 + '{"@context":"https://schema.org","@type":"CollectionPage",\n'
                 + '"name":' + jstr(b_title) + ',"url":' + jstr(b_url) + ",\n"
                 + '"description":' + jstr(b_desc) + "}\n"
                 + "</script>")
        head = inject(head, block)
        write(p, pre + head + post)

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # trust pages (not section tools, so not picked up above)
    for slug in ("legal", "privacy", "about", "contact", "glossary"):
        if os.path.exists(os.path.join(MONEY, slug, "index.html")):
            sitemap_urls.append(BASE + f"/money/{slug}/")
    # guide pages
    for d in sorted(glob.glob(os.path.join(MONEY, "guides", "*", "index.html"))):
        gslug = d.split(os.sep)[-2]
        sitemap_urls.append(BASE + f"/money/guides/{gslug}/")
    for u in sorted(set(sitemap_urls)):
        sm.append("  <url><loc>" + u + "</loc><lastmod>" + TODAY + "</lastmod></url>")
    sm.append("</urlset>")
    write(os.path.join(ROOT, "sitemap.xml"), "\n".join(sm) + "\n")
    write(os.path.join(ROOT, "robots.txt"),
          "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "/sitemap.xml\n")
    print("SEO pass complete: %d URLs in sitemap" % len(set(sitemap_urls)))


if __name__ == "__main__":
    main()
