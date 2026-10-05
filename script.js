// Honed Signal v1 — minimal JS. CSS handles smooth scroll in modern
// browsers; this is a fallback for older ones.
(function () {
  "use strict";

  if ("scrollBehavior" in document.documentElement.style) return;

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      var target = document.querySelector(link.getAttribute("href"));
      if (target) {
        event.preventDefault();
        window.scrollTo(0, target.getBoundingClientRect().top + window.pageYOffset);
      }
    });
  });
})();
