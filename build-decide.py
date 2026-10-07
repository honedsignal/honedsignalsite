#!/usr/bin/env python3
"""Generate the Honed Money Decision Center: landing + 10 decision paths."""
import os

MONEY = "money"
BASE = "https://honedsignal.com"

CSS = """<style>
:root{--bg:#0b0e14;--panel:#121722;--ink:#f5f5f5;--muted:#9aa3b5;--orange:#f7931a;--teal:#2fbfae;--line:#232c3d}
body{background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;line-height:1.6}
.wrap{max-width:860px;margin:0 auto;padding:20px clamp(16px,4vw,32px) 60px}
.back-link{display:inline-block;color:var(--muted);text-decoration:none;font-size:.9rem;margin:6px 0 0}
.back-link:hover{color:var(--ink)}
.hs-hero{position:relative;border-radius:18px;overflow:hidden;margin:20px 0 30px;min-height:230px;display:flex;align-items:flex-end;background:#121720}
.hs-hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hs-hero .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,14,20,.08) 0%,rgba(11,14,20,.82) 100%)}
.hs-hero h1{position:relative;z-index:1;margin:0;padding:30px clamp(20px,4vw,38px);font-size:clamp(1.7rem,4.6vw,2.5rem);line-height:1.18;color:#f5f5f5;font-weight:700;letter-spacing:-.01em}
.lede{font-size:1.12rem;color:var(--muted);max-width:640px}
.qgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:28px 0}
.qcard{display:block;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;text-decoration:none;color:var(--ink);transition:border-color .15s}
.qcard:hover{border-color:var(--orange)}
.qcard h2{font-size:1.08rem;margin:0 0 8px;line-height:1.35}
.qcard p{margin:0;color:var(--muted);font-size:.92rem}
.step{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;margin:18px 0}
.step .n{display:inline-block;background:var(--orange);color:#1a1206;font-weight:700;border-radius:999px;width:30px;height:30px;line-height:30px;text-align:center;margin-right:10px}
.step h2{display:inline;font-size:1.15rem}
.step p{color:var(--muted);margin:10px 0}
.step .go{display:inline-block;margin-top:8px;background:var(--orange);color:#1a1206;font-weight:600;text-decoration:none;padding:10px 20px;border-radius:10px}
.step .go:hover{filter:brightness(1.08)}
.together{background:#14202c;border:1px solid #2a3f52;border-radius:14px;padding:22px;margin:28px 0}
.together h2{margin-top:0;font-size:1.2rem}
.together p{color:var(--muted)}
footer{color:#7d8698;font-size:.8rem;text-align:center;margin-top:44px}
@media(max-width:640px){.hs-hero{min-height:165px;margin:14px 0 22px}.hs-hero h1{padding:22px 20px}}
</style>"""

FOOT = """<footer>For informational purposes only. Results are estimates, not financial advice.<br>Last reviewed: October 2026.</footer>"""

def page(title, desc, body_html, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
</head>
<body>
<div class="wrap">
{body_html}
{FOOT}
</div>
</body>
</html>"""

DECISIONS = [
 dict(slug="can-i-afford-this-house", img="housing",
      q="Can I afford this house?",
      sub="Three numbers tell you the truth before you fall in love with a listing.",
      intro=("A house you can't comfortably afford stops being a dream and starts being a trap. "
             "Forget rules of thumb — run these three calculators in order and you'll know exactly "
             "where you stand."),
      steps=[
       ("See what price range fits your income",
        "Mortgage Affordability Calculator", "/money/mortgage-affordability-calculator/",
        "Tells you the home price your income can actually support, not the one a lender will approve you for.",
        "If the house you want is above this range, it's a stretch — no matter what the bank says."),
       ("Price the monthly payment on the real house",
        "Mortgage Payment Calculator", "/money/mortgage-payment-calculator/",
        "Shows the true monthly cost — principal, interest, taxes, and insurance — for the actual home you're eyeing.",
        "Compare it to your take-home pay. If it's more than about a third, pause."),
       ("Count the cash you'll need on day one",
        "Closing Cost Calculator", "/money/closing-cost-calculator/",
        "Estimates the down payment plus closing costs due at signing — the number people forget until it's too late.",
        "If you don't have this in cash without emptying your emergency fund, you're not ready yet."),
      ],
      together=("If all three numbers fit comfortably — the price is in your range, the payment leaves "
                "breathing room, and you have the cash — you can afford the house. If any one of them "
                "is a stretch, the honest answer is not yet.")),
 dict(slug="buy-or-rent", img="buy-or-rent",
      q="Should I buy or rent?",
      sub="It's not a lifestyle question first. It's a math question first.",
      intro=("Buying isn't automatically smarter than renting — it depends on prices, rents, how long "
             "you'll stay, and what your money could do elsewhere. These three calculators settle it "
             "with numbers instead of opinions."),
      steps=[
       ("Run the head-to-head numbers",
        "Rent vs. Buy Calculator", "/money/rent-vs-buy-calculator/",
        "Compares the total cost of buying versus renting over the same years, including the costs people leave out.",
        "This is your anchor number. If buying doesn't clearly win here, renting is probably the smarter move."),
       ("Check what buying power you actually have",
        "Mortgage Affordability Calculator", "/money/mortgage-affordability-calculator/",
        "Shows the price range your income supports, so you're comparing realistic homes — not fantasy ones.",
        "Use this to keep the rent-vs-buy comparison honest."),
       ("Know what renting really costs you",
        "First Apartment Budget Calculator", "/money/first-apartment-budget-calculator/",
        "Lays out the full monthly cost of renting — rent plus everything around it.",
        "Plug this number into the rent-vs-buy comparison for an accurate result."),
      ],
      together=("If buying wins the math AND you'll stay put for at least five years AND the payment fits "
                "your budget, buy. If any of those fail, renting isn't throwing money away — it's the "
                "right financial decision.")),
 dict(slug="debt-or-invest", img="debt",
      q="Should I pay off debt or invest?",
      sub="High-interest debt is a guaranteed return killer. Do the math anyway.",
      intro=("Every dollar has two possible jobs: killing debt or growing investments. The right choice "
             "depends on what your debt costs versus what investing might earn. These calculators make "
             "the comparison concrete."),
      steps=[
       ("See what your debt is really costing you",
        "Credit Card Payoff Analyzer", "/money/credit-card-payoff-analyzer/",
        "Shows how much interest you'll pay and how long you'll be trapped making minimum payments.",
        "Write down the interest rate. That's the guaranteed return you get from paying it off."),
       ("See what investing that money could earn",
        "Investment Return Calculator", "/money/investment-return-calculator/",
        "Projects what the same dollars could grow to in the market over the same years.",
        "Compare this growth to your debt's interest rate. Debt at 25% beats almost any investment."),
       ("Check how stretched you already are",
        "Debt-to-Income Ratio Calculator", "/money/debt-to-income-ratio-calculator/",
        "Measures how much of your income is already spoken for by debt payments.",
        "If this is high, paying down debt isn't just smart — it's urgent."),
      ],
      together=("Simple rule that holds up: if your debt charges more than about 7–8% interest, kill the "
                "debt first — that's a guaranteed return no investment can promise. Below that, splitting "
                "between debt and investing is reasonable.")),
 dict(slug="can-i-retire", img="retirement",
      q="Can I retire yet?",
      sub="Retirement isn't an age. It's a number.",
      intro=("You can retire when your money can cover your life without your paycheck. These three "
             "calculators check whether you're there — or how far away you are."),
      steps=[
       ("Project what you'll have saved",
        "Retirement Savings Projector", "/money/retirement-savings-projector/",
        "Estimates your nest egg at retirement based on what you're saving now.",
        "This is your starting point. Everything else builds on it."),
       ("Add what Social Security pays you",
        "Social Security Estimator", "/money/social-security-estimator/",
        "Estimates your monthly benefit at different claiming ages.",
        "Later claiming means bigger checks — see what waiting is worth to you."),
       ("Check what you'll be forced to withdraw",
        "RMD Calculator", "/money/rmd-calculator/",
        "Shows the minimum you must pull from tax-deferred accounts each year after 73.",
        "This affects your tax picture in retirement — good to know before you plan spending."),
      ],
      together=("Add your projected savings withdrawals to Social Security. If that total covers your "
                "spending with room to spare — year after year — you're ready. If not, you now know "
                "exactly how big the gap is.")),
 dict(slug="how-much-to-save", img="personal",
      q="How much should I save?",
      sub="Three buckets, in order. Fill them one at a time.",
      intro=("Saving feels vague until you give it targets. There are really only three: a safety net, "
             "your future self, and everything in between. Here's how to size each one."),
      steps=[
       ("Size your safety net first",
        "Emergency Fund Calculator", "/money/emergency-fund-calculator/",
        "Calculates the cash cushion that covers your essential bills for 3–6 months.",
        "This comes before everything else. No safety net, no peace of mind."),
       ("See what you can actually set aside",
        "Monthly Budget Planner", "/money/monthly-budget-planner/",
        "Maps your income against spending to find your real monthly surplus.",
        "Be honest here — a plan you can't follow is worse than no plan."),
       ("Watch what your savings become",
        "Compound Interest Calculator", "/money/compound-interest-calculator/",
        "Shows how your monthly savings grow over decades with compounding.",
        "This is your motivation engine. Small amounts early beat big amounts late."),
      ],
      together=("Fund the emergency cushion first, then automate monthly savings from your budget surplus. "
                "The compound interest calculator shows you why starting now matters more than the amount.")),
 dict(slug="should-i-refinance", img="refinance",
      q="Should I refinance my mortgage?",
      sub="A lower rate is only half the story. The fees are the other half.",
      intro=("Refinancing trades a lower rate for upfront closing costs. It only wins if you keep the "
             "loan long enough for the monthly savings to repay those costs. These calculators do that "
             "math for you."),
      steps=[
       ("Find your break-even point",
        "Refinance Break-Even Calculator", "/money/refinance-break-even-calculator/",
        "Calculates how many months until the monthly savings repay the refinancing costs.",
        "If you'll sell or move before break-even, refinancing loses money."),
       ("Compare the payments side by side",
        "Mortgage Payment Calculator", "/money/mortgage-payment-calculator/",
        "Shows your current payment versus the refinanced payment with the new rate and term.",
        "Watch the term — a lower payment from stretching the loan longer can cost more overall."),
       ("Consider the alternative: pay it down faster",
        "Extra Mortgage Payment Calculator", "/money/extra-mortgage-payment-calculator/",
        "Shows what happens if you put extra money toward your current mortgage instead.",
        "Sometimes the best refinance is no refinance — just paying down what you have."),
      ],
      together=("Refinance if the rate drop is meaningful, the break-even is well within your plans to stay, "
                "and the total interest over the life of the loan actually falls. Otherwise, extra payments "
                "on your current loan may do more.")),
 dict(slug="how-much-insurance", img="insurance",
      q="How much insurance do I need?",
      sub="Insure what you can't afford to lose. Skip the rest.",
      intro=("Insurance exists for one reason: to protect against losses you couldn't absorb yourself. "
             "These calculators size the coverage that actually matters — and keep you from overbuying."),
      steps=[
       ("Size your life insurance",
        "Life Insurance Needs Calculator", "/money/life-insurance-needs-calculator/",
        "Estimates the coverage your family would need if your income disappeared.",
        "If nobody depends on your income, you may need far less than agents suggest."),
       ("Protect your paycheck itself",
        "Disability Insurance Needs Calculator", "/money/disability-insurance-needs-calculator/",
        "Shows how much disability coverage protects the income your whole plan depends on.",
        "You're more likely to become disabled than to die young — this one matters."),
       ("Know your self-insurance layer",
        "Emergency Fund Calculator", "/money/emergency-fund-calculator/",
        "Sizes the cash cushion that covers small emergencies without a claim.",
        "A solid emergency fund lets you take higher deductibles and pay less in premiums."),
      ],
      together=("Buy enough term life and disability to protect dependents and income, keep an emergency fund "
                "for the small stuff, and skip the expensive policies that protect against things you could "
                "absorb. Insurance is a safety net, not an investment.")),
 dict(slug="take-this-job", img="career",
      q="Should I take this job offer?",
      sub="The salary number is the least informative part of the offer.",
      intro=("A job offer is a whole package: pay, benefits, commute, hours, growth. Comparing two "
             "salaries without the rest is like comparing two cars by color. These calculators compare "
             "the whole deal."),
      steps=[
       ("Compare the full offers apples to apples",
        "Job Offer Comparison Calculator", "/money/job-offer-comparison-calculator/",
        "Weighs salary, benefits, bonuses, and perks side by side.",
        "A lower salary with great benefits can beat a higher salary with none."),
       ("See what the paycheck really is",
        "Take-Home Pay Calculator", "/money/take-home-pay-calculator/",
        "Estimates your actual take-home pay after federal taxes in 2026.",
        "The gross salary is fantasy. This is the number your life runs on."),
       ("Normalize it if the pay structure differs",
        "Salary vs. Hourly Calculator", "/money/salary-vs-hourly-calculator/",
        "Converts between salary and hourly so different offer structures compare fairly.",
        "Hourly with overtime can beat salary — do the conversion before you judge."),
      ],
      together=("The right offer is the one with the best total compensation for the life you want — "
                "take-home pay, benefits, hours, and growth. If the numbers are close, let the non-money "
                "factors decide.")),
 dict(slug="start-a-business", img="business",
      q="Should I start a business?",
      sub="Enthusiasm is not a business plan. These numbers are.",
      intro=("Most businesses fail on math, not effort. Before you leap, know exactly how much you must "
             "sell, how long your money lasts, and what to charge. These three calculators give you that."),
      steps=[
       ("Learn how much you must sell to survive",
        "Break-Even Calculator", "/money/break-even-calculator/",
        "Calculates the sales volume where the business stops losing money.",
        "If you can't see a realistic path to this number, the idea needs work."),
       ("Know how long your money lasts",
        "Cash Runway Calculator", "/money/cash-runway-calculator/",
        "Shows how many months your savings cover the business before it must pay for itself.",
        "Your runway must be longer than your path to break-even. Otherwise you're planning to crash."),
       ("Figure out what to charge",
        "Freelance Rate Calculator", "/money/freelance-rate-calculator/",
        "Works backward from the income you need to the rate you must charge.",
        "Most new businesses undercharge. This keeps you honest."),
      ],
      together=("Start when you can see a credible path to break-even inside your cash runway, at prices "
                "customers will actually pay. If the math doesn't work on paper, it won't work in the "
                "real world either.")),
 dict(slug="can-i-afford-this-car", img="auto",
      q="Can I afford this car?",
      sub="The sticker price is the smallest part of what a car costs.",
      intro=("A car drains money four ways: the payment, insurance, fuel, and repairs. Most buyers only "
             "look at the first one. These calculators show you all four before you sign."),
      steps=[
       ("Price the monthly payment",
        "Auto Loan Calculator", "/money/auto-loan-calculator/",
        "Estimates your monthly payment for the price, down payment, rate, and term.",
        "Longer terms lower the payment but raise the total cost — check both."),
       ("Add the costs everyone forgets",
        "Car Ownership Cost Calculator", "/money/car-ownership-cost-calculator/",
        "Totals insurance, fuel, maintenance, and depreciation — the real cost of owning.",
        "This number is often double the payment alone. Let it sink in."),
       ("Check it against your actual budget",
        "Monthly Budget Planner", "/money/monthly-budget-planner/",
        "Shows whether the total car cost fits your real monthly spending.",
        "If the car breaks the budget, the answer is a cheaper car — not a longer loan."),
      ],
      together=("You can afford the car if the full ownership cost fits your budget with room to spare, "
                "the loan term is reasonable, and you're not raiding your emergency fund for the down "
                "payment.")),
]

LANDING_Q = "What are you trying to decide?"
LANDING_SUB = "Skip the menu. Pick your question — we'll walk you through the calculators that answer it, in order."
LANDING_INTRO = ("Honed Money has 112 calculators, but most people don't need a calculator — they need an "
                 "answer. Choose the decision you're facing below. Each path guides you through the two or "
                 "three calculators that matter for that decision, explains what each number means, and "
                 "shows you how to put it all together.")

def landing():
    cards = "\n".join(
        f'<a class="qcard" href="/money/decide/{d["slug"]}/"><h2>{d["q"]}</h2><p>{d["sub"]}</p></a>'
        for d in DECISIONS)
    body = f"""<a class="back-link" href="/money/">← Honed Money</a>
<div class="hs-hero">
  <img src="/money/images/decide.webp" alt="" aria-hidden="true">
  <div class="shade"></div>
  <h1 class="hs-hero-title">{LANDING_Q}</h1>
</div>
<p class="lede">{LANDING_INTRO}</p>
<div class="qgrid">
{cards}
</div>"""
    return page("Decision Center — What Are You Trying to Decide? | Honed Money",
                LANDING_SUB + " " + LANDING_INTRO[:120],
                CSS + body,
                BASE + "/money/decide/")

def decision(d):
    steps = "\n".join(
        f"""<div class="step">
<span class="n">{i+1}</span><h2>{title}</h2>
<p>{what}</p>
<a class="go" href="{url}">{name} →</a>
<p><strong>What to do with it:</strong> {dowith}</p>
</div>"""
        for i, (title, name, url, what, dowith) in enumerate(d["steps"]))
    body = f"""<a class="back-link" href="/money/decide/">← Decision Center</a>
<div class="hs-hero">
  <img src="/money/images/{d["img"]}.webp" alt="" aria-hidden="true">
  <div class="shade"></div>
  <h1 class="hs-hero-title">{d["q"]}</h1>
</div>
<p class="lede">{d["intro"]}</p>
{steps}
<div class="together">
<h2>Putting it together</h2>
<p>{d["together"]}</p>
</div>"""
    return page(f'{d["q"]} | Honed Money Decision Center',
                d["sub"],
                CSS + body,
                BASE + f'/money/decide/{d["slug"]}/')

def main():
    os.makedirs(os.path.join(MONEY, "decide"), exist_ok=True)
    open(os.path.join(MONEY, "decide", "index.html"), "w").write(landing())
    for d in DECISIONS:
        p = os.path.join(MONEY, "decide", d["slug"])
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "index.html"), "w").write(decision(d))
    print("generated", 1 + len(DECISIONS), "pages")

if __name__ == "__main__":
    main()
