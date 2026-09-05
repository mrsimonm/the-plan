# Planner block categories — design spec

**Status:** proposal for review. No code changed yet.
**Owner decision made:** merge "Quick task" into "Task".
**Owner decision still open:** may subtasks / checklist items be scheduled onto the
calendar as their own blocks? Recommended default below is *"inside the parent,
promotable"* — the design is written around it and the open spots are flagged
`[open]`.

This spec answers one question: **how should the differentiation between Tasks,
Quick tasks, Subtasks and Checklists work?** The short answer is that those four
are not four kinds of thing — the app has been pretending they are, which is why
the planner feels incoherent. The fix is a single object with two kinds and a
small set of placement rules.

---

## 1. Why it feels weird today

The four labels mix three different axes and reuse one word for two things:

| Label | What the record actually is today | Axis it really belongs to |
|---|---|---|
| **Task** | `kind:"task"`, optional day, optional time, may carry `steps` | *kind* |
| **Quick task** | `kind:"quick"` — whole day, no time, no editor, no subtasks, tick-only | *capture style*, not a kind |
| **Subtask** | `steps[]` — inline `{id,text,done}`, one level deep, never a block, invisible on the board | *containment* |
| **Checklist** | not an object at all — a *bucket* of dateless tasks | *container* |

Specific faults (each traceable to a line):

- **"Quick" names two unrelated things.** It is a stored kind *and* the name of
  the dateless bucket: `pBucket()` returns `"quick"` for any task with no `due`
  (index.html:8979), while `kind:"quick"` is a whole-day chip that always *has*
  a due date. The Checklists panel ("add something… then break it into steps")
  and the quick chips above each day column are different features sharing a
  word.
- **A quick task is a dead end.** Tapping its chip calls `pOpenEditDialog`, which
  silently returns for quick (9600–9602), so it can never be renamed, given a
  time, or broken into steps from the board. It is kept out of the gesture
  engine on purpose so it can never become timed (10660–10662, 11361–11365).
- **Subtasks are second-class.** They are `{id,text,done}` glue on the parent,
  never schedulable, and a parent's breakdown is invisible on the board. The
  normalizer flattens any nesting past one level and throws the structure away
  (7627–7630).
- **Events cannot hold anything.** The steps UI hides for events (9589–9596); an
  event converted from a task silently keeps hidden steps.
- **Checklist items are stranded.** A dateless task cannot be given a day from
  its own row, and never appears on the board. The code comments even say this
  was a deliberate, unresolved decision: *"parking a chip for it here… was
  precisely the link that was meant to stay unmade until we decide how it should
  work"* (10682–10689). This spec *is* that decision.
- **Projects cannot be divided into parts.** A projplan project is an hour
  budget with a colour; tasks attach by `projectId` but there is no structure.

---

## 2. The system

### 2.1 One primitive: the Task

Everything the user can add is **a task**: a discrete piece of work. A task has
three optional attributes and nothing else is required to create it:

1. **A day** (`due`) — the day it belongs to.
2. **A time and duration** (`time`, `hours`) — only given when it is placed on
   the clock. **Never required to write something down.**
3. **A parent** — the task, event, or project it lives under.

A task with no day and no duration is simply an *unscheduled* task; its home is
a checklist. Giving it a day moves it onto the calendar. Giving it a time draws
it as a clock block. This is the whole "add without specifying how long" rule:
duration is a property you fill in *at scheduling time*, never at capture time.

### 2.2 Two kinds: Task and Event

The only two kinds stored on a record. One axis of *nature*:

- **Task** — work still to be done. Rolls forward when it slips (overdue), and
  is what the calendar nags about.
- **Event** — a fixed thing that happens (`time` + `hours` mandatory, never
  overdue, never rolls). A timed task stays a task; timing does not promote it
  to an event (this is already the runtime behaviour — see the comment at
  11382–11395 — and the spec keeps it).

Everything else the user listed is **not a kind**:

- **Quick task** → merged into Task (owner decision). "Quick" survives only as a
  *capture verb*: a fast-add affordance whose result is a plain untimed task on
  the day you are looking at. Because it is a task now, it can be edited, given
  subtasks, dragged onto an hour, selected, duplicated — all the things it
  cannot do today. A task added "quick" keeps one behavioural trait: because it
  has no time, it ticks off as a whole-day item (see 4.3).
- **Subtask** → a task whose parent is another task.
- **Checklist** → a *container of unscheduled tasks*, not a kind of task. The
  current panel under the add form becomes the default checklist. Because a
  checklist is just tasks, a checklist can exist standalone (the panel), under a
  task (its subtasks), under an event (its prep list), or under a project (its
  parts).

### 2.3 One containment mechanism everywhere

**Any task or event can hold children; a child is itself a task.** That one rule
answers all three product questions:

- *"Clean the kitchen" + subtasks* — "Clean the kitchen" is a task; sink /
  surfaces / dishes / dishwasher are its children. Each child is a full task, so
  each could itself be given a day later without being rebuilt.
- *Items under events* — an event can hold children too. Children of an event
  are its prep/checklist: untimed tasks shown inside the event, tickable, and
  each `[open]` optionally schedulable to its own time.
- *Projects divided into parts* — a project's parts are the tasks filed under it
  (`projectId`), and each part is a task that can itself hold children. Because
  children are ordinary tasks, "break a project into parts" needs no separate
  subproject object.

**A project stays a project.** projplan projects remain hour budgets on the
Timeline. This spec does not add phases/sub-budgets to the Gantt — that is a
separate Timeline feature (see 7, later phase). "Parts" here means the task
breakdown that hangs off the project, surfaced in the project overview card and
usable for nesting.

### 2.4 Naming going forward

User-facing vocabulary is reduced to: **Task**, **Event**, **Checklist**
(a list of unscheduled tasks). "Subtasks" stays as the word for a task's
children. "Quick task" and "Plan" leave the kind vocabulary: "quick" is a
fast-add button; "plan" is already just the `untracked` flag and stays a
checkbox.

---

## 3. How blocks are differentiated on the calendar

The visible board should stop distinguishing by the four old labels and instead
distinguish by **time shape** and **nature**, with **containment** shown as a
small badge. A block is one of three shapes:

| Shape | What it is | How it looks / behaves today's equivalent |
|---|---|---|
| **Clock block** | task or event with `time`+`hours` | the `wb-ev` / `wb-tk` grid blocks; solid vs dashed left edge already encodes Event vs Task (1261–1271) |
| **Whole-day chip** | task with a day, no time (the old quick chip) | a chip in its day's chip row with a tick |
| **Off the board** | unscheduled task (`due` empty) | checklist rows, not blocks |

Rules:

1. **Nature** (Task vs Event) shows as the existing solid/dashed edge; a timed
   task keeps the dashed edge so "work" reads differently from "commitment".
2. **Shape** is never a kind — any untimed dated task can be dragged onto an
   hour and becomes a clock block *without changing kind* (already true at
   11382–11395), and any clock block dropped on the parking lot loses its time
   and becomes a whole-day chip (already true — it currently also rewrites
   events to tasks; see 8.9 to fix).
3. **Containment** shows as a count badge / expander on the parent chip or block
   (the step counts that already exist at 11799–11800 and 11841–11848 are the
   seed of this). Children themselves do **not** draw as blocks by default.
   `[open]` If a child is given its own day, it draws as its own chip/block on
   that day, tinted or tagged with its parent so the relationship survives on the
   board. If instead the decision is *never independent*, children stay purely
   in-parent and only the badge shows.
4. **Done** is already a universal green override (`.wb-blk.done`, 1251–1252);
   whole-day chips keep it.
5. All colour coding that exists stays: project colour via `projectId`, sleep /
   hours / care lanes untouched, recurring blocks untouched.

---

## 4. Behaviour per surface

### 4.1 The add form (currently `#pAddForm`, 4234–4259)

The segmented row "Quick / Task / Event / Plan / Project" collapses to:

- **Task** — default. Date optional, time optional, duration optional.
- **Event** — needs a time; date falls back to the selected day.
- **no completion** checkbox (the `untracked` "plan" flag) available for both.
- **Project** keeps opening its own dialog.
- **Quick capture** becomes the separate little field (see 4.2), not a segment.

"Plan" as a preset is removed; a plan is an event (or task) with *no completion*
ticked. Nothing here is new storage — it is retiring the fake kind vocabulary.

### 4.2 The Checklists panel (4261–4278)

The panel stays exactly where it is and keeps its promise — *unscheduled work,
its home is the list, not the board* — but the wall comes down in one direction
only, deliberately:

- Add a line with **no day, no time, no duration** (already true).
- Break any item into children underneath (already true, upgraded to 4.5).
- **Give it a day:** each item gets a small "put on a day" affordance that opens
  a date picker. Picking a day moves the item to Today/Scheduled and it appears
  on the board as a whole-day chip or clock block. This is the decision the
  comment at 10682–10689 left open. Nothing ever moves the other way (a
  scheduled task that loses its day returns here — that is what "drop on the
  parking lot" will do).

### 4.3 Whole-day items (old Quick tasks) on the board

The per-day chip row above each day column (the old `quickCell`, 10444–10551)
stops belonging to `kind:"quick"` and becomes the home of **any untimed task
dated to that visible day**. Behaviours:

- Chip shows title + tick. Ticking is reversible while the item sits on its day
  (as today at 11457–11461): a whole-day item is "the day happened", not "the
  work is done", so an untick is legitimate.
- Tap opens the editor (no more silent no-op at 9600–9602).
- Drag to another day moves `due`; drag onto an hour gives it a time and it
  becomes a clock block — *staying a task*.
- A whole-day item whose day has passed behaves like any other slipped task
  (overdue → parking/roll), which is the one deliberate change from old-quick
  semantics: old quick chips never nagged because they could not do anything
  else. Now that they are tasks they roll like tasks. `[open]` If Simon wants
  the old "stays put forever, never rolls" back for some items, that is a
  per-task `sticky` flag — not built by default.

### 4.4 Lists (Today / Scheduled / Done / Recurring)

Unchanged shape. A task's children render in its expandable drawer exactly as
`steps` do today (11782–11792). The drawer gains the new child affordances
(reorder, promote-to-day). Done list shows a parent and its children as today.

### 4.5 Subtasks become real records (data change, see 5)

`steps[]` entries upgrade from `{id,text,done}` to **mini task records** so a
child can carry a day/time of its own and, `[open]`, be promoted to the board.
The renderers that read `steps` keep working because the array stays on the
parent; the edit/tick/rename handlers (12449–12530) stay; only the add and
sanitize paths change shape.

### 4.6 Events

An event can hold children — its prep/checklist — shown in the slot/edit dialog
where steps are today (the UI exists, 9566–9577; it is merely hidden for events
at 9589–9596). "Make a task / Make an event" conversions (12428–12437) stop
hiding/discarding the breakdown and keep it in both directions. Children of an
event default to untimed detail on the event's day. `[open]` optionally
placeable at their own times.

### 4.7 Projects

The "All projects" overview card (11890–11956) already lists a project's tasks
and their subtask tallies; it becomes the natural home for **parts**: top-level
tasks under the project are its parts, and nesting gives part → task → subtask.
No new storage. The Timeline keeps its budget model untouched.

---

## 5. Data model

### 5.1 The record (one flat array `S.planner.tasks`, two kinds)

```js
{
  id: "tk_1",
  title: "Clean the kitchen",
  kind: "task",                 // "task" | "event"   ("quick" removed)
  due: "",                      // ISO day, or "" = unscheduled → checklist
  time: "",                     // "HH:MM" when placed on the clock
  hours: 0,
  done: false,
  doneAt: undefined,
  untracked: false,             // "plan" / no completion — kept as a flag
  projectId: null,              // part of a projplan project when set
  groupId: null,                // multi-day event runs — untouched
  steps: [                      // children — was {id,text,done}; now:
    { id: "st_1", text: "Clean the sink", done: false, due: "", time: "", hours: 0, steps: [] }
  ],
  noteId: undefined, blockId: undefined   // Notes bridge — untouched
}
```

Design notes:

- **Children stay embedded** in the parent's `steps` array rather than becoming
  their own flat records with `parentId`. Reasons: every existing reader of
  `steps` (row renderers, tallies, dup/copy, notes bridge) keeps working with a
  shape upgrade instead of a relocation; children can never leak into Today /
  Scheduled / Checklist as phantom top-level rows; "children live inside their
  parent" is then true by construction, which is the recommended `[open]`
  default. A child that is promoted to the board is still *found* by walking
  parents (`pFindAny(id)`), which the gesture engine already does per-id via
  `pFindTask` (12386).
- **Depth:** children may have children, with a hard cap (recommend 8) and a
  cycle guard (a task can never be its own ancestor). The load-time sanitizer
  replaces the current flatten-to-one-level pass (7627–7630) with a recursive
  normalise that caps depth and drops cycles instead of flattening.
- **`quick` kind is gone.** Records that were `kind:"quick"` become `kind:"task"`
  keeping `due`, `done`/`doneAt`; `time`/`hours` were already empty for them.
- **`untracked`** stays a boolean, still forbidden from forcing a dead tick in
  the checklist (fix 8.7).

### 5.2 Migration (in `migrate()`, 7505+)

Version gate `modelV:8`:

1. Map every `kind:"quick"` → `kind:"task"` (no other field change needed).
2. Upgrade each `steps[]` entry in place to the mini-task shape (preserve
   `id`, `text`, `done`; add the new optional fields).
3. Replace flatten-at-depth-1 with recursive normalise (cap 8, cycle guard).
4. Back up pre-v8 state via the existing `pBackupBeforeMigrate` so nothing is
   unrecoverable, matching how v7 handled its split.
5. The whitelist at 7641 narrows to `event`/`task`; the quick-specific resets at
   7644 and 7652 are deleted; all other normalisation is unchanged.

### 5.3 Sample: your example, before and after

Before (today) — "Clean the kitchen" is a dateless checklist task with glue steps:

```js
{ id:"a", title:"Clean the kitchen", kind:"task", due:null, steps:[
  { id:"s1", text:"Clean the sink", done:false },
  { id:"s2", text:"Clean surfaces", done:false },
  { id:"s3", text:"Do dishes", done:false },
  { id:"s4", text:"Clean the dishwasher", done:false } ] }
```

After — same thing, but each step is a task-shaped record, so any one of them
can be promoted:

```js
{ id:"a", title:"Clean the kitchen", kind:"task", due:"2026-09-07", time:"", hours:1,
  steps:[
    { id:"s1", text:"Clean the sink", done:false, due:"", time:"", hours:0, steps:[] },
    { id:"s2", text:"Clean surfaces", done:false, due:"2026-09-07", time:"09:00", hours:1, steps:[] },
    { id:"s3", text:"Do dishes", done:false, due:"", time:"", hours:0, steps:[] },
    { id:"s4", text:"Clean the dishwasher", done:false, due:"", time:"", hours:0, steps:[] } ] }
```

(`s2` is shown promoted: it now has its own slot and will draw on the board while
still counting as a child of "Clean the kitchen".)

---

## 6. What this closes / what stays open

Closed by this spec:

- Quick task is a task (owner decision).
- Checklist items can be promoted to a day; the wall is one-way and deliberate.
- Subtasks are real (task-shaped) records, not glue.
- Events can hold prep/checklists.
- Projects get parts via the ordinary task nesting, no new object.

Explicitly **open** (`[open]` above), defaulting to the recommended choice:

1. May a promoted child draw as its own block on the board, or stay purely
   in-parent? Recommended: yes with a parent tag, opt-in per child.
2. Do old-quick whole-day items roll like tasks when their day passes, or keep a
   `sticky` no-roll mode? Recommended: roll like tasks (no flag).
3. Depth beyond task → subtask. Recommended: allow nesting to a cap of 8; UI can
   still treat >1 level as "advanced".

Out of scope for this change: Timeline project phases/sub-budgets, checklist
reordering (nice-to-have), undo.

---

## 7. Build order

1. **Model + migration only** (no UI): kind whitelist, `quick`→`task` map,
   recursive step normaliser, v8 gate + backup. Verify with a state dump that a
   pre-existing tree (quicks, checklists, events-with-hidden-steps) reloads
   identically in appearance.
2. **Whole-day items on the board**: chip row driven by *any* untimed dated
   task; delete the quick special-cases in the gesture engine, `pItemsFor`,
   `pSel`, `pDupTask`, `pOpenEditDialog` guard; give chips the editor. Delete
   dead `.wb-quick`/`.wb-adtask` CSS.
3. **Add form**: retire Quick/Plan segments → Task/Event + no-completion +
   separate quick-capture field.
4. **Promotion affordance** in the Checklists panel (put on a day).
5. **Events hold children**: unhide the steps editor for events; keep the
   breakdown through Task↔Event conversion.
6. **Project parts**: surface nesting in the overview card; allow parent ordering
   under a project.
7. *(later, separate)* Timeline phases with sub-budgets if wanted.

## 8. Touch-point inventory (current code)

Referenced while writing this spec; verify each when implementing:

- Whitelist & quick resets: 7641, 7644, 7652 — narrow / delete.
- Steps flatten: 7627–7630 → recursive normalise.
- `pBucket` "quick" naming: 8979 — rename internally (e.g. `undated`), keep the
  panel label "Checklists".
- `pItemsFor` quick branches: 9143, 9158–9169.
- Quick-chip render: `quickByDay` 10439–10451, `quickCell` 10444, gutter 10362.
- Quick gestures: 10756–10797 (chip drag/tap/day move), `pQuickAdd` 12006–12012.
- Board quick-lane cells data: 10504, 10632; parking exclusions 10660–10662,
  10701–10706.
- Silent no-op editor guard: 9600–9602.
- Tick rules: 11453–11464 (reversible whole-day tick).
- Drag/park: 11206–11224 (drop to parking clears time), 11361–11365 (quick
  never timed), 9835–9837 (`pSelAllPark` rewrites events to tasks — fix).
- Steps UI: dialog 9566–9577 + hidden-for-events 9589–9596; rows 11782–11792;
  checklist 11826–11855; handlers 12449–12530; `pAddStep` 12482.
- Add form / segments: 4237–4243, 12014–12045, 12051–12081.
- Conversion keeps steps: 12428–12437.
- Projplan (unchanged except reading nesting): overview 11890–11956.
- Dead CSS: `.wb-quick` 912–918, `.wb-adtask` 1071–1093.
- Search labels ("Event"/"Task" only): 12260.
- Notes → planner bridge: 27597, 27940 (writes task-shaped records).
