# Teachbench — complete handover

**Read this file and nothing else.** It is written to be picked up cold,
by a session or a model with none of the conversation that produced it.
It covers what exists, how to run it, what is left, and the decisions
still outstanding.

Last updated at the end of the build session that created the student
portal.

**The original brief is preserved alongside this file** at
`docs/teachbench-student-spec.md` — Margo's own requirements, gathered in
a voice interview before any code existed. Where this handover says "the
spec", that is the document it means. Read it if you are deciding what to
build next; it carries her priorities and her reasoning, which this file
only summarises.

---

# 1. What this is

Two related halves of a teaching tool, both living inside the single
~20,000-line `index.html`, reached from the app menu at the top of the
page.

**Teachbench (teacher-side)** — the older half. Margo's own workspace:
students, teaching materials, a vocabulary library, weekly lessons and
search. Code lives in the `TB` IIFE; render entry points are
`renderTeachbench()` and the `tbRender*` family. Data is a single
`localStorage` key, `teachbench.data`, schema version 12. Sub-tabs:
Students / Week / Tasks / Words / Search.

**Student portal (newer half)** — built in the session this file
records. Flashcards with spaced repetition, homework both ways, a
calendar, streaks and month-end summaries. Data is in **Firestore**, so
it genuinely syncs between Margo's device and each student's phone.

The portal is reached two ways:
- **Students**: `index.html#s=<accessCode>`. This hides every trace of
  the rest of the app — no menu, no Potting Bench, no teacher tools —
  and is sticky across reloads via a `teachbenchStudent.local` flag.
  There is a "Not you?" control to release a device.
- **Teacher**: the "Student Bench" entry in the app menu, which shows a
  sign-in screen and then her roster.

Who it is for: Margo teaches private English lessons to a handful of
students, mostly children and teenagers on phones. Simon owns the app.

---

# 2. How to run and test it

```bash
cd /Users/simonmusel/Desktop/theapp
python3 -m http.server 8955
```

Then open `http://localhost:8955/index.html`.

It is also deployed — pushing to `main` publishes it.

**To test the teacher side:** app menu → Student Bench → sign in as
`musel.simon@gmail.com` (owner, sees all students) or
`linlab.cz@gmail.com` (teacher, sees only her own). Add a student, add
cards, send homework, press Copy to get their access link.

**To test the student side:** paste that link into a **private/incognito
window** so it is genuinely a separate device. Never test a student link
in the same browser where you are signed in as a teacher without
expecting the app to sign you out — see §7.

**To test the pure logic without any of the UI**, from the browser
console. `SRS` and `STREAK` are deliberately pure functions over plain
data — no DOM, no network — precisely so this works:

```js
SRS.scheduleNext(SRS.fresh(), 'good', new Date())   // → 1 day, ease 2.5
STREAK.record(STREAK.empty(), {wasDue:true, daysLate:0, anySlipped:false}, new Date())
```

---

# 3. Firebase

Project **`teachbench-student`** · Blaze plan (a refundable 600 CZK
prepayment sits on the account; real usage should stay at zero) ·
Firestore in **europe-central2** · Storage bucket
`teachbench-student.firebasestorage.app` in US-EAST1 (the no-cost
location).

Sign-in methods enabled: **Anonymous** (students) and **Email/Password**
(staff).

| Role | Account | Firebase Auth UID |
|---|---|---|
| owner | musel.simon@gmail.com | `iXTZ90oFgFd5a0accU3YIwopydR2` |
| teacher | linlab.cz@gmail.com | `EhA9l7gHrpga7vQnsOE8zsAK0OA2` |

Roles are documents in a `staff` collection keyed by UID, each with a
`role` of `owner` or `teacher`. Hiring a teacher = create an Auth user
and one `staff` doc; no code change.

Security rules live in `firestore.rules` and `storage.rules` in this
repo — the deployed copies are in the console, and these are the
reviewable source of truth. Keep them in step by hand.

**Firestore shape:**

```
staff/{uid}                                    role, email, name
accessCodes/{sha256HexOfCode}                  studentId
studentAuth/{anonymousUid}                     studentId, codeHash, createdAt
teachbenchStudents/{studentId}                 name, teacherId, codeHash, createdAt
  /flashcards/{cardId}                         type, front, back, explanation,
                                               intervalStage, easeFactor, intervalDays,
                                               nextReviewDate, lastReviewedAt,
                                               reviewCount, lapses
  /homework/{itemId}                           direction, kind, text, photoPath,
                                               status, createdAt
  /progress/streak                             currentStreak, bestStreak, points,
                                               lastStudyDate, onTime, late, extra, days
```

Storage: `teachbenchHomework/{studentId}/{itemId}/{filename}`.

**How the access-code login works** (no Cloud Functions, so it stays on
the free tier): the plain code is never stored, only its SHA-256 hash as
a document id in `accessCodes`. A student's device signs in anonymously,
fetches that one document by exact hash — it cannot list the collection,
so codes cannot be enumerated — then writes `studentAuth/{its own uid}`.
The rules only permit that write if the code hash really does map to
that student. Redemption is idempotent, so a cleared browser can redeem
the same code again.

**Verified by hand** that an anonymous device cannot: list students,
list staff, enumerate access codes, create a student, or forge a
device-to-student mapping. All five denied.

---

# 4. Where the code is

All inside `index.html`. Search for these symbols rather than trusting
line numbers — several sessions edit this file and the numbers move.

| Symbol | What it is |
|---|---|
| `const SRS` | SM-2 spaced repetition. Pure, no DOM, no network. |
| `const STREAK` | Streak and points rules. Pure. |
| `const RECAP` | Month-end summaries. Pure, derives everything from cards. |
| `const TBS` | Firestore/Auth/Storage data layer. Async, listener-based. |
| `const TBS_UI` | Every line of DOM work for the portal. |
| `<section id="view-teachbench-student">` | All portal markup. |
| `.tbs-*` | All portal CSS, one block. |
| `bootStudentApp` / `studentModeRequested` / `markStudentDevice` | The student-mode boot gate, next to `boot()`. |
| `FIREBASE_CONFIG` | The project config. Not a secret. |
| `const TB` | The older teacher-side module (localStorage). |

The Firebase SDK is injected **only when the portal starts**, so Potting
Bench sessions stay as network-free as they always were.

`TBS` deliberately does not look like `TB`. `TB` is synchronous
localStorage (`load` → mutate → `save`); `TBS` is async with live
`onSnapshot` listeners, because data has to arrive without a refresh.
Do not try to force them into one shape.

---

# 5. What is built and working

Teacher: sign-in with owner/teacher roles · student roster with a
traffic light and progress counts · add students · issue and revoke
access links · add vocabulary, grammar and pronunciation cards · send
homework with photos · per-student dashboard · month-end planning notes
for pasting into an LLM.

Student: access-code entry · a Today screen with what is due · review
sessions with Again/Hard/Good/Easy · self-marking grammar cards ·
text-to-speech on pronunciation cards · a word list · a month calendar
of upcoming reviews · homework both ways with photos · streak and
points · a month-end recap.

**Verified, not assumed:**
- SM-2 gives textbook intervals — 1, 6, 15, 38 days on repeated correct
  answers; a lapse resets the ladder, drops ease 2.5 → 2.18 and
  re-shows the card in 10 minutes rather than tomorrow.
- The streak rules behave as the spec demanded (see §6).
- Calendar day maths across month lengths, leap-year February (29
  days), Monday-first alignment, and month navigation round-trips.
- The security rules block all five attacks listed in §3.

---

# 6. Design decisions worth not re-litigating

**Student mode is sticky and hides everything else.** A student device
must never see Margo's own tools. The `#s=` fragment is consumed on
first use, so a `localStorage` flag carries the mode afterwards. Written
only on the genuine student path — if Margo opens a student link from
her own app, her device does not become a student's.

**Streaks reward the schedule, not attendance.** The spec was explicit
that a generic daily streak was wrong: it would punish a student on a
day the algorithm gave them nothing to do, and reward opening the app to
do nothing. So: a day with **nothing due does not break** a streak;
letting a card sit **more than a day past its slot does**; and
voluntary early practice earns a few points but **cannot inflate** the
streak. Verified: three on-time days → 3; a quiet day carries it to 4;
one card left four days late resets to 1 while the best run is
remembered; a fortnight away honestly reports 0 rather than a stale
number; per-day history self-prunes at 62 days.

**Photos are downscaled on the device before upload** (a 4 MB phone
photo becomes a few hundred KB) because Margo is often on mobile data.
The upload happens **before** the message document is written, because
the rules deliberately forbid a student editing a message after sending
it — so the storage path must exist first.

**"Learned" means an interval of 21 days or more**, the usual SM-2 line
between still-learning and long-term memory. `statsFor()` is shared by
the roster and the detail panel so the traffic light and the numbers
cannot disagree.

**Access codes are shown once.** Firestore keeps only the hash; the
plain code is cached in the issuing browser. Pressing Copy on a device
that does not have it issues a **new** code and revokes the old link —
deliberate, so a lost phone can be cut off.

---

# 7. Seven bugs found and fixed after the first build

Recorded because they show the shapes this code is prone to.

1. **Student mode was never persisted** (critical). The boot gate read a
   flag nothing ever wrote, while the `#s=` fragment was stripped after
   first use — so the first pull-to-refresh dropped a student into the
   teacher's whole app.
2. **A signed-in teacher opening a student link bound her own account to
   that student, permanently** — the rules forbid rewriting a
   `studentAuth` mapping once made. Now it steps down to a fresh
   anonymous identity first. This fires the moment anyone tests a link
   they just copied.
3. **A student's half-written homework answer was destroyed** whenever a
   message arrived, because the thread re-rendered the composer with
   itself. The composer is static markup now, and text survives a failed
   send.
4. **A double-tap on a grade button** graded one card twice and skipped
   the next. The guard now closes first, and the write no longer blocks
   the next card.
5. **A re-issued link did not revoke the old one** unless the teacher
   was on the device that created it. The code hash now lives on the
   student record.
6. **`photoUrl()` cached failures**, so one flaky moment left a photo
   permanently blank.
7. **A dropped connection rendered as "no words yet"** — wrong and
   disheartening for a child.

Items 2 and 3 in §9 below are the same class of bug as #7, still
unfixed.

---

# 8. THE BIG ONE — the two halves do not know each other exists

**The most valuable outstanding item, and not a polish job.** It is the
thing most likely to decide whether Margo uses any of this.

Verified in the code: two entirely separate student lists, no bridge.
The `TB` module keeps students, words and lessons in `localStorage`; the
portal keeps its own students and flashcards in Firestore. **Nothing in
`TB` ever calls `TBS`** — every `TBS.*` call site is inside `TBS_UI`.

Consequences today:

- She must **add every student twice**, once in each half.
- Her **vocabulary library cannot become flashcards.** Words already
  typed into Teachbench must be retyped one at a time in the student
  panel. The whole system rests on her adding cards after every lesson;
  making her type everything twice is exactly the friction that stops
  that happening.
- **Lessons cannot appear on the student calendar** (§9 item 12),
  because lesson times only exist on her device.
- Teachbench is **single-device**: laptop and phone hold different data,
  and neither is backed up.

**Three honest ways forward. This needs Simon's decision before anyone
writes code:**

- **(a) Bridge them.** Keep both stores; add "push to flashcards"
  actions — send a word from the library into a student's deck, and
  match a Teachbench student to a portal student once. Smallest change,
  but leaves two lists to keep in step.
- **(b) Move Teachbench onto Firestore too.** One student list, one
  source of truth, works across her devices, and lesson times become
  available to the student calendar for free. Much the largest job:
  migrating `teachbench.data` and rewriting `TB`'s synchronous storage
  layer as async.
- **(c) Leave them separate on purpose** and accept the double entry as
  the price of not touching working code.

**Recommendation: do not decide this until Margo has used the thing
(§9 item 5).** If she says she would rather add cards fresh after a
lesson anyway, the answer changes completely and (c) becomes right.

---

# 9. Everything not done

## Blocked on Simon — not code

**4. Publish the `progress` rules block.** Streaks are fully implemented
but every write is silently rejected until this is added in the Firebase
console under Firestore → Rules, just above the existing
`match /homework/{itemId}` line:

```
match /progress/{docId} {
  allow read: if canManage(studentId) || isThisStudent(studentId);
  allow create, update: if isThisStudent(studentId);
  allow delete: if canManage(studentId);
}
```

**5. Nobody has used it for a real lesson.** Everything is verified by
automated checks and by hand in a browser, but no actual teacher and no
actual student have been through it end to end. The load-bearing
assumption is that adding cards after a lesson is fast enough that Margo
does it every time. If that is false, nothing else matters — and §8 is
the main threat to it.

## Loose ends in the student portal (~15 minutes total)

**1. Dead "Level" line in the planning notes.** `RECAP.forTeacher`
prints `Level: ${student.level || "not set"}`, but nothing in this
module sets a level and there is no UI for it, so every export reads
"not set". Either add a selector beside the student name field or delete
the line. (The `TB` module *does* have levels — another symptom of §8.)

**2. The student's Words tab lies when the connection drops.**
`renderCardList` shows "Nothing here yet" whether there are no cards or
the load failed. `state.cardsError` is already populated by the
`onCards` listener and already handled correctly on the Today screen
(`renderStudentToday`); the same treatment just needs applying here.

**3. The calendar has the same gap** — `renderCalendar`'s footnote
cannot distinguish "no words yet" from "could not load them".

## Teacher-side Teachbench — known gaps

**6. Single-device, no backup, no export.** `teachbench.data` lives in
one browser's `localStorage`. Losing that profile loses every student,
material, word and lesson. Even without doing §8(b), an export/import
would be cheap insurance.

**7. No role model.** The portal has real roles enforced by Firestore
rules; Teachbench is whoever holds the browser. If a second teacher is
hired, only half the app understands that.

## Deferred by design — agreed, never started

**8. Push notifications.** The spec called these core rather than a
courtesy: hitting the review windows on time is the mechanism that makes
spaced repetition work. Needs Firebase Cloud Messaging (VAPID keys, ~5
minutes in the console) plus a service worker.

**9. Wispr Flow integration** — pull her recorded lesson summaries in
automatically so vocabulary covered in a lesson is not re-entered by
hand. Overlaps heavily with §8: both are "do not type it twice".

**10. Photo annotation** — draw on a submitted homework photo before
sending it back.

**11. Teacher voice notes** on cards, instead of or alongside TTS.

**12. Lesson times on the student calendar.** Shows review due-dates
only. Blocked on §8.

**13. Speech recognition** for pronunciation cards. Playback only today.

**14. Colour-coded dashboard polish.** A basic traffic light exists; the
richer version in the spec does not.

**15. DeepSeek integration** — no defined use case in the spec.

## Known weakness elsewhere in the app — Simon's call

**16. The bare `catch(e){}` around the load path in `loadShared()`.**
`try{ ... return migrate(d); }catch(e){}` swallows any throw and falls
through to `seed()`, so failing to READ stored data is indistinguishable
from having none: the app silently presents itself as empty while the
real data sits intact in `localStorage`, and the next write destroys it.
Reproduced during this build with a realistic store — a trivial missing
function became an apparent data-loss incident. Two commits (`fdd8041`,
`5ed90db`) hardened symptoms; the shape remains. The photos fetch
immediately above it already distinguishes these two cases properly and
is the model to follow. Not part of either Teachbench module, so left
alone.

## Open question never answered

**17. Handing the app to another model (e.g. DeepSeek) safely** — how to
give it a working copy, let it commit and push, and keep a reliable way
to roll back if its work goes wrong. Simon asked twice; it was never
answered.

---

# 10. Working practices in this repo

**Several Claude sessions edit `index.html` at once.** During this build
there were three, and this caused three separate near-misses, one of
which shipped a broken `main` that presented as data loss.

- **Never run a bare `git add index.html`.** Stage your own hunks with
  `git add -p` and check the staged diff for other people's markers
  before committing.
- Announce which regions you are working in, and stay out of others'.
- If a peer's work ends up in your commit, fix the message rather than
  rewriting history over their code.
- Before a destructive git operation, back up the file first. A stash
  that will not reapply is a bad moment to discover you have no copy.

**Other sessions' regions during this build** (may have moved on): the
calendar board `pBoardHtml` / `pWireBoard`, planner dialogs, `.wb-*` and
`.lu-*` CSS; and a Notes module at the end of `<style>`, `<main>` and
`<script>` plus one line each in `APPS` and `showNow()`.

---

# 11. Suggested order

1. **Item 4** — publish the rules. Two minutes, unblocks streaks.
2. **Item 5** — try it with Margo. This tells you how urgent §8 is, and
   may change the answer entirely.
3. **§8** — decide (a), (b) or (c), then build it.
4. **Items 1–3** — quick correctness fixes.
5. **Item 8** — push notifications, the spec's own stated priority.
