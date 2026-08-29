# Overnight notes — 29 Aug 2026

Branch: **`overnight-features`** (branched from `main` at `88cacb2`). `main` untouched.
Nothing pushed, nothing force-pushed, no branches deleted.

Review in the order below; every commit stands on its own.

```
f9e8b92  Planner: fullscreen focus mode for the calendar                (Task 6)
61efba1  Add OVERNIGHT_NOTES.md
5ec452f  Planner: click or drag empty grid to add a task or event      (Task 5a/5b)
561dc16  Planner: add an All Projects overview                          (Task 4)
b943150  Planner: Task / Event / Subtask model in the UI                (Task 3)
b5e8f9c  Planner: v7 Task/Event split groundwork, and four board fixes  (Task 3 + review fixes)
93c5b0b  Timeline: add a Grid calendar mode alongside the linear Gantt   (Task 2)
a904b32  Planner: frame today and draw a now-line across the board      (Task 1c)
a4702e9  Planner: make the board's grid lines and day separators legible (Task 1b)
916f037  Planner: draw scheduled project time as real calendar blocks   (Task 1a)
```

---

## Status at a glance

| Task | State | Notes |
|---|---|---|
| 1a projects as calendar blocks | **Done, tested** | |
| 1b grid line contrast | **Done, tested** | both themes |
| 1c today frame + now line | **Done, tested** | |
| 2 Month/Quarter/Year grid + toggle | **Done, tested** | lives under Timeline — see decision D1 |
| 3 Task / Event / Subtask + migration | **Done, tested** | migration verified branch-by-branch |
| 4 All Projects overview | **Done, tested** | small Gantt included |
| 5a click empty slot → dialog | **Done, tested** | |
| 5b drag range → dialog | **Done, tested** | mouse only, see decision D5 |
| 5c drag to move | **Already worked; verified not regressed** | copy/duplicate **not** built |
| 5d resize handles | **Partial (pre-existing)** | bottom-edge only; sides/corners not built |
| 5e double-click detail / wheel scroll | **Not built** | |
| 6 fullscreen focus mode | **Done, tested** | fullscreen button + Escape to exit |
| 7 "Plachta" year canvas | **Not built** | plan sketched below |

---

## Needs your attention

1. **Visually check the All Projects card on a real screen.** It was verified
   structurally (asserting against the live DOM: correct rows, hours, states,
   task rollups), but the browser pane I test in kept collapsing to zero width,
   so I never got a clean screenshot of that card laid out at full size. The
   values are right; I have not *seen* it.

2. **The migration has already run against your real data** the first time the
   app booted from this branch. A snapshot of the pre-migration state is in
   `localStorage` under `pottingbench.backup.pre-v7`. To pull it out as a file,
   open the console and run `pDownloadBackup()`. It is written once and never
   overwritten, so it still holds the original v6 state.

3. **`hours` on a Task is kept but no longer prominent.** The day budget is
   computed from it, so dropping it would have silently emptied your planned
   totals — but a Task's duration is now only editable from the add form. If
   you want Tasks to stop consuming budget, that is a product decision I did
   not make for you.

4. **Two projects on one day can still overlap** when the day is genuinely
   overbooked. They now get the ⚠ clash marker instead of silently rendering as
   unexplained half-width lanes. Honest, but an overbooked day will look busy.

---

## Migration logic (Task 3)

Runs once, gated on `S.planner.modelV !== 7`. **Before any record is touched**,
`pBackupBeforeMigrate()` writes the whole state (minus photos) to
`localStorage["pottingbench.backup.pre-v7"]`.

Photos are excluded on purpose: they are megabytes of base64, no migration has
ever touched them, and including them is the one thing likely to blow the
storage quota and cost us the backup we came here to make.

**The rule, per your brief:** no meaningful duration → Task; real time range →
Event.

| Old record | Becomes | Why |
|---|---|---|
| `time` set **and** `hours > 0` | **Event** | a real time range |
| `time` set but `hours === 0` | **Task**, time cleared | a time with no duration is not a range |
| no `time` | **Task** | nothing to anchor to a clock |
| old `kind:"project"` (had steps) | **Task** | every Task can hold subtasks now, so the kind is obsolete |

**Nothing is deleted.**
- `hours` survives on Tasks (the day budget reads it).
- `steps` survives on *every* record, including the handful that become Events.
  An Event does not display subtasks, but they stay in the data — convert it
  back to a Task and they reappear. I followed your stated rule (time range
  wins) rather than letting subtasks override it, but kept the data so the
  call stays reversible.
- Subtasks are flattened to one level and given id/text/done defaults.

Verified against a hand-built v6 fixture covering all six branches: 0 records
lost, correct kind on each, backup written, photos excluded, and the migration
is idempotent (three runs give an identical result, and migrating different
data afterwards does not overwrite the original backup).

---

## Decisions I made on your behalf

**D1 — Where the Grid calendar lives.** Task 2 was approved when the scope pill
still had Month/Quarter/Year buttons. Those no longer exist: Month is now the
hours×days board and the long-range magnifications moved under **Timeline**. So
the Grid↔Linear toggle sits in **Timeline**, next to the zoom pills. Linear is
the existing Gantt, untouched; Grid is the calendar of squares.

**D2 — Grid honours all four magnifications**, not the three originally
planned: one full month grid, three for a Quarter, dot-only miniatures for Half
(6) and Year (12). Half was in your magnification list, so leaving it without a
Grid equivalent would have made the toggle inconsistent.

**D3 — Grid stays read-only** (your approved default). Editing lives in Linear
where the drag model already exists, so the two can never disagree about what
an edit meant. Clicking a day opens it in the Day board.

**D4 — Projects are auto-placed on the calendar.** A project has a day-level
hour budget and no time-of-day, so drawing it as a normal block meant inventing
one: it packs into the day's first free gap from 09:00, stepping over anything
already booked. **These times are presentation only** — the day's budget totals
are computed before placement and never see them. A project block deliberately
does *not* claim to be "running now" even when the clock falls inside its
invented slot; that would be a countdown against a time you never set.

**D5 — Drag-to-select is mouse only.** The track is also how the board scrolls
on a phone; stealing that to draw a selection would trade a gesture you rely on
for one already reachable from the add form. A touch *tap* still opens the
dialog.

**D6 — "Half" and "six months" are the same duration**, so the magnification
list is Month / Quarter / Half / Year rather than carrying both.

---

## What I did not build, and why

- **5c copy/duplicate a block.** Moving already worked and still does.
  Duplicating needs a modifier-key or long-press affordance that does not
  collide with the existing move gesture; I did not want to guess at that
  interaction and leave it half-wired.
- **5d side/corner resize handles.** Bottom-edge resize is pre-existing and
  works. Stretching a block *across days* is a genuinely different operation —
  one Event belongs to one day in this model, so it would have to split into
  per-day records. That needs a decision from you first.
- **5e double-click to edit / wheel to scroll hours.** Not started.
- **7 "Plachta" year canvas.** Not started. Sketch below.

### Sketch: "Plachta" year canvas (Task 7)

The pieces mostly exist; it is largely assembly plus one real problem.

- `pBoardHtml(days)` already renders an arbitrary list of days as columns with
  hours down the side, and already scrolls horizontally. A year is just
  `pDaysFor("year", iso)` returning 365 ISO strings.
- The blocker is cost, not layout: the board calls `pBudgetOf(d)` per day, which
  calls `pItemsFor(d)`, which re-scans `S.hours.sessions` from scratch on every
  call. At 365 columns that is 365 full scans per render. Month (31) is already
  the current ceiling.
- So the real work is **windowing or indexing**: either render only ~60 days
  either side of the scroll position and fill in as it scrolls, or precompute a
  day→items index once per render instead of re-scanning per day. I would do
  the index first — it is a contained change and it makes Month cheaper too.
- Column width would drop to ~18–24px with the day header reduced to a number,
  and the hour gutter must stay `position:sticky`.

---

## Testing notes

Everything below was exercised in a real browser, not just read:

- **1a** project renders as a grid block at 10:00 after a 09:00 standup
  (correctly skipping the occupied slot), drag handle intact, old chips gone.
- **1b** measured contrast against the card — dark-mode hour rules went from
  ~1.1:1 to 1.63:1, separators to 2.39:1.
- **1c** today framed; 7 now-line segments across a week, solid + dot on today;
  **0** on a week that does not contain today.
- **2** all four magnifications render (42 / 112 / 224 / 441 cells), paging
  steps by the right span, a day cell opens the Day board.
- **3** migration fixture (above); Task↔Event round trip preserves subtasks and
  hours; a dateless chip dragged onto an hour became an Event at 05:00.
- **4** three projects with correct state / hours / end date / task rollups.
- **5** click → dialog at that hour with a 1h default; drag → dialog with the
  swept range; existing block drag still moves 07:00→10:00 without the new
  dialog firing.
- **6** entering hides header/nav and pins the card fullscreen with the board
  still rendering its blocks; ✕ and Escape both restore everything. Screenshotted
  at full size.

**Console is clean** apart from two pre-existing errors unrelated to this work:
a `sw.js` 404 (the service worker is not served by the plain static test server)
and `InvalidStateError: Transition was aborted`, from my test script switching
views faster than the View Transitions API settles.

### A caveat about the test environment

The browser pane repeatedly collapsed to zero width mid-session, which makes
`getBoundingClientRect()` return zeros. Early drag tests using those
coordinates failed for that reason and **not** because the feature was broken —
once the pane was re-opened and driven with real screen coordinates, the same
drags worked first time. Anywhere I claim something is tested, it was verified
either by asserting on live DOM content or by a real pointer gesture after the
pane recovered.
