# Beta release checklist — merged & ordered

> ## RELEASE STATUS — `beta-1` tagged on `1322079` (2026-09-05 03:00)
> - **Gates 1–8, 10 ✅** shipped on `main`: `c1b3937 db77f68 06f81e3 2b46e31 98d22f9` (Wave 1) · `5fcf65b bf99655 f49e510 71624a7` (Wave 2) · `138d35d 33a8a4e 69733da faf88e7` (Wave 3 + esc hardening + favicon) · `405a491` smoke gate · `1322079` firebase.json/.firebaserc.
> - **Gate 9 — NOT APPLICABLE.** There is no desktop build of this app: `/Applications/Munder Difflin.app` (v0.4.6) is the *agent harness*, not Potting Bench. The web/PWA build is the only customer surface (audit item R3 was a conflation).
> - **Final proof:** smoke 17/17 PASS on `1322079`; a fresh unsynced 360px boot makes exactly two same-origin requests and **zero** Google/Firebase requests.
> - **Deferred to post-beta:** IndexedDB photo storage (B3, >M) · Czech dict-vs-UI gap scan · `watchLang` perf (R8) · roster traffic-light (N3) · data-layer test seed (R7).
> - **Owner items still open:** C (`firebase login` → rules deploy is one command), A, B, D, E.

- **Date:** 2026-09-05 · **Sources:** `docs/beta-readiness-meredith.md` (engineering, ids B/R/N) + `docs/beta-readiness-ux.md` (customer walkthrough on a 360px phone, ids U/N-). Both are read-only surveys of HEAD `43f119f`; nothing below has been implemented yet.
- **Correction to earlier messages:** the plant catalogue is **already merged and live (~1,074 species, commit `cb27e1b`)**. The only bug is a stale counter that tells customers "158 plants".

---

## 0 · Already good — don't regress
Empty states + first-run copy on every app · deep live-switchable Czech · add-plant picker with the full catalogue and an escape hatch · confirmed destructive actions · migrate→verify→commit import · well-designed Firestore/Storage rules · no secrets in the page · the old "everything I entered vanished" bug is fixed on HEAD.

---

## 1 · Release gates — do these, in this order (Meredith)

| # | Item | Ref | Effort |
|---|---|---|---|
| 1 | **Global error capture + "copy diagnostics"** — `error`/`unhandledrejection` listeners, ring buffer in `pottingbench.local`, stamped with build; export from Settings | B1 | S | ✅ `5fcf65b` |
| 2 | **One version stamp + update toast** — `bump.py` rewrites `BUILD` and SW `CACHE` together; SW `updatefound` → "Reload for new version"; version chip opens About/What's-new (build, sync state, backup + diagnostics links) | B4, U-5 | S | ✅ chip `2b46e31`; stamp + toast `bf99655` |
| 3 | **Fix the plant count** — compute `speciesCount` after the merge block (~14445); add a "Browse all" tile to the Academy teaser | U-3, R2 | S | ✅ `c1b3937` |
| 4 | **Phone tab strip** — six tabs must fit at ≤360px (short labels/icons) or add edge-fade + peek; move day-progress chip out of the overflow. Verify at 320/360/390 | U-1 | M | ✅ `db77f68` |
| 5 | **Storage-full protection** — estimate `JSON.stringify(S).length` before write; non-blocking "nearly full → export / remove photos" nudge; new photos to IndexedDB | B3, N6 | M | ✅ `71624a7` (estimator + CTA; IndexedDB photos deferred) |
| 6 | **Quiet the silent `catch{}`** — ~40 data-path sites (start: `saveLocal` ~7955, `setLang` ~7840) log + badge instead of swallowing; async click handlers get a visible catch | R1 | M | ✅ `f49e510` (named paths log to ring; async handlers covered by the global harness) |
| 7 | **Defer Firebase until sync is used** — `PSYNC.start()` (~25498) must not load the SDK / call Google auth on a fresh, unsynced first launch | U-2 | M | ✅ `138d35d` |
| 8 | **FAB hygiene** — Notes ✎/⚡ only in apps that own them, first-use labels, bottom clearance for lists | U-4, N-5 | S | ✅ `06f81e3` |
| 9 | **Repackage the desktop app from HEAD** — v0.4.6 predates the data-loss fix; add a boot self-check line to diagnostics | R3 | S | ⛔ N/A — no desktop pipeline exists; "Munder Difflin v0.4.6" is the agent harness, not this app (web/PWA only) |
| 10 | **Smoke test** — one script: `node --check` on the extracted script + Playwright boot of every app/view failing on console errors (repo already has `.playwright-cli`, `qa-home.yml`) | R4, R7 | M | ✅ `405a491` `tools/smoke/smoke.sh` — 17/17 PASS on `1322079` |

Rule for all of the above: one item = one commit, pushed; `node --check` clean; verified at a 360px viewport before push.

---

## 2 · Only the owner can do these

| # | Item | Ref |
|---|---|---|
| A | **Decide the beta offering** — Potting Bench only, or TeachBench too? (If plants only, C and D can wait.) | — |
| B | **Pick first customers** (how many, Czech/English, phone models) — and confirm someone has a mid-tier Android to test on | N1 |
| C | **Verify Firebase rules are published** — Firestore + Storage, verbatim from repo, in the console; ideally switch to `firebase deploy --only firestore:rules,storage:rules` | B2, R5 |
| D | **Run one real pilot lesson** — teacher adds cards after a lesson, a student reviews on their own phone; confirm streaks update | B2 |
| E | **Real-phone pass on keyboards** — add-plant bottom fields, planner quick-add: does the on-screen keyboard cover inputs? | N-4 |

---

## 3 · Should-fix if time allows (before or during beta)

- **Czech placeholder gaps** — Settings email / AI-key / model placeholders stay English; add to CS dict; script a dict-vs-UI gap scan · U-6, N8 · S · placeholders added ✅ `98d22f9`; dict-vs-UI gap scan still open
- **TeachBench backup nudge** — one-time "save a backup now" after the first student; "last backup: <date>" in Students header · U-7, N-6 · S · ✅ `33a8a4e`
- **Export discoverability** — obvious Export in each app's settings + "last export" reminder · N2 · S · ✅ `33a8a4e` (About sheet export + last-backup row; Settings export already present)
- **innerHTML/esc scan** — lint-style pass for `${…}` inside `innerHTML` templates not wrapped in `esc(`; note `esc` skips `'` · R6 · M · ✅ `69733da` (scan `docs/beta-esc-scan.md`; esc widened for `'`/`` ` ``; routine-name escape; photo `src` gated by `safeImg`; ids sanitised at migrate/import choke points)
- **Czech `watchLang` observer cost** — scope the MutationObserver to views that need it; benchmark on a mid-tier phone · R8 · M
- **TeachBench roster traffic-light** — cheap, high-visibility for a teacher beta · N3 · S–M
- **Seed a tiny data-layer test harness** — migrate/normalise round-trips, i18n dict integrity · R7 · M

---

## 4 · Explicitly NOT before beta
Splitting the 30k-line file (only if a real device measures slow — 615 KB gz, single request today) · multi-teacher auth · push notifications · filtering the app switcher per purchased module · photo provenance.

---

## Suggested sequencing
- **Tonight / day 1:** gates 1, 2, 3, 8 (all S, independent).
- **Day 2:** gates 4, 5, 6.
- **Day 3:** gates 7, 9, 10 → tag a beta build.
- **Owner, any evening:** A, B, C, D, E.
- **Beta go:** gates 1–10 green + A–D done.
