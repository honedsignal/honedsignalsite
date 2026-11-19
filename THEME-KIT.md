# Honed Signal Theme Kit

System / Light / Dark theming for honedsignal.com, rolled out in tranches.
Approved by Freddie, Nov 18, 2026. **Default theme is Dark** — that is a
brand decision, not a technical default. Tranche 0+1 (pilot): homepage +
Reports section. Later tranches reuse this document verbatim.

## The contract

- **Storage:** `localStorage` key `hs-theme`, values `dark` | `light` |
  `system`. No saved value = **Dark**.
- **Resolution** (runs in `<head>`, before first paint, from `/theme.js`):
  saved `light`/`dark` wins → that theme. Saved `system` → follow
  `prefers-color-scheme`, and keep following it live (media-query change
  listener). Nothing saved → `data-theme="dark"`.
- **Markup:** the resolved theme is `data-theme="dark" | "light"` on
  `<html>`; the chosen mode is mirrored on `data-theme-mode`. Pages ship
  with `data-theme="dark"` in the HTML so even no-JS renders the default.
- **`color-scheme`** follows the resolved theme (`/theme.css` pins it;
  `/theme.js` also sets it inline and updates the `theme-color` meta:
  dark `#0B0E14`, light `#FAF8F4`).
- **Print always renders light.** Every themed page carries a print block
  that forces its light variable values with `!important` under
  `html[data-theme="dark"]`, and the toggle is `display:none` in print.

## Shared files (do not fork per page)

- `/theme.js` — resolver + toggle controller. Load synchronously in
  `<head>` before the page's stylesheets.
- `/theme.css` — the segmented-control styling + `color-scheme` pinning.
  The control is a fixed navy pill in both themes (`#F5F5F5` on `#161C28`,
  selected = `#F5F5F5` bg / `#0B0E14` text, focus outline `#2EC4B6` 3px) —
  AA in both themes by construction, independent of page theme.

## Toggle markup (paste into the page's header/nav chrome)

```html
<div class="hs-theme-switch" data-hs-theme-switch>
  <div class="hs-theme-seg" role="group" aria-label="Page theme">
    <button type="button" data-theme-choice="system" aria-pressed="false">System</button>
    <button type="button" data-theme-choice="light" aria-pressed="false">Light</button>
    <button type="button" data-theme-choice="dark" aria-pressed="true">Dark</button>
  </div>
</div>
```

`/theme.js` wires every `[data-hs-theme-switch]` on the page, persists
clicks to `hs-theme`, and keeps `aria-pressed` in sync with the mode.

## Page CSS pattern

Each page keeps its own variable names; the kit only fixes how the two
themes are keyed:

```css
:root { /* light values — also the no-JS fallback */ color-scheme: light; }
html[data-theme="dark"] { /* dark values */ color-scheme: dark; }
```

Never key theme rules off `@media (prefers-color-scheme: dark)` any more —
that made the OS, not the reader's saved choice, decide. (The dark-mode
report page is the one partial exception in CSS: its dark block is
`:root[data-theme="dark"]`, already attribute-keyed.)

### Palettes (locked; do not drift)

- **Dark:** navy `#0B0E14` family — surfaces `#12161F` / `#171C27`, ink
  `#F0EEE8`, soft `#C3C8D2`, faint `#8B919E`, line `#262C38`, orange
  `#FF6B35`, teal `#2EC4B6`.
- **Light:** warm paper `#FAF8F4` family — the values already proven on
  the existing light pages (see `reports/exactly-8-arms` `:root`):
  surface `#FFFFFF`, surface-2 `#EFEDE8`, ink `#14161C`, soft `#454A55`,
  faint `#6D7280`, line `#D9D5CC`, orange `#D96E00` (strong `#A34E00`),
  teal `#0D7A6E` (strong `#0A665C`). Homepage light uses ink `#171A21`,
  surface `#FFFDF8`, muted `#5C6572` (from the dark-mode report page).

## Per-page notes (pilot)

- **Homepage** (`index.html` + shared `style.css`): `style.css` gained
  `--bg/--text/--line/--line-strong/--header-bg/--cta-bg/--cta-text/
  --orange-strong` variables; dark values are the original hexes, so the
  12 other pages that link `style.css` but have no resolver are
  byte-for-byte unaffected (light rules only fire under
  `html[data-theme="light"]`). Toggle sits in a `.hs-theme-bar` row
  inside the site header.
- **Reports index** (`reports/index.html`): was dark-only with hard-coded
  colors; light treatments are `html[data-theme="light"]` overrides in
  its inline style. Toggle sits in the top nav next to the back link.
- **Report articles** (`meta-publishing`, `california-music-economy`,
  `exactly-8-arms`, `bowlwatch`, `bowlwatch/recheck-log`): their
  `@media (prefers-color-scheme: dark)` variable blocks were re-keyed to
  `html[data-theme="dark"]` (including exactly-8-arms' `article` component
  variables and `.pill-yes`). Their heroes stay navy in both themes by
  design (`--hero-bg`). Toggle sits in the `.hs-util` bar after the back
  link. Print: the existing print block already forced hero/bg light;
  an appended print block forces the remaining light variables.
- **Dark-mode report** (`reports/dark-mode/`): already attribute-keyed;
  its page-local resolver/controller were replaced by `/theme.js` and
  its buttons now carry `data-theme-choice`. Default changed from
  System to the uniform site rule: **Dark**. Its hard-coded dark
  components (scoreboard, badges, play buttons, 60-30-10 bar) already
  had explicit light print versions and variable-driven screen colors.
- **404.html: not themed.** It shares no header/nav chrome (standalone
  centered card, no nav), so there is no existing chrome to hold the
  toggle; revisit if it ever gets the standard header.
- **Pre-existing mobile overflows (not theme-caused, verified identical
  on HEAD before the pilot):** homepage `.nav-links` row overflows
  390px by ~77px in both themes, and `bowlwatch/recheck-log` prose
  URLs overflow 390px by ~404px in both themes. The pilot added zero
  new overflow; fixing either is a separate layout job.

## QA checklist for every new tranche page

Headless Chromium against a local server, per page:

1. First visit (empty storage) renders **dark** at any OS setting.
2. Light choice persists across pages (same origin) and across reload.
3. System follows OS emulation both ways, live and after reload.
4. No horizontal overflow at 1280px and 390px in either theme.
5. Heroes full-display, uncropped, in both themes (aspect-ratio sizing,
   never fixed-height cover crops).
6. Toggle is keyboard-focusable; focus outline visible in both themes.
7. Print preview renders light with the toggle hidden.
8. Eyeball light mode for dark-on-light breakage: invisible text, dark
   badges with dark text, illegible charts, hard-coded dark components.
