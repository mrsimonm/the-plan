#!/usr/bin/env python3
"""Bump the build number and the service-worker cache name together.

One number, one name: the whole point is that they can never drift again —
a phone reports BUILD.n and its SW cache is named for the SAME n, so "which
build is this phone running" has one answer.

    python3 tools/bump.py            # n+1, at=today, sw CACHE = v<n>
    python3 tools/bump.py --dry      # print what would change, change nothing

Edits index.html (the `const BUILD` stamp) and sw.js (the `CACHE` name).
Nothing else in either file is touched.
"""
import datetime, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
SW   = os.path.join(ROOT, "sw.js")

BUILD_RE  = re.compile(r'const BUILD=\{ver:"([0-9.]+)",n:([0-9]+),at:"[^"]*"\}')
CACHE_RE  = re.compile(r'const CACHE = "potting-bench-v([0-9]+)";')

def main():
    dry = "--dry" in sys.argv
    html = open(HTML, encoding="utf-8").read()
    sw   = open(SW, encoding="utf-8").read()

    m = BUILD_RE.search(html)
    if not m:
        sys.exit("could not find the BUILD stamp in index.html")
    ver, n = m.group(1), int(m.group(2))
    new_n = n + 1
    today = datetime.date.today().isoformat()

    c = CACHE_RE.search(sw)
    if not c:
        sys.exit("could not find the CACHE name in sw.js")
    if int(c.group(1)) == new_n:
        sys.exit("cache name already matches build %d — nothing to do" % new_n)

    new_build = 'const BUILD={ver:"%s",n:%d,at:"%s"}' % (ver, new_n, today)
    new_cache = 'const CACHE = "potting-bench-v%d";' % new_n
    html2 = BUILD_RE.sub(new_build, html, count=1)
    sw2   = CACHE_RE.sub(new_cache, sw, count=1)

    if html2 == html and sw2 == sw:
        print("no change (BUILD already bumped?)")
        return

    if dry:
        print("dry run — would set:")
        print("  index.html: " + new_build)
        print("  sw.js:      " + new_cache)
        return

    open(HTML, "w", encoding="utf-8").write(html2)
    open(SW, "w", encoding="utf-8").write(sw2)
    print("bumped to build %d; sw CACHE now %s" % (new_n, "potting-bench-v%d" % new_n))

if __name__ == "__main__":
    main()
