/* Honed Signal theme kit — resolver + toggle controller.
   Contract (see THEME-KIT.md):
   - localStorage key "hs-theme": "dark" | "light" | "system".
   - No saved choice -> Dark (the site default, Freddie's decision 2026-11-18).
   - "system" is an explicit, persisted choice: it follows
     prefers-color-scheme and keeps following it live.
   - The resolved theme lands on <html data-theme="dark"|"light"> before
     first paint (this file is loaded synchronously in <head>).
   This file is shared by every themed page; do not fork it per page. */
(function () {
  "use strict";
  var root = document.documentElement;
  var KEY = "hs-theme";
  var mq = window.matchMedia("(prefers-color-scheme: dark)");

  function storedMode() {
    try {
      var v = window.localStorage.getItem(KEY);
      if (v === "dark" || v === "light" || v === "system") return v;
    } catch (e) { /* storage unavailable — fall through to the default */ }
    return null;
  }
  function currentMode() {
    return storedMode() || "dark";
  }
  function resolvedTheme(mode) {
    if (mode === "system") return mq.matches ? "dark" : "light";
    return mode;
  }
  function apply() {
    var mode = currentMode();
    var theme = resolvedTheme(mode);
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-theme-mode", mode);
    root.style.colorScheme = theme;
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#0B0E14" : "#FAF8F4");
    return { mode: mode, theme: theme };
  }

  apply();
  if (mq.addEventListener) {
    mq.addEventListener("change", function () {
      if (currentMode() === "system") apply();
    });
  }

  function init() {
    var switches = document.querySelectorAll("[data-hs-theme-switch]");
    switches.forEach(function (sw) {
      var buttons = sw.querySelectorAll("[data-theme-choice]");
      function sync() {
        var state = apply();
        buttons.forEach(function (btn) {
          btn.setAttribute(
            "aria-pressed",
            btn.getAttribute("data-theme-choice") === state.mode ? "true" : "false"
          );
        });
        var note = document.getElementById("os-note");
        if (note) {
          if (state.mode === "system") {
            note.textContent = "Following your system setting — currently " + state.theme;
          } else if (storedMode()) {
            note.textContent =
              "Manual override: " + state.mode + " (System returns to your OS setting)";
          } else {
            note.textContent = "Site default: dark (System follows your OS setting)";
          }
        }
      }
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            window.localStorage.setItem(KEY, btn.getAttribute("data-theme-choice"));
          } catch (e) { /* choice lasts for this view only */ }
          sync();
        });
      });
      sync();
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
