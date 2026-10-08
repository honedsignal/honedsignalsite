# Honed Money — Third-Party Audit Briefing Template

Use this document when asking another AI to audit honedsignal.com/money/.
Copy the sections below into your prompt. Fill in the bracketed fields.

---

## 1. What you're auditing

Honed Money is a static finance-calculator suite at **https://honedsignal.com/money/**.
- **[NUMBER] free calculators** across 21 sections (verify the count yourself — don't trust this number)
- Each calculator is a standalone HTML page with client-side JavaScript — no backend, no API calls for math
- Global keyword search at /money/search/, browse at /money/browse/, Decision Center (guided paths) at /money/decide/
- Financial glossary, trust pages (/money/legal/, /privacy/, /about/, /contact/), proper 404s
- PWA: manifest, service worker, installable on mobile, works offline after first visit

## 2. How to test (do this, not shortcuts)

- **Load the actual page in a real browser.** Don't just fetch the HTML — the calculators run JavaScript. If your page-fetcher can't execute JS, say so explicitly instead of reporting the page as broken.
- **Run each calculator with realistic inputs.** Enter values, click calculate, verify the output math by hand.
- **Test validation:** enter bad inputs (negative numbers, text, empty fields). Every calculator must show a clear error, not silently fail or produce NaN.
- **Test on mobile viewport** (375px wide). Check that forms, results, and buttons are usable — no overlapping text, no cut-off inputs.
- **Check the "What's next?" cross-links** at the bottom of each calculator — they should point to real, related tools.
- **Verify metadata:** each page needs a unique `<title>`, meta description, and canonical URL.

## 3. What NOT to do (lessons from past audits)

- **Do NOT mistake your own tool limitations for site defects.** If your fetcher can't load a page or execute JavaScript, that's YOUR limitation — report it as "could not test" not "broken."
- **Do NOT trust HTTP status codes alone.** This site has soft fallbacks — a dead calculator can return 200 with an empty page. You must verify the calculator actually works.
- **Do NOT audit from cached or stale data.** Check the live site, not your training data or a cached copy.
- **Do NOT skip the math.** Re-derive at least the core formula for each calculator you test. A calculator that runs but computes wrong is worse than one that's visibly broken.

## 4. What to report

For each issue, provide:
1. **URL** of the affected page
2. **What's wrong** (one sentence)
3. **How to reproduce** (exact steps)
4. **Severity:** Critical (wrong math, data loss) / Major (broken on mobile, validation missing) / Minor (typo, cosmetic)

Also report:
- Total calculators tested vs. total on site
- Any pages you could NOT test and why
- Overall verdict in one paragraph

## 5. Scope and depth: [FILL IN SECTIONS]

**Default expectation is FULL COVERAGE unless the scope says otherwise.** That means:

- Every calculator page: load it, run it with realistic inputs, verify the math, test validation with bad inputs, check mobile layout
- Every section page: verify all listed tools link to real pages
- Homepage, browse, search, Decision Center, glossary, trust pages: load and spot-check
- Every "What's next?" link: click through and confirm the target exists
- Search index vs. reality: every URL in /money/search-index.json must resolve to a working page
- Sitemap vs. reality: every URL in /sitemap.xml must resolve

Do not sample. Do not spot-check a few and extrapolate. Touch everything in scope.
If the scope is the full site, that means all 115+ calculators. Budget your work accordingly
and report progress if you can't finish in one pass — but don't silently skip pages.

## 6. Feature and gap ideas

After the audit, step back and think like a product person. Based on everything you touched:

- **Missing tools:** Are there obvious calculators that should exist but don't? (e.g. a section has 3 tools but competitors cover 8)
- **Thin sections:** Any section that feels underbuilt compared to the others?
- **Missing features:** Anything the site itself should do but doesn't? (e.g. comparison mode, saved results, print-friendly output)
- **Content gaps:** Glossary terms that should exist but don't? Decision paths that should exist but don't?
- **UX improvements:** Anything that would make the tools easier to find, use, or share?

For each idea, give one sentence on what it is and one sentence on why it matters.
Separate these clearly from the bug report — they're suggestions, not defects.
Be opinionated. If you think something's a bad idea, say so and why.

---

## Appendix: Site structure reference

- Homepage: /money/ (shows total calculator count — verify it matches reality)
- Search index: /money/search-index.json (source of truth for tool URLs)
- Sitemap: /sitemap.xml
- Section pages: /money/{section}/ (e.g. /money/taxes/, /money/students/)
- Tool pages: /money/{tool-slug}/ (e.g. /money/tax-bracket-calculator/)
- Decision paths: /money/decide/{slug}/ (10 guided paths)

## Appendix: Known good patterns

- Every calculator page has: hero image, input form, results panel, "What's next?" links, legal disclaimer, "Last reviewed" date
- Art style: dark navy background, orange/teal palette, flat-cartoon storybook illustrations
- Back-to-hub link: plain "← Honed Money" at the top of every page
