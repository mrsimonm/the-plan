# Teachbench — everything still to do

Covers both halves of the teaching side of the app:

- **Teachbench (teacher-side)** — the `TB` module. Students, materials,
  a vocabulary library, weekly lessons and search. Stored in
  `localStorage` under `teachbench.data`. Reached from the app menu as
  "Teachbench".
- **Student portal** — the `SRS` / `TBS` / `TBS_UI` / `STREAK` / `RECAP`
  modules. Flashcards, spaced repetition, homework, calendar, streaks.
  Stored in **Firestore** (project `teachbench-student`). Reached either
  from the app menu as "Student Bench" (teacher's own way in) or by a
  student opening `index.html#s=<code>`.

Everything in the student portal's original v1 plan is implemented and
live. This file lists only what is NOT done.

Firebase: project `teachbench-student`, Blaze plan, Firestore in
europe-central2. Owner `musel.simon@gmail.com`, teacher
`linlab.cz@gmail.com`. Rules live in `firestore.rules` / `storage.rules`.

---

## 0. The big one: the two halves do not know about each other

**This is the most valuable outstanding item, and it is not a polish
job — it is the thing most likely to decide whether Margo actually uses
any of this.**

Verified in the code: there are two entirely separate student lists with
no bridge between them. The teacher-side `TB` module keeps students,
words and lessons in `localStorage`; the student portal keeps its own
students and flashcards in Firestore. Nothing in `TB` ever calls `TBS`.

Consequences today:

- She must **add every student twice** — once in Teachbench for lesson
  planning, once in Student Bench for flashcards.
- Her **vocabulary library cannot become flashcards.** Words she has
  already typed into Teachbench have to be retyped, one at a time, in
  the student panel. The whole system rests on her adding cards after
  every lesson; making her type everything twice is exactly the friction
  that will stop that happening.
- **Lessons cannot appear on the student's calendar** (see item 12),
  because lesson times only exist on her device.
- Teachbench is **single-device**: `localStorage` means her laptop and
  her phone hold different data, and neither is backed up.

There are three honest ways forward. This needs Simon's decision before
anyone writes code:

- **(a) Bridge them.** Keep both stores, add "push to flashcards"
  actions: send a word from the library to a student's deck, and match a
  Teachbench student to a portal student once. Smallest change, but
  leaves two lists to keep in step.
- **(b) Move Teachbench onto Firestore too.** One student list, one
  source of truth, works across her devices, and lesson times become
  available to the student calendar for free. Much the largest job: it
  means migrating `teachbench.data` and rewriting `TB`'s synchronous
  storage layer as async.
- **(c) Leave them separate on purpose** and accept the double entry as
  the price of not touching working code.

## 1. Loose ends in the student portal (~15 minutes total)

1. **Dead "Level" line in the teacher's planning notes.**
   `RECAP.forTeacher` prints `Level: ${student.level || "not set"}`, but
   nothing in this module ever sets a level and there is no UI for it, so
   every export reads "not set". Either add a level selector beside the
   student name field, or delete the line. (Note: the teacher-side `TB`
   module *does* have levels — another symptom of item 0.)

2. **The student's Words tab lies when the connection drops.**
   `renderCardList` shows "Nothing here yet" whether there are no cards
   or the load failed. `state.cardsError` is already populated by the
   `onCards` listener and already handled correctly on the Today screen
   (`renderStudentToday`); the same treatment just needs applying here.
   This matters — a misleading empty state on the Potting Bench load
   path is what turned a trivial missing-function bug into an apparent
   data-loss incident during this build.

3. **The calendar has the same gap.** `renderCalendar`'s footnote cannot
   distinguish "no words yet" from "could not load them".

## 2. Blocked on Simon — not code

4. **Publish the `progress` rules block.** Streaks are fully implemented
   but every write is silently rejected until this is added in the
   Firebase console under Firestore → Rules, just above the existing
   `match /homework/{itemId}` line:

   ```
   match /progress/{docId} {
     allow read: if canManage(studentId) || isThisStudent(studentId);
     allow create, update: if isThisStudent(studentId);
     allow delete: if canManage(studentId);
   }
   ```

5. **Nobody has used it for a real lesson.** Everything is verified by
   automated checks and by hand in a browser, but no actual teacher and
   no actual student have been through it end to end. The load-bearing
   assumption is that adding cards after a lesson is fast enough that
   Margo does it every time. If that is false, nothing else matters —
   and item 0 is the main threat to it.

## 3. Teacher-side Teachbench — known gaps

6. **Single-device, no backup.** `teachbench.data` lives in one browser's
   `localStorage`. Losing that browser profile loses her students,
   materials, vocabulary and lesson history. There is no export either.
   Even without doing item 0(b), an export/import would be cheap
   insurance.

7. **No way to hire a teacher into Teachbench.** The student portal has a
   real role model (owner / teacher / student, enforced by Firestore
   rules, `staff` collection). Teachbench has none — it is whoever holds
   the browser. If a second teacher is ever hired, only the portal half
   understands that.

## 4. Deferred by design — agreed, never started

8. **Push notifications.** The spec called these core rather than a
   courtesy: hitting the review windows on time is the mechanism that
   makes spaced repetition work. Needs Firebase Cloud Messaging (VAPID
   keys, ~5 minutes in the console) plus a service worker.
9. **Wispr Flow integration** — pull her recorded lesson summaries in
   automatically, so the vocabulary covered in a lesson does not have to
   be re-entered by hand. Note this overlaps heavily with item 0: both
   are about not typing the same thing twice.
10. **Photo annotation** — draw on a submitted homework photo before
    sending it back.
11. **Teacher voice notes** on cards, instead of or alongside TTS.
12. **Lesson times on the student calendar.** It shows review due-dates
    only. Blocked on item 0 — lesson times live in `teachbench.data`,
    not Firestore.
13. **Speech recognition** for pronunciation cards. Playback only today.
14. **Colour-coded dashboard polish.** A basic traffic light exists on
    the roster; the richer version described in the spec does not.
15. **DeepSeek integration** — no defined use case in the spec.

## 5. Known weakness elsewhere in the app — Simon's call

16. **The bare `catch(e){}` around the load path in `loadShared()`.**
    `try{ ... return migrate(d); }catch(e){}` swallows any throw and
    falls through to `seed()`, so failing to READ stored data is
    indistinguishable from having none: the app silently presents itself
    as empty while the real data sits intact in `localStorage`, and the
    next write destroys it. Reproduced during this build with a
    realistic store. Two commits (`fdd8041`, `5ed90db`) hardened
    symptoms; the shape remains. The photos fetch immediately above it
    already distinguishes these two cases properly and is the model to
    follow. Not part of either Teachbench module, so left alone.

## 6. Open question never answered

17. **Handing the app to another model (e.g. DeepSeek) safely** — how to
    give it a working copy, let it commit and push, and keep a reliable
    way to roll back if its work goes wrong. Simon asked; it was never
    answered.

---

## Notes for whoever picks this up

- **Several Claude sessions edit `index.html` concurrently.** Never run a
  bare `git add index.html`; stage your own hunks with `git add -p` and
  check the staged diff for other people's markers before committing.
  Three separate near-misses happened during this build, one of which
  shipped a broken `main`.
- The student app is reachable two ways: a real student link
  (`index.html#s=<code>`, which hides all teacher chrome and is sticky
  across reloads via `teachbenchStudent.local`), and the "Student Bench"
  app-menu entry, which is how the teacher reaches her own side.
- `SRS` and `STREAK` are pure functions over plain data with no DOM and
  no network, so they can be exercised straight from the browser
  console — that is how the spaced-repetition intervals and the streak
  rules were verified.
- Teacher-side render entry points are `renderTeachbench()` and the
  `tbRender*` family; the student portal's is `TBS_UI.start()`.

## Suggested order

1. Item 4 (publish the rules — two minutes, unblocks streaks)
2. Item 5 (try it with Margo — tells you whether item 0 is urgent)
3. Item 0 (decide a/b/c, then build it)
4. Items 1–3 (quick correctness fixes)
5. Item 8 (push notifications — the spec's own priority)
