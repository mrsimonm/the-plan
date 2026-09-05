# TeachBench functional audit — 2026-09-05

- **Auditor:** Dwight (read-only; no code touched). **HEAD audited:** 4990e63 + working tree as served (Meredith editing in parallel — line numbers below may drift).
- **Method:** repo served on 127.0.0.1:8137, fresh in-memory playwright-cli profile, 360×732 portrait (dialog geometry additionally at 320 and 390; desktop pass at 1280×800 noted per flow). Throwaway local student "Audit Tester"; no Firebase writes.
- **Severity:** BLOCKER / SHOULD-FIX / NICE.

---

## 1 · 'Can do' questionnaire (mandatory section)

**Verdict at this HEAD: the core flow WORKS on a fresh profile.** Render, tick, persist, reload, re-open — all correct, no console errors. Tick stored as `{studentId, itemId, doneOn}` via `TB.saveData`, restored after full page reload.

**One real bug found (SHOULD-FIX): C2 students are shown beginner statements.**
- Repro: student with level `C2 Proficient` → detail → Can do shows **A1 and A2** headings/statements.
- Cause (read from code, `tbRenderCanDo`): `const order=["a1","a2","b1","b2","c1"]` has no `"c2"`; `order.indexOf("c2")` is −1, clamped by `Math.max(0,-1)` to 0, so the window shows `a1..a2`. `c1p` is fine (strips `p` → `c1` → shows B2+C1). There are also **no C2 statements at all** in `TB.CANDO` (pool: a1×6, a2×6, b1×6, b2×6, c1×4) — so the fix is either add c2 entries + `"c2"` to `order`, or clamp a C2 student to the B2/C1 window instead of A1/A2.
- Location: `tbRenderCanDo()` — search `/* ---- can-do ----` in index.html (~line 30643 at time of writing); the `order`/`base`/`at` lines.

**Why the owner may have seen it as "broken":** if their student is C2 (or unlevelled → defaults to the A1 window), the list shows content that looks wrong for the student, and on the OLD dialog CSS (see §2) any sheet it sat near opened mis-placed. I could not reproduce any failure to tick/save at this HEAD. If the owner can say which student/level and what exactly failed (no render? tick won't stick? wrong statements?), I'll chase that specific mode.

## 2 · Phone dialogs (mandatory section)

**Verdict at this HEAD: all 13 TeachBench dialogs measure centred, fully on-screen, and internally scrollable at 320, 360, and 390 px.** Measured programmatically (`showModal()` + `getBoundingClientRect`): left/right gaps equal (±2px), no viewport overflow, `.dlg-body` scrolls when content exceeds 88dvh cap, close control present — for `tbEditDlg, tbLessonDlg, tbListEditDlg, tbMatEditDlg, tbMatPickerDlg, tbOccDlg, tbPayDlg, tbPortalDlg, tbPushDlg, tbRunDlg, tbWordEditDlg, tbWordPickerDlg`.

- **The owner's complaint matches the PREVIOUS CSS**, described verbatim in the stylesheet comment (dialogs "opening in weird places": flush left, bottom-anchored, 36px short of full width). The fix (`inset:0; margin:auto; width:calc(100vw - 24px); max-height:88dvh`) landed in **991d18d** — if the owner saw the bug on the deployed site or an older build, that is consistent; at current HEAD I cannot reproduce any off-centre dialog.
- **`tbsPhotoDlg` (student portal photo viewer): opened as an empty shell it is a 75px-high box with no `.dlg-body` and NO close button** (backdrop/Esc only). Needs re-checking through its real opener with a photo loaded — flagged VERIFY below, potential SHOULD-FIX for a visible close affordance.
- Keyboard: `max-height` uses `dvh` so the box follows the visual viewport when the keyboard opens (code-level check; emulated run cannot produce a real on-screen keyboard — needs the owner's real-phone pass, checklist item E).

---

## 3 · Flow-by-flow (teacher)

| Flow | Result | Notes |
|---|---|---|
| Students: add | PASS | 360px; name+level form, row appears, persists across reload. |
| Students: open detail | PASS | Renders inline (not a dialog); account, portal card, can-do sections present. |
| Can-do tick/untick/persist | PASS | See §1. C2 window bug SHOULD-FIX. |
| Edit details (tbEditDlg) | PASS | Name/level/notes; centred; saves + closes. |
| New lesson (tbLessonDlg) | PASS | Date PREFILLED; saves to `lessons`; appears under "Upcoming". |
| Lesson open / edit / Run | PASS | Run opens tbRunDlg → Attended/No-show/Excused; "attended" decremented account 10→9 correctly. |
| Attendance (tbRunDlg) | PASS | Status stored on the lesson; account math (attended/left) correct. |
| Record payment (tbPayDlg) | PASS *(with a snag)* | Saves `{date,lessons,amount,note}`; account shows "lessons left". SNAG below. |
| Vocab quick-add (student detail) | PASS | term+def → `words`+`studentWords`. |
| Word bank add / list add | PASS | Bank word + named list stored in `words`/`vocabLists`. |
| Word edit (tbWordEditDlg) | PASS | Opens via row's "Edit word" button; edit persists. |
| Task add (tbMatForm) | PASS *(with a snag)* | Needs a body/content or it shows "Please add some content." — see snag. |
| Assign tasks (tbMatPickerDlg) | PASS | Checkbox pick → `studentMaterials` with status. |
| Save note (student) | PASS | `student.notes` persisted. |
| Week view | **FAIL** | Mon–Fri only — see BUG below. |
| Tasks / Search tabs | PASS | Search needs ≥2 letters; matches students/words. |
| Backup: Export | PASS | Fires download; no console error. Restore = file-picker (not driven here; code path present). |
| Connect to portal (tbPortalDlg) | BLOCKED-Firebase | Correctly reports "Not signed in to the portal…"; needs a real portal sign-in to exercise. |

### Additional real bugs (teacher)

**BUG (SHOULD-FIX) — Week view is Monday–Friday only; weekend lessons are invisible.**
- Repro: today is Sat 5 Sep; a lesson saved for today does NOT show in Week, and the header reads "Aug 31 – Sep 4" (excludes today).
- Cause: `WEEKDAYS` (~line 6418) is a 5-entry Mon..Fri array; the week view iterates it, so Sat/Sun never render. A teacher who gives weekend lessons (common for a tutor) can't see them in the week view.
- Impact: on any Saturday/Sunday the "This week" view omits the current day entirely.

**SNAG (NICE) — payment date not prefilled.** `tbPayDlg`'s date field is `required` but opens empty, whereas `tbLessonDlg` prefills today. Clicking Save with it empty silently no-ops (native validation bubble only). Prefill today for consistency.

**SNAG (NICE) — "Add task" with an empty body shows "Please add some content." but the warning is easy to miss** (inline, above the fold only if scrolled). Works correctly once a body/URL is given. Not a bug, but a first-time teacher may think the button is dead.

## 4 · Flow-by-flow (student portal)

**BLOCKER (first cold load) — Student Bench can dead-end at "Can't connect. Check your internet and reload." with NO controls, on a machine that is online.**
- Repro: within a session where Firebase had not yet loaded, first navigation to Student Bench (or first teacher "Connect to portal") showed "Can't connect…" and, on the portal side, a console warning `ReferenceError: firebase is not defined`. A full page **reload fixes it** — after reload, Student Bench shows the Teacher sign-in screen (Email/Password/Sign in) correctly and `typeof firebase === "object"`.
- **Root cause (confirmed via the diag ring buffer):** `pottingbench.diag` captured `Uncaught SyntaxError: Unexpected token '<'` stamped `app:teachbench`. That is a script being handed HTML. The service worker's non-shell fetch handler (`sw.js:66`) answers ANY failed fetch with `caches.match("./index.html")` — including the cross-origin Firebase SDK `.js` files. When one of the four `gstatic` SDK scripts loses its first-load race / transient failure, the SW returns **index.html** as the script body → `Unexpected token '<'` → `firebase` never defined → the portal boot shows its offline message. Once the SDK is cached, reloads succeed, which is why it looks intermittent.
- Why the owner likely hit it: a first-time student (or the owner testing Student Bench cold) is exactly the cold-cache path. The message ("check your internet") is also misleading — the network is fine; the SW mis-served a script.
- Fix direction (sw.js is not mine to edit — flagging for Meredith): the offline fallback must not return index.html for non-navigation requests; only navigation/shell requests should fall back to the shell. Guard on `e.request.mode === "navigate"` (or destination) before serving index.html.

Because a working portal sign-in requires real Firebase auth (a staff account) — and the task says to report, not guess — the following were **BLOCKED-Firebase** and NOT exercised end-to-end:
- Student entry via access code
- Review session / the six practice shapes
- Streak display
- Homework upload

The teacher-side pieces that feed them (word push to flashcards, portal link/unlink) are present in code but gated behind the same portal sign-in. Recommend the owner run one real pilot (checklist item D) to cover these, ideally after the sw.js fix so a cold first load doesn't greet the student with "Can't connect".

## 5 · Console / diagnostics

- No console errors during the teacher-side flows above (student add/edit, lessons, attendance, payments, words, tasks, notes, assignment) or the 39-open dialog geometry sweep.
- **`pottingbench.diag` ring buffer (4 entries): the load-bearing evidence** — two `Uncaught SyntaxError: Unexpected token '<'` errors stamped `b:1.0.58, app:teachbench`. This is the SW-serving-HTML-for-a-script signature behind the Student Bench "Can't connect" (see §4). The diag buffer worked exactly as intended (B1) and pinned the root cause.
- Desktop pass (1280×800): TeachBench renders, all 5 tabs present, no horizontal scroll; sampled dialog (tbLessonDlg) centred at 493px. No desktop-specific issues found.

## Severity summary
- **BLOCKER (1):** Student Bench "Can't connect" on cold first load — SW (`sw.js:66`) serves index.html for a failed cross-origin script fetch. Reload recovers, but it's the student's first impression.
- **SHOULD-FIX (2):** can-do C2 students shown A1/A2 statements (+ no C2 statements exist); Week view Mon–Fri only (weekend lessons invisible).
- **NICE (3):** payment date not prefilled; "Add task" empty-body warning easy to miss; tbsPhotoDlg empty-shell has no visible close (VERIFY through real opener).
- **Could not reproduce:** off-centre phone dialogs (fixed in 991d18d); can-do save failure (works at HEAD).
- **BLOCKED-Firebase:** student access-code entry, six practice shapes, streaks, homework upload — need a real portal sign-in (owner pilot / checklist D).

## 6 · Student-portal edge cases (requested set) — mostly NOT RUN, with reasons

god asked for a specific edge-case battery on the student portal. Nearly all of it lives **inside a review session**, which requires opening a valid student link `#s=<accesscode>` whose hashed code matches a real student document in Firestore — i.e. a teacher must first be signed in (real Firebase auth) and have created a portal student with a code. No such account is available to this read-only audit, and the task forbids Firebase writes against real data, so these could not be exercised. Each is listed with exactly what blocks it, so the owner's pilot (checklist D) can cover them deliberately.

| Edge case | Status | Why / what's needed |
|---|---|---|
| Access code: wrong code | NOT RUN (BLOCKED-Firebase) | Code entry hashes (`normaliseCode` → SHA-256) and does a Firestore lookup; with no seeded student every code is "not found", so only the not-found path is observable, and only once Firebase has loaded (blocked by the §4 cold-load SW bug on first try). Needs a seeded student to test the accept path. |
| Access code: blank code | NOT RUN | Same lookup path; needs a live portal to confirm the empty-submit guard. |
| Access code: space-padded ("  ABCD 1234 ") | NOT RUN — but code-level note | `normaliseCode` uppercases and strips everything non-A–Z0–9, so padding/dashes/case *should* normalise to the same hash. That is a code read, not a live test; unverified at runtime. |
| Rapid double-tap on an answer | NOT RUN | Requires being inside a review with a loaded card set → valid code → staff sign-in. |
| Refresh mid-review | NOT RUN | Same precondition (in-review). |
| Browser back mid-review | NOT RUN | Same precondition. The portal uses `#s=` and `history.replaceState` on entry (index.html ~24544), so back-behaviour is worth checking live once a session exists. |
| Offline mid-review then back online (`setOffline`) | NOT RUN | Same precondition. Note the SDK enables `enablePersistence` (~24621), so cached reads *should* survive a drop once loaded — untested. |
| Language switch mid-session | NOT RUN in-portal | Live EN⇄CZ switch verified on the TEACHER side (no errors); not verified inside a student review. |
| 320px width (portal) | PARTIAL | The Student Bench **entry/sign-in** screen was seen at 360; not measured at 320 inside a review. Teacher-side 320 fully covered in §2. |
| Dialogs opened during a review | NOT RUN | The 13 TeachBench dialogs measured in §2 are teacher-side; student-review dialogs (if any beyond `tbsPhotoDlg`) need a live session. `tbsPhotoDlg` empty-shell has no visible close (VERIFY, §2). |

## 7 · Coverage

- **RAN (teacher side, all at 360×732 + desktop 1280 sample):** students add/edit/note; lessons add/edit/Run; attendance + account math; payments; word bank add/edit + lists; vocab quick-add; task add + assign; Tasks/Week/Search tabs; can-do render/tick/persist/reload; backup export; all 13 dialogs' geometry at 320/360/390; Student Bench cold-boot + reload recovery; language switch (teacher side).
- **NOT RUN (all BLOCKED-Firebase — need a real staff sign-in / seeded student, which this read-only audit cannot create):** student access-code accept path; the six practice shapes; streak display; homework upload; and the in-review edge-case battery in §6 (double-tap, refresh/back/offline mid-review, in-review language switch and 320px, in-review dialogs).
- **PARTIAL:** portal 320px (entry screen only); space-padded code (code-read only, not runtime).
- **Recommendation:** run one real pilot session (checklist D) to clear §6, ideally AFTER the `sw.js:66` cold-load fix so a first-time student isn't met with "Can't connect."
