/* Honed Money — Recently-used tools (account-free, localStorage).
 * On calculator/tool pages only, records {title, url, ts} into the
 * "hm-recent" localStorage key (cap 6 entries, deduped by URL, newest first).
 * Everything is guarded so a localStorage failure (private mode etc.)
 * never breaks the page.
 */
(function () {
  "use strict";
  var KEY = "hm-recent";
  var MAX = 6;

  function isToolPage() {
    // Tool pages carry WebApplication structured data; hub/section/browse/
    // search/decide/about/contact/glossary and decision pages do not.
    try {
      var tags = document.querySelectorAll('script[type="application/ld+json"]');
      for (var i = 0; i < tags.length; i++) {
        var txt = tags[i].textContent || "";
        if (txt.indexOf('"@type":"WebApplication"') !== -1) return true;
      }
    } catch (e) { /* ignore */ }
    return false;
  }

  function load() {
    try {
      var raw = window.localStorage.getItem(KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) { return []; }
  }

  function save(list) {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(list));
    } catch (e) { /* ignore: private mode, quota, etc. */ }
  }

  function record() {
    if (!isToolPage()) return;
    var title = "";
    try {
      var h1 = document.querySelector("h1");
      title = (h1 && h1.textContent || document.title || "").trim();
    } catch (e) { title = ""; }
    if (!title) return;

    var url = "";
    try { url = window.location.pathname || ""; } catch (e) { url = ""; }
    if (!url) return;
    // Strip the file name so the canonical tool URL is stored.
    url = url.replace(/index\.html$/, "");
    if (url.charAt(url.length - 1) !== "/") url += "/";

    var now = Date.now();
    var list = load().filter(function (item) {
      return item && item.url && item.url !== url;
    });
    list.unshift({ title: title, url: url, ts: now });
    list = list.slice(0, MAX);
    save(list);
  }

  try {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", record);
    } else {
      record();
    }
  } catch (e) { /* never break the host page */ }
})();
