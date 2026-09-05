# Beta readiness — engineering survey (Meredith)

- **Date:** 2026-09-05 (corrected 2026-09-05 after the UX walkthrough — see ERRATA below)
- **Repo:** `/Users/simonmusel/Desktop/theapp` — single-file SPA `index.html` (30,360 lines, 1.98 MB raw / 615 KB gzip) + `sw.js` PWA.
- **HEAD audited:** `43f119f` (Sep 5). **Scope:** read-only engineering survey for a first-customer beta. Built on the module audit; line references are to current HEAD.

## ERRATA (added 2026-09-05 during the UX pass)

- **R2 below was WRONG as written.** The 916 validated records are **already merged and shipped** in HEAD — commit `cb27e1b` ("The library goes from 158 plants to 916"), GENERATED block at `index.html` lines 14620–17384 (`SPECIES` group `.list.push` of 916 records; the "7 objects" seen by a naive scan are the 7 **category groups**, not species). The `tools/batches/*.json` files are the source of truth for re-running `merge_plants.py`; they are NOT waiting to be merged. R2 is superseded by the one real leftover defect: **`const speciesCount` (`~14445`) is evaluated *before* the generated pushes run, so every Academy count/placeholder freezes at the old 158 while ~1,074 species are actually live and searchable.** Fix: derive the count after the pushes (make it a function or move it below the GENERATED block). Item also appears as UX doc U-3.
- **N1's "Firebase SDK is lazy-loaded only when used" is only true of the student portal (TBS).** The main app's PSYNC boot is NOT lazy: `PSYNC.start()` runs unconditionally at the end of boot (`~25498`) and loads the Firebase SDK + makes auth network calls on every launch, even unsigned-in. Caught live (network trace on a fresh profile). See UX doc U-2 for the fix. The main app's PSYNC boot is NOT lazy: `PSYNC.start()` runs unconditionally at the end of boot (`~25498`) and loads the Firebase SDK + makes auth network calls on every launch, even unsigned-in. Caught live (network trace on a fresh profile). See UX doc U-2 for the fix.
- **What a customer runs:** the web build (Netlify/PWA) and/or the packaged Electron app "Munder Difflin v0.4.6". Several fixes below already landed in HEAD but the packaged build is older — see B4.

## Module map at a glance (used throughout)

| App / module | Where it lives | Notes |
|---|---|---|
| Potting Bench (core) | tabs garden / mix / cuttings / plan / library / stats | plant library sub-app: plants, shelf, academy, history + editors |
| Shared state `S` | `pottingbench.v2` + PSYNC (Firestore) | per-user, per-device prefs in `pottingbench.local` (`L`) |
| Planner / Daily + project timeline | `karlovo-planovac-v4` (legacy v1–v3 migrate) | separate storage key, module-local |
| Hours | inside `S.hours` | |
| Teachbench (teacher) | `teachbench.data` (own key, schema 13) | localStorage-only, single browser, no roles |
| Teachbench Student portal | own Firebase app (`teachbench-student`) | anonymous-auth students + staff; rules live in repo |
| Notes + quick note (✎) | inside `S` | AI key in `L` only |
| Settings | whole-app | |
| Bilingual EN/CZ | `t()` + CS dict (~1.9k lines) | |

---

# BLOCKER

## B1 · No way to debug a customer bug remotely (app-wide)
- **Where:** whole app; only 8 `console.error` sites, 0 `console.log`, 23 `console.warn`; no `window.onerror`, no `unhandledrejection` listener anywhere in `index.html`.
- **What:** when a first customer hits an error, nothing is recorded anywhere the team can see. The repo has no `log.jsonl`/telemetry/diagnostics channel of its own (the "log.jsonl with app-start events" is not in this repo — it is a packaging/harness artifact).
- **Why it matters:** beta's whole job is finding and fixing real-world bugs; with no capture, every report is a guessing game, and many failures here are *silent by design* (see R1) so the user may not even see an error.
- **Fix:** add a tiny boot-time global error harness: `window.addEventListener('error'|'unhandledrejection')` → stamp with `BUILD.ver/BUILD.n`, keep a ring buffer (last N) in `pottingbench.local`, offer "copy diagnostics" from Settings, and (optional, later) a remote sink. Log the failure reason, current app/view, and a small state digest — never full `S` (photos/base64).
- **Effort:** S.

## B2 · TeachBench has never been run by a real teacher/student end-to-end
- **Where:** TeachBench teacher module + student portal + Firestore rules (`firestore.rules`).
- **What:** per `TEACHBENCH-TODO.md` §5/§9: no real lesson has been run; the student portal review session has **never been exercised against a real Firebase sign-in** (only 39 pure-function unit checks + browser checks); §4 notes the `progress` rules block may or may not have been published to the console (nobody can see it) — if it is missing, every streak write is silently rejected and streaks read as permanently zero.
- **Why it matters:** if TeachBench is in the beta offering, the load-bearing loop (teacher adds cards fast after a lesson, student reviews) is unproven, and a rules mispublish looks like a code bug.
- **Fix:** (a) someone with console access verifies/publishes the current `firestore.rules` and `storage.rules` verbatim; (b) one pilot teacher+student run a real lesson cycle before beta; (c) add an end-to-end smoke that signs in and reviews one card of each of the six practice shapes.
- **Effort:** M (mostly human/console + QA), code-side L.

## B3 · Data-loss edge at the localStorage quota with photos (app-wide)
- **Where:** `S` (incl. base64 `photos`) persisted to `pottingbench.v2` in localStorage; coalesced write `pFlushWrite` (`~7982`), `touch()`/`push()` (`~7991`).
- **What:** localStorage quota is ~5 MB; a store with a dozen photos was already measured at 1.9 MB. When a write is rejected the app sets a "storage full" sync badge, but nothing nudges the user to back up or offload photos, and export/import caps at 12 MB (`readImport`, `~21467`) while imports are validated then committed — good, but quota pressure is otherwise silent until the moment it breaks.
- **Why it matters:** "everything I entered is gone"-class incidents are the worst possible first-customer experience; photos are the single biggest quota driver and are excluded from PSYNC sync on purpose.
- **Fix:** before writing, estimate `JSON.stringify(S).length` against a safe threshold and surface a non-blocking "storage nearly full — export a backup / remove photos" call to action; consider storing photos in IndexedDB instead of localStorage; keep the already-good migrate-first-render-verify-then-commit import path.
- **Effort:** M.

## B4 · Version/update hygiene — three version numbers, no update prompt
- **Where:** `BUILD={ver:"1.0",n:57}` (`~7777`) shown as "v1.0.57" in the shell footer; `sw.js CACHE="potting-bench-v46"` (`sw.js:6`); packaged app "Munder Difflin v0.4.6"; `bump.py` is meant to bump `BUILD.n` and the SW cache name together but they have drifted (n 57 vs cache v46).
- **What:** a customer cannot tell which build they are on, cannot see that an update exists, and there is no proactive "update available — reload" path (SW is network-first for the shell, which mitigates staleness, but the CACHE/BUILD drift is exactly the class of mistake that previously froze 25 builds under one cache name).
- **Why it matters:** beta feedback is only actionable if the version it came from is known; stale clients multiply support load.
- **Fix:** single source of truth for the stamp; make `bump.py` rewrite `BUILD` *and* `CACHE` in one step; listen for the SW `updatefound`/controllerchange and show a "Reload for the new version" toast; put a readable "About/build" line in Settings alongside a "copy diagnostics" affordance (see B1).
- **Effort:** S.

---

# SHOULD-FIX

## R1 · Silent catch blocks hide real failures (app-wide)
- **Where:** 158 `catch` sites total; ~38 empty `}catch(e){}` plus 2 explicit `.catch(()=>{})` swallows. Two to fix first: `saveLocal()` (`~7955`) — an `L` pref write failing is silently ignored (benign today, but sets the pattern); `setLang()`'s `try{ renderAll(); renderAcademy(); show(curView); }catch(e){}` (`~7840`) — any render error while switching language vanishes. 50 async click handlers (`addEventListener("click",async...`) have no visible catch, so a thrown error there becomes an unhandled rejection nobody sees.
- **Why it matters:** the single most common customer bug class is "tapped something, nothing happened, no error anywhere." Empty catches make those undebuggable and can mask data-path failures.
- **Fix:** never swallow in data paths (log + badge); for UI render paths, log once and show a non-blocking error; add the B1 global handler as the safety net. Tighten the ~40 worst sites (keep genuinely-benign ones, e.g. speech-recognition cleanup at `~28590`, SW registration `.catch(()=>{})`).
- **Effort:** M.

## R2 · Academy count is frozen at the pre-merge 158 (Potting Bench — Library/Academy)
- **Where:** `index.html` — `const speciesCount = SPECIES.reduce(...)` (`~14445`) is evaluated before the GENERATED merge block (`14620–17384`) pushes the other ~916 records, so `speciesCount` stays 158. Rendered in the Academy index teaser ("4 of 158 — type a name or tag…") and the search placeholder ("Search 158 plants"). The full catalogue (~1,074 species across 7 category groups) IS live, searchable and pickable (the add-plant picker exposes ~1,100 names incl. cultivars).
- **What:** customer-facing copy understates the catalogue by ~6× ("Search 158 plants" when ~1,074 are there). Confirmed live on HEAD via the web build.
- **Why it matters:** a first customer judging plant coverage reads the number and stops; the flagship content win (commit `cb27e1b`) is invisible in the very place it should be advertised.
- **Fix:** compute the count from live `SPECIES` after the merge block (function or relocated const). Effort is a one-line change; no data migration.
- **Effort:** S.

## R3 · The `loadShared` data-loss class is fixed in HEAD but must be proven in the *packaged* build
- **Where:** `loadShared()` (`~7926`) now separates "read failed" from "found none" via `readFailed`/`stateLoaded`, refuses to publish over unread state, and `push()` re-checks `stateLoaded` (`~8021`). Pre-migration snapshots auto-save to `pottingbench.backup.<tag>` (`~7482`, recoverable via console `pDownloadBackup()`).
- **What:** this directly closes the old "everything I entered was gone" incident (TEACHBENCH-TODO §16 is now stale). But that fix landed after the v0.4.6 packaging, so a beta customer on the packaged app may still be running the pre-fix code.
- **Fix:** rebuild/repackage from HEAD and add a stored-data "boot self-check" line to the B1 diagnostics so the team can confirm the user's boot path actually read their data.
- **Effort:** S (repackage) + S (self-check).

## R4 · Multi-agent single-file editing has no guardrails (regression risk for the release train)
- **Where:** repo working practices (TEACHBENCH-TODO §10): three sessions edited `index.html` simultaneously and it "shipped a broken main that presented as data loss." No tests, no CI, no linters referenced; `node --check` on the extracted script is the only local validation.
- **Why it matters:** the weeks before beta are when the most people touch the file and the most churn happens — exactly when a silent breakage is most likely.
- **Fix:** minimum bar before beta: (a) a `node --check`-style syntax gate in a one-line script and (b) a Playwright smoke that boots the app, renders each app/view, and checks the console for thrown errors — the repo already has `.playwright-cli` and `qa-home.yml`, so this is mostly assembling what exists. Optional: a region-lock convention doc.
- **Effort:** M (mostly assembling existing tooling).

## R5 · Firestore/Storage rules are excellent but must be verified as *published*
- **Where:** `firestore.rules` (roles owner/teacher/student, per-field update restrictions, private per-user potting-bench state, hashed access codes) and `storage.rules` (10 MB image-only homework uploads). Rules comments say "paste the whole file into the console" — deployment is manual and unverifiable from the repo.
- **Why it matters:** a missing publish means silent feature failure (streaks, homework) rather than a clean denial, which reads as a bug to customers and burns beta time.
- **Fix:** make rules deployment a recorded, one-command-ish step (firebase CLI `deploy --only firestore:rules,storage:rules`) and verify current console state once before beta.
- **Effort:** S.

## R6 · innerHTML-heavy rendering with a consistent `esc()` — needs a targeted audit, not a rewrite
- **Where:** 186 `innerHTML` assignments; 499 `esc(` calls; user data is widely interpolated into template literals. `esc` (`~7779`) escapes `& < > "` but not `'`.
- **What:** no obviously exploitable sink found in this pass, and the app escapes far more than it forgets, but with this many string-built DOM sites the risk is concentration (one missed field) rather than architecture. Example pattern needing review: rendered rows that interpolate user text into `title=`/`placeholder=`/inline `style=` attributes, and any path where imported/backup data flows into `innerHTML` without `esc`.
- **Why it matters:** customers will paste names/species/notes; a single unescaped path is a stored-XSS vector in a PWA that holds real personal data.
- **Fix:** add a lint-style scan for `${...}` inside `innerHTML` template literals where the payload isn't wrapped in `esc(` or a known-safe token; fix stragglers. Low priority to migrate to DOM APIs.
- **Effort:** M.

## R7 · No automated test suite at all (app-wide)
- **Where:** repo has no test files/runner (TeachBench's 39 unit checks live in the separate Teachbench project, not here).
- **Why it matters:** the three biggest beta moves — merging 916 species (R2), repackaging (R3), and continuing concurrent feature work — are exactly the changes that a suite would de-risk. First-customer bugs in migrations/storage have historically been the most expensive.
- **Fix:** seed a small harness around the pure parts (migrate/normalise round-trips from fixtures, i18n dict integrity, species-merge validation is already `--check`). Doesn't need coverage of UI; the data layer is where the damage was.
- **Effort:** M.

## R8 · Planner focus-mode/quick-task distinction and Czech re-walk cost (module: Planner)
- **Where:** `watchLang()` MutationObserver (`~7823`) re-walks *every added DOM subtree* when language is Czech — during large renders (planner board, plant lists) this is a real per-render tax on the device that needs it most. The Quick-Task demotion bug (`~7641`) is fixed (runs per-load, not version-gated).
- **Why it matters:** performance work in OVERNIGHT_NOTES already found the mobile experience was dominated by per-action full-store rewrites (now coalesced); the i18n observer is the remaining obvious per-render cost, and Czech-speaking customers are first on the list.
- **Fix:** scope the observer to views actually needing translation or cache per-subtree translated nodes; benchmark before/after on a mid-tier phone (Overnight §2 lists the method).
- **Effort:** M.

---

# NICE-TO-HAVE

## N1 · Performance/startup of the 30k-line single file (measured)
- **Measured:** `index.html` = 1.98 MB; **CSS 244 KB (60 KB gz)**, **inline JS 1.61 MB (528 KB gz)**; 788 function definitions; ~30k lines. Single classic `<script>` tag (deliberate architecture), so one request + SW shell; nothing else blocks first load (Firebase SDK is lazy-loaded only when PSYNC/portal is used — comment `~29612`; Tesseract OCR and remote clipper fetch are on-demand).
- **What:** worst cost is main-thread JS parse+eval of ~1.6 MB before first paint on a mid-tier phone (order 0.3–1 s, sometimes more); gzip transfer is a single 615 KB round-trip. Largest code islands by source size: Teachbench student app (~2.0k lines), Notes (~2.2k lines across parts), Planner+timeline (~1.3k), Czech dict (~1.9k).
- **Suggested (only if a customer device is measurably slow):** extract the biggest *lazy* islands that most users never open (Teachbench student app block; possibly the full CS dictionary) into files the SW caches and the app `import()`s on demand. Do **not** split the shared Potting Bench core — it is one cohesive render loop and splitting buys little.
- **Effort:** L (do only if measurement demands it). Measure FCP/parse on a Moto G-class device first.

## N2 · Backup hygiene & discoverability (app-wide)
- Where: full-state export/import (`~21423`+) is strong (tagged, versioned, migrate→render-verify→commit, 12 MB cap, multi-host download incl. `window.claude` hook + text fallback); TeachBench has its own Backup/restore; auto pre-migration snapshots exist but are console-only.
- Improve: surface a "last export date" + periodic reminder in Settings, and one obvious "Export" affordance in each app's settings so a non-technical customer can do it without help.
- **Effort:** S.

## N3 · TeachBench roster traffic-light (module: TeachBench)
- Per TEACHBENCH-TODO §14, `TB.lessonAccount` already computes what the teacher-side roster needs; adding the colour-coded dashboard is cheap and high-visibility for a teacher beta.
- **Effort:** S–M.

## N4 · Teacher-side role model (module: TeachBench)
- Teachbench teacher data remains "whoever holds the browser" (no auth/roles), while the student portal has a real role model. Acceptable for single-teacher beta; document it and only build multi-teacher auth if beta demands it.
- **Effort:** L (do not pre-build).

## N5 · Push notifications / review-window reminders (module: TeachBench student portal)
- Deferred by design (FCM/VAPID + SW). The spec considered these core to spaced repetition. Not beta-blocking if the pilot habit is formed in-lesson; revisit post-beta.
- **Effort:** L.

## N6 · Photos: offload + provenance
- Photos are base64 in `S` and excluded from PSYNC by design. Nice: move new photos to IndexedDB (or Storage via the existing authenticated bucket) so quota stops being the ceiling (see B3), and add per-photo timestamp/plant already partially present in log.
- **Effort:** L.

## N7 · Security posture — no action required, noted for confidence
- Firebase API key ships in plain (`~23593`) — acknowledged in-code as not-a-secret (Firebase web config); the real gate is `firestore.rules`/`storage.rules`, which are well-designed (field-level update restrictions on flashcards, student can only touch their own SRS fields, homework photos 10 MB image-only, potting-bench user state strictly private per uid). Anthropic AI key is deliberately kept in per-device `L` (`~27821`, plaintext in localStorage but never uploaded to Firestore) with plain fallbacks for every AI feature. No secrets found in the page beyond the Firebase web config. Only note: warn users the AI key is device-local and re-enterable.
- **Effort:** none (R5 covers the publish side).

## N8 · i18n completeness check (module: all)
- `t()` falls back to English when the CS entry is missing (by design, `~7789`), so a hole is a half-translated screen rather than a crash. Cheap pre-beta win: script the CS dict (`CS={}` near the bottom, `~21890`) against visible English UI strings to find gaps before Czech customers do.
- **Effort:** S.

---

# The one-line top five (for the summary message)
1. B1 — no global error capture/telemetry → a first-customer bug cannot be debugged remotely; add error/unhandledrejection capture + diagnostics export.
2. B2 — TeachBench has never run a real teacher+student cycle and the student portal was never exercised against live Firebase; verify rules are published and run one pilot lesson.
3. B4 — three drifting version stamps (BUILD 1.0.57, SW cache v46, packaged v0.4.6) and no update prompt → stale, untraceable clients.
4. B3 — localStorage quota + base64 photos is the realistic "my data vanished" risk; add a near-full backup/offload nudge, consider IndexedDB for photos.
5. R2 (corrected) — the species catalogue IS merged and live (~1,074) but every Academy count is frozen at the pre-merge 158 (`speciesCount` evaluated before the GENERATED block); one-line fix so the flagship content is visible to first customers.
