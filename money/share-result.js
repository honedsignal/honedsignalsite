/* Honed Money — Share result via phone share sheet.
 * Adds a "Share" button next to the existing Email/Copy/CSV actions on
 * calculator pages. Uses navigator.share() so it opens the phone's native
 * share sheet. The button only renders when navigator.share exists
 * (mobile browsers); on desktop nothing is added and nothing breaks.
 * IIFE, dependency-free, everything try/catch guarded. */
(function () {
  'use strict';

  function init() {
    try {
      if (!document || !document.getElementById) return;
      // Already added (idempotent double-run guard).
      if (document.getElementById('shareResults')) return;
      // Desktop or unsupported browser: do nothing, no button.
      if (typeof navigator === 'undefined' || typeof navigator.share !== 'function') return;

      var anchorIds = [
        'emailResults', 'copyResults', 'downloadCsv',
        'emailButton', 'copyButton', 'downloadButton',
        'emailBtn', 'copyBtn', 'exportBtn'
      ];
      var container = null, anchor = null, i;
      for (i = 0; i < anchorIds.length; i++) {
        try { anchor = document.getElementById(anchorIds[i]); } catch (e) { anchor = null; }
        if (anchor) break;
      }
      if (anchor && anchor.parentNode && anchor.parentNode.nodeType === 1 &&
          anchor.parentNode !== document.body) {
        container = anchor.parentNode;
      }
      if (!container) {
        var selectors = ['.result-actions', '.actions', '.result-tools', '.action-row', '.actions-row'];
        for (i = 0; i < selectors.length; i++) {
          try { container = document.querySelector(selectors[i]); } catch (e) { container = null; }
          if (container) break;
        }
      }
      if (!container || !container.appendChild) return;

      // Copy the class list of an existing sibling action so the button
      // matches the page's own styling, whatever variant it uses
      // (.action, .text-btn, .download, .copy-results, ...).
      var btnClass = 'action';
      try {
        var siblings = container.querySelectorAll('button, a');
        for (i = 0; i < siblings.length; i++) {
          var c = siblings[i].getAttribute && siblings[i].getAttribute('class');
          if (c && c.replace(/\s+/g, '')) { btnClass = c; break; }
        }
      } catch (e) { /* keep default */ }

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.id = 'shareResults';
      btn.setAttribute('class', btnClass);
      btn.textContent = 'Share';
      btn.setAttribute('aria-label', 'Share these results');

      function shareText() {
        try {
          var ids = [
            'resultSummary', 'projectionSummary', 'summaryText', 'explainSummary',
            'explanationText', 'summaryCopy', 'utilSummary', 'paymentSummary',
            'savingsCopy', 'resultsExplanation', 'explainCopy', 'headline-note'
          ];
          for (var j = 0; j < ids.length; j++) {
            var el = null;
            try { el = document.getElementById(ids[j]); } catch (e) { el = null; }
            if (el && el.textContent && el.textContent.replace(/\s+/g, '')) {
              return el.textContent.replace(/\s+/g, ' ').trim().slice(0, 2000);
            }
          }
          var meta = document.querySelector('meta[name="description"]');
          if (meta && meta.getAttribute) {
            var d = meta.getAttribute('content');
            if (d && d.replace(/\s+/g, '')) return d.trim().slice(0, 2000);
          }
        } catch (e) { /* fall through */ }
        return '';
      }

      btn.addEventListener('click', function () {
        try {
          var data = { title: document.title, text: shareText(), url: location.href };
          var p = navigator.share(data);
          if (p && typeof p.catch === 'function') {
            p.catch(function () { /* user cancelled or share failed: silent */ });
          }
        } catch (e) { /* user cancelled or share failed: silent */ }
      });

      container.appendChild(btn);
    } catch (e) { /* never break the page */ }
  }

  try {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  } catch (e) { /* never break the page */ }
})();
