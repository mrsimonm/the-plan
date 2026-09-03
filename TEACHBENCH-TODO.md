# Teachbench Student App — what is left

Status as of the end of the build session. Everything in the original v1
plan is implemented, committed and live on `main`. This file lists only
what is NOT done, so any session (or another model) can pick it up cold.

Relevant files:
- `index.html` — the whole app. The student module lives in three IIFEs
  near the end of the script: `SRS` (spaced repetition maths), `TBS`
  (Firestore data layer), `TBS_UI` (all DOM work), plus `STREAK` and
  `RECAP`. Markup is `<section id="view-teachbench-student">`; styles are
  the `.tbs-*` block.
- `firestore.rules`, `storage.rules` — deployed copies live in the
  Firebase console; these are the reviewable source of truth.

Firebase project: `teachbench-student` (Blaze plan, Firestore in
europe-central2). Owner: musel.simon@gmail.com. Teacher: linlab.cz@gmail.com.

---

## A. Loose ends in the student module — DONE (commit b548844)

All three are fixed. Kept below for the record.

1. **Dead "Level" line in the teacher's planning notes.**
   `RECAP.forTeacher` prints `Level: ${student.level || "not set"}`, but
   nothing in this module ever sets a level and there is no UI for it, so
   it reads "not set" in every export. Either add a level selector beside
   the student name field, or delete the line.

2. **The student's Words tab lies when the connection drops.**
   `renderCardList` shows "Nothing here yet" whether there are no cards or
   the load failed. `state.cardsError` is already populated by the
   `onCards` listener and is already handled correctly on the Today screen
   (`renderStudentToday`) — the same treatment just needs applying here.
   This matters: a misleading empty state on the Potting Bench load path
   is what turned a trivial missing-function bug into an apparent
   data-loss incident during the build.

3. **The calendar has the same gap.** `renderCalendar`'s footnote cannot
   distinguish "no words yet" from "could not load them". Same fix.

## B. Blocked on Simon — not code

4. **Publish the `progress` rules block.** Streaks are fully implemented
   but every write is silently rejected until this is added in the
   Firebase console under Firestore -> Rules, just above the existing
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
   no actual student have been through it. The load-bearing assumption is
   that adding cards after a lesson is fast enough that Margo does it
   every time; if that is false, the rest does not matter.

## C. Deferred by design — agreed, never started

6. **Push notifications.** The spec called these core rather than a
   courtesy: hitting the review windows on time is the mechanism that
   makes spaced repetition work. Needs Firebase Cloud Messaging (VAPID
   keys, ~5 minutes in the console) plus a service worker.
7. **Wispr Flow integration** — pull lesson summaries in automatically.
8. **Lesson times on the student calendar.** It shows review due-dates
   only. Lesson times live in the teacher-side `teachbench.data`
   localStorage store, not Firestore, so this needs those to be migrated
   first — deliberately not smuggled into the student-app work.
9. **Photo annotation** — draw on a submitted homework photo before
   sending it back.
10. **Teacher voice notes** on cards, instead of / alongside TTS.
11. **Speech recognition** for pronunciation cards. Playback only today.
12. **DeepSeek integration** — no defined use case in the spec.
13. **Colour-coded dashboard polish.** A basic traffic light exists on the
    roster; the richer version described in the spec does not.

## D. Known weakness elsewhere in the app — Simon's call

14. **DONE — no longer the shape described below.** `loadShared()` now
    tracks `readFailed` and gates `stateLoaded` on it, so a failed read or a
    throwing `migrate()` can no longer publish a blank seed over real data.
    Original report:

    **The bare `catch(e){}` around the load path in `loadShared()`.**
    `try{ ... return migrate(d); }catch(e){}` swallows any throw and falls
    through to `seed()`, so a failure to READ stored data is
    indistinguishable from having none — the app silently presents itself
    as empty while the real data sits intact in localStorage, and the next
    write destroys it. Reproduced during the build with a realistic store.
    Two commits (fdd8041, 5ed90db) hardened symptoms; the shape remains.
    The photos fetch immediately above it already distinguishes these two
    cases properly and is the model to follow. Not part of the Teachbench
    module, so left alone.

## E. Open question never answered

15. **Handing the app to another model (DeepSeek) safely** — how to give
    it a working copy, let it commit and push, and keep a reliable way to
    roll back if its work goes wrong. Simon asked; it was not answered.

---

## Notes for whoever picks this up

- **Several Claude sessions edit `index.html` concurrently.** Never run a
  bare `git add index.html`; stage your own hunks with `git add -p` and
  check the staged diff for other people's markers before committing.
  Three separate near-misses happened during this build, one of which
  shipped a broken `main`.
- The student app is reachable two ways: a real student link
  (`index.html#s=<code>`, which hides all the teacher chrome and is
  sticky across reloads), and a normal "Student Bench" entry in the app
  menu, which is how the teacher reaches her own side.
- `SRS` and `STREAK` are pure functions over plain data with no DOM and no
  network, so they can be exercised directly in the browser console —
  that is how the spaced-repetition intervals and the streak rules were
  verified.

---

## F. Cross-device sync for the MAIN app (added 2026-09-03)

Built and pushed: commits `07ebb91` (the sync layer) and `2894f3d` (the
multi-account safety fix). Data and schedules sync between devices via
Firestore; photos deliberately do not travel.

`PSYNC`, at the very end of the script in `index.html`, supplies an `ART`
whose `publish()` writes to `users/{uid}/state/main`. Everything else —
`touch()`, `push()`, the debounce, the `stateLoaded` guard — is the
original, long-dormant sync path, unchanged.

**Blocked on Simon, and nothing works until it is done:**

1. **Publish `firestore.rules` in the Firebase console.** It now carries
   the new `users/{userId}/state/{docId}` block AND the `progress` block
   from item 4 above, which was still unpublished. Until this is done
   every sync write is refused and the badge reads "sync: not allowed".
2. **Create the accounts.** Firebase console -> Authentication -> Users ->
   Add user, one per person. There is no sign-up screen in the app by
   design; passwords are handed out. Each person then signs in at
   Settings -> Potting Bench -> Sync.

**Verified live on 2026-09-03**, with a phone holding the real data and an
empty laptop:

- Rules published; sign-in works; the phone uploaded to
  `users/{uid}/state/main` and the laptop pulled it down and rendered it.
- Two ordering bugs were found by doing this for real rather than by
  reading the code, and both are fixed (`2894f3d`, `c0b0489`). The second
  was live and would have destroyed the phone's data: a device that
  adopted an empty cloud only set a marker and did not upload until the
  next edit, so the empty laptop would have claimed the cloud second and
  published over the full phone -- with every step reporting "synced".

**Still never tested:**

- **The account-switch path.** Sign in as user 1, add a plant, sign out,
  sign in as user 2 on the same device: user 2 must see an empty app, not
  user 1's plant. This is what `2894f3d` exists to guarantee and it needs
  two real accounts to exercise.
- **The order still matters when adding a device.** Whichever device signs
  in first while the cloud is empty becomes the master. Bring the device
  that HOLDS the data up first, and export a backup from it beforehand.
  The app does not yet refuse to overwrite a device holding real data with
  an empty cloud copy; that guard is worth adding.

**Known limits, by choice, worth revisiting only if they bite:**

- Conflicts are whole-state newest-wins. Right for one person on two
  devices; it does not merge simultaneous edits made in two places.
- Photos stay on the device that took them, so libraries diverge. Firebase
  Storage would fix it and was explicitly deferred.
- It is per-person data, not shared data. Three accounts means three
  separate worlds; there is no way for two people to share one set of
  plants.
