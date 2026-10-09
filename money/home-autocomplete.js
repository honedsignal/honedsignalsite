/* Honed Money — homepage search autocomplete.
 * Standalone variant reusing window.HonedFuzzy (fuzzy.js). Shows up to 6
 * tappable suggestions under the sticky homepage search as the user types.
 * Fully guarded: no-ops if fuzzy.js or the index can't load.
 */
(function () {
  "use strict";
  var DEBOUNCE_MS = 150;
  var MIN_CHARS = 2;
  var MAX_ITEMS = 6;

  try {
    var input = document.getElementById("calculator-search");
    if (!input || !window.HonedFuzzy) return;

    // Wrap the input so the dropdown positions under it.
    var wrap = document.createElement("div");
    wrap.className = "hm-ac-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    var box = document.createElement("div");
    box.className = "hm-ac-box";
    box.setAttribute("role", "listbox");
    box.setAttribute("aria-label", "Search suggestions");
    wrap.appendChild(box);

    var IDX = null;
    var items = [];
    var active = -1;
    var open = false;
    var timer = null;

    fetch("/money/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (j) { IDX = j; })
      .catch(function () { IDX = null; });

    function close() {
      open = false; active = -1; items = [];
      box.classList.remove("open"); box.innerHTML = "";
      input.setAttribute("aria-expanded", "false");
    }

    function esc(s) {
      return String(s == null ? "" : s).replace(/&/g, "&amp;")
        .replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function render() {
      var html = "";
      for (var i = 0; i < items.length; i++) {
        var e = items[i];
        html += '<a class="hm-ac-item' + (i === active ? " active" : "") + '"' +
          ' role="option" aria-selected="' + (i === active) + '"' +
          ' href="' + esc(e.u) + '">' +
          '<span class="hm-ac-t">' + esc(e.t) + "</span>" +
          '<span class="hm-ac-d">' + esc(e.d || "") + "</span></a>";
      }
      box.innerHTML = html;
      open = items.length > 0;
      box.classList.toggle("open", open);
      input.setAttribute("aria-expanded", open ? "true" : "false");
    }

    function update() {
      var v = input.value.trim();
      if (!IDX || v.length < MIN_CHARS) { close(); return; }
      try {
        items = window.HonedFuzzy.suggest(IDX, v, MAX_ITEMS);
      } catch (e) { items = []; }
      active = -1;
      render();
    }

    function schedule() {
      clearTimeout(timer);
      timer = setTimeout(update, DEBOUNCE_MS);
    }

    input.addEventListener("input", schedule);
    input.addEventListener("blur", function () { setTimeout(close, 150); });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { close(); return; }
      if (!open) return;
      if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
        ev.preventDefault();
        var nodes = box.querySelectorAll(".hm-ac-item");
        active = ev.key === "ArrowDown"
          ? (active + 1 >= items.length ? 0 : active + 1)
          : (active - 1 < 0 ? items.length - 1 : active - 1);
        for (var n = 0; n < nodes.length; n++) {
          nodes[n].classList.toggle("active", n === active);
          nodes[n].setAttribute("aria-selected", n === active ? "true" : "false");
        }
      } else if (ev.key === "Enter" && active >= 0 && items[active]) {
        ev.preventDefault();
        location.href = items[active].u;
      }
    });
    document.addEventListener("click", function (ev) {
      if (!wrap.contains(ev.target)) close();
    });
  } catch (e) { /* never break the homepage */ }
})();
