/*
 * Honed Money — input hint tooltips (input-hints.js)
 *
 * Adds a small "?" button next to labeled inputs on seeded calculator pages.
 * The button toggles a short plain-English hint (typical 2026 ranges included).
 *
 * Design constraints:
 *  - No external JS dependencies.
 *  - Must never break a page: everything is wrapped so failures are silent.
 *  - HINTS is keyed by page slug (the money/<slug>/ directory name). Pages
 *    with no entry are left completely untouched.
 *  - Label matching is case-insensitive substring on normalized label text.
 */
(function () {
  'use strict';

  try {
    // ---- Resolve the page slug ------------------------------------------
    var SLUG = (function () {
      try {
        var p = String(window.location && window.location.pathname || '').replace(/\/+$/, '');
        return p.substring(p.lastIndexOf('/') + 1).toLowerCase();
      } catch (e) {
        return '';
      }
    })();
    if (!SLUG) return;

    // ---- Hint database ---------------------------------------------------
    // Keys are normalized label texts (lowercase, non-alphanumerics collapsed
    // to a single space). Matching is substring-based; longest keys are tried
    // first so specific labels win over shorter generic ones.
    var HINTS = {

      'mortgage-payment-calculator': {
        'home price': 'Enter the agreed purchase price of the home, before subtracting your down payment.',
        'down payment': 'Common down payments run from 3-5% of the price (typical conventional minimum) up to 20%, which avoids private mortgage insurance (PMI).',
        'annual interest rate': '30-year fixed mortgage rates in 2026 are often in the 7-8% range (15-year loans are often 6-7%). Your actual quote depends on credit score, down payment, and lender.',
        'loan term': 'The most common terms are 30, 20, or 15 years. Shorter terms mean higher monthly payments but much less total interest.'
      },

      'refinance-break-even-calculator': {
        'current loan balance': 'The remaining balance you still owe, found on your mortgage statement.',
        'current interest rate': 'Your existing mortgage rate, from your statement or loan documents.',
        'new interest rate': 'The refinance rate a lender is offering you. 30-year fixed rates in 2026 are often in the 7-8% range.',
        'new loan term': '30, 20, or 15 years are most common. A shorter new term raises the payment but cuts total interest.',
        'closing costs': 'Refinance closing costs usually run 2-5% of the loan amount. The break-even point is how many months of savings it takes to recover them.'
      },

      'mortgage-affordability-calculator': {
        'annual household income': 'Use gross (before-tax) income for everyone who will be on the loan.',
        'monthly debt payments': 'Include car payments, student loans, and credit card minimums. Lenders commonly want total debt-to-income under 43% (36% or less is preferred).',
        'down payment': 'Common down payments run from 3-5% of the price (typical conventional minimum) up to 20%, which avoids PMI.',
        'interest rate': '30-year fixed mortgage rates in 2026 are often in the 7-8% range (15-year loans are often 6-7%).',
        'loan term': 'The most common terms are 30, 20, or 15 years.'
      },

      'auto-loan-calculator': {
        'vehicle price': 'The average new-car transaction price crossed $50,000 in 2026 (Kelley Blue Book), and buyers financed about $45,000 on average (Edmunds, Q3 2026).',
        'down payment': '20% down is the common recommendation, and lenders often want at least 10%. A bigger down payment means less interest and no risk of owing more than the car is worth.',
        'trade-in value': 'What a dealer pays you for your current car. It reduces the amount you need to finance.',
        'apr': 'New-car APRs in 2026 are often in the 6-8% range; used-car rates are often 7-9%. Excellent credit earns the lowest rates.',
        'loan term': 'Common terms are 36-72 months. In 2026 a record share of buyers stretched to 84 months (Edmunds) - longer terms lower the payment but raise total interest a lot.'
      },

      'credit-card-payoff-analyzer': {
        'extra amount available each month': 'Any amount above the minimums you can put toward debt. Paying the highest-APR card first (the avalanche method) costs the least in interest.',
        'balance': 'The total amount you currently owe on the card.',
        'apr': 'Credit card APRs in 2026 are often in the 20-24% range. Your exact rate is on your card statement.',
        'minimum': 'Minimum payments are often around 1-2% of the balance. Paying only the minimum can keep you in debt for years.'
      },

      'take-home-pay-calculator': {
        'annual gross salary': 'Your pay before taxes and any deductions.',
        'hourly rate': 'Full-time is usually 40 hours a week, 52 weeks a year.',
        'filing status': 'Your filing status sets your tax brackets and standard deduction. Most people are Single or Married Filing Jointly.',
        'state + local rate': 'Your combined state and local income tax as a percent. Texas has no state income tax, so 0% works for most Texans.',
        'retirement': '401(k)/403(b) contributions come out before taxes, lowering your taxable income.',
        'health / hsa / fsa': 'Health insurance premiums and HSA/FSA contributions are usually pre-tax.',
        'other after-tax deductions': 'Things like union dues or after-tax savings taken from your paycheck.'
      },

      'rent-vs-buy-calculator': {
        'home price': 'The purchase price of the home you would buy.',
        'down payment (percent of home price)': 'Common down payments run from 3-5% of the price (typical conventional minimum) up to 20%, which avoids PMI.',
        'mortgage rate': '30-year fixed mortgage rates in 2026 are often in the 7-8% range (15-year loans are often 6-7%).',
        'loan term': '30 years is most common for purchases.',
        'property tax / year': 'The U.S. average effective property tax is roughly 1% of home value per year, but it varies widely by state and county.',
        'home insurance / month': 'Required by lenders. Covers damage to the home and liability.',
        'maintenance / year': 'A common rule of thumb is about 1% of the home value per year for upkeep and repairs.',
        'monthly rent': 'What you would pay in rent for a comparable place.',
        'years before moving': 'Buying usually needs around 5 or more years in the home to beat renting, once closing and selling costs are counted.',
        'rent increase / year': 'U.S. rents have historically risen about 3-4% per year on average.',
        'home appreciation / year': 'U.S. home prices have historically appreciated roughly 4-5% per year on average over long periods.',
        'investment return / year': 'U.S. stocks have historically returned about 7-10% per year on average over long periods, before inflation.'
      },

      'compound-interest-calculator': {
        'starting amount': 'The lump sum you are starting with. Use 0 if you are starting from scratch.',
        'starting balance': 'The lump sum you are starting with. Use 0 if you are starting from scratch.',
        'monthly contribution': 'What you plan to add each month, every month.',
        'annual interest rate': 'Try 7-10% for a stock-heavy mix (the long-run historical average) or 3.5-4.5% for a high-yield savings account. This is before inflation and taxes.'
      },

      'emergency-fund-calculator': {
        'already saved': 'What you already have set aside in savings for emergencies.',
        'monthly contribution': 'How much you can add to the fund each month.',
        'safety cushion': '3-6 months of essential expenses is the common guideline. Aim for 6+ months if your income is irregular.',
        'housing': 'Include rent or mortgage plus property tax and insurance in your housing number.',
        'groceries': 'Your typical monthly grocery spending.'
      },

      'retirement-savings-projector': {
        'current retirement savings': 'Total across all your retirement accounts today (401(k), IRA, etc.).',
        'monthly contribution': 'What you put in each month. Include any employer match - that is free money worth capturing first.',
        'years until retirement': 'How many years until you plan to retire and stop contributing.',
        'expected annual return': 'Many planners use 6-7% after inflation for a stock-heavy mix (the long-run market average is about 7-10% per year before inflation).'
      },

      'student-loan-payoff-calculator': {
        'current loan balance': 'The total you still owe across the loans you want to model.',
        'interest rate': 'Federal direct loans for 2026-27 are around 6.5% for undergrads and up to about 9% for PLUS loans; private refinance rates are often 4-11%.',
        'monthly payment': 'Your required monthly payment, from your servicer.',
        'extra payment each month': 'Extra payments go straight to principal and shorten the loan the most when applied to the highest-rate loan first.'
      },

      'student-loan-refi-vs-idr-calculator': {
        'current loan balance': 'The total you still owe on the loans being compared.',
        'current weighted interest rate': 'The balance-weighted average rate across your current loans.',
        'refinance offer rate': 'The fixed rate a lender offered you. In 2026, fixed refinance rates are often in the 4-11% range depending on credit.',
        'refinance term': 'Refinance terms commonly run 5-20 years.',
        'estimated idr monthly payment': 'Your income-driven repayment payment, based on income and family size.',
        'idr forgiveness horizon': 'IDR forgiveness is usually after 20-25 years of payments.',
        'expected tax rate on forgiven balance': 'A forgiven federal loan balance may be taxed as income - use your marginal tax rate.'
      },

      'debt-payoff-strategy-comparison': {
        'total credit card debt': 'The combined balance across the cards you want to pay off.',
        'average annual interest rate (apr)': 'Credit card APRs in 2026 are often in the 20-24% range. Use the weighted average across your cards.',
        'extra you can pay each month': 'Any amount above the minimums. The avalanche method (highest APR first) costs the least; the snowball method (smallest balance first) gives quicker wins.'
      },

      'balance-transfer-calculator': {
        'balance to transfer': 'The amount you would move to the new card.',
        'current card apr': 'The APR on the card you are transferring from. Credit card APRs in 2026 are often in the 20-24% range.',
        'introductory apr': '0% intro offers commonly last 12-21 months. After that the regular rate (often 20%+) applies.',
        'introductory period': 'How many months the intro rate lasts.',
        'transfer fee': 'Usually 3-5% of the transferred balance, added to what you owe.'
      },

      'debt-consolidation-calculator': {
        'total debt balance': 'The combined balance of the debts you would roll into the new loan.',
        'weighted average apr': 'The balance-weighted average APR of your current debts. Credit card APRs in 2026 are often in the 20-24% range.',
        'loan apr': 'Personal loan APRs in 2026 are often in the 10-15% range for good credit, and can reach 36% for weaker credit.',
        'loan term': 'Personal loan terms commonly run 3-5 years.',
        'one-time loan fees': 'Origination fees are often 1-8% of the loan amount - they raise the true cost, so include them.'
      },

      'bonus-take-home': {
        'bonus amount': 'Bonuses are usually withheld at a flat 22% federal rate (37% on amounts over $1M). That is just withholding - your final tax depends on total yearly income.',
        'filing status': 'Your filing status sets your tax brackets and standard deduction.',
        'state + local effective rate %': 'Your combined state and local income tax as a percent. Texas has no state income tax, so 0% works for most Texans.'
      },

      'college-savings-estimator': {
        "child's current age": 'Your child\'s age now. The more years until college, the more compounding can help.',
        'current 529 balance': 'What is already saved in the 529 or other college fund.',
        'monthly contribution': 'What you plan to add each month until college starts.',
        'school type': 'Public in-state schools cost far less than private ones - the choice changes the target a lot.'
      },

      'closing-cost-calculator': {
        'home price': 'The purchase price of the home.',
        'how are you buying?': 'Paying cash skips lender fees (origination, appraisal, points). Financing adds them - closing costs usually run 2-5% of the loan amount.',
        'expected loan amount': 'Your mortgage amount if financing. Closing costs usually run 2-5% of the loan amount.'
      },

      'cd-treasury-ladder-calculator': {
        'total invested': 'The total amount you will spread across the rungs of the ladder.',
        'amount per rung': 'How much goes into each CD or Treasury. Equal rungs keep the ladder simple.',
        'average annual yield': 'CD and Treasury yields in 2026 are often in the 3.5-4.5% range, depending on term.',
        'number of rungs': 'More rungs means money frees up more often, but each rung is smaller.',
        'rung length': 'How long each rung is locked in, e.g. 6 or 12 months.'
      },

      'down-payment-vs-investment-calculator': {
        'extra down payment': 'The lump sum you are deciding between putting toward the home or investing.',
        'mortgage interest rate': 'Your mortgage rate. Extra down payment effectively "earns" this rate by avoiding interest - 30-year fixed rates in 2026 are often in the 7-8% range.',
        'expected annual investment return': 'U.S. stocks have historically returned about 7-10% per year on average over long periods. Using a lower rate accounts for market risk.',
        'comparison period': 'How many years you plan to hold the home or stay invested.'
      },

      'debt-snowball-vs-avalanche-calculator': {
        'extra monthly payment': 'Any amount above the minimums. Avalanche (highest APR first) costs the least in interest; snowball (smallest balance first) gives faster wins.',
        'balance': 'The current balance owed on each debt.',
        'apr': 'Credit card APRs in 2026 are often in the 20-24% range. Your exact rate is on the statement.',
        'minimum payment': 'The smallest payment the lender accepts each month - often around 1-2% of a credit card balance.'
      },

      'debt-to-income-ratio-calculator': {
        'car payments': 'Your total monthly car payment(s).',
        'card minimums': 'The minimum monthly payments across your credit cards.',
        'student loans': 'Your total monthly student loan payment(s).',
        'other debt': 'Any other recurring debt payments (personal loans, medical debt, etc.). Most mortgage lenders want total debt-to-income under 43%; 36% or less is preferred.'
      },

      'mortgage-discount-points-calculator': {
        'loan amount': 'Your mortgage amount, after the down payment.',
        'base interest rate': 'The rate quoted with zero points. 30-year fixed rates in 2026 are often in the 7-8% range.',
        'discounted rate': 'The lower rate the lender offers if you pay points.',
        'points cost': 'One point costs 1% of the loan amount and typically lowers the rate about 0.25 points.',
        'expected years in the home': 'Points usually break even in about 4-7 years - staying longer is when they pay off.'
      },

      'extra-mortgage-payment-calculator': {
        'loan balance': 'The remaining balance you still owe on your mortgage.',
        'interest rate': 'Your current mortgage rate. Extra payments effectively "earn" this rate by avoiding interest - 30-year fixed rates in 2026 are often in the 7-8% range.',
        'remaining term': 'How many years are left on your loan.',
        'extra principal each month': 'Extra payments go straight to principal. Make sure your lender applies them to principal, not future payments.'
      },

      'dividend-reinvestment-calculator': {
        'starting shares': 'How many shares you own today.',
        'current share price': 'The price per share right now.',
        'starting annual dividend yield': 'The S&P 500\'s dividend yield is often in the 1-2% range; individual stocks vary widely.',
        'annual dividend growth': 'How fast you expect the dividend to grow each year.',
        'years held': 'How long you plan to hold and reinvest.'
      },

      'unit-price-calculator': {
        'price': 'The total price on the shelf tag or listing.',
        'quantity': 'The amount you get — ounces, count, liters, whatever the package states. Use the same unit for both products.',
      },

      'bnpl-true-cost': {
        'purchase price': 'The sticker price before any fees or interest.',
        'number of payments': 'Most buy-now-pay-later plans split into 4 payments over 6 weeks; longer plans often add interest.',
        'fees': 'Late fees, rescheduling fees, or interest the plan charges. A 0% 4-payment plan with no fees costs exactly the sticker price.'
      },

      'child-care-cost-calculator': {
        'rate': 'What the provider charges — the U.S. average for center-based infant care is roughly $300/week, but it varies a lot by state and city.',
        'days per week': 'How many days each week the child attends.',
        'weeks per year': '52 for year-round care; use fewer if care pauses in summer.'
      },

      'car-repair-vs-replace': {
        'repair cost': 'The quote from the shop, including parts and labor.',
        'current value': 'What the car is worth today — check Kelley Blue Book or similar. If the repair costs more than the car is worth, that is a strong signal to replace.',
        'replacement cost': 'The out-the-door price of the replacement car you would buy.',
      }

    };

    var page = HINTS[SLUG];
    if (!page) return;

    // ---- Helpers ---------------------------------------------------------
    function norm(s) {
      return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    }

    // Longest keys first: specific labels win over generic substrings.
    var keys = Object.keys(page).sort(function (a, b) {
      return norm(b).length - norm(a).length;
    });

    function hintFor(text) {
      var n = norm(text);
      if (!n) return null;
      for (var i = 0; i < keys.length; i++) {
        if (n.indexOf(norm(keys[i])) !== -1) return page[keys[i]];
      }
      return null;
    }

    var MARK = 'data-hm-hint';

    // ---- Styles (inline so no site CSS dependency) ------------------------
    var css =
      '.hm-hint-btn{display:inline-block;width:1.15em;height:1.15em;margin-left:.45em;' +
      'border-radius:50%;border:1px solid #ff8c42;background:#0b0e14;color:#ff9e5e;' +
      'font-size:.78em;line-height:1;font-weight:700;cursor:pointer;padding:0;' +
      'vertical-align:middle;text-align:center}' +
      '.hm-hint-btn:hover,.hm-hint-btn:focus-visible{background:#ff8c42;color:#0b0e14;outline:2px solid #ff9e5e;outline-offset:2px}' +
      '.hm-hint{display:block;margin:.4em 0 .9em;padding:.5em .7em;max-width:36em;' +
      'font-size:.85em;line-height:1.45;color:#c9d4ea;background:rgba(255,140,66,.07);' +
      'border-left:2px solid #ff8c42;border-radius:0 8px 8px 0}';

    function ensureStyles() {
      if (document.getElementById('hm-hint-styles')) return;
      var st = document.createElement('style');
      st.id = 'hm-hint-styles';
      st.type = 'text/css';
      if (st.styleSheet) {
        st.styleSheet.cssText = css; // old IE safety, harmless elsewhere
      } else {
        st.appendChild(document.createTextNode(css));
      }
      (document.head || document.documentElement).appendChild(st);
    }

    // ---- Attachment -------------------------------------------------------
    function attachToLabel(label) {
      if (!label || label.getAttribute(MARK)) return;
      var hint = hintFor(label.textContent);
      if (!hint) return;
      label.setAttribute(MARK, 'attached');
      ensureStyles();

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'hm-hint-btn';
      btn.textContent = '?';
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Hint for: ' + norm(label.textContent));

      var box = document.createElement('div');
      box.className = 'hm-hint';
      box.setAttribute('hidden', '');
      box.textContent = hint;

      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', open ? 'false' : 'true');
        if (open) {
          box.setAttribute('hidden', '');
        } else {
          box.removeAttribute('hidden');
        }
      });

      if (label.parentNode) {
        label.parentNode.insertBefore(btn, label.nextSibling);
        label.parentNode.insertBefore(box, btn.nextSibling);
      }
    }

    function attachAll() {
      var i, els;

      // Standard <label> elements (includes JS-rendered forms).
      els = document.querySelectorAll('label');
      for (i = 0; i < els.length; i++) attachToLabel(els[i]);

      // Fallback: inputs whose aria-label acts as the field label.
      els = document.querySelectorAll('input[aria-label], select[aria-label]');
      for (i = 0; i < els.length; i++) {
        (function (el) {
          if (el.getAttribute(MARK)) return;
          var hint = hintFor(el.getAttribute('aria-label'));
          if (!hint) return;
          el.setAttribute(MARK, 'attached');
          ensureStyles();
          var wrap = document.createElement('span');
          wrap.style.display = 'inline-block';
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'hm-hint-btn';
          btn.textContent = '?';
          btn.setAttribute('aria-expanded', 'false');
          btn.setAttribute('aria-label', 'Hint for: ' + norm(el.getAttribute('aria-label')));
          var box = document.createElement('div');
          box.className = 'hm-hint';
          box.setAttribute('hidden', '');
          box.textContent = hint;
          btn.addEventListener('click', function () {
            var open = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', open ? 'false' : 'true');
            if (open) box.setAttribute('hidden', ''); else box.removeAttribute('hidden');
          });
          wrap.appendChild(btn);
          if (el.parentNode) {
            el.parentNode.insertBefore(wrap, el.nextSibling);
            wrap.appendChild(box);
          }
        })(els[i]);
      }
    }

    // ---- Boot --------------------------------------------------------------
    function boot() {
      try {
        attachAll();
      } catch (e) {
        /* silent */
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', boot);
    } else {
      boot();
    }
    // Re-run for forms rendered by the page's own scripts after load.
    setTimeout(boot, 800);
    setTimeout(boot, 2500);

  } catch (err) {
    /* Never break the page. */
  }
})();
