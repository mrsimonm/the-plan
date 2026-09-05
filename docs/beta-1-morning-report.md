# Good morning — beta-1 is tagged ☕

**Short version:** everything on the release list that code could fix is done, tested, and on `main`. The build is tagged **`beta-1`**. There is one 2-minute thing only you can do (a Google login), and a few human-only checks.

---

## What changed while you slept (all live on the web build, v1.0.58)

**You'll see these on your phone**
- Academy now says the real plant count (~1,074, was "158") and has a **Browse all** tile.
- All **six tabs fit** on a phone screen — Library and Stats aren't hidden anymore.
- The floating Notes buttons only appear where they belong, with a first-use label, and never cover the bottom of a list.
- Tapping the version chip opens an **About / What's-new** sheet (build, sync state, last backup, Copy diagnostics).
- Czech placeholders in Settings are now Czech. A favicon shows in the tab.
- TeachBench nudges "save a backup now" when the first student is added, and shows the last backup date. Every export stamps a date.

**Under the hood**
- **Error capture** — errors are recorded on-device; "Copy diagnostics" in About gives you a JSON you can paste to me. Silent failures now show a badge instead of vanishing.
- **One version number** (`v1.0.58`, SW cache v58), kept in sync by `tools/bump.py`; users get a "reload for new version" toast.
- **Storage-nearly-full warning** before data can be lost.
- **Firebase no longer loads on first launch** — a fresh boot makes exactly two requests, both to your own site, zero to Google. Verified twice, independently.
- **Security hardening** from a full XSS scan: routine names escaped, photo `src` gated to real image data, imported/synced ids sanitised at one choke point, `esc()` widened. Attack payloads tested on a phone viewport — nothing executes.
- **Smoke test gate** (`tools/smoke/smoke.sh`): boots all 17 screens at phone size and fails on any console error. Passes 17/17 on the tagged build.

**Commits (main):** `c1b3937 db77f68 06f81e3 2b46e31 98d22f9 · 5fcf65b bf99655 f49e510 71624a7 · 138d35d 33a8a4e 69733da faf88e7 · 405a491 · 1322079` → tag `beta-1`.

---

## One correction to the plan
There is **no desktop app to rebuild**. "Munder Difflin v0.4.6" is the *agent-office harness*, not Potting Bench. The plant app is web/PWA only — that's the surface your customers get. Closed that item as not applicable.

---

## Needs you (in order)

1. **`firebase login`** in a terminal (if `firebase` isn't found: `export PATH="$HOME/.local/node/bin:$PATH"` first). Then tell me **done** — Dwight publishes the Firestore/Storage rules with one command. *Why: if the rules in the console are stale, TeachBench streaks silently fail.*
2. **Decide the beta offering:** plants only, or plants + TeachBench?
3. **Pick the first customers** (how many, Czech/English, which phones).
4. **One real pilot lesson** — teacher adds cards, a student reviews on their own phone.
5. **Real-phone keyboard check** — does the keyboard cover inputs in add-plant / planner quick-add?

**Also still waiting on you (not release-blocking):** the Planner block-categories spec review · DeepSeek finish (A or B) · Margo's retest of the TeachBench fix.

---

## Deferred on purpose (post-beta)
Photos to IndexedDB (bigger job) · Czech dictionary gap scan · `watchLang` performance · TeachBench roster traffic-light · a small data-layer test suite.

Team is stood down. Nothing is running, nothing is broken.
