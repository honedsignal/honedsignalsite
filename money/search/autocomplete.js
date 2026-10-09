/* Honed Money search autocomplete — typo-tolerant suggestions dropdown.
 *
 * Enhancement over the existing full search: shows up to 6 tappable
 * suggestions (title + one-line description) as the user types.
 * Depends on window.HonedFuzzy (fuzzy.js) and the page's IDX array,
 * which the page fetches once from /money/search-index.json and caches.
 * The existing render()-based full search is left untouched.
 */
(function () {
  "use strict";
  var DEBOUNCE_MS = 150;
  var MIN_CHARS = 2;
  var MAX_ITEMS = 6;

  var input = document.getElementById("q");
  var box = document.getElementById("ac");
  if (!input || !box || !window.HonedFuzzy) return;

  var items = [];
  var active = -1;
  var open = false;
  var timer = null;

  function hasIndex() {
    return typeof IDX !== "undefined" && IDX && IDX.length;
  }

  function close() {
    open = false;
    active = -1;
    items = [];
    box.classList.remove("open");
    box.innerHTML = "";
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  }

  function render() {
    var html = "";
    for (var i = 0; i < items.length; i++) {
      var e = items[i];
      html +=
        '<a class="ac-item' + (i === active ? " active" : "") + '"' +
        ' role="option" id="ac-opt-' + i + '"' +
        ' aria-selected="' + (i === active ? "true" : "false") + '"' +
        ' href="' + e.u + '">' +
        '<span class="ac-t">' + e.t + "</span>" +
        '<span class="ac-d">' + (e.d || "") + "</span></a>";
    }
    box.innerHTML = html;
    open = items.length > 0;
    box.classList.toggle("open", open);
    input.setAttribute("aria-expanded", open ? "true" : "false");
    if (!open) input.removeAttribute("aria-activedescendant");
  }

  function setActive(i) {
    active = i;
    var nodes = box.querySelectorAll(".ac-item");
    for (var n = 0; n < nodes.length; n++) {
      var on = n === i;
      nodes[n].classList.toggle("active", on);
      nodes[n].setAttribute("aria-selected", on ? "true" : "false");
    }
    if (i >= 0) {
      input.setAttribute("aria-activedescendant", "ac-opt-" + i);
      if (nodes[i] && nodes[i].scrollIntoView) {
        nodes[i].scrollIntoView({ block: "nearest" });
      }
    } else {
      input.removeAttribute("aria-activedescendant");
    }
  }

  function update() {
    var v = input.value.trim();
    if (!hasIndex() || v.length < MIN_CHARS) {
      close();
      return;
    }
    items = window.HonedFuzzy.suggest(IDX, v, MAX_ITEMS);
    active = -1;
    render();
  }

  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(update, DEBOUNCE_MS);
  }

  input.addEventListener("input", schedule);

  input.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") {
      close();
      return;
    }
    if (!open) {
      // Let the user open the dropdown with ArrowDown without waiting
      // for the debounce; otherwise leave keys to the page as before.
      if (ev.key === "ArrowDown" && input.value.trim().length >= MIN_CHARS) {
        clearTimeout(timer);
        update();
        ev.preventDefault();
      }
      return;
    }
    if (ev.key === "ArrowDown") {
      setActive(active + 1 >= items.length ? 0 : active + 1);
      ev.preventDefault();
    } else if (ev.key === "ArrowUp") {
      setActive(active - 1 < 0 ? items.length - 1 : active - 1);
      ev.preventDefault();
    } else if (ev.key === "Enter") {
      if (active >= 0 && items[active]) {
        // A suggestion is highlighted: go straight to the tool.
        ev.preventDefault();
        location.href = items[active].u;
      }
      // Otherwise: leave default behavior alone (full search unchanged).
    }
  });

  // Hide on blur, but wait a beat so a tap/click on a suggestion lands.
  input.addEventListener("blur", function () {
    setTimeout(close, 150);
  });

  // Called by the page once the search index finishes loading, so a query
  // typed before the fetch resolves still gets suggestions.
  window.__acIndexReady = function () {
    if (input.value.trim().length >= MIN_CHARS) update();
  };
})();
