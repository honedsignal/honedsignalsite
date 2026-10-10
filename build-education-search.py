#!/usr/bin/env python3
"""Build education search: search-index.json + /education/search/ page.
Mirrors money/build-search.py; parses the 5 hub sections."""
import json, os, re, html as ihtml

EDU = "education"
BASE = "https://honedsignal.com"

def parse_hub():
    doc = open(os.path.join(EDU, "index.html"), encoding="utf-8").read()
    sections = []
    for m in re.finditer(
        r'<section class="edu-section" aria-label="([^"]+)">(.*?)</section>',
        doc, re.S):
        sec_name, body = m.group(1), m.group(2)
        cards = []
        for c in re.finditer(
            r'<a class="card" href="(/education/([^"/]+)/)"><h3>(.*?)</h3><p>(.*?)</p>',
            body, re.S):
            url, slug = c.group(1), c.group(2)
            title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c.group(3))).strip()
            desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c.group(4))).strip()
            cards.append((slug, title, desc, url))
        sections.append((sec_name, cards))
    return sections

def main():
    entries = []
    sections = parse_hub()
    total = 0
    for sec_name, cards in sections:
        for slug, title, desc, url in cards:
            tp = os.path.join(EDU, slug, "index.html")
            if not os.path.exists(tp):
                print("WARN: missing tool page", slug); continue
            mt = re.search(r"<title>(.*?)</title>",
                           open(tp, encoding="utf-8").read(), re.S)
            pt = re.sub(r"\s+", " ", mt.group(1)).strip() if mt else title
            pt = re.sub(r"\s*\|\s*Honed Signal\s*$", "", pt)
            entries.append({"t": pt, "d": desc, "u": url,
                            "tags": [sec_name], "kind": "tool"})
            total += 1
    entries.append({"t": "Education Tools",
                    "d": "All education tools for students, teachers, parents, and admins.",
                    "u": "/education/", "tags": [], "kind": "hub"})
    # dedupe on URL
    seen, unique = set(), []
    for e in entries:
        if e["u"] not in seen:
            seen.add(e["u"]); unique.append(e)
    entries = unique
    with open(os.path.join(EDU, "search-index.json"), "w") as f:
        json.dump(entries, f, separators=(",", ":"))
    print("index entries:", len(entries), "tool cards parsed:", total)

    tags = sorted({t for e in entries for t in e["tags"]})
    tag_pills = "\n".join(
        f'<button class="tag" data-tag="{ihtml.escape(t)}">{ihtml.escape(t)}</button>'
        for t in tags)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Search Education Tools | Honed Signal</title>
<meta name="description" content="Search all education tools by keyword or topic: paying for college, grades and study, teachers, parents, school operations.">
<link rel="canonical" href="{BASE}/education/search/">
<style>
:root{{--bg:#0b0e14;--panel:#121722;--ink:#f5f5f5;--muted:#9aa3b5;--orange:#f7931a;--line:#232c3d}}
body{{background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;line-height:1.6}}
.wrap{{max-width:860px;margin:0 auto;padding:20px clamp(16px,4vw,32px) 60px}}
.back-link{{display:inline-block;color:var(--muted);text-decoration:none;font-size:.9rem;margin:6px 0 0}}
h1{{font-size:clamp(1.7rem,4.6vw,2.4rem);letter-spacing:-.01em}}
.lede{{color:var(--muted)}}
#q{{width:100%;box-sizing:border-box;background:var(--panel);border:1px solid var(--line);border-radius:12px;color:var(--ink);font-size:1.1rem;padding:14px 18px;margin:18px 0 6px}}
#q:focus{{outline:2px solid var(--orange);border-color:var(--orange)}}
.tags{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 6px}}
.tag{{background:var(--panel);border:1px solid var(--line);color:var(--muted);border-radius:999px;padding:7px 14px;font-size:.85rem;cursor:pointer}}
.tag.on{{background:var(--orange);border-color:var(--orange);color:#1a1206;font-weight:600}}
#count{{color:var(--muted);font-size:.9rem;margin:10px 0}}
.res{{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:10px 0;text-decoration:none;color:var(--ink)}}
.res:hover{{border-color:var(--orange)}}
.res h2{{font-size:1.05rem;margin:0 0 4px}}
.res p{{margin:0;color:var(--muted);font-size:.9rem}}
.res .k{{font-size:.75rem;color:var(--orange);text-transform:uppercase;letter-spacing:.06em}}
footer{{color:#7d8698;font-size:.8rem;text-align:center;margin-top:44px}}
</style>
</head>
<body>
<div class="wrap">
<a class="back-link" href="/education/">&larr; Education Tools</a>
<h1>Search Education Tools</h1>
<p class="lede">Find any tool by keyword, or filter by topic.</p>
<input id="q" type="search" placeholder="Try &lsquo;scholarship&rsquo;, &lsquo;IEP&rsquo;, &lsquo;lesson plan&rsquo;&hellip;" autocomplete="off" aria-label="Search education tools">
<div class="tags" id="tags">{tag_pills}</div>
<div id="count"></div>
<div id="results"></div>
<footer>For informational purposes only.</footer>
</div>
<script>
let IDX = [];
let activeTag = "";
const q = document.getElementById("q"), res = document.getElementById("results"),
      count = document.getElementById("count");
fetch("/education/search-index.json").then(r => r.json()).then(d => {{ IDX = d; render(""); }});
const params = new URLSearchParams(location.search);
if (params.get("q")) {{ q.value = params.get("q"); }}
q.addEventListener("input", () => render(q.value.trim().toLowerCase()));
document.getElementById("tags").addEventListener("click", e => {{
  const b = e.target.closest(".tag"); if (!b) return;
  document.querySelectorAll(".tag").forEach(t => t.classList.remove("on"));
  if (activeTag === b.dataset.tag) {{ activeTag = ""; }}
  else {{ activeTag = b.dataset.tag; b.classList.add("on"); }}
  render(q.value.trim().toLowerCase());
}});
function render(term) {{
  const words = term.split(/\\s+/).filter(Boolean);
  const hits = IDX.filter(e => {{
    if (activeTag && !e.tags.includes(activeTag)) return false;
    if (!words.length) return true;
    const hay = (e.t + " " + e.d + " " + e.tags.join(" ")).toLowerCase();
    return words.every(w => hay.includes(w));
  }});
  count.textContent = hits.length + (hits.length === 1 ? " result" : " results");
  res.innerHTML = hits.slice(0, 60).map(e =>
    `<a class="res" href="${{e.u}}"><span class="k">${{e.kind}}</span><h2>${{e.t}}</h2><p>${{e.d}}</p></a>`
  ).join("") || "<p class='lede'>No matches. Try fewer words or a different topic.</p>";
}}
</script>
</body>
</html>"""
    os.makedirs(os.path.join(EDU, "search"), exist_ok=True)
    open(os.path.join(EDU, "search", "index.html"), "w").write(html)
    print("search page written")

if __name__ == "__main__":
    main()
