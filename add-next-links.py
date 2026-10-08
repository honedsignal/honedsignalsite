#!/usr/bin/env python3
"""Inject 'What's next?' cross-link boxes into Honed Money calculator pages.
Idempotent: skips pages that already have the box.
"""
import os, re, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
MONEY = os.path.join(ROOT, "money")

# slug -> [(link title, url), ...] — specific next steps
NEXT = {
    "mortgage-payment-calculator": [("Can you afford it?", "/money/mortgage-affordability-calculator/"), ("Pay it off faster", "/money/extra-mortgage-payment-calculator/")],
    "mortgage-affordability-calculator": [("Estimate the payment", "/money/mortgage-payment-calculator/"), ("Down payment vs investing", "/money/down-payment-vs-investment-calculator/")],
    "rent-vs-buy-calculator": [("Check affordability", "/money/mortgage-affordability-calculator/"), ("Estimate closing costs", "/money/closing-cost-calculator/")],
    "extra-mortgage-payment-calculator": [("See the full schedule", "/money/mortgage-amortization-schedule-viewer/"), ("Refinance break-even", "/money/refinance-break-even-calculator/")],
    "mortgage-amortization-schedule-viewer": [("Pay it off faster", "/money/extra-mortgage-payment-calculator/"), ("Refinance break-even", "/money/refinance-break-even-calculator/")],
    "mortgage-discount-points-calculator": [("Estimate the payment", "/money/mortgage-payment-calculator/"), ("Refinance break-even", "/money/refinance-break-even-calculator/")],
    "refinance-break-even-calculator": [("Compare scenarios", "/money/mortgage-scenario-comparison/"), ("Estimate the payment", "/money/mortgage-payment-calculator/")],
    "mortgage-scenario-comparison": [("Refinance break-even", "/money/refinance-break-even-calculator/"), ("Pay it off faster", "/money/extra-mortgage-payment-calculator/")],
    "closing-cost-calculator": [("Estimate the payment", "/money/mortgage-payment-calculator/"), ("Down payment vs investing", "/money/down-payment-vs-investment-calculator/")],
    "down-payment-vs-investment-calculator": [("Check affordability", "/money/mortgage-affordability-calculator/"), ("Estimate closing costs", "/money/closing-cost-calculator/")],
    "heloc-vs-home-equity-loan-calculator": [("Debt payoff strategies", "/money/debt-payoff-strategy-comparison/")],
    "home-sale-proceeds-calculator": [("Rent vs buy", "/money/rent-vs-buy-calculator/")],
    "property-tax-estimator": [("Home maintenance costs", "/money/home-maintenance-cost-calculator/")],
    "home-maintenance-cost-calculator": [("True cost of ownership", "/money/car-ownership-cost-calculator/")],
    "credit-card-payoff-analyzer": [("Compare payoff strategies", "/money/debt-payoff-strategy-comparison/"), ("Plan a windfall", "/money/windfall-planner-calculator/")],
    "debt-payoff-strategy-comparison": [("Analyze a card payoff", "/money/credit-card-payoff-analyzer/"), ("Consolidation check", "/money/debt-consolidation-calculator/")],
    "debt-consolidation-calculator": [("Compare payoff strategies", "/money/debt-payoff-strategy-comparison/"), ("Balance transfer check", "/money/balance-transfer-calculator/")],
    "balance-transfer-calculator": [("Analyze a card payoff", "/money/credit-card-payoff-analyzer/")],
    "take-home-pay-calculator": [("Build a 50/30/20 budget", "/money/50-30-20-budget-calculator/"), ("Find your tax bracket", "/money/tax-bracket-calculator/")],
    "tax-bracket-calculator": [("Estimate take-home pay", "/money/take-home-pay-calculator/"), ("Roth vs traditional", "/money/roth-vs-traditional-calculator/")],
    "50-30-20-budget-calculator": [("Build your emergency fund", "/money/emergency-fund-calculator/"), ("Estimate take-home pay", "/money/take-home-pay-calculator/")],
    "emergency-fund-calculator": [("Build a 50/30/20 budget", "/money/50-30-20-budget-calculator/"), ("High-yield savings options", "/money/cd-treasury-ladder-calculator/")],
    "compound-interest-calculator": [("Project retirement savings", "/money/retirement-savings-projector/"), ("I-bond calculator", "/money/i-bond-calculator/")],
    "retirement-savings-projector": [("Am I on track?", "/money/retirement-income-gap-calculator/"), ("Compare retirement ages", "/money/retirement-age-comparison/")],
    "retirement-income-gap-calculator": [("Estimate Social Security", "/money/social-security-estimator/"), ("Project retirement savings", "/money/retirement-savings-projector/")],
    "retirement-age-comparison": [("Am I on track?", "/money/retirement-income-gap-calculator/"), ("Social Security estimator", "/money/social-security-estimator/")],
    "social-security-estimator": [("Am I on track?", "/money/retirement-income-gap-calculator/"), ("Estimate retiree health costs", "/money/medicare-retiree-health-cost-estimator/")],
    "medicare-retiree-health-cost-estimator": [("Long-term care costs", "/money/long-term-care-cost-calculator/"), ("Am I on track?", "/money/retirement-income-gap-calculator/")],
    "pension-lump-sum-vs-annuity-calculator": [("Am I on track?", "/money/retirement-income-gap-calculator/")],
    "rmd-calculator": [("Roth conversion check", "/money/roth-conversion-calculator/")],
    "roth-conversion-calculator": [("Roth vs traditional", "/money/roth-vs-traditional-calculator/"), ("Find your tax bracket", "/money/tax-bracket-calculator/")],
    "roth-vs-traditional-calculator": [("Roth conversion check", "/money/roth-conversion-calculator/")],
    "401k-match-calculator": [("Project retirement savings", "/money/retirement-savings-projector/")],
    "i-bond-calculator": [("Build a CD/Treasury ladder", "/money/cd-treasury-ladder-calculator/"), ("Compound interest", "/money/compound-interest-calculator/")],
    "cd-treasury-ladder-calculator": [("I-bond calculator", "/money/i-bond-calculator/"), ("Build your emergency fund", "/money/emergency-fund-calculator/")],
    "hdhp-vs-ppo-calculator": [("FSA vs HSA", "/money/fsa-vs-hsa-calculator/")],
    "fsa-vs-hsa-calculator": [("HDHP vs PPO", "/money/hdhp-vs-ppo-calculator/")],
    "cobra-vs-marketplace-calculator": [("HDHP vs PPO", "/money/hdhp-vs-ppo-calculator/")],
    "term-vs-whole-life-insurance-calculator": [("How much coverage?", "/money/life-insurance-needs-calculator/")],
    "life-insurance-needs-calculator": [("Term vs whole life", "/money/term-vs-whole-life-insurance-calculator/"), ("Disability needs", "/money/disability-insurance-needs-calculator/")],
    "disability-insurance-needs-calculator": [("Term vs whole life", "/money/term-vs-whole-life-insurance-calculator/")],
    "umbrella-insurance-calculator": [("Homeowners estimate", "/money/homeowners-insurance-estimator/")],
    "homeowners-insurance-estimator": [("Umbrella check", "/money/umbrella-insurance-calculator/")],
    "auto-insurance-deductible-calculator": [("Umbrella check", "/money/umbrella-insurance-calculator/"), ("True car cost", "/money/car-ownership-cost-calculator/")],
    "long-term-care-cost-calculator": [("Retiree health costs", "/money/medicare-retiree-health-cost-estimator/")],
    "auto-loan-calculator": [("True cost of ownership", "/money/car-ownership-cost-calculator/"), ("Check your deductible", "/money/auto-insurance-deductible-calculator/")],
    "car-ownership-cost-calculator": [("EV vs gas", "/money/ev-vs-gas-car-calculator/"), ("Commute cost", "/money/commute-cost-calculator/")],
    "ev-vs-gas-car-calculator": [("Commute cost", "/money/commute-cost-calculator/"), ("True cost of ownership", "/money/car-ownership-cost-calculator/")],
    "commute-cost-calculator": [("EV vs gas", "/money/ev-vs-gas-car-calculator/")],
    "lease-vs-buy-car-calculator": [("True cost of ownership", "/money/car-ownership-cost-calculator/")],
    "student-loan-payoff-calculator": [("Refinance vs IDR", "/money/student-loan-refi-vs-idr-calculator/")],
    "student-loan-refi-vs-idr-calculator": [("Payoff calculator", "/money/student-loan-payoff-calculator/")],
    "windfall-planner-calculator": [("Compare debt strategies", "/money/debt-payoff-strategy-comparison/"), ("Build your emergency fund", "/money/emergency-fund-calculator/")],
    "salary-vs-hourly-calculator": [("Estimate take-home pay", "/money/take-home-pay-calculator/")],
    "freelance-rate-calculator": [("Self-employment tax", "/money/self-employment-tax-estimator/")],
    "self-employment-tax-estimator": [("Freelance rate", "/money/freelance-rate-calculator/"), ("Quarterly tax check", "/money/quarterly-tax-estimator/")],
}

BOX_CSS = """<style>.hs-next{max-width:680px;margin:28px auto 0;padding:18px 20px;border:1px solid #2a3448;border-radius:12px;background:#121826}.hs-next h3{margin:0 0 10px;font-size:1rem;color:#f7931a}.hs-next ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}.hs-next a{color:#e8eaf0;text-decoration:none}.hs-next a:hover{color:#f7931a}.hs-next a span.arr{color:#f7931a;margin-right:6px}</style>"""

def box_html(links):
    items = "".join(f'<li><a href="{url}"><span class="arr">→</span>{title}</a></li>' for title, url in links)
    return f'{BOX_CSS}\n<div class="hs-next"><h3>What\'s next?</h3><ul>{items}</ul></div>'

def section_of(slug):
    """Find parent section by checking which section page links to this slug."""
    for sec in os.listdir(MONEY):
        sp = os.path.join(MONEY, sec, "index.html")
        if not os.path.isfile(sp) or sec in ("browse", "decide", "search"):
            continue
        try:
            with open(sp) as f:
                if f'/{slug}/' in f.read():
                    return sec
        except Exception:
            pass
    return None

def default_links(slug):
    links = []
    sec = section_of(slug)
    if sec:
        sec_name = sec.replace("-", " ").title()
        links.append((f"More {sec_name} calculators", f"/money/{sec}/"))
    links.append(("Guided decision paths", "/money/decide/"))
    return links[:2]

def process(path):
    slug = path.split(os.sep)[-2]
    # skip non-calculator pages
    if slug in ("browse", "decide", "search", "legal", "privacy", "about", "contact", "glossary"):
        return "skip"
    # skip section index pages (they list tools, not calculators)
    with open(path) as f:
        html = f.read()
    if 'class="hs-next"' in html:
        return "already"
    # must look like a calculator (has inputs or calculate button)
    if "<input" not in html and "calculate" not in html.lower():
        return "skip"
    links = NEXT.get(slug, default_links(slug))
    box = box_html(links)
    # tier 1: after explain-results section
    m = re.search(r'(<p class="result-explanation-copy"[^>]*>.*?</p>|<div class="result-explanation"[^>]*>.*?</div>)', html, re.S)
    if m:
        html = html[:m.end()] + "\n" + box + html[m.end():]
    # tier 2: before hs-legal div
    elif '<div class="hs-legal"' in html:
        html = html.replace('<div class="hs-legal"', box + '\n<div class="hs-legal"', 1)
    # tier 3: before </main>
    elif "</main>" in html:
        html = html.replace("</main>", box + "\n</main>", 1)
    # tier 4: before <footer
    elif "<footer" in html:
        html = html.replace("<footer", box + "\n<footer", 1)
    else:
        return "no-anchor"
    with open(path, "w") as f:
        f.write(html)
    return "ok"

def main():
    results = {}
    for p in sorted(glob.glob(os.path.join(MONEY, "*", "index.html"))):
        r = process(p)
        results[r] = results.get(r, 0) + 1
    print(results)

if __name__ == "__main__":
    main()
