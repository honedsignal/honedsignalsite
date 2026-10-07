#!/usr/bin/env python3
"""Structural QA for Honed Money tool pages. Usage: qa.py <dir> [<dir>...]"""
import re, sys, os, glob

CHECKS = []
def check(files):
    fails = 0
    for f in sorted(files):
        doc = open(f, encoding="utf-8").read()
        name = os.path.basename(os.path.dirname(f))
        errs = []
        # 1. mobile viewport
        if 'name="viewport"' not in doc:
            errs.append("missing viewport")
        # 2. static back link to /money/
        m = re.search(r'<a[^>]*href="/money/"[^>]*>(.*?)</a>', doc, re.S)
        if not m:
            errs.append("missing ← Honed Money link")
        else:
            tag = re.search(r'<a[^>]*href="/money/"[^>]*>', doc).group(0)
            if "←" not in m.group(1):
                errs.append("back link missing ←")
            if re.search(r"position\s*:\s*(fixed|sticky)", doc):
                errs.append("floating/sticky positioning found")
        # 3. email button (mailto)
        if "mailto:" not in doc:
            errs.append("missing mailto email")
        # 4. copy control
        if not re.search(r"[Cc]opy results|navigator\.clipboard|execCommand\(\s*['\"]copy", doc):
            errs.append("missing copy control")
        # 5. explain control
        if not re.search(r"[Ee]xplain (these|the) results", doc):
            errs.append("missing explain control")
        # 6. no hardcoded numeric values on number inputs
        for im in re.finditer(r'<input[^>]*type="(number|text)"[^>]*>', doc):
            tag = im.group(0)
            vm = re.search(r'value="([^"]*)"', tag)
            if vm and re.search(r"\d", vm.group(1)):
                errs.append(f"hardcoded input value: {vm.group(1)[:20]}")
                break
        # 7. orange email button styling hint
        if not re.search(r"--orange", doc):
            errs.append("missing orange var (email btn?)")
        if errs:
            fails += 1
            print(f"FAIL {name}: {'; '.join(errs)}")
        else:
            print(f"ok   {name}")
    print(f"\n{len(files)-fails}/{len(files)} passed")
    return fails

files = []
for d in sys.argv[1:]:
    files += glob.glob(os.path.join(d, "*/index.html"))
sys.exit(1 if check(files) else 0)
