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
| `const TB` | The older teacher-side module (localStorage). Schema 13. |
| `const DRILL` | The six practice modes. Pure, no DOM, no network. |
| `tbRun*` / `tbPortal*` / `tbPush*` | Lesson mode and the bridge to the portal. |
| `tbExportBackup` / `tbParseBulkWords` | Backup, and pasting a whole word list. |
| `tbRenderAccount` / `tbStatementText` | Attendance, packs and the monthly statement. |

The teacher-side additions live in one block at the **end of the script**,
and they **wrap** the existing `tbRender*` functions rather than editing
them. That is on purpose: several sessions edit this file at once, and a
wrapper at the end of the script cannot collide with someone working in the
middle of the module.

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

**Czech past tense misgenders students, so it is avoided entirely.** The
review session's feedback line was written as `napsal jsi` ("you wrote",
masculine). Czech forces a gender on the past participle — there is no
neutral form — so that line called every girl using the portal "he". It is
now `tvoje odpověď:` ("your answer:"), which sidesteps the choice rather
than picking one.

The same rule shaped the CEFR can-do statements: they are infinitives
("Objednat si v kavárně jídlo a pití") rather than first person, because a
literal "I described my weekend" would have forced `dělal` / `dělala`.
Their ids are unchanged, so stored ticks still line up.

This is not a translation nicety — most of Margo's students are children,
and about half of them are girls. Any new student-facing Czech string that
reaches for a past tense needs the same treatment.

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

# 8. THE BRIDGE — decided and built (option a)

**Status: done.** Previously the most valuable outstanding item, and it was
left open because it is a product decision with three legitimate answers.

Simon asked for an unattended build and could not be consulted, so option
**(a) bridge them** was taken, deliberately and not (b):

- (b) is an async rewrite of `TB`'s working synchronous storage layer.
  That is not something to do overnight, unattended, in a file five
  sessions are editing.
- (a) leaves both stores intact and is undone by clearing one field, so if
  Margo's first real use says the answer is (b) or (c), nothing here is in
  the way.

What exists now:

- `student.portalId` on the Teachbench record links a student to the same
  person in the portal roster. Set once from **Student portal → Link**, on
  the student's detail page.
- **Send words to flashcards** pushes a student's vocabulary across as
  cards. The word's `example` sentence travels with it, which turns the
  same card into a gap-fill for free.
- **Lesson mode** (§8a below) does the same automatically at the end of a
  lesson.

Still true, and still worth knowing:

- The two student lists are still two lists. Adding a student still has to
  happen in both halves; only the *words* stop being typed twice.
- Lesson times still do not reach the student calendar (§9 item 12).

**The Firebase SDK still loads only when the portal is actually used.** The
first version of the check tested for `window.firebase`, which the main
app's own sync (PSYNC) also defines — that would have dragged the portal
open on every student page. It now checks that a member of staff is
genuinely signed in, and otherwise waits for a button press.

## 8a. Lesson mode — the thing the system actually rests on

New, and the most important part of this work. The app was used before a
lesson to plan and after it to record; the hour in between had no screen.

**Run** on any lesson opens the plan, a scratch pad for words as they come
up, notes, and how it went. It ends with **Save and make cards**: the words
become the student's vocabulary and, when the student is linked, flashcards
in the portal in the same press.

The load-bearing assumption in §9 item 5 was that adding cards after a
lesson is fast enough that Margo does it every time. This is the answer to
that assumption, and it is the thing to watch when she first uses it.

# 9. Everything not done

## Blocked on Simon — not code

**4. Publish the `progress` rules block — VERIFY THIS.** Two sessions
disagree about whether it is already live: one says it was published on
4 Sep, the one that wrote the code says it was not. Nobody in a Claude
session can see the Firebase console, so this has to be checked by hand.

If it is missing, every streak write is silently rejected and the streak
will read as permanently zero while looking like a code bug. The block goes
under Firestore → Rules, just above the existing `match /homework/{itemId}`
line — or simply paste the whole of `firestore.rules`, which is the
reviewable source of truth and already contains it:

```
match /progress/{docId} {
  allow read: if canManage(studentId) || isThisStudent(studentId);
  allow create, update: if isThisStudent(studentId);
  allow delete: if canManage(studentId);
}
```

**5. Nobody has used it for a real lesson. STILL THE BIGGEST RISK.**
Everything is verified by automated checks and by hand in a browser, but no
actual teacher and no actual student have been through it end to end.

The load-bearing assumption is that adding cards after a lesson is fast
enough that Margo does it every time. Lesson mode (§8a) is the answer to
that assumption, and it is the single thing to watch when she first uses
it. If she does not reach for it, nothing else here matters.

**One part of tonight's work could not be tested at all**: the student
portal's review session needs a Firebase sign-in, and no session has the
password. The six practice modes are covered by 39 unit checks over the
pure `DRILL` module and verified live in the browser, and every element and
handler they need is confirmed present — but no card has been reviewed
through the real UI. Treat §12 as unproven in the app until someone signs
in and reviews one card of each shape.

## Loose ends in the student portal — DONE

Items 1, 2 and 3 were fixed by another session in commit `b548844` and are
kept here only so nobody re-derives them: the dead `Level:` line is gone
from `RECAP.forTeacher`, and `renderCardList` / `renderCalendar` both check
`state.cardsError` before claiming there are no cards.

## Teacher-side Teachbench — gaps closed

**6. Single-device, no backup, no export — DONE.** `TB.buildBackup` and
`TB.parseBackup` already existed with no way to reach them. Teachbench →
Students → **Backup** now exports a dated JSON file and restores one.
Restoring replaces everything, so the file is read and described first and
the destructive press is never the first one. `teachbench.data` is still
one browser's localStorage; this only means losing it is now recoverable.

**7. No role model.** Still true. The portal has real roles enforced by
Firestore rules; Teachbench is whoever holds the browser.

## Also built in the same run (schema 13)

All localStorage, so none of it waits on the Firebase console:

- **Attendance** on every lesson (attended / no-show / excused), separate
  from `state` so "moved, then missed" is recordable.
- **Late cancellations**: `cancelledAt` makes "was it inside 24 hours?" a
  question the app answers. A late cancellation is charged; one made in
  good time is not.
- **Rate, lesson packs and a monthly statement** — plain text to paste into
  an invoice. Credits left and money owed are *derived*, never stored, so a
  running total cannot drift from the lessons actually taught.
- **Bulk paste** of a whole word list, and duplicate detection in the bank.
- **CEFR can-do checklist** per student, showing their level and one either
  side.
- **Rest days** on the student's streak (earned, capped at two, never
  purchasable) and a **rescue list** of the five most-lapsed words.
- **Six practice modes** in the review session — see §12.

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

**13. Speech recognition — DONE.** Pronunciation cards now score what the
student says, using the browser's own recogniser (no server, no cost). Any
of the recogniser's alternatives matching counts, because it routinely puts
the right word second for a non-native accent. On a device with no
recogniser the card falls back to listen-and-self-grade rather than showing
a button that does nothing.

**14. Colour-coded dashboard polish.** A basic traffic light exists on the
portal roster; the richer version in the spec does not. The teacher-side
Teachbench roster still has no traffic light at all — that one is worth
doing next and is cheap, since `TB.lessonAccount` already computes what it
would need.

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

1. **Item 4** — confirm the `progress` rules block really is published.
   Two sessions disagree and only the console can settle it.
2. **Item 5** — try it with Margo, and specifically watch whether she uses
   lesson mode. That answers the only question that matters.
3. **Item 8 (push notifications)** — the spec's own stated priority, and
   now the largest thing still missing. Needs FCM keys from the console.
4. **The teacher-side traffic light** (item 14) — cheap, and
   `TB.lessonAccount` already computes what it needs.
5. **Lesson times on the student calendar** (item 12) — now unblocked for
   any student who is linked, since `portalId` exists.

# 12. The review session: six shapes, one card

Added in the same run. Every card used to be the same interaction — read,
reveal, grade yourself — which is hard to do honestly and boring inside a
fortnight. A card is now asked in whichever of these it can support:

| mode | what the student sees | checked? |
|---|---|---|
| `reveal` | the word, then its meaning | self-graded |
| `choice` | the word, and four meanings to pick from | yes |
| `reverse` | the meaning, recall the word | self-graded |
| `type` | the meaning, type the word | yes |
| `cloze` | the example sentence with the word blanked out | yes |
| `listen` | nothing — it is spoken; type what you heard | yes |
| `say` | the word; say it, the recogniser scores it | yes |

Nothing extra is stored to make this work. Cards gained one optional field,
`example`, written only by the teacher, and every other shape is derived
from what was already there.

**The ramp is deliberate.** A word met once is offered as recognition,
because being asked to produce a word seen a single time is a wall rather
than a test. The harder shapes arrive once the SM-2 interval stage says it
is sticking. Rotation is by review count rather than at random, so the same
card never asks the same thing twice running and the right answer never
moves about under a student who is still reading.

The rules live in **`DRILL`**, a new module beside `SRS` and `STREAK` and
pure for the same reason — no DOM, no network, exercisable from the
console, which is how it was verified:

```js
DRILL.checkAnswer("recieve", "receive")            // → "close"
DRILL.clozeFrom({front:"apple", example:"I ate an apple."})
DRILL.modesFor({type:"vocab", back:"jablko", intervalStage:3}, deck, {})
```

Answer checking is **Damerau**, not Levenshtein: swapping two adjacent
letters is the commonest typo there is, and counting "recieve" as two edits
would mark a student wrong for a slip of the fingers. Tolerance scales with
word length and is zero under four letters, where "cat" for "cot" is a real
mistake. Accents and punctuation are folded away.

A checked answer **highlights** the honest grade but never picks it. The
student knows things about how well they knew it that a string comparison
cannot see.

## What was deliberately not taken from Duolingo

Recorded so it is not proposed again as an oversight. Duolingo is optimised
for a stranger with no teacher and no reason to come back; Margo's students
have both.

- **Leagues and leaderboards** — there is no cohort. Ranking three
  one-to-one students against each other loses the one who comes third.
- **Hearts and lives** — being locked out for wrong answers punishes
  exactly the moment retrieval practice is working. Getting it wrong is the
  mechanism, not the failure.
- **Gems and a shop** — a second game to play instead of a language.
- **A purchasable streak repair** — a streak you can buy back has stopped
  meaning anything. Rest days are earned, capped at two, and never sold.
