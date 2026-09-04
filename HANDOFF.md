# Handoff — what still needs doing

Written at the end of the session that shipped builds up to **53**
(`potting-bench-v44`). Everything below is open. `POLISH-CHECKLIST.md` has the
per-item detail for the polish work; this file is the whole picture, ordered by
what I would pick up first.

Nothing here is speculative — each item was either measured, deliberately
deferred with a reason, or raised by another session.

---

## 1 · Do these first — small, known, and they bite

**Clear the test data out of the browser's local state.** I seeded a fake
plant (`testplant1`, "Big Monstera"), a few notes ("Monstera cuttings batch 3",
"Garden centre list", "Leaf spots", "Repot in spring"), two notebooks
(Propagation, Shopping) and two planner tasks, to make screens show something
while testing. It is in localStorage on the machine I tested on, **not** in
git — but if that is the same browser Simon uses, he will see it. Delete by
hand, or clear the app's state and let it re-seed.

**`GET data/state.json` 404 on every boot.** `loadShared()` still fetches the
legacy artifact-sync file, left behind when PSYNC (Firestore) took over. The
failure is handled and falls through to local state, so it costs a wasted
round-trip on boot, not correctness — but it is a console error on every load
and a real delay on mobile data.
*Not fixed on purpose:* it sits in the state-loading path whose own comment
documents the "everything I entered was gone" incident, and sync belongs to
another session. Coordinate before touching it.

**`.btn:active` is defined six times** — once in the base and once inside each
design skin. Press feel therefore differs by design. Probably fine (skins are
allowed their own character), but nobody chose it deliberately.

---

## 2 · The polish checklist, unfinished

Seven boxes open in `POLISH-CHECKLIST.md`:

- Stale content after a view switch — anything that renders late or flashes
- Strings with no Czech, and attributes never passed through `t()`
- Dialogs: reachable, dismissible, never taller than a phone screen
- View transitions: one considered transition rather than several competing
- Planner render cost — the board redraws in full on every change
- Long lists: garden, plants, log, notes
- Boot: time to first meaningful paint

What is already done and verified: every view measured at 390x844, 844x390 and
1440x900 with no clipping or overflow anywhere; tap targets fixed; the
`[hidden]` trap closed file-wide; `backdrop-filter` off on phone (402 elements
to 0); one press-feedback layer and a global reduced-motion switch.

Two things in section 1 of the checklist were **measured for overflow only**.
Still unchecked: visual overlap that does not overflow, and text truncated
mid-word.

---

## 3 · Deliberately deferred, with reasons

**Rotate the calendar's time axis for landscape.** Hours run vertically in
every layout. Sideways on a phone they should run across the screen. This is
the board's geometry, not its styling: `top`/`height` become `left`/`width`
across the block renderer, the hour gutter, the "now" marker, the resize
handles and the drag maths (`WB_PXH` is already a single adaptive variable, so
that part is ready). Doing it half-right breaks dragging, which is the
planner's core interaction — worth its own session with the drag behaviour
tested properly.

**Staggered list entrances.** Rows are rebuilt on every render — `renderNotes`
runs on each keystroke of a search — so an entrance animation on rows replays
as a flicker while you type. Would need render-level change detection first.

**Note photos do not sync between devices.** Photos are excluded from PSYNC by
design; a note written on the phone shows "This photo is on another device" on
the laptop. Defensible for gallery shots, arguably wrong for a photo that is
*inside* a note. The fix is Firebase Storage. Simon's call.

---

## 4 · Notes module — left out of the original build

From the outline Simon approved, three items were explicitly not built:

- **Rich text** (bold/italic) — the editor is plain text per block
- **`[[wiki links]]` between notes** — the links panel exists; inline linking
  in the editor does not
- **Saved searches / smart folders** — worth it past a few hundred notes

And one that needs a provider: **semantic/vector search**. Hybrid search today
is keyword + fuzzy + tag/link ranking. True semantic search needs an embedding
service; Anthropic does not offer one.

---

## 5 · Bigger pieces, not started

**Teachbench: the four-tier classroom.** Teacher-only space, content library,
collaborative zone, private student workbooks — plus asynchronous assignment
distribution, deadline locking and inline voice feedback. This is a data-model
and Firestore-rules rebuild, multi-user. It needs its own design pass; it is
not a bolt-on.

**Web clipper fetching arbitrary URLs.** Blocked by CORS from a static page.
Today it is paste- and share-based, with OCR for images. A real clipper needs
a proxy.

---

## 6 · Raised by other sessions, still open

**Should user-named things ever be translated?** The Czech sweep was
translating user data: a notebook named "Propagation" rendered as "Množení", a
plant called "Big Monstera" as "Velká monstera", and — worst — Teachbench was
showing students the *answer*, rendering a vocabulary card whose front is
"water" as "zálivka". Card faces, note titles, tags, notebook and plant names
are now exempt. **Roughly 40 render sites are still exposed**: product and
brand names, formula and schedule names, task titles, project names, people
names. Not obviously a bug in every case — a plant someone named "Mint"
arguably *should* read "Máta". Needs a decision, then a sweep.

**DeepSeek writes into the live repo.** It runs in `~/Desktop/deepseek version`
via aider, and its `_preview/*.py` scripts are hard-coded to open
`/Users/simonmusel/Desktop/theapp/index.html` — the shared working tree, while
three Claude sessions are editing it. A worktree exists for it at
`~/Desktop/theapp-deepseek` (branch `deepseek`) and is untouched. Point those
scripts there.

## 7 · Session of 4 Sep — plants, a toxicity gate, the phone parking lot

Three things landed. None of them are open; they are here so the next session
knows the ground moved.

**The plant library went from 158 to 1,074.** Twenty-three genus batches,
generated by a Munder Difflin agent floor, validated and merged. Pipeline:

```
tools/plant-data-handoff.md    the spec, with a {{GENUS}} placeholder
tools/batches/<genus>.json     one file per genus — the SOURCE
tools/merge_plants.py          validates (--check) and merges
```

`index.html` is the **output**, not the source: the merge rewrites one
`GENERATED` block whole from the batch files on every run, so it is idempotent
and never double-adds. The `SPECIES` literal still reads 158 and that is
correct — the other 916 are pushed in at load by the generated block. Do not
"fix" that count.

**A toxicity gate now guards `merge_plants.py`, and it is the important part.**
The spec had always said toxicity was the one field where a guess is
unacceptable. Nineteen batches still came back with maidenhair fern, bird's
nest fern, parlour palm, sundew, butterwort and Sarracenia marked toxic to cats
and dogs — all of them non-toxic, three of them already in the app precisely
because they are the ones people buy for a house with animals in it. The
batches also contradicted each other, Boston fern and staghorn coming back
clean while maidenhair did not, which is what gave it away. `--check` had
waved all of it through: it validated ranges and categories and had nothing to
say about the field that matters.

`TOXICITY` in that script now holds the settled ASPCA answers keyed by genus
and common name. A record contradicting one is a hard error, not a warning, and
it refuses in both directions — a toxic plant marked safe fails as hard as a
safe plant marked toxic. **A plant absent from the table is not thereby
cleared, only uncovered.** Never add a guess to it; everything in there becomes
unarguable.

**The parking lot was capped on phones** (`5aaba19`). `.wb-parking` and
`.wb-quick` each capped at three rows / 132px, which is a desktop cap: on a
375px phone the header, nav, scope switcher and search already cost 305px, so
three rows pushed the first hour to 445px. Two rows under 640px wide, one row
under 520px tall. Verified with an emulated viewport only — **not yet tested on
a physical phone.**

`howea.json` holds one record. **That is correct, not a failed batch.** The
genus has two species, both endemic to Lord Howe Island, and the app already
had the other one (kentia palm). I misread it as a failure first time round.

### Munder Difflin, the agent harness

Installed this session at `/Applications/Munder Difflin.app`; hive at
`~/HarnessAgents/hive/` (`registry.json` for the fleet, `spawn-requests/` for
pending workers, `PROTOCOL.md` for the rules). Two behaviours look like faults
and are not:

- **Workers do not self-start.** A spawned agent sits idle at 0% context until
  it receives a prompt. A standing goal alone never triggers it.
- **Autonomous spawning is off by default** (Settings → Autonomy & Budgets).
  Requests then wait in `spawn-requests/` unpicked — neither failed nor
  deleted.

**Git isolation (own worktree)** is per-agent, on the Workspace step. Turn it
**on** for code work on `index.html`, so each agent gets its own checkout and
cannot touch the shared tree — this is the answer to the concurrency problem in
the working rules below. Turn it **off** for plant work, because the spec file
is untracked and would not exist in a fresh worktree at all.

Workers are briefed never to touch `index.html`. Keep it that way.

### Two time-wasters

- A **GateGuard hook** intercepts the first Bash command and every file write,
  demanding a short "facts" preamble. Answer it and retry the same command — it
  is not a permission denial.
- Port **8955** is usually already held by a peer session's server. Navigate to
  it rather than starting a second one.

---

## Working rules for this repo

- **Several sessions edit `index.html` at once.** Never `git add index.html`
  wholesale — stage your own hunks, then `git show :index.html`, extract the
  script and `node --check` the **staged blob**, not the working tree. A commit
  tonight swept ~600 lines of another session's uncommitted work into an
  unrelated message.
- Never a whole-file write, never `sed -i` with line numbers. String-anchored
  edits only; append at the end of `<style>` / `<script>`.
- The build stamp in `BUILD` and `CACHE` in `sw.js` move **together**, and you
  pull before bumping.
- `requestAnimationFrame` does not run in a hidden tab — use timers for
  anything that must survive a backgrounded window.
- **A whole-file write will eat another session's file, not just
  `index.html`.** This handoff was itself overwritten by a `cat >` that did not
  check whether the file already existed; 145 lines were recovered from
  `6a2775f`. Check, then append.
