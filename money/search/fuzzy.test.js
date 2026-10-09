/* Validation: fuzzy scorer typo tolerance against the real search index.
 * Run: node money/search/fuzzy.test.js   (from ~/workspace/honedsignal-site)
 */
const assert = require("assert");
const path = require("path");
const fuzzy = require("./fuzzy.js");
const entries = require(path.join(__dirname, "..", "search-index.json"));

const cases = [
  // [query, expected pattern in a top-3 title, label]
  ["morgage", /mortgage/i, "typo: morgage -> mortgage"],
  ["rent", /rent/i, "exact: rent"],
  ["take home", /take.?home/i, "multi-word: take home"],
  ["retierment", /retire/i, "typo: retierment -> retirement"],
  ["bnpl", /bnpl/i, "acronym: bnpl"],
];

let failures = 0;
for (const [query, want, label] of cases) {
  const hits = fuzzy.suggest(entries, query, 6);
  console.log(`\n"${query}" (${label}) — ${hits.length} suggestion(s):`);
  hits.slice(0, 4).forEach((e, i) => {
    console.log(
      `  ${i + 1}. ${fuzzy.decodeEntities(e.t)}  [${e.kind}] ${e.u}` +
      `  score=${fuzzy.entryScore(query, e).toFixed(1)}`
    );
  });
  try {
    assert(hits.length > 0, "expected at least one suggestion");
    assert(
      hits.slice(0, 3).every((e) => e.kind === "tool"),
      "all top-3 suggestions must be kind=tool"
    );
    assert(
      hits.slice(0, 3).some((e) => want.test(fuzzy.decodeEntities(e.t))),
      `expected a top-3 title matching ${want}`
    );
    console.log("  PASS");
  } catch (err) {
    failures++;
    console.log("  FAIL:", err.message);
  }
}

// Edge cases
console.log("\nedge cases:");
const edge = [
  ["", 0, "empty query -> no suggestions"],
  ["x", 0, "1-char query -> no suggestions"],
  ["zzzzzzzzz", 0, "gibberish -> no suggestions"],
];
for (const [query, wantLen, label] of edge) {
  const n = fuzzy.suggest(entries, query, 6).length;
  const ok = n === wantLen;
  if (!ok) failures++;
  console.log(`  "${query}" -> ${n} suggestion(s)  ${ok ? "PASS" : "FAIL"} (${label})`);
}
// Non-tool entries must never be suggested
const housing = fuzzy.suggest(entries, "housing", 6);
const nonTool = housing.filter((e) => e.kind !== "tool");
if (nonTool.length) { failures++; console.log("  FAIL: non-tool suggestions leaked"); }
else console.log('  "housing" -> all suggestions are tools  PASS');

console.log(failures ? `\n${failures} FAILURE(S)` : "\nALL TESTS PASSED");
process.exit(failures ? 1 : 0);
