/* Honed Money fuzzy scorer — dependency-free typo-tolerant matching.
 *
 * Shared between the browser autocomplete (window.HonedFuzzy) and node
 * tests (module.exports). Only scores entries with kind === "tool".
 */
(function (root) {
  "use strict";

  // Titles in search-index.json carry multi-level HTML entity escaping
  // (e.g. "&amp;amp;amp;..."), so decode repeatedly before matching.
  function decodeEntities(s) {
    s = String(s);
    var prev, n = 0;
    do {
      prev = s;
      s = s
        .replace(/&amp;/g, "&")
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&quot;/g, '"')
        .replace(/&#39;|&apos;/g, "'");
      n++;
    } while (s !== prev && n < 12);
    return s;
  }

  function norm(s) {
    return decodeEntities(s).toLowerCase().replace(/\s+/g, " ").trim();
  }

  /* Subsequence score: every character of q appears in order in text.
   * Rewards consecutive runs and early, compact matches (typo tolerance
   * for missing/transposed letters, e.g. "morgage" -> "mortgage").
   * Returns 0 when q is not a subsequence of text. */
  function subseqScore(q, text) {
    var qi = 0, score = 0, run = 0, first = -1, last = -1;
    for (var i = 0; i < text.length && qi < q.length; i++) {
      if (text[i] === q[qi]) {
        if (first === -1) first = i;
        if (last === i - 1) { run++; score += 8 + run * 3; }
        else { run = 0; score += 6; }
        last = i;
        qi++;
      }
    }
    if (qi < q.length) return 0;
    var span = last - first + 1;
    score -= span * 0.6;   // penalize spread-out matches
    score -= first * 0.4;  // prefer matches that start early
    return score > 0 ? score : 0.5;
  }

  function wordBoundaryBonus(word, field) {
    var idx = field.indexOf(word);
    if (idx === -1) return 0;
    if (idx === 0) return 30;
    return /[^a-z0-9]/.test(field.charAt(idx - 1)) ? 22 : 0;
  }

  /* Score one query word against one field.
   * Exact substring match earns a big bonus (weighted by field);
   * otherwise score each word-token of the field and take the best:
   * a small-edit match (Damerau-Levenshtein, catches transpositions
   * like "retierment" -> "retirement") outranks a loose subsequence. */
  function fieldScore(word, field, weight) {
    if (field.indexOf(word) !== -1) {
      return (110 + wordBoundaryBonus(word, field)) * weight;
    }
    var tokens = field.split(/[^a-z0-9]+/);
    var thresh = editThreshold(word);
    var best = 0;
    for (var i = 0; i < tokens.length; i++) {
      var tok = tokens[i];
      if (!tok || tok.length < 2) continue;
      var cand = 0;
      if (thresh > 0 && Math.abs(tok.length - word.length) <= thresh) {
        var d = damerau(word, tok, thresh);
        if (d <= thresh) cand = 85 - d * 18;
      }
      if (cand === 0) {
        var s = subseqScore(word, tok);
        if (s > 0) cand = Math.min(s, 60);
      }
      if (cand > best) best = cand;
    }
    return best * weight;
  }

  /* How many edits to tolerate for a query word, by length.
   * Short words get none: edit matching on 2-3 letter words is noise. */
  function editThreshold(word) {
    if (word.length >= 7) return 2;
    if (word.length >= 4) return 1;
    return 0;
  }

  /* Optimal string alignment (restricted Damerau-Levenshtein) with an
   * early-out cap: adjacent transposition counts as a single edit. */
  function damerau(a, b, maxDist) {
    var la = a.length, lb = b.length;
    if (Math.abs(la - lb) > maxDist) return maxDist + 1;
    var d = [];
    var i, j;
    for (i = 0; i <= la; i++) d[i] = [i];
    for (j = 1; j <= lb; j++) d[0][j] = j;
    for (i = 1; i <= la; i++) {
      for (j = 1; j <= lb; j++) {
        var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
        d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
        if (i > 1 && j > 1 &&
            a.charAt(i - 1) === b.charAt(j - 2) &&
            a.charAt(i - 2) === b.charAt(j - 1)) {
          d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
        }
      }
    }
    return d[la][lb];
  }

  /* Total score for a query against one index entry.
   * Every query word must match somewhere (title, tags, or description),
   * otherwise the entry scores 0 and is excluded. */
  function entryScore(query, entry) {
    var words = norm(query).split(" ").filter(Boolean);
    if (!words.length) return 0;
    var title = norm(entry.t || "");
    var desc = norm(entry.d || "");
    var tags = norm((entry.tags || []).join(" "));
    var total = 0;
    for (var i = 0; i < words.length; i++) {
      var best = Math.max(
        fieldScore(words[i], title, 3),
        fieldScore(words[i], tags, 2),
        fieldScore(words[i], desc, 1)
      );
      if (best <= 0) return 0;
      total += best;
    }
    return total;
  }

  function suggest(entries, query, limit) {
    limit = limit || 6;
    if (!query || norm(query).length < 2) return [];
    var scored = [];
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      if (e.kind !== "tool") continue; // tools only: skip section/decision entries
      var s = entryScore(query, e);
      if (s > 0) scored.push({ e: e, s: s });
    }
    scored.sort(function (a, b) {
      return b.s - a.s || (a.e.t < b.e.t ? -1 : a.e.t > b.e.t ? 1 : 0);
    });
    return scored.slice(0, limit).map(function (x) { return x.e; });
  }

  var api = {
    decodeEntities: decodeEntities,
    subseqScore: subseqScore,
    entryScore: entryScore,
    suggest: suggest
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.HonedFuzzy = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
