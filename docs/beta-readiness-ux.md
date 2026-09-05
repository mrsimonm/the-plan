# Beta readiness — first-customer UX walkthrough (Meredith)

- **Date:** 2026-09-05 · **Method:** drove the actual web build (HEAD `43f119f`) in a real browser at a phone viewport (360×732) via the repo's Playwright tooling — fresh profile, so true first-launch state, then each app. Code read only where the UI couldn't reach.
- **Lens:** a new, slightly impatient paying customer on a phone, week one.
- **Not repeating:** engineering findings in `docs/beta-readiness-meredith.md` are cross-referenced by their ids (B/R/N) instead. **Read that doc's ERRATA first** — the "916 unmerged species" claim there was wrong; the catalogue is merged and live.

## What is already genuinely good (don't regress it)
- Empty states everywhere are excellent and on-voice (Garden, Bench, Grow, Diary, Library, Hours, Planner, Notes, TeachBench all greet a fresh install with a plain-language explanation + the right next action).
- First-run onboarding copy on the empty Garden is a model ("Tap + Plant and pick what it is — the app fills in how often it wants watering… whether it's safe around animals").
- Czech coverage is deep and switchable live; even FAB tooltips translate ("Nová poznámka").
- Add-plant picker holds the full ~1,100-name catalogue (incl. cultivars) with a search box and an explicit "+ Add a plant that is not in the list" escape hatch.
- TeachBench is honest up front that its data lives only in that browser and nudges export ("Občas si vyexportuj kopii někam do bezpečí").
- Destructive actions are confirmed and import is migrate-then-render-verify-then-commit (eng-side: already noted).

---

# BLOCKER

## U-1 · On a phone the top tab strip runs off-screen — Library and Stats (and the day-progress chip) are effectively invisible
- **Where:** Potting Bench tab strip (`.nav`, ~`4243`). Measured at 360px wide: tabs span Garden 18→96, Bench →172, Grow →241, Diary →310, **Library →390, Stats →459**; `.nav` is `overflow-x:auto`, so the last two tabs (and the today-progress `#taskPct`, sitting at x≈462) need an undiscoverable swipe to appear. No fade/chevron/partial-peek hint that there is more.
- **What the customer sees:** the app they're asked to judge has 4 tabs; the plant Library hub (All plants, Shelf, Academy, History) and Stats are out of reach for anyone who doesn't guess to drag the tab bar. The "% done today" indicator in the tab row lives past the edge too.
- **Why it hurts:** Library is where a plant customer goes for reference content and their collection; week-one churn lives exactly here. On the owner's own phone right now this is the first thing they'll trip on.
- **Fix:** make all six fit at ≤360px (shorten to icon-or-short labels — Garden/Bench/Grow/Diary/Library/Stats can be ~5-char labels), or keep the swipe strip but add an edge-fade + a visible sliver of the next tab so "there's more" reads instantly. Move the day-progress out of the overflow (Garden already shows a Today card).
- **Effort:** M (CSS + a couple of labels; verify at 320/360/390).

---

# SHOULD-FIX

## U-2 · First launch silently phones home to Firebase before the customer has done anything
- **Where:** boot always ends with `PSYNC.start()` (`~25498`), which loads the Firebase SDK (3-4 scripts from gstatic, ~200+ KB) and makes auth network calls (Google identitytoolkit + auth iframe) — confirmed on a fresh profile load with no sync sign-in, no student mode, no user action.
- **What the customer sees:** nothing, but their first open is slower and depends on the network; offline it's a console 404/failed-request every launch (app still boots). For a privacy-conscious first customer it's an unrequested call to Google before they've agreed to sync.
- **Why it hurts:** the app's own selling point is "works in a room full of plants with no signal"; the first-run moment — where speed and trust decide retention — is when it's least justified.
- **Fix:** defer Firebase init until sync is actually engaged (user taps "Sign in"/"Sync") or a signed-in account exists; keep a `navigator.onLine`/lazy gate. Photos/publish logic already treats offline as "local as ever", so the behaviour change is safe.
- **Effort:** M.

## U-3 · Academy advertises "Search 158 plants" while ~1,074 are actually there
- **Where:** Library → Academy index. The search placeholder and teaser count read "158 plants" / "4 of 158" because `speciesCount` (`~14445`) is computed *before* the merge block pushes the rest of the catalogue. Live, typing a letter returns ~1,000+ tiles (verified: query "a" → 1,056 tiles).
- **What the customer sees:** an app that promises a reference library but appears to hold 158 plants — and shows only 4 tiles until they guess to type. The flagship content win is invisible.
- **Why it hurts:** a plant customer scans that count and judges coverage instantly; 158 looks thin next to competitors, ~1,074 looks like a reason to buy.
- **Fix:** derive the count after the merge (function/repositioned const) — one line (eng R2, corrected). Consider a "Browse all" tile in the teaser so non-typers see the catalogue size.
- **Effort:** S.

## U-4 · Floating "New note ✎ / Scratchpad ⚡" buttons float over every app, with no context for a new customer
- **Where:** bottom-right FABs (`#nQuick`, scratchpad) are visible on Potting Bench Garden/Bench/Grow, Planner, Hours, Settings — every screen, not just Notes (verified on Garden and Planner), and ✎ is redundant next to Notes' own "+ New note".
- **What the customer sees:** two unexplained round buttons over their plants that belong to an app they haven't opened; scratchpad's ⚡ meaning is opaque. They sit at the bottom of the reading area (y≈610-716 on a 732px viewport) and can cover the last row of long lists once a customer has data.
- **Why it hurts:** week-one noise and possible occlusion of the exact content the plant app exists for.
- **Fix:** show quick-capture FABs only in apps that own them (Notes + wherever quick capture was a deliberate cross-app feature), give them discoverable labels on first use, and add bottom clearance so list content never hides behind them.
- **Effort:** S.

## U-5 · The version chip does nothing visible and there's no "what's new / about"
- **Where:** the "v1.0.57" footer chip (~bottom of the shell). Tapping it in the walkthrough produced no visible result; it reads as a button but isn't one a customer can use.
- **Why it hurts:** customers can't tell if they're current, and there's no obvious place to hear about changes — feeding eng B4 (stale, untraceable clients).
- **Fix:** make the chip open an About/What's-new sheet (build, last update, sync state, export/backup links, diagnostics copy) or at least style it as non-interactive text; pair with the B4 update-reload toast.
- **Effort:** S.

## U-6 · Mixed-language placeholders in the Czech UI
- **Where:** Settings — email placeholder "you@example.com", AI-key "sk-ant-…" and model field stay English while everything around them is Czech (verified live with `html lang=cs`).
- **What the customer sees:** a jarring English hint inside an otherwise complete Czech screen.
- **Why it hurts:** half-translated is the classic "this app doesn't care about my language" signal; it's the exact class the task asked to hunt.
- **Fix:** add the few placeholder strings to the CS dict (keep the "sk-ant-…" prefix as data, localise the frame).
- **Effort:** S.

## U-7 · TeachBench teacher: data-safety honesty is there, but the safe action isn't prompted at the moment of risk
- **Where:** TeachBench → Students (empty). The app already warns the data lives in "this browser only" and there is a Backup export (good). But a brand-new teacher adding their first real student gets no "export a copy" cue until later, and the roster view doesn't show a last-backup date.
- **Why it hurts:** a teacher who loses the browser loses attendance, payments and vocabulary state — the worst possible first-month story for the TeachBench beta.
- **Fix:** after the first student is added, show a one-time, dismissible "save a backup now" nudge with the existing export; surface "last backup: <date>" in the Students header afterwards.
- **Effort:** S.

---

# NICE-TO-HAVE

- **N-1 · Optional first-run coach marks** (3 quick, dismissible pointers: the six tabs incl. the swipeable Library/Stats after U-1; the + Plant button; the app switcher ▾). The copy-led empty states carry most of the load already; this only adds speed for impatient users.
- **N-2 · App switcher shows every suite app to every customer.** A plant-only first customer sees "Student Bench" and "Teachbench" in the ▾ menu. Harmless today; if the app is sold per-module later, filter by what the account owns.
- **N-3 · Academy teaser "Browse all" affordance** (ties into U-3) — one tap to unroll the grouped list instead of requiring the search box.
- **N-4 · Verify dialogs/inputs clear the on-screen keyboard** on the smallest targets (add-plant flow bottom fields, planner quick-add) — couldn't be exercised headlessly; worth one pass on a real phone.
- **N-5 · Garden list bottom-clearance under the FABs** once a customer has enough plants to scroll (fold into U-4 check).
- **N-6 · Keep the honest single-browser note in TeachBench but pair every mention with the exact one-tap Export** (fold into U-7).

---

# Top five for the owner (cross-refs)
1. **U-1** — the top tabs overflow a 360px phone: Library + Stats (and the day-progress) are off-screen without an undiscoverable swipe. Make six tabs fit or add an edge-fade peek. (BLOCKER)
2. **U-3 / eng R2 (corrected)** — Academy says "158 plants" but ~1,074 are live: one-line `speciesCount` fix + a browse-all tile so the catalogue sells itself.
3. **U-2** — first launch loads the Firebase SDK and phones Google auth before any consent or sync need; defer until the user actually syncs.
4. **U-5 / eng B4** — the version chip does nothing and there's no What's-new/About; give customers a way to know they're current.
5. **U-4 / U-7** — two small trust-and-noise items: unlabelled Notes FABs floating over every app, and no backup nudge at the exact moment a teacher creates their first real data.
