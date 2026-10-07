#!/usr/bin/env python3
"""Build Honed Money global search: search-index.json + /money/search/ page."""
import glob, json, os, re, html as ihtml

MONEY = "money"
BASE = "https://honedsignal.com"
SECTIONS = {
    "auto": "Auto", "budget": "Budget", "business": "Business",
    "career": "Career", "credit": "Credit", "debt": "Debt",
    "divorce": "Divorce", "estate-planning": "Estate Planning",
    "family": "Family", "health": "Health", "housing": "Housing",
    "insurance": "Insurance", "investing": "Investing",
    "military": "Military", "personal": "Personal", "pets": "Pets",
    "retirement": "Retirement", "students": "Students", "taxes": "Taxes",
    "travel": "Travel", "wedding": "Wedding",
}

# extra cross-tags for tools that span sections: slug -> [tags]
XTAGS = {
    "take-home-pay-calculator": ["Career", "Taxes"],
    "tax-bracket-calculator": ["Personal"],
    "effective-vs-marginal-tax-rate-calculator": ["Personal"],
    "w-4-withholding-calculator": ["Career"],
    "quarterly-estimated-tax-calculator": ["Business"],
    "self-employment-tax-estimator": ["Business"],
    "capital-gains-tax-calculator": ["Investing"],
    "tax-loss-harvesting-calculator": ["Investing"],
    "hsa-tax-savings-calculator": ["Health", "Investing"],
    "hsa-vs-ira-comparison-calculator": ["Retirement", "Health"],
    "roth-conversion-calculator": ["Retirement", "Taxes"],
    "roth-vs-traditional-ira-calculator": ["Retirement", "Taxes"],
    "rmd-calculator": ["Taxes"],
    "social-security-estimator": ["Retirement"],
    "retirement-savings-projector": ["Investing"],
    "debt-to-income-ratio-calculator": ["Housing"],
    "rent-vs-buy-calculator": ["Housing"],
    "mortgage-affordability-calculator": ["Personal"],
    "credit-card-payoff-analyzer": ["Budget"],
    "debt-snowball-vs-avalanche-calculator": ["Budget"],
    "balance-transfer-calculator": ["Credit"],
    "emergency-fund-calculator": ["Insurance"],
    "net-worth-calculator": ["Investing"],
    "compound-interest-calculator": ["Retirement", "Investing"],
    "investment-return-calculator": ["Retirement"],
    "college-savings-estimator": ["Students"],
    "childcare-cost-calculator": ["Budget"],
    "life-insurance-needs-calculator": ["Family"],
    "disability-insurance-needs-calculator": ["Career"],
    "cobra-vs-marketplace-calculator": ["Insurance"],
    "hdhp-vs-ppo-calculator": ["Insurance"],
    "va-disability-pay-calculator": ["Health"],
    "va-home-loan-calculator": ["Housing"],
    "military-retirement-estimator": ["Retirement"],
    "ppm-move-profit-estimator": ["Career"],
    "job-offer-comparison-calculator": ["Personal"],
    "salary-vs-hourly-calculator": ["Personal"],
    "freelance-rate-calculator": ["Career"],
    "severance-pay-estimator": ["Debt"],
    "solar-payback-calculator": ["Taxes"],
    "home-office-deduction-estimator": ["Taxes", "Business"],
    "charitable-deduction-calculator": ["Personal"],
    "estate-tax-estimator": ["Taxes"],
    "funeral-cost-estimator": ["Family"],
    "will-vs-trust-calculator": ["Family"],
    "divorce-cost-estimator": ["Personal"],
    "alimony-estimator": ["Taxes"],
    "child-support-estimator": ["Family"],
    "gpa-calculator": ["Career"],
    "first-apartment-budget-calculator": ["Housing", "Budget"],
    "student-loan-payoff-calculator": ["Debt"],
    "wedding-budget-calculator": ["Budget"],
    "wedding-guest-cost-calculator": ["Travel"],
    "honeymoon-budget-calculator": ["Travel", "Budget"],
    "vacation-budget-calculator": ["Budget"],
    "road-trip-cost-calculator": ["Auto"],
    "points-and-miles-value-calculator": ["Credit"],
    "tip-calculator": ["Family"],
    "subscription-cost-analyzer": ["Budget"],
    "paycheck-budget-planner": ["Career"],
    "50-30-20-budget-calculator": ["Personal"],
    "monthly-budget-planner": ["Personal"],
    "credit-score-simulator": ["Housing"],
    "credit-utilization-calculator": ["Debt"],
    "credit-score-improvement-planner": ["Housing"],
    "pet-insurance-calculator": ["Insurance"],
    "dog-ownership-cost-calculator": ["Budget"],
    "cat-ownership-cost-calculator": ["Budget"],
    "car-ownership-cost-calculator": ["Budget"],
    "ev-vs-gas-car-calculator": ["Taxes"],
    "lease-vs-buy-car-calculator": ["Credit"],
    "auto-loan-calculator": ["Credit", "Budget"],
    "auto-insurance-deductible-calculator": ["Personal"],
    "umbrella-insurance-calculator": ["Family"],
    "long-term-care-cost-calculator": ["Health", "Retirement"],
    "homeowners-insurance-estimator": ["Housing"],
    "term-vs-whole-life-insurance-calculator": ["Investing"],
    "dividend-calculator": ["Taxes"],
    "dividend-reinvestment-calculator": ["Retirement"],
    "dollar-cost-averaging-calculator": ["Retirement"],
    "portfolio-allocation-calculator": ["Retirement"],
    "position-size-calculator": ["Personal"],
    "risk-reward-calculator": ["Personal"],
    "investment-fee-calculator": ["Retirement"],
    "401k-match-calculator": ["Retirement", "Career"],
    "break-even-calculator": ["Career"],
    "profit-margin-calculator": ["Career"],
    "cash-runway-calculator": ["Personal"],
    "business-loan-calculator": ["Debt"],
    "employee-cost-calculator": ["Taxes"],
    "relocation-cost-calculator": ["Career", "Housing"],
    "law-enforcement-overtime-calculator": ["Taxes"],
    "out-of-pocket-health-cost-estimator": ["Budget"],
    "wedding-budget-calculator": ["Family"],
}

def parse_cards(sec):
    out = []
    p = os.path.join(MONEY, sec, "index.html")
    doc = open(p, encoding="utf-8").read()
    for b in re.finditer(r"<article\b[^>]*>(.*?)</article>", doc, re.S):
        block = b.group(1)
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
    entries = []
    for sec, sec_name in sorted(SECTIONS.items()):
        # section entry
        entries.append({
            "t": sec_name + " Money Calculators",
            "d": "All %s calculators in one place." % sec_name.lower(),
            "u": "/money/%s/" % sec,
            "tags": [sec_name], "kind": "section",
        })
        for slug, title, desc in parse_cards(sec):
            tags = [sec_name] + [t for t in XTAGS.get(slug, []) if t != sec_name]
            _tp = os.path.join(MONEY, slug, "index.html")
            if not os.path.exists(_tp):
                print("WARN: missing tool page", slug); continue
            mt = re.search(r"<title>(.*?)</title>", open(_tp, encoding="utf-8").read(), re.S)
            pt = re.sub(r"\s+", " ", mt.group(1)).strip() if mt else title
            pt = re.sub(r"\s*\|\s*Honed Money\s*$", "", pt)
            entries.append({
                "t": pt, "d": desc, "u": "/money/%s/" % slug,
                "tags": tags, "kind": "tool",
            })
    # decision paths
    dp = os.path.join(MONEY, "decide", "index.html")
    if os.path.exists(dp):
        entries.append({"t": "Decision Center — What Are You Trying to Decide?",
                        "d": "Pick your question; we'll walk you through the calculators that answer it.",
                        "u": "/money/decide/", "tags": ["Decisions"], "kind": "decisions"})
        for d in sorted(glob.glob(os.path.join(MONEY, "decide", "*", "index.html"))):
            slug = d.split(os.sep)[-2]
            doc = open(d, encoding="utf-8").read()
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S)
            q = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else slug
            entries.append({"t": q, "d": "A guided path: the calculators that answer this decision, in order.",
                            "u": "/money/decide/%s/" % slug, "tags": ["Decisions"], "kind": "decision"})

    # deduplicate on URL, keeping first occurrence
    seen = set()
    unique = []
    for e in entries:
        if e["u"] not in seen:
            seen.add(e["u"])
            unique.append(e)
    entries = unique

    with open(os.path.join(MONEY, "search-index.json"), "w") as f:
        json.dump(entries, f, separators=(",", ":"))
    print("index entries:", len(entries))

    # ---- search page ----
    tags = sorted({t for e in entries for t in e["tags"]})
    tag_pills = "\n".join(
        f'<button class="tag" data-tag="{ihtml.escape(t)}">{ihtml.escape(t)}</button>' for t in tags)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Search Honed Money | Honed Money</title>
<meta name="description" content="Search all 112 Honed Money calculators and 10 decision paths by keyword or topic tag.">
<link rel="canonical" href="{BASE}/money/search/">
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
<a class="back-link" href="/money/">&larr; Honed Money</a>
<h1>Search Honed Money</h1>
<p class="lede">Find any calculator or decision path by keyword, or filter by topic.</p>
<input id="q" type="search" placeholder="Try &lsquo;refinance&rsquo;, &lsquo;retirement&rsquo;, &lsquo;credit score&rsquo;&hellip;" autocomplete="off" aria-label="Search Honed Money">
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
fetch("/money/search-index.json").then(r => r.json()).then(d => {{ IDX = d; render(""); }});
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
    os.makedirs(os.path.join(MONEY, "search"), exist_ok=True)
    open(os.path.join(MONEY, "search", "index.html"), "w").write(html)
    print("search page written")

if __name__ == "__main__":
    main()
